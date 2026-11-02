"""Banc de mutations de l'étage des juges d'idéation v2 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour
la bonne raison**) — cœur `pole/juges_idees_v2.py` et lanceur `demonstrations/validation_juges_idees_v2.py`.

Mécanique des bancs v55 et v56 (`essais/mutations_v55.py`) : la fonction visée est recompilée en mémoire avec le fragment
muté, substituée, puis restaurée ; aucun fichier n'est modifié. Une mutation n'est « tuée » que si au moins un essai visé échoue
avec un texte qui correspond au **motif attendu** ; un échec d'une autre nature est « tuée pour une autre raison » (non tuée), un
échec du banc lui-même (`__class__`, `NameError`, `SyntaxError`) « défaut du banc ». Le banc ne charge pas les bancs v54 à v56
(ils importent toutes les couches) ; il recopie leur mécanique, en plus court. Les courses à juges scriptés mémorisées par le
module d'essais sont oubliées avant chaque mutation (sinon une mutation du jeu ou de la lecture ne serait pas vue).

  python3 -I -B essais/mutations_juges_idees_v2.py [--raisons]      (depuis le dossier orchestrator)
"""

import contextlib
import inspect
import io
import os
import re
import sys
import textwrap
import traceback
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import test_juges_idees_v2 as T  # noqa: E402

J, L = T.J, T.lanceur
P = "essais.test_juges_idees_v2."
BANC = re.compile(r"__class__ cell not found|NameError|SyntaxError|IndentationError")
NR = r"not raised"
FAUX = r"True is not false"
REFUS_MANQUE = r"0 != 2"

MUTATIONS = [
    # --- preuve citée ---------------------------------------------------------------------------------------------------------
    ("citation de la fiche non cherchée dans la source", J, "verifier_citation",
     "if not any(c in normaliser_citation(s) for s in sources):", "if False:", [P + "Citations"], FAUX),
    ("citation commune aux deux fiches admise", J, "verifier_citation",
     "if any(c in normaliser_citation(s) for s in interdites_sources):", "if False:", [P + "Citations"], FAUX),
    ("citation du dossier non exigée", J, "lire_comparaison", "if dossier_a_preuves(dossier):", "if False:", [P + "Citations"], FAUX),
    ("citation prise dans l'autre fiche admise comme source", J, "lire_comparaison",
     'valeurs_textuelles(servies[pref]["contenu"]), CITATION_FICHE_MIN',
     'valeurs_textuelles(servies[pref]["contenu"]) + valeurs_textuelles(autre["contenu"]), CITATION_FICHE_MIN',
     [P + "Citations"], r"'introuvable' not found"),
    ("critère hors de la liste admis", J, "lire_comparaison", 'if c.get("critere") not in CRITERES_V2:', "if False:",
     [P + "Citations"], FAUX),
    ("identifiant choisi hors des deux fiches servies admis", J, "lire_comparaison", "if pref not in servies:", "if False:",
     [P + "Citations"], r"KeyError|NoneType"),
    # --- gardes A4, matériaux --------------------------------------------------------------------------------------------------
    ("garde A4 retirée de l'entrée complète d'une paire", J, "entree_paire",
     'garde_a4(entree, interdites, mode, "l\'entrée complète")', "pass", [P + "Entrees"], r"ProtocoleRefuse not raised"),
    ("contrôle de forme des témoins ignoré", J, "exiger_materiaux", 'if not forme["conforme"]:', "if False:",
     [P + "Materiaux"], r"ProtocoleRefuse not raised"),
    ("vérité connue des témoins non exigée", J, "exiger_materiaux", "if ecarts:", "if False:", [P + "Materiaux"], NR),
    ("loi fausse non contrôlée contre la table", J, "verifier_materiaux",
     'if classe == "fausse_redigee" and not (xa - xb >= ECART_VRAI_MIN and abs(oa - ob) <= ECART_NUL_MAX):', "if False:",
     [P + "Materiaux"], FAUX.replace("True is not false", "False is not true")),
    # --- plan, famille -------------------------------------------------------------------------------------------------------
    ("règle de famille désactivée", J, "juge_admissible", "return all(famille_juge not in f for f in familles)", "return True",
     [P + "Plan"], r"False is not true|ProtocoleRefuse not raised"),
    ("juge de la famille des gabarits admis", J, "etapes_v1", "if j[\"famille\"] == FAMILLE_AUTEUR_TEMOINS:", "if False:",
     [P + "Plan"], r"ProtocoleRefuse not raised"),
    ("paires du juge B non restreintes aux paires mélangées", J, "etapes_v1",
     "melangees = [p for p in graphes[(lot[\"nom\"], 1)][\"paires\"] if qualite[p[0]] != qualite[p[1]]]",
     "melangees = list(graphes[(lot[\"nom\"], 1)][\"paires\"])", [P + "Plan"], r"False is not true"),
    ("graphe : degré impair sur un nombre impair de fiches admis", J, "graphe_circulant", "if degre % 2 == 1 and n % 2 == 1:",
     "if False:", [P + "Plan"], r"ProtocoleRefuse not raised"),
    # --- Bradley et Terry, verdicts --------------------------------------------------------------------------------------------
    ("effet de position non rendu", J, "ajuster_bt", '"position": float(x[n])', '"position": 0.0', [P + "BradleyTerry"],
     r"0\.0 != 0\.4|not greater than 1"),
    ("budget de notables non appliqué", J, "verdicts_lot", "retenus = candidats[:k]", "retenus = candidats", [P + "Verdicts"],
     r"Lists differ|True is not false"),
    ("plancher des ancres retiré", J, "verdicts_lot", "if plancher is None or forces[i] > plancher + EPSILON_EGALITE",
     "if True", [P + "Verdicts"], r"Lists differ|True is not false"),
    ("ancres inversées ignorées", J, "verdicts_lot", "if tb - tm <= EPSILON_EGALITE:", "if False:", [P + "Verdicts"],
     r"'ancré' != 'ancres inversées'"),
    ("égalité à la limite du budget départagée", J, "verdicts_lot", "if len(candidats) > k > 0 and", "if False and",
     [P + "Verdicts"], FAUX),
    # --- statistiques ---------------------------------------------------------------------------------------------------------
    ("aire : égalités comptées comme victoires", J, "aire", "(0.5 if p == q else 0.0)", "(1.0 if p == q else 0.0)",
     [P + "Statistiques"], r"1\.0 != 0\.5"),
    ("kappa à la convention v53 (1 au plafond)", J, "kappa_cohen", '{"kappa": None, "accord": po', '{"kappa": 1.0, "accord": po',
     [P + "Statistiques", P + "Mesures"], r"is not None"),
    ("kappa des paires orienté par l'ordre des identifiants", J, "kappa_paires",
     'reference = min(cle, key=lambda i: hashlib.sha256(i.encode("utf-8")).hexdigest())', "reference = cle[0]",
     [P + "Mesures"], r"None != 1\.0"),
    ("kappa des paires sur la position présentée", J, "kappa_paires", 'xa.append(e["gagnant"] == reference)',
     'xa.append(e["premier_gagne"])', [P + "Mesures"], r"0\.0 != 1\.0"),
    ("bascule de position mal comptée", J, "biais_position", 'bascules += es[0]["gagnant"] != es[1]["gagnant"]',
     'bascules += es[0]["gagnant"] == es[1]["gagnant"]', [P + "Mesures"], r"0\.0 != 1\.0|1\.0 != 0\.0"),
    ("part du premier mal comptée", J, "biais_position", 'premier = sum(1 for e in valides if e["premier_gagne"])',
     'premier = sum(1 for e in valides if not e["premier_gagne"])', [P + "Mesures"], r"0\.0 != 1\.0|1\.0 != 0\.0"),
    ("test-retest : plafond binaire faux", J, "plafond_spearman_binaire", "return 1.0 - sum(", "return 1.0 + 0 * sum(",
     [P + "Statistiques"], r"within 7 places"),
    # --- course : compteur, arrêts --------------------------------------------------------------------------------------------
    ("plafond de dépense ignoré", J.Compteur, "budget_appel", "if self.reste() < MINIMUM_APPEL_USD:", "if False:",
     [P + "Compteur"], r"ArretDevis not raised"),
    ("projection au prix observé ignorée", J.Compteur, "exiger_projection", "if p > self.reste() + 1e-9:", "if False:",
     [P + "Compteur"], r"ArretDevis not raised|\d+ != 0"),
    ("durée maximale ignorée", J.Compteur, "verifier_duree", "if ecoule > self.duree_max_s:", "if False:", [P + "Compteur"],
     r"ArretDuree not raised"),
    ("phase descriptive jouée malgré le budget", J, "executer_validation", "if p > compteur.reste():", "if False:",
     [P + "Compteur"], r"ArretDevis"),
    ("A2 : modèle servi non contrôlé", J, "appeler",
     'if r.statut == "ok" and not modele_conforme(juge["modele"], r.modele_servi):', "if False:", [P + "Compteur"],
     r"ArretModeleServi not raised"),
    ("erreur d'un relais non convertie en arrêt (journal perdu)", J, "executer_validation",
     'raise ArretJuges(f"erreur pendant la course : {type(erreur).__name__} : {str(erreur)[:500]}", journal) from erreur', "raise",
     [P + "Compteur"], r"OSError: relais injoignable"),
    ("garde de validité retirée", J, "_garde_validite", "if mauvais > VALIDITE_GARDE_PART * len(fenetre):", "if False:",
     [P + "Mesures"], r"ArretValidite not raised"),
    # --- lecture gelée ----------------------------------------------------------------------------------------------------------
    ("lecture : l'issue « ne fait pas mieux » n'est jamais prononcée", J, "lire_validation", 'elif not crit["D1"]["tenu"]:',
     "elif False:", [P + "Lecture"], r"!= 'I3'"),
    ("lecture : phase décisive incomplète ignorée", J, "lire_validation", 'raisons_i0.append("phase décisive du juge A incomplète")',
     "pass", [P + "Lecture"], r"!= 'I0'"),
    ("audit : un résultat décevant ne déclenche rien", J, "audit_symetrie", 'motifs.append(f"décevant : aire v2 {x:.3f} ≤ {au[\'aire_basse\']}")',
     "pass", [P + "Lecture"], FAUX.replace("True is not false", "False is not true")),
    # --- lanceur ----------------------------------------------------------------------------------------------------------------
    ("lanceur : brouillon admis", L, "lire_preenregistrement",
     "if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)):",
     "if os.path.dirname(reel) != dossier:", [P + "LanceurCheminReel"], REFUS_MANQUE),
    ("lanceur : marqueur restant admis", L, "lire_preenregistrement", "if restants:", "if False:", [P + "LanceurCheminReel"],
     REFUS_MANQUE),
    ("lanceur : empreintes du code non comparées", L, "lire_preenregistrement", "if presente != attendue:", "if False:",
     [P + "LanceurCheminReel"], REFUS_MANQUE),
    ("lanceur : valeurs fixes du plan non comparées", L, "lire_plan", "if lignes[k] != v:", "if False:", [P + "LanceurCheminReel"],
     REFUS_MANQUE),
    ("lanceur : plafond au-dessus de 30 USD admis", L, "lire_plan", "if not 0 < plafond <= PLAFOND_MAX_USD:", "if not 0 < plafond:",
     [P + "LanceurCheminReel"], r"'hors de \]0' not found"),
    ("lanceur : GO autre que celui du texte admis", L, "verifier_go", 'if go != plan["go"]:', "if False:", [P + "LanceurCheminReel"],
     REFUS_MANQUE),
    ("lanceur : configuration d'une autre empreinte admise", L, "preparer_reel", 'if sha_conf != plan["configuration_sha256"]:',
     "if False:", [P + "LanceurCheminReel"], REFUS_MANQUE),
    ("lanceur : variable de clé admise", L, "juges_reels", "if presents:", "if False:", [P + "LanceurCheminReel"],
     r"'les relais tiennent les clés' not found"),
    ("lanceur : devis non comparé à la part du juge", L, "verifier_devis",
     'if d["usd"].get(e, 0.0) > plan[f"plafond_{cle}_usd"] + 1e-9:', "if False:", [P + "LanceurCheminReel"], REFUS_MANQUE),
    ("lanceur : graine admise en mode réel", L, "principal", "if args.graine is not None:", "if False:", [P + "LanceurCheminReel"],
     REFUS_MANQUE),
]


def _proprietaire(cible, nom):
    if isinstance(cible, type):
        for k in cible.__mro__:
            if nom in vars(k):
                return k
    return cible


def appliquer(cible, nom, ancien, nouveau):
    proprietaire = _proprietaire(cible, nom)
    brut = inspect.getattr_static(proprietaire, nom)
    src = textwrap.dedent(inspect.getsource(brut))
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois")
    # globals du module lui-même (pas une copie) : la fonction mutée voit ce que les essais y substituent (par exemple
    # `unittest.mock.patch.object(lanceur, "DOSSIER_PREREG", …)`) ; la fabrique est retirée aussitôt
    espace = vars(sys.modules[brut.__module__])
    code = ("def __fabrique_mutation__(__class__):\n" + textwrap.indent(src.replace(ancien, nouveau), "    ")
            + f"\n    return {brut.__name__}\n")
    exec(compile(code, f"<mutation {brut.__qualname__}>", "exec"), espace)
    g = espace.pop("__fabrique_mutation__")(proprietaire if isinstance(proprietaire, type) else None)
    setattr(proprietaire, nom, g)

    def restaurer():
        setattr(proprietaire, nom, brut)
    return restaurer


def jouer(noms):
    T._COURSES.clear()
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in noms)
    flux = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()):
        r = unittest.TextTestRunner(stream=flux, verbosity=0).run(suite)
    return r.testsRun, [(str(t), txt) for t, txt in r.failures + r.errors]


def classer(echecs, motif):
    if not echecs:
        return "SURVIVANTE"
    if any(re.search(motif, t + "\n" + txt, re.S) for t, txt in echecs):
        return "tuée"
    if any(BANC.search(txt) for _, txt in echecs):
        return "DÉFAUT DU BANC"
    return "TUÉE POUR UNE AUTRE RAISON"


def _derniere_ligne(txt):
    lignes = [l for l in txt.strip().splitlines() if l.strip()]
    return lignes[-1][:220] if lignes else ""


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    noms = sorted({x for m in MUTATIONS for x in m[5]})
    for n in noms:
        unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {_derniere_ligne(txt)}")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS:
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
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec")
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {_derniere_ligne(txt)}")
    apres = jouer(noms)
    total = len(MUTATIONS)
    print(f"mutations juges-idees-v2 : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre "
          f"raison : {comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; "
          f"survivantes : {comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
