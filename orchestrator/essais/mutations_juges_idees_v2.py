"""Banc de mutations de l'étage des juges d'idéation v2, brouillon 2 (R5 : chaque garde neutralisée doit faire échouer son essai,
**pour la bonne raison**) — cœur `pole/juges_idees_v2.py` et lanceur `demonstrations/validation_juges_idees_v2.py`.

Mécanique des bancs v55 et v56 (`essais/mutations_v55.py`) : la fonction visée est recompilée en mémoire avec le fragment
muté, substituée, puis restaurée ; aucun fichier n'est modifié. Une mutation n'est « tuée » que si au moins un essai visé échoue
avec un texte qui correspond au **motif attendu** ; un échec d'une autre nature est « tuée pour une autre raison » (non tuée), un
échec du banc lui-même (`__class__`, `NameError`, `SyntaxError`) « défaut du banc ». Les courses à juges scriptés mémorisées par
le module d'essais sont oubliées avant chaque mutation ; le contrôle de diagnosticité mémorisé est oublié avant et après chaque
mutation qui vise la classe `Diagnosticite` (sinon un résultat calculé sous mutation resterait en mémoire).

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
VRAI = r"False is not true"
REFUS = r"0 != 2"
CHEMIN = [P + "LanceurCheminReel"]

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
    # --- gardes A4, matériaux, forme -------------------------------------------------------------------------------------------
    ("garde A4 retirée de l'entrée complète d'une paire", J, "entree_paire",
     'garde_a4(entree, interdites, mode, "l\'entrée complète")', "pass", [P + "Entrees"], r"ProtocoleRefuse not raised"),
    ("étiquette interdite pendant la course : erreur brute au lieu d'un arrêt avec journal", J, "jouer_etape",
     "raise ArretJuges(f\"{e} (lot {lot['nom']}, paire {premier}, {second})\") from None", "raise", [P + "Entrees"],
     r"EtiquetteDansEntree"),
    ("empreinte interne des matériaux non vérifiée", J, "exiger_materiaux", 'if calculee != materiaux.get("empreinte"):',
     "if False:", [P + "Materiaux"], r"ProtocoleRefuse not raised"),
    ("matériaux d'une autre empreinte que celle du texte admis", J, "exiger_materiaux",
     "if empreinte_attendue is not None and calculee != empreinte_attendue:", "if False:", [P + "Materiaux"],
     r"ProtocoleRefuse not raised"),
    ("vérité connue des témoins non exigée", J, "exiger_materiaux", "if ecarts:", "if False:", [P + "Materiaux"], NR),
    ("contrôle de forme des témoins ignoré", J, "exiger_materiaux", 'if not forme["conforme"]:', "if False:",
     [P + "Materiaux"], r"ProtocoleRefuse not raised"),
    ("contrôle de forme réduit à la longueur et aux chiffres (brouillon 1)", J, "controle_forme",
     "for k in INDICES_FORME}", 'for k in ("longueur", "chiffres")}', [P + "Materiaux"], r"KeyError|True is not false|not raised"),
    ("contrôle de forme sans borne basse (indice favorable aux mauvais témoins admis)", J, "controle_forme",
     "1 - seuil - 1e-12 <= a <= seuil + 1e-12", "a <= seuil + 1e-12", [P + "Materiaux"], FAUX),
    ("étiquette interdite dans un témoin non contrôlée", J, "exiger_materiaux",
     "garde_a4(json.dumps(f[\"contenu\"], ensure_ascii=False), ETIQUETTES_INTERDITES_TEMOINS, \"prefixe\", f\"la fiche {f['ident']}\")",
     "pass", [P + "Materiaux"], r"ProtocoleRefuse not raised"),
    ("loi fausse de deux groupes non contrôlée contre la table", J, "verifier_materiaux",
     'if classe == "fausse_redigee" and not (xa - xb >= ECART_VRAI_MIN and abs(oa - ob) <= ECART_NUL_MAX):', "if False:",
     [P + "Materiaux"], VRAI),
    ("loi fausse graduée non contrôlée contre la table", J, "verifier_materiaux",
     'if classe == "fausse_redigee" and not (loi["affirme"][1] - loi["affirme"][0] >= ECART_VRAI_MIN',
     'if False and not (loi["affirme"][1] - loi["affirme"][0] >= ECART_VRAI_MIN', [P + "Materiaux"], VRAI),
    ("signe contraire non contrôlé", J, "verifier_materiaux",
     'if classe == "signe_contraire" and loi.get("signe_prediction") == loi["signe"]:', "if False:", [P + "Materiaux"], VRAI),
    ("champ « signe » non contrôlé", J, "verifier_materiaux", 'if f["contenu"].get("signe") != loi.get("signe_prediction"):',
     "if False:", [P + "Materiaux"], VRAI),
    # --- diagnosticité (contre-lecture v1, B1) ----------------------------------------------------------------------------------
    ("contrôle de diagnosticité ignoré par la garde des matériaux", J, "exiger_materiaux", 'if not diag["conforme"]:', "if False:",
     [P + "Diagnosticite"], r"ProtocoleRefuse not raised"),
    ("diagnosticité : juges de forme jamais retenus contre les matériaux", J, "controle_diagnosticite",
     'if d1 > DIAGNOSTICITE_D1_MAX or resume["aire_moyenne"] > DIAGNOSTICITE_AIRE_MAX:', "if False:", [P + "Diagnosticite"], VRAI),
    ("diagnosticité : D1b du juge « dossier sans tables » jamais retenu", J, "controle_diagnosticite",
     "if d1b > DIAGNOSTICITE_D1B_MAX:", "if False:", [P + "Diagnosticite"], VRAI),
    # --- plan, famille -------------------------------------------------------------------------------------------------------
    ("règle de famille désactivée", J, "juge_admissible", "return all(famille_juge not in f for f in familles)", "return True",
     [P + "Plan"], r"False is not true|ProtocoleRefuse not raised"),
    ("juge de la famille des gabarits admis (cœur)", J, "etapes_v2", "if j[\"famille\"] == FAMILLE_AUTEUR_TEMOINS:", "if False:",
     [P + "Plan"], r"ProtocoleRefuse not raised"),
    ("juges A et B sur le même relais admis (cœur)", J, "etapes_v2",
     'or juge_a.get("fournisseur") == juge_b.get("fournisseur")):', "or False):", [P + "Plan"], r"ProtocoleRefuse not raised"),
    ("paires du juge B non restreintes aux paires mélangées", J, "etapes_v2",
     "melangees = [p for p in graphes[(lot[\"nom\"], 1)][\"paires\"] if qualite[p[0]] != qualite[p[1]]]",
     "melangees = list(graphes[(lot[\"nom\"], 1)][\"paires\"])", [P + "Plan"], r"False is not true|not less than or equal"),
    ("graphe : degré impair sur un nombre impair de fiches admis", J, "graphe_circulant", "if degre % 2 == 1 and n % 2 == 1:",
     "if False:", [P + "Plan"], r"ProtocoleRefuse not raised"),
    ("identifiant réel de la forme des témoins admis (contre-lecture v1, M5)", J, "lot_reel_depuis",
     'if re.match(r"^monde-\\d+-\\d+$", f["ident"]):', "if False:", [P + "Plan"], r"ProtocoleRefuse not raised"),
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
     'xa.append(e["premier_gagne"])', [P + "Mesures"], r"0\.0 != 1\.0|1\.0 != 0\.0|within"),
    ("bascule de position mal comptée", J, "biais_position", 'bascules += es[0]["gagnant"] != es[1]["gagnant"]',
     'bascules += es[0]["gagnant"] == es[1]["gagnant"]', [P + "Mesures", P + "Statistiques"], r"0\.0 != 1\.0|1\.0 != 0\.0|1 != 0|0 != 1"),
    ("bascule groupée par paire tous tirages confondus (contre-lecture v1, M3)", J, "biais_position",
     'par_paire.setdefault((e.get("tirage"), tuple(e["paire"])), []).append(e)', 'par_paire.setdefault(tuple(e["paire"]), []).append(e)',
     [P + "Statistiques"], r"0 != 2"),
    ("part du premier mal comptée", J, "biais_position", 'premier = sum(1 for e in valides if e["premier_gagne"])',
     'premier = sum(1 for e in valides if not e["premier_gagne"])', [P + "Mesures"], r"0\.0 != 1\.0|1\.0 != 0\.0"),
    ("test-retest : plafond binaire faux", J, "plafond_spearman_binaire", "return 1.0 - sum(", "return 1.0 + 0 * sum(",
     [P + "Statistiques"], r"within 7 places"),
    ("test binomial : queue mal comptée", J, "test_binomial_unilateral", "for x in range(k, n + 1)", "for x in range(k + 1, n + 1)",
     [P + "Statistiques"], r"0\.125|within 7 places"),
    ("seuil binomial décalé d'un cran", J, "seuil_binomial", "return k + 1", "return k", [P + "Statistiques"],
     r"not less than or equal to 0\.1"),
    # --- statuts du relais, appels, reprises (contre-lecture v1, B2) -----------------------------------------------------------
    ("A2 : modèle servi différent sur « ok » non contrôlé", J, "classer_resultat", "if not modele_conforme(modele, r.modele_servi):",
     "if False:", [P + "Relais"], r"ArretModeleServi not raised|'reponse' != 'a2'"),
    ("A2 : modèle servi absent admis (contre-lecture v1, B7)", J, "classer_resultat",
     "if not modele_conforme(modele, r.modele_servi):",
     "if r.modele_servi is not None and not modele_conforme(modele, r.modele_servi):", [P + "Relais"],
     r"ArretModeleServi not raised|'reponse' != 'a2'"),
    ("A2 : statut « refus » de la commande v56 lu comme un refus du modèle", J, "classer_resultat", "if ev in EVENEMENTS_A2:",
     "if False:", [P + "Relais"], r"ArretModeleServi not raised|'refus_modele' != 'a2'"),
    ("refus du modèle lu comme une réponse", J, "appeler",
     'texte = (r.texte_brut or r.texte_final) if c["genre"] == "reponse" else None', "texte = (r.texte_brut or r.texte_final)",
     [P + "Relais"], r"is not None"),
    ("rien d'envoyé compté comme une perte (aucune attente)", J, "appeler", "if rien_envoye:", "if False:", [P + "Relais"],
     r"'perte' != 'reponse'"),
    ("quota (code 4) non repris après attente", J, "appeler", 'rien_envoye = (c["genre"] in ("relais", "quota")',
     'rien_envoye = (c["genre"] in ("relais",)', [P + "Relais"], r"'perte' != 'reponse'"),
    ("panne du juge jamais déclarée (attente sans fin)", J.Compteur, "verifier_panne", "if sans_reponse > PANNE_DUREE_S:",
     "if False:", [P + "Relais"], r"ArretDuree"),
    ("échecs coûteux consécutifs jamais une panne", J.Compteur, "verifier_echecs_couteux",
     "if self.echecs_couteux_suite.get(juge, 0) >= ECHECS_COUTEUX_MAX:", "if False:", [P + "Relais"],
     r"ArretPanne not raised|ArretInfrastructure"),
    ("appel perdu jamais repris", J, "jouer_etape", "a_faire.append((x, essai + 1))", "pass", [P + "Relais"], r"2 != 3"),
    ("reprise sans borne", J, "jouer_etape", "definitive = essai > REPRISES_MAX", "definitive = False", [P + "Relais"], r"3 != 2"),
    ("pertes définitives sans plafond de 15 %", J, "_garde_pertes", "if n > PERTES_MAX_PART * prevus:", "if False:", [P + "Relais"],
     r"ArretInfrastructure not raised"),
    ("incident compté dans le prix observé", J.Compteur, "noter", "if connu and dans_le_prix:", "if connu:", [P + "Relais"],
     r"Lists differ"),
    # --- compteur ------------------------------------------------------------------------------------------------------------
    ("plafond de dépense de la course ignoré", J.Compteur, "budget_appel", "if self.reste() < MINIMUM_APPEL_USD:", "if False:",
     [P + "Compteur"], r"ArretPart|ArretDevis not raised"),
    ("part du juge ignorée", J.Compteur, "budget_appel", "if self.reste_part(juge) < MINIMUM_APPEL_USD:", "if False:",
     [P + "Compteur"], r"ArretPart not raised"),
    ("projection : reste de la part ignoré", J.Compteur, "tient", "if pj > self.reste_part(j) + 1e-9:", "if False:",
     [P + "Compteur"], FAUX),
    ("projection : reste du plafond ignoré", J.Compteur, "tient", "if p > self.reste() + 1e-9:", "if False:", [P + "Compteur"],
     r"ArretDevis not raised"),
    ("durée maximale ignorée", J.Compteur, "verifier_duree", "if ecoule > self.duree_max_s:", "if False:",
     [P + "Compteur", P + "Pannes"], r"ArretDuree not raised"),
    ("durée maximale nulle admise (cœur)", J.Compteur, "__init__",
     "if isinstance(duree_max_s, bool) or not (isinstance(duree_max_s, (int, float)) and math.isfinite(duree_max_s) and duree_max_s > 0):",
     "if False:", [P + "Compteur"], r"ProtocoleRefuse not raised"),
    ("coût déclaré illisible admis", J.Compteur, "noter",
     "if isinstance(cout, bool) or not (isinstance(cout, (int, float)) and math.isfinite(cout) and cout >= 0):", "if False:",
     [P + "Compteur"], r"ArretDevis not raised"),
    # --- course : projections, arrêts du juge ou de la course -------------------------------------------------------------------
    ("projections de la dépense toujours tenues", J, "executer_validation", "ok, motif = compteur.tient(besoin)",
     "ok, motif = True, None", [P + "Pannes"], r"ArretDevis not raised|False is not true|\[\] is not true|ArretPart"),
    ("phase décisive de A au-delà de la part : pas d'arrêt", J, "executer_validation",
     'raise ArretDevis(f"phase {phase} : {motif} : la phase décisive ne tiendrait pas", juge=j, phase=phase)', "pass",
     [P + "Pannes"], r"ArretDevis not raised"),
    ("phase de B projetée en bloc (les comparaisons de B perdues avec l'ancien protocole)", J, "executer_validation",
     'if mode == "etape":', "if False:", [P + "Pannes"], r"False is not true|is not true"),
    ("arrêt du juge B étendu à toute la course", J, "executer_validation", 'if phase == "decisive-a":', "if True:", [P + "Pannes"],
     r"ArretPanne|ArretValidite"),
    ("arrêt dans la phase décisive de A non remonté à la course", J, "executer_validation", 'if phase == "decisive-a":',
     "if False:", [P + "Pannes", P + "Mesures"], r"ArretPanne not raised|ArretValidite not raised"),
    ("juge arrêté : ses étapes suivantes jouées quand même", J, "executer_validation", "if j in exclus or j in sautes:",
     "if False:", [P + "Pannes"], r"Lists differ|!= \[|First differing"),
    ("garde de validité retirée", J, "_garde_validite", "if mauvais > VALIDITE_GARDE_PART * len(fenetre):", "if False:",
     [P + "Mesures"], r"ArretValidite not raised"),
    ("erreur d'un relais non convertie en arrêt (journal perdu)", J, "executer_validation",
     'raise ArretJuges(f"erreur pendant la course : {type(erreur).__name__} : {str(erreur)[:500]}", journal) from erreur', "raise",
     [P + "Pannes"], r"OSError: relais injoignable"),
    # --- lecture gelée ----------------------------------------------------------------------------------------------------------
    ("lecture : l'issue « ne fait pas mieux » n'est jamais prononcée", J, "lire_validation", 'elif not crit["D1"]["tenu"]:',
     "elif False:", [P + "Lecture"], r"!= 'I3'"),
    ("lecture : phase décisive incomplète ignorée", J, "lire_validation",
     'raisons_i0.append("phase décisive du juge A incomplète ou arrêtée")', "pass", [P + "Lecture"], r"!= 'I0'"),
    ("lecture : pertes du relais au-delà de 15 % ignorées", J, "lire_validation",
     'if da.get("prevus") and da.get("pertes_definitives", 0) > s["pertes_max_part"] * da["prevus"]:', "if False:",
     [P + "Lecture"], r"!= 'I0'"),
    ("lecture : D6 mesuré sous 20 comparaisons valides de B", J, "lire_validation",
     'b_mesurable = bool(ex.get("n") and ex["n"] >= s["paires_b_min"] and', 'b_mesurable = bool(ex.get("n") and', [P + "Lecture"],
     r"is not None"),
    ("lecture du bras : S1 confondue avec S2", J, "lire_validation", 'bras = "S2" if crit["D2"]["tenu"] else "S1"', 'bras = "S2"',
     [P + "Lecture"], r"Lists differ"),
    ("lecture : réserve « accord du juge B non mesuré » absente", J, "lire_validation",
     'reserves.append("accord du juge B non mesuré (moins de 20 comparaisons valides, ou validité sous 0,85)")', "pass",
     [P + "Lecture", P + "Pannes"], r"False is not true|\[\] is not true"),
    ("audit : un résultat décevant ne déclenche rien", J, "audit_symetrie", 'motifs.append(f"décevant : {nom} {valeur:.3f} ≤ {bas}")',
     "pass", [P + "Lecture"], VRAI),
    # --- lanceur ----------------------------------------------------------------------------------------------------------------
    ("lanceur : brouillon admis", L, "lire_preenregistrement",
     "if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)):",
     "if os.path.dirname(reel) != dossier:", CHEMIN, REFUS),
    ("lanceur : texte au bon nom hors du dossier fixé admis (contre-lecture v1, B7)", L, "lire_preenregistrement",
     "if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)):",
     "if not NOM_PREREG.match(os.path.basename(reel)):", CHEMIN, REFUS),
    ("lanceur : texte non scellé admis", L, "lire_preenregistrement", "if not verifier_scelle(reel):", "if False:", CHEMIN, REFUS),
    ("lanceur : marqueur restant admis", L, "lire_preenregistrement", "if restants:", "if False:", CHEMIN, REFUS),
    ("lanceur : fermeture du code incomplète admise", L, "lire_preenregistrement",
     "if sorted(noms) != sorted(FICHIERS_GELES) or len(set(noms)) != len(noms):", "if False:", CHEMIN, REFUS),
    ("lanceur : empreintes du code non comparées", L, "lire_preenregistrement", "if presente != attendue:", "if False:", CHEMIN, REFUS),
    ("lanceur : clés du plan non vérifiées", L, "lire_plan", "if set(lignes) != CLES_PLAN:", "if False:", CHEMIN, r"'clés' not found"),
    ("lanceur : valeurs fixes du plan non comparées", L, "lire_plan", "if lignes[k] != v:", "if False:", CHEMIN, REFUS),
    ("lanceur : juges A et B sur le même relais admis (contre-lecture v1, B7)", L, "lire_plan",
     'if a["etiquette"] == b["etiquette"] or a["famille"] == b["famille"] or a["fournisseur"] == b["fournisseur"]:',
     'if a["etiquette"] == b["etiquette"] or a["famille"] == b["famille"]:', CHEMIN, r"'plan-gele : juges A et B' not found"),
    ("lanceur : juge de la famille des gabarits admis", L, "lire_plan", 'if j["famille"] == J.FAMILLE_AUTEUR_TEMOINS:', "if False:",
     CHEMIN, r"'plan-gele : juge juge-b de la famille' not found"),
    ("lanceur : consigne v2 d'une autre empreinte admise", L, "lire_plan",
     'if lignes["consigne_paire_sha256"] != J.EMPREINTE_CONSIGNE_PAIRE_V2:', "if False:", CHEMIN, REFUS),
    ("lanceur : plafond au-dessus de 60 USD admis", L, "lire_plan", "if not 0 < plafond <= PLAFOND_MAX_USD:", "if not 0 < plafond:",
     CHEMIN, r"'hors de \]0' not found"),
    ("lanceur : parts des juges hors du plafond admises", L, "lire_plan", "if not (pa > 0 and pb > 0 and pa + pb <= plafond + 1e-9):",
     "if False:", CHEMIN, REFUS),
    ("lanceur : durée maximale nulle admise (contre-lecture v1, B7)", L, "lire_plan", "if not duree > 0:", "if False:", CHEMIN,
     r"'duree_max_h > 0' not found"),
    ("lanceur : graine admise en mode réel", L, "principal", "if args.graine is not None:", "if False:", CHEMIN, REFUS),
    ("lanceur : options de plan admises en mode réel", L, "principal", "if donnees:", "if False:", CHEMIN, REFUS),
    ("lanceur : configuration d'une autre empreinte admise", L, "preparer_reel", 'if sha_conf != plan["configuration_sha256"]:',
     "if False:", CHEMIN, REFUS),
    ("lanceur : GO autre que celui du texte admis", L, "verifier_go", 'if go != plan["go"]:', "if False:", CHEMIN, REFUS),
    ("lanceur : GO non vérifié au registre (montant, type, validité, révocation)", L, "verifier_go",
     'return cfg.verifier_go_v56(go, registre, plan["plafond_usd"])', 'return {"identifiant": go}', CHEMIN, REFUS),
    ("lanceur : variable de clé admise", L, "juges_reels", "if presents:", "if False:", CHEMIN,
     r"'les relais tiennent les clés' not found"),
    ("lanceur : budget par appel sous deux fois le prix de plan admis", L, "budget_par_appel", "if b + 1e-12 < minimum:",
     "if False:", CHEMIN, REFUS),
    ("lanceur : matériaux non comparés à l'empreinte du texte", L, "preparer_reel",
     'controles = J.exiger_materiaux(materiaux, plan["materiaux_sha256"])', "controles = J.exiger_materiaux(materiaux)", CHEMIN, REFUS),
    ("lanceur : pièce de la configuration absente admise (contre-lecture v1, B7)", L, "preparer_reel", "if plan[k] not in pieces:",
     "if False:", CHEMIN, r"'absente' not found"),
    ("lanceur : lot réel non soumis à la garde A4 de la configuration (contre-lecture v1, B7)", L, "preparer_reel",
     'J.exiger_lot_reel(lot_reel, lot_reel["interdites"], lot_reel["mode_a4"])', "pass", CHEMIN, r"'réelle' not found"),
    ("lanceur : devis requis non comparé à la part du juge", L, "verifier_devis",
     'if d["requis_usd"].get(e, 0.0) > plan[f"plafond_{cle}_usd"] + 1e-9:', "if False:", CHEMIN, REFUS),
    ("lanceur : durée haute non comparée à la durée maximale (contre-lecture v1, B7)", L, "verifier_devis",
     'if d["duree_h"][1] * 3600.0 > plan["duree_max_s"] + 1e-9:', "if False:", CHEMIN, REFUS),
    ("lanceur : relais d'un juge absent admis", L, "juges_reels", 'if j["fournisseur"] not in adaptateurs:', "if False:", CHEMIN,
     r"'relais' not found"),
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
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
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
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec", flush=True)
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {_derniere_ligne(txt)}")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS:
        diagnostic = any(e.endswith("Diagnosticite") for e in essais)
        if diagnostic:
            J._DIAGNOSTICITES.clear()
        try:
            restaurer = appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  {libelle} : {e}", flush=True)
            continue
        try:
            n, echecs = jouer(essais)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
            if diagnostic:
                J._DIAGNOSTICITES.clear()
        verdict = classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec", flush=True)
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {_derniere_ligne(txt)}")
    apres = jouer(noms)
    total = len(MUTATIONS)
    print(f"mutations juges-idees-v2 (brouillon 2) : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour "
          f"une autre raison : {comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; "
          f"survivantes : {comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
