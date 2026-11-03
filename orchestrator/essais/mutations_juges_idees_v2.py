"""Banc de mutations de l'étage des juges d'idéation v2, brouillon 3 (R5 : chaque garde neutralisée doit faire échouer son essai,
**pour la bonne raison**) — cœur `pole/juges_idees_v2.py` et lanceur `demonstrations/validation_juges_idees_v2.py`.

Mécanique des bancs v55 et v56 (`essais/mutations_v55.py`) : la fonction visée est recompilée en mémoire avec le fragment
muté, substituée, puis restaurée ; aucun fichier n'est modifié. Une mutation n'est « tuée » que si au moins un essai visé échoue
avec un texte qui correspond au **motif attendu** ; un échec d'une autre nature est « tuée pour une autre raison » (non tuée), un
échec du banc lui-même (`__class__`, `NameError`, `SyntaxError`) « défaut du banc ». Les courses à juges scriptés mémorisées par
le module d'essais sont oubliées avant chaque mutation ; le contrôle de diagnosticité mémorisé est oublié avant et après chaque
mutation qui vise la classe `Diagnosticite` (sinon un résultat calculé sous mutation resterait en mémoire).

  python3 -I -B essais/mutations_juges_idees_v2.py [--raisons] [--seulement MOTIF]      (depuis le dossier orchestrator)

`--seulement MOTIF` (expression régulière sur le libellé) ne joue que les mutations qu'elle retient (mise au point) ; le banc
complet est celui sans `--seulement`.
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
     'if classe == "fausse_redigee" and not (abs(loi["affirme"][1] - loi["affirme"][0]) >= ECART_VRAI_MIN',
     'if False and not (abs(loi["affirme"][1] - loi["affirme"][0]) >= ECART_VRAI_MIN', [P + "Materiaux"], VRAI),
    ("signe contraire non contrôlé", J, "verifier_materiaux",
     'if classe == "signe_contraire" and loi.get("signe_prediction") == loi["signe"]:', "if False:", [P + "Materiaux"], VRAI),
    ("champ « signe » non contrôlé", J, "verifier_materiaux", 'if f["contenu"].get("signe") != loi.get("signe_prediction"):',
     "if False:", [P + "Materiaux"], VRAI),
    # --- diagnosticité (contre-lecture v1, B1) ----------------------------------------------------------------------------------
    ("contrôle de diagnosticité ignoré par la garde des matériaux", J, "exiger_materiaux", 'if not diag["conforme"]:', "if False:",
     [P + "Diagnosticite"], r"ProtocoleRefuse not raised"),
    ("diagnosticité : juges de forme jamais retenus contre les matériaux", J, "controle_diagnosticite",
     'if nom != "dossier_sans_tables" and (d1 > DIAGNOSTICITE_D1_MAX or resume["aire_moyenne"] > DIAGNOSTICITE_AIRE_MAX):',
     "if False:", [P + "Diagnosticite"], VRAI),
    ("diagnosticité : D1b du juge « dossier sans tables » jamais retenu", J, "controle_diagnosticite",
     "if d1b > DIAGNOSTICITE_D1B_MAX or (af is not None and af > DIAGNOSTICITE_AIRE_D1B_MAX):",
     'if nom != "dossier_sans_tables" and (d1b > DIAGNOSTICITE_D1B_MAX or (af is not None and af > DIAGNOSTICITE_AIRE_D1B_MAX)):',
     [P + "Diagnosticite"], VRAI),
    # --- brouillon 3 : B8, la lecture des tables ne s'obtient plus sans lire une table (contre-lecture v2) ------------------------
    ("B8 : écart d'une loi fausse non apparié (écarts fixes du brouillon 2)", J, "_ecart_apparie",
     "return int(max(ECART_VRAI_MIN, base + _choisir(rng, JITTER_APPARIE))), k", "return int(_choisir(rng, ECARTS_FAUX)), k",
     [P + "Materiaux"], r"test_ecarts_apparies_et_tables_lues.*(False is not true|\(')"),
    ("B8 : interaction fausse non appariée (écarts décalés de 9 points)", J, "_ecart_apparie",
     "return (base[0] + _choisir(rng, JITTER_APPARIE), max(0, base[1] + _choisir(rng, JITTER_APPARIE))), k",
     "return (base[0] + 9, base[1] + 9), k",
     [P + "Materiaux"], r"test_ecarts_apparies_et_tables_lues.*False is not true"),
    ("B8 : contrôle de forme sans le sous-ensemble de D1b", J, "controle_forme",
     "for a in list(aires.values()) + list(aires_d1b.values()))", "for a in list(aires.values()))",
     [P + "Materiaux"], r"test_artefact_forme_brouillon2_et_sous_ensemble_de_d1b.*(True is not false|not raised)"),
    ("B8 : vocabulaire non contrôlé", J, "controle_forme", "            and all(v[\"conforme\"] for v in vocabulaire.values())}",
     "            and True}", [P + "Materiaux"], r"test_artefact_forme_brouillon2_et_sous_ensemble_de_d1b.*True is not false"),
    ("B8 : centre des taux d'une loi fausse non apparié (centré sur la table)", J, "_fiches_du_monde",
     "centre = _centre_affirme(spec, tables, k_bonne)", 'centre = sum(l["taux"] for l in tables["table1"][cle]) / 3 if genre != "interaction_fausse" else None',
     [P + "Materiaux"], r"test_ecarts_apparies_et_tables_lues.*(False is not true|!=)"),
    ("B8 : écart annoncé hors des indices de forme", J, "indices_forme", '"ecart_affirme": ampleur_annoncee(c)', '"ecart_affirme": 0.0',
     [P + "Materiaux"], r"0\.5 != 1\.0"),
    ("B8 : champ « signe » « - » hors des indices de forme (M12)", J, "indices_forme",
     '"signe_negatif": 1.0 if str(c.get("signe")) == "-" else 0.0', '"signe_negatif": 0.5', [P + "Materiaux"],
     r"0\.5 != 0\.6"),
    ("B8 : juges adverses retirés (juges de forme du brouillon 2 seulement)", J, "juges_du_controle",
     'juges = {"+".join(o): ("forme", o, "surface") for o in VARIANTES_FORME}',
     'juges = {"+".join(o): ("forme", o, "surface") for o in VARIANTES_FORME[:6]}', [P + "Diagnosticite"],
     r"KeyError: 'ampleur'|'ampleur' not found"),
    ("B8 : D1b des juges de surface jamais retenu", J, "controle_diagnosticite",
     "if d1b > DIAGNOSTICITE_D1B_MAX or (af is not None and af > DIAGNOSTICITE_AIRE_D1B_MAX):", "if False:",
     [P + "Diagnosticite"], r"test_artefact_diagnosticite_brouillon2.*False is not true"),
    ("B8 : témoin « lecteur des tables » jamais exigé", J, "controle_diagnosticite",
     "if d1b < DIAGNOSTICITE_TEMOIN_D1B_PART_MIN * graines_plan - 1e-9:", "if False:", [P + "Diagnosticite"],
     r"test_artefact_temoin_qui_ne_lit_pas_les_tables.*(True is not false|False is not true)"),
    ("B8 : lecteur des tables sans comparaison des chiffres", J, "verifier_par_les_tables", "tol = TOLERANCE_LECTEUR_POINTS",
     "tol = 1e9", [P + "Materiaux"], r"test_ecarts_apparies_et_tables_lues.*(False != True|True != False)"),
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
    ("A2 : modèle servi différent sur « ok » non contrôlé", J, "classer_resultat",
     "if not modele_conforme(modele, r.modele_servi, permis):", "if False:", [P + "Relais"],
     r"ArretModeleServi not raised|'reponse' != 'a2'"),
    ("A2 : modèle servi absent admis (contre-lecture v1, B7)", J, "classer_resultat",
     "if not modele_conforme(modele, r.modele_servi, permis):",
     "if r.modele_servi is not None and not modele_conforme(modele, r.modele_servi, permis):", [P + "Relais"],
     r"ArretModeleServi not raised|'reponse' != 'a2'"),
    ("A2 : statut « refus » de la commande v56 lu comme un refus du modèle", J, "classer_resultat", "if ev in EVENEMENTS_A2:",
     "if False:", [P + "Relais"], r"ArretModeleServi not raised|'refus_modele' != 'a2'"),
    ("refus du modèle lu comme une réponse", J, "appeler",
     'texte = (r.texte_brut or r.texte_final) if c["genre"] == "reponse" else None', "texte = (r.texte_brut or r.texte_final)",
     [P + "Relais"], r"is not None"),
    ("code 3 (rien d'envoyé ou pire cas) compté comme une perte (aucune attente)", J, "appeler", 'if c["genre"] == "relais":',
     "if False:", [P + "Relais"], r"'perte' != 'reponse'"),
    ("B9 : quota de Google (code 3 au pire cas) non repris après attente", J, "classer_resultat",
     'return {"genre": "relais", "code": code, "motif": erreur[:200], "envoye": not plancher}',
     'return {"genre": "relais" if plancher else "non_conforme", "code": code, "motif": erreur[:200], "envoye": not plancher}',
     [P + "Relais"], r"'perte' != 'reponse'"),
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
    # --- brouillon 3 : B9, table des codes de la commande réelle ; I6, horloge de panne (contre-lecture v2) -----------------------
    ("B9 : code 4 attendu comme un code 3 (prémisse du brouillon 2)", J, "appeler", 'if c["genre"] == "relais":',
     'if c["genre"] in ("relais", "refus_budget"):', [P + "Relais"], r"ArretPanne|ArretDuree|ArretRefusBudget not raised"),
    ("B9 : code 4 au budget borné par la part lu comme un refus de budget", J, "appeler",
     "if budget < float(plafond_session) - 1e-12:", "if False:", [P + "Relais"], r"ArretRefusBudget"),
    ("B9 : refus de requête (413) attendu comme un relais injoignable", J, "classer_resultat",
     "if plancher and _REQUETE.search(erreur):", "if False:", [P + "Relais"], r"ArretPanne|ArretDuree|'relais' != 'requete'"),
    ("B9 : panne de 6 h dans les phases décisives (budget de temps qui coupe la mesure)", J.Compteur, "verifier_panne",
     "if phase in PHASES_SANS_PANNE:", "if False:", [P + "Relais"], r"ArretPanne"),
    ("B9 : compte d'échecs de suite appliqué au code 3", J, "appeler",
     "compteur.echec(j)\n            attente = ATTENTES_RELAIS_S",
     "compteur.echec_couteux(j)\n            compteur.verifier_echecs_couteux(j)\n            attente = ATTENTES_RELAIS_S",
     [P + "Relais"], r"ArretPanne"),
    ("B9 : attentes du code 3 bornées à 300 s (brouillon 2)", J, "appeler",
     "attente = ATTENTES_RELAIS_S[min(rang, len(ATTENTES_RELAIS_S) - 1)]", "attente = ATTENTES_RELAIS_S[min(rang, 4)]",
     [P + "Relais"], r"Lists differ|!= 19"),
    ("B9 : aucune attente après un échec coûteux", J, "jouer_etape", 'compteur.attendre_apres_echec(juge["etiquette"])', "pass",
     [P + "Relais"], r"\{'nombre': 0"),
    ("I6 : horloge de panne partie du dernier succès (brouillon 2)", J.Compteur, "echec",
     "self.debut_serie.setdefault(juge, self.horloge())",
     "self.debut_serie.setdefault(juge, self.dernier_succes.get(juge, self.horloge()))", [P + "Relais"], r"ArretPanne"),
    ("I6 : horloge de panne non remise à zéro sur une réponse", J.Compteur, "succes", "self.debut_serie.pop(juge, None)", "pass",
     [P + "Relais"], r"ArretPanne"),
    ("I7 : bras sans dossier joué après B (ordre du brouillon 2)", J, "executer_validation", "for phase in PHASES_V2:",
     'for phase in ("decisive-a", "decisive-b", "sans-dossier-a", "reel-ancien", "reel-v2"):', [P + "Pannes"],
     r"0 != 30|Lists differ"),
    ("I7 : identifiants servis admis par la configuration ignorés (A2)", J, "appeler",
     'c = classer_resultat(r, juge["modele"], juge.get("modeles_servis_permis", ()))', 'c = classer_resultat(r, juge["modele"])',
     CHEMIN, r"Lists differ|\[\] != \["),
    ("I8 : journal non écrit au fil de l'eau", J, "ajouter", "if fil is not None:", "if False:", [P + "Pannes"],
     r"Lists differ|0 != 39"),
    ("I8 : interruption de l'orchestrateur non convertie (journal perdu)", J, "executer_validation",
     'raise ArretInterruption(f"interruption de l\'orchestrateur pendant la course ({type(erreur).__name__})", journal) from erreur',
     "raise", [P + "Pannes"], r"KeyboardInterrupt"),
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
     [P + "Compteur", P + "Pannes.test_artefact_duree_maximale"], r"ArretDuree not raised"),  # brouillon 3 : sans la garde, les
    # essais de relais injoignable pour toujours dans une phase décisive ne finiraient pas (aucune panne par la durée) : exclus ici
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
    # --- brouillon 3 : lanceur (contre-lecture v2, I7, I8, M15) et juge « dossier sans tables » (M11) ----------------------------
    ("lanceur : marqueur « À REMPLIR » non cherché (seuls les marqueurs <<…>>)", L, "lire_preenregistrement",
     "restants = sorted(set(MARQUEUR.findall(texte)))", 'restants = sorted(set(re.findall(r"<<[A-Z0-9_]+>>", texte)))', CHEMIN,
     REFUS),
    ("lanceur : porte de plafond absente admise (M15)", L, "juges_reels", 'if j["fournisseur"] not in portes:', "if False:", CHEMIN,
     r"'porte de plafond absente pour « astra »' not found"),
    ("lanceur : identifiants servis de la configuration non transmis au cœur (I7)", L, "preparer_reel",
     'plan[cle]["modeles_servis_permis"] = list(infos["modeles_servis_permis"].get(plan[cle]["etiquette"], []))', "pass", CHEMIN,
     r"KeyError: 'modeles_servis_permis'|Lists differ"),
    ("lanceur : journal au fil de l'eau non scellé sur un arrêt (I8)", L, "principal",
     "        fil.sceller(compteur.bilan())\n        journal = dict(e.partiel", "        journal = dict(e.partiel",
     [P + "LanceurABlanc"], r"False is not true"),
    ("M11 : redite lue par le seul nom de la caractéristique (brouillon 2)", J, "defauts_hors_tables",
     "if (nom is not None and nom in etablies) or lexicale:", "if nom is not None and nom in etablies:", [P + "Materiaux"],
     r"test_redite_lue_par_les_mots_propres_de_la_loi_etablie.*False != True"),
]


# fonctions du cœur que le contrôle de diagnosticité n'appelle jamais (sa mémoire peut rester pendant leurs mutations)
HORS_DU_CONTROLE = frozenset(("lire_validation", "audit_symetrie", "kappa_cohen", "kappa_paires", "plafond_spearman_binaire",
                              "test_binomial_unilateral", "seuil_binomial", "exiger_materiaux", "controle_forme", "indices_forme",
                              "verifier_materiaux", "lot_reel_depuis", "executer_validation", "delong_difference"))


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
    choisies = MUTATIONS
    if "--seulement" in argv:
        motif = re.compile(argv[argv.index("--seulement") + 1])
        choisies = [m for m in MUTATIONS if motif.search(m[0])]
    noms = sorted({x for m in choisies for x in m[5]})
    for n in noms:
        unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec", flush=True)
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {_derniere_ligne(txt)}")
    comptes = {}
    propre = dict(J._DIAGNOSTICITES)
    for libelle, cible, nom, ancien, nouveau, essais, motif in choisies:
        # brouillon 3 : la mémoire du contrôle de diagnosticité est restaurée après chaque mutation (un contrôle calculé sous mutation,
        # par exemple du lecteur des tables, ne sert jamais aux mutations suivantes) ; elle est vidée avant toute mutation du cœur
        # qui peut toucher le chemin du contrôle (tout le cœur sauf `HORS_DU_CONTROLE`) ; une mutation du lanceur la garde
        if cible is not L and nom not in HORS_DU_CONTROLE:
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
            J._DIAGNOSTICITES.clear()
            J._DIAGNOSTICITES.update(propre)
        verdict = classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec", flush=True)
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {_derniere_ligne(txt)}")
    apres = jouer(noms)
    total = len(choisies)
    print(f"mutations juges-idees-v2 (brouillon 3) : {total}{'' if choisies is MUTATIONS else ' (sélection --seulement)'} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour "
          f"une autre raison : {comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; "
          f"survivantes : {comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
