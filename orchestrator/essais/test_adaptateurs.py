import asyncio
import os
import sys
import unittest

from essais.aides import CasAvecDossier
from pole import adaptateurs
from pole.adaptateurs import AdaptateurClaudeSDK, MoteurIndisponible, MoteurNonArme, construire_options
from pole.caviardage import caviarder, caviarder_objet, contient_secret
from pole.garde_outils import evaluer_appel, evaluer_commande, fabriquer_crochet
from pole.relais import (JETON_FACTICE, CleDansEnvironnement, RelaisInvalide, RelaisSimule, noms_de_cle_presents,
                         valider_url_relais, variables_agent)

RELAIS = "http://127.0.0.1:8787"


class CrochetPreToolUse(CasAvecDossier):
    INTERDITES = [
        "cat /etc/passwd", "cd .. && ls", "ls ../", "cat ~/.bashrc", "cd", "env", "printenv", "export", "set",
        "cat /proc/self/environ", "python3 -c \"import os; print(os.environ)\"", "echo $ANTHROPIC_API_KEY",
        "echo ${!A*}", "curl https://exemple.org", "wget http://x", "pip install numpy", "python3 -m pip install x",
        "git status", "sudo ls", "timeout 5 curl http://x", "ls > /tmp/x", "cp a.txt /tmp/", "python3 -c \"open('/etc/hosts').read()\"",
        "exec 3<>/dev/tcp/1.2.3.4/80", "python3 -c 'import socket'", "declare -p", "su -", "x=1; cd /",
    ]
    SAINES = [
        "python3 experience.py", "ls -la", "cat donnees.json", "python3 -I -B experience.py > sortie.txt 2>/dev/null",
        "mkdir -p resultats && cp donnees.json resultats/", "cat ./sous/fichier.txt", "set -euo pipefail; python3 a.py",
        "export GRAINE=3 && python3 a.py", "PYTHONHASHSEED=0 python3 a.py", "echo 'je n ai pas su' > note.txt",
    ]

    def test_commandes_interdites_refusees(self):
        for commande in self.INTERDITES:
            with self.subTest(commande=commande):
                autorise, motif = evaluer_commande(commande, self.tmp)
                self.assertFalse(autorise, motif)

    def test_commandes_saines_acceptees(self):
        for commande in self.SAINES + [f"cat {os.path.join(self.tmp, 'donnees.json')}"]:
            with self.subTest(commande=commande):
                autorise, motif = evaluer_commande(commande, self.tmp)
                self.assertTrue(autorise, motif)

    def test_outils_de_fichiers(self):
        self.assertTrue(evaluer_appel("Write", {"file_path": os.path.join(self.tmp, "a.py")}, self.tmp)[0])
        self.assertFalse(evaluer_appel("Read", {"file_path": "/etc/passwd"}, self.tmp)[0])
        self.assertFalse(evaluer_appel("Edit", {"file_path": os.path.join(self.tmp, "..", "x")}, self.tmp)[0])
        self.assertFalse(evaluer_appel("WebFetch", {"url": "https://x"}, self.tmp)[0])

    def test_lien_symbolique_vers_l_exterieur_refuse(self):
        os.symlink("/etc/hosts", os.path.join(self.tmp, "lien"))
        self.assertFalse(evaluer_appel("Read", {"file_path": os.path.join(self.tmp, "lien")}, self.tmp)[0])

    def test_format_du_crochet_sdk(self):
        crochet = fabriquer_crochet(self.tmp)
        refus = asyncio.run(crochet({"tool_name": "Bash", "tool_input": {"command": "curl http://x"}}, "id", {"signal": None}))
        self.assertEqual(refus["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(refus["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        accord = asyncio.run(crochet({"tool_name": "Bash", "tool_input": {"command": "ls"}}, "id", {"signal": None}))
        self.assertEqual(accord, {})


class Options(CasAvecDossier):
    def test_options_saines(self):
        o = construire_options(self.tmp, 1.5, 12, url_relais=RELAIS, modele="claude-opus-5")
        self.assertEqual(o["cwd"], self.tmp)
        self.assertEqual(o["allowed_tools"], ["Read", "Write", "Edit", "Bash"])
        self.assertEqual(o["max_budget_usd"], 1.5)
        self.assertEqual(o["max_turns"], 12)
        self.assertEqual(o["permission_mode"], "dontAsk")
        self.assertEqual(o["setting_sources"], [])
        self.assertTrue(o["sandbox"]["enabled"])
        self.assertFalse(o["sandbox"]["allowUnsandboxedCommands"])
        for outil in ("WebFetch", "WebSearch", "Agent", "Task"):
            self.assertIn(outil, o["disallowed_tools"])
        # v47 (R-764) : point d'accès et jeton factice, plus les deux variables qui interdisent tout repli de modèle au kit
        self.assertEqual(o["env"], {"ANTHROPIC_BASE_URL": RELAIS, "ANTHROPIC_API_KEY": JETON_FACTICE,
                                    "CLAUDE_CODE_NO_MODEL_FALLBACK": "true", "CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK": "1"})
        self.assertIsNone(o["fallback_model"])
        self.assertEqual(o["crochets"]["PreToolUse"][0]["crochet"].dossier, os.path.realpath(self.tmp))

    def test_options_incoherentes_refusees(self):
        for args in ((self.tmp, 0, 5), (self.tmp, float("nan"), 5), ("relatif", 1.0, 5), (self.tmp, 1.0, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                construire_options(*args, url_relais=RELAIS)
        with self.assertRaises(RelaisInvalide):
            construire_options(self.tmp, 1.0, 5, url_relais="https://relais.exemple.org")


class Relais(unittest.TestCase):
    def test_relais_local_accepte_distant_refuse(self):
        self.assertEqual(valider_url_relais("http://localhost:9000/v1"), "http://localhost:9000/v1")
        for url in ("https://api.exemple.org", "ftp://127.0.0.1", "http://u:p@127.0.0.1", ""):
            with self.subTest(url=url), self.assertRaises(RelaisInvalide):
                valider_url_relais(url)

    def test_l_agent_ne_voit_que_le_jeton_factice(self):
        cle = "cle-de-test-factice-0000"
        env = variables_agent(RELAIS)
        self.assertNotIn(cle, str(env))
        relais = RelaisSimule(cle, RELAIS)
        reponse = relais.transmettre({"chemin": "/v1/messages", "en_tetes": {"x-api-key": env["ANTHROPIC_API_KEY"]}})
        self.assertTrue(relais.journal[-1]["cle_ajoutee"])
        self.assertNotIn(cle, str(reponse))
        with self.assertRaises(RelaisInvalide):
            relais.transmettre({"en_tetes": {"x-api-key": "une-autre-cle"}})

    def test_noms_de_cle_detectes_sans_lire_les_valeurs(self):
        self.assertEqual(noms_de_cle_presents({}), [])
        self.assertEqual(noms_de_cle_presents({"ANTHROPIC_API_KEY": "x", "HOME": "/h"}), ["ANTHROPIC_API_KEY"])


class AdaptateurReel(unittest.TestCase):
    """Aucun de ces essais ne peut lancer un agent réel : l'adaptateur n'est armé qu'avec un SDK rendu introuvable."""

    def test_importable_sans_le_sdk(self):
        self.assertNotIn("claude_agent_sdk", sys.modules)
        self.assertTrue(hasattr(adaptateurs, "AdaptateurSimule"))

    def test_non_arme_ne_lance_rien(self):
        with self.assertRaises(MoteurNonArme):
            AdaptateurClaudeSDK(RELAIS, environnement={}).lancer("experimentateur", "consigne", os.getcwd(), 1.0, 3)
        self.assertNotIn("claude_agent_sdk", sys.modules)

    def test_sdk_absent_erreur_claire(self):
        sauvegarde = sys.modules.get("claude_agent_sdk", "absent")
        sys.modules["claude_agent_sdk"] = None
        try:
            with self.assertRaises(MoteurIndisponible):
                AdaptateurClaudeSDK(RELAIS, environnement={}, arme=True).lancer("experimentateur", "c", os.getcwd(), 1.0, 3,
                                                                                  modele="claude-opus-5-5")
        finally:
            if sauvegarde == "absent":
                del sys.modules["claude_agent_sdk"]
            else:
                sys.modules["claude_agent_sdk"] = sauvegarde

    def test_cle_dans_l_environnement_refusee(self):
        adaptateur = AdaptateurClaudeSDK(RELAIS, environnement={"ANTHROPIC_API_KEY": "x"}, arme=True)
        with self.assertRaises(CleDansEnvironnement):
            adaptateur.lancer("experimentateur", "consigne", os.getcwd(), 1.0, 3)
        self.assertNotIn("claude_agent_sdk", sys.modules)


class Caviardage(unittest.TestCase):
    def test_secret_plante_caviarde(self):
        texte = "résultat ok ; clé sk-ant-api03-AbCdEfGhIjKlMnOpQrStUv ; api_key=ZZZZZZZZZZZZ ; ghp_" + "a" * 36
        propre, n = caviarder(texte)
        self.assertEqual(n, 3)
        self.assertFalse(contient_secret(propre))
        self.assertIn("résultat ok", propre)

    def test_texte_sain_inchange(self):
        texte = "statistique z = 3.2 ; seuil 2.33 ; le jeton de tour est rendu ; 120 tirages"
        self.assertEqual(caviarder(texte), (texte, 0))
        self.assertEqual(caviarder_objet({"a": [texte]}), ({"a": [texte]}, 0))


if __name__ == "__main__":
    unittest.main()
