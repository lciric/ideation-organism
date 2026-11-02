"""Banc de mutations de la v63 (R5 : chaque garde ou correction neutralisée fait échouer son essai, **pour la raison attendue**) —
cœur (`pole/tour_ferme_v63.py`), évaluateur servi (`pole/evaluateur_lois_v62.py`), lecture gelée (`pole/lecture_tour_ferme_v63.py`),
lanceur (`demonstrations/tour_ferme_v63.py`) et programme de lecture (`demonstrations/lire_tour_ferme_v63.py`), ces deux derniers
chargés par `essais/test_tour_ferme_v63.py` sous « essais. » (le banc les atteint). Mécanique du banc v56 (recompilation en mémoire,
raison attendue, restauration, témoin avant et après) ; les mutations de constante (`FICHIERS_GELES`, borne par carte) sont posées
sur l'attribut du module et retirées après. Aucun fichier n'est modifié.

Trois groupes : (1) les 24 mutations du banc v62, portées sur le code v63 ; (2) les sondes de la contre-lecture 3 — les six
survivantes de B10 (T2, T3, T4, T5, plafond de l'étage, durée), le témoin dans la sélection (I31), l'appel de la machine jetable au
lanceur (garde 15), l'étage 2 non refusé (garde 12) — plus une mutation de bord par critère de la garde 14 et par garde 5 et 13 ;
(3) une mutation au moins par correction v63 (I26, I27, I28, I29, I30, mineurs 29, 30, 34, garde 7, 8 et 9 sur le code v63, version
du relevé). La sonde « entropie non exigée au chemin réel » n'est pas au banc : son artefact (un texte scellé d'empreinte < 2⁶⁴)
ne se fabrique pas ; l'unité `entropie_decisive` est essayée (`Garde6Complete`).

  python3 -I -B essais/mutations_tour_ferme_v63.py [--raisons] [--seulement MOT]      (depuis le dossier orchestrator)
"""

import os
import sys
import time
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v56 as m56  # noqa: E402
from essais import test_tour_ferme_v63 as E  # noqa: E402  (charge le lanceur et le programme de lecture sous « essais. »)
from essais import test_gardes_tour_ferme_v63 as EG  # noqa: E402,F401
from pole import evaluateur_lois_v62 as EV  # noqa: E402
from pole import lecture_tour_ferme_v63 as LE  # noqa: E402
from pole import tour_ferme_v63 as TF  # noqa: E402

m55 = m56.m55
LANCEUR, LECTEUR = E.LANCEUR, E.LECTEUR
TT = "essais.test_tour_ferme_v63."
TG = "essais.test_gardes_tour_ferme_v63."
NR = r"not raised"


def constante(module):
    return ("constante", module)


def sans(nom):
    return lambda v: tuple(x for x in v if x != nom)


PORTEES_V62 = [
    ("C8 (B7) : loi non servie dans le texte du test", TF, "texte_du_test", '+ MARQUE_LOI + json_canonique(loi).decode("utf-8"))', ")",
     [TT + "ServiceDeLaLoi"], r"C8 : loi absente"),
    ("C9 (B8) : grammaire non servie aux proposeurs", TF, "contexte_du_proposeur", '"grammaire": json.loads(json.dumps(GRAMMAIRE))},', "},",
     [TT + "GrammaireServie"], r"C9 : grammaire"),
    ("C9 : borne ±4 du gabarit non tenue", TF, "_verifier_noeud", "if borne_softmax is not None and any(", "if False and any(",
     [TT + "GrammaireServie"], r"C9 : borne"),
    ("C10 (B9) : lectures attendues = générations jouées (v61)", LE, "lire_etage1",
     "lectures_attendues = sorted((x, g) for x in BRAS_ETAGE1 for g in range(2, n_gen + 1))  # B9 : jouées ou non",
     "lectures_attendues = sorted((x, g) for x, v in jouees.items() for g in v if g >= 2)", [TT + "LectureV63", TT + "CourseMuette"], r"B9"),
    ("C11 (I22) : machine jetable non vérifiée en mode réel (fonction)", LANCEUR, "exiger_machine_jetable_reel",
     "exiger_machine_jetable_v56(environnement, permis_en_plus=permis)", "pass", [TT + "MachineJetable"], NR),
    ("C12 (I10) : session du proposeur en échec tue (« réponse illisible »)", TF.ProposeurAdaptateur, "proposer",
     'if r.statut != "ok" or r.erreur or refus is not None:', "if False:", [TT + "ProposeurChemin"], NR),
    ("C12 (I10) : exception d'une génération non convertie en arrêt à relevé partiel", TF, "jouer_etage_1",
     'arret = f"{type(e).__name__} : {str(e)[:500]}"', "raise", [TT + "Arrets"], r"C12"),
    ("C13 (I12) : part d'un relais ignorée", TF.Compteur, "ajouter",
     "if relais in self.parts and self.par_relais[relais] > self.parts[relais] + 1e-9:", "if False:", [TT + "PartsDesRelais"], NR),
    ("C13 (I12) : pire cas avant l'étage ignoré", TF.Compteur, "verifier_parts_avant_etage",
     "if relais in self.parts and self.parts[relais] - self.par_relais.get(relais, 0.0) < besoin - 1e-9:", "if False:",
     [TT + "PartsDesRelais", TT + "ReservationI30"], NR),
    ("C13 (I12) : « budget_depasse » d'un relais pris pour le plafond de la fiche", TF.AdaptateurEtageV63, "lancer",
     'if r.statut == "budget_depasse" and (', "if False and (", [TT + "PartsDesRelais"], NR),
    ("C14 (I14) : gains écrits arrondis à 4 décimales", EV, "ecrire_gains", '"%d,%r\\n" % (i, x)', '"%d,%.4f\\n" % (i, x)',
     [TT + "PleinePrecision"], r"C14"),
    ("C14 (mineur 24) : copie de la tranche non vérifiée", TF, "contre_calculer",
     "if sha_attendue is not None and sha256_fichier(chemin_episodes) != sha_attendue:", "if False:", [TT + "PleinePrecision"], NR),
    ("garde 10 : contre-calcul tolérant (arrêt de bout en bout)", TF, "contre_calculer", "<= TOLERANCE_CONTRE_CALCUL", "<= 1.0",
     [TT + "Arrets"], r"arrondi|fabrique"),
    ("C15 (I15) : identifiant réel servi à l'étage", TF, "identifiant_opaque",
     'return "F-" + hashlib.sha256(f"{racine}|{tache}|{ident_reel}".encode("utf-8")).hexdigest()[:12]', "return ident_reel",
     [TT + "Aveugle"], r"C15"),
    ("C16 (I17) : A4 « promeut autant » sans carte réelle jugée (v61)", LE, "lire_etage1",
     "    elif not nr or not na:\n        a4 = A4_NON_MESURABLE  # I17 : jamais « promeut autant » sans carte réelle jugée\n    elif diff[0] > 0:",
     "    elif diff is not None and diff[0] > 0:", [TT + "LectureV63"], r"I17"),
    ("C16 (I16) : P4 sans cas", LE, "cas_p4", 'return "informative" if max(g2) > 0 else "vide"', 'return "informative"',
     [TT + "LectureV63"], r"I16"),
    ("C16 (I18) : recherche de la loi plantée absente acceptée", LE, "exiger_recherche",
     'raise ReleveInvalide("recherche de la loi plantée absente, nulle ou mal formée (S1, point 3) : relevé invalide")',
     'return {"contextes_cherches": 0, "touches": [], "lignes_de_tranche_dans_les_contextes": []}', [TT + "LectureV63"], NR),
    ("C16 (T34) : S5 sans le « non concluant » par bras", LE, "lire_etage1", '"S5_asymetrie": bool(s5_gardien or s5_nc)',
     '"S5_asymetrie": bool(s5_gardien)', [TT + "LectureV63"], r"S5"),
    ("C17 (I19) : sceau du préenregistrement non vérifié", LANCEUR, "lire_preenregistrement", "if not verifier_scelle(reel):", "if False:",
     [TT + "Garde6Complete"], NR),
    ("C17 (I19) : marqueur hors de l'étage 2 accepté", LANCEUR, "lire_preenregistrement",
     "restants = sorted(set(MARQUEUR.findall(hors_zone)))", "restants = []", [TT + "Garde6Complete"], NR),
    ("C18 (I20) : relevé non scellé lu", LECTEUR, "lire", "if not verifier_scelle(chemin):", "if False:", [TT + "CourseSaine"], r"C18"),
    ("C19 (I23) : la recopie de g lit le bilan réel de g", TF, "jouer_etage_1",
     'src = source_recopie if bras == "recopie_melange" else etat[bras]', 'src = etat["reel"] if bras == "recopie_melange" else etat[bras]',
     [TT + "CourseSaine"], r"C19"),
    ("C20 (I24) : monde planté non vérifié", LANCEUR, "verifier_monde", 'if monde.get("sha256") != sha_attendue:', "if False:",
     [TT + "MondeGele"], NR),
    ("C21 (mineur 21) : moteur « simule » en mode réel", LANCEUR, "moteur_de_l_etage", 'return "claude-sdk" if reel else "simule"',
     'return "simule"', [TT + "EtageV63"], r"C21"),
]

SONDES_CL3 = [
    ("B10, garde 14 : T2 neutralisé (sonde)", LE, "lire_etage1", "    t2 = (len(vraie) == attendues", "    t2 = True or (len(vraie) == attendues",
     [TG + "Garde14T2"], r"garde 14 : T2 tient"),
    ("B10, garde 14 : T3 neutralisé (sonde)", LE, "lire_etage1", "    t3 = (faux_ps <= 1", "    t3 = True or (faux_ps <= 1",
     [TG + "Garde14T3"], r"garde 14 : T3 tient"),
    ("B10, garde 14 : T4 neutralisé (sonde)", LE, "lire_etage1", "    t4 = ((nc / testees", "    t4 = True or ((nc / testees",
     [TG + "Garde14T4"], r"garde 14 : T4 tient"),
    ("B10, garde 14 : T5 neutralisé (sonde)", LE, "lire_etage1", '    t5 = bras["aleatoire"]["fd"] <= 1', '    t5 = True or bras["aleatoire"]["fd"] <= 1',
     [TG + "Garde14T5"], r"garde 14 : T5 tient"),
    ("B10, garde 5 : plafond global de l'étage neutralisé (sonde)", TF.Compteur, "ajouter", "if self.usd > self.plafond_usd:", "if False:",
     [TG + "Garde5PlafondEtage", TG + "Garde5DeBoutEnBout"], r"garde 5 : plafond de l'étage franchi sans arrêt|'plafond de dépense de l'étage franchi' not found"),
    ("B10, garde 13 : durée neutralisée (sonde)", TF.Compteur, "verifier_duree", "if self.horloge() - self.debut > self.duree_max_s:",
     "if False:", [TG + "Garde13Duree", TG + "Garde13DeBoutEnBout"], r"garde 13 : durée|arrêt attendu \(code 3\)"),
    ("I31, garde 7 : témoin dans la sélection non refusé (sonde)", TF, "jouer_generation", "if set(retenues) & set(par_ident_t):", "if False:",
     [TT + "Garde7Selection"], r"'témoin dans la sélection' not found|garde 7 \(sélection\)"),
    ("garde 15 : appel de la machine jetable retiré au lanceur (sonde)", LANCEUR, "principal",
     "permis = exiger_machine_jetable_reel(environnement, conf)", "permis = ()", [TT + "CheminReelVerifierSeulement"],
     r"garde 15 \(lanceur, chemin réel\)"),
    ("garde 12 : étage 2 non refusé (sonde)", LANCEUR, "principal", "if args.etage != 1:", "if False:", [TT + "RefusAvantToutAppel"],
     r"garde 12 : étage 2 lancé"),
    # bords des seuils (B10) : chaque seuil déplacé d'un pas
    ("B10, garde 14 : T2, « sauf au plus une » → deux", LE, "lire_etage1", 'for c in vraie) >= attendues - 1', 'for c in vraie) >= attendues - 2',
     [TG + "Garde14T2"], r"garde 14 : T2 tient"),
    ("B10, garde 14 : T3, au plus 1 témoin faux retenu → 2", LE, "lire_etage1", "t3 = (faux_ps <= 1 and", "t3 = (faux_ps <= 2 and",
     [TG + "Garde14T3"], r"garde 14 : T3 tient"),
    ("B10, garde 14 : T3, T-ELIM « sauf au plus une » → deux", LE, "lire_etage1", 'for c in elim) >= attendues - 1', 'for c in elim) >= attendues - 2',
     [TG + "Garde14T3"], r"garde 14 : T3 tient"),
    ("B10, garde 14 : T4, ≤ 0,20 devient < 0,20", LE, "lire_etage1", "(nc / testees if testees else 0.0) <= SEUIL_INCONCLUSIF\n",
     "(nc / testees if testees else 0.0) < SEUIL_INCONCLUSIF\n", [TG + "Garde14T4"], r"garde 14 : T4 manque au bord"),
    ("B10, garde 14 : T4, seuil par bras ignoré", LE, "lire_etage1",
     'and all(r["part_non_concluant"] <= SEUIL_INCONCLUSIF_PAR_BRAS for r in bras.values())', "and True", [TG + "Garde14T4"],
     r"garde 14 : T4 tient"),
    ("B10, garde 14 : T4, désaccord du contre-calcul ignoré", LE, "lire_etage1",
     'and all(r["contre_calcul_en_desaccord"] == 0 for r in bras.values()))', "and True)", [TG + "Garde14T4"], r"garde 14 : T4 tient"),
    ("B10, garde 14 : T5, au plus 1 FD aléatoire → 2", LE, "lire_etage1", 't5 = bras["aleatoire"]["fd"] <= 1 and',
     't5 = bras["aleatoire"]["fd"] <= 2 and', [TG + "Garde14T5"], r"garde 14 : T5 tient"),
    ("B10, garde 14 : T5, FD de la recopie ignorées", LE, "lire_etage1", ' and bras["recopie_melange"]["fd"] <= 1', "",
     [TG + "Garde14T5"], r"garde 14 : T5 tient"),
    ("B10, garde 5 : égalité au plafond refusée", TF.Compteur, "ajouter", "if self.usd > self.plafond_usd:", "if self.usd >= self.plafond_usd:",
     [TG + "Garde5PlafondEtage"], r"plafond de dépense de l'étage franchi : 1\.0000"),
    ("B10, garde 13 : égalité à la durée refusée", TF.Compteur, "verifier_duree", "if self.horloge() - self.debut > self.duree_max_s:",
     "if self.horloge() - self.debut >= self.duree_max_s:", [TG + "Garde13Duree"], r"plafond de durée de l'étage franchi : 10 s"),
]

CORRECTIONS_V63 = [
    ("I26 : indice non entier accepté (si_sinon)", TF, "_verifier_noeud", 'if not _entier(c["indice"], (0, 1)):', 'if c["indice"] not in (0, 1):',
     [TT + "GardienEntiers", TT + "CourseIndiceFlottant"], r"I26"),
    ("I26 : sous-population non entière acceptée", TF, "_verifier_noeud", 'if not _entier(c["sous_population"], (0, 1)):',
     'if c["sous_population"] not in (0, 1):', [TT + "GardienEntiers"], r"I26"),
    ("I26 : trait et issue d'oscillation non entiers acceptés", TF, "_verifier_noeud",
     'if not _entier(o["trait"], (0, 1)) or not _entier(o["issue"], tuple(range(K))):', "if False:", [TT + "GardienEntiers"], r"I26"),
    ("I26 : seuil non fini accepté", TF, "_verifier_noeud", 'if not nombre_fini(c.get("seuil", 0.0)):', "if False:",
     [TT + "GardienEntiers"], r"I26"),
    ("I26 : jeu factice retiré du gardien", TF, "garder", 'motif = evaluer_sur_jeu_factice(carte["loi_predictive"])', "motif = None",
     [TT + "GardienJeuFactice"], r"I26 : le gardien laisse passer"),
    ("I26 : écart de l'évaluateur servi non vu", TF, "evaluer_sur_jeu_factice",
     "if len(q) != K or max(abs(a - b) for a, b in zip(p, q)) > TOLERANCE_EVALUATEUR_SERVI:", "if False:", [TT + "GardienJeuFactice"],
     r"I26 : écart de l'évaluateur servi"),
    ("I26 : probabilités hors du simplexe acceptées", TF, "evaluer_sur_jeu_factice",
     "if len(p) != K or not all(nombre_fini(v) and v >= 0.0 for v in p) or abs(sum(p) - 1.0) > 1e-9:", "if False:",
     [TT + "GardienJeuFactice"], r"hors du simplexe"),
    ("I26 : exception de la vérification qui remonte (gabarit)", TF, "verifier_loi_servable",
     "        except Exception as e:  # noqa: BLE001 — I26 : une vérification qui échoue refuse la loi ; elle ne remonte jamais",
     "        except ZeroDivisionError as e:", [TT + "AucuneExceptionQuiRemonte"], r"OverflowError"),
    ("I26 : exception du gardien mécanique qui remonte", TF, "garder",
     "    except Exception as e:  # noqa: BLE001 — I26 : refus motivé, jamais une exception qui remonte", "    except ZeroDivisionError as e:",
     [TT + "AucuneExceptionQuiRemonte"], r"Out of range float values"),
    ("I26 : réponse trop imbriquée non rattrapée", TF, "extraire_propositions", "except (ValueError, RecursionError):", "except ValueError:",
     [TT + "AucuneExceptionQuiRemonte"], r"RecursionError"),
    ("I27 : pole/ideation.py hors du bloc gelé", constante(LANCEUR), "FICHIERS_GELES", None, sans("pole/ideation.py"),
     [TT + "Fermeture", TT + "FermetureEnCourse"], r"I27"),
    ("I27 : pole/tests_de_mort.py hors du bloc gelé", constante(LANCEUR), "FICHIERS_GELES", None, sans("pole/tests_de_mort.py"),
     [TT + "Fermeture", TT + "FermetureEnCourse"], r"I27"),
    ("I27 : module d'un chemin non joué hors du bloc gelé", constante(LANCEUR), "FICHIERS_GELES", None, sans("pole/simulation_v56.py"),
     [TT + "Fermeture"], r"I27"),
    ("I28 : issue A4 lue sur un arrêt (v62)", LE, "lire_etage1",
     "    if partiel:  # I28 : un relevé d'arrêt ne rend aucune issue A4 (ses chiffres restent rapportés, marqués partiels)\n"
     "        a4, cause = A4_ARRET, None\n", "", [TT + "LectureV63", TT + "ArretEnGeneration2", TT + "Arrets"], r"I28"),
    ("I29 : ligne de tranche dans un contexte sans conséquence (v62)", LE, "exiger_recherche",
     '    if r["lignes_de_tranche_dans_les_contextes"]:\n        raise DefautDeCourse(', '    if False:\n        raise DefautDeCourse(',
     [TT + "LectureV63", TT + "FuiteDansLesContextes"], r"I29|test_ligne_de_tranche"),
    ("mineur 29 : relevé d'arrêt invalide lu « critère »", LE, "lire_tour_etage_1", '"n1": "arret" if arret else "critere"', '"n1": "critere"',
     [TT + "LectureV63"], r"mineur 29"),
    ("mineur 30 : trajectoire de P7 non calculée", LE, "trajectoire_p7",
     "(dernier < premier) if (premier is not None and dernier is not None) else None", "None", [TT + "LectureV63"], r"mineur_30"),
    ("I30 : borne par carte non passée à l'étage", TF, "jouer_etage", '"budget_test_usd": BUDGET_EXPERIMENTATEUR_PAR_CARTE_USD, ', "",
     [TT + "EtageV63"], r"I30"),
    ("I30 : pire cas de l'étage à 0,5 USD par carte (règle v62)", TF, "jouer_etage", "n * BUDGET_EXPERIMENTATEUR_PAR_CARTE_USD,",
     "n * v5.BUDGET_TEST_USD_DEFAUT,", [TT + "ReservationI30"], r"I30"),
    ("I30 : borne par carte relevée à 0,5 USD (constante)", constante(TF), "BUDGET_EXPERIMENTATEUR_PAR_CARTE_USD", None, 0.5,
     [TG + "DevisI30", TT + "ReservationI30"], r"I30"),
    ("mineur 34 : dossier du bac laissé par une sonde refusée", LANCEUR, "preparer_bac",
     "        if parent:\n            shutil.rmtree(parent, True)\n        raise", "        raise",
     [TT + "SondeDuBac", TT + "CheminReelVerifierSeulement"], r"mineur 34"),
    ("mineur 34 : dossier des sessions laissé par un refus (mode réel)", LANCEUR, "principal",
     "        for d in (parent_bac, base_sessions):  # mineur 34 (v63) : un refus ne laisse aucun dossier temporaire\n"
     "            if d:\n                shutil.rmtree(d, True)\n", "", [TT + "CheminReelVerifierSeulement"], r"mineur 34"),
    ("lecture v63 d'un relevé d'une autre version du cœur", LECTEUR, "lire",
     'if rapport.get("version") != VERSION_DU_COEUR or rapport["releve"].get("version") != VERSION_DU_COEUR:', "if False:",
     [TT + "CourseSaine"], r"autre version du cœur"),
    ("I31, garde 8 : clés en trop acceptées au gabarit", TF, "completer_carte", "if en_trop or manquantes:", "if manquantes:",
     [TT + "GrammaireServie", TT + "Garde8Course"], r"garde 8|clés en trop"),
    ("I31, garde 9 : familles non séparées acceptées", TF, "exiger_familles_separees",
     "if not experimentateur[1] or not verificateur[1] or experimentateur[1] == verificateur[1]:", "if False:",
     [TT + "Garde9", TT + "RefusAvantToutAppel"], r"FamillesNonSeparees not raised"),
    ("I31, garde 7 : témoin dans l'archive ou la vue accepté", TF, "exiger_sans_temoin", "if presents:", "if False:", [TT + "Garde7"], NR),
]

MUTATIONS_V63 = PORTEES_V62 + SONDES_CL3 + CORRECTIONS_V63


def appliquer(cible, nom, ancien, nouveau):
    if isinstance(cible, tuple) and cible and cible[0] == "constante":
        module = cible[1]
        avant = getattr(module, nom)
        setattr(module, nom, nouveau(avant) if callable(nouveau) else nouveau)
        return lambda: setattr(module, nom, avant)
    return m56.appliquer(cible, nom, ancien, nouveau)


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    seul = argv[argv.index("--seulement") + 1] if "--seulement" in argv else None
    liste = [m for m in MUTATIONS_V63 if seul is None or seul in m[0]]
    noms = sorted({x for m in liste for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    t0 = time.time()
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec", flush=True)
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes = {}
    groupes = {id(m): g for g, l in (("v62", PORTEES_V62), ("cl3", SONDES_CL3), ("v63", CORRECTIONS_V63)) for m in l}
    for m in liste:
        libelle, cible, nom, ancien, nouveau, essais, motif = m
        try:
            restaurer = appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError, KeyError, AttributeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  [{groupes[id(m)]}] {libelle} : {type(e).__name__} : {e}", flush=True)
            continue
        try:
            n, echecs = m55.jouer(essais)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
        verdict = m55.classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  [{groupes[id(m)]}] {libelle} : {len(echecs)}/{n} essais en échec", flush=True)
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {m55._derniere_ligne(txt)}")
    apres = m55.jouer(noms)
    total = len(liste)
    print(f"mutations v63 : {total} (portées de la v62 : {len([m for m in liste if groupes[id(m)] == 'v62'])}, sondes et bords de la "
          f"contre-lecture 3 : {len([m for m in liste if groupes[id(m)] == 'cl3'])}, corrections v63 : "
          f"{len([m for m in liste if groupes[id(m)] == 'v63'])}) ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour "
          f"une autre raison : {comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; "
          f"survivantes : {comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)} ; {time.time() - t0:.0f} s")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
