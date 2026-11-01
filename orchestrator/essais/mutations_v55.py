"""Banc de mutations de la v55 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**).

Corrige deux défauts du banc v54 relevés par CL19 (CL19-08, section E) :

1. **`super()` à la recompilation** : une méthode recompilée hors de sa classe perdait la cellule `__class__` (« super():
   __class__ cell not found ») ; la mutation « DEP3 analyseur non exigé » était « tuée » par ce défaut du banc. Le source muté
   est maintenant compilé dans une fabrique qui fournit `__class__` = la classe qui définit la méthode.
2. **Raison de l'échec** : une mutation n'est « tuée » que si au moins un essai visé échoue avec un texte d'échec qui
   correspond au **motif attendu** (expression régulière propre à la mutation). Un échec d'une autre nature est compté
   « tuée pour une autre raison » (non tuée) ; un échec dû au banc (`__class__ cell`, `NameError`, `SyntaxError`) est compté
   « défaut du banc ». Aucun fichier n'est modifié (fonction recompilée en mémoire, substituée, puis restaurée).

Contenu : les 56 mutations de la v54 (sur le code v54, avec leurs essais v54, motif ajouté) et les mutations des gardes
nouvelles de la v55 (essais v55).

  python3 -B essais/mutations_v55.py [--raisons]      (depuis le dossier de livraison ; une ligne par mutation)
"""

import inspect
import io
import os
import re
import sys
import tempfile
import textwrap
import traceback
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

import aides  # noqa: E402

aides.BASE = tempfile.mkdtemp(prefix="pole-mutations-v55-")
_PREMIER = aides.BASE
import essais.aides as _ea  # noqa: E402

_ea.BASE = aides.BASE

from essais import mutations_v54 as m54  # noqa: E402  (liste v54 seulement ; son principal n'est pas joué)
from pole import bisociateur_v55, configuration_v55, coffre_v55, course2_v55, etage_entre_generations_v55  # noqa: E402
from pole import gardes_e0_v55, noyau_v55, prepilote_v55  # noqa: E402

import atexit  # noqa: E402
import shutil  # noqa: E402

for _d in {_PREMIER, aides.BASE, _ea.BASE, m54.aides.BASE}:  # dossiers temporaires des bancs v54 et v55 : retirés en fin de banc
    atexit.register(shutil.rmtree, _d, True)
aides.BASE = _ea.BASE = m54.aides.BASE = tempfile.mkdtemp(prefix="pole-mutations-v55-")
atexit.register(shutil.rmtree, aides.BASE, True)
T = "essais.test_v55_corrections."
BANC = re.compile(r"super\(\): __class__ cell not found|NameError|SyntaxError|IndentationError")
NR = r"not raised"

# --- motifs des 56 mutations v54 (raison attendue de l'échec) ----------------------------------------------------------------
MOTIFS_V54 = {
    "CL18-01 consommation d'un juge omise": r"AssertionError: 48 != 81|AssertionError: \d+ != \d+",
    "CL18-01 coût perdu sur exception (pas de pire cas)": r"AssertionError: 0\.0 != 0\.5",
    "CL18-02 coupure ignorée par le budget": r"\+ non_mesuree_budget|evenement\"\] == \"coupure-budget\"",
    "CL18-02 marque de coupure non posée": r"c\.get\(\"coupure\"\)|evenement\"\] == \"coupure-budget\"",
    "CL18-02 nœud ignoré (course enchaîne)": r"NoeudArret not raised",
    "CL18-03 égalité → « au moins »": r"\[montant plus grand\].*GoRefuse not raised|GoRefuse not raised",
    "CL18-03 plusieurs montants acceptés": r"plusieurs montants",
    "CL18-03 « par lancement » accepté": r"\[par lancement\]",
    "CL18-03 portée ignorée (toujours N × S17)": r"exigé \(reçu 'course'\)|AssertionError: [\d.]+ != [\d.]+",
    "CL18-05 passeport sans recalcul": r"assertFalse\(g\.aiguilleur\.a_passeport\(f\)\)",
    "CL18-06 préfixe → mot entier": r"\[des témoins\]|\[deux fusions\]|\[\] is not true",
    "CL18-06 fiche exclue → toujours arrêt": r"EtiquetteDansEntree: A4 : étiquette interdite dans la fiche servie",
    "CL18-08 entrée du bisociateur non filtrée": r"set\(q\.split\(\"\|\"\)\) <= kimi",
    "CL18-08 passe « tableau » toujours jugée": r"'passe2' unexpectedly found",
    "CL18-10 refus technique compté au débordement": r"'prop-kimi' unexpectedly found",
    "CL18-10 metteur toujours arrêté": r"arret_metteur_fusion=False\).*True != False",
    "CL18-12 sessions non opaques": r"len\(n\) == 16",
    "CL18-12 A4 sur l'entrée complète retirée": r"EtiquetteDansEntree not raised",
    "CL18-13 morceaux de nom de clé ignorés": r"MachineNonJetable not raised",
    "CL18-14 kappa 1 sur marges constantes": r"1\.0 is not None",
    "CL18-14 verdict absent compté non notable": r"AssertionError: 0\.5 != 1\.0",
    "CL18-16 cumul écrêté": r"\+ non_mesuree|AssertionError: [\d.]+ != [\d.]+",
    "CL18-16 M6b coupée fait tomber C13": r"\+ non_mesuree_hors_porte",
    "CL18-17 héritage sans garde A4": r"EtiquetteDansEntree not raised",
    "CL18-17 n compté toutes cases ensemble": r"non produit \(effectif\)",
    "I-1 nom de structure libre": r"BisociationRefusee not raised",
    "I-2 désaccord par valeur non éprouvé": r"not raised|ligne 24 \(ÉCHEC",
    "I-2 ordre non vérifié": r"BisociationRefusee not raised",
    "I-3 seuils S28 de l'annexe non exigés": r"'I-3' not found",
    "I-4 définitions non vérifiées": r"assertFalse\(d\[\"produit\"\]\)",
    "I-4 consigne non vérifiée": r"assertFalse\(d\[\"produit\"\]\)",
    "I-5 règle de divergence ignorée": r"None != \('n1'",
    "I-6 poids négatif accepté": r"'I-6' not found",
    "I-6 tables non contrôlées": r"'I-6' not found",
    "I-7 cause « niches indistinctes » perdue": r"niches indistinctes",
    "I-8 paire reportée au bras suivant": r"\{'basique': \[\], 'meta': \[\]\}|AssertionError: \{",
    "I-9 une seule empreinte acceptée": r"assertFalse\(d\[\"produit\"\]\)",
    "I-9 décision R-NNN non exigée": r"assertFalse\(d\[\"produit\"\]\)",
    "I-10 profil vide accepté": r"'profil vide' not found",
    "I-10 jeu d'essai absent accepté": r"jeu_essai_non_vacuite absent|'I-10' not found|not raised",
    "A3 échecs consécutifs sans arrêt": r"AssertionError: 10 != 3|ligne 25 \(ÉCHEC",
    "A3 délai ignoré": r"NoeudArret not raised|ligne 25 \(ÉCHEC",
    "A11 limite sans arrêt": r"ligne 32 \(ÉCHEC",
    "A11 bascule acceptée": r"BasculeInterdite not raised|ligne 1 \(ÉCHEC",
    "A14 jamais dépassée": r"\+ non_mesuree_technique|ligne 28 \(ÉCHEC",
    "A5 maximum d'exclus ignoré": r"NoeudArret not raised|'e4_aiguillage' unexpectedly found",
    "S6 ancres non contrôlées": r"NoeudArret not raised",
    "A8 longueur non contrôlée": r"NoeudArret not raised",
    "A6 ambigus ignorés": r"NoeudArret not raised",
    "A7 S19 ignorée": r"NoeudArret not raised",
    "A13 squelettes non revérifiés": r"NoeudArret not raised",
    "Ligne 31 source de M6b non cherchée": r"m6b-fiche-arretee|ligne 31 \(ÉCHEC",
    "É0 table R5 sans refus": r"GardesE0Refusees not raised",
    "DEP3 analyseur non exigé": r"EtageUnAbsent not raised",
    "DEP4 non exigée": r"'confirmation de DEP4' not found|\"confirmation de DEP4\" in m",
    "Plan du pré-pilote non imposé": r"ConfigurationRefusee not raised",
}

C = course2_v55.GenerationV55
P = prepilote_v55.PrePiloteV55
MUTATIONS_V55 = [
    ("CL19-01 ligne 20 : source absente non acceptée", gardes_e0_v55, "rejouer_gardes_v55",
     "elif isinstance(dgk, dict) and dgk.get(\"cause\") == CAUSE_SOURCE_ABSENTE:", "elif False:",
     [T + "TestCL19_01SourcesAbsentes"], r"GardesE0Refusees: A12.*ligne 20"),
    ("CL19-01 lignes 22b-24 : annexe absente non acceptée", gardes_e0_v55, "rejouer_gardes_v55",
     "garde sans objet, déclarée ; réserve jointe (O15)\",\n                  statut=SANS_OBJET)",
     "garde sans objet, déclarée ; réserve jointe (O15)\",\n                  statut=None)",
     [T + "TestCL19_01SourcesAbsentes"], r"GardesE0Refusees: A12.*ligne 22b"),
    ("CL19-01 « sans objet » refusé au départ", gardes_e0_v55, "rejouer_gardes_v55",
     "x[\"statut\"] not in STATUTS_SATISFAITS]", "x[\"statut\"] != REJOUEE]",
     [T + "TestCL19_01SourcesAbsentes"], r"GardesE0Refusees: A12.*sans objet"),
    ("CL19-02 pré-pilote : analyse après nœud", P, "executer", "if self.noeud:\n            raise NoeudArret(self.noeud)",
     "if False:\n            raise NoeudArret(self.noeud)", [T + "TestCL19_02RienApresNoeud"], r"NoeudArret not raised|dépôt 'pp2-e5-detail' : sceau absent"),
    ("CL19-02 course : classement après nœud", C, "executer", "if self.noeud:  # CL19-02", "if False:  # CL19-02",
     [T + "TestCL19_02RienApresNoeud"], r"assertFalse\(fin\[\"coffre\"\]\[\"fin_e9\"\]\)"),
    ("CL19-02 attestation É5bis non écrite", P, "executer", "if \"É5bis\" in self.noeud and self.pp[\"temoins\"][\"version\"] == 1:",
     "if False:", [T + "TestCL19_02RienApresNoeud", T + "TestCL19_06Externes"], r"FileNotFoundError.*temoins-v1-e5bis"),
    ("CL19-03 copie de la clé gardée en mémoire", P, "etape_e1_redacteur", "self.__dict__.pop(\"_cle_classes\", None)", "pass",
     [T + "TestCL19_03CleDesClasses"], r"hasattr\(g, \"_cle_classes\"\)"),
    ("CL19-03 classe gardée dans le plan des fonds", P, "etape_e1_redacteur",
     "self.fonds = [{k: v for k, v in f.items() if k != \"classe\"} for f in self.fonds]", "pass",
     [T + "TestCL19_03CleDesClasses"], r"\"classe\" not in f for f in g\.fonds"),
    ("CL19-03 clé lue hors journal", P, "_lire_cle", "return self.coffre.lire_pour_garde(self.tache(\"cle-classes\"), role, raison)",
     "return 0, json.load(open(os.path.join(self.coffre.dossier, self.tache(\"cle-classes\") + \".json\")))",
     [T + "TestCL19_03CleDesClasses"], r"jeton de lecture 0 inconnu"),
    ("CL19-03 lecture non déclarée permise", coffre_v55.CoffreV55, "lire_pour_garde", "if (nom, role) not in self.lectures_permises:",
     "if False:", [T + "TestCL19_03CleDesClasses"], r"LectureAvantFinE9 not raised"),
    ("CL19-03 identifiants en sortie de garde", coffre_v55.CoffreV55, "noter_sortie_garde",
     "if not isinstance(k, str) or not (v is None or isinstance(v, (bool, int, float))):", "if False:",
     [T + "TestCL19_03CleDesClasses"], r"SortieDeGardeRefusee not raised"),
    ("CL19-03 ordre d'É6 non trié", P, "etape_e6_juges", "for i in sorted(self.rendus):", "for i in sorted(self.rendus, reverse=True):",
     [T + "TestCL19_03CleDesClasses"], r"Lists differ"),
    ("CL19-03 É9 réduite par la clé d'antériorité", P, "etape_e9_anteriorite", "garde = set(lire_liste_reduite(self.conf))",
     "garde = {f[\"ident\"] for f in fiches if json.loads(self.piece(an[\"cle\"])).get(f[\"ident\"]) != \"sans_defaut\"}",
     [T + "TestCL19_03CleDesClasses"], r"'anteriorite_cle' unexpectedly found"),
    ("CL19-03 liste de réduction non scellée acceptée", prepilote_v55, "lire_liste_reduite",
     "if not verifier_scelle(chemin_piece(conf, conf[\"pieces\"][nom][\"chemin\"])):", "if False:",
     [T + "TestCL19_03CleDesClasses"], NR),
    ("CL19-03 longueur de la liste non contrôlée", prepilote_v55, "lire_liste_reduite", " or len(liste) != attendu:", ":",
     [T + "TestCL19_03CleDesClasses"], NR),
    ("CL19-04 sessions sous la sortie", noyau_v55.OrchestreV55, "session", "d = os.path.join(self.racine_sessions, opaque)",
     "d = os.path.join(self.sortie, \"sessions\", opaque)", [T + "TestCL19_04Sessions"], r"SessionsMalPlacees: dossier de session"),
    ("CL19-04 racine sous la sortie acceptée", noyau_v55, "verifier_emplacement_sessions", "if _sous(base, sortie):", "if False:",
     [T + "TestCL19_04Sessions"], NR),
    ("CL19-04 lien symbolique accepté", noyau_v55, "verifier_emplacement_sessions",
     "if os.path.realpath(base) != os.path.abspath(base):", "if False:", [T + "TestCL19_04Sessions"], NR),
    ("CL19-05 « ≈ » accepté", configuration_v55, "lire_plafond", "if APPROX.search(cellule):", "if False:",
     [T + "TestCL19_05LigneDeGo"], NR),
    ("CL19-05 nombre étranger accepté", configuration_v55, "lire_plafond", "if any(abs(x - ms[0][0]) > 1e-9 for x in nombres):",
     "if False:", [T + "TestCL19_05LigneDeGo", T + "TestLanceurV7"], NR + r"|nombre étranger"),
    ("CL19-05 milliers lus comme en v54", configuration_v55, "lire_plafond", "ms = montants_v55(cellule)",
     "ms = [(float(m.group(1).replace(\",\", \".\")), m.group(2)) for m in c54.MONTANT.finditer(cellule)]",
     [T + "TestCL19_05LigneDeGo"], r"GoRefuse: A15 : nombre étranger"),
    ("CL19-05 « par génération » accepté", configuration_v55, "lire_plafond", "if PAR_UNITE.search(cellule):", "if False:",
     [T + "TestCL19_05LigneDeGo"], NR),
    ("CL19-05 phrase DEP4 non lue", configuration_v55, "verifier_dependances_lancement_v55",
     "if phrase.strip() not in c53.texte_piece(conf, nom):", "if False:", [T + "TestCL19_05LigneDeGo"], r"ne contient pas la phrase\" in m"),
    ("CL19-06 script du résultat non vérifié", gardes_e0_v55, "verifier_resultat_externe",
     " or conf[\"pieces\"][script][\"sha256\"] != res.get(\"script_sha256\"):", ":", [T + "TestCL19_06Externes"], NR),
    ("CL19-06 résultat non scellé accepté", gardes_e0_v55, "verifier_resultat_externe", "if not verifier_scelle(",
     "if False and not verifier_scelle(", [T + "TestCL19_06Externes"], NR),
    ("CL19-06 identifiant non vérifié", gardes_e0_v55, "verifier_resultat_externe",
     "if res.get(\"ligne\") != n or res.get(\"identifiant\") != declaration[\"identifiant\"]:", "if res.get(\"ligne\") != n:",
     [T + "TestCL19_06Externes"], NR),
    ("CL19-06 version 2 sans attestation", prepilote_v55, "verifier_configuration_pre_pilote_v55",
     "if pp[\"temoins\"][\"version\"] == 2:\n        lire_attestation_v1(conf)", "if False:\n        lire_attestation_v1(conf)",
     [T + "TestCL19_06Externes"], NR),
    ("CL19-07 ancre sans borne après", prepilote_v55, "motif_ancre",
     "apres = (r\"(?!\\w)\" if a[-1:].isalnum() else \"\") + (r\"(?![.,]\\d)\" if a[-1:].isdigit() else \"\")", "apres = \"\"",
     [T + "TestCL19_07S6"], r"1\.0 != 0\.5|NoeudArret not raised"),
    ("CL19-07 extension décimale acceptée", prepilote_v55, "motif_ancre", "(r\"(?![.,]\\d)\" if a[-1:].isdigit() else \"\")", "\"\"",
     [T + "TestCL19_07S6"], r"1\.0 != 0\.5"),
    ("CL19-07 ancre sans borne avant", prepilote_v55, "motif_ancre", "avant = (r\"(?<!\\w)\" if a[:1].isalnum() else \"\")",
     "avant = (\"\")", [T + "TestCL19_07S6"], r"1\.0 != 0\.5"),
    ("CL19-07 nombres ajoutés ignorés", P, "_rendre", "if s6[\"nombres_ajoutes\"] > self.pp[\"s6\"][\"nombres_ajoutes_max\"]:",
     "if False:", [T + "TestCL19_07S6"], NR),
    ("CL19-08 exception quelconque comptée « arrêtée »", gardes_e0_v55, "_arrete",
     "except Exception:  # noqa: BLE001 — autre exception : la garde n'a pas arrêté pour sa raison\n        return False",
     "except Exception:  # noqa: BLE001\n        return True", [T + "TestCL19_08Artefacts"], r"leve\(KeyError\(\"x\"\)\)"),
    ("CL19-08 ligne 21 non jouée par la génération", C, "etape_etiquettes",
     "verifier_bascule_gk(self.bras_decl_e0, self.bras_decl)", "pass", [T + "TestCL19_08Artefacts"], NR),
    ("CL19-08 changement de déclaration non vu", course2_v55, "verifier_bascule_gk",
     "if (decl_courante or {}).get(\"gu_krenn\") != d0:", "if False:", [T + "TestCL19_08Artefacts"], NR),
    ("CL19-08 ligne 22b sans artefact de lecture", gardes_e0_v55, "rejouer_gardes_v55",
     "art = (_arrete(lambda: lire(os.path.join(tmp, \"absente.md\"), sha), BisociationRefusee, \"absente\")\n"
     "                   and _arrete(lambda: lire(copie, sha_copie), BisociationRefusee, \"contre_lecture\")\n"
     "                   and _arrete(lambda: lire(chemin, \"0\" * 64), BisociationRefusee, \"empreinte différente\")\n"
     "                   and ", "art = (", [T + "TestCL19_08Artefacts"], NR),
    ("CL19-09 empreinte du brouillon relu non cherchée", bisociateur_v55, "lire_annexe_meta_v55",
     "if piece[1] not in p[\"contre_lecture\"]:", "if False:", [T + "TestCL19_09Annexe"], r"KeyError: 'motif'"),
    ("CL19-09 R-000 accepté", bisociateur_v55, "lire_annexe_meta_v55", "if not any(int(d) > 0 for d in", "if False and not any(int(d) > 0 for d in",
     [T + "TestCL19_09Annexe"], r"KeyError: 'motif'"),
    ("CL19-09 différence non vérifiée", bisociateur_v55, "lire_annexe_meta_v55", "    difference_limitee(relu, annexe)\n", "",
     [T + "TestCL19_09Annexe"], r"KeyError: 'motif'"),
    ("CL19-10 modèle servi absent accepté", noyau_v55.OrchestreV55, "appel",
     "controle_a2(a[\"r\"].statut, getattr(a[\"r\"], \"modele_servi\", None), kw.get(\"modele\"))", "None",
     [T + "TestCL19_10Ecarts"], NR),
    ("CL19-10 cause (iii) perdue", C, "_notes", "causes[\"meta\"] = \"non produit (moins de 2 fiches étiquetées)\"", "pass",
     [T + "TestCL19_10Ecarts"], r"moins de 2 fiches étiquetées"),
    ("CL19-10 cause (iv) perdue", C, "_notes", "causes[\"gu_krenn\"] = (\"non produit (moins de 2 fiches notables)\" if",
     "causes[\"gu_krenn\"] = (\"non produit (aucune paire éligible)\" if", [T + "TestCL19_10Ecarts"], r"moins de 2 fiches notables"),
    ("CL19-11 _PAT accepté", etage_entre_generations_v55, "nom_de_cle_v55", " or n.endswith(\"_PAT\")", "",
     [T + "TestCL19_11MachineJetable"], NR),
    ("CL19-11 TOKENIZERS_PARALLELISM refusé", etage_entre_generations_v55, "nom_de_cle_v55",
     "if n in NOMS_SANS_SECRET:\n        return False", "if False:\n        return False", [T + "TestCL19_11MachineJetable"],
     r"MachineNonJetable: .*TOKENIZERS_PARALLELISM"),
    ("CL19-12 entrée de rendu gardée sur le squelette seul", P, "_rendre",
     "fv.garde(entree, self.interdites, self.a4_mode, \"l'entrée complète d'un rendu (consigne comprise)\")", "None",
     [T + "TestCL19_12Mineurs"], NR),
    ("CL19-12 relecteur muet compté ambigu", P, "_boite_e5", "non_relus.append(i)\n            continue", "lu = {}",
     [T + "TestCL19_12Mineurs"], r"does not match"),
    ("CL19-12 cohérence de D-g non vérifiée", configuration_v55, "verifier_dependances_lancement_v55",
     "if isinstance(mot, str) and MARQUEUR not in mot and (", "if False and (", [T + "TestCL19_12Mineurs"], r"\"CL19-12\" in m for m"),
    ("CL19-09 spécification non exigée au lancement réel", None, "ideation_v7.executer",
     "if args.moteur == \"reel\" and spec[\"conforme\"] is not True:", "if False:", [T + "TestCL19_09Annexe"], r"'CL19-09' not found"),
]


def _classe_definissante(cible, nom):
    if not isinstance(cible, type):
        return None
    for k in cible.__mro__:
        if nom in vars(k):
            return k
    return None


def _remplacer_partout(ancien, nouveau):
    for nom, mod in list(sys.modules.items()):
        if mod is None or not (nom.startswith("pole") or nom.startswith("essais") or nom.startswith("aides")
                               or nom.startswith("ideation_v7")):
            continue
        for k, v in list(vars(mod).items()):
            if v is ancien:
                setattr(mod, k, nouveau)


def appliquer(cible, nom, ancien, nouveau):
    if cible is None:  # mutation du lanceur : le source est relu à chaque chargement ; on mute le chargeur
        return _appliquer_lanceur(nom, ancien, nouveau)
    proprietaire = _classe_definissante(cible, nom) or cible
    brut = inspect.getattr_static(proprietaire, nom)
    est_static = isinstance(brut, staticmethod)
    f = brut.__func__ if est_static else (brut if not isinstance(proprietaire, type) else getattr(proprietaire, nom))
    f = getattr(f, "__func__", f)
    src = textwrap.dedent(inspect.getsource(f))
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois")
    mod = sys.modules[f.__module__]
    espace = dict(vars(mod))
    code = ("def __fabrique_mutation__(__class__):\n" + textwrap.indent(src.replace(ancien, nouveau), "    ")
            + f"\n    return {f.__name__}\n")
    exec(compile(code, f"<mutation {f.__qualname__}>", "exec"), espace)
    g = espace["__fabrique_mutation__"](proprietaire if isinstance(proprietaire, type) else None)
    g = getattr(g, "__func__", g)
    if isinstance(proprietaire, type):
        setattr(proprietaire, nom, staticmethod(g) if est_static else g)
    else:
        _remplacer_partout(f, g)

    def restaurer():
        if isinstance(proprietaire, type):
            setattr(proprietaire, nom, brut)
        else:
            _remplacer_partout(g, f)
    return restaurer


def _appliquer_lanceur(nom, ancien, nouveau):
    import importlib.machinery
    chemin = os.path.join(RACINE, "demonstrations", "ideation_v7.py")
    with open(chemin, encoding="utf-8") as x:
        src = x.read()
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois")
    orig = importlib.machinery.SourceFileLoader.get_data

    def get_data(self, path):
        if os.path.realpath(path) == os.path.realpath(chemin):
            return src.replace(ancien, nouveau).encode("utf-8")
        return orig(self, path)
    importlib.machinery.SourceFileLoader.get_data = get_data

    def restaurer():
        importlib.machinery.SourceFileLoader.get_data = orig
    return restaurer


def jouer(noms):
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in noms)
    flux = io.StringIO()
    r = unittest.TextTestRunner(stream=flux, verbosity=0).run(suite)
    echecs = [(str(t), txt) for t, txt in r.failures + r.errors]
    return r.testsRun, echecs


def classer(echecs, motif):
    if not echecs:
        return "SURVIVANTE"
    if any(re.search(motif, t + "\n" + txt, re.S) for t, txt in echecs):  # nom de l'essai (sous-essai compris) et trace
        return "tuée"
    if any(BANC.search(txt) for _, txt in echecs):
        return "DÉFAUT DU BANC"
    return "TUÉE POUR UNE AUTRE RAISON"


def _derniere_ligne(txt):
    lignes = [l for l in txt.strip().splitlines() if l.strip()]
    return lignes[-1][:220] if lignes else ""


def principal(argv=None):
    raisons = "--raisons" in (argv if argv is not None else sys.argv[1:])
    tout = [(lib, cib, nom, anc, nou, ess, MOTIFS_V54.get(lib, r"(?!)")) for lib, cib, nom, anc, nou, ess in m54.MUTATIONS]
    tout += MUTATIONS_V55
    noms = sorted({x for m in tout for x in m[5]})
    for n in noms:
        unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in tout:
        try:
            restaurer = appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  {libelle} : {e}")
            continue
        try:
            n, echecs = jouer(essais)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
        verdict = classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  [{'v54' if libelle in MOTIFS_V54 else 'v55'}] {libelle} : {len(echecs)}/{n} essais en échec")
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {_derniere_ligne(txt)}")
    apres = jouer(noms)
    total = len(tout)
    print(f"mutations : {total} (v54 : {len(m54.MUTATIONS)}, v55 : {len(MUTATIONS_V55)}) ; tuées pour la raison attendue : "
          f"{comptes.get('tuée', 0)} ; tuées pour une autre raison : {comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; "
          f"défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : {comptes.get('SURVIVANTE', 0)} ; "
          f"non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
