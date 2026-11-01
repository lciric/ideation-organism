"""Garde des outils des agents (crochet `PreToolUse` du Claude Agent SDK), logique pure et testable.

Refuse toute commande Bash qui sort du dossier de l'expérience, lit l'environnement, touche au réseau ou élève ses
droits ; refuse Read, Write, Edit (et Glob, Grep) hors du dossier ; refuse tout autre outil. C'est une **première
barrière** par motifs : une commande obscurcie (chemin encodé, interpréteur détourné) peut la franchir ; la barrière
réelle reste le bac à sable (réseau coupé, dossier seul accessible) et l'absence de clé dans l'environnement de l'agent.

v7, version 5 (défaut 6 du premier lancement réel) : la garde **sépare le code du shell**. Le corps d'une redirection
`<<FIN` destinée à un interpréteur (python, node, perl, ruby, Rscript, julia, php) ou à un fichier (`cat`, `tee`), et
l'argument de `python -c` (`node -e`, `perl -e`…), sont du code : seuls leurs **littéraux de chaîne** y sont lus comme
des chemins (`open('/etc/passwd')` reste refusé). En (a), `sum(t)/len(t)` devenait le chemin `/len`, `(k+1)/120` le
chemin `/120`, `set(x)` la commande `set` sans argument, `(~m)` le dossier personnel, et `print(a / b)` la racine `/` :
deux vérifications ont échoué faute de rejeu. Le corps d'une redirection destinée à un shell, ou à une commande inconnue,
reste lu comme du shell (le plus strict) ; une redirection sans fin est refusée. Les contrôles globaux (environnement,
variables sensibles, réseau) portent toujours sur le texte entier de la commande, code compris.
"""

import os
import re
import shlex

from .outils import chemin_dans

COMMANDES_RESEAU = {
    "curl", "wget", "pip", "pip3", "pipx", "git", "ssh", "scp", "sftp", "rsync", "nc", "ncat", "netcat", "telnet",
    "ftp", "apt", "apt-get", "yum", "dnf", "brew", "conda", "mamba", "micromamba", "npm", "npx", "yarn", "pnpm",
    "uv", "gh", "socat", "aria2c", "http", "https", "nslookup", "dig", "ping", "docker",
}
MOTIFS_RESEAU = ("/dev/tcp", "/dev/udp", "urllib", "http.client", "import requests", "requests.get", "requests.post",
                 "socket", "httpx", "aiohttp", "ftplib", "smtplib", "telnetlib", "paramiko", "ensurepip", "-m pip")
COMMANDES_ENV = {"env", "printenv", "compgen"}
COMMANDES_ENV_SI_NUES = {"export", "declare", "typeset", "set", "readonly"}
COMMANDES_PRIVILEGE = {"sudo", "su", "doas", "pkexec"}
CHEMINS_SYSTEME_PERMIS = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/zero"}
VARIABLE_SENSIBLE = re.compile(r"\$\{?!?[A-Za-z_]*(?:KEY|TOKEN|SECRET|PASS|AUTH|CRED|COOKIE|SESSION)[A-Za-z_0-9]*",
                               re.I)
SEPARATEURS = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;", "\n"}
OUTILS_FICHIERS = {"Read": ("file_path",), "Write": ("file_path",), "Edit": ("file_path",),
                   "MultiEdit": ("file_path",), "Glob": ("path",), "Grep": ("path",)}
INTERPRETE_CODE = re.compile(r"^(?:python[0-9.]*|pypy[0-9.]*|node|nodejs|perl|ruby|Rscript|julia|php)$")
OPTIONS_CODE = {"-c", "-e", "-E", "--eval"}
COQUILLES = {"bash", "sh", "zsh", "dash", "ksh"}
ECRIVAINS = {"cat", "tee"}
DELIMITEUR = re.compile(r"(-?)[ \t]*(?:'([^'\n]+)'|\"([^\"\n]+)\"|(\\?)([A-Za-z_0-9][A-Za-z_0-9.-]*))")
LITTERAL = re.compile(r"'''(.*?)'''|\"\"\"(.*?)\"\"\"|'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"", re.S)
APPELS_PERSONNELS = re.compile(r"\bexpanduser\b|\bPath\.home\s*\(|\bhomedir\s*\(|\bgetpwuid\b")
PROFONDEUR_MAX = 3


class CommandeIllisible(ValueError):
    pass


def _mots(commande):
    lexeur = shlex.shlex(commande, posix=True, punctuation_chars=";&|()<>")
    lexeur.whitespace_split = True
    lexeur.commenters = ""
    return list(lexeur)


def _commandes_simples(mots):
    courant = []
    for mot in mots:
        if mot in SEPARATEURS or set(mot) <= set(";&|()"):
            if courant:
                yield courant
            courant = []
        else:
            courant.append(mot)
    if courant:
        yield courant


def _premier_mot(simple):
    """(indice, nom) du premier mot qui n'est pas une affectation VAR=valeur."""
    for indice, mot in enumerate(simple):
        if re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", mot):
            continue
        return indice, os.path.basename(mot)
    return len(simple), ""


# --- découpage : shell et corps des redirections << ---------------------------------------------------------------
def _consommateur(ligne_avant):
    """Nature du corps d'une redirection << d'après la commande qui la reçoit : « shell » (par défaut, le plus strict) ou
    « code » (interpréteur connu, ou écriture d'un fichier par cat ou tee)."""
    segment = re.split(r"[;&|()]", ligne_avant)[-1]
    try:
        mots = [os.path.basename(m) for m in shlex.split(segment, posix=True)]
    except ValueError:
        return "shell"
    if any(m in COQUILLES for m in mots):
        return "shell"
    if any(INTERPRETE_CODE.match(m) or m in ECRIVAINS for m in mots):
        return "code"
    return "shell"


def decouper_heredocs(commande):
    """(texte_shell, [(nature, corps, delimiteur_cite)]) ; le texte shell garde les lignes des redirections, sans leurs
    corps. Les guillemets sont suivis d'une ligne à l'autre ; une redirection sans corps ou sans fin lève
    CommandeIllisible."""
    shell, corps_trouves = [], []
    i, n = 0, len(commande)
    simple = double = False
    en_attente, debut_ligne = [], 0
    while i < n:
        c = commande[i]
        if c == "\\" and not simple and i + 1 < n:
            shell.append(commande[i:i + 2])
            i += 2
            continue
        if c == "'" and not double:
            simple = not simple
        elif c == '"' and not simple:
            double = not double
        elif c == "\n" and not simple and not double:
            shell.append(c)
            i += 1
            for tiret, delim, cite, avant in en_attente:
                lignes = []
                while True:
                    if i >= n:
                        raise CommandeIllisible(f"redirection << sans fin (délimiteur {delim!r})")
                    fin = commande.find("\n", i)
                    ligne = commande[i:] if fin < 0 else commande[i:fin]
                    i = n if fin < 0 else fin + 1
                    if (ligne.lstrip("\t") if tiret else ligne) == delim:
                        break
                    lignes.append(ligne)
                corps_trouves.append((_consommateur(avant), "\n".join(lignes), cite))
            en_attente, debut_ligne = [], i
            continue
        elif not simple and not double and commande.startswith("<<", i) and not commande.startswith("<<<", i):
            m = DELIMITEUR.match(commande, i + 2)
            if m:
                delim = m.group(2) or m.group(3) or m.group(5)
                cite = bool(m.group(2) or m.group(3) or m.group(4))
                en_attente.append((m.group(1) == "-", delim, cite, commande[debut_ligne:i]))
                shell.append(commande[i:m.end()])
                i = m.end()
                continue
        shell.append(c)
        i += 1
    if en_attente:
        raise CommandeIllisible("redirection << sans corps")
    return "".join(shell), corps_trouves


def _substitutions(texte):
    """Contenus des substitutions de commande `$(…)` (parenthèses équilibrées) et `…` d'un texte."""
    contenus, i = [], 0
    while True:
        i = texte.find("$(", i)
        if i < 0:
            break
        profondeur, j = 1, i + 2
        while j < len(texte) and profondeur:
            profondeur += {"(": 1, ")": -1}.get(texte[j], 0)
            j += 1
        contenus.append(texte[i + 2:j - 1] if profondeur == 0 else texte[i + 2:])
        i = j
    contenus.extend(re.findall(r"`([^`]*)`", texte))
    return contenus


# --- chemins -------------------------------------------------------------------------------------------------------
def _chemins_hors_dossier_shell(mot, dossier):
    """Chemins absolus, personnels (~) ou remontants (..) qui sortent du dossier, dans un mot du shell."""
    fautifs = []
    candidats = set(re.findall(r"(?:(?<=^)|(?<=[\s'\"=:(`,;|&<>]))(/[^\s'\"`;|&<>(),]*)", mot))
    for morceau in re.split(r"[=:,]", mot):
        if morceau.startswith("/"):
            candidats.add(morceau)
    for chemin in sorted(candidats):
        if chemin in CHEMINS_SYSTEME_PERMIS or chemin_dans(dossier, chemin):
            continue
        fautifs.append(chemin)
    if re.search(r"(?:^|[\s'\"=:(`,;|&<>])~", mot):
        fautifs.append("~ (dossier personnel)")
    for morceau in re.findall(r"[^\s'\"`;|&<>()=:,]*\.\.[^\s'\"`;|&<>()=:,]*", mot):
        if not chemin_dans(dossier, morceau):
            fautifs.append(morceau)
    return fautifs


def _fautifs_code(code, dossier):
    """Dans du code, seuls les littéraux de chaîne sont des chemins : absolu dont le premier composant existe (hors du
    dossier et hors des chemins système permis), personnel (`~`, `~/…`), ou remontant qui sort du dossier ; plus les
    appels qui mènent au dossier personnel (expanduser, Path.home…)."""
    fautifs = []
    for m in LITTERAL.finditer(code):
        brut = next((g for g in m.groups() if g is not None), "")
        s = brut.strip()
        if not s:
            continue
        tete = s.split()[0]
        if re.match(r"^/[A-Za-z0-9_.~-]", tete):
            premier = "/" + tete[1:].split("/")[0]
            if os.path.exists(premier) and tete not in CHEMINS_SYSTEME_PERMIS and not chemin_dans(dossier, tete):
                fautifs.append(tete)
        if s == "~" or s.startswith("~/"):
            fautifs.append("~ (dossier personnel)")
        if re.search(r"(?:^|/)\.\.(?:/|$)", tete) and not chemin_dans(dossier, tete):
            fautifs.append(tete)
    if APPELS_PERSONNELS.search(code):
        fautifs.append("appel vers le dossier personnel")
    return fautifs


# --- évaluation ----------------------------------------------------------------------------------------------------
def _evaluer_shell(texte, dossier, profondeur):
    """(autorisée, motif) pour un texte de shell (corps des redirections déjà retirés)."""
    if profondeur > PROFONDEUR_MAX:
        return False, "commande trop imbriquée"
    try:
        texte_shell, corps = decouper_heredocs(texte)
        mots = _mots(texte_shell)
    except ValueError as erreur:
        return False, f"commande non analysable ({erreur})"
    for simple in _commandes_simples(mots):
        indice, premier = _premier_mot(simple)
        arguments = simple[indice + 1:]
        noms = {os.path.basename(m) for m in simple}
        if (noms & {"sudo", "doas", "pkexec"}) or premier in COMMANDES_PRIVILEGE:
            return False, "élévation de droits interdite (sudo, su, doas, pkexec)"
        reseau = noms & {"curl", "wget", "pip", "pip3", "git"}
        if premier in COMMANDES_RESEAU or reseau:
            return False, f"accès réseau ou dépôt interdit ({premier if premier in COMMANDES_RESEAU else sorted(reseau)[0]})"
        if premier in COMMANDES_ENV:
            return False, f"lecture de l'environnement interdite ({premier})"
        if premier in COMMANDES_ENV_SI_NUES and (not arguments or any(a.startswith("-p") for a in arguments)):
            return False, f"lecture de l'environnement interdite ({premier} sans affectation)"
        if premier == "cd" and (not arguments or arguments[0] in ("-", "~")):
            return False, "cd vers le dossier personnel ou précédent interdit"
        # Arguments de code (`python -c CODE`, `node -e CODE`…) et de shell (`bash -c COMMANDE`), repérés par leur rang.
        rangs_hors_shell = set()
        for k in range(indice + 1, len(simple) - 1):
            if simple[k] in OPTIONS_CODE and INTERPRETE_CODE.match(premier):
                rangs_hors_shell.add(k + 1)
                corps.append(("code", simple[k + 1], False))
            elif simple[k] == "-c" and premier in COQUILLES:
                rangs_hors_shell.add(k + 1)
                corps.append(("shell", simple[k + 1], True))
        fautifs = []
        for rang, mot in enumerate(simple):
            if rang in rangs_hors_shell:
                continue
            fautifs.extend(_chemins_hors_dossier_shell(mot, dossier))
        if fautifs:
            return False, "chemin hors du dossier de l'expérience : " + ", ".join(fautifs[:3])
    for nature, contenu, cite in corps:
        if nature == "shell":
            autorise, motif = _evaluer_shell(contenu, dossier, profondeur + 1)
            if not autorise:
                return False, motif
            continue
        fautifs = _fautifs_code(contenu, dossier)
        if fautifs:
            return False, "chemin hors du dossier de l'expérience (dans le code) : " + ", ".join(fautifs[:3])
        if not cite:  # substitutions de commande exécutées par le shell avant l'interpréteur
            for sous in _substitutions(contenu):
                autorise, motif = _evaluer_shell(sous, dossier, profondeur + 1)
                if not autorise:
                    return False, motif
    return True, "commande autorisée"


def evaluer_commande(commande, dossier):
    """(autorisée, motif) pour une commande Bash exécutée avec `dossier` pour répertoire courant."""
    if not isinstance(commande, str) or not commande.strip():
        return False, "commande vide ou illisible"
    if "environ" in commande or "getenv" in commande:
        return False, "lecture de l'environnement (environ, getenv) interdite"
    if VARIABLE_SENSIBLE.search(commande) or "${!" in commande:
        return False, "lecture d'une variable sensible de l'environnement interdite"
    for motif in MOTIFS_RESEAU:
        if motif in commande:
            return False, f"accès réseau interdit ({motif})"
    return _evaluer_shell(commande, dossier, 0)


def evaluer_appel(outil, entree, dossier):
    """(autorisé, motif) pour un appel d'outil quelconque.

    v46 (tour (c), note de conception § 2.1) : deux trous fermés — le motif de `Glob` (`pattern`) et le filtre de `Grep`
    (`glob`) sont des chemins : absolu hors du dossier, personnel (`~`), remontant (`..`) ou à accolades → refusés
    (`motif_hors_racine`) ; avant, `Glob {"pattern": "/etc/*"}` et `Grep {"glob": "/root/**"}` étaient admis."""
    entree = entree or {}
    if outil == "Bash":
        return evaluer_commande(entree.get("command", ""), dossier)
    if outil in OUTILS_FICHIERS:
        for cle in OUTILS_FICHIERS[outil]:
            chemin = entree.get(cle)
            if chemin is None and outil in ("Glob", "Grep"):
                continue
            if not isinstance(chemin, str) or not chemin:
                return False, f"{outil} : chemin manquant"
            if not chemin_dans(dossier, chemin):
                return False, f"{outil} : chemin hors du dossier de l'expérience ({chemin})"
        if outil in ("Glob", "Grep") and ".." in str(entree.get("pattern", "")):
            return False, f"{outil} : motif remontant hors du dossier"
        for cle in ({"Glob": ("pattern",), "Grep": ("glob",)}.get(outil, ())):  # v46 : motifs de chemin
            if entree.get(cle) is not None:
                motif = motif_hors_racine(entree[cle], dossier, entree.get("path"))
                if motif:
                    return False, f"{outil} : {cle} {motif}"
        return True, f"{outil} dans le dossier"
    return False, f"outil non autorisé pour un agent du pôle : {outil}"


# --- v46 : lecture seule confinée à une racine (tour (c), dossier fermé) ------------------------------------------------
# Proposeurs Claude à outils du kit : `Read`, `Grep`, `Glob` seulement, sur le dossier fermé (copie vérifiée par empreinte,
# racine de lecture) ; aucune écriture, aucune commande. Le crochet est la barrière principale pour les outils de fichiers
# (ils tournent dans le processus du kit, pas dans le bac à sable du système : SUPPOSÉ, à éprouver en réel).
OUTILS_LECTURE = ("Read", "Grep", "Glob")
PARAMETRES_LECTURE = {
    "Read": {"file_path", "offset", "limit", "pages"},
    "Glob": {"pattern", "path"},
    "Grep": {"pattern", "path", "glob", "type", "output_mode", "-A", "-B", "-C", "-n", "-i", "head_limit", "offset",
             "multiline", "context"},
}
METACARACTERES_MOTIF = "*?["


def _composants_interdits(texte):
    """Motif de refus si `texte` porte `~` en tête de composant, un composant `..`, une accolade ou un caractère nul."""
    if "\x00" in texte:
        return "caractère nul"
    if "{" in texte or "}" in texte:
        return "accolades refusées (une alternative pourrait sortir de la racine)"
    composants = texte.replace("\\", "/").split("/")
    if any(c == ".." for c in composants):
        return "remontant (..)"
    if any(c.startswith("~") for c in composants):
        return "dossier personnel (~)"
    return None


def chemin_hors_racine(chemin, racine):
    """None si `chemin` (absolu ou relatif à `racine`) reste dans `racine` après liens résolus (`os.path.realpath`), sans
    `..` ni `~` ; sinon le motif du refus."""
    if not isinstance(chemin, str) or not chemin:
        return "chemin manquant"
    motif = _composants_interdits(chemin)
    if motif:
        return f"{motif} : {chemin}"
    if not chemin_dans(racine, chemin):
        return f"hors de la racine de lecture (liens résolus) : {chemin}"
    return None


def motif_hors_racine(motif, racine, base=None):
    """None si le motif de chemin (`Glob.pattern`, `Grep.glob`) ne peut désigner que des fichiers de `racine` ; sinon le
    motif du refus. Absolu : seulement sous la racine ; relatif : à `base` (dans la racine) ou à la racine ; le préfixe
    sans métacaractère est résolu (`os.path.realpath`) et doit rester dans la racine."""
    if not isinstance(motif, str) or not motif:
        return "motif manquant"
    refus = _composants_interdits(motif)
    if refus:
        return f"{refus} : {motif}"
    if base is not None:
        refus = chemin_hors_racine(base, racine)
        if refus:
            return "base " + refus
    depart = racine if base is None else (base if os.path.isabs(base) else os.path.join(racine, base))
    coupe = min([motif.find(c) for c in METACARACTERES_MOTIF if c in motif] or [len(motif)])
    prefixe = os.path.dirname(motif[:coupe]) if coupe < len(motif) else motif
    cible = prefixe if os.path.isabs(motif) else os.path.join(depart, prefixe)
    if os.path.isabs(motif):
        r = os.path.realpath(racine)
        if not (os.path.normpath(motif) == r or os.path.normpath(motif).startswith(r + os.sep)
                or os.path.normpath(motif).startswith(os.path.normpath(racine) + os.sep)):
            return f"absolu hors de la racine de lecture : {motif}"
    if not chemin_dans(racine, cible or depart):
        return f"hors de la racine de lecture (liens résolus) : {motif}"
    return None


def evaluer_appel_lecture(outil, entree, racine):
    """(autorisé, motif) pour un proposeur à lecture seule confinée à `racine` (v46) : `Read`, `Grep`, `Glob` seulement ;
    tout paramètre inconnu refusé ; chemins (`file_path`, `path`) et motifs de chemin (`Glob.pattern`, `Grep.glob`) hors de
    la racine refusés — absolus hors racine, `..`, `~`, accolades, liens symboliques résolus qui sortent ; toute écriture
    (`Write`, `Edit`, `MultiEdit`, `NotebookEdit`) et toute commande (`Bash`) refusées ; tout autre outil (`mcp__…`,
    `WebFetch`, `Task`…) refusé."""
    entree = entree if isinstance(entree, dict) else {}
    if outil in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        return False, f"écriture interdite (lecture seule du dossier fermé) : {outil}"
    if outil == "Bash":
        return False, "commande interdite (lecture seule du dossier fermé) : Bash"
    if outil not in OUTILS_LECTURE:
        return False, f"outil non autorisé en lecture seule : {outil}"
    inconnus = sorted(set(entree) - PARAMETRES_LECTURE[outil])
    if inconnus:
        return False, f"{outil} : paramètre inconnu refusé ({', '.join(inconnus)})"
    if outil == "Read":
        refus = chemin_hors_racine(entree.get("file_path"), racine)
        if refus:
            return False, f"Read : {refus}"
        return True, "Read dans la racine de lecture"
    if entree.get("path") is not None:
        refus = chemin_hors_racine(entree["path"], racine)
        if refus:
            return False, f"{outil} : path {refus}"
    cle_motif = "pattern" if outil == "Glob" else "glob"
    if outil == "Glob" or entree.get("glob") is not None:
        refus = motif_hors_racine(entree.get(cle_motif), racine, entree.get("path"))
        if refus:
            return False, f"{outil} : {cle_motif} {refus}"
    if outil == "Grep" and not isinstance(entree.get("pattern"), str):
        return False, "Grep : motif de recherche manquant"
    return True, f"{outil} dans la racine de lecture"


def fabriquer_crochet_lecture(racine, max_demandes=1000, lire_depense=None, plafond_usd=None, seuil_avertissement=0.8):
    """v46 : crochet `PreToolUse` de lecture seule confinée à `racine`. Consigne chaque appel (`crochet.journal` : outil,
    entrée, autorisé, motif, rang) ; au-delà de `max_demandes` appels admis, refuse tout (garde-fou anti-boucle,
    `crochet.incident` mis) ; si `lire_depense` (dépense de la session lue au relais, en dollars) et `plafond_usd` sont
    donnés, le premier appel après `seuil_avertissement` × plafond est refusé avec « il te reste X USD : rends ta fiche »
    (`crochet.avertissement` mis) — le motif d'un refus est rendu au modèle comme résultat de l'outil (SUPPOSÉ, à éprouver)."""
    racine = os.path.realpath(racine)
    etat = {"admis": 0}

    async def crochet(input_data, tool_use_id, context):
        outil = input_data.get("tool_name", "")
        entree = input_data.get("tool_input") or {}
        autorise, motif = evaluer_appel_lecture(outil, entree, racine)
        if autorise and etat["admis"] >= max_demandes:
            autorise, motif = False, (f"garde-fou anti-boucle : {max_demandes} demandes de lecture admises ; plus aucune "
                                      "lecture : rends ta fiche")
            crochet.incident = {"type": "garde-fou anti-boucle", "max_demandes_lecture": max_demandes,
                                "rang": len(crochet.journal) + 1}
        if autorise and lire_depense is not None and plafond_usd and not crochet.avertissement:
            try:
                depense = float(lire_depense())
            except Exception:  # noqa: BLE001 — relais illisible : aucun avertissement possible, dit au journal
                depense = None
                crochet.relais_illisible = True
            if depense is not None and depense >= seuil_avertissement * plafond_usd:
                reste = max(0.0, plafond_usd - depense)
                autorise, motif = False, f"avertissement de budget : il te reste {reste:.2f} USD : rends ta fiche"
                crochet.avertissement = {"rang": len(crochet.journal) + 1, "depense_usd": round(depense, 6),
                                         "reste_usd": round(reste, 6)}
        if autorise:
            etat["admis"] += 1
        crochet.journal.append({"rang": len(crochet.journal) + 1, "outil": outil,
                                "entree": {k: v for k, v in entree.items() if isinstance(v, (str, int, float, bool))},
                                "autorise": autorise, "motif": motif})
        if autorise:
            return {}
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": motif}}

    crochet.dossier = racine
    crochet.journal = []
    crochet.incident = None
    crochet.avertissement = None
    crochet.relais_illisible = False
    crochet.max_demandes = max_demandes
    return crochet


def fabriquer_crochet(dossier):
    """Crochet `PreToolUse` au format du Claude Agent SDK : refuse avec un motif, sinon laisse le flux normal."""
    dossier = os.path.realpath(dossier)

    async def crochet(input_data, tool_use_id, context):
        autorise, motif = evaluer_appel(input_data.get("tool_name", ""), input_data.get("tool_input") or {}, dossier)
        if autorise:
            return {}
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": motif}}

    crochet.dossier = dossier
    return crochet
