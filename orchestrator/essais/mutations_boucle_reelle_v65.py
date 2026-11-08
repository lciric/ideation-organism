"""Banc de mutations de la v65 (R5 : chaque garde ou pièce neutralisée fait échouer son essai, **pour la raison attendue**) — cœur
(`pole/boucle_reelle_v65.py`), lecture gelée (`pole/lecture_boucle_reelle_v65.py`), lanceur (`demonstrations/boucle_reelle_v65.py`,
chargé par `essais/test_boucle_reelle_v65.py` sous « essais. »). Mécanique du banc v56 (`essais/mutations_v55.py` : recompilation en
mémoire de la fonction mutée, raison attendue, restauration, témoin avant et après) ; les mutations de constante sont posées sur
l'attribut du module et retirées après. Aucun fichier n'est modifié. La course saine mise en cache par les essais est rejouée sous
chaque mutation (cache vidé avant chaque passe ; les essais retirent son dossier en fin de passe).

Groupes : M1 héritage de départ (garde 17), M2 jeu planté et classe couverte (garde 19), M3 jugement avec l'archive (garde 18), M4 bras
réel seul (garde 20), génération 2 et copies (garde 21), gardes de dépense (plafonds, GO cité), bac réel (garde 22), configuration v5
(commandes nommées), texte scellé et plan (garde 6), M5 lecture gelée (C1 à C6, A1 à A4).

  python3 -I -B essais/mutations_boucle_reelle_v65.py [--raisons] [--seulement MOT]      (depuis le dossier orchestrator)
"""

import os
import sys
import time
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v55 as m55  # noqa: E402
from essais import test_boucle_reelle_v65 as E  # noqa: E402  (charge le lanceur et le programme de lecture sous « essais. »)
from pole import boucle_reelle_v65 as B  # noqa: E402
from pole import lecture_boucle_reelle_v65 as LE  # noqa: E402

LANCEUR = E.LANCEUR
TT = "essais.test_boucle_reelle_v65."
NR = r"not raised"


def constante(module):
    return ("constante", module)


MUTATIONS = [
    # M1 — héritage de départ (garde 17)
    ("M1 : empreinte de l'héritage non comparée au texte", B, "lire_heritage_depart", "if sha != attendue:", "if False:",
     [TT + "HeritageDepart"], r"empreinte|HeritageDepartRefuse"),
    ("M1 : seule K1 non exigée", B, "lire_heritage_depart", "if not isinstance(lois, dict) or sorted(lois) != [NOM_DEPART]:",
     "if not isinstance(lois, dict):", [TT + "HeritageDepart"], NR),
    ("M1 : loi plantée dans l'héritage non cherchée", B, "lire_heritage_depart", "        if egales:", "        if False:",
     [TT + "HeritageDepart"], NR),
    ("M1 : lien symbolique suivi", B, "lire_heritage_depart", "if not stat.S_ISREG(st.st_mode):", "if False:",
     [TT + "HeritageDepart"], r"régulier|not raised"),
    ("M1/M4 : archive lue non comparée à l'archive précédente ∪ retenues", B, "lire_heritage_v65",
     'if not _egales(h["archive"], attendue):', "if False:", [TT + "Generation2LitLaSelection"], r"archive|not raised"),
    # M2 — jeu planté (garde 19), classe couverte
    ("M2/garde 19 : empreinte du jeu non comparée au plan", B, "lire_jeu_plante", "if sha != attendue:", "if False:",
     [TT + "JeuPlante"], r"garde 19|not raised"),
    ("M2 : jeu non canonique accepté", B, "lire_jeu_plante", "if canonique != octets:", "if False:", [TT + "JeuPlante"], r"canonique"),
    ("M2 : fausse hors classe non refusée", B, "verifier_jeu", "        if ligne is None:", "        if False:",
     [TT + "JeuPlante"], r"FausseHorsClasse|JeuPlanteRefuse"),
    ("M2 : jeu incomplet accepté", B, "verifier_jeu", "tuple(sorted(jeu[groupe])) != tuple(sorted(noms))", "False",
     [TT + "JeuPlante"], r"incomplet|KeyError"),
    ("M2 : mélange avec une loi inconnue pris pour couvert", B, "classer_couverte",
     "if not connues_ici or len(connues_ici) + len(fixes) != len(comps):", "if not connues_ici:", [TT + "ClasseCouverte"], r"is not None"),
    ("M2 : composition d'étapes prise pour couverte", B, "classer_couverte", 'etapes <= {"puissance", "inclinaison"}',
     'etapes <= {"puissance", "inclinaison", "melange_aveugle", "oscillation"}', [TT + "ClasseCouverte"], r"is not None"),
    ("garde 19 : jeu utilisé ≠ bloc accepté", B, "exiger_jeu_conforme", "if json_canonique(jeu) != octets:", "if False:",
     [TT + "JeuPlante"], r"garde 19|not raised"),
    # M3 — jugement avec l'archive (garde 18)
    ("M3 : lois plantées jugées sans l'archive (le défaut de la v64)", B, "juger_v65", "archive_plantees = archive  #",
     "archive_plantees = {}  #", [TT + "JugementAvecArchive"], r"ArchiveDesPlanteesAbsente|garde 18|M3"),
    ("M3 : seuil log(m/α) des lois plantées retiré", B, "juger_v65", 'promue = bool(ev["promue"]) and log_e >= seuil',
     'promue = bool(ev["promue"])', [TT + "JugementAvecArchive"], r"test_seuil_hors_famille"),
    ("garde 18 : membres d'archive des lois plantées non vérifiés", B, "exiger_archive_des_plantees", "    if ecarts:", "    if False:",
     [TT + "JugementAvecArchive"], r"garde 18|not raised"),
    # M4 — bras réel seul (garde 20), génération 2, copies (garde 21), garde 7
    ("garde 20 : bras de référence acceptés", B, "exiger_bras_reel_seul", "if option != OPTION_BRAS:", "if False:",
     [TT + "BrasReelSeul"], NR + r"|BrasRefuse"),
    ("M4 : la génération 2 ne lit pas la sélection (héritage de départ servi)", B, "jouer_boucle",
     'heritage = lire_heritage_v65(prec["dossier"], prec["sha"], prec["archive"], depart)', "heritage = depart",
     [TT + "Generation2LitLaSelection"], r"assert|Error"),
    ("M4 : copies des retenues non replantées en génération 2", B, "plantees_generation_2",
     "[_plantee(nom, loi, racine, tache) for nom, _source, loi in copies]", "[]", [TT + "Generation2LitLaSelection"], r"copies|!= 0|0 != "),
    ("M4 : lois plantées promues de la génération 1 non testées", B, "jouer_generation_v65",
     "a_tester_p = promues_plantees if generation == 1 else []", "a_tester_p = []", [TT + "CourseSaine"], r"assert|éliminée|survit"),
    ("garde 21 : copie d'une carte non retenue acceptée", B, "exiger_copies_conformes", "        if src not in retenues:",
     "        if False:", [TT + "CopiesGarde21"], r"non retenue"),
    ("garde 21 : sources autres que les quatre premières acceptées", B, "exiger_copies_conformes",
     "if [(n, s) for n, s, _ in copies] != attendues:", "if False:", [TT + "CopiesGarde21"], r"quatre premières|not raised"),
    ("garde 21 : copies sans l'ordre des log e", B, "copies_de_la_selection", "sorted(retenues, key=cle)", "sorted(retenues)",
     [TT + "CopiesGarde21"], r"quatre premières"),
    ("garde 7 : loi plantée dans l'archive ou la vue acceptée", B, "exiger_sans_plantee", "    if presents:", "    if False:",
     [TT + "Garde7Plantees"], NR),
    ("§ 7.6 : loi gelée non retirée avant la recherche dans l'étage", B, "chercher_dans_un_texte_d_etage", 'reste = reste.replace(forme, " ")',
     "pass", [TT + "CourseSaine"], r"test_recherche_de_la_loi_plantee"),
    # gardes de dépense
    ("dépense : borne d'un appel non comparée à la part restante", B.CompteurV65, "verifier_avant_appel",
     "if relais not in self.parts or reste_part <= 1e-9 or reste <= 1e-9 or borne > reste_part + 1e-9 or borne > reste + 1e-9:",
     "if False:", [TT + "GardesDeDepense"], NR + r"|PlafondAtteint"),
    ("dépense : appel permis quand la part est épuisée (borne nulle)", B.CompteurV65, "verifier_avant_appel", "reste_part <= 1e-9 or ",
     "", [TT + "GardesDeDepense"], NR),
    ("dépense : plafond de la machine non tenu", B.CompteurV65, "ajouter_machine",
     "if self.machine_usd > self.plafond_machine_usd + 1e-9:", "if False:", [TT + "GardesDeDepense"], NR),
    ("dépense : GO cité non exigé", B, "exiger_go_cite", 'raise GoNonCite(f"aucun appel sans le GO',
     'return True or GoNonCite(f"aucun appel sans le GO', [TT + "GardesDeDepense"], NR + r"|GoNonCite"),
    ("dépense : adaptateur réel appelé sans GO", B.AdaptateurSousGo, "lancer", "exiger_go_cite(self.go, self.go_attendu, self.montant_usd)",
     "pass", [TT + "GardesDeDepense"], NR),
    ("dépense : adaptateur réel appelé au-delà de la part", B.AdaptateurSousGo, "lancer",
     "self.compteur.verifier_avant_appel(self.relais, budget_usd)", "pass", [TT + "GardesDeDepense"], NR + r"|avant l'appel"),
    ("dépense : proposeur appelé sans contrôle de la part restante", B, "jouer_generation_v65",
     "compteur.verifier_avant_appel(p.relais, p.budget)  # arrêt au plafond, avant l'appel", "pass",
     [TT + "GardesDeDepense"], r"test_course_arretee_au_plafond"),
    ("dépense : GO lu au plafond des modèles seul (sans la machine)", LANCEUR, "principal",
     'go = cfg.verifier_go_v56(args.go, args.registre_go, plan["plafond_modeles_usd"] + plan["plafond_machine_usd"])',
     'go = cfg.verifier_go_v56(args.go, args.registre_go, plan["plafond_modeles_usd"])', [TT + "CheminReelVerifierSeulement"],
     r"pas exactement|GoNonCite|!= 0|0 != 2|2 != 0"),
    # bac réel (garde 22), configuration v5
    ("garde 22 : bwrap < 0.9 accepté", LANCEUR, "exiger_machine_du_bac", "if tuple(version[:2]) < VERSION_BWRAP_MIN:", "if False:",
     [TT + "BacReel"], NR),
    ("garde 22 : utilisateur dédié non exigé en mode réel", LANCEUR, "exiger_machine_du_bac",
     "if reel and (utilisateur_bac is None or int(utilisateur_bac) <= 0):", "if False:", [TT + "BacReel", TT + "CheminReelVerifierSeulement"],
     NR + r"|utilisateur dédié"),
    ("garde 3 : bwrap absent → repli sur l'exécuteur factice", LANCEUR, "exiger_machine_du_bac", "    if version is None:\n",
     "    if version is None and False:\n", [TT + "BacReel"], NR + r"|bwrap absent|TypeError"),
    ("M6 : empreinte d'une commande v6 nommée non vérifiée", LANCEUR, "exiger_configuration_v65",
     'if sha256_fichier(c["chemin"]) != c["sha256"]:', "if False:", [TT + "ConfigurationV5", TT + "CheminReelVerifierSeulement"],
     r"empreinte|not raised|0 != 2"),
    ("M6 : commande v6 absente non refusée", LANCEUR, "exiger_configuration_v65", 'if not os.path.isfile(c["chemin"]):', "if False:",
     [TT + "ConfigurationV5"], r"absente|FileNotFoundError"),
    ("M6 : plafonds de la configuration non comparés au plan", LANCEUR, "exiger_configuration_v65",
     "if not isinstance(s.get(k), (int, float)) or abs(float(s[k]) - float(v)) > 1e-9:", "if False:", [TT + "ConfigurationV5"], NR),
    # texte scellé (garde 6) et plan
    ("garde 6 : code gelé non comparé au code présent", LANCEUR, "lire_preenregistrement", "    if ecarts:", "    if False:",
     [TT + "Garde6V65"], r"code différent|not raised"),
    ("garde 6 : marqueur restant accepté", LANCEUR, "lire_preenregistrement", "    if restants:", "    if False:", [TT + "Garde6V65"], NR),
    ("plan : m ≠ 2 × cartes + 10 accepté", B, "lire_plan", ' or entiers["m_e_bh"] != m_impose(entiers["cartes_par_proposeur"])', "",
     [TT + "PlanV65"], NR),
    ("plan : autre nombre de générations accepté", B, "lire_plan", 'if entiers["generations"] != GENERATIONS:', "if False:",
     [TT + "PlanV65"], NR),
    ("plan : parts ≠ plafond des modèles acceptées", B, "lire_plan",
     'if round(reels["plafond_kimi_usd"] * 100) + round(reels["plafond_argon_usd"] * 100) != round(reels["plafond_modeles_usd"] * 100):',
     "if False:", [TT + "PlanV65"], NR),
    # M5 — lecture gelée
    ("M5 : ordre C2 avant C4", constante(LE), "ORDRE", None, ("C5", "C2", "C4", "C3", "C6", "C1"), [TT + "LectureGelee"], r"C4 avant C2"),
    ("M5 : C2 partielle non écrite sous un arrêt", LE, "lire_boucle", 'partielles.append("C2 (partielle)")', "pass",
     [TT + "LectureGelee"], r"partielle"),
    ("M5 : C4 partielle non écrite sous un arrêt", LE, "lire_boucle", 'partielles.append("C4 (partielle)")', "pass",
     [TT + "LectureGelee"], r"partielle"),
    ("M5/P6 : empreinte lue ≠ écrite non vue", LE, "verifier_lecture_selection", 'if x.get("attendu") != x.get("lu") or not x.get("lu"):',
     "if False:", [TT + "LectureGelee"], r"C4|partielle"),
    ("M5/P6 : vue de la génération 2 non vérifiée", LE, "verifier_lecture_selection",
     'if sorted((vues.get(2) or {}).get("lois") or []) != attendu:', "if False:", [TT + "LectureGelee"], r"vue"),
    ("M5/P6 : membres d'archive de la génération 2 non vérifiés", LE, "verifier_lecture_selection", "        if faux:", "        if False:",
     [TT + "LectureGelee"], r"membres"),
    ("M5/P6 : copies non vérifiées contre la sélection", LE, "verifier_lecture_selection", "if [s for _, s in copies] != attendues:",
     "if False:", [TT + "LectureGelee"], r"copies"),
    ("M5 : copie promue non lue C4", LE, "lire_boucle", '"C4": bool(ecarts_p6) or bool(copies_promues),', '"C4": bool(ecarts_p6),',
     [TT + "LectureGelee"], r"C4|C1"),
    ("M5 : fausse promue non lue C2", LE, "lire_boucle", '"C2": bool(fausses_promues),', '"C2": False,', [TT + "LectureGelee"], r"C2"),
    ("M5 : C3 jamais lue", LE, "lire_boucle", '"C3": not vraies_ps,', '"C3": False,', [TT + "LectureGelee"], r"C3"),
    ("M5 : T-ELIM non contrôlée (C6)", LE, "lire_boucle", 'if not (t_elim.get("promue") and t_elim.get("verdict") == "éliminée"):',
     "if False:", [TT + "LectureGelee"], r"C6"),
    ("M5 : T-MAL non contrôlée (C6)", LE, "lire_boucle", 'if t_mal.get("gardien") != "refuse":', "if False:", [TT + "LectureGelee"], r"C6"),
    ("M5 : A1 non déclenché sous C1", LE, "lire_boucle", '"A1": audit_a1(releve, journal) if issue == "C1" else {"declenche": False}',
     '"A1": {"declenche": False}', [TT + "LectureGelee"], r"test_C1"),
    ("M5 : A2 sans rejeu", LE, "audit_a2", "k = _rejouer(", "k = None and _rejouer(", [TT + "LectureGelee"], r"None != 0|0 != None"),
    ("M5 : A3 sans rejeu à la même graine", LE, "audit_a3", '"rejeu_egal": p.get("log_richesse_max") == round(ev["log_richesse_max"], 6)',
     '"rejeu_egal": False', [TT + "LectureGelee"], r"même graine"),
    ("M5 : A4 non déclenché sur une copie promue", LE, "lire_boucle", '"A4": audit_a4(releve) if copies_promues else {"declenche": False}',
     '"A4": {"declenche": False}', [TT + "LectureGelee"], r"test_C4"),
    ("M5 : fausse découverte réelle non écrite en tête", LE, "lire_boucle",
     'en_tete = [f"fausse découverte d\'une carte réelle : {i} (hors du dessin ; audit A2 sur sa forme)" for i in fausses_decouvertes]',
     "en_tete = []", [TT + "LectureGelee"], r"en_tete|fausse découverte|test_fausse_decouverte"),
]


def appliquer(cible, nom, ancien, nouveau):
    if isinstance(cible, tuple) and cible and cible[0] == "constante":
        module = cible[1]
        avant = getattr(module, nom)
        setattr(module, nom, nouveau(avant) if callable(nouveau) else nouveau)
        return lambda: setattr(module, nom, avant)
    return m55.appliquer(cible, nom, ancien, nouveau)


def jouer(noms, cible=None):
    E._COURSE.clear()  # la course saine est rejouée sous chaque mutation (jamais le cache d'une autre passe)
    return m55.jouer(noms)


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    seul = argv[argv.index("--seulement") + 1] if "--seulement" in argv else None
    liste = [m for m in MUTATIONS if seul is None or seul in m[0]]
    noms = sorted({x for m in liste for x in m[5]})
    t0 = time.time()
    temoin = jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec", flush=True)
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes = {}
    for m in liste:
        libelle, cible, nom, ancien, nouveau, essais, motif = m
        try:
            restaurer = appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError, KeyError, AttributeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  {libelle} : {type(e).__name__} : {e}", flush=True)
            continue
        try:
            n, echecs = jouer(essais, cible)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
        verdict = m55.classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec", flush=True)
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {m55._derniere_ligne(txt)}")
    apres = jouer(noms)
    total = len(liste)
    print(f"mutations v65 : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)} ; {time.time() - t0:.0f} s")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
