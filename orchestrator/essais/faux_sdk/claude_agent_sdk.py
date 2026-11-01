"""Faux moteur (version 0.6.0, pièce 3 : répétition générale). Imite l'interface du Claude Agent SDK que l'adaptateur réel
utilise (`ClaudeAgentOptions`, `HookMatcher`, `query`, `AssistantMessage`, `TextBlock`, `ResultMessage`,
`ClaudeSDKError`), **sans aucun appel de modèle**. Il n'est jamais installé : on le rend importable au seul processus de la
répétition générale (`PYTHONPATH=essais/faux_sdk`, voir `demonstrations/repetition_generale_v6.py`).

À chaque `query` : (1) contrôle des options (dossier absolu existant, mode de permission, outils, variables d'environnement
de l'agent : seulement le point d'accès vers le relais et le jeton factice) ; (2) le rôle est joué par le simulateur du pôle
(`pole.simulation.AdaptateurSimule`) dans le dossier de l'agent, exactement comme en simulation ; (3) les crochets
`PreToolUse` de l'adaptateur sont exercés sur une courte séquence d'appels d'outils, dont deux interdits (réseau, chemin
hors du dossier), et leurs décisions sont consignées (`FAUX_SDK_JOURNAL`, JSON par ligne) ; (4) un appel réel au relais
local (`ANTHROPIC_BASE_URL` + `/v1/messages`, jeton factice) prouve la chaîne agent → relais → amont, et son usage donne
le coût rendu dans `ResultMessage.total_cost_usd`. Un relais qui refuse (401, 402, 502) rend un résultat en erreur, comme
le vrai moteur quand l'interface de programmation refuse.
"""

import http.client
import json
import os
import re
import urllib.parse

# v7, version 5 : marque du faux moteur ; l'orchestrateur n'exige pas le bac à sable quand il n'y a aucun agent réel (le
# vrai paquet `claude_agent_sdk` ne porte jamais cette marque).
EST_FAUX_SDK = True

JOURNAL = os.environ.get("FAUX_SDK_JOURNAL")
GRAINE = int(os.environ.get("FAUX_SDK_GRAINE", "20261027"))
ROLE_PAR_CONSIGNE = (("expérimentateur du pôle", "experimentateur"), ("vérificateur du pôle", "verificateur"),
                     ("recombinaison du pôle", "recombinaison"), ("synthèse du pôle", "synthese"),
                     ("proposeur du pôle", "proposeur"))
APPELS_D_OUTILS = [
    ("Read", {"file_path": "fiche.json"}),
    ("Bash", {"command": "ls"}),
    ("Bash", {"command": "curl http://example.com/"}),
    ("Read", {"file_path": "/etc/passwd"}),
    ("WebFetch", {"url": "http://example.com/"}),
]


class ClaudeSDKError(Exception):
    pass


class ClaudeAgentOptions:
    def __init__(self, **reglages):
        self.__dict__.update(reglages)


class HookMatcher:
    def __init__(self, matcher=None, hooks=()):
        self.matcher, self.hooks = matcher, list(hooks)


class TextBlock:
    def __init__(self, text):
        self.text = text


class AssistantMessage:
    def __init__(self, content, model=None, stop_reason=None, usage=None):
        self.content, self.model, self.stop_reason, self.usage = content, model, stop_reason, usage


class SystemMessage:
    def __init__(self, subtype, data):
        self.subtype, self.data = subtype, data


class ResultMessage:
    def __init__(self, subtype, result, total_cost_usd, is_error=False, stop_reason=None, model_usage=None):
        self.subtype, self.result, self.total_cost_usd, self.is_error = subtype, result, total_cost_usd, is_error
        self.stop_reason, self.model_usage = stop_reason, model_usage  # v49 (CL13-06) : champs du kit 0.2.172


def _consigner(entree):
    if JOURNAL:
        with open(JOURNAL, "a", encoding="utf-8") as f:
            f.write(json.dumps(entree, ensure_ascii=False, sort_keys=True) + "\n")


def _role(options):
    consigne = getattr(options, "system_prompt", "") or ""
    for marque, role in ROLE_PAR_CONSIGNE:
        if marque in consigne:
            return role
    raise ClaudeSDKError("rôle introuvable dans la consigne système")


def _controler_options(options):
    cwd = getattr(options, "cwd", None)
    if not (isinstance(cwd, str) and os.path.isabs(cwd) and os.path.isdir(cwd)):
        raise ClaudeSDKError("cwd absent, relatif ou inexistant")
    if getattr(options, "permission_mode", None) != "dontAsk":
        raise ClaudeSDKError("mode de permission inattendu")
    if set(getattr(options, "allowed_tools", [])) != {"Read", "Write", "Edit", "Bash"}:
        raise ClaudeSDKError("outils autorisés inattendus")
    env = getattr(options, "env", None) or {}
    # v47 (R-764) : le point d'accès, le jeton factice, et les deux variables qui interdisent tout repli de modèle au kit
    if set(env) != {"ANTHROPIC_BASE_URL", "ANTHROPIC_API_KEY", "CLAUDE_CODE_NO_MODEL_FALLBACK", "CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK"}:
        raise ClaudeSDKError("variables d'environnement de l'agent inattendues : " + ", ".join(sorted(env)))
    if env["CLAUDE_CODE_NO_MODEL_FALLBACK"] != "true" or getattr(options, "fallback_model", "absent") is not None:
        raise ClaudeSDKError("repli de modèle non interdit (R-764)")
    if not getattr(options, "model", None):
        raise ClaudeSDKError("modèle non précisé")
    bac = getattr(options, "sandbox", None) or {}
    if not bac.get("enabled") or bac.get("network", {}).get("allowedDomains"):
        raise ClaudeSDKError("bac à sable inattendu")
    if not isinstance(getattr(options, "max_budget_usd", None), float) or options.max_budget_usd <= 0:
        raise ClaudeSDKError("plafond de dépense inattendu")


async def _exercer_crochets(options, role):
    decisions = []
    for matcher in (getattr(options, "hooks", None) or {}).get("PreToolUse", []):
        for crochet in matcher.hooks:
            for outil, entree in APPELS_D_OUTILS:
                reponse = await crochet({"tool_name": outil, "tool_input": entree}, "id-factice", {})
                sortie = (reponse or {}).get("hookSpecificOutput") or {}
                decisions.append({"role": role, "outil": outil, "entree": entree,
                                  "decision": sortie.get("permissionDecision", "allow"),
                                  "motif": sortie.get("permissionDecisionReason")})
    for d in decisions:
        _consigner(dict(d, type="crochet"))
    return decisions


def _appeler_relais(options, role):
    env = options.env
    parties = urllib.parse.urlsplit(env["ANTHROPIC_BASE_URL"])
    corps = json.dumps({"model": options.model, "max_tokens": 16, "stream": False,
                        "messages": [{"role": "user", "content": f"appel de répétition générale ({role})"}]}).encode()
    connexion = http.client.HTTPConnection(parties.hostname, parties.port, timeout=30)
    try:
        connexion.request("POST", "/v1/messages", body=corps,
                          headers={"Content-Type": "application/json", "x-api-key": env["ANTHROPIC_API_KEY"],
                                   "anthropic-version": "2023-06-01"})
        reponse = connexion.getresponse()
        octets = reponse.read()
    finally:
        connexion.close()
    if reponse.status != 200:
        return None, reponse.status
    from pole.relais_reel import cout_usd
    objet = json.loads(octets.decode("utf-8"))
    return cout_usd(objet.get("model"), objet.get("usage")), 200


_SIMULATEUR = None


def _simulateur():
    global _SIMULATEUR
    if _SIMULATEUR is None:
        from pole.simulation import AdaptateurSimule, MondeSimule
        _SIMULATEUR = AdaptateurSimule(GRAINE, MondeSimule(GRAINE))  # monde propre : sans objet sous le monde du noyau
    return _SIMULATEUR


async def query(prompt, options):
    _controler_options(options)
    role = _role(options)
    decisions = await _exercer_crochets(options, role)
    cout, statut = _appeler_relais(options, role)
    _consigner({"type": "relais", "role": role, "statut": statut, "cout_usd": cout})
    if cout is None:
        yield ResultMessage("error_during_execution", f"le relais a refusé l'appel (statut {statut})", 0.0, is_error=True)
        return
    if os.environ.get("FAUX_SDK_REFUS") == role:  # v47 (R-764) : rejoue l'incident du 29 octobre 10:43 UTC
        yield AssistantMessage([TextBlock("")], model=options.model, stop_reason="refusal")
        yield SystemMessage("model_refusal_fallback", {"original_model": options.model, "fallback_model": "claude-opus-4-8"})
        yield AssistantMessage([TextBlock("réponse sous un autre modèle")], model="claude-opus-4-8",
                               usage={"input_tokens": 400000, "output_tokens": 20000})
        yield ResultMessage("error_max_budget_usd", "budget dépassé", 4.66, is_error=True)
        return
    resultat = _simulateur().lancer(role, prompt, options.cwd, options.max_budget_usd, options.max_turns, modele=options.model)
    texte = resultat.texte_final
    if role == "experimentateur" and re.search(r"[0-9a-f]{64}", texte) is None:
        texte += "\n(faux moteur : aucune empreinte dans la réponse simulée)"
    yield AssistantMessage([TextBlock(texte)], model=options.model, stop_reason="end_turn")
    sous_type = {"ok": "success", "budget_depasse": "error_max_budget_usd", "tours_epuises": "error_max_turns"}.get(
        resultat.statut, "error_during_execution")
    # Coût rendu : celui que le relais a réellement compté pour cet appel (le simulateur n'a pas de coût réel).
    yield ResultMessage(sous_type, texte, cout, is_error=sous_type != "success")
    _consigner({"type": "resultat", "role": role, "sous_type": sous_type, "refus_de_crochet":
                sum(d["decision"] == "deny" for d in decisions)})
