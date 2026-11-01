"""**Version 2 du fichier d'essais** (orchestrateur v51) : les essais de `essais/test_v7_ideation.py` (v50, gardé dans
`CODE-orchestrateur-pole-v7-v50.zip`, R12) rejoués sur les versions 2 du cœur, de l'étage et du lanceur (`pole/ideation_v2.py`,
`pole/tests_de_mort_v2.py`, `demonstrations/ideation_v2.py`), adaptés aux corrections de la contre-lecture CL15 (chaque
adaptation porte « v51 »). Les essais nouveaux de la v51 sont dans `essais/test_v51_bac_reel.py`.

Essais de la version 35 (depuis la 32) : la course d'idéation (prise « idéation » : proposer et classer seulement).

Cas sains : fiche au gabarit validée et empreintée ; liste blanche par empreinte acceptée ; anonymisation par juge
(permutations différentes, clé hors des fiches servies, aucune empreinte servie) ; notes complètes agrégées (moyenne
nommée à deux juges, porte fixée d'avance, porte « unanimité », départage par empreinte) ; course entière avec faux
adaptateur : manifeste de départ scellé avant le premier appel, témoins lus à part, classement lisible, lectures par juge ;
seconde passe qui ajoute (ne remplace pas) et sert le matériau après ; appel de contrôle conforme.
Artefacts (R5) : champ hors gabarit, énumération hors valeurs, bloc JSON absent, liste vide, fiches en trop, note hors
borne, note manquante, pièce hors liste blanche ou à empreinte différente, lien symbolique, variantes de chemin (accents,
`_`, « données »), paraphrases devant la garde, secret caviardé, session en erreur (arrêt dur, code d'erreur), juge
invalide (arrêt), plafond total, appel de contrôle refusé (statut, texte, coût, relais muet), url du relais en https ou
avec chemin, étiquettes invalides, absence de témoins, max_tours trop grand — tous refusés avec un motif.
v35 (CL34) : attestation donnée à la course refusée ; bras différé seul chemin (attestation sans l'empreinte de la consigne
refusée, sceau faux refusé, rejeu refusé, plafond total tenu, témoins lus chez le juge externe, manifeste sur tous les
chemins) ; coût manquant du juge externe → erreur ; environnement minimal de la commande ; `tools=[]` dans les options et
`--tools ''` sur la ligne de commande du kit ; borne de temps par session ; `nombre` borné ; contrôles comptés ; manifeste de
fin sur toute exception ; pluriels devant la garde.
"""

import json
import os
import re
import sys
import unittest

from essais.aides import CasAvecDossier
from pole import ideation_v2 as idn  # v51 : version 2 du cœur (la version 1 est essayée par l'archive de la v50)
from pole.adaptateurs import Resultat, construire_options
from pole.relais import RelaisInvalide


def fiche_brute(**modifs):
    f = {"nom": "Essai", "type": "question",
         "enonce": "Le transfert d'un moniteur vers le diffus suit-il une courbe prédite avant le test ?",
         "loi_predictive": {"espace_instances": "familles × dilution, dix familles", "prediction": "rappel décroît",
                            "signe": "-", "metrique": "rappel à 1 % de fausses alertes"},
         "perte_traduction": "la forme est résumée par une pente",
         "questions_servies": ["Q4", "Q3"],
         "avantage": {"source": "programme", "texte": "théorie explicite", "incopiable_parce_que": "exige la carte"},
         "originalite": {"niveau": "transposition", "texte": "détection de rupture"},
         "demande_organisme": {"nature": "ajout", "texte": "générateur de dilution"},
         "cout": {"nature": "processeur", "ordre_de_grandeur": "jours"},
         "piege": "artefact de découpe", "cosmetique_si": "courbes plates",
         "anteriorite": [{"reference": "Ramtin, Nain, Towsley 2601.20022", "statut": "RAPPORTE"}]}
    for cle, valeur in modifs.items():
        if isinstance(valeur, dict) and isinstance(f.get(cle), dict):
            f[cle] = dict(f[cle], **valeur)
        else:
            f[cle] = valeur
    return f


def notes_pour(identifiants, base=2, **sur):
    notes = []
    for i in identifiants:
        c = {k: base for k in idn.CRITERES}
        c.update(sur.get(i, {}))
        notes.append({"identifiant": i, "criteres": c, "justifications": {k: "ligne" for k in idn.CRITERES}})
    return {"notes": notes, "doublons": []}


class FauxAdaptateur:
    """Rend des fiches pour un proposeur, des notes pour un juge, « OK » pour l'appel de contrôle ; coût fixe ; peut
    simuler une erreur ou des notes données par une fonction (identifiants → objet)."""
    nom = "faux-ideation"

    def __init__(self, fiches_par_etiquette, notes_par_juge=None, cout=0.5, notes_base=2, erreur_pour=(),
                 texte_controle="OK", cout_controle=0.01, statut_controle="ok"):
        self.fiches = fiches_par_etiquette
        self.notes = notes_par_juge or {}
        self.cout, self.notes_base = cout, notes_base
        self.erreur_pour = set(erreur_pour)
        self.texte_controle, self.cout_controle, self.statut_controle = texte_controle, cout_controle, statut_controle
        self.appels = []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        self.appels.append({"role": role, "consigne": consigne, "dossier": dossier, "modele": modele,
                            "budget": budget_usd, "max_tours": max_tours})
        if consigne == idn.APPEL_DE_CONTROLE_CONSIGNE:
            return Resultat(self.texte_controle, [], self.cout_controle, self.statut_controle)
        etiquette = os.path.basename(os.path.dirname(dossier)) if role == "proposeur_ideation" else os.path.basename(dossier)
        passe = os.path.basename(dossier)
        if (etiquette, passe) in self.erreur_pour or etiquette in self.erreur_pour:
            return Resultat("API Error: 400 Bad request version", [], 0.0, "erreur", "APIError")
        if role == "proposeur_ideation":
            fiches = self.fiches[etiquette]
            if callable(fiches):
                fiches = fiches(passe, consigne)
            elif passe == "passe-2":
                fiches = [dict(f, nom=f["nom"] + " (revue)") for f in fiches]
            texte = "Voici.\n```json\n" + json.dumps({"fiches": fiches}, ensure_ascii=False) + "\n```"
            return Resultat(texte, [], self.cout, "ok")
        if role == "juge_ideation":
            idents = sorted(set(re.findall(r'"identifiant": "(T\d\d)"', consigne)))
            objet = self.notes.get(etiquette)
            if callable(objet):
                objet = objet(idents, consigne)
            if objet is None:
                objet = notes_pour(idents, base=self.notes_base)
            return Resultat("```json\n" + json.dumps(objet) + "\n```", [], self.cout, "ok")
        raise AssertionError(role)


class TestFiche(unittest.TestCase):
    def test_fiche_valide_et_empreinte_stable(self):
        a = idn.valider_fiche_ideation(fiche_brute(), "a", 1)
        b = idn.valider_fiche_ideation(fiche_brute(), "b", 7, passe=2)
        self.assertEqual(a["empreinte"], b["empreinte"])
        self.assertEqual(a["identifiant_auteur"], "a-p1-01")
        self.assertEqual(b["identifiant_auteur"], "b-p2-07")
        self.assertNotIn("empreinte", idn.vue_servie(a))
        self.assertNotIn("auteur", idn.vue_servie(a))

    def test_artefacts_refuses_avec_motif(self):
        cas = {"champ hors gabarit": fiche_brute(extra="x"), "type hors valeurs": fiche_brute(type="idee"),
               "signe hors valeurs": fiche_brute(loi_predictive={"signe": "±"}),
               "source hors valeurs": fiche_brute(avantage={"source": "chance"}),
               "incopiable manquant": fiche_brute(avantage={"incopiable_parce_que": ""}),
               "questions vides": fiche_brute(questions_servies=[]),
               "antériorité sans statut": fiche_brute(anteriorite=[{"reference": "x"}]),
               "champ trop long": fiche_brute(piege="x" * (idn.LONGUEUR_MAX_CHAMP + 1))}
        for nom, brut in cas.items():
            with self.assertRaises(idn.FicheIdeationInvalide, msg=nom):
                idn.valider_fiche_ideation(brut, "a", 1)

    def test_secret_caviarde(self):
        faux = "sk-" + "ant-" + "abcdefghijklmnop"  # construit à l'exécution : la recherche de clés du dépôt reste propre
        f = idn.valider_fiche_ideation(fiche_brute(piege="clé " + faux + " dans le texte"), "a", 1)
        self.assertNotIn(faux, json.dumps(f))

    def test_garde_niveau_methode_paraphrases(self):
        self.assertEqual(idn.signaux_niveau_methode(idn.vue_servie(idn.valider_fiche_ideation(fiche_brute(), "a", 1))), [])
        for phrase in ("Étape 1 : exécute le script suivant", "Étape 1. ouvrir", "Première étape — préparer",
                       "Phase 1 : préparer", "1) ceci est long\n2) cela", "afin de contourner le moniteur de sortie",
                       "pour échapper au détecteur", "to evade the probe", "injection de consigne", "exploiter la faille",
                       "une porte dérobée", "exfiltration lente"):
            self.assertTrue(idn.signaux_niveau_methode(phrase), phrase)
        for phrase in ("La première famille tenue à l'écart", "un moniteur boîte noire par épisode",
                       "le juge figé à borne", "une sonde linéaire sur la dernière couche"):
            self.assertEqual(idn.signaux_niveau_methode(phrase), [], phrase)


class TestTemoinsEtGardeV34(CasAvecDossier):
    def test_liste_numerotee_dans_une_fiche_signalee(self):
        f = idn.valider_fiche_ideation(fiche_brute(piege="1) préparer le terrain\n2) agir ensuite"), "a", 1)
        self.assertTrue(idn.signaux_niveau_methode(idn.vue_servie(f)))

    def test_classes_de_temoins_imposees(self):
        p = os.path.join(self.tmp, "t.json")

        def ecrire(temoins):
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"temoins": temoins}, f, ensure_ascii=False)
            return idn.construire_liste_blanche([p], os.path.join(self.tmp, f"lb-{len(os.listdir(self.tmp))}.json"))
        complet = [{"fiche": fiche_brute(nom="V"), "attendu": "eligible", "classe": "vrai"},
                   {"fiche": fiche_brute(nom="F1"), "attendu": "ineligible", "classe": "faux_falsifiabilite"},
                   {"fiche": fiche_brute(nom="F2"), "attendu": "ineligible", "classe": "faux_anteriorite"},
                   {"fiche": fiche_brute(nom="J"), "attendu": "eligible", "classe": "jumeau", "jumeau_de": "V"}]
        self.assertEqual(len(idn.charger_temoins(p, ecrire(complet))), 4)
        for mauvais, motif in ((complet[:3], "classe manquante"), (complet[:1] + [dict(complet[1], classe="vrai")] + complet[2:], "faux marqué vrai"),
                               (complet[:3] + [dict(complet[3], jumeau_de=None)], "jumeau sans cible"),
                               (complet[:3] + [dict(complet[3], jumeau_de="X")], "jumeau_de inconnu"),
                               ([dict(t, classe="vrai", attendu="eligible") for t in complet], "une seule classe")):
            with self.assertRaises(idn.FicheIdeationInvalide, msg=motif):
                idn.charger_temoins(p, ecrire(mauvais))


class TestPieces(CasAvecDossier):
    def ecrire(self, nom, contenu="x"):
        chemin = os.path.join(self.tmp, nom)
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        return chemin

    def test_liste_blanche_acceptee_et_variantes_refusees(self):
        p = self.ecrire("piece-a.md", "# A")
        liste = idn.construire_liste_blanche([p], os.path.join(self.tmp, "lb.json"))
        self.assertEqual(idn.verifier_pieces([p], liste), [os.path.realpath(p)])
        for nom in ("donnees/banque.json", "x/mode-tenu-a-l-ecart-v1.md", "x/bras_attaque/a.md", "x/bras-d-attaque/a.md",
                    "données/a.md", "x/mode_tenu_à_l_écart/a.md", "docs/carte-hypotheses-v1.md", "x/banques/a.md",
                    "x/banque_v3.json", "prereg/P3-consignes-v1.md"):
            c = self.ecrire(nom)
            liste2 = dict(liste, **{os.path.realpath(c): idn.sha256_fichier(c)})
            with self.assertRaises(idn.PieceInterdite, msg=nom):
                idn.verifier_pieces([c], liste2)

    def test_hors_liste_empreinte_differente_lien(self):
        p = self.ecrire("piece-b.md", "# B")
        with self.assertRaises(idn.PieceInterdite):
            idn.verifier_pieces([p], {})
        with self.assertRaises(idn.PieceInterdite):
            idn.verifier_pieces([p], {os.path.realpath(p): "0" * 64})
        liste = idn.construire_liste_blanche([p], os.path.join(self.tmp, "lb2.json"))
        with open(p, "a") as f:
            f.write("modifié")
        with self.assertRaises(idn.PieceInterdite):
            idn.verifier_pieces([p], liste)
        lien = os.path.join(self.tmp, "lien.md")
        os.symlink(p, lien)
        liste3 = idn.construire_liste_blanche([p], os.path.join(self.tmp, "lb3.json"))
        with self.assertRaises(idn.PieceInterdite):
            idn.verifier_pieces([lien], dict(liste3, **{os.path.realpath(lien): liste3[os.path.realpath(p)]}))

    def test_url_relais_ideation(self):
        self.assertEqual(idn.valider_url_relais_ideation("http://127.0.0.1:8787"), "http://127.0.0.1:8787")
        for url in ("https://127.0.0.1:8787", "http://127.0.0.1:8787/v1", "http://relais.exemple.org", "http://127.0.0.1:1?x=1"):
            with self.assertRaises(RelaisInvalide, msg=url):
                idn.valider_url_relais_ideation(url)


class TestAnonymisationEtNotes(unittest.TestCase):
    def setUp(self):
        self.fiches = [idn.valider_fiche_ideation(fiche_brute(nom=f"F{i}"), "a" if i < 3 else "b", i) for i in range(1, 7)]

    def test_anonymisation_par_juge(self):
        a1, cle1 = idn.anonymiser(self.fiches, 1, "juge-1")
        a2, cle2 = idn.anonymiser(self.fiches, 1, "juge-2")
        self.assertEqual(sorted(cle1.values()), sorted(f["identifiant_auteur"] for f in self.fiches))
        self.assertNotEqual([a["nom"] for a in a1], [a["nom"] for a in a2])
        for a in a1:
            for champ in idn.CHAMPS_INTERNES:
                self.assertNotIn(champ, a)
        encore, _ = idn.anonymiser(self.fiches, 1, "juge-1")
        self.assertEqual([a["nom"] for a in a1], [a["nom"] for a in encore])

    def test_notes_valides_et_artefacts(self):
        idents = ["T01", "T02"]
        notes, doubles = idn.valider_notes(notes_pour(idents), idents)
        self.assertEqual(set(notes), set(idents))
        with self.assertRaises(idn.NotesInvalides):
            idn.valider_notes(notes_pour(["T01"]), idents)
        trop = notes_pour(idents)
        trop["notes"][0]["criteres"]["avantage"] = 4
        with self.assertRaises(idn.NotesInvalides):
            idn.valider_notes(trop, idents)
        with self.assertRaises(idn.NotesInvalides):
            idn.valider_notes(notes_pour(idents + ["T99"]), idents)
        booleen = notes_pour(idents)
        booleen["notes"][1]["criteres"]["robustesse"] = True
        with self.assertRaises(idn.NotesInvalides):
            idn.valider_notes(booleen, idents)
        demi = notes_pour(idents)
        demi["notes"][0]["criteres"]["avantage"] = 2.5
        with self.assertRaises(idn.NotesInvalides):
            idn.valider_notes(demi, idents)

    def test_agregation_nommee_porte_unanimite_departage(self):
        par = {f["identifiant_auteur"]: f for f in self.fiches}
        ids = list(par)
        j1 = {i: {"criteres": {k: 1 for k in idn.CRITERES}} for i in ids}
        j2 = {i: {"criteres": {k: 1 for k in idn.CRITERES}} for i in ids}
        j1[ids[0]]["criteres"]["avantage"] = 3  # un seul juge élève : moyenne 2 → éligible, unanimité fausse
        j1[ids[1]]["criteres"]["originalite"] = 3
        j2[ids[1]]["criteres"]["originalite"] = 3  # unanimité vraie
        cl = idn.agreger({"j1": j1, "j2": j2}, par)
        parl = {l["identifiant_auteur"]: l for l in cl}
        self.assertEqual(parl[ids[0]]["nom_agregat"], "moyenne")
        self.assertTrue(parl[ids[0]]["eligible"])
        self.assertFalse(parl[ids[0]]["eligible_unanimite"])
        self.assertTrue(parl[ids[1]]["eligible_unanimite"])
        self.assertEqual([l["identifiant_auteur"] for l in cl][:2], [ids[1], ids[0]])  # totaux 7 puis 6
        # les quatre autres fiches sont à égalité stricte (1 partout, inéligibles) : départage par empreinte, déterministe
        reste = [l["identifiant_auteur"] for l in cl][2:]
        self.assertEqual(reste, sorted(reste, key=lambda i: par[i]["empreinte"]))
        trois = idn.agreger({"j1": j1, "j2": j2, "j3": j2}, par)
        self.assertEqual(trois[0]["nom_agregat"], "mediane")


class TestCourse(CasAvecDossier):
    def preparer(self, temoins_json=None):
        p = os.path.join(self.tmp, "piece-a.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("# Pièce A\nTexte de contexte.")
        q = os.path.join(self.tmp, "question.md")
        with open(q, "w", encoding="utf-8") as f:
            f.write("Quelles questions ?")
        m = os.path.join(self.tmp, "materiau.md")
        with open(m, "w", encoding="utf-8") as f:
            f.write("# Matériau\nTour interne.")
        t = os.path.join(self.tmp, "temoins.json")
        with open(t, "w", encoding="utf-8") as f:
            json.dump(temoins_json or {"temoins": [
                {"fiche": fiche_brute(nom="Sobre fort"), "attendu": "eligible", "classe": "vrai"},
                {"fiche": fiche_brute(nom="Verbeux vide", enonce="Long " * 50), "attendu": "ineligible",
                 "note_max": {"falsifiabilite": 1}, "classe": "faux_falsifiabilite"},
                {"fiche": fiche_brute(nom="Assuré occupé", originalite={"niveau": "inedite", "texte": "jamais vu"}),
                 "attendu": "ineligible", "note_max": {"originalite": 1}, "classe": "faux_anteriorite"},
                {"fiche": fiche_brute(nom="Jumeau"), "attendu": "eligible", "jumeau_de": "Sobre fort", "classe": "jumeau"}]},
                f, ensure_ascii=False)
        lb = os.path.join(self.tmp, "liste-blanche.json")
        idn.construire_liste_blanche([p, q, m, t], lb)
        return dict(liste_blanche=lb, question=q, pieces=[p], materiau=[m], temoins=t)

    def budgets(self):
        return {("proposeur_ideation", "claude-opus-5-5"): 1.0, ("proposeur_ideation", "claude-fable-5-1"): 1.0,
                ("juge_ideation", "claude-opus-5-5"): 1.0, ("juge_ideation", "claude-fable-5-1"): 1.0}

    def lancer(self, ad, sortie, **modifs):
        if not hasattr(self, "_prep"):
            self._prep = self.preparer()  # la liste blanche est scellée une fois par essai (jamais écrasée)
        args = dict(self._prep, proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                    juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")], graine=7,
                    budget_total_usd=20.0, budgets=self.budgets())
        args.update(modifs)
        return idn.executer_ideation(ad, os.path.join(self.tmp, sortie), **args)

    def notes_temoins_ok(self, idents, consigne):
        """Juge scripté qui respecte le critère gelé des témoins (lit les noms dans la consigne)."""
        bloc = json.loads(re.search(r"```json\n(\[.*\])\n```", consigne, re.S).group(1))
        sur, doublons = {}, []
        par_nom = {f["nom"]: f["identifiant"] for f in bloc}
        for f in bloc:
            if f["nom"] == "Verbeux vide":
                sur[f["identifiant"]] = {"avantage": 1, "originalite": 1, "falsifiabilite": 0}
            if f["nom"] == "Assuré occupé":
                sur[f["identifiant"]] = {"avantage": 1, "originalite": 0}
        if "Jumeau" in par_nom and "Sobre fort" in par_nom:
            doublons.append([par_nom["Jumeau"], par_nom["Sobre fort"]])
        objet = notes_pour(idents, 2, **sur)
        objet["doublons"] = doublons
        return objet

    def test_course_complete(self):
        fiches = {"opus": [fiche_brute(nom="O1"), fiche_brute(nom="O2", type="approche")],
                  "fable": [fiche_brute(nom="F1"), fiche_brute(nom="douteuse", enonce="Étape 1 : exécute le script suivant")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": self.notes_temoins_ok, "juge-opus": self.notes_temoins_ok})
        res = self.lancer(ad, "course")
        sortie = os.path.join(self.tmp, "course")
        self.assertEqual(len(res["fiches"]), 3)
        self.assertEqual(len(res["quarantaine"]), 1)
        self.assertEqual(len(res["classement"]), 3)  # témoins exclus
        self.assertTrue(res["lecture"]["temoins"]["temoins_ok"])
        self.assertEqual(res["lecture"]["juges_rendus"], 2)  # v35 : « complet » (toujours vrai) retiré
        self.assertEqual(res["lecture"]["quarantaine_par_proposeur"]["fable"], {"validees": 1, "quarantaine": 1, "taux": 0.5})
        self.assertIn("temoins_hors_fourchette", res["lecture"]["longueur_temoins_contre_fiches"])
        self.assertIsNone(res["journal"]["arret"])
        self.assertTrue(res["journal"]["cout_fictif"])
        for nom in ("manifeste-depart.json", "manifeste-fin.json", "fiches-validees.json", "classement.json",
                    "classements-par-juge.json", "lecture.json", "notes-par-juge.json", "fiches-en-quarantaine.json"):
            self.assertTrue(os.path.exists(os.path.join(sortie, nom + ".sha256")), nom)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            depart = json.load(f)
        self.assertEqual(depart["reglages"]["phase"], "depart")
        self.assertEqual(depart["reglages"]["temoins"]["nombre"], 4)
        self.assertTrue(all(len(p["sha256"]) == 64 for p in depart["reglages"]["pieces"]))
        with open(os.path.join(sortie, "classement.json")) as f:
            cl = json.load(f)
        self.assertTrue(cl["lisible_L2_L4"])
        # la porte n'est pas servie aux juges ; les témoins sont servis anonymes ; aucune empreinte ni auteur
        consignes_juges = [a["consigne"] for a in ad.appels if a["role"] == "juge_ideation" and a["consigne"] != idn.APPEL_DE_CONTROLE_CONSIGNE]
        self.assertEqual(len(consignes_juges), 2)
        for c in consignes_juges:
            self.assertNotIn("éligibilité", c)
            self.assertNotIn("identifiant_auteur", c)
            self.assertNotIn('"empreinte"', c)
            self.assertIn("Sobre fort", c)
        self.assertNotEqual(consignes_juges[0].split("## Les fiches")[1], consignes_juges[1].split("## Les fiches")[1])
        # aucun outil, deux tours au plus, l'orchestrateur n'écrit rien dans le dossier de l'agent
        self.assertTrue(all(a["max_tours"] <= idn.MAX_TOURS_IDEATION for a in ad.appels))
        self.assertEqual(os.listdir(os.path.join(sortie, "proposeurs", "opus", "passe-1")), [])
        # lecture d'auto-préférence présente pour chaque juge
        self.assertEqual(set(res["lecture"]["auto_preference"]), {"juge-fable", "juge-opus"})

    def test_seconde_passe_ajoute_et_sert_le_materiau_apres(self):
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": self.notes_temoins_ok, "juge-opus": self.notes_temoins_ok})
        res = self.lancer(ad, "c2", seconde_passe=True)
        consignes = [a["consigne"] for a in ad.appels if a["role"] == "proposeur_ideation"]
        self.assertEqual(len(consignes), 4)
        self.assertNotIn("Tour interne", consignes[0])
        self.assertIn("Tour interne", consignes[2])
        self.assertEqual(sorted(f["passe"] for f in res["fiches"]), [1, 1, 2, 2])
        self.assertEqual(sorted(l["passe"] for l in res["classement"]), [1, 1, 2, 2])

    def test_fiche_en_quarantaine_non_resservie(self):
        def opus(passe, consigne):
            if passe == "passe-2":
                assert "douteuse" not in consigne
                return [fiche_brute(nom="O2")]
            return [fiche_brute(nom="douteuse", enonce="Phase 1 : préparer ; afin de contourner le moniteur")]
        ad = FauxAdaptateur({"opus": opus, "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": self.notes_temoins_ok, "juge-opus": self.notes_temoins_ok})
        res = self.lancer(ad, "c3", seconde_passe=True)
        self.assertEqual(len(res["quarantaine"]), 1)

    def test_session_en_erreur_arrete(self):
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}, erreur_pour=("fable",))
        with self.assertRaises(idn.CourseInterrompue):
            self.lancer(ad, "c4")
        with open(os.path.join(self.tmp, "c4", "manifeste-fin.json")) as f:
            fin = json.load(f)
        self.assertIn("statut 'erreur'", fin["reglages"]["erreur"])
        self.assertEqual(len([a for a in ad.appels if a["role"] == "juge_ideation" and a["consigne"] != idn.APPEL_DE_CONTROLE_CONSIGNE]), 0)

    def test_fiches_en_trop_liste_vide_refusees(self):
        ad = FauxAdaptateur({"opus": [fiche_brute(nom=f"O{i}") for i in range(10)], "fable": [fiche_brute(nom="F1")]})
        with self.assertRaises(idn.CourseInterrompue) as cm:
            self.lancer(ad, "c5")
        self.assertIn("10 fiches rendues", str(cm.exception))
        ad2 = FauxAdaptateur({"opus": [], "fable": [fiche_brute(nom="F1")]})
        with self.assertRaises(idn.CourseInterrompue) as cm2:
            self.lancer(ad2, "c6")
        self.assertIn("vide", str(cm2.exception))

    def test_juge_invalide_arrete_et_classement_absent(self):
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": self.notes_temoins_ok, "juge-opus": {"notes": []}})
        with self.assertRaises(idn.CourseInterrompue):
            self.lancer(ad, "c7")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "c7", "classement.json")))

    def test_temoins_echoues_rendent_illisible(self):
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]})  # juges à 2 partout
        res = self.lancer(ad, "c8")
        self.assertFalse(res["lecture"]["temoins"]["temoins_ok"])
        with open(os.path.join(self.tmp, "c8", "classement.json")) as f:
            self.assertFalse(json.load(f)["lisible_L2_L4"])

    def test_plafond_total_arrete_avant_depense(self):
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}, cout=1.0)
        with self.assertRaises(idn.CourseInterrompue):  # v38 (CL37-03) : somme des plafonds 4 > 1,5 → refus avant tout appel
            self.lancer(ad, "c9a", budget_total_usd=1.5)
        self.assertEqual(ad.appels, [])
        with self.assertRaises(idn.CourseInterrompue):  # tolérée : arrêt au premier dépassement, avant la dépense
            self.lancer(ad, "c9", budget_total_usd=1.5, tolerer_somme_plafonds=True)
        self.assertLessEqual(ad.appels[-1]["budget"], 1.0)

    def test_reglages_refuses(self):
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")]})
        with self.assertRaises(idn.CourseInterrompue):
            self.lancer(ad, "c10", temoins=None)
        with self.assertRaises(idn.CourseInterrompue):
            self.lancer(ad, "c11", juges=[("Juge Opus", "claude-opus-5-5")])
        with self.assertRaises(idn.CourseInterrompue):
            self.lancer(ad, "c12", max_tours=6)
        with self.assertRaises(idn.CourseInterrompue):
            self.lancer(ad, "c13", budgets={})

    def test_appel_de_controle(self):
        sortie = os.path.join(self.tmp, "ctrl")
        etat = {"appels": 0, "depense_usd": 0.0}

        def relais():
            return dict(etat)
        ad = FauxAdaptateur({})
        orig = ad.lancer

        def lancer_compte(*a, **k):
            r = orig(*a, **k)
            etat["appels"] += 1
            etat["depense_usd"] += 0.01
            return r
        ad.lancer = lancer_compte
        lecture = idn.appel_de_controle(ad, ["claude-opus-5-5"], sortie, 0.1, relais)
        self.assertEqual(lecture["claude-opus-5-5"]["problemes"], [])
        for mauvais in (dict(texte_controle="Bonjour"), dict(statut_controle="erreur"), dict(cout_controle=0.0)):
            with self.assertRaises(idn.CourseInterrompue):
                idn.appel_de_controle(FauxAdaptateur({}, **mauvais), ["claude-opus-5-5"], sortie, 0.1, None)
        with self.assertRaises(idn.CourseInterrompue):  # relais muet
            idn.appel_de_controle(FauxAdaptateur({}), ["claude-fable-5-1"], sortie, 0.1, lambda: {"appels": 0, "depense_usd": 0.0})

    def test_options_sans_outil_pour_les_roles_ideation(self):
        dossier = os.path.join(self.tmp, "course", "proposeurs", "opus", "passe-1")
        os.makedirs(dossier)
        for role in ("proposeur_ideation", "juge_ideation"):
            o = construire_options(dossier, 1.0, 2, url_relais="http://127.0.0.1:8787", modele="claude-opus-5-5",
                                   role=role, interdire_lecture=[os.path.join(self.tmp, "course")])
            self.assertEqual(o["allowed_tools"], [])
            self.assertEqual(o["max_turns"], 2)


class TestCommandeExterne(CasAvecDossier):
    """v33 → v36 : juge d'une autre lignée (Argon) par commande externe ; v36 : à poids égal et proposeur à égalité."""

    def commande(self, script, nom="juge.py"):
        chemin = os.path.join(self.tmp, nom)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(script)
        return [sys.executable, "-I", chemin]

    FICHE = json.dumps(fiche_brute(nom="Argon A"), ensure_ascii=False)
    SCRIPT_OK = (
        "import sys, json, re\n"
        "consigne = sys.stdin.read()\n"
        "if 'exactement OK' in consigne:\n"
        "    print(json.dumps({'texte': 'OK', 'cout_usd': 0.001})); sys.exit(0)\n"
        "if consigne.startswith('# Prise « idéation » du pôle — tour de moisson'):\n"  # v47 : réponse au tour de moisson
        "    print(json.dumps({'texte': '```json\\n' + json.dumps({'moisson': [{'source': 'arxiv', 'requete': 'monitor diffuse control', 'resultats': 2}]}) + '\\n```', 'cout_usd': 0.01})); sys.exit(0)\n"
        "if 'passe de proposition' in consigne:\n"
        "    f1 = json.loads(%r); f2 = dict(f1, nom='Argon B')\n"
        "    if 'première passe' in consigne: f1['nom'] = 'Argon A (revue)'\n"
        "    print(json.dumps({'texte': '```json\\n' + json.dumps({'fiches': [f1, f2]}, ensure_ascii=False) + '\\n```', 'cout_usd': 0.25})); sys.exit(0)\n"
        "bloc = json.loads(re.search(r'```json\\n(\\[.*\\])\\n```', consigne, re.S).group(1))\n"
        "par_nom = {f['nom']: f['identifiant'] for f in bloc}\n"
        "notes = []\n"
        "for f in bloc:\n"
        "    c = {k: 2 for k in ('avantage','originalite','falsifiabilite','traitabilite','robustesse')}\n"
        "    if f['nom'] == 'Verbeux vide': c.update({'avantage': 1, 'originalite': 1, 'falsifiabilite': 0})\n"
        "    if f['nom'] == 'Assuré occupé': c.update({'avantage': 1, 'originalite': 0})\n"
        "    if f['nom'].startswith('Argon'): c.update({'avantage': 3})\n"
        "    if f['nom'] == 'O1': c.update({'avantage': 0})\n"
        "    notes.append({'identifiant': f['identifiant'], 'criteres': c, 'justifications': {}})\n"
        "doublons = [[par_nom['Jumeau'], par_nom['Sobre fort']]] if 'Jumeau' in par_nom and 'Sobre fort' in par_nom else []\n"
        "print(json.dumps({'texte': '```json\\n' + json.dumps({'notes': notes, 'doublons': doublons}) + '\\n```', 'cout_usd': 0.3}))\n") % FICHE

    def test_commande_factice_notes_et_controle(self):
        from pole.adaptateurs import AdaptateurCommandeExterne, AdaptateurJugeExterne
        self.assertIs(AdaptateurJugeExterne, AdaptateurCommandeExterne)
        ad = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK), environnement={})
        r = ad.lancer("juge_ideation", idn.APPEL_DE_CONTROLE_CONSIGNE, self.tmp, 0.1, 1, modele="autre-lignee-x")
        self.assertEqual((r.statut, r.texte_final, r.cout_declare_usd, r.cout_inconnu), ("ok", "OK", 0.001, False))
        with self.assertRaises(ValueError):
            ad.lancer("experimentateur", "x", self.tmp, 1.0, 1)
        self.assertEqual(sorted(ad.description()), ["commande", "controle_modele_servi", "delai_s", "empreintes", "modeles_servis_permis",
                                                       "variables_transmises"])
        self.assertIn("facultatif", ad.description()["controle_modele_servi"])  # v49 (CL13-05) : barrière dite absente si non exigée
        self.assertIn(ad.commande[-1], ad.description()["empreintes"])
        with self.assertRaises(ValueError):
            AdaptateurCommandeExterne(self.commande("x"), delai_s=0)

    def test_artefacts_de_la_commande(self):
        """R5 : coût absent, NaN, infini, nul, négatif, sortie non JSON, code ≠ 0 → erreur ; coût imprimé avant un échec
        compté (CL35-02) ; coût illisible → plafond de session compté et marqué inconnu."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        cas = (("import sys; sys.exit(3)", "erreur", 1.0, True),
               ("print('pas du json')", "erreur", 1.0, True),
               ("import json; print(json.dumps({'texte': 'x', 'cout_usd': 9.0}))", "budget_depasse", 9.0, False),
               ("import json; print(json.dumps({'texte': 'x'}))", "erreur", 1.0, True),
               ("import json; print(json.dumps({'cout_usd': 1}))", "erreur", 1.0, True),
               ("print('{\"texte\": \"x\", \"cout_usd\": NaN}')", "erreur", 1.0, True),
               ("print('{\"texte\": \"x\", \"cout_usd\": Infinity}')", "erreur", 1.0, True),
               ("import json; print(json.dumps({'texte': 'x', 'cout_usd': 0}))", "erreur", 1.0, True),
               ("import json; print(json.dumps({'texte': 'x', 'cout_usd': -1}))", "erreur", 1.0, True),
               ("import json, sys; print(json.dumps({'texte': 'x', 'cout_usd': 0.4})); sys.exit(3)", "erreur", 0.4, False),
               ("import json; print(json.dumps({'texte': 'x', 'cout_usd': 0.5}))", "ok", 0.5, False))
        for script, attendu, cout, inconnu in cas:
            ad = AdaptateurCommandeExterne(self.commande(script), environnement={})
            r = ad.lancer("juge_ideation", "consigne", self.tmp, 1.0, 1)
            self.assertEqual((r.statut, r.cout_declare_usd, r.cout_inconnu), (attendu, cout, inconnu), script)
        from pole.relais import CleDansEnvironnement
        ad = AdaptateurCommandeExterne(self.commande("print(1)"), environnement={"ANTHROPIC_API_KEY": "x"})
        with self.assertRaises(CleDansEnvironnement):
            ad.lancer("juge_ideation", "consigne", self.tmp, 1.0, 1)

    def test_delai_arrete_tout_le_groupe(self):
        """CL35-13 : au délai, le petit-enfant de la commande est arrêté aussi ; coût inconnu → plafond compté."""
        import time
        from pole.adaptateurs import AdaptateurCommandeExterne
        pid_f = os.path.join(self.tmp, "petit-enfant.pid")
        script = ("import subprocess, sys, time\n"
                  f"p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
                  f"open({pid_f!r}, 'w').write(str(p.pid))\n"
                  "time.sleep(60)\n")
        ad = AdaptateurCommandeExterne(self.commande(script), environnement={}, delai_s=1.5)
        debut = time.monotonic()
        r = ad.lancer("juge_ideation", "consigne", self.tmp, 0.7, 1)
        self.assertLess(time.monotonic() - debut, 10.0)  # M26 : avec `kill` au lieu de `killpg`, le tube tenu par le petit-enfant bloque 60 s
        self.assertEqual((r.statut, r.cout_declare_usd, r.cout_inconnu), ("erreur", 0.7, True))
        self.assertIn("délai", r.erreur)
        pid = int(open(pid_f).read())

        def vivant():
            try:
                with open(f"/proc/{pid}/status") as f:
                    return not any(l.startswith("State:") and "Z" in l for l in f)
            except OSError:
                return False
        for _ in range(30):
            if not vivant():
                break
            time.sleep(0.1)
        else:
            try:
                os.kill(pid, 9)
            except ProcessLookupError:
                pass
            self.fail("le petit-enfant a survécu au délai")

    def test_environnement_minimal_de_la_commande(self):
        """CL34-09 / CL35-05 : environnement explicite et minimal, plus plafond de session et rôle."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        from pole.relais import CleDansEnvironnement
        script = "import os, json; print(json.dumps({'texte': ','.join(sorted(os.environ)), 'cout_usd': 0.01}))"
        env = {"PATH": os.environ.get("PATH", "/usr/bin"), "HOME": "/tmp", "LANG": "C.UTF-8", "HTTPS_PROXY": "http://x",
               "CHEMIN_CLE_JUGE": "/dev/null", "AUTRE": "1"}
        ad = AdaptateurCommandeExterne(self.commande(script), environnement=env, variables_transmises=("CHEMIN_CLE_JUGE",))
        self.assertEqual(sorted(ad.environnement_commande()), ["CHEMIN_CLE_JUGE", "HOME", "LANG", "PATH"])
        r = ad.lancer("juge_ideation", "consigne", self.tmp, 1.0, 1)
        self.assertEqual(r.statut, "ok")
        self.assertEqual(r.texte_final, "CHEMIN_CLE_JUGE,HOME,LANG,PATH,PLAFOND_SESSION_USD,ROLE_POLE")
        with self.assertRaises(CleDansEnvironnement):
            AdaptateurCommandeExterne(self.commande(script), environnement=env, variables_transmises=("ANTHROPIC_API_KEY",))

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def test_adaptateur_principal_externe_refuse(self):
        """CL35-06 : une commande externe ne peut pas être l'adaptateur principal (ni le rôle réel d'un mixte)."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        ad = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK), environnement={})
        with self.assertRaises(idn.CourseInterrompue):
            c.lancer(ad, "cx-principal")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "cx-principal")))

        class Mixte:
            nom = "mixte"
            reel = ad
        with self.assertRaises(idn.CourseInterrompue):
            c.lancer(Mixte(), "cx-mixte")
        # moteur réel déclaré avec un adaptateur qui n'est pas celui du kit
        faux = FauxAdaptateur({"opus": [fiche_brute()], "fable": [fiche_brute()]})
        with self.assertRaises(idn.CourseInterrompue):
            c.lancer(faux, "cx-moteur", moteur="claude-sdk")
        self.assertEqual(faux.appels, [])

    def test_proposeur_externe_dans_la_course(self):
        """n° 119 : Argon propose à égalité dans la course (question et pièces) ; sa seconde passe exige l'attestation du
        matériau ; il ne voit jamais les fiches des autres ; plafond externe séparé."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        ext = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK), environnement={})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        prop_ext = [("argon", "gemini-argon", ext)]
        with self.assertRaises(idn.CourseInterrompue):  # plafond externe nul
            c.lancer(ad, "cx-0", budgets=budgets, proposeurs_externes=prop_ext, budget_externe_usd=0.0)
        with self.assertRaises(idn.CourseInterrompue):  # seconde passe avec matériau sans attestation : refus avant tout appel
            c.lancer(ad, "cx-1", budgets=budgets, proposeurs_externes=prop_ext, budget_externe_usd=3.0, seconde_passe=True)
        self.assertEqual(ad.appels, [])
        res = c.lancer(ad, "cx-2", budgets=budgets, proposeurs_externes=prop_ext, budget_externe_usd=3.0)
        auteurs = {f["auteur"] for f in res["fiches"]}
        self.assertEqual(auteurs, {"opus", "fable", "argon"})
        self.assertAlmostEqual(res["journal"]["cout_externe_usd"], 0.25)
        self.assertAlmostEqual(res["journal"]["cout_total_usd"], 4 * 0.5)
        self.assertEqual(res["lecture"]["quarantaine_par_proposeur"]["argon"]["validees"], 2)
        # attestation du matériau scellée → seconde passe ; Argon reçoit le matériau et SES fiches seulement
        att = os.path.join(self.tmp, "attestation-materiau.json")
        prep = c._prep
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-28",
                                     "materiau_sha256": {os.path.basename(prep["materiau"][0]):
                                                         idn.sha256_fichier(prep["materiau"][0])}})
        res = c.lancer(ad, "cx-3", budgets=budgets, proposeurs_externes=prop_ext, budget_externe_usd=3.0,
                       seconde_passe=True, attestation_materiau=att)
        consigne2 = open(os.path.join(self.tmp, "cx-3", "proposeurs", "traces-argon", "passe-2", "consigne.md")
                         if os.path.exists(os.path.join(self.tmp, "cx-3", "proposeurs", "traces-argon", "passe-2", "consigne.md"))
                         else os.path.join(self.tmp, "cx-3", "proposeurs", "argon", "traces-passe-2", "consigne.md"),
                         encoding="utf-8").read()
        self.assertIn("Matériau servi", consigne2)
        self.assertIn("Argon A", consigne2)
        self.assertNotIn('"O1"', consigne2)
        self.assertNotIn('"F1"', consigne2)
        self.assertEqual(sum(1 for f in res["fiches"] if f["auteur"] == "argon" and f["passe"] == 2), 2)
        # attestation à l'empreinte fausse → refus avant tout appel
        att2 = os.path.join(self.tmp, "attestation-materiau-fausse.json")
        idn.ecrire_json_scelle(att2, {"lecteur": "Lazar", "lu_le": "2026-10-28",
                                      "materiau_sha256": {os.path.basename(prep["materiau"][0]): "0" * 64}})
        n = len(ad.appels)
        with self.assertRaises(idn.CourseInterrompue):
            c.lancer(ad, "cx-4", budgets=budgets, proposeurs_externes=prop_ext, budget_externe_usd=3.0,
                     seconde_passe=True, attestation_materiau=att2)
        self.assertEqual(len(ad.appels), n)

    def attester(self, chemin, sortie, etiquette="argon"):
        consigne = os.path.join(sortie, "juges-bras-rapporte", f"traces-{etiquette}", "consigne-en-attente.md")
        idn.ecrire_json_scelle(chemin, {"lecteur": "Lazar", "lu_le": "2026-10-28",
                                        "fiches_validees_sha256": idn.sha256_fichier(os.path.join(sortie, "fiches-validees.json")),
                                        "consignes_en_attente_sha256": {etiquette: idn.sha256_fichier(consigne)}})
        return chemin

    def test_bras_differe_a_poids_egal(self):
        """CL34-01, CL34-04, n° 118 : la course n'appelle jamais le juge externe et n'écrit aucun classement ; le bras,
        après attestation scellée, note à poids égal : classement à trois juges (médiane), accords par paire ; jamais rejoué."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1"), fiche_brute(nom="O2")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        externe = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK), environnement={})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        # R5 : attestation donnée à la course → refus avant tout appel
        with self.assertRaises(idn.CourseInterrompue):
            c.lancer(ad, "cx-refus", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")],
                     attestation_lecture_humaine=os.path.join(self.tmp, "x.json"))
        self.assertEqual(ad.appels, [])
        res = c.lancer(ad, "cx", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "cx")
        self.assertTrue(res["en_attente_bras"])
        self.assertIsNone(res["classement"])
        for nom in ("classement.json", "classements-par-juge.json", "lecture.json"):
            self.assertFalse(os.path.exists(os.path.join(sortie, nom)), nom)
        for nom in ("lecture-course.json", "notes-par-juge.json", "noyau/temoins-servis.json", "noyau/modeles.json",
                    "juges-bras-rapporte/traces-argon/consigne-en-attente.md"):
            self.assertTrue(os.path.exists(os.path.join(sortie, nom + ".sha256")), nom)
        self.assertTrue(all("argon" not in os.path.relpath(a["dossier"], sortie) for a in ad.appels))
        externes = [("argon", "autre-lignee-x", externe)]
        # attestation non scellée → refus
        att_nue = os.path.join(self.tmp, "att-nue.json")
        with open(att_nue, "w") as f:
            json.dump({"lecteur": "Lazar"}, f)
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att_nue, budgets=budgets, juges_externes=externes)
        # attestation scellée mais consigne fausse → refus ; aucun manifeste du bras
        att_f = os.path.join(self.tmp, "att-fausse.json")
        idn.ecrire_json_scelle(att_f, {"lecteur": "Lazar", "lu_le": "2026-10-28",
                                       "fiches_validees_sha256": idn.sha256_fichier(os.path.join(sortie, "fiches-validees.json")),
                                       "consignes_en_attente_sha256": {"argon": "0" * 64}})
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att_f, budgets=budgets, juges_externes=externes)
        att = self.attester(os.path.join(self.tmp, "att.json"), sortie)
        # juges donnés ≠ course → refus ; plafond externe insuffisant → refus AVANT le contrôle (CL35-05), sans manifeste
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-modele", externe)])
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets, juges_externes=externes,
                                      budget_externe_usd=0.5)
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-rapporte.json")))
        self.assertFalse(os.path.exists(os.path.join(sortie, "bras-rapporte-controle")))
        # cas sain : trois juges
        apres = idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets, juges_externes=externes)
        self.assertFalse(apres["sans_bras"])
        self.assertTrue(all(l["nombre_juges"] == 3 and l["nom_agregat"] == "mediane" for l in apres["classement"]))
        o1 = next(l for l in apres["classement"] if l["identifiant_auteur"] == "opus-p1-01")
        self.assertEqual(o1["agregat"]["avantage"], 2)  # notes (2, 2, 0) : médiane 2, pas la moyenne 1,33
        self.assertEqual(o1["par_juge"]["argon"]["avantage"], 0)
        self.assertEqual(sorted(apres["lecture"]["juges_agreges"]), ["argon", "juge-fable", "juge-opus"])
        self.assertEqual(len(apres["lecture"]["accords_de_rang_par_paire"]), 3)
        self.assertTrue(apres["lecture"]["temoins"]["temoins_ok"])
        self.assertTrue(apres["lecture"]["temoins_juge_externe"]["temoins_ok"])
        self.assertTrue(apres["lecture"]["lisible_L2_L4"])
        self.assertIn("argon", apres["lecture"]["auto_preference"])
        self.assertEqual(apres["journal"]["controle"]["argon"]["texte"], "OK")
        self.assertFalse(apres["journal"]["cout_fictif"])
        for nom in ("classement.json", "classements-par-juge.json", "lecture.json", "manifeste-bras-rapporte.json",
                    "notes-bras-rapporte.json"):
            self.assertTrue(os.path.exists(os.path.join(sortie, nom + ".sha256")), nom)
        with open(os.path.join(sortie, "manifeste-bras-rapporte.json")) as f:
            m = json.load(f)["reglages"]
        self.assertEqual(m["commande_externe"][0]["commande"], externe.commande)  # CL35-03
        # rejeu → refus
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets, juges_externes=externes)

    def test_bras_en_panne_classement_sans_bras(self):
        """n° 118 point 3 : Argon en panne → classement à deux juges marqué illisible, manifeste avec l'erreur, code distinct ;
        témoins échoués chez Argon → classement à trois juges illisible."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1"), fiche_brute(nom="O2")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        panne = AdaptateurCommandeExterne(self.commande(
            "import sys, json\nc = sys.stdin.read()\n"
            "if 'exactement OK' in c: print(json.dumps({'texte': 'OK', 'cout_usd': 0.001})); sys.exit(0)\n"
            "print(json.dumps({'texte': 'x', 'cout_usd': 0.2})); sys.exit(3)\n", "panne.py"), environnement={})
        c.lancer(ad, "cp", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "cp")
        att = self.attester(os.path.join(self.tmp, "att-p.json"), sortie)
        with self.assertRaises(idn.SansJugeExterne) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", panne)])
        res = cm.exception.resultat
        self.assertTrue(res["sans_bras"])
        self.assertTrue(all(l["nombre_juges"] == 2 for l in res["classement"]))
        self.assertFalse(res["lecture"]["lisible_L2_L4"])
        self.assertAlmostEqual(res["journal"]["cout_total_usd"], 0.201)  # le coût imprimé avant l'échec est compté
        self.assertTrue(os.path.exists(os.path.join(sortie, "classement-sans-bras.json.sha256")))
        self.assertFalse(os.path.exists(os.path.join(sortie, "classement.json")))
        with open(os.path.join(sortie, "manifeste-bras-rapporte.json")) as f:
            self.assertIn("code 3", json.load(f)["reglages"]["erreur"])
        # témoins échoués chez Argon : trois juges, illisible
        mauvais = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK.replace("'avantage': 1, 'originalite': 0", "'avantage': 3, 'originalite': 3"), "mauvais.py"), environnement={})
        c.lancer(ad, "ct", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "ct")
        att = self.attester(os.path.join(self.tmp, "att-t.json"), sortie)
        apres = idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                          juges_externes=[("argon", "autre-lignee-x", mauvais)])
        self.assertFalse(apres["lecture"]["lisible_L2_L4"])
        self.assertFalse(apres["lecture"]["temoins_juge_externe"]["temoins_ok"])
        self.assertTrue(all(l["nombre_juges"] == 3 for l in apres["classement"]))

    def test_bras_simule_sur_course_reelle_refuse(self):
        """CL35-04 : course marquée réelle (adaptateur du kit, modèles permis) → un adaptateur qui n'est pas une commande
        externe est refusé avant tout écrit ; CL35-03 : la commande est consignée ; CL36-03 : Argon obligatoire."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        ad.nom = "claude-sdk"
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        ext = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK), environnement={})
        with self.assertRaises(idn.CourseInterrompue):  # CL36-03 : course réelle sans Argon proposeur ET juge → refus
            c.lancer(ad, "cr0", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0,
                     moteur="claude-sdk")
        self.assertEqual(ad.appels, [])
        c.lancer(ad, "cr", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=4.0,
                 proposeurs_externes=[("argon-p", "gemini-argon", ext)], moteur="claude-sdk")
        sortie = os.path.join(self.tmp, "cr")
        att = self.attester(os.path.join(self.tmp, "att-r.json"), sortie)
        simule = FauxAdaptateur({}, notes_par_juge={"argon": c.notes_temoins_ok})
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", simule)])
        self.assertEqual(simule.appels, [])
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-rapporte.json")))
        # proposeur externe sans juge externe sur une course réelle : refusé (CL36-03, « juge oublié », n° 118)
        with self.assertRaises(idn.CourseInterrompue) as cm:
            c.lancer(ad, "cr1", budgets=budgets, proposeurs_externes=[("argon-p", "gemini-argon", ext)],
                     budget_externe_usd=4.0, moteur="claude-sdk")
        self.assertIn("obligatoires", str(cm.exception))
        # et un proposeur externe simulé sur une course réelle est refusé aussi (CL35-04), juge externe présent
        with self.assertRaises(idn.CourseInterrompue) as cm:
            c.lancer(ad, "cr2", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")],
                     proposeurs_externes=[("argon-p", "gemini-argon", simule)], budget_externe_usd=4.0, moteur="claude-sdk")
        self.assertIn("CL35-04", str(cm.exception))


    def test_bras_non_joue_relancable(self):
        """CL36-01 : commande introuvable ou clé dans l'environnement → rien envoyé, rien dépensé : manifeste « non joué »
        numéroté, bras relançable ; puis le bras se joue."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        c.lancer(ad, "cn", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "cn")
        att = self.attester(os.path.join(self.tmp, "att-n.json"), sortie)
        introuvable = AdaptateurCommandeExterne(["/chemin/qui/n/existe/pas"], environnement={})
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", introuvable)])
        self.assertIn("non joué", str(cm.exception))
        self.assertTrue(os.path.exists(os.path.join(sortie, "manifeste-bras-non-joue-1.json.sha256")))
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-rapporte.json")))
        cle_env = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK), environnement={"ANTHROPIC_API_KEY": "x"})
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", cle_env)])
        self.assertTrue(os.path.exists(os.path.join(sortie, "manifeste-bras-non-joue-2.json")))
        # attestation complète mais au sceau faux (modifiée après scellement) → refus
        att_f = os.path.join(self.tmp, "att-n-fausse.json")
        self.attester(att_f, sortie)
        with open(att_f, "a") as f:
            f.write("\n")
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att_f, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", introuvable)])
        self.assertIn("sceau", str(cm.exception))  # CL39-12 : le motif est bien le sceau
        self.assertFalse(os.path.exists(os.path.join(sortie, "juges-bras-rapporte", "traces-argon", "reponse.md")))  # M28
        # CL37-02 : contrôle « KO » qui a coûté 0,15 → tentative payée, coût scellé, imputé au plafond externe
        ko = AdaptateurCommandeExterne(self.commande(
            "import sys, json\nc = sys.stdin.read()\nprint(json.dumps({'texte': 'KO', 'cout_usd': 0.15}))\n", "ko.py"),
            environnement={})
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", ko)])
        self.assertIn("0.1500 USD comptés", str(cm.exception))
        self.assertTrue(os.path.exists(os.path.join(sortie, "bras-tentative-3.json.sha256")))
        with open(os.path.join(sortie, "bras-tentative-3.json")) as f:
            self.assertAlmostEqual(json.load(f)["reglages"]["journal"]["cout_total_usd"], 0.15)
        # trois tentatives faites : plus de relance
        bon = AdaptateurCommandeExterne(self.commande(self.SCRIPT_OK), environnement={})
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", bon)])
        self.assertIn("tentatives", str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-rapporte.json")))
        # course neuve : une tentative payée, puis le bras joué avec le coût précédent imputé
        c.lancer(ad, "cn2", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie2 = os.path.join(self.tmp, "cn2")
        att2 = self.attester(os.path.join(self.tmp, "att-n2.json"), sortie2)
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie2, attestation_lecture_humaine=att2, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", ko)])
        apres = idn.executer_bras_differe(sortie2, attestation_lecture_humaine=att2, budgets=budgets,
                                          juges_externes=[("argon", "autre-lignee-x", bon)])
        self.assertFalse(apres["sans_bras"])
        self.assertAlmostEqual(apres["journal"]["cout_tentatives_precedentes_usd"], 0.15)
        self.assertEqual(apres["journal"]["tentative"], 2)
        self.assertTrue(os.path.exists(os.path.join(sortie2, "manifeste-bras-rapporte.json")))


class TestLanceurV37(CasAvecDossier):
    """CL35-07, 08, 09, CL36-03 : le lanceur refuse avec un code, jamais une trace."""

    def lanceur(self):
        import importlib.util
        chemin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demonstrations", "ideation_v2.py")
        spec = importlib.util.spec_from_file_location("ideation_v1_lanceur", chemin)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_options_refusees(self):
        import contextlib
        import io
        lanceur = self.lanceur()
        base = [os.path.join(self.tmp, "s"), "--liste-blanche", "l", "--question", "q", "--temoins", "t"]
        for options in (["--commande-externe", "x"], ["--delai-session-s", "0"], ["--attestation-lecture-humaine", "a"],
                        ["--nombre", "13"], ["--delai-commande-s", "-1"]):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    lanceur.principal(base + options)
            self.assertEqual(cm.exception.code, 2, options)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = lanceur.principal(base + ["--moteur", "claude-sdk"])  # M29 : course réelle sans Argon → refus d'abord
        self.assertEqual(code, 2)
        self.assertIn("obligatoires", err.getvalue())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):  # CL35-08 : non armé → 2, pas une trace
            code = lanceur.principal(base + ["--moteur", "claude-sdk", "--proposeur-externe", "a=x", "--juge-externe", "b=x",
                                             "--commande-externe", "x"])
        self.assertEqual(code, 2)
        self.assertIn("MoteurNonArme", err.getvalue())
        # M31 : --commande-externe avec --juge-externe seul, hors bras → refusé
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                lanceur.principal(base + ["--juge-externe", "b=x", "--commande-externe", "x"])
        # M18, M21, M22, M30 : défauts du devis en vigueur
        a = lanceur.construire_analyseur()
        self.assertEqual(a.get_default("taille_max_pieces"), 750_000)
        self.assertEqual(a.get_default("delai_commande_s"), 1800.0)
        self.assertEqual(a.get_default("budget_externe_usd"), 11.6)
        self.assertEqual(lanceur.BUDGETS_PAR_DEFAUT[("juge_ideation", "claude-opus-5-5")], 4.0)
        from pole.adaptateurs import DELAI_SESSION_S, AdaptateurCommandeExterne
        self.assertEqual(DELAI_SESSION_S, 3600)
        self.assertEqual(AdaptateurCommandeExterne.DELAI_COMMANDE_S, 1800)
        self.assertEqual(lanceur.BUDGETS_PAR_DEFAUT[("proposeur_ideation", "claude-fable-5-1")], 9.3)  # CL36-04, CL37-03

    def test_controle_argon_avant_toute_passe(self):
        """CL36-02 / CL37-01 : avec une commande factice, le proposeur externe est contrôlé avant toute passe, sous son
        rôle, à la taille réelle des pièces, son coût compté ; Argon joue en tête de chaque passe. Une commande qui casse
        sur une grosse consigne arrête avant tout appel Claude de proposition."""
        import contextlib
        import io
        lanceur = self.lanceur()
        cours = TestCourse("test_course_complete")
        cours.tmp = self.tmp
        prep = cours.preparer()
        cmd = TestCommandeExterne("test_commande_factice_notes_et_controle")
        cmd.tmp = self.tmp
        commande = " ".join(cmd.commande(cmd.SCRIPT_OK))
        sortie = os.path.join(self.tmp, "lanceur-ok")
        base = [sortie, "--liste-blanche", prep["liste_blanche"], "--question", prep["question"], "--piece", prep["pieces"][0],
                "--temoins", prep["temoins"], "--proposeur-externe", "argon=gemini-argon", "--juge-externe",
                "argon-j=gemini-argon", "--commande-externe", commande, "--budget-externe-usd", "9"]
        import unittest.mock
        env_propre = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")}
        out = io.StringIO()
        with unittest.mock.patch.dict(os.environ, env_propre, clear=True), contextlib.redirect_stdout(out):
            code = lanceur.principal(base)
        self.assertEqual(code, 0, out.getvalue())
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            depart = json.load(f)["reglages"]
        ctrl = depart["versions"]["appel_de_controle"]["externe:argon"]
        self.assertEqual(ctrl["role"], "proposeur_ideation")
        self.assertGreater(ctrl["taille_consigne"], depart["taille_pieces_servies"]["proposeurs"])
        self.assertAlmostEqual(depart["cout_externe_deja_engage_usd"], 0.001)
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            journal = json.load(f)["reglages"]["journal"]
        self.assertEqual(journal["appels"][0]["etiquette"], "argon")  # CL37-01 : Argon en tête
        self.assertAlmostEqual(journal["cout_externe_usd"], 0.001 + 0.25)
        # commande qui casse au-delà de 100 caractères : refus au contrôle, aucun proposeur Claude appelé
        casse = " ".join(cmd.commande("import sys, json\nc = sys.stdin.read()\n"
                                      "if len(c) > 100: sys.exit(3)\nprint(json.dumps({'texte': 'OK', 'cout_usd': 0.001}))\n",
                                      "casse.py"))
        sortie2 = os.path.join(self.tmp, "lanceur-casse")
        err = io.StringIO()
        with unittest.mock.patch.dict(os.environ, env_propre, clear=True), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(err):
            code = lanceur.principal([sortie2 if x == sortie else x for x in base[:-4]] + ["--commande-externe", casse,
                                                                                            "--budget-externe-usd", "9"])
        self.assertEqual(code, 2)
        self.assertIn("appel de contrôle refusé", err.getvalue())
        self.assertFalse(os.path.exists(os.path.join(sortie2, "manifeste-depart.json")))


class TestV40(CasAvecDossier):
    """v40 (relecture CL6) : sommes externes avec le contrôle du bras, plafonds finis, tentatives de contrôle scellées,
    garde du relais avec la dépense, bras interrompu après envoi verrouillé, interruption qui arrête Argon, refus avant
    les contrôles, contrôle simulé par préfixe."""

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def cmd(self):
        c = TestCommandeExterne("test_commande_factice_notes_et_controle")
        c.tmp = self.tmp
        return c

    def lanceur(self):
        return TestLanceurV37("test_options_refusees").lanceur()

    def test_sommes_et_plafonds_non_finis(self):
        """M12 à M14, M17, M19 : somme externe (contrôle du bras compris) refusée au cœur et par verifier_reglages ;
        totaux et plafonds non finis refusés."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]})
        ext = AdaptateurCommandeExterne(self.cmd().commande(self.cmd().SCRIPT_OK), environnement={})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        ext_args = dict(budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", ext)],
                        juges_externes=[("argon-j", "autre-lignee-x")], seconde_passe=False)
        # cœur : 1,0 + 1,0 + 0,2 (contrôle du bras) = 2,2 > 2,1 refusé ; 2,2 accepté
        with self.assertRaises(idn.CourseInterrompue) as cm:
            c.lancer(ad, "s-ext-refus", budget_externe_usd=2.1, **ext_args)
        self.assertIn("externes", str(cm.exception))
        self.assertEqual(ad.appels, [])
        c.lancer(ad, "s-ext-ok", budget_externe_usd=2.2, **ext_args)
        # verifier_reglages : mêmes sommes (M13, M14), plafonds non finis (M19)
        prep = c._prep
        base = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"], temoins=prep["temoins"],
                    budgets=budgets, proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                    juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")],
                    proposeurs_externes=[("argon", "gemini-argon")], juges_externes=[("argon-j", "autre-lignee-x")])
        idn.verifier_reglages(budget_total_usd=4.0, budget_externe_usd=2.2, **base)
        with self.assertRaises(idn.CourseInterrompue):
            idn.verifier_reglages(budget_total_usd=3.9, budget_externe_usd=2.2, **base)
        with self.assertRaises(idn.CourseInterrompue):
            idn.verifier_reglages(budget_total_usd=4.0, budget_externe_usd=2.1, **base)
        mauvais = dict(budgets); mauvais[("juge_ideation", "claude-opus-5-5")] = float("nan")
        with self.assertRaises(idn.CourseInterrompue):
            idn.verifier_reglages(budget_total_usd=4.0, budget_externe_usd=2.2, **dict(base, budgets=mauvais))
        with self.assertRaises(idn.CourseInterrompue):
            idn.verifier_reglages(budget_total_usd=4.0, budget_externe_usd=2.2, max_tours=3, **base)  # CL39-07
        # cœur : totaux non finis (M17)
        for champ in ("budget_total_usd", "budget_externe_usd", "cout_deja_engage_usd"):
            with self.assertRaises(idn.CourseInterrompue):
                c.lancer(ad, f"nan-{champ}", **{champ: float("nan")})
        with self.assertRaises(idn.CourseInterrompue):
            c.lancer(ad, "nan-session", budgets=mauvais)

    def test_garde_du_relais(self):
        """CL39-03, M15 : plafond − réserve − dépense ≥ total − plus petit juge."""
        lanceur = self.lanceur()
        budgets = {("juge_ideation", "claude-opus-5-5"): 4.0, ("juge_ideation", "claude-fable-5-1"): 7.0}
        juges = [("a", "claude-opus-5-5"), ("b", "claude-fable-5-1")]
        lu = lanceur.verifier_relais({"plafond_usd": 40, "reserve_par_appel_usd": 4, "depense_usd": 0.0}, 40.0, budgets, juges)
        self.assertEqual(lu["depense_usd"], 0.0)
        with self.assertRaises(idn.CourseInterrompue):  # réserve 10 : 30 < 36
            lanceur.verifier_relais({"plafond_usd": 40, "reserve_par_appel_usd": 10}, 40.0, budgets, juges)
        with self.assertRaises(idn.CourseInterrompue):  # relance après 0,4 dépensés : 35,6 < 36
            lanceur.verifier_relais({"plafond_usd": 40, "reserve_par_appel_usd": 4, "depense_usd": 0.4}, 40.0, budgets, juges)
        lanceur.verifier_relais({}, 40.0, budgets, juges)  # relais muet sur ses plafonds : rien à vérifier

    def test_tentatives_de_controle_scellees(self):
        """CL39-02, CL39-07, CL39-08, M16 : un contrôle refusé est scellé avec son coût dans SORTIE-controle, imputé à la
        relance, borné à trois ; un refus de réglage ou une SORTIE existante tombent avant tout contrôle ; la répétition
        simulée avec un proposeur externe sans commande passe."""
        import contextlib
        import io
        import unittest.mock
        lanceur = self.lanceur()
        c = self.cours()
        prep = c.preparer()
        cmd = self.cmd()
        casse = " ".join(cmd.commande("import sys, json\nc = sys.stdin.read()\nprint(json.dumps({'texte': 'KO', 'cout_usd': 0.15}))\n",
                                      "casse.py"))
        sortie = os.path.join(self.tmp, "l-tent")
        env_propre = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")}
        base = [sortie, "--liste-blanche", prep["liste_blanche"], "--question", prep["question"], "--piece", prep["pieces"][0],
                "--temoins", prep["temoins"], "--proposeur-externe", "argon=gemini-argon", "--juge-externe",
                "argon-j=gemini-argon", "--budget-externe-usd", "11.2"]
        with unittest.mock.patch.dict(os.environ, env_propre, clear=True), contextlib.redirect_stderr(io.StringIO()):
            for n in (1, 2, 3):
                code = lanceur.principal(base + ["--commande-externe", casse])
                self.assertEqual(code, 2)
                chemin = os.path.join(sortie + "-controle", f"tentative-{n}.json")
                self.assertTrue(os.path.exists(chemin + ".sha256"), n)
                with open(chemin) as f:
                    r = json.load(f)["reglages"]
                self.assertAlmostEqual(r["cout_externe_usd"], 0.15)
                self.assertEqual(r["relancable"], n < 3)
            self.assertFalse(os.path.exists(sortie))
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(lanceur.principal(base + ["--commande-externe", casse]), 2)
            self.assertIn("tentatives", err.getvalue())
            self.assertFalse(os.path.exists(os.path.join(sortie + "-controle", "tentative-4.json")))
        # M16 / CL39-07 : réglage refusé AVANT tout contrôle (aucun dossier de contrôle, commande jamais appelée)
        sortie2 = os.path.join(self.tmp, "l-regl")
        with unittest.mock.patch.dict(os.environ, env_propre, clear=True), contextlib.redirect_stderr(io.StringIO()):
            code = lanceur.principal([sortie2 if x == sortie else x for x in base] + ["--commande-externe", casse,
                                                                                         "--taille-max-pieces", "5"])
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(sortie2 + "-controle"))
        os.makedirs(sortie2)
        with unittest.mock.patch.dict(os.environ, env_propre, clear=True), contextlib.redirect_stderr(io.StringIO()):
            code = lanceur.principal([sortie2 if x == sortie else x for x in base] + ["--commande-externe", casse])
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(sortie2 + "-controle"))
        # CL39-08 : répétition simulée avec proposeur externe, sans commande
        sortie3 = os.path.join(self.tmp, "l-sim")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = lanceur.principal([sortie3 if x == sortie else x for x in base])
        self.assertEqual(code, 0, out.getvalue())

    def test_bras_interrompu_apres_envoi_verrouille(self):
        """CL39-04 : une exception pendant la session du juge du bras, après envoi, compte le plafond et verrouille."""
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        c.lancer(ad, "ci", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "ci")
        cmd = self.cmd()
        att = cmd.attester(os.path.join(self.tmp, "att-ci.json"), sortie)

        class Coupe:
            nom = "commande-externe"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
                    return Resultat("OK", [], 0.001, "ok")
                raise RuntimeError("coupé pendant la session")

            def description(self):
                return {"commande": ["coupe"]}
        with self.assertRaises(RuntimeError):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", Coupe())])
        chemin = os.path.join(sortie, "manifeste-bras-rapporte.json")
        self.assertTrue(os.path.exists(chemin))
        with open(chemin) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertAlmostEqual(j["cout_total_usd"], 1.001)  # contrôle 0,001 + plafond 1,0 de la session interrompue
        self.assertEqual(j["consigne_envoyee"], "argon")
        self.assertFalse(any(f.startswith("bras-tentative") or f.startswith("manifeste-bras-non-joue") for f in os.listdir(sortie)))
        bon = self.cmd()
        from pole.adaptateurs import AdaptateurCommandeExterne
        with self.assertRaises(idn.CourseInterrompue):  # verrouillé
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x",
                                                       AdaptateurCommandeExterne(bon.commande(bon.SCRIPT_OK), environnement={}))])

    def test_tentative_payee_imputee_et_non_lance(self):
        """M07, M09 : « rien envoyé » exige « aucun processus parti » ; le coût d'une tentative payée réduit le plafond."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        c.lancer(ad, "cp9", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=1.3)
        sortie = os.path.join(self.tmp, "cp9")
        cmd = self.cmd()
        att = cmd.attester(os.path.join(self.tmp, "att-cp9.json"), sortie)
        ko = AdaptateurCommandeExterne(cmd.commande("import sys, json\nsys.stdin.read()\nprint(json.dumps({'texte': 'KO', 'cout_usd': 0.15}))\n", "ko9.py"),
                                       environnement={})
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", ko)])
        self.assertNotIn("non joué", str(cm.exception))  # M07 : un processus est parti → tentative payée, pas « non joué »
        self.assertTrue(os.path.exists(os.path.join(sortie, "bras-tentative-1.json")))
        bon = AdaptateurCommandeExterne(cmd.commande(cmd.SCRIPT_OK), environnement={})
        with self.assertRaises(idn.CourseInterrompue) as cm:  # M09 : 0,15 + 0,2 + 1,0 > 1,3 → plafond externe insuffisant
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", bon)])
        self.assertIn("plafond externe", str(cm.exception))

    def test_interruption_arrete_le_groupe_et_compte(self):
        """CL37-07, CL39-05, M20 : une interruption pendant la commande arrête tout son groupe ; la session interrompue
        est comptée au plafond par la course et le manifeste de fin est écrit."""
        import subprocess
        import unittest.mock
        from pole.adaptateurs import AdaptateurCommandeExterne
        cmd = self.cmd()
        ad = AdaptateurCommandeExterne(cmd.commande("import sys, time\nsys.stdin.read()\ntime.sleep(30)\n", "lent.py"), environnement={})
        tues = []
        vrai_communicate = subprocess.Popen.communicate

        lances = []

        def communicate_coupe(self_p, *a, **k):
            if not getattr(self_p, "_deja", False):
                self_p._deja = True
                lances.append(self_p)
                raise KeyboardInterrupt()
            return vrai_communicate(self_p, *a, **k)
        with unittest.mock.patch.object(subprocess.Popen, "communicate", communicate_coupe), \
                unittest.mock.patch("os.killpg", side_effect=lambda pid, sig: tues.append((pid, sig))):
            with self.assertRaises(KeyboardInterrupt):
                ad.lancer("juge_ideation", "consigne", self.tmp, 1.0, 1)
        self.assertEqual(len(tues), 1)  # M20 : le groupe est visé
        for p in lances:  # v41 : `os.killpg` était simulé — la commande lente est arrêtée ici (aucun processus survivant)
            p.kill()
            p.communicate()
        # la course compte la session interrompue au plafond et écrit le manifeste de fin
        c = self.cours()

        class Interrompt(FauxAdaptateur):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                raise KeyboardInterrupt()
        ad2 = Interrompt({"opus": [fiche_brute()], "fable": [fiche_brute()]})
        with self.assertRaises(KeyboardInterrupt):
            c.lancer(ad2, "c-int")
        with open(os.path.join(self.tmp, "c-int", "manifeste-fin.json")) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertEqual(j["appels"][0]["statut"], "interrompue")
        self.assertAlmostEqual(j["cout_total_usd"], 1.0)  # plafond de la session compté
        self.assertIn("taille_consigne", j["appels"][0])


    def test_sigterm_sur_le_lanceur(self):
        """CL39-05 : SIGTERM à l'orchestrateur pendant la session d'Argon → code 2, manifeste de fin écrit avec la session
        comptée au plafond, commande et petit-enfant arrêtés."""
        import signal
        import subprocess
        import time
        c = self.cours()
        prep = c.preparer()
        cmd = self.cmd()
        pid_f = os.path.join(self.tmp, "pe.pid")
        lent = " ".join(cmd.commande(
            "import sys, json, subprocess, time\nc = sys.stdin.read()\n"
            "if 'exactement OK' in c: print(json.dumps({'texte': 'OK', 'cout_usd': 0.001})); sys.exit(0)\n"
            f"p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); open({pid_f!r}, 'w').write(str(p.pid))\n"
            "time.sleep(60)\n", "lent2.py"))
        sortie = os.path.join(self.tmp, "l-term")
        lanceur = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demonstrations", "ideation_v2.py")
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")}
        p = subprocess.Popen([sys.executable, "-I", "-B", lanceur, sortie, "--liste-blanche", prep["liste_blanche"], "--question",
                              prep["question"], "--piece", prep["pieces"][0], "--temoins", prep["temoins"], "--proposeur-externe",
                              "argon=gemini-argon", "--juge-externe", "argon-j=gemini-argon", "--commande-externe", lent,
                              "--budget-externe-usd", "11.2"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(100):
            if os.path.exists(pid_f):
                break
            time.sleep(0.1)
        else:
            p.kill()
            self.fail("la commande lente n'a pas démarré")
        p.send_signal(signal.SIGTERM)
        out, err = p.communicate(timeout=30)
        self.assertEqual(p.returncode, 2, err.decode("utf-8", "replace"))
        self.assertIn("interruption", err.decode("utf-8", "replace"))
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertEqual(j["appels"][-1]["statut"], "interrompue")
        pe = int(open(pid_f).read())
        for _ in range(30):
            try:
                with open(f"/proc/{pe}/status") as f:
                    if any(l.startswith("State:") and "Z" in l for l in f):
                        break
            except OSError:
                break
            time.sleep(0.1)
        else:
            os.kill(pe, 9)
            self.fail("le petit-enfant d'Argon a survécu au SIGTERM")


def _lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return f.read()


class TestV41(CasAvecDossier):
    """v41 (relecture CL7 de la v40) : contrôle interrompu compté au plafond (CL40-02), même contrôle du bras au lanceur
    et au cœur et refus du cœur scellé (CL40-03), contrôle à la taille réelle et passe 2 d'Argon juste après sa passe 1
    (CL40-04), `relancable` calculé et contrôle Claude payé (CL40-01, code), deux tolérances, valeurs non finies du
    chemin de l'argent (CL40-05), classement sans bras après envoi (CL40-08), M07 (CL40-07), écrits (CL40-09)."""

    ENV = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def cmd(self):
        c = TestCommandeExterne("test_commande_factice_notes_et_controle")
        c.tmp = self.tmp
        return c

    def lanceur(self, cout_controle_claude=None, ko_claude=None):
        """Lanceur chargé à neuf ; avec `cout_controle_claude`, le contrôle Claude simulé rend ce coût (moteur simulé payé) ;
        v42 : `ko_claude` (un modèle) rend « KO » au contrôle, à ce même coût."""
        lanceur = TestLanceurV37("test_options_refusees").lanceur()
        if cout_controle_claude is not None:
            original = lanceur.AdaptateurIdeationSimule.lancer

            def lancer(s, role, consigne, dossier, budget_usd, max_tours, modele=None):
                if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
                    return Resultat("KO" if modele == ko_claude else "OK", [], cout_controle_claude, "ok")
                return original(s, role, consigne, dossier, budget_usd, max_tours, modele)
            lanceur.AdaptateurIdeationSimule.lancer = lancer
        return lanceur

    def env_propre(self):
        return {k: v for k, v in os.environ.items() if k in self.ENV}

    def principal(self, lanceur, argv):
        """Appelle le lanceur dans un environnement sans variable de clé ; rend (code, sortie, erreur)."""
        import contextlib
        import io
        import unittest.mock
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, self.env_propre(), clear=True), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = lanceur.principal(argv)
        return code, out.getvalue(), err.getvalue()

    def prep_devis(self):
        """Pièces des essais, matériau attesté : réglages du devis v7 quinquies (seconde passe, Argon proposeur et juge)."""
        prep = self.cours().preparer()
        att = os.path.join(self.tmp, "att-materiau.json")
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-29", "materiau_sha256": {
            os.path.basename(prep["materiau"][0]): idn.sha256_fichier(prep["materiau"][0])}})
        return prep, att

    def base(self, sortie, prep, att=None, *options):
        b = [sortie, "--liste-blanche", prep["liste_blanche"], "--question", prep["question"], "--piece", prep["pieces"][0],
             "--temoins", prep["temoins"], "--proposeur-externe", "argon=gemini-argon", "--juge-externe", "argon-j=gemini-argon"]
        if att:
            b += ["--materiau", prep["materiau"][0], "--seconde-passe", "--attestation-materiau", att]
        return b + list(options)

    def script(self, corps, nom):
        return " ".join(self.cmd().commande(corps, nom))

    SCRIPT_PLAFOND = (  # Argon au pire cas : chaque appel rend son plafond de session ; v49 : et le modèle servi (celui qu'on lui demande)
        "import sys, json, os\nc = sys.stdin.read()\ncout = float(os.environ['PLAFOND_SESSION_USD'])\n"
        "if c.startswith('Réponds exactement OK'): print(json.dumps({'texte': 'OK', 'cout_usd': cout, 'modele_servi': os.environ.get('MODELE_DEMANDE_POLE')})); sys.exit(0)\n"
        "if os.environ['ROLE_POLE'] == 'juge_ideation':\n"
        "    import re\n"
        "    bloc = json.loads(re.search(r'```json\\n(\\[.*\\])\\n```', c, re.S).group(1)); par_nom = {f['nom']: f['identifiant'] for f in bloc}\n"
        "    notes = []\n"
        "    for f in bloc:\n"
        "        k = {x: 2 for x in ('avantage', 'originalite', 'falsifiabilite', 'traitabilite', 'robustesse')}\n"
        "        if f['nom'] in ('Verbeux vide', 'Assuré occupé'): k.update({'avantage': 1, 'originalite': 0, 'falsifiabilite': 0})\n"
        "        notes.append({'identifiant': f['identifiant'], 'criteres': k, 'justifications': {}})\n"
        "    d = [[par_nom['Jumeau'], par_nom['Sobre fort']]]\n"
        "    print(json.dumps({'texte': '```json\\n' + json.dumps({'notes': notes, 'doublons': d}) + '\\n```', 'cout_usd': cout, 'modele_servi': os.environ.get('MODELE_DEMANDE_POLE')})); sys.exit(0)\n"
        "f1 = json.loads(%r); f2 = dict(f1, nom='Argon B')\n"
        "if 'première passe' in c: f1['nom'] = 'Argon A revue'; f2['nom'] = 'Argon B revue'\n"
        "print(json.dumps({'texte': '```json\\n' + json.dumps({'fiches': [f1, f2]}, ensure_ascii=False) + '\\n```', "
        "'cout_usd': cout, 'modele_servi': os.environ.get('MODELE_DEMANDE_POLE')}))\n") % json.dumps(fiche_brute(nom="Argon A"), ensure_ascii=False)

    # --- CL40-02 ---------------------------------------------------------------------------------------------------------

    def test_controle_interrompu_compte_le_plafond_et_garde_les_lectures(self):
        """CL40-02 : une exception au contrôle du second modèle compte son plafond et garde la lecture (et le coût) du
        premier ; une interruption remonte telle quelle, lectures jointes ; une clé dans l'environnement (rien lancé) compte 0."""
        from pole.relais import CleDansEnvironnement

        class Panne:
            nom = "panne"

            def __init__(self, exc):
                self.exc = exc

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                if modele == "claude-opus-5-5":
                    raise self.exc
                return Resultat("OK", [], 0.01, "ok")
        sortie = os.path.join(self.tmp, "ctrl-int")
        modeles = ["claude-fable-5-1", "claude-opus-5-5"]
        with self.assertRaises(idn.ControleRefuse) as cm:
            idn.appel_de_controle(Panne(RuntimeError("panne de l'adaptateur")), modeles, sortie, 0.2)
        lec = cm.exception.lecture
        self.assertAlmostEqual(lec["claude-fable-5-1"]["cout_compte_usd"], 0.01)  # premier modèle : payé, gardé
        self.assertEqual(lec["claude-opus-5-5"]["statut"], "interrompue")
        self.assertAlmostEqual(idn.cout_compte_controle(lec["claude-opus-5-5"]), 0.2)  # plafond, jamais 0
        self.assertTrue(lec["claude-opus-5-5"]["cout_inconnu"])
        self.assertAlmostEqual(sum(idn.cout_compte_controle(c) for c in lec.values()), 0.21)
        with self.assertRaises(KeyboardInterrupt) as cm2:
            idn.appel_de_controle(Panne(KeyboardInterrupt("signal 15")), modeles, sortie, 0.2)
        self.assertAlmostEqual(sum(idn.cout_compte_controle(c) for c in cm2.exception.lecture.values()), 0.21)
        with self.assertRaises(CleDansEnvironnement) as cm3:  # levée avant tout lancement : rien compté
            idn.appel_de_controle(Panne(CleDansEnvironnement("clé")), modeles, sortie, 0.2)
        self.assertEqual(idn.cout_compte_controle(cm3.exception.lecture["claude-opus-5-5"]), 0.0)
        self.assertTrue(cm3.exception.lecture["claude-opus-5-5"]["non_lance"])
        # cas sain inchangé
        self.assertEqual(idn.appel_de_controle(Panne(None), ["claude-fable-5-1"], sortie, 0.2)["claude-fable-5-1"]["problemes"], [])

    def _attendre_pids(self, pid_f, p):
        import time
        for _ in range(150):
            if os.path.exists(pid_f) and _lire(pid_f).strip():
                return
            time.sleep(0.1)
        p.kill()
        p.communicate()
        self.fail("la commande lente n'a pas démarré")

    def _morts(self, pids):
        import time
        for pe in pids:
            for _ in range(50):
                try:
                    with open(f"/proc/{pe}/status") as f:
                        if any(l.startswith("State:") and "Z" in l for l in f):
                            break
                except OSError:
                    break
                time.sleep(0.1)
            else:
                os.kill(pe, 9)
                self.fail(f"processus {pe} survivant au SIGTERM")

    SCRIPT_LENT_CONTROLE = (
        "import sys, json, os, subprocess, time\nc = sys.stdin.read()\n"
        "if c.startswith('Réponds exactement OK'):\n"
        "    p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        "    open(%r, 'w').write(str(os.getpid()) + ' ' + str(p.pid)); time.sleep(60)\n"
        "print(json.dumps({'texte': 'x', 'cout_usd': 0.1}))\n")

    def test_sigterm_pendant_le_controle_de_la_course(self):
        """CL40-02 (S3) : SIGTERM pendant le contrôle d'Argon dans la course → code 2, tentative scellée au plafond de la
        session de contrôle (2,5 chez Argon), message vrai, commande et petit-enfant arrêtés."""
        import signal
        import subprocess
        prep = self.cours().preparer()
        pid_f = os.path.join(self.tmp, "ctrl.pid")
        lent = self.script(self.SCRIPT_LENT_CONTROLE % pid_f, "lent-ctrl.py")
        sortie = os.path.join(self.tmp, "l-sig-ctrl")
        chemin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demonstrations", "ideation_v2.py")
        p = subprocess.Popen([sys.executable, "-I", "-B", chemin] + self.base(sortie, prep) + ["--commande-externe", lent],
                             env=self.env_propre(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._attendre_pids(pid_f, p)
        p.send_signal(signal.SIGTERM)
        _, err = p.communicate(timeout=30)
        err = err.decode("utf-8", "replace")
        self.assertEqual(p.returncode, 2, err)
        self.assertIn("contrôle compris", err)
        with open(os.path.join(sortie + "-controle", "tentative-1.json")) as f:
            r = json.load(f)["reglages"]
        self.assertTrue(idn.verifier_scelle(os.path.join(sortie + "-controle", "tentative-1.json")))
        self.assertAlmostEqual(r["cout_externe_usd"], 2.5)  # v40 : 0,0
        self.assertEqual(r["lectures"]["externe:argon"]["statut"], "interrompue")
        self.assertIn("tentative_scellee", err)
        self._morts([int(x) for x in _lire(pid_f).split()])

    def test_sigterm_pendant_le_controle_du_bras(self):
        """CL40-02 (S3b) : SIGTERM pendant le contrôle du bras → code 2, bras-tentative scellée au plafond du contrôle
        (0,2), `relancable` calculé, commande et petit-enfant arrêtés."""
        import signal
        import subprocess
        prep = self.cours().preparer()
        sortie = os.path.join(self.tmp, "l-bras-sig")
        code, out, err = self.principal(self.lanceur(), self.base(sortie, prep) + ["--commande-externe",
                                                                                   " ".join(self.cmd().commande(self.cmd().SCRIPT_OK))])
        self.assertEqual(code, 0, out + err)
        att = self.cmd().attester(os.path.join(self.tmp, "att-bras-sig.json"), sortie, "argon-j")
        pid_f = os.path.join(self.tmp, "bras.pid")
        lent = self.script(self.SCRIPT_LENT_CONTROLE % pid_f, "lent-bras.py")
        chemin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demonstrations", "ideation_v2.py")
        p = subprocess.Popen([sys.executable, "-I", "-B", chemin, sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine",
                              att, "--juge-externe", "argon-j=gemini-argon", "--commande-externe", lent],
                             env=self.env_propre(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._attendre_pids(pid_f, p)
        p.send_signal(signal.SIGTERM)
        _, err = p.communicate(timeout=30)
        err = err.decode("utf-8", "replace")
        self.assertEqual(p.returncode, 2, err)
        self.assertIn("interruption", err)
        chemin_t = os.path.join(sortie, "bras-tentative-1.json")
        self.assertTrue(idn.verifier_scelle(chemin_t))
        with open(chemin_t) as f:
            r = json.load(f)["reglages"]
        self.assertAlmostEqual(r["journal"]["cout_total_usd"], 0.2)  # v40 : 0,0
        self.assertTrue(r["relancable"])  # 11,6 ≥ course + 0,2 + 3,5 + 0,2 : relance calculée possible
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-rapporte.json")))
        self._morts([int(x) for x in _lire(pid_f).split()])

    # --- CL40-03 ---------------------------------------------------------------------------------------------------------

    def test_s9_meme_controle_du_bras_et_refus_du_coeur_scelle(self):
        """CL40-03 (S9) : `--budget-controle-usd 0.1 --budget-externe-usd 11.1`, Argon au pire cas, seconde passe : le
        lanceur et le cœur comptent le même contrôle du bras (0,1) → la course part. Un refus du cœur après des contrôles
        payés (contrôle Claude rendu « ok » au-dessus de son plafond) écrit une tentative scellée avec les coûts, relance
        calculée impossible et refusée avant tout contrôle."""
        prep, att = self.prep_devis()
        argon = self.script(self.SCRIPT_PLAFOND, "argon-plafond.py")
        sortie = os.path.join(self.tmp, "l-s9")
        code, out, err = self.principal(self.lanceur(), self.base(sortie, prep, att, "--commande-externe", argon,
                                                                   "--budget-controle-usd", "0.1", "--budget-externe-usd", "11.1"))
        self.assertIn(code, (0, 4), err)  # v40 : 2, « somme des plafonds externes 11.20 > total externe 11.1 »
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            sommes = json.load(f)["reglages"]["somme_des_plafonds"]
        self.assertAlmostEqual(sommes["budget_controle_bras_usd"], 0.1)
        self.assertAlmostEqual(sommes["externe_avec_controle_du_bras"], 11.1)  # 2,5 + 2 × 2,5 + 3,5 + 0,1
        self.assertFalse(os.path.exists(os.path.join(sortie + "-controle", "tentative-1.json")))
        # le bras, lancé sans répéter l'option, joue le contrôle que la course a compté (0,1) : Argon 7,5 + 0,1 + 3,5 = 11,1
        att_b = self.cmd().attester(os.path.join(self.tmp, "att-s9.json"), sortie, "argon-j")
        code, out, err = self.principal(self.lanceur(), [sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine", att_b,
                                                         "--juge-externe", "argon-j=gemini-argon", "--commande-externe", argon])
        self.assertIn(code, (0, 4), err)  # avant : refus « 7,5 + 3,7 > 11,1 » (contrôle du bras repris à 0,2)
        with open(os.path.join(sortie, "manifeste-bras-rapporte.json")) as f:
            jb = json.load(f)["reglages"]["journal"]
        self.assertAlmostEqual(jb["controle"]["argon-j"]["cout_compte_usd"], 0.1)
        self.assertAlmostEqual(jb["cout_externe_deja_compte_course_usd"] + jb["cout_total_usd"], 11.1)
        # refus du cœur après les contrôles payés (SUPPOSÉ : un contrôle « ok » au-dessus de son plafond, 0,5 > 0,2)
        sortie2 = os.path.join(self.tmp, "l-coeur")
        args2 = self.base(sortie2, prep, att, "--commande-externe", argon)
        code, out, err = self.principal(self.lanceur(cout_controle_claude=0.5), args2)
        self.assertEqual(code, 2)
        self.assertIn("somme des plafonds Claude", err)
        self.assertFalse(os.path.exists(sortie2))
        chemin_t = os.path.join(sortie2 + "-controle", "tentative-1.json")
        self.assertTrue(idn.verifier_scelle(chemin_t))  # v40 : aucune trace
        with open(chemin_t) as f:
            r = json.load(f)["reglages"]
        self.assertAlmostEqual(r["cout_claude_usd"], 1.0)
        self.assertAlmostEqual(r["cout_externe_usd"], 2.5)
        self.assertFalse(r["relancable"])
        code, out, err = self.principal(self.lanceur(cout_controle_claude=0.5), args2)  # relance : refus avant tout contrôle
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(os.path.join(sortie2 + "-controle", "tentative-2.json")))
        self.assertFalse(os.path.exists(os.path.join(sortie2 + "-controle", "tentative-2")))

    # --- CL40-04 ---------------------------------------------------------------------------------------------------------

    def test_controle_a_la_taille_reelle_de_la_passe_2_et_ordre_d_argon(self):
        """CL40-04 (S5) : le contrôle d'Argon porte sa consigne de passe 2 au maximum (fiches à la taille maximale champ par
        champ × nombre, matériau) ; une passe 2 réelle à champs de 3 000 caractères n'est pas plus grosse que le contrôle ;
        sans matériau la seconde passe compte aussi ses fiches ; Argon joue sa passe 2 juste après sa passe 1, avant toute
        passe Claude. **Changé en v43** (CL42-04, décision de Lazar : « retirer » la borne de fiche) : retour aux assertions de
        la v41 — fiche maximale de plus de 13 × 3 000 caractères, grosse fiche d'Argon à quatre champs de 3 000 (v42 : 12 000
        et trois champs)."""
        c = self.cours()
        prep = c.preparer()
        c._prep = prep
        att = os.path.join(self.tmp, "att-m.json")
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-29", "materiau_sha256": {
            os.path.basename(prep["materiau"][0]): idn.sha256_fichier(prep["materiau"][0])}})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        args = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"], temoins=prep["temoins"],
                    budgets=budgets, proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                    juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")],
                    proposeurs_externes=[("argon", "gemini-argon")], budget_total_usd=20.0, budget_externe_usd=5.0,
                    nombre_par_proposeur=8)
        taille_fiche = len(json.dumps([idn.fiche_maximale()], ensure_ascii=False, indent=1))
        self.assertGreater(taille_fiche, 13 * idn.LONGUEUR_MAX_CHAMP)  # v43 (CL42-04) : comme la v41 (v42 : 12 000)
        v2 = idn.verifier_reglages(materiau=prep["materiau"], seconde_passe=True, attestation_materiau=att, **args)
        self.assertGreater(len(v2["texte_controle_externe"]), 8 * taille_fiche)  # v40 : 8 × 4 000
        self.assertIn("Tour interne", v2["texte_controle_externe"])
        v2b = idn.verifier_reglages(seconde_passe=True, **args)  # sans matériau : les fiches de passe 1 comptent
        self.assertGreater(len(v2b["texte_controle_externe"]), 8 * taille_fiche)
        v1 = idn.verifier_reglages(**args)
        self.assertLess(len(v1["texte_controle_externe"]), taille_fiche)
        # une passe 2 réelle aux champs de 3 000 caractères (8 fiches) n'est pas plus grosse que la consigne de contrôle
        # (v43 : quatre champs de 3 000, comme la v41 ; v42 : trois, sous la borne de 12 000 retirée)
        controle = idn.consigne_de_controle(v2["texte_controle_externe"])
        grosse = fiche_brute(nom="Argon gros")
        for k in ("enonce", "perte_traduction", "piege", "cosmetique_si"):
            grosse[k] = "y" * idn.LONGUEUR_MAX_CHAMP
        ordre = []

        class Argon:
            nom = "argon-simule"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                ordre.append(("argon", os.path.basename(dossier), len(consigne)))
                fiches = [dict(grosse, nom=f"Argon {i}") for i in range(8)]
                return Resultat("```json\n" + json.dumps({"fiches": fiches}, ensure_ascii=False) + "\n```", [], 0.1, "ok")
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        orig = ad.lancer

        def lancer_note(role, consigne, dossier, budget_usd, max_tours, modele=None):
            if role == "proposeur_ideation":
                ordre.append(("claude", os.path.basename(dossier), len(consigne)))
            return orig(role, consigne, dossier, budget_usd, max_tours, modele)
        ad.lancer = lancer_note
        res = c.lancer(ad, "c-ordre", budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", Argon())],
                       budget_externe_usd=5.0, seconde_passe=True, attestation_materiau=att)
        self.assertEqual([(q, d) for q, d, _ in ordre][:2], [("argon", "passe-1"), ("argon", "passe-2")])  # v40 : Claude avant
        self.assertEqual([(q, d) for q, d, _ in ordre][2:], [("claude", "passe-1")] * 2 + [("claude", "passe-2")] * 2)
        self.assertLessEqual(ordre[1][2], len(controle))  # la passe 2 réelle tient dans la taille éprouvée
        # ordre des fiches écrites inchangé : passe 1 (Argon, opus, fable) puis passe 2
        self.assertEqual([f["passe"] for f in res["fiches"]], [1] * 10 + [2] * 10)
        self.assertEqual(res["fiches"][0]["auteur"], "argon")

    def test_controle_du_bras_porte_la_consigne_du_juge(self):
        """CL40-04 (S6), **inversé en v42** (CL41-01, option B de session-depot) : le contrôle du bras redevient court (41
        caractères, aucune fiche) ; la consigne du juge n'est envoyée qu'à la session du juge, telle quelle."""
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        c.lancer(ad, "cb", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "cb")
        att = self.cmd().attester(os.path.join(self.tmp, "att-cb.json"), sortie)
        with open(os.path.join(sortie, "juges-bras-rapporte", "traces-argon", "consigne-en-attente.md"), encoding="utf-8") as f:
            consigne_juge = f.read()
        recu = []

        class Enregistre:
            nom = "commande-externe"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                recu.append(consigne)
                if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
                    return Resultat("OK", [], 0.01, "ok")
                return Resultat("```json\n" + json.dumps(c.notes_temoins_ok(
                    sorted(set(re.findall(r'"identifiant": "(T\d\d)"', consigne))), consigne)) + "\n```", [], 0.3, "ok")

            def description(self):
                return {"commande": ["enregistre"]}
        apres = idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                          juges_externes=[("argon", "autre-lignee-x", Enregistre())])
        self.assertEqual(recu[0], idn.APPEL_DE_CONTROLE_CONSIGNE)  # v41 : la consigne du juge entière
        self.assertNotIn(consigne_juge, recu[0])
        self.assertEqual(apres["journal"]["controle"]["argon"]["taille_consigne"], len(idn.APPEL_DE_CONTROLE_CONSIGNE))
        self.assertEqual(recu[1], consigne_juge)
        self.assertFalse(apres["sans_bras"])

    # --- CL40-01 (code) : relance calculée, contrôle Claude payé ; tolérances ------------------------------------------

    SCRIPT_KO = "import sys, json\nc = sys.stdin.read()\nopen(%r, 'a').write('appel\\n')\nprint(json.dumps({'texte': 'KO', 'cout_usd': 0.15}))\n"
    SCRIPT_CTRL_OK = "import sys, json\nc = sys.stdin.read()\nopen(%r, 'a').write('appel\\n')\nprint(json.dumps({'texte': 'OK', 'cout_usd': 0.15}))\n"

    def test_relancable_calcule_avec_un_controle_claude_paye(self):
        """CL40-01 (code), point 6 : contrôle Claude payé (0,01 puis 0,2 par modèle), réglages du devis v7 quinquies (somme
        Claude 40,0 exactement), Argon « OK » à 0,15, le second contrôle Claude « KO » (payé). **Changé en v43** (CL40-01,
        option c, décision de Lazar : les contrôles réussis ne sont pas rejoués) : la somme de la relance compte les coûts
        imputés et le seul contrôle à refaire — 0,02 + 0,2 + 39,6 = 39,82 ≤ 40, relançable, et la relance ne rejoue que le
        contrôle « KO » (Argon et le premier contrôle Claude repris) ; à 0,2 : 0,4 + 0,2 + 39,6 = 40,2 > 40, non relançable,
        relance refusée avant tout contrôle. Total relevé à 41 : trois tentatives au plus, Argon appelé une seule fois.
        (v42 : relance 40,02 et 40,4, non relançable ; la relance à 41 rejouait tous les contrôles, Argon trois fois.)"""
        prep, att = self.prep_devis()
        for cout, somme, relancable in ((0.01, "39.8200", True), (0.2, "40.2000", False)):
            journal = os.path.join(self.tmp, f"ko-{cout}.log")
            ko = self.script(self.SCRIPT_CTRL_OK % journal, f"ko-{cout}.py")
            sortie = os.path.join(self.tmp, f"l-paye-{cout}")
            argv = self.base(sortie, prep, att, "--commande-externe", ko)
            code, out, err = self.principal(self.lanceur(cout_controle_claude=cout, ko_claude="claude-opus-5-5"), argv)
            self.assertEqual(code, 2)
            chemin = os.path.join(sortie + "-controle", "tentative-1.json")
            self.assertTrue(idn.verifier_scelle(chemin))
            with open(chemin) as f:
                r = json.load(f)["reglages"]
            self.assertAlmostEqual(r["cout_claude_usd"], 2 * cout)
            self.assertAlmostEqual(r["cout_externe_usd"], 0.15)
            self.assertEqual(r["relancable"], relancable, r["motifs_relance"])
            self.assertEqual(r["controles_a_refaire"], ["claude-opus-5-5"])
            self.assertAlmostEqual(r["sommes_de_la_relance_hors_cette_tentative"]["claude"], 39.8)
            if not relancable:
                self.assertTrue(any(somme in m for m in r["motifs_relance"]), r["motifs_relance"])
                self.assertIn('"relancable": false', err)
            self.assertNotIn("trois tentatives", err)
            n = len(_lire(journal).splitlines())
            code, out, err = self.principal(self.lanceur(cout_controle_claude=cout, ko_claude="claude-opus-5-5"), argv)
            self.assertEqual(code, 2)
            self.assertEqual(len(_lire(journal).splitlines()), n)  # Argon jamais rappelé (refus, ou contrôle repris)
            if relancable:  # la relance ne rejoue que le contrôle « KO »
                with open(os.path.join(sortie + "-controle", "tentative-2.json")) as f:
                    r2 = json.load(f)["reglages"]
                self.assertEqual(sorted(r2["lectures"]), ["claude-opus-5-5"])
                self.assertEqual(sorted(r2["controles_repris"]), ["claude-fable-5-1", "externe:argon"])
                self.assertEqual({v["repris_de_tentative"] for v in r2["controles_repris"].values()}, {1})
                self.assertAlmostEqual(r2["cout_claude_usd"], cout)
                self.assertEqual(r2["cout_externe_usd"], 0.0)
            else:
                self.assertIn("somme des plafonds Claude", err)
                self.assertFalse(os.path.exists(os.path.join(sortie + "-controle", "tentative-2.json")))
        # total relevé à 41 : relance calculée possible, seul le contrôle « KO » rejoué (bornée à trois)
        journal = os.path.join(self.tmp, "ko-41.log")
        ko = self.script(self.SCRIPT_CTRL_OK % journal, "ko-41.py")
        sortie = os.path.join(self.tmp, "l-paye-41")
        argv = self.base(sortie, prep, att, "--commande-externe", ko, "--budget-total-usd", "41", "--budget-externe-usd", "12")
        for n in (1, 2, 3):  # sommes de la relance : 40,2 ; 40,4 ; 40,6 (≤ 41) ; la troisième atteint la borne
            code, _, err = self.principal(self.lanceur(cout_controle_claude=0.2, ko_claude="claude-opus-5-5"), argv)
            self.assertEqual(code, 2)
            with open(os.path.join(sortie + "-controle", f"tentative-{n}.json")) as f:
                r = json.load(f)["reglages"]
            self.assertEqual(r["relancable"], n < 3, r["motifs_relance"])
        self.assertIn("3 tentatives faites", r["motifs_relance"][0])
        code, _, err = self.principal(self.lanceur(cout_controle_claude=0.2, ko_claude="claude-opus-5-5"), argv)
        self.assertEqual(code, 2)
        self.assertIn("tentatives", err)
        self.assertEqual(len(_lire(journal).splitlines()), 1)  # v42 : 3

    def test_tolerances_separees(self):
        """CL40-01 (code), point 5 : la tolérance Claude ne désarme pas la somme externe, et inversement ; l'ancienne option
        vaut les deux et est consignée au manifeste."""
        c = self.cours()
        prep = c.preparer()
        c._prep = prep
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        base = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"], temoins=prep["temoins"],
                    budgets=budgets, proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                    juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")],
                    proposeurs_externes=[("argon", "gemini-argon")], juges_externes=[("argon-j", "autre-lignee-x")])
        # Claude au-dessus (4 > 3), externe au-dessus (2,2 > 2,0)
        idn.verifier_reglages(budget_total_usd=3.0, budget_externe_usd=2.2, tolerer_somme_claude=True, **base)
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.verifier_reglages(budget_total_usd=4.0, budget_externe_usd=2.0, tolerer_somme_claude=True, **base)
        self.assertIn("externes", str(cm.exception))
        idn.verifier_reglages(budget_total_usd=4.0, budget_externe_usd=2.0, tolerer_somme_externe=True, **base)
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.verifier_reglages(budget_total_usd=3.0, budget_externe_usd=2.2, tolerer_somme_externe=True, **base)
        self.assertIn("Claude", str(cm.exception))
        idn.verifier_reglages(budget_total_usd=3.0, budget_externe_usd=2.0, tolerer_somme_plafonds=True, **base)
        # au cœur
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]})
        ext = dict(budgets=budgets, juges_externes=[("argon-j", "autre-lignee-x")])
        with self.assertRaises(idn.CourseInterrompue) as cm:
            c.lancer(ad, "t-c", budget_total_usd=3.0, budget_externe_usd=1.0, tolerer_somme_claude=True, **ext)
        self.assertIn("externes", str(cm.exception))
        self.assertEqual(ad.appels, [])
        # lanceur : options séparées, ancienne option consignée
        lanceur = self.lanceur()
        sortie = os.path.join(self.tmp, "l-tol")
        argv = self.base(sortie, prep, None, "--budget-externe-usd", "11.6", "--tolerer-somme-plafonds")
        code, out, err = self.principal(lanceur, argv)
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            d = json.load(f)["reglages"]
        self.assertEqual(d["versions"]["tolerances"], {"claude": True, "externe": True, "option_ancienne_les_deux": True})
        self.assertTrue(d["somme_des_plafonds"]["toleree_claude"] and d["somme_des_plafonds"]["toleree_externe"])
        a = lanceur.construire_analyseur()
        ns = a.parse_args(["s", "--tolerer-somme-plafonds-externe"])
        self.assertEqual(idn.tolerances(ns.tolerer_somme_plafonds, ns.tolerer_somme_plafonds_claude,
                                        ns.tolerer_somme_plafonds_externe), (False, True))

    # --- CL40-05 ---------------------------------------------------------------------------------------------------------

    def test_chemin_de_l_argent_valeurs_non_finies(self):
        """CL40-05 : `budget_controle_bras_usd` (réglages, cœur, bras), champs du relais, coûts et sceaux des tentatives :
        NaN, ±∞, négatif, booléen refusés ; cas sains acceptés."""
        c = self.cours()
        prep = c.preparer()
        c._prep = prep
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        base = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"], temoins=prep["temoins"],
                    budgets=budgets, proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                    juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")],
                    juges_externes=[("argon-j", "autre-lignee-x")], budget_total_usd=4.0, budget_externe_usd=1.2)
        for x in (float("nan"), -float("inf"), -5.0, True):  # v40 : −5,0 faisait passer 1,2 de plafonds sous un total de 6,0
            with self.subTest(budget_controle_bras_usd=x), self.assertRaises(idn.CourseInterrompue):
                idn.verifier_reglages(budget_controle_bras_usd=x, **base)
            with self.subTest(coeur=x), self.assertRaises(idn.CourseInterrompue):
                c.lancer(FauxAdaptateur({}), f"nf-{x}", budgets=budgets, juges_externes=[("argon-j", "autre-lignee-x")],
                         budget_externe_usd=1.2, budget_controle_bras_usd=x)
        idn.verifier_reglages(budget_controle_bras_usd=0.2, **base)  # sain
        idn.verifier_reglages(budget_controle_bras_usd=0, **dict(base, budget_externe_usd=1.0))  # sain : nul permis
        # relais
        lanceur = self.lanceur()
        juges = [("a", "claude-opus-5-5"), ("b", "claude-fable-5-1")]
        bj = {("juge_ideation", "claude-opus-5-5"): 4.0, ("juge_ideation", "claude-fable-5-1"): 7.0}
        sain = {"plafond_usd": 44, "reserve_par_appel_usd": 4, "depense_usd": 0.0}
        lanceur.verifier_relais(sain, 40.0, bj, juges)
        for champ, mauvais in (("depense_usd", (float("nan"), -float("inf"), True, -1.0)),
                               ("plafond_usd", (float("nan"), float("inf"), True)),
                               ("reserve_par_appel_usd", (float("nan"), -float("inf"), True))):
            for x in mauvais:
                with self.subTest(champ=champ, valeur=x), self.assertRaises(idn.CourseInterrompue):
                    lanceur.verifier_relais(dict(sain, **{champ: x}), 40.0, bj, juges)
        lanceur.verifier_relais({}, 40.0, bj, juges)  # relais muet : inchangé
        # tentatives de contrôle : sceau, coûts, numérotation, dossier sans tentative
        d = os.path.join(self.tmp, "s-controle")
        os.makedirs(d)
        r = {"reglages": {"cout_claude_usd": 0.4, "cout_externe_usd": 0.15}}
        idn.ecrire_json_scelle(os.path.join(d, "tentative-1.json"), r)
        self.assertEqual(len(lanceur.lire_tentatives_controle(d)), 1)  # sain
        with open(os.path.join(d, "tentative-2.json"), "w") as f:  # sans sceau
            json.dump(r, f)
        with self.assertRaises(idn.CourseInterrompue):
            lanceur.lire_tentatives_controle(d)
        os.remove(os.path.join(d, "tentative-2.json"))
        idn.ecrire_scelle(os.path.join(d, "tentative-2.json"), '{"reglages": {"cout_claude_usd": NaN, "cout_externe_usd": 0}}')
        with self.assertRaises(idn.CourseInterrompue):
            lanceur.lire_tentatives_controle(d)
        for nom in ("tentative-2.json", "tentative-2.json.sha256"):
            os.remove(os.path.join(d, nom))
        idn.ecrire_json_scelle(os.path.join(d, "tentative-2.json"), {"reglages": {"cout_claude_usd": -2.5, "cout_externe_usd": 0}})
        with self.assertRaises(idn.CourseInterrompue):
            lanceur.lire_tentatives_controle(d)
        for nom in ("tentative-2.json", "tentative-2.json.sha256"):
            os.remove(os.path.join(d, nom))
        with open(os.path.join(d, "tentative-1.json"), "a") as f:  # sceau faux
            f.write(" ")
        with self.assertRaises(idn.CourseInterrompue):
            lanceur.lire_tentatives_controle(d)
        d2 = os.path.join(self.tmp, "s2-controle")
        os.makedirs(os.path.join(d2, "tentative-1"))  # dossier de contrôle sans tentative scellée (arrêt brutal, ou retrait)
        with self.assertRaises(idn.CourseInterrompue):
            lanceur.lire_tentatives_controle(d2)
        idn.ecrire_json_scelle(os.path.join(d2, "tentative-2.json"), r)  # numérotation trouée
        with self.assertRaises(idn.CourseInterrompue):
            lanceur.lire_tentatives_controle(d2)
        # bras : tentative payée au sceau absent → refus ; budget du contrôle non fini → refus
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        c.lancer(ad, "nf-bras", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "nf-bras")
        att = self.cmd().attester(os.path.join(self.tmp, "att-nf.json"), sortie)
        bon = Enregistreur(c)
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets, budget_controle_usd=float("nan"),
                                      juges_externes=[("argon", "autre-lignee-x", bon)])
        with open(os.path.join(sortie, "bras-tentative-1.json"), "w") as f:
            json.dump({"reglages": {"journal": {"cout_total_usd": 0.15}}}, f)
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", bon)])
        self.assertIn("sceau", str(cm.exception))
        self.assertEqual(bon.recu, [])

    # --- CL40-08, CL40-07 (M07) ------------------------------------------------------------------------------------------

    def test_bras_interrompu_apres_envoi_ecrit_le_classement_sans_bras(self):
        """CL40-08 (S8) : interruption pendant la session du juge d'Argon (consigne envoyée) → manifeste, plafond compté,
        `classement-sans-bras.json` à deux juges marqué « sans juge externe », l'interruption remonte, bras verrouillé."""
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        c.lancer(ad, "ck", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "ck")
        att = self.cmd().attester(os.path.join(self.tmp, "att-ck.json"), sortie)
        coupe = Enregistreur(c, interrompre_juge=True)
        with self.assertRaises(KeyboardInterrupt):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", coupe)])
        chemin = os.path.join(sortie, "classement-sans-bras.json")
        self.assertTrue(idn.verifier_scelle(chemin))  # v40 : absent
        with open(chemin) as f:
            cl = json.load(f)
        self.assertFalse(cl["lisible_L2_L4"])
        self.assertIn("interrompu après envoi", cl["sans_juge_externe"])
        self.assertTrue(all(l["nombre_juges"] == 2 for l in cl["lignes"]))
        with open(os.path.join(sortie, "manifeste-bras-rapporte.json")) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertAlmostEqual(j["cout_total_usd"], 0.01 + 1.0)
        with self.assertRaises(idn.CourseInterrompue):  # verrouillé
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", Enregistreur(c))])

    def test_m07_controle_du_bras_a_cout_nul_processus_parti(self):
        """CL40-07 (M07) : un contrôle du bras où un processus est parti mais rien n'est compté (exception avec un plafond
        de contrôle nul ; ou « KO » à coût 0 d'un adaptateur fictif) est une **tentative payée** (bornée), jamais « non
        joué » ; seule une commande non lancée ou une clé dans l'environnement donnent « non joué »."""
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        for nom, adapt, plafond in (("m7a", Enregistreur(c, panne_controle=True), 0.0),
                                    ("m7b", Enregistreur(c, ko_gratuit=True), 0.2)):
            c.lancer(ad, nom, budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
            sortie = os.path.join(self.tmp, nom)
            att = self.cmd().attester(os.path.join(self.tmp, f"att-{nom}.json"), sortie)
            with self.assertRaises(idn.CourseInterrompue) as cm:
                idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets, budget_controle_usd=plafond,
                                          exiger_cout_controle=False, juges_externes=[("argon", "autre-lignee-x", adapt)])
            self.assertNotIn("non joué", str(cm.exception), nom)
            self.assertTrue(os.path.exists(os.path.join(sortie, "bras-tentative-1.json")), nom)
            self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-non-joue-1.json")), nom)

    def test_bras_tentative_relancable_calcule(self):
        """Point 4 (bras) : `relancable` d'une tentative payée du bras est calculé sur le plafond externe de la relance
        (coût de la tentative imputé), pas promis par le seul compte : 0,15 + 0,2 + 1,0 > 1,3 → faux dès la première."""
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        for nom, total, attendu in (("rb1", 1.3, False), ("rb2", 2.0, True)):
            c.lancer(ad, nom, budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=total)
            sortie = os.path.join(self.tmp, nom)
            att = self.cmd().attester(os.path.join(self.tmp, f"att-{nom}.json"), sortie)
            from pole.adaptateurs import AdaptateurCommandeExterne
            ko = AdaptateurCommandeExterne(self.cmd().commande(
                "import sys, json\nsys.stdin.read()\nprint(json.dumps({'texte': 'KO', 'cout_usd': 0.15}))\n", f"ko-{nom}.py"),
                environnement={})
            with self.assertRaises(idn.CourseInterrompue) as cm:
                idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                          juges_externes=[("argon", "autre-lignee-x", ko)])
            with open(os.path.join(sortie, "bras-tentative-1.json")) as f:
                r = json.load(f)["reglages"]
            self.assertEqual(r["relancable"], attendu, nom)  # v40 : vrai dans les deux cas
            self.assertIn("relance permise" if attendu else "plus de relance", str(cm.exception))

    # --- CL40-09 ---------------------------------------------------------------------------------------------------------

    def test_ecrits_du_lanceur(self):
        """CL40-09 : le devis en vigueur (v7 quinquies) nommé partout ; message d'interruption vrai pour les contrôles ;
        plus de promesse « trois tentatives » sans calcul."""
        chemin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demonstrations", "ideation_v2.py")
        with open(chemin, encoding="utf-8") as f:
            texte = f.read()
        for ancien in ("v7 bis", "v7 ter", "v7 quater", "relance permise\", qui", "bornée à trois)"):
            self.assertNotIn(ancien, texte)
        self.assertIn("devis v7 quinquies", texte)
        self.assertIn("contrôle compris", texte)


class Enregistreur:
    """Juge externe d'essai (v41) : enregistre ce qu'il reçoit ; contrôle « OK » à 0,01 ; options : panne au contrôle,
    « KO » gratuit au contrôle, interruption pendant la session du juge."""
    nom = "commande-externe"

    def __init__(self, cours, panne_controle=False, ko_gratuit=False, interrompre_juge=False):
        self.cours, self.recu = cours, []
        self.panne_controle, self.ko_gratuit, self.interrompre_juge = panne_controle, ko_gratuit, interrompre_juge

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        self.recu.append(consigne)
        if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
            if self.panne_controle:
                raise RuntimeError("panne pendant le contrôle")
            return Resultat("KO" if self.ko_gratuit else "OK", [], 0.0 if self.ko_gratuit else 0.01, "ok")
        if self.interrompre_juge:
            raise KeyboardInterrupt("signal 15")
        idents = sorted(set(re.findall(r'"identifiant": "(T\d\d)"', consigne)))
        return Resultat("```json\n" + json.dumps(self.cours.notes_temoins_ok(idents, consigne)) + "\n```", [], 0.3, "ok")

    def description(self):
        return {"commande": ["enregistreur"]}


class TestReglagesV35(CasAvecDossier):
    def test_options_tools_vides_et_effort(self):
        """CL34-02 / CL34-08 : `tools=[]` (jeu disponible) pour les rôles de l'idéation, effort fixé ; les autres rôles
        gardent le jeu par défaut du kit (None)."""
        dossier = os.path.join(self.tmp, "course", "juges", "j")
        os.makedirs(dossier)
        o = construire_options(dossier, 1.0, 2, url_relais="http://127.0.0.1:8787", modele="claude-opus-5-5",
                               role="juge_ideation", interdire_lecture=[os.path.join(self.tmp, "course")])
        self.assertEqual((o["tools"], o["allowed_tools"], o["effort"]), ([], [], "medium"))
        o = construire_options(dossier, 1.0, 2, url_relais="http://127.0.0.1:8787", modele="claude-opus-5-5",
                               role="experimentateur", interdire_lecture=[os.path.join(self.tmp, "course")])
        self.assertIsNone(o["tools"])
        self.assertIsNone(o["effort"])

    def test_ligne_de_commande_du_kit_sans_outil(self):
        """CL34-02 : la ligne de commande construite par le kit porte `--tools ''` (jamais exécutée)."""
        try:
            import claude_agent_sdk as sdk
            from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
        except ImportError:
            self.skipTest("kit d'agent absent")
        from pole.adaptateurs import AdaptateurClaudeSDK
        dossier = os.path.join(self.tmp, "course", "juges", "j")
        os.makedirs(dossier)
        o = construire_options(dossier, 1.0, 2, url_relais="http://127.0.0.1:8787", modele="claude-opus-5-5",
                               role="juge_ideation", interdire_lecture=[os.path.join(self.tmp, "course")])
        options = AdaptateurClaudeSDK.options_sdk(sdk, o)
        options.cli_path = "/bin/true"
        cmd = SubprocessCLITransport("x", options)._build_command()
        self.assertIn("--tools", cmd)
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        self.assertNotIn("--allowedTools", cmd)
        self.assertEqual(cmd[cmd.index("--effort") + 1], "medium")
        for nom in [n for n in sys.modules if n.startswith("claude_agent_sdk")]:  # CL39-12 : ne pas laisser le kit chargé
            del sys.modules[nom]

    def test_borne_de_temps_par_session(self):
        """CL34-05 : une session qui pend au-delà du délai rend « erreur » avec un motif, sans lever."""
        import asyncio
        from pole.adaptateurs import AdaptateurClaudeSDK

        class FauxSDK:
            class ClaudeSDKError(Exception):
                pass

            class AssistantMessage:
                pass

            class ResultMessage:
                pass

            class TextBlock:
                pass

            @staticmethod
            async def query(prompt, options):
                await asyncio.sleep(5)
                yield None
        texte, cout, statut, erreur, lecture = asyncio.run(AdaptateurClaudeSDK._executer(FauxSDK, "x", None, delai_s=0.2))
        self.assertEqual((texte, cout, statut, lecture["refus"]), ("", 0.0, "erreur", None))  # v47 (R-764) : lecture rendue
        self.assertIn("délai de session dépassé", erreur)
        with self.assertRaises(ValueError):
            AdaptateurClaudeSDK("http://127.0.0.1:8787", delai_s=0)

    def test_garde_pluriels(self):
        """CL34-10 : pluriels signalés."""
        for texte in ("Étapes 1 : préparer", "les injections de consignes", "des portes dérobées", "exécuter les scripts fournis"):
            self.assertTrue(idn.signaux_niveau_methode(texte), texte)
        self.assertFalse(idn.signaux_niveau_methode("classe exfiltration, nommée par protocole") == [], "signal assumé")


class TestCourseV35(CasAvecDossier):
    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def test_nombre_borne_et_controles_comptes(self):
        """CL34-11 : nombre ∉ [1, 12] refusé ; CL34-07 : le coût déjà engagé (contrôles) entre au journal et au plafond."""
        c = self.cours()
        fiches = {"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        for n in (0, 13, True):
            with self.assertRaises(idn.CourseInterrompue):
                c.lancer(ad, f"c-{n}", nombre_par_proposeur=n)
        with self.assertRaises(idn.CourseInterrompue):
            c.lancer(ad, "c-neg", cout_deja_engage_usd=-1)
        self.assertEqual(ad.appels, [])
        res = c.lancer(ad, "c-ok", cout_deja_engage_usd=0.07)
        self.assertAlmostEqual(res["journal"]["cout_appels_de_controle_usd"], 0.07)
        self.assertAlmostEqual(res["journal"]["cout_total_usd"], 0.07 + 4 * 0.5)
        c.lancer(ad, "c-juste", budget_total_usd=2.5, tolerer_somme_plafonds=True)  # sans contrôle : 1,5 + 1 = 2,5, passe
        with self.assertRaises(idn.CourseInterrompue):  # 0,07 + 1,5 + 1 > 2,5 : le contrôle compté arrête avant le dernier juge
            c.lancer(ad, "c-plafond", cout_deja_engage_usd=0.07, budget_total_usd=2.5, tolerer_somme_plafonds=True)
        with self.assertRaises(idn.CourseInterrompue):  # CL37-03 : sans tolérance, 4,07 > 4 refusé avant tout appel
            n = len(ad.appels)
            c.lancer(ad, "c-somme", cout_deja_engage_usd=0.07, budget_total_usd=4.0)
        self.assertEqual(len(ad.appels), n)

    def test_taille_max_pieces_bornee(self):
        """v37 : taille des pièces réglable, plafond dur, consignée au manifeste ; hors borne → refus avant tout appel."""
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute()], "fable": [fiche_brute()]})
        for t in (0, idn.TAILLE_MAX_PIECES_ABSOLUE + 1, True, 10.0):
            with self.assertRaises(idn.CourseInterrompue):
                c.lancer(ad, f"t-{t}", taille_max_pieces=t)
        self.assertEqual(ad.appels, [])
        with self.assertRaises(idn.PieceInterdite):  # pièces plus longues que le réglage
            c.lancer(ad, "t-court", taille_max_pieces=5)
        res = c.lancer(ad, "t-ok", taille_max_pieces=650_000)
        with open(os.path.join(self.tmp, "t-ok", "manifeste-depart.json")) as f:
            m = json.load(f)["reglages"]
        self.assertEqual(m["taille_max_pieces"], 650_000)
        self.assertGreater(m["taille_pieces_servies"]["proposeurs"], 0)
        self.assertIsNotNone(res["classement"])

    def test_manifeste_de_fin_sur_toute_exception(self):
        """CL34-09 : une exception qui n'est pas CourseInterrompue écrit quand même le manifeste de fin, puis remonte."""
        class AdaptateurQuiCasse(FauxAdaptateur):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                raise OSError("relais injoignable")
        c = self.cours()
        ad = AdaptateurQuiCasse({"opus": [fiche_brute()], "fable": [fiche_brute()]})
        with self.assertRaises(OSError):
            c.lancer(ad, "c-casse")
        chemin = os.path.join(self.tmp, "c-casse", "manifeste-fin.json")
        self.assertTrue(os.path.exists(chemin + ".sha256"))
        with open(chemin) as f:
            self.assertIn("OSError", json.load(f)["reglages"]["erreur"])


class TestV42(CasAvecDossier):
    """v42 (contre-lecture CL8 de la v41 ; choix de session-depot, message n° 151) : contrôle du bras court, garde de taille
    sans dépense, plafond externe donné au bras, classement sans juge externe dès qu'une tentative du bras est non
    relançable (CL41-01) ; fiche bornée et marge réaliste (CL41-02) ; consigne de contrôle qui finit par « OK » (CL41-03) ;
    contrôle non court refusé = envoi (CL41-04) ; relais gardé et relancé à neuf (CL41-05) ; fenêtre SORTIE sans manifeste
    (CL41-06) ; Argon contrôlé d'abord (CL41-07) ; un essai par trou de CL41-08 (N03, N04, N07, N08, N13, V12, V20, V34, V36)."""

    def v41(self):
        t = TestV41("test_ecrits_du_lanceur")
        t.tmp = self.tmp
        return t

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def cmd(self):
        c = TestCommandeExterne("test_commande_factice_notes_et_controle")
        c.tmp = self.tmp
        return c

    def journal_de(self, chemin):
        if not os.path.exists(chemin):
            return []
        return [json.loads(l) for l in _lire(chemin).splitlines() if l.strip()]

    # Argon factice au barème haut du code (10 dollars par million de jetons d'entrée à 3 caractères par jeton, plus 2 000
    # jetons de sortie à 50 dollars par million), coût jamais borné par la commande ; chaque appel consigné
    SCRIPT_BAREME = (
        "import sys, json, os, re\nc = sys.stdin.read()\n"
        "ctrl = c.startswith('Réponds exactement OK')\n"
        "open(%r, 'a').write(json.dumps({'taille': len(c), 'controle': ctrl, 'role': os.environ['ROLE_POLE']}) + '\\n')\n"
        "cout = len(c) / 3 * 10e-6 + 2000 * 50e-6\n"
        "if ctrl: print(json.dumps({'texte': 'OK', 'cout_usd': cout})); sys.exit(0)\n"
        "bloc = json.loads(re.search(r'```json\\n(\\[.*\\])\\n```', c, re.S).group(1)); par_nom = {f['nom']: f['identifiant'] for f in bloc}\n"
        "notes = []\n"
        "for f in bloc:\n"
        "    k = {x: 2 for x in ('avantage', 'originalite', 'falsifiabilite', 'traitabilite', 'robustesse')}\n"
        "    if f['nom'] == 'Verbeux vide': k.update({'avantage': 1, 'originalite': 1, 'falsifiabilite': 0})\n"
        "    if f['nom'] == 'Assuré occupé': k.update({'avantage': 1, 'originalite': 0})\n"
        "    notes.append({'identifiant': f['identifiant'], 'criteres': k, 'justifications': {}})\n"
        "d = [[par_nom['Jumeau'], par_nom['Sobre fort']]]\n"
        "print(json.dumps({'texte': '```json\\n' + json.dumps({'notes': notes, 'doublons': d}) + '\\n```', 'cout_usd': cout}))\n")

    def course_avec_piece_juge(self, nom, taille_piece_juge=240_000, versions=None):
        """Course (cœur, faux adaptateur Claude) avec une pièce d'antériorité servie aux juges : consigne du juge externe
        en attente d'environ 243 000 caractères (S6 et S10-grand de CL7 et CL8)."""
        c = self.cours()
        if not hasattr(self, "_prep_pj"):
            self._prep_pj = c.preparer()  # liste blanche scellée une fois par essai (jamais écrasée)
        prep = self._prep_pj
        pj = os.path.join(self.tmp, "piece-juge.md")
        if not os.path.exists(pj):
            with open(pj, "w", encoding="utf-8") as f:
                f.write("# Antériorité\n" + ("Résumé d'article. " * 20000)[:taille_piece_juge])
        lb = os.path.join(self.tmp, "liste-blanche-pj.json")
        if not os.path.exists(lb):
            idn.construire_liste_blanche([prep["pieces"][0], prep["question"], prep["materiau"][0], prep["temoins"], pj], lb)
        c._prep = dict(prep, liste_blanche=lb)
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "gemini-argon")] = 3.5
        c.lancer(ad, nom, budgets=budgets, juges_externes=[("argon", "gemini-argon")], budget_externe_usd=3.7,
                 pieces_juge=[pj], versions=versions)
        sortie = os.path.join(self.tmp, nom)
        att = self.cmd().attester(os.path.join(self.tmp, f"att-{nom}.json"), sortie)
        return sortie, att, budgets

    # --- CL41-01 ---------------------------------------------------------------------------------------------------------

    def test_cl41_01_consigne_du_juge_de_243000_au_bareme_haut(self):
        """CL41-01 (S10-grand) : consigne du juge de 243 000 caractères, Argon au barème haut du code, sans borne à son
        plafond : le contrôle du bras est court (≈ 0,10 < 0,2), le juge joue (≈ 0,91 < 3,5), classement à trois juges
        (v41 : contrôle de 243 000 caractères facturé 0,91 > 0,2, refusé après toute la dépense, aucun classement).
        Variante : garde de taille (donnée, puis par défaut sur un plafond de juge de 0,5) → refus scellé avant tout
        appel, rien payé ; puis le bras se joue.
        **Changé en v43** (CL42-05, choix de session-depot n° 156) : la garde par défaut déduit la provision de sortie du
        juge (6 fiches servies × 2 000 × 5 : 1 400 000 − 60 000) ; chaque refus de taille **compte une tentative non
        relançable** et le premier écrit le classement sans bras (le second ne le réécrit pas) ; le bras se joue donc en
        tentative 3 (v42 : en tentative 1, refus non comptés) ; la taille donnée à la course **ne vaut plus** pour le bras
        (v42 : refus « donnée à la course »)."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        sortie, att, budgets = self.course_avec_piece_juge("c-243k")
        with open(os.path.join(sortie, "juges-bras-rapporte", "traces-argon", "consigne-en-attente.md"), encoding="utf-8") as f:
            taille_juge = len(f.read())
        self.assertGreaterEqual(taille_juge, 243_000)
        journal = os.path.join(self.tmp, "argon-bareme.jsonl")
        argon = AdaptateurCommandeExterne(self.cmd().commande(self.SCRIPT_BAREME % journal, "argon-bareme.py"), environnement={})
        externes = [("argon", "gemini-argon", argon)]
        res = idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets, juges_externes=externes)
        self.assertFalse(res["sans_bras"])
        self.assertTrue(all(l["nombre_juges"] == 3 and l["nom_agregat"] == "mediane" for l in res["classement"]))
        self.assertTrue(idn.verifier_scelle(os.path.join(sortie, "classement.json")))
        appels = self.journal_de(journal)
        self.assertEqual([(a["controle"], a["taille"] if a["controle"] else None) for a in appels],
                         [(True, len(idn.APPEL_DE_CONTROLE_CONSIGNE)), (False, None)])  # contrôle court, puis le juge
        self.assertEqual(appels[1]["taille"], taille_juge)
        ctrl = res["journal"]["controle"]["argon"]
        self.assertLess(ctrl["cout_compte_usd"], 0.2)
        self.assertTrue(ctrl["consigne_courte"])
        self.assertAlmostEqual(res["journal"]["cout_total_usd"], ctrl["cout_compte_usd"] + taille_juge / 3 * 10e-6 + 0.1, places=4)
        self.assertEqual(res["journal"]["garde_taille"]["argon"]["taille_caracteres"], taille_juge)
        # v43 (CL42-05) : 3,5 / 2,5e-6 − provision de sortie (6 fiches servies × 2 000 caractères au rapport 5)
        self.assertEqual(res["journal"]["garde_taille"]["argon"]["taille_max_caracteres"], 1_400_000 - 6 * 10_000)
        self.assertEqual(res["journal"]["garde_taille"]["argon"]["provision_sortie_caracteres"], 60_000)
        # variante : la garde refuse avant toute dépense (taille donnée) ; v43 : tentative 1 non relançable, classement
        # sans bras écrit
        sortie2, att2, _ = self.course_avec_piece_juge("c-243k-garde")
        avant = len(self.journal_de(journal))
        with self.assertRaises(idn.SansJugeExterne) as cm:
            idn.executer_bras_differe(sortie2, attestation_lecture_humaine=att2, budgets=budgets, juges_externes=externes,
                                      taille_max_consigne_externe=100_000)
        self.assertIn("rien payé", str(cm.exception))
        self.assertIsInstance(cm.exception.__cause__, idn.TailleConsigneRefusee)
        self.assertEqual(len(self.journal_de(journal)), avant)  # Argon jamais appelé, pas même au contrôle
        r1 = os.path.join(sortie2, "manifeste-bras-refus-taille-1.json")
        self.assertTrue(idn.verifier_scelle(r1))
        with open(r1) as f:
            g = json.load(f)["reglages"]
        self.assertEqual((g["garde_taille"]["taille_max_caracteres"], g["cout_usd"], g["tentative_comptee"], g["relancable"]),
                         (100_000, 0.0, True, False))
        cl = os.path.join(sortie2, "classement-sans-bras.json")
        empreinte_cl = idn.sha256_fichier(cl)
        # garde par défaut : plafond de juge de 0,5 → 200 000 − 60 000 caractères au plus ; tentative 2, classement gardé
        petit = dict(budgets)
        petit[("juge_ideation", "gemini-argon")] = 0.5
        with self.assertRaises(idn.SansJugeExterne) as cm:
            idn.executer_bras_differe(sortie2, attestation_lecture_humaine=att2, budgets=petit, juges_externes=externes)
        self.assertIn("non réécrit", str(cm.exception))
        r2 = os.path.join(sortie2, "manifeste-bras-refus-taille-2.json")
        self.assertTrue(idn.verifier_scelle(r2))
        with open(r2) as f:
            self.assertEqual(json.load(f)["reglages"]["garde_taille"]["taille_max_caracteres"], 140_000)
        self.assertEqual(idn.sha256_fichier(cl), empreinte_cl)
        self.assertEqual(len(self.journal_de(journal)), avant)
        for nom in os.listdir(sortie2):
            self.assertFalse(nom.startswith(("bras-tentative", "manifeste-bras-non-joue", "manifeste-bras-rapporte",
                                             "bras-rapporte-controle", "classement.json")), nom)
        res2 = idn.executer_bras_differe(sortie2, attestation_lecture_humaine=att2, budgets=budgets, juges_externes=externes)
        self.assertEqual(res2["journal"]["tentative"], 3)  # v43 : les deux refus de taille comptent (v42 : 1)
        self.assertFalse(res2["sans_bras"])
        # v43 : la taille donnée à la course (consignée au manifeste de départ) ne vaut plus pour le bras
        sortie3, att3, _ = self.course_avec_piece_juge("c-243k-option", versions={"taille_max_consigne_externe": {
            "valeur": 200_000, "origine": "option"}})
        res3 = idn.executer_bras_differe(sortie3, attestation_lecture_humaine=att3, budgets=budgets, juges_externes=externes)
        self.assertFalse(res3["sans_bras"])
        self.assertTrue(res3["journal"]["garde_taille"]["argon"]["origine_taille_max"].startswith("défaut"))
        self.assertEqual(len(self.journal_de(journal)), avant + 4)

    def test_cl41_01_plafond_externe_donne_au_bras_et_classement_si_non_relancable(self):
        """CL41-01 : une tentative du bras scellée non relançable écrit tout de suite le classement à deux juges (« sans
        juge externe », code 5), sans verrouiller ; le bras lancé sans `--budget-externe-usd` garde le plafond de la course
        (relance refusée) ; avec `--budget-externe-usd 12` (mot de Lazar), le lanceur le transmet et le bras se joue (v41 :
        code 2 sans classement, `budget_externe_usd=None` toujours passé)."""
        v41 = self.v41()
        prep = self.cours().preparer()
        sortie = os.path.join(self.tmp, "l-nr")
        ok = " ".join(self.cmd().commande(self.cmd().SCRIPT_OK))
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, None, "--commande-externe", ok,
                                                                "--budget-externe-usd", "9"))
        self.assertEqual(code, 0, err)
        att = self.cmd().attester(os.path.join(self.tmp, "att-nr.json"), sortie, "argon-j")
        ko = v41.script("import sys, json\nsys.stdin.read()\nprint(json.dumps({'texte': 'KO', 'cout_usd': 5.2}))\n", "ko52.py")
        bras = [sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine", att, "--juge-externe", "argon-j=gemini-argon"]
        code, out, err = v41.principal(v41.lanceur(), bras + ["--commande-externe", ko])
        self.assertEqual(code, 5, err)  # 0,251 + 5,2 + 3,7 > 9 : non relançable
        self.assertIn("classement-sans-bras.json", err)
        cl = os.path.join(sortie, "classement-sans-bras.json")
        self.assertTrue(idn.verifier_scelle(cl))  # v41 : absent
        with open(cl) as f:
            c = json.load(f)
        self.assertFalse(c["lisible_L2_L4"])
        self.assertIn("non relançable", c["sans_juge_externe"])
        self.assertTrue(all(l["nombre_juges"] == 2 for l in c["lignes"]))
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-rapporte.json")))  # pas de verrou
        with open(os.path.join(sortie, "bras-tentative-1.json")) as f:
            self.assertFalse(json.load(f)["reglages"]["relancable"])
        code, out, err = v41.principal(v41.lanceur(), bras + ["--commande-externe", ok])
        self.assertEqual(code, 2)
        self.assertIn("plafond externe 9.0 insuffisant", err)  # plafond relu au manifeste de départ, pas le défaut 11,6
        code, out, err = v41.principal(v41.lanceur(), bras + ["--commande-externe", ok, "--budget-externe-usd", "12"])
        self.assertIn(code, (0, 4), err)
        with open(os.path.join(sortie, "manifeste-bras-rapporte.json")) as f:
            jb = json.load(f)["reglages"]["journal"]
        self.assertEqual(jb["plafond_externe_usd"], 12.0)
        self.assertAlmostEqual(jb["cout_tentatives_precedentes_usd"], 5.2)
        with open(os.path.join(sortie, "classement.json")) as f:
            self.assertTrue(all(l["nombre_juges"] == 3 for l in json.load(f)["lignes"]))
        # une valeur non finie donnée au bras est refusée avant tout appel
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets={}, juges_externes=[],
                                      budget_externe_usd=float("nan"))

    def test_cl41_01_classement_apres_le_dernier_bras_non_joue(self):
        """CL41-01 : trois tentatives « non jouées » (commande introuvable : rien envoyé, rien payé) — la troisième est
        scellée non relançable et écrit le classement à deux juges « sans juge externe », sans verrou (v41 : aucun)."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        c.lancer(ad, "nj", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        sortie = os.path.join(self.tmp, "nj")
        att = self.cmd().attester(os.path.join(self.tmp, "att-nj.json"), sortie)
        introuvable = [("argon", "autre-lignee-x", AdaptateurCommandeExterne(["/chemin/qui/n/existe/pas"], environnement={}))]
        for n in (1, 2, 3):
            with self.assertRaises(idn.CourseInterrompue) as cm:
                idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets, juges_externes=introuvable)
            self.assertEqual(isinstance(cm.exception, idn.SansJugeExterne), n == 3, n)
            self.assertEqual(os.path.exists(os.path.join(sortie, "classement-sans-bras.json")), n == 3, n)
        with open(os.path.join(sortie, "classement-sans-bras.json")) as f:
            cl = json.load(f)
        self.assertIn("tentative 3 du bras non relançable", cl["sans_juge_externe"])
        self.assertTrue(all(l["nombre_juges"] == 2 for l in cl["lignes"]))
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-bras-rapporte.json")))

    def test_cl41_01_garde_de_taille_de_la_course_avant_tout_controle(self):
        """CL41-01 (course) : consigne de contrôle d'Argon plus grosse que `--taille-max-consigne-externe` (donnée, puis par
        défaut : `--budget-controle-externe-usd` / prix prudent) → code 2, refus scellé dans SORTIE-controle, aucun
        contrôle (ni Argon ni Claude), aucune tentative ; la relance sans l'option passe et consigne la valeur par défaut.
        **Changé en v43** (CL42-01) : défaut 520 000 caractères (contrôle 2,5 → 1 000 000 ; passe 2,5 → 1 000 000 moins la
        provision de sortie de 480 000 ; le plus petit) ; v42 : 1 000 000. Le second cas (contrôle à 0,001 → 400) est
        inchangé : le contrôle, entrée seule, y est la session la plus petite."""
        v41 = self.v41()
        prep = self.cours().preparer()
        journal = os.path.join(self.tmp, "argon-garde.jsonl")
        argon = v41.script(self.cmd().SCRIPT_OK.replace("consigne = sys.stdin.read()\n", "consigne = sys.stdin.read()\n"
                                                        "open(%r, 'a').write('{}\\n')\n" % journal, 1), "argon-garde.py")
        sortie = os.path.join(self.tmp, "l-garde")
        argv = v41.base(sortie, prep, None, "--commande-externe", argon)
        for n, options, tmax in ((1, ["--taille-max-consigne-externe", "1000"], 1000),
                                 (2, ["--budget-controle-externe-usd", "0.001"], 400)):
            code, out, err = v41.principal(v41.lanceur(cout_controle_claude=0.2), argv + options)
            self.assertEqual(code, 2, err)
            self.assertIn("garde de taille", err)
            r = os.path.join(sortie + "-controle", f"refus-taille-{n}.json")
            self.assertTrue(idn.verifier_scelle(r))
            with open(r) as f:
                g = json.load(f)["reglages"]
            self.assertEqual((g["garde_taille"]["taille_max_caracteres"], g["cout_usd"]), (tmax, 0.0))
            self.assertEqual(self.journal_de(journal), [])  # Argon jamais appelé
            self.assertEqual(sorted(os.listdir(sortie + "-controle")),
                             sorted(x for k in range(1, n + 1) for x in (f"refus-taille-{k}.json", f"refus-taille-{k}.json.sha256")))
            self.assertFalse(os.path.exists(sortie))
        code, out, err = v41.principal(v41.lanceur(), argv)
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            v = json.load(f)["reglages"]["versions"]
        self.assertEqual(v["tentatives_precedentes"], [])  # les refus de taille ne sont pas des tentatives
        self.assertEqual((v["taille_max_consigne_externe"]["valeur"], v["taille_max_consigne_externe"]["origine"]),
                         (520_000, "defaut"))  # v43 (CL42-01) ; v42 : 1 000 000
        self.assertEqual(v["marge_controle_externe"]["garde_taille"]["taille_max_caracteres"], 520_000)

    # --- CL41-02 ---------------------------------------------------------------------------------------------------------

    def test_cl41_02_fiche_bornee_et_marge_realiste(self):
        """CL41-02 : listes bornées (9 questions, 12 antériorités) ; `fiche_maximale` = le maximum du gabarit ; la passe 2
        réelle à fiches maximales ne dépasse pas la consigne éprouvée ; tailles écrites au manifeste de départ et au journal.
        **Changé en v43** (CL42-04, décision de Lazar : « retirer ») : plus de borne de 12 000 caractères sur la fiche — les
        deux fiches que la v42 refusait (guillemets échappés, quatre champs de 3 000) sont admises ; `fiche_maximale` revient
        au pire cas aux bornes par champ (44 259 caractères servis, v42 : 12 000) ; les listes restent bornées."""
        ok9 = idn.valider_fiche_ideation(fiche_brute(questions_servies=["Q1"] * 9), "a", 1)
        self.assertEqual(len(ok9["questions_servies"]), 9)
        for modif, motif in ((dict(questions_servies=["Q1"] * 10), "questions_servies"),
                             (dict(anteriorite=[{"reference": "r", "statut": "SUPPOSE"}] * 13), "anteriorite")):
            with self.subTest(motif=motif), self.assertRaises(idn.FicheIdeationInvalide) as cm:
                idn.valider_fiche_ideation(fiche_brute(**modif), "a", 1)
            self.assertIn(motif, str(cm.exception))
        for modif in (dict(enonce='"' * 2900, perte_traduction='"' * 2900, piege='"' * 2900),
                      dict(enonce="y" * 3000, perte_traduction="y" * 3000, piege="y" * 3000, cosmetique_si="y" * 3000)):
            self.assertGreater(idn.taille_servie(idn.valider_fiche_ideation(fiche_brute(**modif), "a", 1)), 12_000)  # v42 : refusées
        idn.valider_fiche_ideation(fiche_brute(anteriorite=[{"reference": "r", "statut": "SUPPOSE"}] * 12), "a", 1)
        fm = idn.fiche_maximale()
        taille_fm = idn.taille_servie(fm)
        self.assertGreater(taille_fm, 44_000)  # 44 259 : douze textes de 3 000, listes à leur borne
        self.assertEqual(idn.taille_servie(idn.valider_fiche_ideation(fm, "a", 1)), taille_fm)
        # la passe 2 réelle d'Argon (8 fiches à la taille maximale) tient dans la consigne éprouvée
        c = self.cours()
        prep = c.preparer()
        c._prep = prep
        att = os.path.join(self.tmp, "att-m42.json")
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-29", "materiau_sha256": {
            os.path.basename(prep["materiau"][0]): idn.sha256_fichier(prep["materiau"][0])}})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        v2 = idn.verifier_reglages(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"],
                                   temoins=prep["temoins"], budgets=budgets, materiau=prep["materiau"], seconde_passe=True,
                                   attestation_materiau=att, proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                                   juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")],
                                   proposeurs_externes=[("argon", "gemini-argon")], budget_total_usd=20.0, budget_externe_usd=5.0)
        self.assertEqual(v2["taille_fiche_maximale"], taille_fm)
        self.assertGreater(v2["taille_consigne_controle_externe"], 8 * taille_fm)  # v43 : comme la v41 (v42 : < 8 × 13 000)
        tailles = []

        class Argon:
            nom = "argon-simule"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                tailles.append((os.path.basename(dossier), len(consigne)))
                fiches = [dict(fm, nom=f"Argon {i}".ljust(200, "x")) for i in range(8)]
                return Resultat("```json\n" + json.dumps({"fiches": fiches}, ensure_ascii=False) + "\n```", [], 0.1, "ok")
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        res = c.lancer(ad, "c-borne", budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", Argon())],
                       budget_externe_usd=5.0, seconde_passe=True, attestation_materiau=att)
        self.assertEqual([d for d, _ in tailles], ["passe-1", "passe-2"])
        self.assertLessEqual(tailles[1][1], len(v2["texte_controle_externe"]))
        self.assertEqual(sum(1 for f in res["fiches"] if f["auteur"] == "argon"), 16)
        self.assertEqual(res["journal"]["marge_seconde_passe"]["taille_fiche_maximale_servie"], taille_fm)
        with open(os.path.join(self.tmp, "c-borne", "manifeste-depart.json")) as f:
            self.assertEqual(json.load(f)["reglages"]["taille_fiche_maximale_servie"], taille_fm)
        # la consigne des proposeurs dit les bornes
        self.assertIn("au plus 9 questions servies, au plus 12 antériorités", v2["texte_controle_externe"])
        # au lanceur : taille de la marge et du contrôle au manifeste de départ
        v41 = self.v41()
        sortie = os.path.join(self.tmp, "l-marge")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe",
                                                                " ".join(self.cmd().commande(self.cmd().SCRIPT_OK))))
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            v = json.load(f)["reglages"]["versions"]
        m = v["marge_controle_externe"]
        self.assertEqual(m["taille_fiche_maximale_servie"], taille_fm)
        self.assertEqual(m["taille_consigne_de_controle"], v["appel_de_controle"]["externe:argon"]["taille_consigne"])

    def test_v36_listes_comptees_dans_fiche_maximale(self):
        """CL41-08 (V36) : `fiche_maximale` compte les deux listes à leur borne (9 questions, 12 antériorités)."""
        fm = idn.fiche_maximale()
        self.assertEqual((len(fm["questions_servies"]), len(fm["anteriorite"])), (idn.MAX_QUESTIONS_SERVIES, idn.MAX_ANTERIORITES))
        self.assertEqual((idn.MAX_QUESTIONS_SERVIES, idn.MAX_ANTERIORITES), (9, 12))
        self.assertTrue(all(len(q) == 80 for q in fm["questions_servies"]))

    # --- CL41-03 et N13 --------------------------------------------------------------------------------------------------

    def test_cl41_03_et_n13_consigne_de_controle_recue_par_la_commande(self):
        """CL41-03 : la consigne de contrôle d'Argon que **reçoit la commande** encadre le matériau entre délimiteurs et finit
        par « Fin du matériau. Réponds exactement OK, sans rien d'autre. » ; N13 : ce matériau est sa consigne de passe 2
        (fiches de première passe, matériau, instructions), pas les pièces seules ; au bras, le contrôle reçu est la
        consigne courte, qui finit par « Réponds exactement OK, sans rien d'autre. » (v41 : finit par « un seul bloc json »)."""
        v41 = self.v41()
        prep, att = v41.prep_devis()
        recu = os.path.join(self.tmp, "controles-recus.txt")
        script = self.cmd().SCRIPT_OK.replace(
            "if 'exactement OK' in consigne:\n",
            "if 'exactement OK' in consigne:\n    open(%r, 'a', encoding='utf-8').write(consigne + '\\x00')\n" % recu, 1)
        argon = v41.script(script, "argon-recoit.py")
        sortie = os.path.join(self.tmp, "l-recu")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe", argon))
        self.assertEqual(code, 0, err)
        course = _lire(recu).split("\x00")[0]
        self.assertTrue(course.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE))
        self.assertTrue(course.endswith("Fin du matériau. Réponds exactement OK, sans rien d'autre."))
        self.assertEqual(idn.APPEL_DE_CONTROLE_FIN, "Fin du matériau. Réponds exactement OK, sans rien d'autre.")
        materiau = course.split(idn.DEBUT_MATERIAU_CONTROLE + "\n", 1)[1].rsplit("\n" + idn.FIN_MATERIAU_CONTROLE, 1)[0]
        for attendu in ("## Tes fiches de la première passe", "Tour interne", "## Ce que tu rends", "## Pièce : piece-a.md"):
            self.assertIn(attendu, materiau)  # N13 : la consigne de passe 2, pas les pièces seules
        self.assertNotIn("## Ce que tu rends", course.rsplit(idn.FIN_MATERIAU_CONTROLE, 1)[1])
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            v = json.load(f)["reglages"]["versions"]
        self.assertEqual(len(course), v["appel_de_controle"]["externe:argon"]["taille_consigne"])
        # bras : contrôle court
        att_b = self.cmd().attester(os.path.join(self.tmp, "att-recu.json"), sortie, "argon-j")
        code, out, err = v41.principal(v41.lanceur(), [sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine", att_b,
                                                       "--juge-externe", "argon-j=gemini-argon", "--commande-externe", argon])
        self.assertIn(code, (0, 4), err)
        bras = _lire(recu).split("\x00")[1]
        self.assertEqual(bras, idn.APPEL_DE_CONTROLE_CONSIGNE)
        self.assertTrue(bras.endswith("Réponds exactement OK, sans rien d'autre."))

    # --- CL41-04 ---------------------------------------------------------------------------------------------------------

    def test_cl41_04_controle_non_court_refuse_verrouille_le_bras(self):
        """CL41-04 : contrôle court refusé → tentative payée, message « avant tout envoi des fiches » vrai (la commande n'a
        reçu que 41 caractères) ; un contrôle qui n'était pas court (il a pu recevoir les fiches — ne doit plus arriver,
        simulé ici) et n'a pas rendu « OK » verrouille le bras comme un envoi : manifeste du bras, classement sans bras,
        aucune tentative relançable (v41 : tentative « relance permise », le tirage du juge rejoué)."""
        import unittest.mock
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0

        class NotesAuControle(Enregistreur):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
                    self.recu.append(consigne)
                    return Resultat("```json\n{\"notes\": []}\n```", [], 0.05, "ok")
                return Enregistreur.lancer(self, role, consigne, dossier, budget_usd, max_tours, modele)
        # contrôle court refusé : message vrai, tentative payée
        c.lancer(ad, "nc1", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        s1 = os.path.join(self.tmp, "nc1")
        att1 = self.cmd().attester(os.path.join(self.tmp, "att-nc1.json"), s1)
        a1 = NotesAuControle(c)
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(s1, attestation_lecture_humaine=att1, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", a1)])
        self.assertIn("avant tout envoi des fiches", str(cm.exception))
        self.assertEqual(a1.recu, [idn.APPEL_DE_CONTROLE_CONSIGNE])  # aucune fiche reçue : le message est vrai
        self.assertTrue(os.path.exists(os.path.join(s1, "bras-tentative-1.json")))
        self.assertFalse(os.path.exists(os.path.join(s1, "manifeste-bras-rapporte.json")))
        # contrôle non court (simulé) refusé : verrouillé comme un envoi
        c.lancer(ad, "nc2", budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
        s2 = os.path.join(self.tmp, "nc2")
        att2 = self.cmd().attester(os.path.join(self.tmp, "att-nc2.json"), s2)
        with open(os.path.join(s2, "juges-bras-rapporte", "traces-argon", "consigne-en-attente.md"), encoding="utf-8") as f:
            consigne_juge = f.read()
        a2 = NotesAuControle(c)
        long_controle = lambda supplement=None: idn.APPEL_DE_CONTROLE_CONSIGNE + "\n\n" + consigne_juge  # noqa: E731
        with unittest.mock.patch.object(idn, "consigne_de_controle", long_controle):
            with self.assertRaises(idn.SansJugeExterne) as cm:
                idn.executer_bras_differe(s2, attestation_lecture_humaine=att2, budgets=budgets,
                                          juges_externes=[("argon", "autre-lignee-x", a2)])
        self.assertIn("CL41-04", str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(s2, "bras-tentative-1.json")))
        with open(os.path.join(s2, "manifeste-bras-rapporte.json")) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertEqual(j["consigne_envoyee"], "argon")
        self.assertAlmostEqual(j["cout_total_usd"], 0.05)
        self.assertTrue(idn.verifier_scelle(os.path.join(s2, "classement-sans-bras.json")))
        with self.assertRaises(idn.CourseInterrompue) as cm:  # verrouillé
            idn.executer_bras_differe(s2, attestation_lecture_humaine=att2, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", Enregistreur(c))])
        self.assertIn("déjà été joué", str(cm.exception))

    # --- CL41-05 ---------------------------------------------------------------------------------------------------------

    def test_cl41_05_relancable_relais_garde_et_relance_a_neuf(self):
        """CL41-05 (sonde de CL8) : total 41, relais 41 (réserve 4), contrôles Claude 0,4 : `relancable` faux dans
        l'hypothèse « relais gardé » (écrite au motif) ; le second calcul « relais relancé à neuf » dit la relance possible.
        Relais trop petit même à neuf : les deux faux."""
        lanceur = self.v41().lanceur()
        budgets = dict(lanceur.BUDGETS_PAR_DEFAUT)
        juges = [("juge-opus", "claude-opus-5-5"), ("juge-fable", "claude-fable-5-1")]
        verif = {"somme_claude": 40.0, "somme_externe": 11.2}
        relais = {"plafond_usd": 41.0, "reserve_par_appel_usd": 4.0, "depense_usd": 0.0}
        ok, motifs, neuf = lanceur.relance_possible(1, verif, 0.4, 0.15, 41.0, 11.6, False, False, True, relais, budgets, juges,
                                                    details=True)
        self.assertFalse(ok)
        self.assertEqual(len(motifs), 1)
        self.assertIn("relais gardé (hypothèse) : 36.6000", motifs[0])
        self.assertIn("relais relancé à neuf (devis, point 4) : 37.0000 ≥ 37.0000", motifs[0])
        self.assertTrue(neuf["relancable"], neuf)
        self.assertEqual(lanceur.relance_possible(1, verif, 0.4, 0.15, 41.0, 11.6, False, False, True, relais, budgets, juges),
                         (ok, motifs))  # forme de la v41 gardée sans `details`
        petit = dict(relais, plafond_usd=39.0)
        ok2, motifs2, neuf2 = lanceur.relance_possible(1, verif, 0.4, 0.15, 41.0, 11.6, False, False, True, petit, budgets,
                                                       juges, details=True)
        self.assertFalse(ok2 or neuf2["relancable"])
        self.assertNotIn("la garde du relais accepterait", motifs2[0])

    def test_v34_relais_lu_avec_le_cout_claude_de_la_tentative(self):
        """CL41-08 (V34) : le calcul du relais retire le coût Claude de la tentative (plafond 40,2, réserve 4 : 36,2 − 0,4 =
        35,8 < 36 → faux ; sans ce coût, 36,2 ≥ 36 l'aurait dit vrai)."""
        lanceur = self.v41().lanceur()
        budgets = dict(lanceur.BUDGETS_PAR_DEFAUT)
        juges = [("juge-opus", "claude-opus-5-5"), ("juge-fable", "claude-fable-5-1")]
        verif = {"somme_claude": 30.0, "somme_externe": 11.2}
        relais = {"plafond_usd": 40.2, "reserve_par_appel_usd": 4.0, "depense_usd": 0.0}
        ok, motifs = lanceur.relance_possible(1, verif, 0.4, 0.0, 40.0, 11.6, False, False, True, relais, budgets, juges)
        self.assertFalse(ok)
        self.assertIn("35.8000", motifs[0])
        self.assertTrue(lanceur.relance_possible(1, verif, 0.0, 0.0, 40.0, 11.6, False, False, True, relais, budgets, juges)[0])

    # --- CL41-06 ---------------------------------------------------------------------------------------------------------

    def test_cl41_06_interruption_avant_le_manifeste_de_depart(self):
        """CL41-06 (S12, `lanceur_fenetre.py` de CL8) : interruption au moment d'écrire le manifeste de départ → aucune SORTIE
        (dossier provisoire retiré), tentative scellée relançable, et la relance passe (v41 : SORTIE vide laissée,
        « relançable » puis relance refusée « SORTIE existe déjà »). Au lanceur, une SORTIE créée sans manifeste de départ
        rend `relancable` faux, motif nommé."""
        import glob
        import unittest.mock
        v41 = self.v41()
        prep = self.cours().preparer()
        ok = " ".join(self.cmd().commande(self.cmd().SCRIPT_OK))
        sortie = os.path.join(self.tmp, "l-fenetre")
        argv = v41.base(sortie, prep, None, "--commande-externe", ok)
        vrai = idn.manifeste

        def manifeste_coupe(**k):
            if k.get("phase") == "depart":
                raise KeyboardInterrupt("signal 15 (simulé entre la création de SORTIE et le manifeste de départ)")
            return vrai(**k)
        with unittest.mock.patch.object(idn, "manifeste", manifeste_coupe):
            code, out, err = v41.principal(v41.lanceur(), argv)
        self.assertEqual(code, 2, err)
        self.assertFalse(os.path.exists(sortie))  # v41 : SORTIE vide
        self.assertEqual(glob.glob(sortie + ".depart-en-cours-*"), [])
        with open(os.path.join(sortie + "-controle", "tentative-1.json")) as f:
            r = json.load(f)["reglages"]
        self.assertTrue(r["relancable"], r["motifs_relance"])
        code, out, err = v41.principal(v41.lanceur(), argv)
        self.assertEqual(code, 0, err)  # v41 : 2, « SORTIE existe déjà »
        # au lanceur : SORTIE sans manifeste de départ → relancable faux
        lanceur = v41.lanceur()
        sortie2 = os.path.join(self.tmp, "l-fenetre-2")

        def coeur_coupe(adaptateur, s, **k):
            os.makedirs(s)
            raise KeyboardInterrupt("signal 15")
        with unittest.mock.patch.object(lanceur.idn, "executer_ideation", coeur_coupe):
            code, out, err = v41.principal(lanceur, v41.base(sortie2, prep, None, "--commande-externe", ok))
        self.assertEqual(code, 2)
        with open(os.path.join(sortie2 + "-controle", "tentative-1.json")) as f:
            r = json.load(f)["reglages"]
        self.assertFalse(r["relancable"])
        self.assertTrue(any("sans manifeste de départ" in m for m in r["motifs_relance"]), r["motifs_relance"])
        self.assertFalse(r["relance_relais_relance_a_neuf"]["relancable"])

    # --- CL41-07 ---------------------------------------------------------------------------------------------------------

    def test_cl41_07_panne_d_argon_au_controle_ne_coute_rien_chez_claude(self):
        """CL41-07 : réglages du devis, contrôles Claude payés (0,2 chacun) ; Argon rend « KO » à 0,15 au contrôle, joué en
        premier : aucun contrôle Claude, tentative à 0 côté Claude, relançable (11,2 + 0,15 ≤ 11,6) ; la relance part
        (v41 : 0,4 Claude dépensés, plus de relance)."""
        v41 = self.v41()
        prep, att = v41.prep_devis()
        journal = os.path.join(self.tmp, "ko-07.log")
        ko = v41.script(v41.SCRIPT_KO % journal, "ko-07.py")
        sortie = os.path.join(self.tmp, "l-07")
        code, out, err = v41.principal(v41.lanceur(cout_controle_claude=0.2), v41.base(sortie, prep, att, "--commande-externe", ko))
        self.assertEqual(code, 2)
        with open(os.path.join(sortie + "-controle", "tentative-1.json")) as f:
            r = json.load(f)["reglages"]
        self.assertEqual(r["cout_claude_usd"], 0.0)  # v41 : 0,4
        self.assertAlmostEqual(r["cout_externe_usd"], 0.15)
        self.assertEqual(sorted(r["lectures"]), ["externe:argon"])
        self.assertFalse(os.path.exists(os.path.join(sortie + "-controle", "tentative-1")))  # aucun dossier de contrôle Claude
        self.assertTrue(r["relancable"], r["motifs_relance"])
        argon = v41.script(v41.SCRIPT_PLAFOND, "argon-plafond-07.py")
        code, out, err = v41.principal(v41.lanceur(cout_controle_claude=0.2), v41.base(sortie, prep, att, "--commande-externe", argon))
        self.assertIn(code, (0, 4), err)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            d = json.load(f)["reglages"]
        self.assertAlmostEqual(d["cout_externe_deja_engage_usd"], 0.15 + 2.5)
        self.assertAlmostEqual(d["cout_deja_engage_usd"], 0.4)

    # --- CL41-08 ---------------------------------------------------------------------------------------------------------

    def test_n03_meme_controle_du_bras_au_lanceur_et_au_coeur(self):
        """CL41-08 (N03) : `verifier_reglages` reçoit le même contrôle du bras que le cœur (0,2 par défaut, 0,1 donné) ; une
        somme externe qui ne tient qu'avec un contrôle du bras à 0 (11,1 < 11,2) est refusée avant tout contrôle."""
        import unittest.mock
        v41 = self.v41()
        prep, att = v41.prep_devis()
        argon = v41.script(v41.SCRIPT_PLAFOND, "argon-n03.py")
        vus = {"reglages": [], "coeur": []}
        vrai_v, vrai_c = idn.verifier_reglages, idn.executer_ideation

        def espion_v(**k):
            vus["reglages"].append(k["budget_controle_bras_usd"])
            return vrai_v(**k)

        def espion_c(*a, **k):
            vus["coeur"].append(k["budget_controle_bras_usd"])
            return vrai_c(*a, **k)
        for n, options, attendu in ((1, [], 0.2), (2, ["--budget-controle-usd", "0.1", "--budget-externe-usd", "11.1"], 0.1)):
            with unittest.mock.patch.object(idn, "verifier_reglages", espion_v), \
                    unittest.mock.patch.object(idn, "executer_ideation", espion_c):
                code, out, err = v41.principal(v41.lanceur(), v41.base(os.path.join(self.tmp, f"l-n03-{n}"), prep, att,
                                                                        "--commande-externe", argon, *options))
            self.assertIn(code, (0, 4), err)
            self.assertEqual((vus["reglages"][-1], vus["coeur"][-1]), (attendu, attendu))
        sortie = os.path.join(self.tmp, "l-n03-refus")
        journal = os.path.join(self.tmp, "n03.log")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe",
                                                                v41.script(v41.SCRIPT_KO % journal, "ko-n03.py"),
                                                                "--budget-externe-usd", "11.1"))
        self.assertEqual(code, 2)
        self.assertIn("somme des plafonds externes 11.20 > total externe 11.1", err)
        self.assertFalse(os.path.exists(sortie + "-controle"))
        self.assertFalse(os.path.exists(journal))

    SCRIPT_CTRL = ("import sys, json, os\nc = sys.stdin.read()\nopen(%r, 'a').write('appel\\n')\n"
                   "if c.startswith('Réponds exactement OK'): print(json.dumps({'texte': %r, 'cout_usd': %s})); sys.exit(0)\n")

    def test_n04_n07_n08_couts_des_tentatives_precedentes(self):
        """CL41-08 (N04, N07, N08) : deux tentatives payées (Claude 0,02 et Argon 0,3 ; puis Argon 2,5) ; la relance sous un
        total externe juste est refusée avant tout contrôle ; ensuite la course part et son manifeste de départ porte les
        coûts imputés, comme le journal du cœur. **Changé en v43** (CL40-01, option c, décision de Lazar) : la troisième
        tentative reprend le contrôle d'Argon réussi en tentative 1 (même commande, même consigne) et le premier contrôle
        Claude ; elle ne rejoue que le contrôle Claude « KO » — somme externe de la relance 0,3 + 2,5 + 0 + 6,2 = 9,0 (refusée
        sous 8,9 ; v42 : 11,5, refusée sous 11,4) ; `cout_deja_engage_usd` = 0,02 + 0,01 (v42 : 0,04) et
        `cout_externe_deja_engage_usd` = 0,3 + 2,5 (v42 : 3,1) ; contrôles repris écrits au manifeste et au journal."""
        v41 = self.v41()
        prep = self.cours().preparer()
        journal = os.path.join(self.tmp, "n04.log")
        suite_ok = self.cmd().SCRIPT_OK.split("\n", 2)[2]  # passes et juge du script commun (la consigne est déjà lue)
        argon_ok = v41.script((self.SCRIPT_CTRL % (journal, "OK", "0.3")).replace("c = sys.stdin.read()", "consigne = c = sys.stdin.read()")
                              .replace("import sys, json, os", "import sys, json, os, re") + suite_ok, "argon-n04-ok.py")
        argon_ko = v41.script(self.SCRIPT_CTRL % (journal, "KO", "float(os.environ['PLAFOND_SESSION_USD'])"), "argon-n04-ko.py")
        sortie = os.path.join(self.tmp, "l-n04")

        def argv(commande, total):
            return v41.base(sortie, prep, None, "--commande-externe", commande, "--budget-externe-usd", total)
        code, _, err = v41.principal(v41.lanceur(cout_controle_claude=0.01, ko_claude="claude-opus-5-5"), argv(argon_ok, "11.5"))
        self.assertEqual(code, 2, err)
        code, _, err = v41.principal(v41.lanceur(cout_controle_claude=0.01), argv(argon_ko, "11.5"))
        self.assertEqual(code, 2, err)
        t = [json.loads(_lire(os.path.join(sortie + "-controle", f"tentative-{n}.json")))["reglages"] for n in (1, 2)]
        self.assertEqual([(round(x["cout_claude_usd"], 6), round(x["cout_externe_usd"], 6)) for x in t], [(0.02, 0.3), (0.0, 2.5)])
        n = len(_lire(journal).splitlines())
        code, _, err = v41.principal(v41.lanceur(cout_controle_claude=0.01), argv(argon_ok, "8.9"))
        self.assertEqual(code, 2)
        self.assertIn("somme des plafonds externes 9.00 > total externe 8.9", err)  # N04 (v42 : 11.50 > 11.4)
        self.assertEqual(len(_lire(journal).splitlines()), n)
        self.assertFalse(os.path.exists(os.path.join(sortie + "-controle", "tentative-3.json")))
        code, _, err = v41.principal(v41.lanceur(cout_controle_claude=0.01), argv(argon_ok, "11.5"))
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            d = json.load(f)["reglages"]
        self.assertAlmostEqual(d["cout_deja_engage_usd"], 0.03)  # N08 (v42 : 0,04, le contrôle réussi rejoué)
        self.assertAlmostEqual(d["cout_externe_deja_engage_usd"], 2.8)  # N07 (v42 : 3,1)
        self.assertAlmostEqual(d["somme_des_plafonds"]["externe_avec_controle_du_bras"], 2.8 + 2.5 + 3.5 + 0.2)
        repris = d["versions"]["controles_repris"]
        self.assertEqual(sorted(repris), ["claude-fable-5-1", "externe:argon"])
        self.assertEqual({v["repris_de_tentative"] for v in repris.values()}, {1})
        self.assertEqual(repris["externe:argon"]["sha256_tentative"],
                         idn.sha256_fichier(os.path.join(sortie + "-controle", "tentative-1.json")))
        self.assertEqual(sorted(d["versions"]["appel_de_controle"]), ["claude-opus-5-5"])
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertAlmostEqual(j["cout_appels_de_controle_usd"], 0.03)
        self.assertAlmostEqual(j["cout_appels_de_controle_externes_usd"], 2.8)
        self.assertAlmostEqual(j["cout_externe_usd"], 2.8 + 0.25)
        self.assertEqual(j["controles_repris"], repris)

    def test_v12_relancable_avec_le_cout_externe_de_la_tentative(self):
        """CL41-08 (V12) : réglages du devis, seul le coût externe de la tentative fait dépasser — Argon « KO » à 0,5 :
        somme externe de la relance 11,7 > 11,6, `relancable` faux ; à 0,15 : vrai."""
        v41 = self.v41()
        prep, att = v41.prep_devis()
        for cout, attendu in ((0.5, False), (0.15, True)):
            journal = os.path.join(self.tmp, f"v12-{cout}.log")
            ko = v41.script(self.SCRIPT_CTRL % (journal, "KO", repr(cout)), f"ko-v12-{cout}.py")
            sortie = os.path.join(self.tmp, f"l-v12-{cout}")
            code, _, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe", ko))
            self.assertEqual(code, 2)
            with open(os.path.join(sortie + "-controle", "tentative-1.json")) as f:
                r = json.load(f)["reglages"]
            self.assertEqual(r["cout_claude_usd"], 0.0)
            self.assertEqual(r["relancable"], attendu, r["motifs_relance"])
            if not attendu:
                self.assertEqual(r["motifs_relance"], ["somme des plafonds externes de la relance 11.7000 > total externe 11.6"])

    def test_v20_tentative_du_bras_scellee_au_cout_non_fini(self):
        """CL41-08 (V20, S13 de CL8) : une `bras-tentative` **scellée** au coût NaN, −2,5 ou `true` est refusée avant tout
        appel."""
        c = self.cours()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = 1.0
        for i, valeur in enumerate(("NaN", "-2.5", "true")):
            nom = f"v20-{i}"
            c.lancer(ad, nom, budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=2.0)
            sortie = os.path.join(self.tmp, nom)
            att = self.cmd().attester(os.path.join(self.tmp, f"att-{nom}.json"), sortie)
            idn.ecrire_scelle(os.path.join(sortie, "bras-tentative-1.json"),
                              '{"reglages": {"journal": {"cout_total_usd": %s}}}' % valeur)
            bon = Enregistreur(c)
            with self.subTest(cout=valeur), self.assertRaises(idn.CourseInterrompue) as cm:
                idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                          juges_externes=[("argon", "autre-lignee-x", bon)])
            self.assertIn("coût illisible", str(cm.exception))
            self.assertEqual(bon.recu, [])


class TestV43(CasAvecDossier):
    """v43 (contre-lecture CL9 de la v42 ; choix de session-depot, message n° 156) : garde de la course sur le plus petit
    plafond des sessions d'Argon, provision de sortie, passe gardée avant son envoi (CL42-01) ; garde propre au bras, refus
    de taille compté et classé, chaîne lanceur → manifeste → bras (CL42-05, W07) ; échec du classement de repli dit et
    scellé, second repli sans écrasement (CL42-06, S14, W36) ; NaN au bras sur une SORTIE fraîche, phrase de la borne,
    refus pour taille par proposeur (CL42-07, W30, W35b) ; mesure des consignes sans appel (CL42-03)."""

    def v41(self):
        t = TestV41("test_ecrits_du_lanceur")
        t.tmp = self.tmp
        return t

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def cmd(self):
        c = TestCommandeExterne("test_commande_factice_notes_et_controle")
        c.tmp = self.tmp
        return c

    def journal_de(self, chemin):
        if not os.path.exists(chemin):
            return []
        return [json.loads(l) for l in _lire(chemin).splitlines() if l.strip()]

    def prep(self):
        """Pièces, question, matériau et témoins des essais, préparés une fois par essai (liste blanche jamais écrasée)."""
        if not hasattr(self, "_prep_base"):
            self._prep_base = self.cours().preparer()
        return self._prep_base

    def argon_journal(self, journal, nom):
        """Le script commun (`SCRIPT_OK`) qui consigne chaque appel : taille, contrôle, passe 2."""
        script = self.cmd().SCRIPT_OK.replace(
            "consigne = sys.stdin.read()\n",
            "consigne = sys.stdin.read()\nopen(%r, 'a').write(json.dumps({'taille': len(consigne), 'controle': "
            "'exactement OK' in consigne, 'passe2': 'première passe' in consigne}) + '\\n')\n" % journal, 1)
        return self.v41().script(script, nom)

    # Argon factice au tarif donné (dollars par caractère d'entrée et de sortie), coût jamais borné à son plafond ;
    # chaque appel consigné (CL9 : « tarif_tout »)
    SCRIPT_TARIF = (
        "import sys, json, os, re\nc = sys.stdin.read()\nctrl = c.startswith('Réponds exactement OK')\n"
        "def sortir(t):\n"
        "    cout = len(c) * %r + len(t) * %r\n"
        "    open(%r, 'a').write(json.dumps({'taille': len(c), 'controle': ctrl, 'role': os.environ['ROLE_POLE'], "
        "'cout': cout}) + '\\n')\n"
        "    print(json.dumps({'texte': t, 'cout_usd': cout})); sys.exit(0)\n"
        "if ctrl: sortir('OK')\n"
        "if os.environ['ROLE_POLE'] == 'proposeur_ideation':\n"
        "    f1 = json.loads(%r); f2 = dict(f1, nom='Argon B')\n"
        "    sortir('```json\\n' + json.dumps({'fiches': [f1, f2]}, ensure_ascii=False) + '\\n```')\n"
        "bloc = json.loads(re.search(r'```json\\n(\\[.*\\])\\n```', c, re.S).group(1))\n"
        "notes = [{'identifiant': f['identifiant'], 'criteres': {x: 2 for x in ('avantage', 'originalite', 'falsifiabilite', "
        "'traitabilite', 'robustesse')}, 'justifications': {}} for f in bloc]\n"
        "sortir('```json\\n' + json.dumps({'notes': notes, 'doublons': []}) + '\\n```')\n")

    def prep_grand(self):
        """Réglages du devis (CL9, § 4) : pièce de 750 000 caractères, matériau de 350 000, question de 19 caractères,
        témoins des essais, matériau attesté."""
        prep = self.prep()
        p = os.path.join(self.tmp, "piece-grande.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(("# Pièce A\n" + "Texte de contexte. " * 40_000)[:750_000])
        m = os.path.join(self.tmp, "materiau-grand.md")
        with open(m, "w", encoding="utf-8") as f:
            f.write(("# Matériau\n" + "Tour interne. " * 26_000)[:350_000])
        lb = os.path.join(self.tmp, "liste-blanche-grande.json")
        idn.construire_liste_blanche([p, m, prep["question"], prep["temoins"]], lb)
        att = os.path.join(self.tmp, "att-materiau-grand.json")
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-29",
                                     "materiau_sha256": {"materiau-grand.md": idn.sha256_fichier(m)}})
        return dict(prep, liste_blanche=lb, pieces=[p], materiau=[m]), att

    def prep_piece_juge(self, taille=200_000):
        prep = self.prep()
        pj = os.path.join(self.tmp, "piece-juge.md")
        with open(pj, "w", encoding="utf-8") as f:
            f.write("# Antériorité\n" + ("Résumé d'article. " * 20000)[:taille])
        lb = os.path.join(self.tmp, "liste-blanche-pj.json")
        idn.construire_liste_blanche([prep["pieces"][0], prep["question"], prep["materiau"][0], prep["temoins"], pj], lb)
        return dict(prep, liste_blanche=lb), pj

    def course_bras(self, nom, juge_budget=1.0, budget_externe=2.0):
        """Course (cœur, faux adaptateur Claude) avec un juge externe différé ; rend (cours, sortie, attestation, budgets)."""
        c = self.cours()
        c._prep = self.prep()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("juge_ideation", "autre-lignee-x")] = juge_budget
        c.lancer(ad, nom, budgets=budgets, juges_externes=[("argon", "autre-lignee-x")], budget_externe_usd=budget_externe)
        sortie = os.path.join(self.tmp, nom)
        att = self.cmd().attester(os.path.join(self.tmp, f"att-{nom}.json"), sortie)
        return c, sortie, att, budgets

    # --- CL42-01 ---------------------------------------------------------------------------------------------------------

    def test_cl42_01_controle_releve_seul_refuse_sans_depense_et_garde_donnee_passe(self):
        """CL42-01 (D-a-devis de CL9) : réglages du devis (pièce 750 000, matériau 350 000, huit fiches, seconde passe),
        `--budget-controle-externe-usd 3.0 --budget-externe-usd 12.1` seuls → **refus sans dépense** : la garde reste à
        1 000 000 − 480 000 = 520 000 (la passe d'Argon reste à 2,5, provision de huit fiches de 12 000 au rapport 5),
        refus scellé, ni Argon (au tarif du devis) ni Claude appelés (v42 : garde 1 200 000, contrôle payé 2,73, course
        perdue après la passe 2 d'Argon à 2,51 > 2,5). Au prix de 8,3 dollars par million de jetons
        (`--prix-entree-usd-par-million-jetons`, CL42-04 b) : garde 1 204 819 − 480 000 = 724 819, refus aussi ; prix nul ou
        non fini refusé. Cas sain : `--taille-max-consigne-externe 1500000` donné (le contrôle fait ≈ 1 457 000 caractères
        depuis que la borne de fiche est retirée, CL42-04), Argon au pire cas (chaque session à son plafond) → course et bras
        passent, classement à trois juges ; les deux passes d'Argon gardées par le cœur avant leur envoi contre la taille
        donnée.
        v44 (CL43-02, changé) : la taille donnée ne désarme plus la garde propre de chaque passe (plafond moins la provision
        de huit fiches de 8 000) ; au prix 10 et passes à 2,5, la passe 1 (752 445) serait refusée avant tout contrôle
        (680 000) : le cas sain passe aux réglages (β) (prix 8,3, contrôle 3,1, passe 2 à 3,1, externe 12,8), gardes
        884 819 et 1 173 975 (v43 : 1 500 000 et 1 500 000)."""
        self.assertEqual(idn.provision_sortie_caracteres(8), 480_000)
        self.assertEqual(idn.taille_max_consigne_course_par_defaut(3.0, [2.5], 8)[0], 520_000)
        self.assertEqual(idn.taille_max_consigne_course_par_defaut(2.5, [2.5], 8)[0], 520_000)
        self.assertEqual(idn.taille_max_consigne_course_par_defaut(2.5, [3.7], 8)[0], 1_000_000)  # contrôle, entrée seule
        self.assertEqual(idn.taille_max_consigne_course_par_defaut(2.5, [1.0], 8)[0], 0)  # jamais négatif
        v41 = self.v41()
        prep, att = self.prep_grand()
        journal = os.path.join(self.tmp, "argon-devis.jsonl")
        devis = v41.script(self.SCRIPT_TARIF % (2.5 / 1.1e6, 0.0, journal, TestCommandeExterne.FICHE), "argon-devis.py")
        sortie = os.path.join(self.tmp, "l-devis-a")
        code, out, err = v41.principal(v41.lanceur(cout_controle_claude=0.2), v41.base(
            sortie, prep, att, "--commande-externe", devis, "--budget-controle-externe-usd", "3.0", "--budget-externe-usd", "12.1"))
        self.assertEqual(code, 2, err)
        self.assertIn("garde de taille", err)
        self.assertEqual(self.journal_de(journal), [])  # Argon jamais appelé (v42 : contrôle 2,73, passes 1,71 et 2,51)
        r = os.path.join(sortie + "-controle", "refus-taille-1.json")
        self.assertTrue(idn.verifier_scelle(r))
        with open(r) as f:
            g = json.load(f)["reglages"]
        self.assertEqual((g["garde_taille"]["taille_max_caracteres"], g["cout_usd"], g["tentative_comptee"]), (520_000, 0.0, False))
        self.assertEqual(g["garde_taille"]["provision_sortie_caracteres"], 480_000)
        self.assertGreater(g["garde_taille"]["taille_caracteres"], 1_199_000)
        self.assertIn("passe du proposeur externe 2.5", g["garde_taille"]["origine_taille_max"])
        self.assertEqual(sorted(os.listdir(sortie + "-controle")), ["refus-taille-1.json", "refus-taille-1.json.sha256"])
        self.assertFalse(os.path.exists(sortie))  # aucun contrôle Claude, aucune SORTIE
        # CL42-04 b : prix d'entrée du devis (8,3 dollars par million de jetons) — garde plus haute, refus quand même
        code, out, err = v41.principal(v41.lanceur(cout_controle_claude=0.2), v41.base(
            sortie, prep, att, "--commande-externe", devis, "--prix-entree-usd-par-million-jetons", "8.3"))
        self.assertEqual(code, 2, err)
        with open(os.path.join(sortie + "-controle", "refus-taille-2.json")) as f:
            g2 = json.load(f)["reglages"]["garde_taille"]
        self.assertEqual((g2["taille_max_caracteres"], g2["prix_entree_usd_par_million_jetons"]), (724_819, 8.3))
        self.assertAlmostEqual(g2["cout_prudent_entree_usd"], round(g2["taille_caracteres"] * 8.3e-6 / 4, 4))
        self.assertEqual(self.journal_de(journal), [])
        import contextlib
        import io
        for prix in ("0", "nan", "-1"):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                v41.lanceur().principal(v41.base(sortie, prep, att, "--prix-entree-usd-par-million-jetons", prix))
        # cas sain : garde donnée explicitement, Argon au pire cas → course puis bras, classement à trois juges
        argon = v41.script(v41.SCRIPT_PLAFOND, "argon-plafond-43.py")
        sortie2 = os.path.join(self.tmp, "l-devis-c")
        code, out, err = v41.principal(v41.lanceur(), v41.base(
            sortie2, prep, att, "--commande-externe", argon, "--taille-max-consigne-externe", "1500000",
            "--prix-entree-usd-par-million-jetons", "8.3", "--budget-controle-externe-usd", "3.1",
            "--budget-passe-2-externe-usd", "3.1", "--budget-externe-usd", "12.8"))
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie2, "manifeste-depart.json")) as f:
            v = json.load(f)["reglages"]["versions"]
        self.assertEqual((v["taille_max_consigne_externe"]["valeur"], v["taille_max_consigne_externe"]["origine"]),
                         (1_500_000, "option"))
        self.assertGreater(v["marge_controle_externe"]["taille_consigne_de_controle"], 1_450_000)  # CL42-04 : borne retirée
        with open(os.path.join(sortie2, "manifeste-fin.json")) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertEqual([(x["passe"], x["taille_max_caracteres"], x["refusee"]) for x in j["gardes_taille_sessions"]],
                         [(1, 884_819, False), (2, 1_173_975, False)])  # v43 : 1 500 000 deux fois
        self.assertGreater(j["gardes_taille_sessions"][1]["taille_caracteres"], 1_100_000)
        att_b = self.cmd().attester(os.path.join(self.tmp, "att-devis-c.json"), sortie2, "argon-j")
        code, out, err = v41.principal(v41.lanceur(), [sortie2, "--bras-rapporte-differe", "--attestation-lecture-humaine", att_b,
                                                       "--juge-externe", "argon-j=gemini-argon", "--commande-externe", argon])
        self.assertIn(code, (0, 4), err)
        with open(os.path.join(sortie2, "classement.json")) as f:
            self.assertTrue(all(l["nombre_juges"] == 3 for l in json.load(f)["lignes"]))

    def test_cl42_01_passe_gardee_contre_son_propre_plafond_avant_envoi(self):
        """CL42-01 : `garder_sessions_externes` (donné par le lanceur) — chaque passe d'un proposeur externe est gardée
        avant son envoi contre son propre plafond / prix prudent moins la provision de sortie ; un plafond qui tient la
        passe 1 et pas la passe 2 → passe 2 **non envoyée**, rien payé pour elle, aucune passe Claude, manifeste de fin
        en erreur, gardes au journal (v42 : aucune garde dans le cœur, la passe 2 part). Cas sain : plafond 2,5 → les deux
        passes gardées et jouées.
        v44 (CL43-02, changé) : provision de huit fiches de 8 000 (`TAILLE_FICHE_PROVISIONNEE_PASSE`) au lieu de 12 000 :
        320 000 au lieu de 480 000 ; cas sain 680 000 au lieu de 520 000."""
        c = self.cours()
        prep = self.prep()
        c._prep = prep
        att = os.path.join(self.tmp, "att-p2.json")
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-29", "materiau_sha256": {
            os.path.basename(prep["materiau"][0]): idn.sha256_fichier(prep["materiau"][0])}})
        liste = idn.charger_liste_blanche(prep["liste_blanche"])
        passe1 = len(idn.consigne_proposeur(idn.lire_pieces(prep["pieces"], liste), 8,
                                            idn.lire_pieces([prep["question"]], liste)[0][1]))
        recu = []

        class Argon:
            nom = "argon-simule"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                recu.append((os.path.basename(dossier), len(consigne)))
                fiches = [fiche_brute(nom="Argon A"), fiche_brute(nom="Argon B")]
                return Resultat("```json\n" + json.dumps({"fiches": fiches}, ensure_ascii=False) + "\n```", [], 0.1, "ok")
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = (320_000 + passe1 + 50) * idn.PRIX_CARACTERE_PRUDENT_USD
        args = dict(budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", Argon())], budget_externe_usd=5.0,
                    seconde_passe=True, attestation_materiau=att, garder_sessions_externes=True)
        with self.assertRaises(idn.TailleConsigneRefusee) as cm:
            c.lancer(ad, "c-p2", **args)
        self.assertIn("rien payé", str(cm.exception))
        self.assertEqual([d for d, _ in recu], ["passe-1"])  # la passe 2 n'est jamais partie
        self.assertEqual(ad.appels, [])  # aucune passe Claude
        sortie = os.path.join(self.tmp, "c-p2")
        self.assertFalse(os.path.exists(os.path.join(sortie, "proposeurs", "argon", "passe-2")))
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            fin = json.load(f)["reglages"]
        self.assertIn("garde de taille", fin["erreur"])
        g = fin["journal"]["gardes_taille_sessions"]
        self.assertEqual([(x["passe"], x["refusee"]) for x in g], [(1, False), (2, True)])
        self.assertEqual((g[1]["taille_max_caracteres"], g[1]["provision_sortie_caracteres"]), (passe1 + 50, 320_000))
        self.assertGreater(g[1]["taille_caracteres"], passe1 + 50)
        self.assertAlmostEqual(fin["journal"]["cout_externe_usd"], 0.1)  # la passe 1 seule
        # cas sain
        budgets[("proposeur_ideation", "gemini-argon")] = 2.5
        res = c.lancer(ad, "c-p2-ok", **args)
        self.assertEqual([(x["passe"], x["taille_max_caracteres"], x["refusee"]) for x in res["journal"]["gardes_taille_sessions"]],
                         [(1, 680_000, False), (2, 680_000, False)])  # v43 : 520 000

    # --- CL42-05 et W07 --------------------------------------------------------------------------------------------------

    def test_cl42_05_garde_du_bras_de_bout_en_bout_par_le_lanceur(self):
        """CL42-05, W07 : `--taille-max-consigne-externe 150000` donné au lanceur (consigné « option » au manifeste de
        départ, et appliqué aux passes d'Argon), puis bras **sans option** : la consigne du juge (≈ 210 000 caractères,
        pièce de juge de 200 000) passe sous la garde propre du bras (plafond du juge 3,5 / prix prudent moins la
        provision de sortie des fiches servies) → classement à trois juges (v42 : refus « donnée à la course »). Avec
        `--taille-max-consigne-externe-bras 1000` : code 5, refus scellé compté comme tentative non relançable, classement
        sans bras écrit, Argon jamais appelé ; la relance sans option se joue en tentative 2. Options croisées refusées."""
        import contextlib
        import io
        v41 = self.v41()
        prep, pj = self.prep_piece_juge()
        journal = os.path.join(self.tmp, "argon-w07.jsonl")
        argon = self.argon_journal(journal, "argon-w07.py")
        sortie = os.path.join(self.tmp, "l-w07")
        course = v41.base(sortie, prep, None, "--commande-externe", argon, "--piece-juge", pj,
                          "--taille-max-consigne-externe", "150000")
        code, out, err = v41.principal(v41.lanceur(), course)
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            v = json.load(f)["reglages"]["versions"]
        self.assertEqual((v["taille_max_consigne_externe"]["valeur"], v["taille_max_consigne_externe"]["origine"]),
                         (150_000, "option"))  # W07 : origine écrite par le lanceur
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            j = json.load(f)["reglages"]["journal"]
        self.assertEqual([(x["passe"], x["taille_max_caracteres"]) for x in j["gardes_taille_sessions"]], [(1, 150_000)])
        att = self.cmd().attester(os.path.join(self.tmp, "att-w07.json"), sortie, "argon-j")
        bras = [sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine", att, "--juge-externe", "argon-j=gemini-argon",
                "--commande-externe", argon]
        code, out, err = v41.principal(v41.lanceur(), bras)
        self.assertEqual(code, 0, err)  # v42 : 2, « donnée à la course »
        with open(os.path.join(sortie, "manifeste-bras-rapporte.json")) as f:
            gb = json.load(f)["reglages"]["journal"]["garde_taille"]["argon-j"]
        with open(os.path.join(sortie, "noyau", "cles-anonymisation-par-juge.json")) as f:
            servies = len(json.load(f)["argon-j"])
        self.assertEqual(gb["taille_max_caracteres"], 1_400_000 - servies * 10_000)
        self.assertTrue(gb["origine_taille_max"].startswith("défaut : plafond de la session du juge 3.5"))
        self.assertGreater(gb["taille_caracteres"], 200_000)
        with open(os.path.join(sortie, "classement.json")) as f:
            self.assertTrue(all(l["nombre_juges"] == 3 for l in json.load(f)["lignes"]))
        # option propre au bras : refus compté, classement sans bras, Argon jamais appelé
        sortie_b = os.path.join(self.tmp, "l-w07-b")
        code, out, err = v41.principal(v41.lanceur(), [sortie_b] + course[1:])
        self.assertEqual(code, 0, err)
        att_b = self.cmd().attester(os.path.join(self.tmp, "att-w07-b.json"), sortie_b, "argon-j")
        bras_b = [sortie_b] + bras[1:3] + [att_b] + bras[4:]
        n = len(self.journal_de(journal))
        code, out, err = v41.principal(v41.lanceur(), bras_b + ["--taille-max-consigne-externe-bras", "1000"])
        self.assertEqual(code, 5, err)
        self.assertIn("classement-sans-bras.json", err)
        self.assertEqual(len(self.journal_de(journal)), n)
        r = os.path.join(sortie_b, "manifeste-bras-refus-taille-1.json")
        self.assertTrue(idn.verifier_scelle(r))
        with open(r) as f:
            g = json.load(f)["reglages"]
        self.assertEqual((g["garde_taille"]["taille_max_caracteres"], g["tentative_comptee"], g["relancable"], g["cout_usd"]),
                         (1000, True, False, 0.0))
        cl = os.path.join(sortie_b, "classement-sans-bras.json")
        self.assertTrue(idn.verifier_scelle(cl))
        with open(cl) as f:
            self.assertTrue(all(l["nombre_juges"] == 2 for l in json.load(f)["lignes"]))
        self.assertFalse(os.path.exists(os.path.join(sortie_b, "manifeste-bras-rapporte.json")))
        for options in (bras_b + ["--taille-max-consigne-externe", "1000"],  # la valeur de la course ne vaut plus au bras
                        [os.path.join(self.tmp, "l-w07-c")] + course[1:] + ["--taille-max-consigne-externe-bras", "5"],
                        bras_b + ["--taille-max-consigne-externe-bras", "0"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as cm:
                v41.lanceur().principal(options)
            self.assertEqual(cm.exception.code, 2)
        code, out, err = v41.principal(v41.lanceur(), bras_b)  # relance sans option : tentative 2, jouée
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie_b, "manifeste-bras-rapporte.json")) as f:
            self.assertEqual(json.load(f)["reglages"]["journal"]["tentative"], 2)

    # --- CL42-06 (S14, W36) ---------------------------------------------------------------------------------------------

    def test_cl42_06_echec_du_classement_de_repli_dit_et_scelle(self):
        """CL42-06 (S14 de CL9) : trois bras « non joués » (commande introuvable) ; à la troisième, non relançable, le
        classement de repli échoue (`_classer` qui lève) → code 2, le motif est dans l'exception levée et sur la sortie
        d'erreur, et `classement-sans-bras-impossible-3.json` est scellé (v42 : rien, ni fichier ni message). Après envoi
        (juge en erreur), même échec : fichier scellé, manifeste du bras et exception le disent."""
        import unittest.mock
        v41 = self.v41()
        prep = self.prep()
        sortie = os.path.join(self.tmp, "l-s14")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, None, "--commande-externe",
                                                                " ".join(self.cmd().commande(self.cmd().SCRIPT_OK))))
        self.assertEqual(code, 0, err)
        att = self.cmd().attester(os.path.join(self.tmp, "att-s14.json"), sortie, "argon-j")
        bras = [sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine", att, "--juge-externe", "argon-j=gemini-argon",
                "--commande-externe", "/chemin/qui/n/existe/pas"]

        def panne(*a, **k):
            raise RuntimeError("panne simulée du classement de repli (disque plein)")
        for n in (1, 2):
            code, out, err = v41.principal(v41.lanceur(), bras)
            self.assertEqual(code, 2, err)
        with unittest.mock.patch.object(idn, "_classer", panne):
            code, out, err = v41.principal(v41.lanceur(), bras)
        self.assertEqual(code, 2, err)
        self.assertIn("classement sans bras impossible : RuntimeError : panne simulée", err)
        self.assertIn("classement_sans_bras_impossible", err)
        chemin = os.path.join(sortie, "classement-sans-bras-impossible-3.json")
        self.assertTrue(idn.verifier_scelle(chemin))  # v42 : absent
        with open(chemin) as f:
            r = json.load(f)["reglages"]
        self.assertIn("panne simulée", r["classement_sans_bras_impossible"])
        self.assertIn("tentative 3 du bras non relançable", r["motif_du_repli"])
        self.assertFalse(os.path.exists(os.path.join(sortie, "classement-sans-bras.json")))
        # après envoi : juge en erreur, repli en panne → verrouillé, scellé, dit
        c, s2, att2, budgets = self.course_bras("rp-envoi")

        class JugeEnErreur(Enregistreur):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
                    return Resultat("OK", [], 0.01, "ok")
                return Resultat("", [], 0.3, "erreur", "panne du juge")
        with unittest.mock.patch.object(idn, "_classer", panne), self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(s2, attestation_lecture_humaine=att2, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", JugeEnErreur(c))])
        self.assertNotIsInstance(cm.exception, idn.SansJugeExterne)
        self.assertIn("classement sans bras impossible", str(cm.exception))
        self.assertTrue(idn.verifier_scelle(os.path.join(s2, "classement-sans-bras-impossible-1.json")))
        with open(os.path.join(s2, "manifeste-bras-rapporte.json")) as f:
            self.assertIn("classement sans bras impossible", json.load(f)["reglages"]["erreur"])

    def test_cl42_06_w36_deux_tentatives_non_relancables_sans_ecrasement(self):
        """CL42-06, W36 : deux tentatives non relançables de suite — refus de taille (tentative 1 : classement sans bras
        écrit), puis contrôle « KO » payé 0,9 qui épuise le plafond externe (tentative 2) : le second repli est joué, ne
        réécrit pas le classement (même empreinte, motif de la tentative 1) et l'exception le dit ; aucun échec de repli
        (v42 : le refus de taille n'écrivait aucun classement). Un troisième refus de taille est la tentative 3 ; la quatrième
        est refusée avant tout appel (« 3 tentatives du bras déjà faites ») : les refus de taille comptent."""
        c, sortie, att, budgets = self.course_bras("w36")
        with self.assertRaises(idn.SansJugeExterne) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", Enregistreur(c))], taille_max_consigne_externe=100)
        self.assertIn("tentative 1 du bras non relançable (refus de taille", str(cm.exception))
        cl = os.path.join(sortie, "classement-sans-bras.json")
        empreinte = idn.sha256_fichier(cl)

        class KoPaye(Enregistreur):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                self.recu.append(consigne)
                return Resultat("KO", [], 0.9, "ok")
        ko = KoPaye(c)
        with self.assertRaises(idn.SansJugeExterne) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", ko)])
        self.assertEqual(ko.recu, [idn.APPEL_DE_CONTROLE_CONSIGNE])  # le second a bien été joué (contrôle payé)
        self.assertIn("tentative 2 du bras échouée avant tout envoi des fiches", str(cm.exception))
        self.assertIn("classement-sans-bras.json déjà écrit par une tentative précédente : non réécrit", str(cm.exception))
        self.assertNotIn("impossible", str(cm.exception))
        with open(os.path.join(sortie, "bras-tentative-2.json")) as f:
            self.assertFalse(json.load(f)["reglages"]["relancable"])
        self.assertEqual(idn.sha256_fichier(cl), empreinte)
        with open(cl) as f:
            self.assertIn("tentative 1", json.load(f)["sans_juge_externe"])
        self.assertFalse(any(n.startswith("classement-sans-bras-impossible") for n in os.listdir(sortie)))
        # CL42-05 : les refus de taille comptent parmi les trois tentatives — un troisième (tentative 3), puis plus rien
        with self.assertRaises(idn.SansJugeExterne):
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", Enregistreur(c))], taille_max_consigne_externe=100)
        self.assertTrue(idn.verifier_scelle(os.path.join(sortie, "manifeste-bras-refus-taille-3.json")))
        juge = Enregistreur(c)
        with self.assertRaises(idn.CourseInterrompue) as cm:
            idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                      juges_externes=[("argon", "autre-lignee-x", juge)], taille_max_consigne_externe=100)
        self.assertNotIsInstance(cm.exception, idn.SansJugeExterne)
        self.assertIn("3 tentatives du bras déjà faites", str(cm.exception))
        self.assertEqual(juge.recu, [])

    # --- CL42-07 (W30, W35b) --------------------------------------------------------------------------------------------

    def test_cl42_07_w30_plafond_externe_non_fini_au_bras_sur_sortie_fraiche(self):
        """CL42-07, W30 : sur une SORTIE fraîche (bras jamais joué), `budget_externe_usd` NaN, +∞, négatif ou booléen →
        refus avant tout appel, juge jamais appelé, aucune `bras-tentative` ni aucun fichier du bras scellé ; même chose
        par le lanceur (`--budget-externe-usd nan`). L'essai de la v42 était vide (il échouait d'abord sur « déjà été
        joué ») ; le code de la v42 était juste : cet essai passe sur la v42 et tue W30."""
        c, sortie, att, budgets = self.course_bras("w30")
        avant = sorted(os.listdir(sortie))
        for valeur in (float("nan"), float("inf"), -1.0, True):
            juge = Enregistreur(c)
            with self.subTest(valeur=valeur), self.assertRaises(idn.CourseInterrompue) as cm:
                idn.executer_bras_differe(sortie, attestation_lecture_humaine=att, budgets=budgets,
                                          juges_externes=[("argon", "autre-lignee-x", juge)], budget_externe_usd=valeur)
            self.assertIn("budget_externe_usd", str(cm.exception))
            self.assertEqual(juge.recu, [])
            self.assertEqual(sorted(os.listdir(sortie)), avant)
        v41 = self.v41()
        prep = self.prep()
        journal = os.path.join(self.tmp, "argon-w30.jsonl")
        argon = self.argon_journal(journal, "argon-w30.py")
        s2 = os.path.join(self.tmp, "l-w30")
        code, out, err = v41.principal(v41.lanceur(), v41.base(s2, prep, None, "--commande-externe", argon))
        self.assertEqual(code, 0, err)
        att2 = self.cmd().attester(os.path.join(self.tmp, "att-l-w30.json"), s2, "argon-j")
        n = len(self.journal_de(journal))
        code, out, err = v41.principal(v41.lanceur(), [s2, "--bras-rapporte-differe", "--attestation-lecture-humaine", att2,
                                                       "--juge-externe", "argon-j=gemini-argon", "--commande-externe", argon,
                                                       "--budget-externe-usd", "nan"])
        self.assertEqual(code, 2)
        self.assertIn("budget_externe_usd", err)
        self.assertEqual(len(self.journal_de(journal)), n)
        self.assertFalse(any(x.startswith(("bras-", "manifeste-bras", "classement")) for x in os.listdir(s2)))

    def test_cl42_04_borne_de_fiche_retiree_et_refus_pour_taille_par_proposeur(self):
        """CL42-04 (décision de Lazar : « retirer ») et CL42-07 : la consigne des proposeurs ne dit plus « 12000 caractères au
        plus par fiche » (consigne construite et consigne reçue par Argon) ; une fiche de plus de 40 000 caractères servis,
        champs dans leurs bornes (`fiche_maximale`), est admise ; les bornes par champ et de listes restent, et leurs refus
        sont comptés **par proposeur et par passe**, au journal et au manifeste de fin (Argon 2 : un champ de 3 001
        caractères, dix questions servies ; Opus 1 : treize antériorités ; Fable 0 — son refus pour un signe hors valeurs
        n'est pas un refus pour taille). Remplace l'essai W35b (la phrase n'existe plus). v42 : phrase présente, fiche de
        44 259 caractères refusée, aucun compte."""
        c = self.cours()
        prep = self.prep()
        c._prep = prep
        liste = idn.charger_liste_blanche(prep["liste_blanche"])
        consigne = idn.consigne_proposeur(idn.lire_pieces(prep["pieces"], liste), 8, "Quelles questions ?")
        self.assertNotIn("caractères au plus par fiche", consigne)
        self.assertIn("au plus 9 questions servies, au plus 12 antériorités, 3000 caractères au plus par texte.", consigne)
        fm = idn.valider_fiche_ideation(idn.fiche_maximale(), "a", 1)
        self.assertGreater(idn.taille_servie(fm), 40_000)
        trop_long = fiche_brute(nom="Champ trop long", enonce="y" * (idn.LONGUEUR_MAX_CHAMP + 1))
        with self.assertRaises(idn.FicheTropLongue):
            idn.valider_fiche_ideation(trop_long, "a", 1)
        recu = []

        class Argon:
            nom = "argon-simule"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                recu.append(consigne)
                fiches = [dict(idn.fiche_maximale(), nom="Argon maximal"), dict(trop_long, nom="Argon trop long"),
                          fiche_brute(nom="Argon dix questions", questions_servies=["Q1"] * 10)]
                return Resultat("```json\n" + json.dumps({"fiches": fiches}, ensure_ascii=False) + "\n```", [], 0.1, "ok")
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1"), fiche_brute(nom="O treize", anteriorite=[
                                 {"reference": "r", "statut": "SUPPOSE"}] * 13)],
                             "fable": [fiche_brute(nom="F1"), fiche_brute(nom="F signe", loi_predictive={"signe": "?"})]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        res = c.lancer(ad, "c-refus-taille", budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", Argon())],
                       budget_externe_usd=3.0)
        self.assertNotIn("caractères au plus par fiche", recu[0])
        self.assertIn("Argon maximal", [f["nom"] for f in res["fiches"]])  # 44 259 caractères servis, admise
        attendu = {"argon": {"passe-1": 2, "total": 2}, "opus": {"passe-1": 1, "total": 1}, "fable": {"passe-1": 0, "total": 0}}
        self.assertEqual(res["journal"]["refus_pour_taille_par_proposeur"], attendu)
        self.assertEqual(len(res["refus"]), 4)
        with open(os.path.join(self.tmp, "c-refus-taille", "manifeste-fin.json")) as f:
            fin = json.load(f)["reglages"]
        self.assertEqual(fin["refus_pour_taille_par_proposeur"], attendu)
        self.assertEqual(fin["journal"]["refus_pour_taille_par_proposeur"], attendu)

    # --- CL40-01, option (c) -----------------------------------------------------------------------------------------

    def test_cl40_01_c_relance_sans_rejouer_les_controles_reussis(self):
        """CL40-01, option (c) (décision de Lazar) : réglages du devis, contrôles Claude payés 0,2 et réussis, Argon « OK » à
        0,15 (commande A), puis panne du cœur avant son départ → tentative 1 relançable (0,4 + 0 + 39,6 = 40,0 ≤ 40 ; v42 :
        40,4 > 40, non relançable). Tentative 2 avec une autre commande d'Argon, qui rend « KO » : Argon rejoué (commande
        changée), échoue ; Claude **jamais rappelé**, ses contrôles repris. Tentative 3 avec une commande d'Argon qui marche :
        **seul le contrôle d'Argon est repayé**, Claude n'est pas rappelé pour ses contrôles, la course part ; manifeste de
        départ et journal : contrôles Claude repris de la tentative 1 (empreinte du fichier, de la consigne), coûts imputés
        Claude 0,4 (et non 0,8) et Argon 0,15 + 0,15 + 2,5."""
        import unittest.mock
        v41 = self.v41()
        prep, att = v41.prep_devis()
        lanceur = v41.lanceur(cout_controle_claude=0.2)
        appels_claude = []
        original = lanceur.AdaptateurIdeationSimule.lancer

        def lancer(s, role, consigne, dossier, budget_usd, max_tours, modele=None):
            appels_claude.append((modele, consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE)))
            return original(s, role, consigne, dossier, budget_usd, max_tours, modele)
        lanceur.AdaptateurIdeationSimule.lancer = lancer
        journal = os.path.join(self.tmp, "argon-c.log")
        argon_a = v41.script(v41.SCRIPT_CTRL_OK % journal, "argon-a.py")
        argon_ko = v41.script(v41.SCRIPT_KO % journal, "argon-ko.py")
        argon_b = v41.script(v41.SCRIPT_PLAFOND, "argon-b.py")
        sortie = os.path.join(self.tmp, "l-c")

        def panne(*a, **k):
            raise idn.CourseInterrompue("panne simulée du cœur avant son départ")
        with unittest.mock.patch.object(idn, "executer_ideation", panne):
            code, _, err = v41.principal(lanceur, v41.base(sortie, prep, att, "--commande-externe", argon_a))
        self.assertEqual(code, 2, err)
        t1 = os.path.join(sortie + "-controle", "tentative-1.json")
        with open(t1) as f:
            r1 = json.load(f)["reglages"]
        self.assertEqual((round(r1["cout_claude_usd"], 6), round(r1["cout_externe_usd"], 6)), (0.4, 0.15))
        self.assertEqual(r1["controles_a_refaire"], [])
        self.assertTrue(r1["relancable"], r1["motifs_relance"])  # v42 : 40,4 > 40
        self.assertEqual(sum(1 for _, ctrl in appels_claude if ctrl), 2)
        # tentative 2 : Argon (autre commande) rejoué, « KO » ; Claude jamais rappelé
        appels_claude.clear()
        code, _, err = v41.principal(lanceur, v41.base(sortie, prep, att, "--commande-externe", argon_ko))
        self.assertEqual(code, 2, err)
        self.assertEqual(appels_claude, [])
        with open(os.path.join(sortie + "-controle", "tentative-2.json")) as f:
            r2 = json.load(f)["reglages"]
        self.assertEqual(sorted(r2["lectures"]), ["externe:argon"])
        self.assertEqual(sorted(r2["controles_repris"]), ["claude-fable-5-1", "claude-opus-5-5"])
        self.assertEqual((r2["cout_claude_usd"], round(r2["cout_externe_usd"], 6)), (0.0, 0.15))
        self.assertEqual(r2["controles_a_refaire"], ["externe:argon"])
        self.assertTrue(r2["relancable"], r2["motifs_relance"])
        # tentative 3 : seul le contrôle d'Argon est repayé ; la course part
        appels_claude.clear()
        code, _, err = v41.principal(lanceur, v41.base(sortie, prep, att, "--commande-externe", argon_b))
        self.assertIn(code, (0, 4), err)
        self.assertFalse(any(ctrl for _, ctrl in appels_claude))  # aucun contrôle Claude rejoué
        self.assertTrue(appels_claude)  # les sessions Claude de la course, elles, ont eu lieu
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            d = json.load(f)["reglages"]
        self.assertAlmostEqual(d["cout_deja_engage_usd"], 0.4)  # imputé une fois (v42 : contrôles rejoués, 0,8)
        self.assertAlmostEqual(d["cout_externe_deja_engage_usd"], 0.15 + 0.15 + 2.5)
        repris = d["versions"]["controles_repris"]
        self.assertEqual(sorted(repris), ["claude-fable-5-1", "claude-opus-5-5"])
        for v in repris.values():
            self.assertEqual((v["repris_de_tentative"], v["sha256_tentative"]), (1, idn.sha256_fichier(t1)))
            self.assertEqual(v["consigne_sha256"], r1["lectures"][v["controle"]]["consigne_sha256"])
        self.assertEqual(sorted(d["versions"]["appel_de_controle"]), ["externe:argon"])
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            self.assertEqual(json.load(f)["reglages"]["journal"]["controles_repris"], repris)

    # --- CL42-03 ---------------------------------------------------------------------------------------------------------

    def test_cl42_03_mesurer_consignes_sans_appel(self):
        """CL42-03 : `--mesurer-consignes` écrit les tailles réelles (contrôle d'Argon, passe 2 maximale, juge au
        maximum : 3 proposeurs × 2 passes × 8 fiches maximales + 4 témoins + pièce de juge) et les gardes (course 520 000 ;
        bras 1 400 000 − 52 × 10 000), code 0, sans aucun appel (adaptateurs piégés, commande jamais lancée), sans fichier
        ni SORTIE, même avec `--moteur claude-sdk` non armé. La course réelle lancée ensuite envoie à Argon un contrôle de
        la taille mesurée, et une consigne de juge plus petite que le maximum mesuré (v42 : option inconnue). v43 (CL42-04 b) :
        coûts et gardes au prix donné (`--prix-entree-usd-par-million-jetons 8.3` : garde 724 819) et figures de la provision
        demandée (huit fiches à `fiche_maximale()`, 1 770 360 caractères équivalents), rapportées, non appliquées (garde 0).
        Course lancée sans option : chaque passe d'Argon gardée par le cœur à 520 000 (provision 480 000).
        v44 (CL43-02, changé) : passes gardées à 680 000 (provision de huit fiches de 8 000, 320 000)."""
        import unittest.mock
        from pole.adaptateurs import AdaptateurCommandeExterne
        v41 = self.v41()
        prep, att = v41.prep_devis()
        lb2 = os.path.join(self.tmp, "liste-blanche-mesure.json")
        pj = os.path.join(self.tmp, "piece-juge-mesure.md")
        with open(pj, "w", encoding="utf-8") as f:
            f.write("# Antériorité\n" + "Résumé. " * 3000)
        idn.construire_liste_blanche([prep["pieces"][0], prep["question"], prep["materiau"][0], prep["temoins"], pj], lb2)
        prep = dict(prep, liste_blanche=lb2)
        journal = os.path.join(self.tmp, "argon-mesure.jsonl")
        argon = self.argon_journal(journal, "argon-mesure.py")
        sortie = os.path.join(self.tmp, "l-mesure")
        argv = v41.base(sortie, prep, att, "--commande-externe", argon, "--piece-juge", pj)

        def piege(*a, **k):
            raise AssertionError("aucun appel ne doit partir")
        lanceur = v41.lanceur()
        with unittest.mock.patch.object(lanceur.AdaptateurIdeationSimule, "lancer", piege), \
                unittest.mock.patch.object(AdaptateurCommandeExterne, "lancer", piege):
            code, out, err = v41.principal(lanceur, argv + ["--mesurer-consignes"])
            code_r, out_r, err_r = v41.principal(lanceur, argv + ["--mesurer-consignes", "--moteur", "claude-sdk"])
            code_p, out_p, err_p = v41.principal(lanceur, argv + ["--mesurer-consignes", "--prix-entree-usd-par-million-jetons",
                                                                  "8.3"])
        self.assertEqual((code, code_r, code_p), (0, 0, 0), err + err_r + err_p)
        m = json.loads(out)
        self.assertEqual(json.loads(out_r)["consignes"], m["consignes"])
        mp = json.loads(out_p)
        ctrl = m["consignes"]["consigne_de_controle_externe"]
        self.assertEqual((m["prix_entree_usd_par_million_jetons"], mp["prix_entree_usd_par_million_jetons"]), (10.0, 8.3))
        self.assertAlmostEqual(m["garde_course"]["cout_entree_controle_usd"], round(ctrl * 2.5e-6, 4))
        self.assertAlmostEqual(mp["garde_course"]["cout_entree_controle_usd"], round(ctrl * 8.3e-6 / 4, 4))
        self.assertEqual(mp["garde_course"]["taille_max_caracteres"], 724_819)
        for x in (m, mp):
            nd = x["garde_course"]["provision_huit_fiches_maximales_non_appliquee"]
            self.assertEqual((nd["provision_sortie_caracteres"], nd["taille_max_caracteres"]), (8 * idn.taille_servie(idn.fiche_maximale()) * 5, 0))
        self.assertFalse(os.path.exists(sortie) or os.path.exists(sortie + "-controle") or os.path.exists(journal))
        budgets = dict(self.cours().budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 2.5
        budgets[("juge_ideation", "gemini-argon")] = 3.5
        verif = idn.verifier_reglages(liste_blanche=lb2, question=prep["question"], pieces=prep["pieces"],
                                      materiau=prep["materiau"], temoins=prep["temoins"], seconde_passe=True,
                                      attestation_materiau=att, budgets=budgets, budget_total_usd=40.0, budget_externe_usd=12.0,
                                      proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                                      juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")],
                                      proposeurs_externes=[("argon", "gemini-argon")])
        cs = m["consignes"]
        self.assertEqual(cs["consigne_de_controle_externe"], verif["taille_consigne_controle_externe"])
        self.assertEqual(len(idn.consigne_de_controle(verif["texte_controle_externe"])), cs["consigne_de_controle_externe"])
        self.assertEqual(cs["consigne_passe_2_maximale"], len(verif["texte_controle_externe"]))
        self.assertEqual((cs["fiches_au_juge_au_maximum"], cs["controle_du_bras"]), (52, 41))
        self.assertGreater(cs["consigne_du_juge_maximale"], 48 * 12_000)
        self.assertEqual((m["garde_course"]["taille_max_caracteres"], m["garde_course"]["passerait"]), (520_000, True))
        self.assertEqual(m["garde_bras"]["argon-j"]["taille_max_caracteres"], 1_400_000 - 52 * 10_000)
        # la course réelle : contrôle d'Argon de la taille mesurée ; consigne du juge sous le maximum mesuré
        code, out, err = v41.principal(v41.lanceur(), argv)
        self.assertEqual(code, 0, err)
        appels = self.journal_de(journal)
        self.assertEqual(appels[0]["controle"], True)
        self.assertEqual(appels[0]["taille"], cs["consigne_de_controle_externe"])
        self.assertLessEqual(max(a["taille"] for a in appels if a["passe2"] and not a["controle"]), cs["consigne_passe_2_maximale"])
        with open(os.path.join(sortie, "juges-bras-rapporte", "traces-argon-j", "consigne-en-attente.md"), encoding="utf-8") as f:
            self.assertLess(len(f.read()), cs["consigne_du_juge_maximale"])
        # CL42-01 : sans option, le lanceur fait garder chaque passe d'Argon par le cœur contre son propre plafond
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            g = json.load(f)["reglages"]["journal"]["gardes_taille_sessions"]
        self.assertEqual([(x["passe"], x["taille_max_caracteres"], x["provision_sortie_caracteres"], x["refusee"]) for x in g],
                         [(1, 680_000, 320_000, False), (2, 680_000, 320_000, False)])  # v43 : 520 000, 480 000



class TestV44(CasAvecDossier):
    """v44 (contre-lecture CL10 de la v43 ; périmètre minimal de session-depot pour lancer) : plafond propre à la passe 2
    d'Argon et somme externe de (β) (CL43-01) ; chaque passe gardée contre son propre plafond moins la provision de sortie,
    même sous une taille donnée (CL43-02) ; contrôles Claude repris seulement si le relais n'a pas été relancé (CL43-03) ;
    fichier d'entrée changé entre deux tentatives (X01) ; borne de trois tentatives dite (CL43-05) ; mesures de
    convergence au manifeste de fin (ajout de Lazar)."""

    BETA = ["--budget-controle-externe-usd", "3.1", "--budget-passe-2-externe-usd", "3.1", "--budget-externe-usd", "12.8",
            "--prix-entree-usd-par-million-jetons", "8.3", "--taille-max-consigne-externe", "1490000"]
    BRAS_BETA = ["--prix-entree-usd-par-million-jetons", "8.3", "--budget-externe-usd", "12.8"]

    def v43(self):
        t = TestV43("test_cl42_03_mesurer_consignes_sans_appel")
        t.tmp = self.tmp
        return t

    # Argon factice au barème donné (dollars par caractère d'entrée et de sortie ; jamais borné à son plafond), huit fiches
    # copiées d'une fiche donnée, juge qui respecte le critère des témoins ; chaque appel consigné
    SCRIPT_TARIF_8 = (
        "import sys, json, os, re\nc = sys.stdin.read()\nctrl = c.startswith('Réponds exactement OK')\n"
        "def sortir(t):\n"
        "    cout = len(c) * %r + len(t) * %r\n"
        "    open(%r, 'a').write(json.dumps({'taille': len(c), 'controle': ctrl, 'role': os.environ['ROLE_POLE'], "
        "'passe2': 'première passe' in c, 'cout': cout, 'plafond': float(os.environ['PLAFOND_SESSION_USD'])}) + '\\n')\n"
        "    print(json.dumps({'texte': t, 'cout_usd': cout})); sys.exit(0)\n"
        "if ctrl: sortir('OK')\n"
        "if os.environ['ROLE_POLE'] == 'proposeur_ideation':\n"
        "    f = json.loads(%r)\n"
        "    fiches = [dict(f, nom=('Argon %%d' %% i) + (' revue' if 'première passe' in c else '')) for i in range(8)]\n"
        "    sortir('```json\\n' + json.dumps({'fiches': fiches}, ensure_ascii=False) + '\\n```')\n"
        "bloc = json.loads(re.search(r'```json\\n(\\[.*\\])\\n```', c, re.S).group(1)); par_nom = {f['nom']: f['identifiant'] for f in bloc}\n"
        "notes = []\n"
        "for f in bloc:\n"
        "    k = {x: 2 for x in ('avantage', 'originalite', 'falsifiabilite', 'traitabilite', 'robustesse')}\n"
        "    if f['nom'] in ('Verbeux vide', 'Assuré occupé'): k.update({'avantage': 1, 'originalite': 0, 'falsifiabilite': 0})\n"
        "    notes.append({'identifiant': f['identifiant'], 'criteres': k, 'justifications': {}})\n"
        "sortir('```json\\n' + json.dumps({'notes': notes, 'doublons': [[par_nom['Jumeau'], par_nom['Sobre fort']]]}) + '\\n```')\n")

    def argon_tarif(self, fiche, journal, nom):
        return self.v43().v41().script(self.SCRIPT_TARIF_8 % (8.3e-6 / 4, 41.5e-6 / 4, journal, json.dumps(fiche, ensure_ascii=False)),
                                       nom)

    @staticmethod
    def fiche_de_taille(cible):
        """Une fiche au gabarit dont la taille servie est la plus petite ≥ `cible` (douze textes de même longueur)."""
        for n in range(1, 3000):
            t = ("texte de méthode sans signal " * (n // 29 + 1))[:n]
            f = fiche_brute(nom="Argon", enonce=t, perte_traduction=t, piege=t, cosmetique_si=t,
                            loi_predictive={"espace_instances": t, "prediction": t, "metrique": t},
                            avantage={"texte": t, "incopiable_parce_que": t}, originalite={"texte": t},
                            demande_organisme={"texte": t}, cout={"ordre_de_grandeur": t})
            if idn.taille_servie(idn.valider_fiche_ideation(f, "a", 1)) >= cible:
                return f
        raise AssertionError(cible)

    def journal(self, chemin):
        return self.v43().journal_de(chemin)

    # --- CL43-01 ---------------------------------------------------------------------------------------------------------

    def test_cl43_01_plafond_de_passe_2_et_somme_externe_de_beta(self):
        """CL43-01 : `--budget-passe-2-externe-usd` (plafond de la seule passe 2 d'Argon ; v43 : option inconnue). Ligne (β)
        aux réglages du devis (pièce 750 000, matériau 350 000) : somme externe 3,1 + 2,5 + 3,1 + 3,5 + 0,2 = 12,4 ≤ 12,8,
        `verifier_reglages` l'accepte (passe 1 gardée à 884 819 avant tout contrôle) ; `--budget
        "proposeur_ideation|gemini-argon=3.1"` à la place (les deux passes à 3,1) : 13,0 > 12,8, refus avant tout appel,
        Argon jamais appelé, aucun fichier. Sans l'option : la passe 2 prend le plafond de la passe 1 (comme en v43). Option
        non finie, nulle, ou sans `--seconde-passe` : refusée par l'analyseur."""
        import contextlib
        import io
        v43 = self.v43()
        v41 = v43.v41()
        prep, att = v43.prep_grand()
        budgets = dict(self.v43().cours().budgets())
        budgets.update({("proposeur_ideation", "gemini-argon"): 2.5, ("juge_ideation", "gemini-argon"): 3.5})
        commun = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"],
                      materiau=prep["materiau"], temoins=prep["temoins"], seconde_passe=True, attestation_materiau=att,
                      budgets=budgets, budget_total_usd=40.0, budget_externe_usd=12.8, cout_controles_externes_prevu_usd=3.1,
                      proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")],
                      proposeurs_externes=[("argon", "gemini-argon")], juges_externes=[("argon-j", "gemini-argon")],
                      taille_max_consigne_externe=1_490_000, prix_caractere_usd=idn.prix_caractere(8.3), taille_max_pieces=750_000)
        v = idn.verifier_reglages(budget_passe_2_externe_usd=3.1, garder_passes_externes=True, **commun)
        self.assertAlmostEqual(v["somme_externe"], 12.4)
        self.assertEqual(v["garde_passe_1"]["argon"]["taille_max_caracteres"], 884_819)
        self.assertAlmostEqual(idn.verifier_reglages(**commun)["somme_externe"], 11.8)  # passe 2 = passe 1 (v43)
        with self.assertRaises(idn.CourseInterrompue):
            idn.verifier_reglages(budget_passe_2_externe_usd=float("nan"), **commun)
        journal = os.path.join(self.tmp, "argon-cl43-01.jsonl")
        argon = self.argon_tarif(fiche_brute(nom="Argon"), journal, "argon-cl43-01.py")
        sortie = os.path.join(self.tmp, "l-cl43-01")
        treize = ["--budget-controle-externe-usd", "3.1", "--budget-externe-usd", "12.8", "--prix-entree-usd-par-million-jetons",
                  "8.3", "--taille-max-consigne-externe", "1490000", "--budget", "proposeur_ideation|gemini-argon=3.1"]
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe", argon, *treize))
        self.assertEqual(code, 2, err)
        self.assertIn("somme des plafonds externes 13.00 > total externe 12.8", err)
        self.assertEqual(self.journal(journal), [])
        self.assertFalse(os.path.exists(sortie) or os.path.exists(sortie + "-controle"))
        for options in (["--budget-passe-2-externe-usd", "nan"], ["--budget-passe-2-externe-usd", "0"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as cm:
                v41.lanceur().principal(v41.base(sortie, prep, att, "--commande-externe", argon, *options))
            self.assertEqual(cm.exception.code, 2)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            v41.lanceur().principal(v41.base(sortie, prep, None, "--commande-externe", argon, "--budget-passe-2-externe-usd", "3.1"))

    # --- CL43-02 ---------------------------------------------------------------------------------------------------------

    def test_cl43_02_passe_2_refusee_avant_envoi_fiches_de_8950(self):
        """CL43-02 (B-p31-b83-g700 de CL10, sous (β)) : fiches d'Argon de ≈ 8 950 caractères servis, Argon au barème 8,3
        (sortie au rapport 5), garde donnée 1 490 000 : contrôle 3,02 et passe 1 ≈ 2,31 payés ; la passe 2 (≈ 1 175 000
        caractères) est **refusée avant envoi** contre son plafond 3,1 moins la provision de huit fiches de la plus grande
        fiche admise de passe 1 (1 493 975 − 40 × 8 950 ≈ 1 135 975), au lieu d'être payée 3,18 > 3,1 ; aucune passe
        Claude ; manifeste de fin scellé en erreur, gardes au journal (v43 : option de passe 2 inconnue ; sous la garde
        donnée, passe 2 gardée à 1 490 000 seulement, partie)."""
        v43 = self.v43()
        v41 = v43.v41()
        prep, att = v43.prep_grand()
        fiche = self.fiche_de_taille(8_950)
        journal = os.path.join(self.tmp, "argon-8950.jsonl")
        argon = self.argon_tarif(fiche, journal, "argon-8950.py")
        sortie = os.path.join(self.tmp, "l-8950")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe", argon, *self.BETA))
        self.assertEqual(code, 2, err)
        self.assertIn("garde de taille : consigne de la passe 2", err)
        appels = self.journal(journal)
        self.assertEqual([(a["controle"], a["passe2"]) for a in appels], [(True, True), (False, False)])  # contrôle, passe 1
        self.assertLessEqual(appels[0]["cout"], 3.1)
        self.assertLessEqual(appels[1]["cout"], 2.5)
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            fin = json.load(f)["reglages"]
        g = fin["journal"]["gardes_taille_sessions"]
        self.assertEqual([(x["passe"], x["refusee"], x["plafond_usd"]) for x in g], [(1, False, 2.5), (2, True, 3.1)])
        self.assertEqual(g[0]["taille_max_caracteres"], 884_819)
        tf = g[1]["taille_fiche_provisionnee"]
        self.assertGreaterEqual(tf, 8_950)
        self.assertEqual((g[1]["provision_sortie_caracteres"], g[1]["taille_max_caracteres"]), (40 * tf, 1_493_975 - 40 * tf))
        self.assertGreater(g[1]["taille_caracteres"], g[1]["taille_max_caracteres"])
        self.assertLess(g[1]["taille_caracteres"], 1_490_000)  # la garde donnée seule l'aurait laissée partir (v43)
        self.assertAlmostEqual(fin["journal"]["cout_externe_usd"], appels[0]["cout"] + appels[1]["cout"], places=6)
        self.assertFalse(any(a["role"] == "proposeur_ideation" and not a["externe"] for a in fin["journal"]["appels"]))

    def test_cl43_02_fiches_maximales_et_fiches_courtes(self):
        """CL43-02 : (1) passe 1 trop grosse pour son plafond moins la provision (passe 1 à 1,0) → **refusée avant tout
        contrôle**, refus scellé (`refus-taille-1.json`), Argon et Claude jamais appelés ; (2) fiches d'Argon au maximum par
        champ (44 259) sous (β) : la passe 1 ne peut pas être gardée sur des fiches qu'elle n'a pas encore rendues (sa
        garde, 884 819, la laisse partir ; réserve dite au LISEZMOI) ; sa réponse dépasse son plafond (`budget_depasse`),
        la course s'arrête et la passe 2 n'est **jamais envoyée** ; au cœur, passe 1 tenue (plafond 6,0) : passe 2 refusée
        avant envoi (provision de huit fiches de 44 259, garde 0) ; (3) fiches courtes sous (β) : tout passe, gardes
        884 819 et 1 173 975, puis bras au barème 8,3 → classement à trois juges ; `--mesurer-consignes` aux mêmes réglages
        rapporte les gardes des passes (v43 : option inconnue)."""
        v43 = self.v43()
        v41 = v43.v41()
        prep, att = v43.prep_grand()
        # (1) passe 1 refusée avant tout contrôle
        journal = os.path.join(self.tmp, "argon-p1.jsonl")
        argon = self.argon_tarif(fiche_brute(nom="Argon"), journal, "argon-p1.py")
        s1 = os.path.join(self.tmp, "l-p1")
        code, out, err = v41.principal(v41.lanceur(), v41.base(s1, prep, att, "--commande-externe", argon, *self.BETA,
                                                               "--budget", "proposeur_ideation|gemini-argon=1.0"))
        self.assertEqual(code, 2, err)
        self.assertEqual(self.journal(journal), [])
        with open(os.path.join(s1 + "-controle", "refus-taille-1.json")) as f:
            g = json.load(f)["reglages"]
        self.assertIn("passe 1", g["garde_taille"]["quoi"])
        self.assertEqual((g["cout_usd"], g["tentative_comptee"]), (0.0, False))
        self.assertFalse(os.path.exists(s1))
        # (2) fiches maximales sous (β)
        jmax = os.path.join(self.tmp, "argon-max.jsonl")
        amax = self.argon_tarif(idn.fiche_maximale(), jmax, "argon-max.py")
        s2 = os.path.join(self.tmp, "l-max")
        code, out, err = v41.principal(v41.lanceur(), v41.base(s2, prep, att, "--commande-externe", amax, *self.BETA))
        self.assertEqual(code, 2, err)
        self.assertEqual([(a["controle"], a["passe2"]) for a in self.journal(jmax)], [(True, True), (False, False)])
        with open(os.path.join(s2, "manifeste-fin.json")) as f:
            fin = json.load(f)["reglages"]
        self.assertIn("budget_depasse", fin["erreur"])
        self.assertEqual([x["passe"] for x in fin["journal"]["gardes_taille_sessions"]], [1])
        c = v43.cours()
        c._prep = v43.prep()
        recu = []

        class ArgonMax:
            nom = "argon-simule"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                recu.append(os.path.basename(dossier))
                fiches = [dict(idn.fiche_maximale(), nom=f"Argon {i}") for i in range(8)]
                return Resultat("```json\n" + json.dumps({"fiches": fiches}, ensure_ascii=False) + "\n```", [], 5.0, "ok")
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 6.0
        att_p = os.path.join(self.tmp, "att-max.json")
        idn.ecrire_json_scelle(att_p, {"lecteur": "Lazar", "lu_le": "2026-10-29", "materiau_sha256": {
            os.path.basename(c._prep["materiau"][0]): idn.sha256_fichier(c._prep["materiau"][0])}})
        with self.assertRaises(idn.TailleConsigneRefusee):
            c.lancer(ad, "c-max", budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", ArgonMax())],
                     budget_externe_usd=10.0, seconde_passe=True, attestation_materiau=att_p, garder_sessions_externes=True,
                     budget_passe_2_externe_usd=3.1, prix_caractere_usd=idn.prix_caractere(8.3))
        self.assertEqual(recu, ["passe-1"])
        self.assertEqual(ad.appels, [])
        # (3) fiches courtes sous (β) : tout passe, trois juges
        jc = os.path.join(self.tmp, "argon-court.jsonl")
        ac = self.argon_tarif(fiche_brute(nom="Argon"), jc, "argon-court.py")
        s3 = os.path.join(self.tmp, "l-court")
        lanceur = v41.lanceur()
        code, out, err = v41.principal(lanceur, v41.base(s3, prep, att, "--commande-externe", ac, *self.BETA, "--mesurer-consignes"))
        self.assertEqual(code, 0, err)
        gp = json.loads(out)["gardes_passes_externes"]["argon"]
        self.assertEqual((gp["passe_1"]["taille_max_caracteres"], gp["passe_1"]["passerait"]), (884_819, True))
        self.assertEqual(gp["passe_2_fiches_de_passe_1_au_plus_provisionnees"]["taille_max_caracteres"], 1_173_975)
        self.assertFalse(gp["passe_2_maximale"]["passerait"])
        self.assertFalse(os.path.exists(s3))
        code, out, err = v41.principal(lanceur, v41.base(s3, prep, att, "--commande-externe", ac, *self.BETA))
        self.assertEqual(code, 0, err)
        with open(os.path.join(s3, "manifeste-fin.json")) as f:
            g = json.load(f)["reglages"]["journal"]["gardes_taille_sessions"]
        self.assertEqual([(x["passe"], x["taille_max_caracteres"], x["refusee"]) for x in g],
                         [(1, 884_819, False), (2, 1_173_975, False)])
        self.assertTrue(all(a["cout"] <= a["plafond"] for a in self.journal(jc)))
        att_b = v43.cmd().attester(os.path.join(self.tmp, "att-court.json"), s3, "argon-j")
        code, out, err = v41.principal(lanceur, [s3, "--bras-rapporte-differe", "--attestation-lecture-humaine", att_b,
                                                 "--juge-externe", "argon-j=gemini-argon", "--commande-externe", ac,
                                                 *self.BRAS_BETA])
        self.assertEqual(code, 0, err)
        with open(os.path.join(s3, "classement.json")) as f:
            self.assertTrue(all(l["nombre_juges"] == 3 for l in json.load(f)["lignes"]))

    # --- CL43-03 ---------------------------------------------------------------------------------------------------------

    def test_cl43_03_controles_claude_rejoues_si_le_relais_a_ete_relance(self):
        """CL43-03 : chemin du moteur réel (kit, bac à sable et relais remplacés par des faux locaux ; aucun réseau, aucune
        clé) ; tentative 1 : contrôles Claude payés 0,2 chacun et réussis (dépense lue au relais 0,2 puis 0,4), panne du
        cœur ; tentative 2, relais gardé (dépense 0,4) : contrôles Claude **repris**, motif « relais non relancé » ;
        tentative 3, relais relancé (dépense remise à 0) : contrôles Claude **rejoués** (v43 : repris), motif « relais
        relancé » au manifeste de départ, au journal du cœur et sur la sortie d'erreur ; la course part."""
        import types
        import unittest.mock
        import pole.adaptateurs as pa
        v41 = self.v43().v41()
        prep, att = v41.prep_devis()
        lanceur = v41.lanceur()
        relais = {"appels": 0, "depense_usd": 0.0, "plafond_usd": 50.0, "reserve_par_appel_usd": 4.0}
        appels = []
        simule = lanceur.AdaptateurIdeationSimule(1)

        class FauxKit:
            nom = "claude-sdk"

            def __init__(self, *a, **k):
                pass

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                ctrl = consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE)
                appels.append((modele, ctrl))
                r = simule.lancer(role, consigne, dossier, budget_usd, max_tours, modele)
                cout = 0.2 if ctrl else r.cout_declare_usd
                relais["appels"] += 1
                relais["depense_usd"] = round(relais["depense_usd"] + cout, 6)
                return Resultat(r.texte_final, [], cout, "ok")
        argon = v41.script(v41.SCRIPT_PLAFOND, "argon-relais.py")
        sortie = os.path.join(self.tmp, "l-relais")
        argv = v41.base(sortie, prep, att, "--commande-externe", argon, "--moteur", "claude-sdk", "--confirmer-moteur-reel",
                        "--modele-commande-externe", "gemini-argon",  # v50 (CL14-07) : l'étiquette de l'essai n'est pas celle d'Argon v2
                        "--commande-externe-lit-modele",  # v51 (CL15-05) : la commande factice de l'essai est attestée la lire
                        "--url-relais", "http://127.0.0.1:9", "--racine-depot", self.tmp, "--budget-total-usd", "41")

        def panne(*a, **k):
            raise idn.CourseInterrompue("panne simulée du cœur avant son départ")
        coeur = idn.executer_ideation
        with unittest.mock.patch.object(pa, "AdaptateurClaudeSDK", FauxKit), \
                unittest.mock.patch.object(pa, "importer_sdk", lambda: types.SimpleNamespace(__version__="faux")), \
                unittest.mock.patch.object(pa, "etat_bac_a_sable_detaille",
                                           lambda *a, **k: {"actif": True, "proc_neuf": True, "motif": "faux"}), \
                unittest.mock.patch.object(lanceur, "version_outil_ligne_de_commande", lambda sdk: {"version": "faux"}), \
                unittest.mock.patch.object(lanceur, "lecteur_relais", lambda url: (lambda: dict(relais))):
            with unittest.mock.patch.object(idn, "executer_ideation", panne):
                code, _, err = v41.principal(lanceur, argv)
                self.assertEqual(code, 2, err)
                self.assertEqual(sum(1 for _, c in appels if c), 2)
                self.assertAlmostEqual(relais["depense_usd"], 0.4)
                appels.clear()
                code, _, err = v41.principal(lanceur, argv)  # relais gardé
                self.assertEqual(code, 2, err)
            self.assertEqual(appels, [])
            with open(os.path.join(sortie + "-controle", "tentative-2.json")) as f:
                r2 = json.load(f)["reglages"]
            self.assertEqual(sorted(r2["controles_repris"]), ["claude-fable-5-1", "claude-opus-5-5", "externe:argon"])
            relais.update(appels=0, depense_usd=0.0)  # relais relancé à la même adresse
            self.assertIs(idn.executer_ideation, coeur)
            code, _, err = v41.principal(lanceur, argv)
        self.assertIn(code, (0, 4), err)
        self.assertEqual(sorted(m for m, c in appels if c), ["claude-fable-5-1", "claude-opus-5-5"])  # rejoués
        self.assertIn("relais relancé", err)
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            d = json.load(f)["reglages"]
        self.assertEqual(sorted(d["versions"]["controles_repris"]), ["externe:argon"])
        motifs = d["versions"]["motifs_reprise_controles"]
        self.assertEqual(sorted(motifs), ["claude-fable-5-1", "claude-opus-5-5"])
        self.assertTrue(all(m.startswith("rejoué : relais relancé") for m in motifs.values()))
        with open(os.path.join(sortie, "manifeste-fin.json")) as f:
            self.assertEqual(json.load(f)["reglages"]["journal"]["motifs_reprise_controles"], motifs)
        self.assertAlmostEqual(d["cout_deja_engage_usd"], 0.8)  # 0,4 de la tentative 1, 0,4 rejoués
        self.assertTrue(all("relais non relancé" in m for m in r2["motifs_reprise_controles"].values()))
        # unitaire : dépense non lue à la tentative, relais illisible
        rep = {"claude-opus-5-5": {"repris_de_tentative": 1, "relais_apres_depense_usd": None}}
        self.assertEqual(lanceur.filtrer_reprises_claude(rep, lambda: {"depense_usd": 5.0})[0], {})

        def illisible():
            raise OSError("relais muet")
        self.assertEqual(lanceur.filtrer_reprises_claude(
            {"claude-opus-5-5": {"repris_de_tentative": 1, "relais_apres_depense_usd": 0.2}}, illisible)[0], {})

    # --- X01 (CL43-07) ---------------------------------------------------------------------------------------------------

    def test_x01_fichier_d_entree_change_entre_deux_tentatives(self):
        """X01 (CL43-07) : tentative 1, contrôles réussis, panne du cœur ; la pièce change (liste blanche refaite) ; tentative
        2, même commande d'Argon : la consigne de contrôle d'Argon a changé (empreinte dans la clé de reprise) → **Argon
        rejoué** ; le contrôle Claude (consigne courte et fixe) est repris. Le code de la v43 était juste : cet essai passe
        sur la v43 et tue le défaut X01 (clé sans l'empreinte de la consigne)."""
        import unittest.mock
        v43 = self.v43()
        v41 = v43.v41()
        prep, att = v41.prep_devis()
        lanceur = v41.lanceur()
        journal = os.path.join(self.tmp, "argon-x01.jsonl")
        argon = v43.argon_journal(journal, "argon-x01.py")
        sortie = os.path.join(self.tmp, "l-x01")

        def panne(*a, **k):
            raise idn.CourseInterrompue("panne simulée du cœur avant son départ")
        with unittest.mock.patch.object(idn, "executer_ideation", panne):
            code, _, err = v41.principal(lanceur, v41.base(sortie, prep, att, "--commande-externe", argon))
        self.assertEqual(code, 2, err)
        self.assertEqual([a["controle"] for a in self.journal(journal)], [True])
        p2 = os.path.join(self.tmp, "piece-x01.md")
        with open(p2, "w", encoding="utf-8") as f:
            f.write("# Pièce A changée\nAutre texte de contexte.")
        lb2 = os.path.join(self.tmp, "liste-blanche-x01.json")
        idn.construire_liste_blanche([p2, prep["question"], prep["materiau"][0], prep["temoins"]], lb2)
        prep2 = dict(prep, liste_blanche=lb2, pieces=[p2])
        code, _, err = v41.principal(lanceur, v41.base(sortie, prep2, att, "--commande-externe", argon))
        self.assertIn(code, (0, 4), err)
        appels = self.journal(journal)
        self.assertEqual([a["controle"] for a in appels[:2]], [True, True])  # Argon rejoué avant ses passes
        with open(os.path.join(sortie, "manifeste-depart.json")) as f:
            v = json.load(f)["reglages"]["versions"]
        self.assertEqual(sorted(v["controles_repris"]), ["claude-fable-5-1", "claude-opus-5-5"])
        self.assertEqual(sorted(v["appel_de_controle"]), ["externe:argon"])
        with open(os.path.join(sortie + "-controle", "tentative-1.json")) as f:
            avant = json.load(f)["reglages"]["lectures"]["externe:argon"]["consigne_sha256"]
        self.assertNotEqual(v["appel_de_controle"]["externe:argon"]["consigne_sha256"], avant)

    # --- CL43-05 ---------------------------------------------------------------------------------------------------------

    def test_cl43_05_relance_bornee_par_les_sommes_et_par_trois_tentatives(self):
        """CL43-05 : trois tentatives scellées (contrôles réussis puis repris, rien payé) : la troisième dit « 3 tentatives
        faites (borne MAX_TENTATIVES_BRAS, en plus des sommes) » ; la quatrième est refusée avant tout appel et le message dit
        les deux bornes (v43 : « plus de relance sans un mot de Lazar » seul)."""
        import unittest.mock
        v41 = self.v43().v41()
        prep, att = v41.prep_devis()
        lanceur = v41.lanceur()
        argon = v41.script(v41.SCRIPT_PLAFOND, "argon-cl43-05.py")
        sortie = os.path.join(self.tmp, "l-cl43-05")

        def panne(*a, **k):
            raise idn.CourseInterrompue("panne simulée du cœur avant son départ")
        with unittest.mock.patch.object(idn, "executer_ideation", panne):
            for _ in range(3):
                code, _, err = v41.principal(lanceur, v41.base(sortie, prep, att, "--commande-externe", argon))
                self.assertEqual(code, 2, err)
            code, _, err = v41.principal(lanceur, v41.base(sortie, prep, att, "--commande-externe", argon))
        self.assertEqual(code, 2)
        with open(os.path.join(sortie + "-controle", "tentative-3.json")) as f:
            self.assertIn("3 tentatives faites (borne MAX_TENTATIVES_BRAS, en plus des sommes)",
                          " ".join(json.load(f)["reglages"]["motifs_relance"]))
        self.assertIn("bornée par les sommes ET par 3 tentatives (MAX_TENTATIVES_BRAS)", err)
        self.assertFalse(os.path.exists(os.path.join(sortie + "-controle", "tentative-4.json")))

    # --- ajout de Lazar : mesures de convergence ------------------------------------------------------------------------

    def test_mesures_de_convergence_au_manifeste_de_fin(self):
        """Ajout de Lazar (29 octobre, 10:09 heure de Paris) : deux passes simulées ; Opus modifie sa fiche (énoncé changé,
        une source nouvelle, la pièce citée) → distance d'édition = 1 − rapport de SequenceMatcher sur les mots, Jaccard des
        sources 1 − 1/3, deux sources en passe 1 et 2, une nouvelle, part des pièces citées 0 puis 1 ; Fable rend la même
        fiche → distances 0, aucune source nouvelle ; `pages_lues` nul, motif « course sans outils de lecture » ; rien
        dans les fiches servies aux juges ni dans le classement (v43 : aucune mesure)."""
        import difflib
        c = self.v43().cours()
        c._prep = self.v43().prep()
        f1 = fiche_brute(nom="Pente", anteriorite=[{"reference": "Ramtin arXiv:2601.20022 [p.3]", "statut": "RAPPORTE"}])
        f2 = fiche_brute(nom="Pente", enonce="La pente du transfert, mesurée sur piece-a, est-elle prédite avant le test ?",
                         anteriorite=[{"reference": "Ramtin arXiv:2601.20022v2", "statut": "RAPPORTE"},
                                      {"reference": "Autre arXiv:2501.00001", "statut": "SUPPOSE"}])
        stable = fiche_brute(nom="Stable")
        ad = FauxAdaptateur({"opus": lambda passe, consigne: [f1] if passe == "passe-1" else [f2],
                             "fable": lambda passe, consigne: [stable]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        res = c.lancer(ad, "c-conv", seconde_passe=True)
        with open(os.path.join(self.tmp, "c-conv", "manifeste-fin.json")) as f:
            m = json.load(f)["reglages"]["mesures_convergence"]
        self.assertEqual((m["pages_lues"], m["motif_pages_lues"]), (None, "course sans outils de lecture"))
        o = m["par_proposeur"]["opus"]["opus-p1-01"]
        v1 = next(x for x in res["fiches"] if x["identifiant_auteur"] == "opus-p1-01")
        v2 = next(x for x in res["fiches"] if x["identifiant_auteur"] == "opus-p2-01")
        attendu = round(1 - difflib.SequenceMatcher(None, idn.texte_fiche(v1).split(), idn.texte_fiche(v2).split()).ratio(), 6)
        self.assertEqual((o["identifiant_passe_2"], o["appariement"], o["distance_edition"]), ("opus-p2-01", "même nom", attendu))
        self.assertGreater(o["distance_edition"], 0)
        self.assertEqual((o["distance_jaccard_sources"], o["sources_passe_1"], o["sources_passe_2"], o["sources_nouvelles_passe_2"]),
                         (0.666667, 2, 2, 1))
        self.assertEqual((o["part_pieces_citees_passe_1"], o["part_pieces_citees_passe_2"]), (0.0, 1.0))
        self.assertEqual((o["pages_lues"], o["motif_pages_lues"]), (None, "course sans outils de lecture"))
        s = m["par_proposeur"]["fable"]["fable-p1-01"]
        self.assertEqual((s["distance_edition"], s["distance_jaccard_sources"], s["sources_nouvelles_passe_2"]), (0.0, 0.0, 0))
        for nom in ("classement.json", "fiches-validees.json", "lecture.json"):
            with open(os.path.join(self.tmp, "c-conv", nom), encoding="utf-8") as f:
                self.assertNotIn("distance_edition", f.read())
        for a in ad.appels:
            if a["role"] == "juge_ideation":
                self.assertNotIn("distance", a["consigne"])



class TestV45(CasAvecDossier):
    """v45 (bloquant de lancement démontré par session-depot sur la v44, message n° 175) : `anonymiser` normalisait la
    typographie sur le texte JSON, un guillemet « » ou “ ” y devenait un `"` non échappé (`JSONDecodeError`) après toutes
    les passes des proposeurs, avant le premier juge. v45 : normalisation valeur par valeur. Chaque essai échoue sur la v44."""

    GUILLEMETS = "Le « moniteur » dit “diffus” — l’écart… "

    def v43(self):
        t = TestV43("test_cl42_03_mesurer_consignes_sans_appel")
        t.tmp = self.tmp
        return t

    def temoins_guillemets(self):
        g = self.GUILLEMETS
        return {"temoins": [
            {"fiche": fiche_brute(nom="Sobre fort", enonce=g + "sobre ?"), "attendu": "eligible", "classe": "vrai"},
            {"fiche": fiche_brute(nom="Verbeux vide", enonce=g * 10), "attendu": "ineligible",
             "note_max": {"falsifiabilite": 1}, "classe": "faux_falsifiabilite"},
            {"fiche": fiche_brute(nom="Assuré occupé", originalite={"niveau": "inedite", "texte": "« jamais vu »"}),
             "attendu": "ineligible", "note_max": {"originalite": 1}, "classe": "faux_anteriorite"},
            {"fiche": fiche_brute(nom="Jumeau", piege="“" + g + "”"), "attendu": "eligible", "jumeau_de": "Sobre fort",
             "classe": "jumeau"}]}

    def prep_guillemets(self):
        v41 = self.v43().v41()
        prep = v41.cours().preparer(temoins_json=self.temoins_guillemets())
        att = os.path.join(self.tmp, "att-materiau-v45.json")
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-29", "materiau_sha256": {
            os.path.basename(prep["materiau"][0]): idn.sha256_fichier(prep["materiau"][0])}})
        return v41, prep, att

    def argon_guillemets(self, nom):
        """Le script commun d'Argon (`SCRIPT_OK`), dont les fiches portent des guillemets « » et “ ”."""
        fiche = json.dumps(fiche_brute(nom="Argon A", enonce=self.GUILLEMETS + "?", piege="« piège » “anglais”"),
                           ensure_ascii=False)
        script = TestCommandeExterne.SCRIPT_OK.replace(repr(TestCommandeExterne.FICHE), repr(fiche), 1)
        self.assertNotEqual(script, TestCommandeExterne.SCRIPT_OK)
        return self.v43().v41().script(script, nom)

    def test_v45_1_fiche_et_temoin_a_guillemets_servis_aux_juges(self):
        """Une fiche et un témoin à guillemets « » et “ ” : anonymisés sans erreur (v44 : `JSONDecodeError`), chaque valeur
        normalisée comme avant (`normaliser_typographie`), structure intacte (mêmes clés, mêmes listes) ; la consigne du
        juge se relit en JSON."""
        fiche = idn.valider_fiche_ideation(fiche_brute(nom="Fiche « A »", enonce=self.GUILLEMETS + "?",
                                                       anteriorite=[{"reference": "“Where” 2601.1", "statut": "RAPPORTE"}]),
                                           "opus", 1)
        p = os.path.join(self.tmp, "temoins-v45.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.temoins_guillemets(), f, ensure_ascii=False)
        temoins = idn.charger_temoins(p, idn.construire_liste_blanche([p], os.path.join(self.tmp, "lb-v45.json")))
        toutes = [fiche] + temoins
        anonymes, cle = idn.anonymiser(toutes, 7, "juge-v45")
        self.assertEqual(len(anonymes), 5)
        par_auteur = {cle[a["identifiant"]]: a for a in anonymes}

        def attendu(o):
            if isinstance(o, str):
                return idn.normaliser_typographie(o)
            if isinstance(o, list):
                return [attendu(x) for x in o]
            if isinstance(o, dict):
                return {k: attendu(v) for k, v in o.items()}
            return o
        for f in toutes:
            a = dict(par_auteur[f["identifiant_auteur"]])
            ident = a.pop("identifiant")
            self.assertRegex(ident, r"^T0[1-5]$")
            self.assertEqual(a, attendu(idn.vue_servie(f)))
            self.assertEqual(sorted(a), sorted(idn.vue_servie(f)))
        a = par_auteur[fiche["identifiant_auteur"]]
        self.assertEqual(a["nom"], 'Fiche " A "')
        self.assertTrue(a["enonce"].startswith('Le " moniteur " dit "diffus" - l\'écart... '))
        self.assertEqual(a["anteriorite"], [{"reference": '"Where" 2601.1', "statut": "RAPPORTE"}])
        texte = json.dumps(anonymes, ensure_ascii=False)
        for c in "«»“”’—…":
            self.assertNotIn(c, texte)
        self.assertEqual(json.loads(texte), anonymes)

    def test_v45_2_mesurer_consignes_temoins_a_guillemets(self):
        """`--mesurer-consignes` avec des témoins à guillemets → code 0 (v44 : code 2, `JSONDecodeError`), aucun appel."""
        import unittest.mock
        from pole.adaptateurs import AdaptateurCommandeExterne
        v41, prep, att = self.prep_guillemets()
        argon = self.argon_guillemets("argon-v45-2.py")
        sortie = os.path.join(self.tmp, "l-v45-2")

        def piege(*a, **k):
            raise AssertionError("aucun appel ne doit partir")
        lanceur = v41.lanceur()
        with unittest.mock.patch.object(lanceur.AdaptateurIdeationSimule, "lancer", piege), \
                unittest.mock.patch.object(AdaptateurCommandeExterne, "lancer", piege):
            code, out, err = v41.principal(lanceur, v41.base(sortie, prep, att, "--commande-externe", argon,
                                                             "--mesurer-consignes"))
        self.assertEqual(code, 0, err)
        self.assertGreater(json.loads(out)["consignes"]["consigne_du_juge_maximale"], 0)
        self.assertFalse(os.path.exists(sortie) or os.path.exists(sortie + "-controle"))

    def test_v45_3_course_simulee_complete_a_guillemets(self):
        """Course simulée complète (passe 1, passe 2, Argon proposeur ; juges ; classement) avec témoins et fiches d'Argon à
        guillemets → code 0, classement écrit (v44 : code 2 après les passes, avant le premier juge, sans classement)."""
        v41, prep, att = self.prep_guillemets()
        argon = self.argon_guillemets("argon-v45-3.py")
        sortie = os.path.join(self.tmp, "l-v45-3")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe", argon))
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, "manifeste-fin.json"), encoding="utf-8") as f:
            fin = json.load(f)["reglages"]
        self.assertIsNone(fin["erreur"])
        self.assertEqual(fin["lecture"]["juges_rendus"], 2)
        self.assertTrue(fin["lecture"]["temoins"]["temoins_ok"])
        with open(os.path.join(sortie, "fiches-validees.json"), encoding="utf-8") as f:
            self.assertIn("« piège » “anglais”", f.read())  # la fiche d'Argon à guillemets est bien passée aux juges
        with open(os.path.join(sortie, "notes-par-juge.json"), encoding="utf-8") as f:
            self.assertTrue(json.load(f))
        # bras rapporté différé (juge externe) : anonymisation chez le juge externe, puis classement écrit
        att_lecture = v41.cmd().attester(os.path.join(self.tmp, "att-v45-3.json"), sortie, "argon-j")
        code, out, err = v41.principal(v41.lanceur(), [sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine",
                                                       att_lecture, "--juge-externe", "argon-j=gemini-argon",
                                                       "--commande-externe", argon])
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, "classement.json"), encoding="utf-8") as f:
            lignes = json.load(f)["lignes"]
        self.assertTrue(lignes)
        self.assertTrue(all(l["nombre_juges"] == 3 for l in lignes))

# --- v46 : tour (c) « outils clôturés » (décisions de Lazar du 29 octobre 2026, R-433, R-434, R-441, R-444, R-448) et
# corrections de la contre-lecture CL12 de la v45 (CL45-01 : TestV45 et TestV46 avant `unittest.main()` ; CL45-02 :
# caviardage valeur par valeur après l'analyse JSON). En préparation hors ligne : moteur simulé, Argon factice qui émet des
# demandes, faux kit qui passe ses appels d'outils par le vrai crochet ; aucune session réelle, aucun réseau, aucune clé.
# Un essai par point : (1) dossier fermé ; (2) outils confinés du kit et épreuves R5 du crochet ; (3) outils par protocole ;
# (4) aucun nombre de tours, plafonds de sûreté, garde-fou (incident), avertissement de budget ; (5) mesures au manifeste
# de fin seulement ; (6) cache partagé ; (7) citations vérifiées (L7) ; (8) moisson refusée ; rétrocompatibilité.
import asyncio  # noqa: E402
import time  # noqa: E402

from pole import dossier_ferme as dfm  # noqa: E402
from pole.adaptateurs import AdaptateurCommandeExterne, reglages_kit_par_role  # noqa: E402
from pole.garde_outils import evaluer_appel, evaluer_appel_lecture, fabriquer_crochet_lecture  # noqa: E402
from pole.outils import extraire_bloc_json  # noqa: E402

PAGE_2 = "Le taux de détection atteint 0,73 sur les épisodes diffus."
TEXTE_A = ("# Extrait A\n[p.1] Introduction : moniteurs et menaces diffuses.\n"
           "[p.2] " + PAGE_2 + "\nUne seconde ligne de la page deux.\n"
           "[p.3] Conclusion : la borne tient à dix familles.\n")
TEXTE_B = "Extrait B, page une : grille de mesure bêta.\fExtrait B, page deux : le taux de rappel.\f"
CITATION_JUSTE = "« Le taux de détection atteint 0,73 » [extrait-a.md, p.2]"
CITATION_FAUSSE = "« un passage inventé de toutes pièces » [extrait-a.md, p.3]"
CITATION_ABSENTE = "[extrait-a.md, p.9]"


def fiche_citante(nom):
    return fiche_brute(nom=nom, anteriorite=[{"reference": CITATION_JUSTE + " ; " + CITATION_FAUSSE + " ; " + CITATION_ABSENTE,
                                              "statut": "RAPPORTE"}])


# Argon factice : à chaque tour, lit dans la consigne le nombre de tours déjà servis ; joue le scénario (demandes, version
# provisoire), puis rend ses fiches ; « toujours » : demande sans fin (garde-fou) ; coût = min(cout, part × plafond restant)
SCRIPT_ARGON = r'''
import sys, json, os, re, time
c = sys.stdin.read()
plafond = float(os.environ.get('PLAFOND_SESSION_USD', '1'))
role = os.environ.get('ROLE_POLE')
S = json.loads(%(scenario)r)
def sortir(t, cout):
    with open(%(journal)r, 'a') as j:
        j.write(json.dumps({'role': role, 'taille': len(c), 'plafond': plafond, 'tours_servis': c.count('"tour": '),
                            'avertissement': 'Il te reste' in c, 'passe2': 'première passe' in c}) + '\n')
    print(json.dumps({'texte': t, 'cout_usd': cout})); sys.exit(0)
if c.startswith('Réponds exactement OK'): sortir('OK', 0.001)
if role == 'juge_ideation':
    bloc = json.loads(re.search(r'```json\n(\[.*\])\n```', c, re.S).group(1)); par_nom = {f['nom']: f['identifiant'] for f in bloc}
    notes = []
    for f in bloc:
        k = {x: 2 for x in ('avantage', 'originalite', 'falsifiabilite', 'traitabilite', 'robustesse')}
        if f['nom'] in ('Verbeux vide', 'Assuré occupé'): k.update({'avantage': 1, 'originalite': 0, 'falsifiabilite': 0})
        notes.append({'identifiant': f['identifiant'], 'criteres': k, 'justifications': {}})
    sortir('```json\n' + json.dumps({'notes': notes, 'doublons': [[par_nom['Jumeau'], par_nom['Sobre fort']]]}) + '\n```', 0.01)
time.sleep(S.get('dormir', 0))
n = c.count('"tour": ')
cout = min(S.get('cout', 0.05), S.get('part', 0.5) * plafond)
fiche = S['fiche']
if 'première passe' in c: fiche = dict(fiche, nom=fiche['nom'] + ' revue')
if S.get('toujours') or n < len(S['tours']):
    t = {'demandes': [{'lire': 'extrait-a.md', 'pages': [1, 1]}]} if S.get('toujours') else S['tours'][n]
    texte = '```json\n' + json.dumps({'demandes': t['demandes']}, ensure_ascii=False) + '\n```'
    if t.get('version'):
        texte += '\n```json\n' + json.dumps({'fiches': [dict(fiche, nom=fiche['nom'] + ' brouillon')]}, ensure_ascii=False) + '\n```'
    sortir(texte, cout)
sortir('```json\n' + json.dumps({'fiches': [fiche]}, ensure_ascii=False) + '\n```', cout)
'''


class FauxProtocole:
    """Proposeur Claude par protocole (en processus) : même scénario que l'Argon factice ; juge : notes qui tiennent les
    témoins ; consigne chaque appel et ses arguments de lecture."""
    nom = "faux-protocole"

    def __init__(self, scenarios, juge, dormir=0.0):
        self.scenarios, self.juge, self.dormir = scenarios, juge, dormir
        self.appels = []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, **lecture):
        self.appels.append({"role": role, "consigne": consigne, "dossier": dossier, "budget": budget_usd,
                            "max_tours": max_tours, "lecture": lecture})
        if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
            return Resultat("OK", [], 0.01, "ok")
        if role == "juge_ideation":
            idents = sorted(set(re.findall(r'"identifiant": "(T\d\d)"', consigne)))
            return Resultat("```json\n" + json.dumps(self.juge(idents, consigne)) + "\n```", [], 0.1, "ok")
        time.sleep(self.dormir)
        etiquette = dossier.split(os.sep)[-3]
        s = self.scenarios[etiquette]
        n = consigne.count('"tour": ')
        if n < len(s["tours"]):
            return Resultat("```json\n" + json.dumps({"demandes": s["tours"][n]["demandes"]}, ensure_ascii=False) + "\n```",
                            [], s.get("cout", 0.05), "ok")
        return Resultat("```json\n" + json.dumps({"fiches": [s["fiche"]]}, ensure_ascii=False) + "\n```", [],
                        s.get("cout", 0.05), "ok")


class FauxKit:
    """Faux kit d'agent : pour un proposeur à outils, construit les vraies options (`construire_options`, racine de lecture,
    crochet de lecture seule) et passe chaque appel d'outil scripté par le vrai crochet ; un `Read` admis lit le fichier
    pour de bon. Juges : notes qui tiennent les témoins. Rend le journal du crochet comme l'adaptateur réel."""
    nom = "faux-kit"

    def __init__(self, sortie, appels_outils, juge, fiche, ecrire_dans_copie=False, depense=None):
        self.sortie, self.appels_outils, self.juge, self.fiche = sortie, appels_outils, juge, fiche
        self.ecrire_dans_copie, self.depense = ecrire_dans_copie, depense
        self.appels, self.lus, self.decisions = [], [], []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, **lecture):
        self.appels.append({"role": role, "consigne": consigne, "dossier": dossier, "max_tours": max_tours, "lecture": lecture})
        if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
            return Resultat("OK", [], 0.01, "ok")
        if role == "juge_ideation":
            idents = sorted(set(re.findall(r'"identifiant": "(T\d\d)"', consigne)))
            return Resultat("```json\n" + json.dumps(self.juge(idents, consigne)) + "\n```", [], 0.1, "ok")
        racine = lecture["racine_lecture"]
        o = construire_options(dossier, budget_usd, max_tours, url_relais="http://127.0.0.1:8787", modele=modele, role=role,
                               interdire_lecture=[self.sortie], racine_lecture=racine,
                               max_demandes_lecture=lecture["max_demandes_lecture"], lire_depense=self.depense)
        self.options = o
        crochet = o["crochets"]["PreToolUse"][0]["crochet"]
        for outil, entree in self.appels_outils(racine):
            sortie = asyncio.run(crochet({"tool_name": outil, "tool_input": entree}, "id", None))
            self.decisions.append((outil, entree, sortie))
            if not sortie and outil == "Read":
                with open(entree["file_path"], encoding="utf-8") as f:
                    self.lus.append(f.read())
        if self.ecrire_dans_copie:
            with open(os.path.join(racine, "extrait-a.md"), "a", encoding="utf-8") as f:
                f.write("altéré\n")
        texte = "```json\n" + json.dumps({"fiches": [self.fiche]}, ensure_ascii=False) + "\n```"
        return Resultat(texte, [], 0.2, "ok", journal_outils=list(crochet.journal), incident_outils=crochet.incident,
                        avertissement_outils=crochet.avertissement)


class TestV46(CasAvecDossier):
    """v46 : tour (c) « outils clôturés » en préparation, et corrections de CL12 (voir le commentaire qui précède)."""

    # --- préparation ---------------------------------------------------------------------------------------------------

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def v41(self):
        t = TestV41("test_tolerances_separees")
        t.tmp = self.tmp
        return t

    def ecrire_dossier(self, nom="dossier-ferme", index=True, pages_a=3):
        d = os.path.join(self.tmp, nom)
        os.makedirs(d)
        with open(os.path.join(d, "extrait-a.md"), "w", encoding="utf-8") as f:
            f.write(TEXTE_A)
        os.makedirs(os.path.join(d, "sous"))
        with open(os.path.join(d, "sous", "extrait-b.md"), "w", encoding="utf-8") as f:
            f.write(TEXTE_B)
        if index:
            dfm.ecrire_index(d, [{"chemin": "extrait-a.md", "titre": "Extrait A", "resume": "Résumé de l'extrait A",
                                  "sections": ["Introduction", "Résultats"], "pages": pages_a},
                                 {"chemin": "sous/extrait-b.md", "titre": "Extrait B", "resume": "Résumé B"}])
        return d

    def preparer(self, dossier=None):
        """Pièces des essais (TestCourse) et une liste blanche qui porte aussi l'index du dossier fermé."""
        if not hasattr(self, "_base"):
            self._base = self.cours().preparer()  # liste blanche des pièces écrite une fois (jamais écrasée)
        prep = dict(self._base)
        dossier = dossier or self.ecrire_dossier()
        lb = os.path.join(self.tmp, "lb-v46-" + os.path.basename(dossier) + ".json")
        idn.construire_liste_blanche([prep["question"], prep["pieces"][0], prep["materiau"][0], prep["temoins"],
                                      os.path.join(dossier, "index.json")], lb)
        return dict(prep, liste_blanche=lb), dossier

    def budgets(self, argon=True):
        b = dict(self.cours().budgets())
        if argon:
            b[("proposeur_ideation", "gemini-argon")] = 1.0
        return b

    def course(self, ad, nom, prep, dossier, argon=None, **modifs):
        args = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"],
                    temoins=prep["temoins"], proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")],
                    graine=7, budget_total_usd=20.0, budgets=self.budgets(), dossier_ferme=dossier)
        if argon is not None:
            args.update(proposeurs_externes=[("argon", "gemini-argon", argon)], budget_externe_usd=3.0)
        args.update(modifs)
        return idn.executer_ideation(ad, os.path.join(self.tmp, nom), **args)

    def argon(self, scenario, nom):
        journal = os.path.join(self.tmp, nom + ".journal")
        script = SCRIPT_ARGON % {"scenario": json.dumps(scenario, ensure_ascii=False), "journal": journal}
        cmd = TestCommandeExterne("test_commande_factice_notes_et_controle")
        cmd.tmp = self.tmp
        return AdaptateurCommandeExterne(cmd.commande(script, nom + ".py"), environnement={}), journal, cmd.commande(script, nom + ".py")

    @staticmethod
    def lignes(journal):
        with open(journal, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    @staticmethod
    def lire(chemin):
        with open(chemin, encoding="utf-8") as f:
            return f.read()

    def fin(self, nom):
        return json.loads(self.lire(os.path.join(self.tmp, nom, "manifeste-fin.json")))["reglages"]

    def consignes_des_juges(self, nom):
        base = os.path.join(self.tmp, nom)
        trouves = []
        for racine, _, fichiers in os.walk(base):
            for f in fichiers:
                if f in ("consigne.md", "consigne-en-attente.md") and "juges" in racine:
                    trouves.append(self.lire(os.path.join(racine, f)))
        return trouves

    # --- point 1 : dossier fermé ---------------------------------------------------------------------------------------

    def test_v46_1_dossier_ferme_index_scelle_empreintes_et_artefacts(self):
        """Cas sain : le dossier est chargé (pages par `[p.N]` et par saut de page), la consigne porte l'index (titre,
        résumé, taille, pages, sections) et **jamais le texte** ; `taille_max_pieces` ne s'applique pas au dossier (pièces
        de 30 caractères au plus, dossier plus grand : accepté). Artefacts (R5), tous refusés **avant tout appel** (aucun
        appel, SORTIE jamais créée) : fichier en plus, fichier absent, empreinte changée, index non scellé, index hors de la
        liste blanche, lien symbolique, chemin remontant dans l'index, fichier non texte (octets d'un PDF), secret, nombre
        de pages faux, fragment interdit."""
        prep, dossier = self.preparer()
        d = dfm.charger_dossier_ferme(dossier, idn.charger_liste_blanche(prep["liste_blanche"]))
        self.assertEqual(sorted(d.fichiers["extrait-a.md"]["pages"]), [1, 2, 3])
        self.assertIn(PAGE_2, d.page("extrait-a.md", 2))
        self.assertEqual(sorted(d.fichiers["sous/extrait-b.md"]["pages"]), [1, 2])
        self.assertEqual(d.pages_total, 5)
        index = json.dumps(d.vue_index(), ensure_ascii=False)
        for attendu in ("Extrait A", "Résumé de l'extrait A", "taille_caracteres", "Résultats"):
            self.assertIn(attendu, index)
        ad = FauxKit(os.path.join(self.tmp, "c1"), lambda r: [], self.cours().notes_temoins_ok, fiche_brute(nom="O1"))
        res = self.course(ad, "c1", prep, dossier, taille_max_pieces=30)
        consigne = ad.appels[0]["consigne"]
        self.assertIn("Le dossier fermé (index seulement", consigne)
        self.assertIn("Résumé de l'extrait A", consigne)
        self.assertNotIn(PAGE_2, consigne)
        self.assertNotIn("grille de mesure bêta", consigne)
        self.assertEqual(len(res["fiches"]), 1)
        depart = json.loads(self.lire(os.path.join(self.tmp, "c1", "manifeste-depart.json")))["reglages"]
        self.assertEqual(depart["dossier_ferme"]["index_sha256"], d.index_sha256)
        self.assertEqual(depart["dossier_ferme"]["mode_claude"], "outils")

        def refuse(nom, modifier, motif):
            p2, d2 = self.preparer(self.ecrire_dossier(nom))
            modifier(d2, p2)
            faux = FauxKit(os.path.join(self.tmp, "s-" + nom), lambda r: [], self.cours().notes_temoins_ok, fiche_brute())
            with self.assertRaises(idn.CourseInterrompue, msg=nom) as ctx:
                self.course(faux, "s-" + nom, p2, d2)
            self.assertIn(motif, str(ctx.exception), nom)
            self.assertEqual(faux.appels, [], nom)
            self.assertFalse(os.path.exists(os.path.join(self.tmp, "s-" + nom)), nom)

        def ajouter(d2, _):
            with open(os.path.join(d2, "intrus.md"), "w") as f:
                f.write("x")

        def retirer(d2, _):
            os.remove(os.path.join(d2, "sous", "extrait-b.md"))

        def changer(d2, _):
            with open(os.path.join(d2, "extrait-a.md"), "a") as f:
                f.write("changé")

        def desceller(d2, _):
            with open(os.path.join(d2, "index.json.sha256"), "w") as f:
                f.write("0" * 64 + "  index.json\n")

        def lien(d2, _):
            os.symlink("/etc/hostname", os.path.join(d2, "lien.md"))

        def reindexer(d2, p2, entrees):
            os.remove(os.path.join(d2, "index.json"))
            os.remove(os.path.join(d2, "index.json.sha256"))
            dfm.ecrire_index(d2, entrees)
            idn.construire_liste_blanche([p2["question"], p2["pieces"][0], p2["temoins"], os.path.join(d2, "index.json")],
                                         p2["liste_blanche"] + ".2.json")
            p2["liste_blanche"] = p2["liste_blanche"] + ".2.json"

        def pdf(d2, p2):
            with open(os.path.join(d2, "extrait-a.md"), "wb") as f:
                f.write(b"%PDF-1.7\n\xff\xfe\x00\x81binaire")
            reindexer(d2, p2, [{"chemin": "extrait-a.md", "titre": "A", "resume": "r"},
                               {"chemin": "sous/extrait-b.md", "titre": "B", "resume": "r"}])

        def secret(d2, p2):
            with open(os.path.join(d2, "extrait-a.md"), "w") as f:
                f.write("clé : " + "sk-" + "ant-" + "abcdefghijklmnopqrstu\n")
            reindexer(d2, p2, [{"chemin": "extrait-a.md", "titre": "A", "resume": "r"},
                               {"chemin": "sous/extrait-b.md", "titre": "B", "resume": "r"}])

        def remontant(d2, p2):
            reindexer(d2, p2, [{"chemin": "extrait-a.md", "titre": "A", "resume": "r"},
                               {"chemin": "sous/../sous/extrait-b.md", "titre": "B", "resume": "r"}])

        def interdit(d2, p2):
            os.rename(os.path.join(d2, "extrait-a.md"), os.path.join(d2, "donnees-a.md"))
            reindexer(d2, p2, [{"chemin": "donnees-a.md", "titre": "A", "resume": "r"},
                               {"chemin": "sous/extrait-b.md", "titre": "B", "resume": "r"}])

        def hors_liste(d2, p2):
            idn.construire_liste_blanche([p2["question"], p2["pieces"][0], p2["temoins"]], p2["liste_blanche"] + ".3.json")
            p2["liste_blanche"] = p2["liste_blanche"] + ".3.json"

        refuse("plus", ajouter, "non listés")
        refuse("moins", retirer, "absents")
        refuse("change", changer, "empreinte différente de l'index")
        refuse("descelle", desceller, "non scellé")
        refuse("lien", lien, "lien symbolique")
        refuse("pdf", pdf, "pas un texte UTF-8")
        refuse("secret", secret, "secret")
        refuse("remonte", remontant, "chemin relatif propre")
        refuse("interdit", interdit, "'donnees'")
        refuse("horsliste", hors_liste, "hors de la liste blanche")
        p3, d3 = self.preparer(self.ecrire_dossier("pages", pages_a=4))
        with self.assertRaisesRegex(idn.CourseInterrompue, "déclare 4 pages, 3 trouvées"):
            self.course(FauxKit(self.tmp, lambda r: [], None, fiche_brute()), "s-pages", p3, d3)

    # --- point 2 : outils confinés du kit, épreuves R5 ---------------------------------------------------------------

    def test_v46_2_outils_confines_du_kit_et_epreuves_r5_du_crochet(self):
        """Options : proposeur à dossier fermé → `tools` = `allowed_tools` = Read, Grep, Glob, dossier courant = la racine
        de lecture, crochet de lecture seule ; juge → toujours aucun outil (racine refusée) ; sans dossier : `tools=[]`
        comme en v45 ; ligne de commande du kit (jamais exécutée) : `--tools Read,Grep,Glob`, juge `--tools ''`.
        Crochet, cas sain : lecture d'un fichier du dossier et recherche d'un motif (Grep, Glob) admises. Artefacts, tous
        refusés avec motif : `Read /etc/passwd`, `Glob {"pattern": "/etc/*"}`, `Grep {"glob": "/root/**"}`, `Read` d'un
        lien symbolique vers l'extérieur, chemins à `..`, `~`, accolades, `path` hors racine, paramètre inconnu, `Write`,
        `Edit`, `MultiEdit`, `Bash`, `WebFetch`, `Task`, `mcp__…`. La garde générale (`evaluer_appel`, autres rôles)
        refuse aussi `Glob /etc/*` et `Grep glob /root/**` (v45 : admis). Garde-fou du crochet (incident) et avertissement
        de budget (« il te reste … : rends ta fiche »). Course : copie du dossier vérifiée par empreinte, appels consignés,
        juges sans argument de lecture ; copie altérée → incident dit, jamais silencieux."""
        dossier_agent = self.sous_dossier("course", "proposeurs", "opus", "passe-1")
        d = dfm.charger_dossier_ferme(self.ecrire_dossier())
        racine = os.path.join(dossier_agent, "lecture")
        d.copier_vers(racine)
        dehors = os.path.join(self.tmp, "secret-dehors.txt")
        with open(dehors, "w") as f:
            f.write("secret")
        os.symlink(dehors, os.path.join(racine, "lien-dehors.md"))
        interdits = [os.path.join(self.tmp, "course")]
        o = construire_options(dossier_agent, 1.0, 50, url_relais="http://127.0.0.1:8787", modele="claude-opus-5-5",
                               role="proposeur_ideation", interdire_lecture=interdits, racine_lecture=racine)
        self.assertEqual((o["tools"], o["allowed_tools"], o["cwd"]), (["Read", "Grep", "Glob"], ["Read", "Grep", "Glob"], racine))
        self.assertIn("Read, Grep et Glob", o["system_prompt"])
        juge = os.path.join(self.tmp, "course", "juges", "j")
        os.makedirs(juge)
        with self.assertRaises(ValueError):
            construire_options(juge, 1.0, 2, url_relais="http://127.0.0.1:8787", role="juge_ideation",
                               interdire_lecture=interdits, racine_lecture=racine)
        o_sans = construire_options(dossier_agent, 1.0, 2, url_relais="http://127.0.0.1:8787", role="proposeur_ideation",
                                    interdire_lecture=interdits)
        self.assertEqual((o_sans["tools"], o_sans["cwd"]), ([], dossier_agent))
        o_proto = construire_options(dossier_agent, 1.0, 2, url_relais="http://127.0.0.1:8787", role="proposeur_ideation",
                                     interdire_lecture=interdits, mode_lecture="protocole")
        self.assertEqual(o_proto["tools"], [])
        self.assertIn("bloc JSON {demandes}", o_proto["system_prompt"])
        self.assertEqual(reglages_kit_par_role("outils")["proposeur_ideation"]["tools"], ["Read", "Grep", "Glob"])
        self.assertEqual(reglages_kit_par_role("outils")["juge_ideation"]["tools"], [])
        self.assertEqual(reglages_kit_par_role("protocole")["proposeur_ideation"]["tools"], [])
        self.assertEqual(reglages_kit_par_role()["proposeur_ideation"]["tools"], [])
        try:
            import claude_agent_sdk as sdk
            from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
        except ImportError:
            sdk = None
        if sdk is not None:
            from pole.adaptateurs import AdaptateurClaudeSDK
            for opts, attendu in ((o, "Read,Grep,Glob"), (construire_options(juge, 1.0, 2, url_relais="http://127.0.0.1:8787",
                                                                               role="juge_ideation", interdire_lecture=interdits), "")):
                options = AdaptateurClaudeSDK.options_sdk(sdk, opts)
                options.cli_path = "/bin/true"
                cmd = SubprocessCLITransport("x", options)._build_command()
                self.assertEqual(cmd[cmd.index("--tools") + 1], attendu)
            for nom in [n for n in sys.modules if n.startswith("claude_agent_sdk")]:
                del sys.modules[nom]
        # crochet : cas sain
        fichier = os.path.join(racine, "extrait-a.md")
        sains = [("Read", {"file_path": fichier}), ("Read", {"file_path": "sous/extrait-b.md", "offset": 1, "limit": 5}),
                 ("Grep", {"pattern": "taux", "path": racine}), ("Grep", {"pattern": "taux", "glob": "*.md", "-i": True}),
                 ("Glob", {"pattern": "**/*.md"}), ("Glob", {"pattern": racine + "/sous/*.md"})]
        for outil, entree in sains:
            self.assertEqual(evaluer_appel_lecture(outil, entree, racine)[0], True, (outil, entree))
        artefacts = [("Read", {"file_path": "/etc/passwd"}), ("Glob", {"pattern": "/etc/*"}),
                     ("Grep", {"pattern": "cle", "glob": "/root/**"}), ("Read", {"file_path": os.path.join(racine, "lien-dehors.md")}),
                     ("Read", {"file_path": os.path.join(racine, "..", "..", "traces-passe-1", "consigne.md")}),
                     ("Read", {"file_path": os.path.join(racine, "sous", "..", "extrait-a.md")}),
                     ("Read", {"file_path": "~/.bashrc"}), ("Glob", {"pattern": "../*"}), ("Glob", {"pattern": "~/*"}),
                     ("Glob", {"pattern": "{x,/etc}/*"}), ("Glob", {"pattern": "*", "path": "/etc"}),
                     ("Grep", {"pattern": "x", "path": "/root"}), ("Grep", {"pattern": "x", "glob": "../**"}),
                     ("Read", {"file_path": fichier, "inconnu": 1}), ("Read", {}),
                     ("Write", {"file_path": fichier, "content": "x"}), ("Edit", {"file_path": fichier}),
                     ("MultiEdit", {"file_path": fichier}), ("Bash", {"command": "cat extrait-a.md"}),
                     ("WebFetch", {"url": "https://exemple.org"}), ("Task", {}), ("Agent", {}), ("mcp__serveur__outil", {})]
        for outil, entree in artefacts:
            autorise, motif = evaluer_appel_lecture(outil, entree, racine)
            self.assertFalse(autorise, (outil, entree, motif))
            self.assertTrue(motif)
        # garde générale des autres rôles : les deux trous de la note de conception fermés
        self.assertFalse(evaluer_appel("Glob", {"pattern": "/etc/*"}, dossier_agent)[0])
        self.assertFalse(evaluer_appel("Grep", {"pattern": "cle", "glob": "/root/**"}, dossier_agent)[0])
        self.assertTrue(evaluer_appel("Glob", {"pattern": "**/*.py"}, dossier_agent)[0])
        # crochet : garde-fou anti-boucle et avertissement de budget
        crochet = fabriquer_crochet_lecture(racine, max_demandes=2)
        sorties = [asyncio.run(crochet({"tool_name": "Read", "tool_input": {"file_path": fichier}}, "i", None)) for _ in range(3)]
        self.assertEqual(sorties[:2], [{}, {}])
        self.assertEqual(sorties[2]["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("garde-fou anti-boucle", sorties[2]["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertEqual(crochet.incident["type"], "garde-fou anti-boucle")
        crochet = fabriquer_crochet_lecture(racine, lire_depense=lambda: 0.85, plafond_usd=1.0)
        s = asyncio.run(crochet({"tool_name": "Read", "tool_input": {"file_path": fichier}}, "i", None))
        self.assertIn("il te reste 0.15 USD : rends ta fiche", s["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertEqual(asyncio.run(crochet({"tool_name": "Read", "tool_input": {"file_path": fichier}}, "i", None)), {})
        self.assertAlmostEqual(crochet.avertissement["reste_usd"], 0.15)
        # course à outils du kit (faux kit, vrai crochet)
        prep, dossier = self.preparer(self.ecrire_dossier("dossier-c2"))

        def appels(r):
            return [("Read", {"file_path": os.path.join(r, "extrait-a.md")}), ("Grep", {"pattern": "taux", "path": r}),
                    ("Read", {"file_path": "/etc/passwd"}), ("Glob", {"pattern": "/etc/*"}),
                    ("Grep", {"pattern": "x", "glob": "/root/**"}), ("Write", {"file_path": os.path.join(r, "x.md")}),
                    ("Bash", {"command": "ls"})]
        sortie = os.path.join(self.tmp, "c2")
        kit = FauxKit(sortie, appels, self.cours().notes_temoins_ok, fiche_citante("O1"))
        res = self.course(kit, "c2", prep, dossier)
        self.assertEqual(len(res["fiches"]), 1)
        self.assertEqual(kit.lus, [TEXTE_A])  # une seule lecture admise, celle du dossier
        refus = [(o_, e_) for o_, e_, s_ in kit.decisions if s_]
        self.assertEqual([o_ for o_, _ in refus], ["Read", "Glob", "Grep", "Write", "Bash"])
        prop = [a for a in kit.appels if a["role"] == "proposeur_ideation"][0]
        self.assertEqual(prop["lecture"]["racine_lecture"], os.path.join(sortie, "proposeurs", "opus", "passe-1", "lecture"))
        self.assertEqual(prop["max_tours"], dfm.MAX_DEMANDES_LECTURE_DEFAUT + 5)
        self.assertTrue(all(a["lecture"] == {} for a in kit.appels if a["role"] == "juge_ideation"))
        fin = self.fin("c2")
        copie = fin["journal"]["copies_dossier_ferme"][0]
        self.assertEqual(copie["empreintes"]["extrait-a.md"], dfm.charger_dossier_ferme(dossier).fichiers["extrait-a.md"]["sha256"])
        m = fin["mesures_lecture"]["par_proposeur"]["opus"]["passe-1"]
        self.assertEqual(m["mode"], "outils")
        self.assertEqual((m["demandes"]["total"], m["demandes"]["refusees"], m["demandes"]["lire"]), (7, 5, 2))
        self.assertEqual(sorted({p["page"] for p in m["pages_lues"]}), [1, 2, 3])
        self.assertEqual(fin["journal"]["incidents"], [])
        depart = json.loads(self.lire(os.path.join(sortie, "manifeste-depart.json")))["reglages"]
        self.assertEqual(depart["reglages_kit"]["proposeur_ideation"]["tools"], ["Read", "Grep", "Glob"])
        self.assertEqual(depart["reglages_kit"]["juge_ideation"]["tools"], [])
        # copie altérée pendant la session : incident dit (R5), la course continue, fiches lues avec réserve
        kit2 = FauxKit(os.path.join(self.tmp, "c2b"), lambda r: [], self.cours().notes_temoins_ok, fiche_brute(nom="O1"),
                       ecrire_dans_copie=True)
        self.course(kit2, "c2b", prep, dossier)
        inc = self.fin("c2b")["journal"]["incidents"]
        self.assertEqual(inc[0]["type"], "copie du dossier fermé altérée")
        self.assertEqual(inc[0]["ecarts"], [{"chemin": "extrait-a.md", "ecart": "empreinte différente"}])
        # garde-fou franchi dans le kit : incident, session et course arrêtées
        kit3 = FauxKit(os.path.join(self.tmp, "c2c"), lambda r: [("Read", {"file_path": os.path.join(r, "extrait-a.md")})] * 4,
                       self.cours().notes_temoins_ok, fiche_brute(nom="O1"))
        with self.assertRaisesRegex(idn.CourseInterrompue, "garde-fou anti-boucle"):
            self.course(kit3, "c2c", prep, dossier, max_demandes_lecture=3)
        fin3 = self.fin("c2c")
        self.assertEqual(fin3["journal"]["incidents"][0]["type"], "garde-fou anti-boucle")
        self.assertIn("garde-fou anti-boucle", fin3["erreur"])

    # --- point 3 : outils par protocole -------------------------------------------------------------------------------

    def test_v46_3_outils_par_protocole_argon_et_claude_a_egalite(self):
        """Argon (commande factice) demande une page et une recherche au tour 1 ; le noyau les sert au tour 2 depuis le
        dossier fermé — le texte de la page demandée seulement, et les lignes trouvées avec chemin et page —, rien
        d'autre ; demandes hors du dossier (`/etc/passwd`, `../`, plage vide) refusées avec motif. Claude sous
        `outils_par_protocole` : même mécanisme, **aucun outil du kit** (aucune racine de lecture, `mode_lecture` «
        protocole »). Par le lanceur (moteur simulé, `--dossier-ferme`, seconde passe, puis bras) : code 0, classement à
        trois juges."""
        prep, dossier = self.preparer()
        scenario = {"tours": [{"demandes": [{"lire": "extrait-a.md", "pages": [2, 2]}, {"chercher": "taux"},
                                            {"lire": "/etc/passwd"}, {"lire": "../extrait-a.md"},
                                            {"lire": "extrait-a.md", "pages": [7, 9]}]}],
                    "fiche": fiche_citante("Argon A")}
        argon, journal, _ = self.argon(scenario, "argon-3")
        faux = FauxProtocole({"opus": {"tours": [{"demandes": [{"lire": "sous/extrait-b.md"}]}], "fiche": fiche_brute(nom="O1")}},
                             self.cours().notes_temoins_ok)
        res = self.course(faux, "c3", prep, dossier, argon=argon, outils_par_protocole=True)
        self.assertEqual({f["auteur"] for f in res["fiches"]}, {"argon", "opus"})
        tours = self.lignes(journal)
        self.assertEqual([t["tours_servis"] for t in tours if t["role"] == "proposeur_ideation"], [0, 1])
        c2 = self.lire(os.path.join(self.tmp, "c3", "proposeurs", "argon", "passe-1", "traces-tour-002", "consigne.md"))
        self.assertIn(PAGE_2, c2)
        self.assertNotIn("Introduction : moniteurs", c2)  # page 1 jamais demandée, jamais servie
        self.assertNotIn("grille de mesure bêta", c2)  # l'autre fichier non plus
        self.assertIn('"ligne": "Extrait B, page deux : le taux de rappel."', c2)
        self.assertIn('"chemin": "sous/extrait-b.md"', c2)
        servi = json.loads(re.search(r"Ce que le noyau t'a servi[^\n]*\n+```json\n(.*?)\n```", c2, re.S).group(1))
        statuts = [r["statut"] for r in servi[0]["reponses"]]
        self.assertEqual(statuts, ["servie", "servie", "refusée", "refusée", "refusée"])
        self.assertIn("hors du dossier fermé", servi[0]["reponses"][2]["motif"])
        self.assertEqual({(r["chemin"], r["page"]) for r in servi[0]["reponses"][1]["resultats"]},
                         {("extrait-a.md", 2), ("sous/extrait-b.md", 2)})
        claude = [a for a in faux.appels if a["role"] == "proposeur_ideation"]
        self.assertEqual(len(claude), 2)
        self.assertTrue(all(a["lecture"] == {"mode_lecture": "protocole"} for a in claude))
        self.assertIn("grille de mesure bêta", claude[1]["consigne"])
        depart = json.loads(self.lire(os.path.join(self.tmp, "c3", "manifeste-depart.json")))["reglages"]
        self.assertEqual(depart["reglages_kit"]["proposeur_ideation"]["tools"], [])
        self.assertEqual((depart["dossier_ferme"]["mode_claude"], depart["dossier_ferme"]["mode_externes"]),
                         ("protocole", "protocole"))
        # par le lanceur, moteur simulé : course à dossier fermé, seconde passe, puis bras différé
        v41 = self.v41()
        att = os.path.join(self.tmp, "att-mat-3.json")
        idn.ecrire_json_scelle(att, {"lecteur": "Lazar", "lu_le": "2026-10-29", "materiau_sha256": {
            os.path.basename(prep["materiau"][0]): idn.sha256_fichier(prep["materiau"][0])}})
        idn.construire_liste_blanche([prep["question"], prep["pieces"][0], prep["materiau"][0], prep["temoins"],
                                      os.path.join(dossier, "index.json")], os.path.join(self.tmp, "lb-l3.json"))
        prep_l = dict(prep, liste_blanche=os.path.join(self.tmp, "lb-l3.json"))
        _, _, cmd = self.argon(scenario, "argon-3l")
        sortie = os.path.join(self.tmp, "l3")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep_l, att, "--commande-externe", " ".join(cmd),
                                                               "--dossier-ferme", dossier))
        self.assertEqual(code, 0, err)
        self.assertTrue(os.path.isdir(os.path.join(sortie, "proposeurs", "argon", "passe-2", "tour-002")))
        att_l = v41.cmd().attester(os.path.join(self.tmp, "att-l3.json"), sortie, "argon-j")
        code, out, err = v41.principal(v41.lanceur(), [sortie, "--bras-rapporte-differe", "--attestation-lecture-humaine",
                                                       att_l, "--juge-externe", "argon-j=gemini-argon", "--commande-externe",
                                                       " ".join(cmd)])
        self.assertEqual(code, 0, err)
        lignes = json.loads(self.lire(os.path.join(sortie, "classement.json")))["lignes"]
        self.assertTrue(lignes and all(l["nombre_juges"] == 3 for l in lignes))
        with open(os.path.join(sortie, "juges-bras-rapporte", "traces-argon-j", "consigne-en-attente.md"), encoding="utf-8") as f:
            self.assertIn("citations_verifiees", f.read())

    # --- point 4 : aucun nombre de tours ; plafonds de sûreté --------------------------------------------------------

    def test_v46_4_tours_libres_garde_fou_incident_avertissement_et_delai(self):
        """Aucun nombre de tours fixé : Argon lit sept tours (plus que `MAX_TOURS_IDEATION`) puis rend sa fiche, acceptée.
        Garde-fou : `max_demandes_lecture` = 3 et un Argon qui demande sans fin → arrêt au quatrième tour, **incident** au
        journal et aux mesures (pas un réglage), manifeste de fin en erreur. Avertissement de budget : Argon à 0,45 par
        tour sur un plafond de 1,0 → le troisième tour porte « Il te reste 0.10 USD : rends ta fiche. », la fiche rendue
        est **marquée** sous avertissement, jamais rejetée. Délai de session (`delai_session_s`) sur l'ensemble des tours :
        dépassé → arrêt. Options du lanceur : `--max-demandes-lecture` < 1 ou sans `--dossier-ferme` refusé."""
        prep, dossier = self.preparer()
        juge = self.cours().notes_temoins_ok
        sept = {"tours": [{"demandes": [{"lire": "extrait-a.md", "pages": [1 + k % 3, 1 + k % 3]}]} for k in range(7)],
                "fiche": fiche_brute(nom="Argon A"), "cout": 0.01}
        argon, journal, _ = self.argon(sept, "argon-4a")
        res = self.course(FauxProtocole({"opus": {"tours": [], "fiche": fiche_brute(nom="O1")}}, juge), "c4a", prep, dossier,
                          argon=argon, outils_par_protocole=True)
        self.assertTrue(any(f["auteur"] == "argon" for f in res["fiches"]))
        m = self.fin("c4a")["mesures_lecture"]["par_proposeur"]["argon"]["passe-1"]
        self.assertEqual((m["tours"], m["demandes"]["total"]), (8, 7))
        self.assertGreater(m["tours"], idn.MAX_TOURS_IDEATION)
        # garde-fou anti-boucle
        argon, journal, _ = self.argon({"tours": [], "toujours": True, "fiche": fiche_brute(nom="Argon A"), "cout": 0.01},
                                       "argon-4b")
        with self.assertRaisesRegex(idn.CourseInterrompue, "garde-fou anti-boucle"):
            self.course(FauxProtocole({"opus": {"tours": [], "fiche": fiche_brute(nom="O1")}}, juge), "c4b", prep, dossier,
                        argon=argon, outils_par_protocole=True, max_demandes_lecture=3)
        fin = self.fin("c4b")
        self.assertEqual(len(self.lignes(journal)), 4)  # quatre tours envoyés ; le quatrième n'est pas servi
        incident = fin["journal"]["incidents"][0]
        self.assertEqual((incident["type"], incident["tour"], incident["consigne"]),
                         ("garde-fou anti-boucle", 4, "incident (garde-fou), pas un réglage"))
        self.assertEqual(fin["mesures_lecture"]["incidents"][0]["type"], "garde-fou anti-boucle")
        self.assertIn("garde-fou anti-boucle", fin["erreur"])
        self.assertEqual(fin["mesures_lecture"]["par_proposeur"]["argon"]["passe-1"]["demandes"]["total"], 3)
        # avertissement de budget
        argon, journal, _ = self.argon({"tours": [{"demandes": [{"lire": "extrait-a.md", "pages": [1, 1]}]},
                                                  {"demandes": [{"lire": "extrait-a.md", "pages": [2, 2]}]}],
                                        "fiche": fiche_brute(nom="Argon A"), "cout": 0.45, "part": 1.0}, "argon-4c")
        res = self.course(FauxProtocole({"opus": {"tours": [], "fiche": fiche_brute(nom="O1")}}, juge), "c4c", prep, dossier,
                          argon=argon, outils_par_protocole=True)
        prop = [t for t in self.lignes(journal) if t["role"] == "proposeur_ideation"]
        self.assertEqual([t["avertissement"] for t in prop], [False, False, True])
        self.assertEqual([round(t["plafond"], 6) for t in prop], [1.0, 0.55, 0.1])
        c3 = self.lire(os.path.join(self.tmp, "c4c", "proposeurs", "argon", "passe-1", "traces-tour-003", "consigne.md"))
        self.assertIn("Il te reste 0.10 USD : rends ta fiche.", c3)
        m = self.fin("c4c")["mesures_lecture"]["par_proposeur"]["argon"]["passe-1"]
        self.assertTrue(m["sous_avertissement"])
        self.assertTrue(any(f["auteur"] == "argon" for f in res["fiches"]))  # jamais rejetée
        self.assertAlmostEqual(res["journal"]["cout_externe_usd"], 1.0)
        # délai de session sur l'ensemble des tours
        lent = FauxProtocole({"opus": {"tours": [{"demandes": [{"chercher": "taux"}]}] * 5, "fiche": fiche_brute(nom="O1")}},
                             juge, dormir=0.15)
        with self.assertRaisesRegex(idn.CourseInterrompue, "délai de session dépassé"):
            self.course(lent, "c4d", prep, dossier, outils_par_protocole=True, delai_session_s=0.2)
        self.assertLess(len([a for a in lent.appels if a["role"] == "proposeur_ideation"]), 5)
        # options du lanceur
        v41 = self.v41()
        for argv in (["s", "--max-demandes-lecture", "5"], ["s", "--dossier-ferme", dossier, "--max-demandes-lecture", "0"]):
            with self.assertRaises(SystemExit):
                v41.principal(v41.lanceur(), argv)

    # --- point 5 : mesures au manifeste de fin seulement --------------------------------------------------------------

    def test_v46_5_mesures_de_lecture_au_manifeste_de_fin_jamais_aux_juges(self):
        """Par proposeur et par passe : pages lues dans l'ordre (chemin, page, tour), répétitions, nombre de demandes par
        type, versions de la fiche (une version provisoire rendue avec des demandes, puis la finale : deux versions,
        distance > 0), part du dossier lu ; au manifeste de fin seulement : ni les consignes des juges, ni les fiches
        servies, ni le classement ne les portent (N-053) ; `mesures_convergence` renvoie aux mesures de lecture."""
        prep, dossier = self.preparer()
        scenario = {"tours": [{"demandes": [{"lire": "extrait-a.md", "pages": [2, 3]}], "version": True},
                              {"demandes": [{"lire": "extrait-a.md", "pages": [2, 2]}, {"chercher": "borne"}]}],
                    "fiche": fiche_brute(nom="Argon A"), "cout": 0.01}
        argon, _, _ = self.argon(scenario, "argon-5")
        res = self.course(FauxProtocole({"opus": {"tours": [], "fiche": fiche_brute(nom="O1")}}, self.cours().notes_temoins_ok),
                          "c5", prep, dossier, argon=argon, outils_par_protocole=True)
        fin = self.fin("c5")
        m = fin["mesures_lecture"]["par_proposeur"]["argon"]["passe-1"]
        self.assertEqual([(p["ordre"], p["tour"], p["chemin"], p["page"]) for p in m["pages_lues"]],
                         [(1, 1, "extrait-a.md", 2), (2, 1, "extrait-a.md", 3), (3, 2, "extrait-a.md", 2)])
        self.assertEqual(m["repetitions"], {"extrait-a.md|p.2": 2})
        self.assertEqual(m["demandes"], {"total": 3, "lire": 2, "chercher": 1, "moissonner": 0, "refusees": 0})
        self.assertEqual(m["recherches"][0]["motif"], "borne")
        self.assertEqual(m["versions_fiche"], 2)
        self.assertEqual(len(m["distances_entre_versions"]), 1)
        self.assertGreater(m["distances_entre_versions"][0], 0)
        self.assertEqual((m["pages_distinctes"], m["part_du_dossier_lu"]), (2, 0.4))
        self.assertEqual(fin["mesures_convergence"]["motif_pages_lues"], idn.MOTIF_PAGES_LUES_DOSSIER)
        interdits = ("pages_lues", "part_du_dossier_lu", "repetitions", "versions_fiche", "mesures_lecture", "tours",
                     "sous_avertissement", "Ce que le noyau t'a servi")
        consignes = self.consignes_des_juges("c5")
        self.assertTrue(consignes)
        for c in consignes:
            for mot in interdits:
                self.assertNotIn(mot, c)
            bloc = json.loads(re.search(r"```json\n(\[.*\])\n```", c, re.S).group(1))
            for f in bloc:
                self.assertEqual(set(f) - set(idn.GABARIT), {"identifiant", idn.CHAMP_CITATIONS})
        for nom in ("fiches-validees.json", "notes-par-juge.json", "classement.json", "lecture.json"):
            texte = self.lire(os.path.join(self.tmp, "c5", nom))
            for mot in interdits[:5]:
                self.assertNotIn(mot, texte, nom)
        self.assertEqual(len(res["classement"]), len(res["fiches"]))

    # --- point 6 : cache partagé ---------------------------------------------------------------------------------------

    def test_v46_6_cache_partage_des_pages_servies(self):
        """Une page servie à Argon est servie à Claude depuis le cache : même texte, même empreinte ; chaque service est
        consigné (depuis le cache ou non, à qui, à quel tour) au manifeste de fin."""
        prep, dossier = self.preparer()
        demande = {"tours": [{"demandes": [{"lire": "extrait-a.md", "pages": [2, 2]}]}], "fiche": fiche_brute(nom="Argon A"),
                   "cout": 0.01}
        argon, _, _ = self.argon(demande, "argon-6")
        faux = FauxProtocole({"opus": dict(demande, fiche=fiche_brute(nom="O1"))}, self.cours().notes_temoins_ok)
        self.course(faux, "c6", prep, dossier, argon=argon, outils_par_protocole=True)
        cache = self.fin("c6")["mesures_lecture"]["cache_pages"]
        services = cache["services_detail"]
        self.assertEqual([(s["etiquette"], s["depuis_cache"]) for s in services], [("argon", False), ("opus", True)])
        self.assertEqual(services[0]["sha256"], services[1]["sha256"])
        self.assertEqual(cache["servies_depuis_cache"], 1)
        self.assertEqual(cache["par_page"]["extrait-a.md|p.2"]["servie_a"], ["argon/passe-1/tour-1", "opus/passe-1/tour-1"])
        ca = self.lire(os.path.join(self.tmp, "c6", "proposeurs", "argon", "passe-1", "traces-tour-002", "consigne.md"))
        co = self.lire(os.path.join(self.tmp, "c6", "proposeurs", "opus", "passe-1", "traces-tour-002", "consigne.md"))
        texte = dfm.charger_dossier_ferme(dossier).page("extrait-a.md", 2)
        self.assertIn(json.dumps(texte, ensure_ascii=False), ca)
        self.assertIn(json.dumps(texte, ensure_ascii=False), co)
        m = self.fin("c6")["mesures_lecture"]["par_proposeur"]
        self.assertEqual([p["depuis_cache"] for p in m["opus"]["passe-1"]["pages_lues"]], [True])

    # --- point 7 : citations vérifiées (L7) ------------------------------------------------------------------------------

    def test_v46_7_citations_verifiees_seule_information_outillee_des_juges(self):
        """Vérification mécanique : `« passage » [extrait-a.md, p.2]` → page existante et passage retrouvé (vrai) ;
        passage absent de la page → faux ; page absente → faux ; `[p.2]` après une mention du fichier → attribuée ;
        `[p.4]` sans fichier nommé → non attribuée (manifeste seulement). Dans la course : chaque fiche servie aux juges
        (témoins compris) porte `citations_verifiees` (vrai/faux par citation) ; la consigne des juges l'explique ; le
        détail est au manifeste de fin."""
        d = dfm.charger_dossier_ferme(self.ecrire_dossier("unitaire"))
        v, na = dfm.verifier_citations_texte(["Voir " + CITATION_JUSTE, CITATION_FAUSSE, CITATION_ABSENTE,
                                              "D'après extrait-a, la conclusion [p.3] ; « le taux de rappel » [extrait-b, p.2]",
                                              "rien de nommé [p.4]", "« Le taux… 0,73 » [extrait-a.md, p.2]"], d)
        self.assertEqual([(c["fichier"], c["page"], c["verifiee"]) for c in v],
                         [("extrait-a.md", 2, True), ("extrait-a.md", 3, False), ("extrait-a.md", 9, False),
                          ("extrait-a.md", 3, True), ("sous/extrait-b.md", 2, True), ("extrait-a.md", 2, True)])
        self.assertEqual((v[1]["page_existe"], v[1]["passage_retrouve"]), (True, False))
        self.assertEqual((v[2]["page_existe"], v[2]["passage_retrouve"]), (False, None))
        self.assertEqual([x["citation"] for x in na], ["[p.4]"])
        prep, dossier = self.preparer()
        argon, _, _ = self.argon({"tours": [], "fiche": fiche_citante("Argon A")}, "argon-7")
        res = self.course(FauxProtocole({"opus": {"tours": [], "fiche": fiche_brute(nom="O1")}}, self.cours().notes_temoins_ok),
                          "c7", prep, dossier, argon=argon, outils_par_protocole=True)
        a = [f for f in res["fiches"] if f["auteur"] == "argon"][0]
        self.assertEqual(a[idn.CHAMP_CITATIONS], [{"citation": "[extrait-a.md, p.2]", "verifiee": True},
                                                  {"citation": "[extrait-a.md, p.3]", "verifiee": False},
                                                  {"citation": "[extrait-a.md, p.9]", "verifiee": False}])
        self.assertTrue(all(idn.CHAMP_CITATIONS in t for t in res["temoins"]))
        consigne = self.consignes_des_juges("c7")[0]
        self.assertIn(idn.CITATIONS_JUGE.strip(), consigne)
        bloc = json.loads(re.search(r"```json\n(\[.*\])\n```", consigne, re.S).group(1))
        self.assertTrue(all(idn.CHAMP_CITATIONS in f for f in bloc))
        servie = [f for f in bloc if f["nom"] == "Argon A"][0]
        self.assertEqual([c["verifiee"] for c in servie[idn.CHAMP_CITATIONS]], [True, False, False])
        detail = self.fin("c7")["citations"]["par_fiche"][a["identifiant_auteur"]]
        self.assertEqual(detail["verifiees"][0]["passage"], "Le taux de détection atteint 0,73")
        self.assertTrue(detail["verifiees"][0]["passage_retrouve"])

    # --- point 8 : moisson ---------------------------------------------------------------------------------------------

    def test_v46_8_moisson_reconnue_et_refusee(self):
        """`{"moissonner": "<requête>"}` est reconnue par le protocole et refusée avec le motif « moisson non disponible »
        (v47), servie comme réponse au tour suivant, comptée ; une demande inconnue ou double est refusée aussi."""
        prep, dossier = self.preparer()
        argon, _, _ = self.argon({"tours": [{"demandes": [{"moissonner": "moniteurs diffus 2026"}, {"telecharger": "x"},
                                                          {"lire": "extrait-a.md", "chercher": "taux"}]}],
                                  "fiche": fiche_brute(nom="Argon A"), "cout": 0.01}, "argon-8")
        self.course(FauxProtocole({"opus": {"tours": [], "fiche": fiche_brute(nom="O1")}}, self.cours().notes_temoins_ok),
                    "c8", prep, dossier, argon=argon, outils_par_protocole=True)
        c2 = self.lire(os.path.join(self.tmp, "c8", "proposeurs", "argon", "passe-1", "traces-tour-002", "consigne.md"))
        servi = json.loads(re.search(r"Ce que le noyau t'a servi[^\n]*\n+```json\n(.*?)\n```", c2, re.S).group(1))
        r = servi[0]["reponses"]
        self.assertEqual((r[0]["statut"], r[0]["motif"]), ("refusée", "moisson non disponible (v47)"))
        self.assertEqual([x["statut"] for x in r], ["refusée"] * 3)
        m = self.fin("c8")["mesures_lecture"]["par_proposeur"]["argon"]["passe-1"]["demandes"]
        self.assertEqual((m["moissonner"], m["refusees"], m["total"]), (1, 3, 3))
        self.assertIn("moissonner", dfm.TYPES_DEMANDE)

    # --- rétrocompatibilité -----------------------------------------------------------------------------------------------

    def test_v46_retrocompatibilite_ligne_de_commande_de_la_v45(self):
        """Sans `--dossier-ferme`, la ligne de commande et les entrées de la v45 restent valides : course simulée complète
        (Argon proposeur, seconde passe), code 0 ; consigne de passe 1 identique à celle de la v45 (même fonction, mêmes
        arguments ; aucun dossier, aucun outil) ; réglages du kit sans outil ; aucun dossier `lecture` ni `tour-…` ; ni
        mesures de lecture, ni citations au manifeste de fin ; `--outils-par-protocole` sans `--dossier-ferme` et
        `--dossier-ferme` au bras refusés par l'analyseur."""
        v41 = self.v41()
        prep, att = v41.prep_devis()
        cmd = v41.script(TestCommandeExterne.SCRIPT_OK, "argon-r.py")
        sortie = os.path.join(self.tmp, "r")
        code, out, err = v41.principal(v41.lanceur(), v41.base(sortie, prep, att, "--commande-externe", cmd))
        self.assertEqual(code, 0, err)
        depart = json.loads(self.lire(os.path.join(sortie, "manifeste-depart.json")))["reglages"]
        self.assertIsNone(depart["dossier_ferme"])
        self.assertEqual({r: v["tools"] for r, v in depart["reglages_kit"].items() if r.endswith("ideation")},
                         {"proposeur_ideation": [], "juge_ideation": []})
        fin = self.fin("r")
        self.assertNotIn("mesures_lecture", fin)
        self.assertNotIn("citations", fin)
        self.assertNotIn("incidents", fin["journal"])
        self.assertEqual(fin["mesures_convergence"]["motif_pages_lues"], idn.MOTIF_PAGES_LUES)
        for racine, dossiers, _ in os.walk(sortie):
            self.assertFalse([x for x in dossiers if x == "lecture" or x.startswith("tour-")], racine)
        consigne = self.lire(os.path.join(sortie, "proposeurs", "opus", "traces-passe-1", "consigne.md"))
        liste = idn.charger_liste_blanche(prep["liste_blanche"])
        attendue = idn.consigne_proposeur(idn.lire_pieces(prep["pieces"], liste, 750_000), 8,
                                          idn.lire_pieces([prep["question"]], liste)[0][1])
        self.assertEqual(consigne, attendue)
        self.assertTrue(consigne.startswith("# Prise « idéation » du pôle — passe de proposition\n\nTu n'as aucun outil"))
        self.assertNotIn("citations_verifiees", self.lire(os.path.join(sortie, "fiches-validees.json")))
        for argv in (v41.base(os.path.join(self.tmp, "r2"), prep, None, "--outils-par-protocole"),
                     [sortie, "--bras-rapporte-differe", "--dossier-ferme", self.tmp]):
            with self.assertRaises(SystemExit):
                v41.principal(v41.lanceur(), argv)


    # --- corrections de la contre-lecture CL12 de la v45 -----------------------------------------------------------------

    def test_v46_cl45_01_classes_avant_unittest_main(self):
        """CL45-01 : toutes les classes d'essais de ce fichier sont définies **avant** `unittest.main()` (v45 : `TestV45`
        après, sautée en lancement direct) ; le lancement direct du fichier joue `TestV45` et `TestV46`."""
        import ast
        import subprocess
        chemin = os.path.abspath(__file__)
        with open(chemin, encoding="utf-8") as f:
            arbre = ast.parse(f.read())
        rang_main = next(i for i, n in enumerate(arbre.body) if isinstance(n, ast.If) and "__main__" in ast.dump(n.test))
        classes = [n.name for n in arbre.body[rang_main:] if isinstance(n, ast.ClassDef)]
        self.assertEqual(classes, [])
        self.assertEqual(rang_main, len(arbre.body) - 1)
        racine = os.path.dirname(os.path.dirname(chemin))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q", "essais.test_v7_ideation_v2.TestV45"], cwd=racine,
                           capture_output=True, timeout=300, env={k: v for k, v in os.environ.items()
                                                                  if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")})
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        r = subprocess.run([sys.executable, "-B", "-c", "import sys, runpy; sys.argv = ['x', '-q', 'TestV45.test_v45_1_fiche_et_"
                            "temoin_a_guillemets_servis_aux_juges', 'TestV46.test_v46_cl45_01_classes_avant_unittest_main_seul']; "
                            "runpy.run_path(%r, run_name='__main__')" % chemin], cwd=racine, capture_output=True, timeout=300,
                           env={k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")})
        self.assertIn(b"Ran 2 tests", r.stderr)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])

    def test_v46_cl45_01_classes_avant_unittest_main_seul(self):
        """Témoin du lancement direct (joué par l'essai précédent par `runpy`, en `__main__`) : `TestV46` y est trouvée."""
        self.assertTrue(issubclass(TestV46, unittest.TestCase))

    def test_v46_cl45_02_caviardage_valeur_par_valeur_apres_analyse_json(self):
        """CL45-02 (R5). Cas sain : une valeur porte une clé (`sk-ant-…`) → la fiche est admise, la valeur caviardée, la
        clé n'est écrite nulle part (traces comprises). Artefacts : une valeur `token=abcdefghij"suite` (dans le JSON brut
        `token=abcdefghij\\"suite` : le caviardage du texte mangeait la barre d'échappement, d'où un guillemet nu) et une
        clé privée dont le début et la fin sont dans deux valeurs (le caviardage du texte emportait la structure entre
        elles) : v45 → « aucun bloc JSON {fiches} » (guillemet nu) ou champs perdus en silence (clé privée), course
        arrêtée ou fiche refusée sans motif juste ; v46 → analysées, puis caviardées valeur par valeur, et la fiche dont
        un secret reste à cheval sur deux champs est refusée avec ce motif ;
        même chose pour la justification d'un juge et pour la réponse d'Argon (commande externe : `texte_brut` gardé,
        `texte_final` caviardé)."""
        cle = "sk-" + "ant-" + "abcdefghijklmnopqrstu"
        debut, fin_cle = "-----BEGIN RSA PRIVATE" + " KEY-----", "-----END RSA PRIVATE" + " KEY-----"
        fiche = fiche_brute(nom="O1", enonce="Valeur avec clé " + cle + " ?", piege='token=abcdefghij"suite')
        a_cheval = fiche_brute(nom="O3", perte_traduction="avant " + debut + " milieu", cosmetique_si="fin " + fin_cle + " après")
        brut = "```json\n" + json.dumps({"fiches": [fiche]}, ensure_ascii=False) + "\n```"
        # les deux défauts de la v45 (caviardage sur le texte du bloc JSON), séparés : guillemet nu → bloc illisible ;
        # clé privée à cheval sur deux valeurs → les champs situés entre elles disparaissent en silence
        seul_token = "```json\n" + json.dumps({"fiches": [fiche_brute(piege='token=abcdefghij"suite')]}, ensure_ascii=False) + "\n```"
        self.assertIsNone(extraire_bloc_json(idn.caviarder(seul_token)[0], "fiches"))
        seule_cle = "```json\n" + json.dumps({"fiches": [fiche_brute(perte_traduction="avant " + debut,
                                                                    cosmetique_si=fin_cle + " après")]}, ensure_ascii=False) + "\n```"
        perdue = extraire_bloc_json(idn.caviarder(seule_cle)[0], "fiches")["fiches"][0]
        self.assertFalse({"questions_servies", "avantage", "piege", "cosmetique_si"} & set(perdue))
        c = self.cours()
        juge = c.notes_temoins_ok

        def juge_piege(idents, consigne):
            objet = juge(idents, consigne)
            objet["notes"][0]["justifications"] = {"avantage": 'password=abcdefghij"x ' + cle}
            return objet
        ad = FauxAdaptateur({"opus": [fiche, a_cheval], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": juge_piege, "juge-opus": juge})
        res = c.lancer(ad, "cl45-02")
        o1 = [f for f in res["fiches"] if f["nom"] == "O1"][0]
        self.assertEqual(o1["piege"], 'token=[CAVIARDÉ]"suite')
        self.assertEqual(o1["enonce"], "Valeur avec clé [CAVIARDÉ] ?")
        self.assertEqual([f["nom"] for f in res["fiches"] if f["auteur"] == "opus"], ["O1"])
        self.assertEqual([r["indice"] for r in res["refus"]], [2])  # la clé privée à cheval : refusée, motif dit
        self.assertIn("secret à cheval sur plusieurs champs", res["refus"][0]["motif"])
        self.assertTrue(res["classement"])
        sortie = os.path.join(self.tmp, "cl45-02")
        for racine, _, noms in os.walk(sortie):
            for nom in noms:
                with open(os.path.join(racine, nom), encoding="utf-8", errors="replace") as f:
                    t = f.read()
                for fuite in (cle, "abcdefghij"):
                    self.assertNotIn(fuite, t, os.path.join(racine, nom))
        notes = json.loads(self.lire(os.path.join(sortie, "notes-par-juge.json")))
        justifs = [j for n in notes["juge-fable"].values() for j in n["justifications"].values()]
        self.assertIn('password=[CAVIARDÉ]"x [CAVIARDÉ]', justifs)
        # commande externe : `texte_final` caviardé, `texte_brut` gardé pour l'analyse, la course passe
        script = ("import sys, json\nc = sys.stdin.read()\nprint(json.dumps({'texte': %r, 'cout_usd': 0.1}))\n" % brut)
        cmd = TestCommandeExterne("test_commande_factice_notes_et_controle")
        cmd.tmp = self.tmp
        ext = AdaptateurCommandeExterne(cmd.commande(script, "argon-cl45.py"), environnement={})
        r = ext.lancer("proposeur_ideation", "passe de proposition", self.tmp, 1.0, 1, modele="gemini-argon")
        self.assertNotIn(cle, r.texte_final)
        self.assertIsNone(extraire_bloc_json(r.texte_final, "fiches"))
        self.assertEqual(extraire_bloc_json(r.texte_brut, "fiches")["fiches"][0]["piege"], 'token=abcdefghij"suite')
        self.assertNotIn("texte_brut", repr(r))
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        res = c.lancer(FauxAdaptateur({"opus": [fiche_brute(nom="O2")], "fable": [fiche_brute(nom="F2")]},
                                                 notes_par_juge={"juge-fable": juge, "juge-opus": juge}), "cl45-02b",
                                  budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", ext)], budget_externe_usd=3.0)
        a = [f for f in res["fiches"] if f["auteur"] == "argon"][0]
        self.assertEqual(a["piege"], 'token=[CAVIARDÉ]"suite')
        for racine, _, noms in os.walk(os.path.join(self.tmp, "cl45-02b")):
            for nom in noms:
                with open(os.path.join(racine, nom), encoding="utf-8", errors="replace") as f:
                    self.assertNotIn(cle, f.read())


# --- v47 : moissonneur (option A, « go » de Lazar du 29 octobre 2026, 11:52 heure de Paris, sur les sept points de la note
# `note-moissonneur-integration-v1.md`) et correctif bloquant R-764 (changement de modèle par le kit). Tout hors ligne :
# relais de moisson factice en mémoire sur la boucle locale, garde-fou d'essai qui refuse toute connexion hors boucle
# locale, faux kit pour le refus de modèle ; aucune session réelle, aucun réseau, aucune clé.
import shutil  # noqa: E402
import socket  # noqa: E402

from essais.test_v47_relais_moisson import garde_fou_reseau  # noqa: E402
from pole import moisson as msn  # noqa: E402
from pole.adaptateurs import AdaptateurClaudeSDK, VARIABLES_SANS_REPLI_DE_MODELE  # noqa: E402
from pole.protocole_outils import DEBUT_DONNEES, FIN_DONNEES, Quotas  # noqa: E402
from pole.relais_reel import cout_usd  # noqa: E402

# Rétrocompatibilité v46 → v47 : empreintes SHA-256 des consignes produites par la **v46 reconstruite** (`pole/ideation.py`
# et `pole/dossier_ferme.py` de la v46 rebâtis en inversant chaque modification de la v47, puis vérifiés contre
# EMPREINTES-orchestrateur-pole-v7-v46.txt : 506896543db9…, 52c9097d58ef… ; les huit autres modules importés sont ceux
# de la v46, empreintes égales) sur les gabarits de ces essais : passe 1, passe 2 (matériau, fiche précédente), consigne de
# contrôle d'Argon (fiches maximales), juge, passe 1 et 2 à dossier fermé par protocole, juge à dossier fermé.
CONSIGNES_V46_SHA256 = {
    "passe_1": "c04dabc3fe61048a359010ae1ca2a5031d99a70a3c58864f54aa9830c4ea9afd",
    "passe_2": "e5f7330baca71f68ae8f4f414e9629c8b1f48d79c569171e3c0c79c464cfd362",
    "controle_externe": "81cae48e7b52c9b709ffbf88de32f170759564713df808ba3af569c0ae04e621",
    "juge": "2488eb32417541614ca340fa0723bf02dc4b407cead1396368b57809407f053a",
    "passe_1_dossier_protocole": "4735ceb5266713a5d3a4a5d66c5aa298f2646bb02cbf7f7315d7e0d1ec808cbb",
    "passe_2_dossier_protocole": "d0ceb74febb1ceec98240467444846c6383f5ecaffe66e5cf92857e67792a1a6",
    "juge_dossier": "d199032a7e69a88d02854003f156859700210b5a545d7be9921dd072358b7b17",
}
TITRES_CORPUS = [  # les dix extraits du corpus primaire v1 (titres déclarés)
    "Obfuscated Activations Bypass LLM Latent-Space Defenses",
    "Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols",
    "Quickest Change Detection in Discrete-Time in Presence of a Covert Adversary",
    "When Benchmarks Lie: Evaluating Malicious Prompt Classifiers Under True Distribution Shift",
    "MonitoringBench: Semi-Automated Red-Teaming for Agent Monitoring",
    "SLEIGHT-Bench: A Benchmark of Evasion Attacks Against Agent Monitors",
    "Diffuse AI Control on Fuzzy Tasks",
    "Distributed Attacks in Persistent-State AI Control",
    "Multi-Agent AI Control: Distributed Attacks Hamper Per-Instance Monitors",
    "Caught in the Act: Probes Effectively Detect Sabotage and Catch Unverbalized Deception",
]
REQUETE_SAINE = "monitor transfer diffuse sabotage probes"


def notices_servies(consigne):
    m = re.search(re.escape(DEBUT_DONNEES) + r"\s*```json\n(.*?)\n```\s*" + re.escape(FIN_DONNEES), consigne, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def section_servie(consigne):
    """Les octets de la section de moisson d'une consigne de passe 2 (délimiteurs compris) ; None sans section."""
    i, j = consigne.find(DEBUT_DONNEES), consigne.find(FIN_DONNEES)
    return consigne[i:j + len(FIN_DONNEES)] if i >= 0 and j >= 0 else None


class FauxMoisson:
    """Proposeur et juge scriptés pour la moisson : au tour de moisson, rend le bloc du scénario (une liste de demandes par
    tour, ou un texte brut) ; en passe 2, cite la première notice servie au statut MOISSONNE (`citer`), ou une citation
    fausse (`citation` : « titre_faux », « etiquette_inconnue ») ; un juge `juge_demande` rend un bloc de moisson."""
    nom = "faux-moisson"

    def __init__(self, fiches, demandes, juge, citer=True, citation=None, juge_demande=False, cout=0.05):
        self.fiches, self.demandes, self.juge = fiches, demandes, juge
        self.citer, self.citation, self.juge_demande, self.cout = citer, citation, juge_demande, cout
        self.appels = []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, **lecture):
        self.appels.append({"role": role, "consigne": consigne, "dossier": dossier, "budget": budget_usd, "max_tours": max_tours,
                            "lecture": lecture})
        if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
            return Resultat("OK", [], 0.01, "ok")
        parts = dossier.split(os.sep)
        if role == "juge_ideation":
            idents = sorted(set(re.findall(r'"identifiant": "(T\d\d)"', consigne)))
            texte = "```json\n" + json.dumps(self.juge(idents, consigne)) + "\n```"
            if self.juge_demande:
                texte += "\n```json\n" + json.dumps({"moisson": [{"source": "arxiv", "requete": REQUETE_SAINE, "resultats": 5}]}) + "\n```"
            return Resultat(texte, [], 0.1, "ok")
        if parts[-2] == "moisson":  # tour de moisson : SORTIE/proposeurs/<etiquette>/moisson/tour-00k
            etiquette, k = parts[-3], int(parts[-1][-3:])
            tours = self.demandes.get(etiquette, [])
            d = tours[k - 1] if k <= len(tours) else []
            if isinstance(d, str):
                return Resultat(d, [], self.cout, "ok")
            return Resultat("```json\n" + json.dumps({"moisson": d}, ensure_ascii=False) + "\n```", [], self.cout, "ok")
        etiquette, passe = parts[-2], parts[-1]
        fiche = dict(self.fiches[etiquette])
        if passe == "passe-2":
            fiche["nom"] = fiche["nom"] + " (revue)"
            tours = notices_servies(consigne) or []
            notices = [r for t in tours for rep in t.get("reponses", []) for r in rep.get("resultats", [])]
            if self.citer and notices:
                r = notices[0]
                if self.citation == "titre_faux":
                    ref = f"Un autre titre inventé, {r['auteurs']}, {r['date'][:4]}, {r['identifiant']} {r['etiquette']}"
                elif self.citation == "etiquette_inconnue":
                    ref = f"{r['titre']}, {r['auteurs']}, {r['date'][:4]}, 2600.00001v1 [moisson:arxiv:000000000000:2600.00001v1]"
                else:
                    ref = f"{r['titre']}, {r['auteurs']}, {r['date'][:4]}, {r['identifiant']} {r['etiquette']}"
                fiche["anteriorite"] = list(fiche["anteriorite"]) + [{"reference": ref, "statut": "MOISSONNE"}]
        return Resultat("```json\n" + json.dumps({"fiches": [fiche]}, ensure_ascii=False) + "\n```", [], 0.2, "ok")


class FauxKitRefus:
    """v47 (R-764) : un faux module de kit pour `AdaptateurClaudeSDK._executer` — rejoue un scénario de messages (modèle
    servi, `stop_reason`, usage, événements système) et note si le flux a été clos (session close)."""

    class TextBlock:
        def __init__(self, text):
            self.text = text

    class AssistantMessage:
        def __init__(self, content, model, stop_reason="end_turn", usage=None):
            self.content, self.model, self.stop_reason, self.usage = content, model, stop_reason, usage

    class SystemMessage:
        def __init__(self, subtype, data):
            self.subtype, self.data = subtype, data

    class ResultMessage:
        def __init__(self, subtype, result, total_cost_usd, is_error=False, stop_reason=None, model_usage=None):
            self.subtype, self.result, self.total_cost_usd, self.is_error = subtype, result, total_cost_usd, is_error
            self.stop_reason, self.model_usage = stop_reason, model_usage  # v49 (CL13-06) : champs du kit 0.2.172

    class ClaudeSDKError(Exception):
        pass

    def __init__(self, scenario):
        self.scenario, self.clos, self.servis = scenario, False, 0

    async def query(self, prompt, options):
        try:
            for m in self.scenario:
                self.servis += 1
                yield m
        finally:
            self.clos = True


class TestV47(CasAvecDossier):
    """v47 : moissonneur (option A) — cas sain complet (frais puis rejeu), garde de fuite (cas sain et artefacts),
    artefacts dans la course (quota, source brave, juge qui demande), relais indisponible ou altéré, résumé piégé, bloc
    illisible, rejeu discordant, absence de canal, garde-fou réseau, `--mesurer-consignes`, démonstration par le
    lanceur, rétrocompatibilité octet pour octet avec la v46 ; correctif bloquant R-764 (trois barrières)."""

    def setUp(self):
        super().setUp()
        self.garde = garde_fou_reseau()
        self.garde.__enter__()
        self.addCleanup(self.garde.__exit__, None, None, None)

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def v41(self):
        t = TestV41("test_tolerances_separees")
        t.tmp = self.tmp
        return t

    def prep(self):
        if not hasattr(self, "_prep"):
            self._prep = self.cours().preparer()
        return self._prep

    def course(self, ad, nom, **modifs):
        prep = self.prep()
        args = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"], temoins=prep["temoins"],
                    materiau=prep["materiau"], seconde_passe=True, proposeurs=[("opus", "claude-opus-5-5")],
                    juges=[("juge-opus", "claude-opus-5-5")], graine=7, budget_total_usd=20.0, budgets=self.cours().budgets())
        args.update(modifs)
        return idn.executer_ideation(ad, os.path.join(self.tmp, nom), **args)

    def relais(self, **kw):
        r = msn.RelaisMoissonFactice(**kw)
        self.addCleanup(r.arreter)
        return r

    @staticmethod
    def lire(chemin):
        with open(chemin, encoding="utf-8") as f:
            return f.read()

    def fin(self, nom):
        return json.loads(self.lire(os.path.join(self.tmp, nom, "manifeste-fin.json")))["reglages"]

    def consigne_passe_2(self, ad, etiquette="opus"):
        return [a["consigne"] for a in ad.appels if a["role"] == "proposeur_ideation" and a["dossier"].endswith(os.path.join(etiquette, "passe-2"))][0]

    # --- cas sain complet ---------------------------------------------------------------------------------------------

    def test_v47_1_cas_sain_complet_frais_puis_rejeu(self):
        """Une requête → 5 résultats servis dans la consigne de passe 2 (section entre délimiteurs, étiquettes présentes,
        empreintes recalculées égales, lien de notice jamais un PDF) ; la fiche cite MOISSONNE → `non_opposable: true`,
        L7 étendue la retrouve (étiquette servie à ce proposeur, identifiant et titre concordants) ; cache scellé, index au
        manifeste de fin ; juge : phrase MOISSONNE, jamais la vérification ; `candidats-corpus.json` ; puis la course en
        mode **rejeu** sert les mêmes octets sans appeler le relais."""
        relais = self.relais()
        juge = self.cours().notes_temoins_ok
        demandes = {"opus": [[{"source": "arxiv", "requete": REQUETE_SAINE, "resultats": 5}]]}
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        res = self.course(ad, "m1", moisson="frais", url_relais_moisson=relais.url)
        tour = [a for a in ad.appels if os.sep + "moisson" + os.sep in a["dossier"]]
        self.assertEqual(len(tour), 1)
        self.assertTrue(tour[0]["consigne"].startswith(idn.TITRE_TOUR_MOISSON))
        self.assertIn('"nom": "O1"', tour[0]["consigne"])
        self.assertEqual((tour[0]["budget"], tour[0]["lecture"]), (0.5, {}))
        c2 = self.consigne_passe_2(ad)
        self.assertIn(msn.TITRE_SECTION_MOISSON, c2)
        self.assertIn("RAPPORTE | SUPPOSE | MOISSONNE", c2)
        servis = notices_servies(c2)
        self.assertEqual([t["tour"] for t in servis], [1])
        rep = servis[0]["reponses"][0]
        self.assertEqual((rep["statut"], rep["requete"], len(rep["resultats"])), ("servie", REQUETE_SAINE, 5))
        for r in rep["resultats"]:
            self.assertEqual(r["etiquette"], f"[moisson:arxiv:{msn.empreinte_resultat(r)[:12]}:{r['identifiant']}]")
            self.assertTrue(r["lien"].startswith("https://arxiv.org/abs/"), r["lien"])  # le relais factice sert un lien PDF
            self.assertLessEqual(len(json.dumps(r, ensure_ascii=False, indent=1)), msn.TAILLE_MAX_PAR_RESULTAT)
        self.assertEqual(relais.appels[-1]["jeton"], msn.JETON_MOISSON_FACTICE)
        o1 = [f for f in res["fiches"] if f["auteur"] == "opus" and f["passe"] == 2][0]
        ant = [a for a in o1["anteriorite"] if a["statut"] == "MOISSONNE"]
        self.assertEqual(len(ant), 1)
        self.assertTrue(ant[0]["non_opposable"])
        fin = self.fin("m1")
        verif = fin["moisson"]["verification_moissonnees"][o1["identifiant_auteur"]]
        self.assertEqual((verif[0]["verifiee"], verif[0]["servie_a_ce_proposeur"], verif[0]["identifiant_concordant"],
                          verif[0]["titre_concordant"]), (True, True, True, True))
        self.assertEqual(fin["statut_course"], {"statut": "ok"})
        lignes = fin["moisson"]["resume"]["journal"]["lignes"]
        self.assertEqual([(l["statut"], l["depuis"]) for l in lignes], [("servie", "relais")])
        cache = os.path.join(self.tmp, "m1", "noyau", "moisson")
        cle = lignes[0]["cle"]
        self.assertTrue(idn.verifier_scelle(os.path.join(cache, cle + ".json")))
        self.assertTrue(idn.verifier_scelle(os.path.join(cache, "index.json")))
        self.assertEqual(fin["moisson"]["cache_index_sha256"], idn.sha256_fichier(os.path.join(cache, "index.json")))
        self.assertEqual(sorted(json.loads(self.lire(os.path.join(cache, "index.json")))["entrees"]), [cle])
        candidats = json.loads(self.lire(os.path.join(self.tmp, "m1", "candidats-corpus.json")))
        self.assertEqual(len(candidats["servis"]), 5)
        self.assertEqual([c["verifiee"] for c in candidats["cites"]], [True])
        depart = json.loads(self.lire(os.path.join(self.tmp, "m1", "manifeste-depart.json")))["reglages"]
        self.assertEqual((depart["moisson"]["mode"], depart["moisson"]["sources"], depart["moisson"]["tours"]), ("frais", ["arxiv", "openalex"], 1))
        self.assertEqual(depart["moisson"]["quotas"]["juge_ideation"]["tours"], 0)
        self.assertEqual(depart["reglages_kit"]["proposeur_ideation"]["tools"], [])
        appels_m = [a for a in fin["journal"]["appels"] if a.get("session") == "moisson"]
        self.assertEqual([(a["etiquette"], a["cout_compte_usd"]) for a in appels_m], [("opus", 0.05)])
        juge_c = [a["consigne"] for a in ad.appels if a["role"] == "juge_ideation"][0]
        self.assertIn(idn.MOISSON_JUGE.strip(), juge_c)
        self.assertIn('"MOISSONNE"', juge_c)
        for mot in ("verification_moissonnees", "motif_exact", "servie_a_ce_proposeur", "candidats"):
            self.assertNotIn(mot, juge_c)
        self.assertTrue(res["classement"])
        # rejeu : jamais le réseau, mêmes octets servis
        n_appels = len(relais.appels)
        ad2 = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        res2 = self.course(ad2, "m1r", moisson="rejeu", cache_moisson=cache)
        self.assertEqual(len(relais.appels), n_appels)
        self.assertEqual(section_servie(self.consigne_passe_2(ad2)), section_servie(c2))
        fin2 = self.fin("m1r")
        self.assertEqual((fin2["moisson"]["resume"]["mode"], fin2["moisson"]["resume"]["appels_relais"]), ("rejeu", 0))
        self.assertEqual(fin2["moisson"]["resume"]["journal"]["lignes"][0]["depuis"], "cache de la course passée (rejeu)")
        self.assertTrue(idn.verifier_scelle(os.path.join(self.tmp, "m1r", "noyau", "moisson", cle + ".json")))
        self.assertTrue(res2["classement"])
        # réglages refusés avant tout appel : moisson sans seconde passe ; rejeu avec adresse ; frais sans adresse ; mode inconnu
        for nom, modifs in (("r1", dict(moisson="frais", url_relais_moisson=relais.url, seconde_passe=False)),
                            ("r2", dict(moisson="rejeu", cache_moisson=cache, url_relais_moisson=relais.url)),
                            ("r3", dict(moisson="frais")), ("r4", dict(moisson="brave")),
                            ("r5", dict(moisson="frais", url_relais_moisson="http://exemple.org:1")),
                            ("r6", dict(moisson="frais", url_relais_moisson=relais.url, tours_moisson=3))):
            faux = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
            with self.assertRaises(idn.CourseInterrompue, msg=nom):
                self.course(faux, nom, **modifs)
            self.assertEqual(faux.appels, [], nom)
            self.assertFalse(os.path.exists(os.path.join(self.tmp, nom)), nom)

    # --- garde de fuite -------------------------------------------------------------------------------------------------

    def test_v47_2_garde_de_fuite_cas_sain_et_artefacts(self):
        """Cas sain : les titres des dix extraits du corpus (pièces à en-tête `# EXTRAIT — Titre`) et des requêtes de 3 à
        25 mots passent. Artefacts, motif exact par règle : bardeau d'un témoin (registre d'empreintes, le noyau n'a que
        les empreintes), identifiant d'épisode, étiquette anonyme, empreinte hexadécimale, GO-/R-/CL, nom de fichier,
        fragment interdit, extrait de pièce de plus de 60 caractères (hors titre), clé `sk-ant-…` construite ici, nom de
        variable de clé, jeton factice, adresse, retour à la ligne, 201 caractères, 26 mots, caractères refusés, barre
        oblique hors identifiant arXiv ancien (admis)."""
        corps = ("Texte de la pièce qui décrit longuement une méthode de mesure du rappel des moniteurs sur des épisodes "
                 "diffus et une borne tenue à dix familles de tâches, page après page.")
        pieces = [f"# EXTRAIT — {t}\n\n- Auteurs : X\n\n{corps}\n" for t in TITRES_CORPUS]
        secret = "le mode tenu à l'écart contient cette phrase de test précise que personne ne doit chercher nulle part"
        registre = os.path.join(self.tmp, "registre-bardeaux.json")
        msn.construire_registre_bardeaux([secret], registre)
        temoin = fiche_brute()
        garde = msn.GardeFuite(pieces_textes=pieces, registre_bardeaux=msn.charger_registre_bardeaux(registre),
                               temoins_textes=["\n".join(idn.feuilles_texte(temoin))])
        for t in TITRES_CORPUS:
            self.assertIsNone(garde.verifier(t), t)
        for q in ("monitor diffuse control", " ".join(["mot"] * 25), REQUETE_SAINE, "détection de rupture adversaire caché",
                  "hep-th/9901001 change detection", "Caught in the Act probes sabotage"):
            self.assertIsNone(garde.verifier(q), q)
        cle = "sk-" + "ant-" + "abcdefghijklmnopqrstu"
        artefacts = [
            ("transfert d'un moniteur vers le diffus suit-il une courbe", "règle 5"),  # bardeau du témoin
            ("cette phrase de test précise que personne ne doit chercher", "règle 5"),  # bardeau du registre (texte jamais lu)
            ("moniteur épisode 003 sabotage", "règle 4 : identifiant d'épisode"),
            ("T0.6/ep-003/p1 moniteur", "règle 2 : barre oblique"),
            ("fiche T07 contre T12", "règle 4 : étiquette anonyme"),
            ("empreinte 0123456789abcdef moniteur", "règle 4 : suite hexadécimale"),
            ("voir GO-2026-10-29-01 moniteur", "règle 4 : identifiant GO"),
            ("décision R-764 du noyau", "règle 4 : identifiant R-"),
            ("relecture CL45 moniteur", "règle 4 : identifiant CL"),
            ("lire extrait-a.md moniteur", "règle 4 : nom de fichier"),
            ("données de la banque de tâches", "règle 4 : fragment interdit"),
            (corps[:70], "règle 6"),
            ("clé " + cle + " moniteur", "règle 3 : forme de secret"),
            ("ANTHROPIC_API_KEY moniteur diffus", "règle 3 : nom de variable"),
            ("jeton " + msn.JETON_MOISSON_FACTICE, "règle 3 : jeton factice"),
            ("voir https://exemple.org/page", "règle 2 : adresse"),
            ("moniteur www.exemple.org", "règle 2 : adresse"),
            ("moniteur\ndiffus", "règle 1 : retour à la ligne"),
            ("x" * 201, "règle 1 : 201 caractères"),
            (" ".join(["mot"] * 26), "règle 1 : 26 mots"),
            ("ab", "règle 1"),
            ("moniteur a@b", "règle 2 : caractère refusé"),
            ("moniteur {diffus}", "règle 2 : caractère refusé"),
            ("moniteur a/b", "règle 2 : barre oblique"),
            (42, "règle 1 : requête non textuelle"),
        ]
        for q, motif in artefacts:
            m = garde.verifier(q)
            self.assertIsNotNone(m, q)
            self.assertIn(motif, m, q)
        self.assertNotIn(secret, json.dumps(sorted(garde.registre)))  # le noyau ne détient que des empreintes
        with open(registre, "a") as f:
            f.write(" ")
        with self.assertRaisesRegex(msn.MoissonRefusee, "sceau"):
            msn.charger_registre_bardeaux(registre)
        # le relais ne refait que les règles 1 à 3
        garde_relais = msn.GardeFuite(fragments_interdits=())
        self.assertIsNone(garde_relais.verifier("fiche T07 contre T12", regles=(1, 2, 3)))
        self.assertIn("règle 2", garde_relais.verifier("voir https://exemple.org", regles=(1, 2, 3)))

    # --- artefacts dans la course ------------------------------------------------------------------------------------------

    def test_v47_3_artefacts_dans_la_course_quota_brave_juge(self):
        """Cinq demandes dans un tour : bardeau d'un témoin (refusée, motif exact au journal, motif **générique** servi),
        adresse (idem), source `brave` (refusée au noyau, jamais envoyée), une requête saine (servie), une cinquième
        (quota : refusée, comptée) ; la course continue ; `resultats: 9` ramené à 5 ; un juge qui demande une moisson :
        refus dur consigné, rien envoyé ; une citation MOISSONNE au titre faux ou à l'étiquette non servie est rapportée
        non vérifiée (jamais aux juges) ; demande `{"moissonner"}` d'un tour de lecture : motif « au tour de moisson »."""
        relais = self.relais()
        juge = self.cours().notes_temoins_ok
        temoin_bardeau = "transfert d'un moniteur vers le diffus suit-il une courbe"
        demandes = {"opus": [[{"source": "arxiv", "requete": temoin_bardeau, "resultats": 5},
                              {"source": "openalex", "requete": "voir https://exemple.org", "resultats": 5},
                              {"source": "brave", "requete": "monitor diffus forum", "resultats": 5},
                              {"source": "arxiv", "requete": REQUETE_SAINE, "resultats": 9},
                              {"source": "openalex", "requete": "quickest change detection", "resultats": 5}]]}
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge, juge_demande=True, citation="titre_faux")
        res = self.course(ad, "m3", moisson="frais", url_relais_moisson=relais.url)
        reps = notices_servies(self.consigne_passe_2(ad))[0]["reponses"]
        self.assertEqual([r["statut"] for r in reps], ["refusée", "refusée", "refusée", "servie", "refusée"])
        self.assertEqual(reps[0]["motif"], msn.MOTIF_GENERIQUE)
        self.assertEqual(reps[1]["motif"], msn.MOTIF_GENERIQUE)
        self.assertNotIn("règle", reps[0]["motif"] + reps[1]["motif"])
        self.assertIn("arxiv ou openalex", reps[2]["motif"])
        self.assertIn("quota", reps[4]["motif"])
        self.assertEqual(len(reps[3]["resultats"]), 5)  # 9 ramené au quota
        self.assertEqual([a["params"]["q"][0] for a in relais.appels if a["chemin"] != "/moisson/etat"], [REQUETE_SAINE])
        fin = self.fin("m3")
        lignes = fin["moisson"]["resume"]["journal"]["lignes"]
        self.assertEqual([l["statut"] for l in lignes[:5]], ["refusée", "refusée", "refusée", "servie", "refusée"])
        self.assertIn("règle 5", lignes[0]["motif_exact"])
        self.assertIn("règle 2 : adresse", lignes[1]["motif_exact"])
        self.assertIn("brave", lignes[2]["motif_exact"])
        self.assertIn("quota", lignes[4]["motif_exact"])
        self.assertEqual(fin["moisson"]["resume"]["quotas"]["demandes_par_tour"]["proposeur_ideation|opus|tour-1"], 5)
        # juge qui demande : refus dur, rien envoyé
        self.assertEqual(len(fin["moisson"]["resume"]["refus_durs"]), 1)
        self.assertEqual(fin["moisson"]["resume"]["refus_durs"][0]["role"], "juge_ideation")
        self.assertEqual(len([a for a in relais.appels if a["chemin"] != "/moisson/etat"]), 1)
        from pole.protocole_outils import QuotaRefuse
        with self.assertRaisesRegex(QuotaRefuse, "refus dur"):
            Quotas().ouvrir_tour("juge_ideation", "j")
        # citation au titre faux : rapportée non vérifiée ; étiquette non servie : idem
        o1 = [f for f in res["fiches"] if f["auteur"] == "opus" and f["passe"] == 2][0]
        v = fin["moisson"]["verification_moissonnees"][o1["identifiant_auteur"]][0]
        self.assertEqual((v["verifiee"], v["titre_concordant"], v["identifiant_concordant"]), (False, False, True))
        ad2 = FauxMoisson({"opus": fiche_brute(nom="O1")}, {"opus": [[{"source": "arxiv", "requete": REQUETE_SAINE, "resultats": 2}]]},
                          juge, citation="etiquette_inconnue")
        res2 = self.course(ad2, "m3b", moisson="frais", url_relais_moisson=relais.url)
        o1b = [f for f in res2["fiches"] if f["auteur"] == "opus" and f["passe"] == 2][0]
        v = self.fin("m3b")["moisson"]["verification_moissonnees"][o1b["identifiant_auteur"]][0]
        self.assertEqual((v["verifiee"], v["servie_a_ce_proposeur"]), (False, False))
        self.assertTrue(res2["classement"])
        # MOISSONNE hors d'une course sous moisson, ou en passe 1 : refusé par le gabarit
        with self.assertRaises(idn.FicheIdeationInvalide):
            idn.valider_fiche_ideation(fiche_brute(anteriorite=[{"reference": "x", "statut": "MOISSONNE"}]), "a", 1)
        f = idn.valider_fiche_ideation(fiche_brute(anteriorite=[{"reference": "x", "statut": "MOISSONNE"}]), "a", 1, moisson=True)
        self.assertTrue(f["anteriorite"][0]["non_opposable"])
        # demande `moissonner` d'un tour de lecture du dossier fermé, sous moisson : motif « au tour de moisson »
        mes = dfm.nouvelles_mesures("protocole")
        d = self.ecrire_dossier_ferme()
        r = dfm.servir_demandes(dfm.charger_dossier_ferme(d), dfm.CachePages(dfm.charger_dossier_ferme(d)),
                                [{"moissonner": "x"}], "opus", 1, 1, mes, moisson_active=True)
        self.assertEqual(r[0]["motif"], dfm.MOTIF_MOISSON_AU_TOUR)
        r = dfm.servir_demandes(dfm.charger_dossier_ferme(d), dfm.CachePages(dfm.charger_dossier_ferme(d)),
                                [{"moissonner": "x"}], "opus", 1, 1, mes)
        self.assertEqual(r[0]["motif"], dfm.MOTIF_MOISSON)

    def ecrire_dossier_ferme(self):
        d = os.path.join(self.tmp, "dossier-ferme-47")
        os.makedirs(os.path.join(d, "sous"))
        with open(os.path.join(d, "extrait-a.md"), "w", encoding="utf-8") as f:
            f.write(TEXTE_A)
        with open(os.path.join(d, "sous", "extrait-b.md"), "w", encoding="utf-8") as f:
            f.write(TEXTE_B)
        dfm.ecrire_index(d, [{"chemin": "extrait-a.md", "titre": "Extrait A", "resume": "Résumé de l'extrait A",
                              "sections": ["Introduction", "Résultats"], "pages": 3},
                             {"chemin": "sous/extrait-b.md", "titre": "Extrait B", "resume": "Résumé B"}])
        return d

    # --- relais indisponible, réponse altérée, résumé piégé, bloc illisible, rejeu discordant ---------------------------

    def test_v47_4_indisponible_altere_piege_illisible_et_rejeu_discordant(self):
        """Relais injoignable (refus de connexion), statut 5xx : « moisson indisponible » servi et consigné, la course
        **continue** ; réponse altérée (empreinte fausse) : rejetée, ni servie ni mise en cache ; résumé piégé (garde
        lexicale) : servi réduit au titre ; bloc de demandes illisible : passe 2 sans moisson, dit au journal ; en rejeu :
        requête absente du cache → « absente du cache » ; entrée de cache qui ne concorde plus avec l'index → **arrêt du
        rejeu** (manifeste de fin en erreur)."""
        juge = self.cours().notes_temoins_ok
        demandes = {"opus": [[{"source": "arxiv", "requete": REQUETE_SAINE, "resultats": 3}]]}
        # injoignable : un relais factice arrêté (port fermé)
        mort = msn.RelaisMoissonFactice()
        url_morte = mort.url
        mort.arreter()
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        res = self.course(ad, "m4a", moisson="frais", url_relais_moisson=url_morte)
        rep = notices_servies(self.consigne_passe_2(ad))[0]["reponses"][0]
        self.assertEqual((rep["statut"], rep["motif"]), ("indisponible", "moisson indisponible"))
        self.assertIn("moisson indisponible", self.consigne_passe_2(ad))
        fin = self.fin("m4a")
        self.assertIn("injoignable", fin["moisson"]["resume"]["journal"]["lignes"][0]["motif_exact"])
        self.assertTrue(res["classement"])
        self.assertIsNone(fin["erreur"])
        # statut 500
        r500 = self.relais(panne="statut_500")
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        self.course(ad, "m4b", moisson="frais", url_relais_moisson=r500.url)
        self.assertEqual(notices_servies(self.consigne_passe_2(ad))[0]["reponses"][0]["statut"], "indisponible")
        self.assertFalse(os.path.isdir(os.path.join(self.tmp, "m4b", "noyau", "moisson")))
        # réponse altérée
        alt = self.relais(panne="alteree")
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        self.course(ad, "m4c", moisson="frais", url_relais_moisson=alt.url)
        rep = notices_servies(self.consigne_passe_2(ad))[0]["reponses"][0]
        self.assertEqual(rep["statut"], "rejetée")
        self.assertNotIn("resultats", rep)
        self.assertIn("empreinte", self.fin("m4c")["moisson"]["resume"]["journal"]["lignes"][0]["motif_exact"])
        self.assertFalse(os.path.isdir(os.path.join(self.tmp, "m4c", "noyau", "moisson")))
        with self.assertRaises(msn.ReponseAlteree):
            msn.ClientRelaisMoisson(alt.url).interroger("arxiv", REQUETE_SAINE, 3)
        # résumé piégé : réduit au titre
        piege = self.relais(panne="resume_piege")
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        self.course(ad, "m4d", moisson="frais", url_relais_moisson=piege.url)
        r = notices_servies(self.consigne_passe_2(ad))[0]["reponses"][0]["resultats"]
        self.assertEqual(r[0]["resume"], "")
        self.assertIn("garde lexicale", r[0]["resume_retire"])
        self.assertTrue(r[0]["titre"])
        self.assertTrue(r[1]["resume"])
        self.assertNotIn("exécute le script", self.consigne_passe_2(ad))
        self.assertEqual(self.fin("m4d")["moisson"]["resume"]["journal"]["lignes"][0]["resumes_retires"], 1)
        # bloc illisible : passe 2 sans moisson, dit au journal
        sain = self.relais()
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, {"opus": ["Je ne rends pas de bloc."]}, juge)
        res = self.course(ad, "m4e", moisson="frais", url_relais_moisson=sain.url)
        self.assertEqual(notices_servies(self.consigne_passe_2(ad)), [])
        self.assertIn("passe 2 sans moisson", self.fin("m4e")["journal"]["moisson"]["par_proposeur"]["opus"]["passe_2_sans_moisson"])
        self.assertEqual([a for a in sain.appels if a["chemin"] != "/moisson/etat"], [])
        self.assertTrue(res["classement"])
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, {"opus": ['```json\n{"moisson": "pas une liste"}\n```']}, juge)
        self.course(ad, "m4f", moisson="frais", url_relais_moisson=sain.url)
        self.assertIn("mal formé", self.fin("m4f")["journal"]["moisson"]["par_proposeur"]["opus"]["passe_2_sans_moisson"])
        # rejeu : absente du cache ; puis cache discordant → arrêt
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        self.course(ad, "m4g", moisson="frais", url_relais_moisson=sain.url)
        cache = os.path.join(self.tmp, "m4g", "noyau", "moisson")
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, {"opus": [[{"source": "arxiv", "requete": "autre requete jamais servie", "resultats": 3}]]}, juge)
        res = self.course(ad, "m4h", moisson="rejeu", cache_moisson=cache)
        rep = notices_servies(self.consigne_passe_2(ad))[0]["reponses"][0]
        self.assertEqual(rep["statut"], "absente du cache")
        self.assertTrue(res["classement"])
        cle = self.fin("m4g")["moisson"]["resume"]["journal"]["lignes"][0]["cle"]
        with open(os.path.join(cache, cle + ".json"), "a", encoding="utf-8") as f:
            f.write("\n")
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        with self.assertRaisesRegex(idn.CourseInterrompue, "arrêt du rejeu"):
            self.course(ad, "m4i", moisson="rejeu", cache_moisson=cache)
        self.assertIn("arrêt du rejeu", self.fin("m4i")["erreur"])
        self.assertFalse([a for a in ad.appels if a["role"] == "juge_ideation"])
        # cache absent ou index descellé : refus avant tout appel
        with open(os.path.join(cache, "index.json.sha256"), "w") as f:
            f.write("0" * 64 + "  index.json\n")
        ad = FauxMoisson({"opus": fiche_brute(nom="O1")}, demandes, juge)
        with self.assertRaisesRegex(idn.CourseInterrompue, "index"):
            self.course(ad, "m4j", moisson="rejeu", cache_moisson=cache)
        self.assertEqual(ad.appels, [])

    # --- absence de canal, garde-fou ----------------------------------------------------------------------------------------

    def test_v47_5_absence_de_canal_et_garde_fou_reseau(self):
        """Aucune variable du relais de moisson chez un agent (`variables_agent`, `construire_options`) ni dans
        `environnement_commande` d'Argon ; `tools=[]` inchangé pour les rôles d'idéation ; `garde_outils.py` ne gagne
        aucune commande ; le client du relais n'accepte qu'une adresse locale ; le garde-fou d'essai refuse toute
        connexion hors boucle locale."""
        from pole.relais import variables_agent
        env = variables_agent("http://127.0.0.1:8787")
        o = construire_options(self.tmp, 1.0, 2, url_relais="http://127.0.0.1:8787", modele="claude-opus-5-5", role="proposeur_ideation")
        for cle in list(env) + list(o["env"]):
            self.assertNotIn("MOISSON", cle.upper())
        ext = AdaptateurCommandeExterne([sys.executable, "-c", "pass"], environnement={"PATH": "/usr/bin"})
        for cle in ext.environnement_commande(1.0, "proposeur_ideation"):
            self.assertNotIn("MOISSON", cle.upper())
            self.assertNotIn("RELAIS", cle.upper())
        self.assertEqual({r: v["tools"] for r, v in reglages_kit_par_role().items() if r.endswith("ideation")},
                         {"proposeur_ideation": [], "juge_ideation": []})
        self.assertEqual(o["tools"], [])
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pole", "garde_outils.py"), encoding="utf-8") as f:
            self.assertNotIn("moisson", f.read().lower())
        for url in ("http://exemple.org:1", "https://127.0.0.1:1", "http://127.0.0.1:1/moisson"):
            with self.assertRaises(RelaisInvalide, msg=url):
                msn.ClientRelaisMoisson(url)
        s = socket.socket()
        try:
            with self.assertRaisesRegex(AssertionError, "hors boucle locale"):
                s.connect(("198.51.100.1", 80))
        finally:
            s.close()

    # --- mesures, lanceur -----------------------------------------------------------------------------------------------------

    def test_v47_6_mesurer_consignes_et_lanceur_simule(self):
        """`--mesurer-consignes --moisson frais` compte la moisson au pire cas (20 résultats, ≈ 56 000 caractères : entre
        56 000 et 60 000 ; la passe 2 maximale en grandit d'autant) ; le lanceur en moteur simulé avec `--moisson frais`
        (relais factice en mémoire, Argon simulé) rend 0, le bilan dit la moisson, puis `--moisson rejeu` sur le cache
        rend 0 sans relais ; options incohérentes refusées par l'analyseur."""
        v41 = self.v41()
        prep, att = v41.prep_devis()
        base = ["--mesurer-consignes", "--liste-blanche", prep["liste_blanche"], "--question", prep["question"], "--piece",
                prep["pieces"][0], "--temoins", prep["temoins"], "--materiau", prep["materiau"][0], "--seconde-passe",
                "--proposeur-externe", "argon=gemini-argon", "--juge-externe", "argon-j=gemini-argon"]
        code, out, err = v41.principal(v41.lanceur(), base)
        self.assertEqual(code, 0, err)
        sans = json.loads(out)
        code, out, err = v41.principal(v41.lanceur(), base + ["--moisson", "frais"])
        self.assertEqual(code, 0, err)
        avec = json.loads(out)
        self.assertIsNone(sans["moisson"])
        pire = avec["moisson"]["moisson_pire_cas_caracteres"]
        self.assertTrue(56_000 <= pire <= 60_000, pire)
        self.assertEqual(avec["moisson"]["pire_cas_par_tour_nominal"], 56_000)
        self.assertEqual(avec["moisson"]["resultats_au_pire_cas"], 20)
        self.assertEqual(avec["consignes"]["consigne_passe_2_maximale"] - sans["consignes"]["consigne_passe_2_maximale"],
                         pire + len("\n") + (len(json.dumps(idn.gabarit(True), ensure_ascii=False, indent=1))
                                             - len(json.dumps(idn.GABARIT, ensure_ascii=False, indent=1))))
        self.assertGreater(avec["consignes"]["consigne_de_controle_externe"], sans["consignes"]["consigne_de_controle_externe"])
        code, out, err = v41.principal(v41.lanceur(), base + ["--moisson", "frais", "--tours-moisson", "2"])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["moisson"]["resultats_au_pire_cas"], 40)
        # course simulée complète par le lanceur : frais (relais factice en mémoire), puis rejeu
        cmd = v41.script(TestCommandeExterne.SCRIPT_OK, "argon-m6.py")
        sortie = os.path.join(self.tmp, "l6")
        argv = v41.base(sortie, prep, att, "--commande-externe", cmd, "--moisson", "frais", "--budget-total-usd", "41",
                        "--budget-externe-usd", "12.6")
        code, out, err = v41.principal(v41.lanceur(), argv)
        self.assertEqual(code, 0, err)
        bilan = json.loads(out)
        self.assertEqual(bilan["moisson"]["mode"], "frais")
        self.assertEqual(bilan["moisson"]["proposeurs_avec_tour"], 3)
        self.assertGreaterEqual(bilan["moisson"]["demandes_par_statut"]["servie"], 1)
        self.assertEqual(bilan["moisson"]["moissonnees_verifiees"], bilan["moisson"]["moissonnees_citees"])
        self.assertGreaterEqual(bilan["moisson"]["moissonnees_citees"], 1)
        depart = json.loads(self.lire(os.path.join(sortie, "manifeste-depart.json")))["reglages"]
        self.assertIn("factice en mémoire", depart["versions"]["moisson"]["relais"])
        self.assertTrue(os.path.isfile(os.path.join(sortie, "candidats-corpus.json.sha256")))
        sortie2 = os.path.join(self.tmp, "l6r")
        argv = v41.base(sortie2, prep, att, "--commande-externe", cmd, "--moisson", "rejeu", "--cache-moisson",
                        os.path.join(sortie, "noyau", "moisson"), "--budget-total-usd", "41", "--budget-externe-usd", "12.6")
        code, out, err = v41.principal(v41.lanceur(), argv)
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["moisson"]["mode"], "rejeu")
        a = section_servie(self.lire(os.path.join(sortie, "proposeurs", "opus", "traces-passe-2", "consigne.md")))
        b = section_servie(self.lire(os.path.join(sortie2, "proposeurs", "opus", "traces-passe-2", "consigne.md")))
        self.assertTrue(a and a == b)
        for argv in (v41.base(os.path.join(self.tmp, "x1"), prep, None, "--moisson", "frais"),  # sans seconde passe
                     v41.base(os.path.join(self.tmp, "x2"), prep, att, "--moisson", "rejeu"),  # sans cache
                     v41.base(os.path.join(self.tmp, "x3"), prep, att, "--moisson", "aucune", "--url-relais-moisson", "http://127.0.0.1:1"),
                     v41.base(os.path.join(self.tmp, "x4"), prep, att, "--moisson", "frais", "--url-relais-moisson", "http://exemple.org:1"),
                     v41.base(os.path.join(self.tmp, "x5"), prep, att, "--moisson", "frais", "--tours-moisson", "3"),
                     v41.base(os.path.join(self.tmp, "x6"), prep, att, "--moisson", "frais", "--moteur", "claude-sdk",
                              "--confirmer-moteur-reel", "--url-relais", "http://127.0.0.1:1"),  # frais réel sans adresse ni confirmation
                     [sortie, "--bras-rapporte-differe", "--moisson", "frais"]):
            with self.assertRaises(SystemExit):
                v41.principal(v41.lanceur(), argv)

    # --- rétrocompatibilité --------------------------------------------------------------------------------------------------

    def test_v47_retrocompatibilite_octet_pour_octet_avec_la_v46(self):
        """Sans `moisson`, les consignes (passe 1, passe 2, contrôle d'Argon, juge, dossier fermé par protocole) ont, sur
        les gabarits de ces essais, exactement les empreintes de la v46 reconstruite (`CONSIGNES_V46_SHA256`) ; le gabarit
        servi est `GABARIT` lui-même ; aucune trace de moisson au manifeste de fin ni dans le journal d'une course sans
        moisson ; `--moisson` absent du lanceur = course de la v46."""
        import hashlib
        import tempfile
        pieces = [("piece-a.md", "# Pièce A\nTexte de contexte.", "0" * 64)]
        materiau = [("materiau.md", "# Matériau\nTour interne.", "0" * 64)]
        question = "Quelles questions ?"
        o1 = idn.valider_fiche_ideation(fiche_brute(nom="O1"), "opus", 1)
        f1 = idn.valider_fiche_ideation(fiche_brute(nom="F1"), "fable", 1)
        temoins = [idn.valider_fiche_ideation(f, idn.AUTEUR_TEMOIN, i, passe=0) for i, f in enumerate(
            [fiche_brute(nom="Sobre fort"), fiche_brute(nom="Verbeux vide", enonce="Long " * 50),
             fiche_brute(nom="Assuré occupé", originalite={"niveau": "inedite", "texte": "jamais vu"}), fiche_brute(nom="Jumeau")], 1)]
        anonymes, _ = idn.anonymiser([o1, f1] + temoins, 7, "juge-opus")
        with tempfile.TemporaryDirectory(dir=self.tmp) as tmp:
            d = os.path.join(tmp, "dossier-ferme")
            os.makedirs(os.path.join(d, "sous"))
            with open(os.path.join(d, "extrait-a.md"), "w", encoding="utf-8") as f:
                f.write(TEXTE_A)
            with open(os.path.join(d, "sous", "extrait-b.md"), "w", encoding="utf-8") as f:
                f.write(TEXTE_B)
            dfm.ecrire_index(d, [{"chemin": "extrait-a.md", "titre": "Extrait A", "resume": "Résumé de l'extrait A",
                                  "sections": ["Introduction", "Résultats"], "pages": 3},
                                 {"chemin": "sous/extrait-b.md", "titre": "Extrait B", "resume": "Résumé B"}])
            dossier = dfm.charger_dossier_ferme(d)
            textes = {
                "passe_1": idn.consigne_proposeur(pieces, 8, question),
                "passe_2": idn.consigne_proposeur(pieces, 8, question, materiau=materiau, fiches_precedentes=[idn.vue_servie(o1)]),
                "controle_externe": idn.consigne_de_controle(idn.consigne_proposeur(
                    pieces, 8, question, materiau=materiau, fiches_precedentes=[idn.fiche_maximale()] * 8)),
                "juge": idn.consigne_juge(anonymes, question, (), citations=False),
                "passe_1_dossier_protocole": idn.consigne_proposeur(pieces, 8, question, dossier=dossier, mode="protocole"),
                "passe_2_dossier_protocole": idn.consigne_proposeur(
                    pieces, 8, question, dossier=dossier, mode="protocole", materiau=materiau, fiches_precedentes=[idn.vue_servie(o1)],
                    historique=[{"tour": 1, "demandes": [{"lire": "extrait-a.md", "pages": [2, 2]}], "reponses": [{"statut": "servie"}]}]),
                "juge_dossier": idn.consigne_juge(anonymes, question, (), citations=True),
            }
        for nom, texte in textes.items():
            self.assertEqual(hashlib.sha256(texte.encode("utf-8")).hexdigest(), CONSIGNES_V46_SHA256[nom], nom)
            self.assertNotIn("MOISSONNE", texte)
        self.assertIs(idn.gabarit(False), idn.GABARIT)
        self.assertEqual(idn.STATUTS_ANTERIORITE, ("RAPPORTE", "SUPPOSE"))
        c = self.cours()
        res = c.lancer(FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                                      notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok}), "sans-moisson")
        fin = json.loads(self.lire(os.path.join(self.tmp, "sans-moisson", "manifeste-fin.json")))["reglages"]
        self.assertNotIn("moisson", fin)
        self.assertNotIn("moisson", fin["journal"])
        self.assertEqual(fin["statut_course"], {"statut": "ok"})
        self.assertEqual(fin["depense_modele_non_autorise_usd"], 0.0)
        depart = json.loads(self.lire(os.path.join(self.tmp, "sans-moisson", "manifeste-depart.json")))["reglages"]
        self.assertIsNone(depart["moisson"])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "sans-moisson", "candidats-corpus.json")))
        self.assertTrue(res["classement"])

    # --- correctif bloquant R-764 : changement de modèle par le kit ----------------------------------------------------------

    def test_v47_r764_refus_de_modele_trois_barrieres(self):
        """R-764 (incident réel du 29 octobre, 10:43 UTC). Barrière 1 (kit) : `CLAUDE_CODE_NO_MODEL_FALLBACK=true` et
        `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK=1` dans l'environnement de toute session, `fallback_model=None` explicite.
        Barrière 2 (noyau) : cas sain, un message sous le modèle demandé (suffixe de date admis) → ok ; artefacts, un faux
        kit qui rend `stop_reason: refusal` puis un message sous `claude-opus-4-8` et un résultat « budget dépassé » →
        statut « refus », jamais « budget_depasse », flux clos avant le second message ; un message sous un autre modèle →
        refus, dépense sous modèle non autorisé comptée à part ; événement `system/model_refusal_fallback` → refus ; dans
        la course : session close, sortie mise à l'écart (`A-L-ECART-modele-non-autorise/`, jamais servie aux juges),
        journal avec modèle demandé et servi, manifeste de fin `statut_course` = refus, `depense_modele_non_autorise_usd`.
        Barrière 3 (relais) : `--modeles-permis` — modèle permis relayé, `claude-opus-4-8` refusé sans appel amont (403,
        journal, état), liste vide = tout refusé (dit au démarrage), forme `role=modele` refusée ; le lanceur exige la
        liste exactement égale aux modèles de la course."""
        from essais.faux_sdk import claude_agent_sdk as faux_sdk
        o = construire_options(self.tmp, 1.0, 2, url_relais="http://127.0.0.1:8787", modele="claude-opus-5-5", role="proposeur_ideation")
        for cle, valeur in VARIABLES_SANS_REPLI_DE_MODELE.items():
            self.assertEqual(o["env"][cle], valeur)
        self.assertEqual(o["env"]["CLAUDE_CODE_NO_MODEL_FALLBACK"], "true")
        self.assertIsNone(o["fallback_model"])
        options = AdaptateurClaudeSDK.options_sdk(faux_sdk, o)
        self.assertIsNone(options.fallback_model)
        self.assertEqual(options.env["CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK"], "1")
        self.assertTrue(AdaptateurClaudeSDK.modele_conforme("claude-opus-5-5", "claude-opus-5-5-20261001"))
        for servi in ("claude-opus-4-8", "claude-opus-5", "", None):
            self.assertFalse(AdaptateurClaudeSDK.modele_conforme("claude-opus-5-5", servi), servi)
        opts = faux_sdk.ClaudeAgentOptions(model="claude-opus-5-5")
        K = FauxKitRefus
        # cas sain
        kit = K([K.AssistantMessage([K.TextBlock("réponse")], "claude-opus-5-5-20261001"), K.ResultMessage("success", "réponse", 0.3)])
        texte, cout, statut, erreur, lecture = asyncio.run(AdaptateurClaudeSDK._executer(kit, "consigne", opts, 5))
        self.assertEqual((texte, cout, statut, erreur, lecture["refus"], lecture["modele_servi"]),
                         ("réponse", 0.3, "ok", None, None, "claude-opus-5-5-20261001"))
        # artefact : l'incident rejoué
        usage = {"input_tokens": 400_000, "output_tokens": 20_000}
        kit = K([K.AssistantMessage([K.TextBlock("")], "claude-opus-5-5", stop_reason="refusal"),
                 K.SystemMessage("model_refusal_fallback", {"original_model": "claude-opus-5-5", "fallback_model": "claude-opus-4-8"}),
                 K.AssistantMessage([K.TextBlock("suite sous un autre modèle")], "claude-opus-4-8", usage=usage),
                 K.ResultMessage("error_max_budget_usd", "budget dépassé", 4.66, is_error=True)])
        texte, cout, statut, erreur, lecture = asyncio.run(AdaptateurClaudeSDK._executer(kit, "consigne", opts, 5))
        self.assertEqual(statut, "refus")
        self.assertNotEqual(statut, "budget_depasse")
        self.assertIn("refusal", erreur)
        self.assertEqual((kit.servis, kit.clos, lecture["cout_inconnu"]), (1, True, True))  # flux clos au premier message
        self.assertEqual(lecture["refus"]["evenement"], "assistant.stop_reason")
        self.assertNotIn("autre modèle", texte)
        # artefact : message sous un autre modèle (dépense comptée à part, barème du relais)
        kit = K([K.AssistantMessage([K.TextBlock("sous un autre modèle")], "claude-opus-4-8", usage=usage),
                 K.ResultMessage("error_max_budget_usd", "budget dépassé", 4.66, is_error=True)])
        texte, cout, statut, erreur, lecture = asyncio.run(AdaptateurClaudeSDK._executer(kit, "consigne", opts, 5))
        self.assertEqual((statut, lecture["refus"]["modele_servi"], lecture["refus"]["modele_demande"]), ("refus", "claude-opus-4-8", "claude-opus-5-5"))
        self.assertAlmostEqual(lecture["depense_modele_non_autorise_usd"], cout_usd("claude-opus-4-8", usage))
        self.assertGreater(lecture["depense_modele_non_autorise_usd"], 0)
        self.assertEqual(cout, lecture["depense_modele_non_autorise_usd"])
        self.assertEqual(texte, "")
        # artefact : événement système seul
        kit = K([K.SystemMessage("model_refusal_fallback", {"original_model": "claude-opus-5-5", "fallback_model": "claude-opus-4-8"}),
                 K.AssistantMessage([K.TextBlock("x")], "claude-opus-4-8")])
        _, _, statut, _, lecture = asyncio.run(AdaptateurClaudeSDK._executer(kit, "consigne", opts, 5))
        self.assertEqual((statut, lecture["refus"]["evenement"], lecture["refus"]["modele_servi"], kit.servis),
                         ("refus", "system.model_refusal_fallback", "claude-opus-4-8", 1))
        # dans la course : refus en passe 1 d'opus → arrêt propre, sortie à l'écart, manifeste de fin
        c = self.cours()

        class AdaptateurRefus(FauxAdaptateur):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)
                if role == "proposeur_ideation" and dossier.endswith(os.path.join("opus", "passe-1")):
                    return Resultat("", [], 4.66, "refus", "refus (R-764) : le modèle a rendu stop_reason = refusal",
                                    refus={"motif": "le modèle a rendu stop_reason = refusal", "modele_demande": modele,
                                           "modele_servi": "claude-opus-4-8", "evenement": "assistant.stop_reason"},
                                    modele_servi="claude-opus-4-8", depense_modele_non_autorise_usd=4.66, cout_inconnu=True)
                return r
        ad = AdaptateurRefus({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                             notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        with self.assertRaisesRegex(idn.CourseInterrompue, "refus \\(R-764\\)") as ctx:
            c.lancer(ad, "r764")
        self.assertNotIn("budget", str(ctx.exception).lower().replace("budget_moisson", ""))
        sortie = os.path.join(self.tmp, "r764")
        fin = json.loads(self.lire(os.path.join(sortie, "manifeste-fin.json")))["reglages"]
        self.assertEqual(fin["statut_course"], {"statut": "refus", "role": "proposeur_ideation", "etiquette": "opus",
                                                "modele_demande": "claude-opus-5-5", "modele_servi": "claude-opus-4-8"})
        self.assertEqual(fin["depense_modele_non_autorise_usd"], 4.66)
        self.assertIn("refus (R-764)", fin["erreur"])
        self.assertNotIn("budget dépassé", fin["erreur"])
        self.assertEqual(fin["refus_modele"][0]["modele_servi"], "claude-opus-4-8")
        appel = [a for a in fin["journal"]["appels"] if a["etiquette"] == "opus"][0]
        self.assertEqual((appel["statut"], appel["modele"], appel["modele_servi"], appel["depense_modele_non_autorise_usd"]),
                         ("refus", "claude-opus-5-5", "claude-opus-4-8", 4.66))
        ecart = os.path.join(sortie, "A-L-ECART-modele-non-autorise", "proposeurs", "opus")
        self.assertTrue(os.path.isdir(os.path.join(ecart, "passe-1")))
        self.assertTrue(os.path.isfile(os.path.join(ecart, "traces-passe-1", "reponse.md")))
        self.assertFalse(os.path.exists(os.path.join(sortie, "proposeurs", "opus", "passe-1")))
        self.assertFalse(os.path.exists(os.path.join(sortie, "proposeurs", "opus", "traces-passe-1")))
        self.assertFalse([a for a in ad.appels if a["role"] == "juge_ideation"])
        self.assertEqual(json.loads(self.lire(os.path.join(sortie, "fiches-validees.json"))), [])
        # barrière 3 : le relais de clé
        from essais.faux_sdk.amont_factice import AmontFactice
        from essais.test_v6_relais_reel import appeler, lancer_relais
        amont = AmontFactice()
        self.addCleanup(amont.arreter)
        journal = os.path.join(self.tmp, "journal-r764.jsonl")
        proc, url, ligne = lancer_relais(amont.url, 1.0, journal, modeles_permis="claude-opus-5-5,claude-fable-5-1")
        try:
            self.assertIsNotNone(url, ligne)
            self.assertIn("modèles permis : claude-opus-5-5, claude-fable-5-1", ligne)
            statut, _, _ = appeler(url, "/v1/messages", {"model": "claude-opus-5-5", "messages": []})
            self.assertEqual(statut, 200)
            n = len(amont.requetes)
            statut, _, octets = appeler(url, "/v1/messages", {"model": "claude-opus-4-8", "messages": []})
            self.assertEqual(statut, 403)
            self.assertEqual(json.loads(octets)["erreur"], "modèle non permis")
            self.assertEqual(json.loads(octets)["modele_demande"], "claude-opus-4-8")
            self.assertEqual(len(amont.requetes), n)  # aucun appel amont
            statut, _, _ = appeler(url, "/v1/messages", {"model": "claude-opus-5-5-20261001", "messages": []})
            self.assertEqual(statut, 403)  # noms exacts
            statut, _, octets = appeler(url, "/relais/etat", None, methode="GET")
            etat = json.loads(octets)
            self.assertEqual((etat["refus_modele"], etat["modeles_permis"]), (2, ["claude-opus-5-5", "claude-fable-5-1"]))
            self.assertEqual(etat["depense_usd"], round(cout_usd("claude-opus-5-5", {"input_tokens": 1000, "output_tokens": 200}), 6))
            limite = time.time() + 3
            while time.time() < limite:
                with open(journal, encoding="utf-8") as f:
                    lignes = [json.loads(l) for l in f if l.strip()]
                if any(l.get("statut") == 403 for l in lignes):
                    break
                time.sleep(0.05)
            refus = [l for l in lignes if l.get("statut") == 403]
            self.assertEqual(refus[0]["modele"], "claude-opus-4-8")
            self.assertIn("modèle non permis", refus[0]["motif"])
        finally:
            proc.kill()
            proc.communicate(timeout=10)
        proc, url, ligne = lancer_relais(amont.url, 1.0, journal + ".2", modeles_permis="")
        try:
            self.assertIsNotNone(url, ligne)
            self.assertIn("AUCUN modèle permis", ligne)
            statut, _, octets = appeler(url, "/v1/messages", {"model": "claude-opus-5-5", "messages": []})
            self.assertEqual(statut, 403)
            self.assertEqual((json.loads(octets)["erreur"], json.loads(octets)["modeles_permis"]), ("modèle non permis", []))
        finally:
            proc.kill()
            proc.communicate(timeout=10)
        proc, url, ligne = lancer_relais(amont.url, 1.0, journal + ".3", modeles_permis="proposeur_ideation=claude-opus-5-5")
        self.assertIsNone(url)
        self.assertIn("role=modele", ligne)
        # le lanceur exige la liste exactement égale aux modèles de la course
        lanceur = self.v41().lanceur()
        budgets = {("juge_ideation", "claude-opus-5-5"): 4.0, ("juge_ideation", "claude-fable-5-1"): 7.0}
        juges = [("a", "claude-opus-5-5"), ("b", "claude-fable-5-1")]
        etat = {"plafond_usd": 40, "reserve_par_appel_usd": 4, "depense_usd": 0.0, "modeles_permis": ["claude-opus-5-5", "claude-fable-5-1"]}
        lu = lanceur.verifier_relais(etat, 40.0, budgets, juges, modeles_attendus=["claude-opus-5-5", "claude-fable-5-1", "claude-opus-5-5"])
        self.assertEqual(lu["modeles_permis"], ["claude-opus-5-5", "claude-fable-5-1"])
        for permis in (["claude-opus-5-5"], ["claude-opus-5-5", "claude-fable-5-1", "claude-opus-4-8"], []):
            with self.assertRaisesRegex(idn.CourseInterrompue, "R-764"):
                lanceur.verifier_relais(dict(etat, modeles_permis=permis), 40.0, budgets, juges,
                                        modeles_attendus=["claude-opus-5-5", "claude-fable-5-1"])
        lu = lanceur.verifier_relais({"plafond_usd": 40, "reserve_par_appel_usd": 4}, 40.0, budgets, juges, modeles_attendus=["claude-opus-5-5"])
        self.assertIn("muet", lu["modeles_permis"])  # relais antérieur à la v47 : dit, pas refusé

# ======================================================================================================================
# v48 : étage de tests de mort (décision de Lazar R-776 (a)) — faux kit, faux exécuteurs, arbre de tranche de test
# ======================================================================================================================

import hashlib  # noqa: E402
import io as _io  # noqa: E402
import contextlib as _contextlib  # noqa: E402
import signal as _signal  # noqa: E402

from pole import protocole_outils as pto  # noqa: E402
from pole import tests_de_mort_v2 as tdm  # noqa: E402  (v51 : version 2 de l'étage)

import functools as _functools  # noqa: E402

VARIABLE_ESSAIS_REELS_NON_JOUES = "POLE_ESSAI_BAC_REEL_NON_JOUE"


def exiger_essai_reel(test, motif):
    """v51 (CL15-04) : un essai réel (vrai `bwrap`, noyau superutilisateur et `setpriv`) ne s'ignore **jamais en silence** : sans
    ce qu'il exige, il **échoue**. Seule la variable explicite `POLE_ESSAI_BAC_REEL_NON_JOUE=1` le fait ignorer, avec un motif
    qui le dit (« ESSAI RÉEL NON JOUÉ », compté parmi les ignorés au résultat de la suite)."""
    if os.environ.get(VARIABLE_ESSAIS_REELS_NON_JOUES) == "1":
        test.skipTest(f"ESSAI RÉEL NON JOUÉ ({VARIABLE_ESSAIS_REELS_NON_JOUES}=1, demande explicite) : {motif}")
    test.fail(f"essai réel impossible ici : {motif} (CL15-04 : jamais ignoré en silence ; {VARIABLE_ESSAIS_REELS_NON_JOUES}=1 "
              "pour le déclarer non joué)")


def essai_reel_bwrap(fonction):
    """v51 (CL15-04) : remplace `skipUnless(which("bwrap"))` — sans `bwrap`, l'essai échoue (sauf la variable explicite)."""
    @_functools.wraps(fonction)
    def enveloppe(self, *a, **k):
        if not shutil.which("bwrap"):
            exiger_essai_reel(self, "bwrap absent de cette machine : essai réel à rejouer dans le conteneur de session-depot")
        return fonction(self, *a, **k)
    return enveloppe

# Rétrocompatibilité v47 → v48 : empreintes SHA-256 des sorties d'une course de ces essais (faux adaptateur, deux proposeurs,
# deux juges, seconde passe, matériau) produite par la **v47** (`orchestrateur-pole-v7/pole/` de la v47, empreintes de
# EMPREINTES-orchestrateur-pole-v7-v47.txt vérifiées avant) et par la v48 sans `etage_tests` : identiques octet pour octet.
SORTIES_V47_SHA256 = {
    "classement.json": "67fbfa7cac0607f56451ced58586733b2740edd838a2ec71745118bcb691278d",
    "fiches-validees.json": "b569c13588b16ea151f002b093e5649be7368a2ee08be5aaac42796a7ebd0b7d",
    "notes-par-juge.json": "0d6c64455f30f5f42c4e2ccd292ca64c2711e53f95613c0df196ab9d56aa7d42",
    "lecture.json": "e6f7f70e20592ac25f18a57af70c5c912126ab7424a1d82a2cd338e14d0d2980",
    "classements-par-juge.json": "bdae24eca89ca51ef2847d90e50b7a15658f083fcebcd1b2d374e88b523ce08a",
    "noyau/modeles.json": "dab3b47432cffc61706a6948ba228887994626ea2b283fcfad743c4d9a98dae7",
}
REGLAGES_KIT_V47_SHA256 = "9d3dbb0baed1befed72e41091a0e9e9c928ce0ac8d57f0f688e1e5c49d063f92"
CONSIGNES_V47_SHA256 = {
    "juges/traces-juge-fable/consigne.md": "9b6f9e95a79bab4a0c8d7ecd43c1acef997a70c6bacb1d599f759b431c906637",
    "juges/traces-juge-opus/consigne.md": "d7d7e9c54ec71296fe16d2f9793357a7c5e4867853a0b470bca250671b5e2c43",
    "proposeurs/fable/traces-passe-1/consigne.md": "c04dabc3fe61048a359010ae1ca2a5031d99a70a3c58864f54aa9830c4ea9afd",
    "proposeurs/fable/traces-passe-2/consigne.md": "6057e1eab3ba70b6bba84bc8b52fd19577df1da83086a528f9698df535805b37",
    "proposeurs/opus/traces-passe-1/consigne.md": "c04dabc3fe61048a359010ae1ca2a5031d99a70a3c58864f54aa9830c4ea9afd",
    "proposeurs/opus/traces-passe-2/consigne.md": "0fff5ad5f8aef1a98e15d97290ddc6979006d4065b245fcdd8ac90421efadad5",
}


def section_de(consigne, debut_titre):
    """L'objet JSON de la section de données (`section_servie`) dont le titre commence par `debut_titre`, ou None."""
    m = re.search(r"## " + re.escape(debut_titre) + r"[^\n]*\n.*?" + re.escape(DEBUT_DONNEES) + r"\s*```json\n(.*?)\n```\s*"
                  + re.escape(FIN_DONNEES), consigne, re.S)
    return json.loads(m.group(1)) if m else None


def script_resultat(valeur, donnee="serie-a.csv"):
    """Un script sain : lit la donnée de la tranche (preuve de lecture) et imprime la ligne de résultat gelée."""
    return (f"lignes = open('tranche/{donnee}', encoding='utf-8').read().splitlines()\n"
            f"print('lignes lues :', len(lignes))\nprint('RESULTAT: {valeur}')\n")


def bloc_exp(*demandes):
    return "```json\n" + json.dumps({"experience": list(demandes)}, ensure_ascii=False) + "\n```"


def bloc_fin(motif="fini"):
    return "```json\n" + json.dumps({"fin": motif}, ensure_ascii=False) + "\n```"


def executer(script):
    return {"executer": {"script": script}}


class FauxKitEtage(FauxAdaptateur):
    """Faux kit de la course et de l'étage de tests de mort. Proposeurs et juges : comme `FauxAdaptateur`. Expérimentateur :
    `exp(fiche, tour, consigne)` rend le texte du tour (défaut : un script qui imprime `RESULTAT: 0.4`, puis `fin`). Lecteur :
    `lec(fiche, consigne)` rend le texte (défaut : lecteur honnête, applique le seuil gelé à la dernière ligne de
    résultat). `effets` : fonction appelée à chaque session de l'étage (fiche, role, tour) pour les artefacts."""

    def __init__(self, *args, exp=None, lec=None, cout_exp=0.05, cout_lec=0.02, effets=None, statut_exp="ok", statut_lec="ok", **kw):
        super().__init__(*args, **kw)
        self.exp, self.lec, self.cout_exp, self.cout_lec, self.effets = exp, lec, cout_exp, cout_lec, effets
        self.statut_exp, self.statut_lec = statut_exp, statut_lec

    @staticmethod
    def exp_defaut(fiche, tour, consigne):
        return bloc_exp(executer(script_resultat(0.4))) if tour == 1 else bloc_fin()

    @staticmethod
    def lec_defaut(fiche, consigne):
        prereg = section_de(consigne, tdm.TITRE_SECTION_PREREG)
        vue = section_de(consigne, "Sortie scellée des exécutions")
        reussies = [e for e in vue if e["statut"] == "réussie" and e["lignes_resultat"]]
        if not reussies:
            return "VERDICT: non concluant ; chiffre: aucun ; ligne: aucune"
        ligne = reussies[-1]["lignes_resultat"][-1]
        valeur = float(ligne.split(":", 1)[1])
        survit = tdm.comparer(valeur, prereg["seuil"]["comparateur"], prereg["seuil"]["valeur"])
        return f"VERDICT: {'survit' if survit else 'éliminée'} ; chiffre: {valeur} ; ligne: {ligne}"

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, **lecture):
        if role == "experimentateur_test":
            self.appels.append({"role": role, "consigne": consigne, "dossier": dossier, "modele": modele, "budget": budget_usd,
                                "max_tours": max_tours})
            fiche, tour = os.path.basename(os.path.dirname(os.path.dirname(dossier))), int(os.path.basename(dossier).split("-")[1])
            if self.effets:
                self.effets(fiche, role, tour)
            texte = (self.exp or self.exp_defaut)(fiche, tour, consigne)
            if self.statut_exp != "ok":
                return Resultat("", [], 0.0, self.statut_exp, "APIError")
            return Resultat(texte, [], self.cout_exp, "ok")
        if role == "lecteur_test":
            self.appels.append({"role": role, "consigne": consigne, "dossier": dossier, "modele": modele, "budget": budget_usd,
                                "max_tours": max_tours})
            fiche = os.path.basename(os.path.dirname(dossier))
            if self.effets:
                self.effets(fiche, role, 0)
            if self.statut_lec != "ok":
                return Resultat("", [], 0.0, self.statut_lec, "APIError")
            return Resultat((self.lec or self.lec_defaut)(fiche, consigne), [], self.cout_lec, "ok")
        return super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)


class ExecuteurNonIsole(tdm.ExecuteurBacASable):
    """Faux exécuteur **sans aucune isolation** (le script s'exécute tel quel) : la sonde du noyau doit le refuser."""
    nom = "non-isole"

    def __init__(self, **kw):
        super().__init__(bwrap="(aucun)", python=sys.executable, **kw)

    def verifier_outils(self):
        return None

    def verifier_identite(self):
        return None  # v50 : l'identité n'est pas le sujet de ce faux (c'est l'absence d'isolation du réseau que la sonde doit voir)

    BORNE_MEMOIRE_BAC = False  # v51 : ni la mémoire du bac ni le filtre ne sont le sujet de ce faux (aucun groupe de contrôle créé)
    FILTRE_APPELS = False

    def commande(self, script, travail, fd_seccomp=None):  # v51 : signature de la version 2
        return [self.python, "-I", "-B", script]


class ExecuteurReseauSeul(tdm.ExecuteurFactice):
    """Faux exécuteur qui isole le réseau mais pas le système de fichiers : la sonde doit le refuser pour l'écriture."""
    nom = "reseau-seul"
    factice = False

    def commande(self, script, travail, fd_seccomp=None):  # v51 : signature de la version 2
        prelude = tdm.PRELUDE_FACTICE.replace("builtins.open = _ouvrir\nio.open = _ouvrir\n", "")
        return [self.python, "-I", "-B", "-c", prelude, script]


class TestV48(CasAvecDossier):
    """v48 : étage de tests de mort (R-776 a) — cas sain complet ; fiche sans seuil, sans champ, à données hors tranche ;
    script réseau et écriture hors du dossier (échecs visibles, sonde du bac à sable qui refuse un exécuteur non isolé) ;
    quotas ; délai ; lecteur hors format ; classement modifié ; changement de modèle ; bac à sable absent ; réglages ;
    rétrocompatibilité sans l'option ; lanceur."""

    def setUp(self):
        super().setUp()
        self.garde = garde_fou_reseau()
        self.garde.__enter__()
        self.addCleanup(self.garde.__exit__, None, None, None)

    # --- aides -----------------------------------------------------------------------------------------------------------

    def cours(self):
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        return c

    def prep(self):
        """Les pièces des essais et une tranche exploratoire (index scellé, deux fichiers) dans la même liste blanche."""
        if hasattr(self, "_prep48"):
            return self._prep48
        base = self.cours().preparer()
        tr = os.path.join(self.tmp, "tranche")
        os.makedirs(tr)
        for nom, texte in (("serie-a.csv", "a,b\n1,2\n3,4\n5,6\n"), ("serie-b.csv", "c\n7\n8\n")):
            with open(os.path.join(tr, nom), "w", encoding="utf-8") as f:
                f.write(texte)
        dfm.ecrire_index(tr, [{"chemin": "serie-a.csv", "titre": "Série A", "resume": "Trois lignes de démonstration"},
                              {"chemin": "serie-b.csv", "titre": "Série B", "resume": "Deux lignes de démonstration"}])
        lb = os.path.join(self.tmp, "liste-blanche-v48.json")
        idn.construire_liste_blanche([base["question"], base["pieces"][0], base["materiau"][0], base["temoins"],
                                      os.path.join(tr, "index.json")], lb)
        self._prep48 = dict(base, liste_blanche=lb, tranche=tr)
        return self._prep48

    def etage(self, **modifs):
        e = {"nombre": 2, "tranche": self.prep()["tranche"], "experimentateur": ("exp", "claude-opus-5-5"),
             "lecteur": ("lec", "claude-fable-5-1"), "executeur": tdm.ExecuteurFactice(delai_s=30.0)}
        e.update(modifs)
        return e

    @staticmethod
    def champ_test(donnees=("serie-a.csv",), seuil="au moins 0,3", test="part des lignes positives de la série"):
        return {"seuil": seuil, "test": test, "donnees": list(donnees)}

    def fiche(self, nom, test=True, prediction="effet d'au moins 0,3", **modifs):
        f = fiche_brute(nom=nom, loi_predictive={"prediction": prediction, "signe": "+"})
        if test is True:
            f["test_de_mort"] = self.champ_test()
        elif test:
            f["test_de_mort"] = test
        f.update(modifs)
        return f

    def kit(self, fiches=None, **kw):
        c = self.cours()
        fiches = fiches or {"opus": [self.fiche("O1"), self.fiche("O2")], "fable": [self.fiche("F1"), self.fiche("F2")]}
        return FauxKitEtage(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok}, **kw)

    def course(self, ad, nom, etage=True, **modifs):
        c = self.cours()
        c._prep = {k: v for k, v in self.prep().items() if k != "tranche"}
        args = {}
        if etage:
            args["etage_tests"] = etage if isinstance(etage, dict) else self.etage()
        args.update(modifs)
        return c.lancer(ad, nom, **args)

    @staticmethod
    def lire(chemin):
        with open(chemin, encoding="utf-8") as f:
            return f.read()

    def json(self, nom, *chemin):
        return json.loads(self.lire(os.path.join(self.tmp, nom, *chemin)))

    def fin(self, nom):
        return self.json(nom, "manifeste-fin.json")["reglages"]

    def etage_de(self, nom):
        return self.json(nom, "manifeste-tests-de-mort.json")["reglages"]["resume"]

    def retenues(self, nom, n):
        return [l["identifiant_auteur"] for l in self.json(nom, "classement.json")["lignes"] if l["eligible"]][:n]

    def par_fiche(self, nom):
        return {r["identifiant_auteur"]: r for r in self.etage_de(nom)["par_fiche"]}

    def appels_fiche(self, ad, fiche, role=None):
        return [a for a in ad.appels if os.sep + fiche + os.sep in a["dossier"] + os.sep and a["role"] in
                (("experimentateur_test", "lecteur_test") if role is None else (role,))]

    # --- 1. cas sain complet -------------------------------------------------------------------------------------------------

    def test_v48_01_cas_sain_complet(self):
        """Course à quatre fiches, étage sur les deux premières éligibles du classement figé : préenregistrement court scellé
        **avant** la première session (journal numéroté, dates des fichiers, empreinte dans la consigne), script exécuté par
        le noyau (factice), sortie scellée, lecteur neuf, verdicts selon le seuil gelé (survit ≥ 0,3, éliminée en dessous),
        section « tests de mort (exploratoires) » du manifeste de fin, matériau, classement intact, jamais servi aux juges."""
        def exp(fiche, tour, consigne):
            return bloc_exp(executer(script_resultat(0.4 if fiche.startswith("opus") else 0.1))) if tour == 1 else bloc_fin()
        ad = self.kit(exp=exp)
        res = self.course(ad, "e1")
        sortie = os.path.join(self.tmp, "e1")
        retenues = self.retenues("e1", 2)
        self.assertEqual(len(retenues), 2)
        etage = self.etage_de("e1")
        self.assertEqual(etage["candidates"], retenues)
        self.assertEqual([r["identifiant_auteur"] for r in etage["par_fiche"]], retenues)
        self.assertTrue(etage["termine"])
        self.assertEqual(etage["statut_epistemique"], "exploratoire")
        # classement figé : empreinte avant, sceau intact après
        cl = os.path.join(sortie, "classement.json")
        fige = self.json("e1", "noyau", "tests-de-mort", "classement-fige.json")
        self.assertEqual(fige["classement_sha256"], idn.sha256_fichier(cl))
        self.assertEqual(fige["retenues_dans_l_ordre"], retenues)
        self.assertTrue(etage["classement_intact"] and idn.verifier_scelle(cl))
        journal = self.json("e1", "manifeste-tests-de-mort.json")["reglages"]["journal"]["evenements"]
        self.assertEqual([e["n"] for e in journal], list(range(1, len(journal) + 1)))
        self.assertEqual(journal[0]["evenement"], "classement-fige")
        verdicts = {}
        for ident in retenues:
            d = os.path.join(sortie, "noyau", "tests-de-mort", ident)
            prereg = os.path.join(d, "prereg-court.json")
            self.assertTrue(idn.verifier_scelle(prereg), ident)
            p = json.loads(self.lire(prereg))
            self.assertEqual((p["seuil"]["comparateur"], p["seuil"]["valeur"]), ("≥", 0.3))
            self.assertEqual((p["prediction"]["valeur"], p["prediction"]["signe"]), (0.3, "+"))
            self.assertEqual(p["donnees"][0]["chemin"], "serie-a.csv")
            self.assertEqual(p["donnees"][0]["sha256"], idn.sha256_fichier(os.path.join(self.prep()["tranche"], "serie-a.csv")))
            self.assertTrue(p["hypothese"] and p["metrique"] and p["test_de_mort"] and p["plan_d_analyse"] and p["liste_d_arret"])
            self.assertEqual(p["fiche"]["extraits"]["nom"], p["fiche"]["nom"])
            # ordre prouvé : journal numéroté, dates des fichiers, empreinte dans la consigne
            n_prereg = next(e["n"] for e in journal if e["evenement"] == "prereg-court-scelle" and e["fiche"] == ident)
            n_session = next(e["n"] for e in journal if e["evenement"] == "session" and e["fiche"] == ident)
            self.assertLess(n_prereg, n_session)
            consigne = os.path.join(d, "experimentateur", "traces-tour-001", "consigne.md")
            self.assertLessEqual(os.stat(prereg).st_mtime_ns, os.stat(consigne).st_mtime_ns)
            self.assertIn(idn.sha256_fichier(prereg), self.lire(consigne))
            # la consigne : prereg, index de la tranche, aucun outil du kit, protocole
            c1 = self.lire(consigne)
            self.assertIn("Tu n'as aucun outil", c1)
            self.assertEqual(section_de(c1, tdm.TITRE_SECTION_PREREG)["seuil"]["valeur"], 0.3)
            self.assertEqual([e["chemin"] for e in section_de(c1, "Index de la tranche exploratoire")], ["serie-a.csv", "serie-b.csv"])
            # exécution par le noyau : script scellé, sortie scellée, dossier de travail
            e1 = os.path.join(d, "execution-01")
            for nom in ("script.py", "stdout.txt", "stderr.txt", "resultat.json"):
                self.assertTrue(idn.verifier_scelle(os.path.join(e1, nom)), nom)
            self.assertIn("RESULTAT:", self.lire(os.path.join(e1, "stdout.txt")))
            self.assertIn("lignes lues : 4", self.lire(os.path.join(e1, "stdout.txt")))
            self.assertTrue(idn.verifier_scelle(os.path.join(d, "sortie-scellee.json")))
            r = self.par_fiche("e1")[ident]
            verdicts[ident] = r["verdict"]
            self.assertEqual((r["statut"], r["desaccord"]), ("testée", None))
            self.assertEqual(r["lecteur"]["verdict"], r["lecture_mecanique"]["verdict"])
            self.assertEqual(r["tours"], 2)
        attendu = {i: ("survit" if i.startswith("opus") else "éliminée") for i in retenues}
        self.assertEqual(verdicts, attendu)
        self.assertEqual(sum(etage["comptes"].values()), 2)
        # section du manifeste de fin, matériau, manifeste scellé
        fin = self.fin("e1")
        self.assertEqual(fin["tests_de_mort_exploratoires"]["statut"], "joué")
        self.assertEqual(fin["tests_de_mort_exploratoires"]["comptes"], etage["comptes"])
        self.assertEqual(res["tests_de_mort"]["comptes"], etage["comptes"])
        self.assertTrue(idn.verifier_scelle(os.path.join(sortie, "manifeste-tests-de-mort.json")))
        mat = os.path.join(sortie, "noyau", "tests-de-mort", "materiau-tests-de-mort.md")
        self.assertTrue(idn.verifier_scelle(mat))
        self.assertIn("exploratoires", self.lire(mat))
        self.assertNotIn("RESULTAT", self.lire(mat))  # comptes et étiquettes, jamais le détail des sorties
        # jamais servi aux juges de la même course : les juges ont déjà rendu avant la première session de l'étage
        rangs = [i for i, a in enumerate(ad.appels) if a["role"] in ("experimentateur_test", "lecteur_test")]
        juges = [i for i, a in enumerate(ad.appels) if a["role"] == "juge_ideation"]
        self.assertTrue(rangs and juges and max(juges) < min(rangs))
        for a in ad.appels:
            if a["role"] == "juge_ideation":
                self.assertNotIn("VERDICT", a["consigne"])
                self.assertNotIn("RESULTAT:", a["consigne"])
                self.assertNotIn("tests_de_mort_exploratoires", a["consigne"])
        # les proposeurs ont reçu l'index de la tranche et le champ au gabarit
        c_prop = [a["consigne"] for a in ad.appels if a["role"] == "proposeur_ideation"][0]
        self.assertIn("## Tranche exploratoire", c_prop)
        self.assertIn('"test_de_mort"', c_prop)
        self.assertIn("serie-a.csv", c_prop)
        # coûts : l'étage entre dans le total (jamais gratuit), fictif avec le faux kit
        self.assertEqual(etage["couts"], {"claude_usd": round(2 * (0.05 * 2 + 0.02), 6), "externe_usd": 0.0})
        self.assertTrue(fin["journal"]["cout_fictif"])
        self.assertEqual(fin["journal"]["cout_etage_tests_usd"], etage["couts"])
        depart = self.json("e1", "manifeste-depart.json")["reglages"]["tests_de_mort"]
        self.assertEqual(depart["nombre"], 2)
        self.assertEqual(depart["tranche_index_sha256"], etage["tranche"]["index_sha256"])
        self.assertEqual(depart["plafond_etage_claude_usd"], 1.2)

    # --- 2. fiche sans seuil, sans champ, prédiction non chiffrée ---------------------------------------------------------------

    def test_v48_02_fiche_sans_champ_ni_seuil_ni_prediction_chiffree_refusee_a_l_etage(self):
        """Une fiche sans `test_de_mort`, une au seuil non chiffré, une à la prédiction non chiffrée sont **refusées à
        l'étage** (motif consigné, aucun préenregistrement, aucune session) ; la quatrième, saine, est testée ; les quatre
        restent jugées et classées (l'étage ne change pas le classement)."""
        fiches = {"opus": [self.fiche("Sans champ", test=False), self.fiche("Seuil flou", test=self.champ_test(seuil="à voir")),
                           self.fiche("Prédiction floue", prediction="rappel décroît"), self.fiche("Saine")]}
        ad = self.kit(fiches)
        self.course(ad, "e2", etage=self.etage(nombre=4), proposeurs=[("opus", "claude-opus-5-5")],
                    juges=[("juge-opus", "claude-opus-5-5")])
        etage = self.etage_de("e2")
        self.assertEqual((etage["refusees_a_l_etage"], sum(etage["comptes"].values())), (3, 1))
        motifs = {r["nom"]: r["motif"] for r in etage["par_fiche"] if r["statut"] != "testée"}
        self.assertEqual(set(motifs), {"Sans champ", "Seuil flou", "Prédiction floue"})
        self.assertIn("test_de_mort", motifs["Sans champ"])
        self.assertIn("seuil non chiffré", motifs["Seuil flou"])
        self.assertIn("prédiction non chiffrée", motifs["Prédiction floue"])
        for r in etage["par_fiche"]:
            d = os.path.join(self.tmp, "e2", "noyau", "tests-de-mort", r["identifiant_auteur"])
            if r["statut"] == "testée":
                self.assertTrue(os.path.exists(os.path.join(d, "prereg-court.json")))
                continue
            self.assertFalse(os.path.exists(os.path.join(d, "prereg-court.json")))
            self.assertTrue(idn.verifier_scelle(os.path.join(d, "refus.json")))
            self.assertEqual(self.appels_fiche(ad, r["identifiant_auteur"]), [])
        classement = self.json("e2", "classement.json")["lignes"]
        self.assertEqual(len([l for l in classement]), 4)
        self.assertTrue(etage["classement_intact"])
        self.assertEqual(self.fin("e2")["tests_de_mort_exploratoires"]["refusees_a_l_etage"], 3)

    # --- 3. données hors tranche ------------------------------------------------------------------------------------------------

    def test_v48_03_donnees_hors_tranche_refusees(self):
        """Données demandées hors de l'index de la tranche (fichier absent, remontée de dossier, chemin `donnees/…`, une bonne
        et une mauvaise) → fiche refusée à l'étage, aucune session ; aucune lecture hors de la tranche n'est possible."""
        hors = [["autre.csv"], ["../index.json"], ["donnees/x.csv"], ["serie-a.csv", "hors.csv"], ["/etc/passwd"]]
        fiches = {"opus": [self.fiche(f"Hors {k}", test=self.champ_test(donnees=d)) for k, d in enumerate(hors)]}
        ad = self.kit(fiches)
        self.course(ad, "e3", etage=self.etage(nombre=5), proposeurs=[("opus", "claude-opus-5-5")],
                    juges=[("juge-opus", "claude-opus-5-5")])
        etage = self.etage_de("e3")
        self.assertEqual((etage["refusees_a_l_etage"], sum(etage["comptes"].values())), (5, 0))
        for r in etage["par_fiche"]:
            self.assertIn("hors de la tranche exploratoire", r["motif"])
            self.assertEqual(self.appels_fiche(ad, r["identifiant_auteur"]), [])
        self.assertEqual([a for a in ad.appels if a["role"] in ("experimentateur_test", "lecteur_test")], [])

    # --- 4. réseau ------------------------------------------------------------------------------------------------------------

    def test_v48_04_script_reseau_echec_visible_et_sonde_refuse_un_executeur_non_isole(self):
        """Un script qui tente une connexion vers un port ouvert par le noyau sur la boucle locale échoue **visiblement**
        (code ≠ 0, erreur dans la sortie d'erreur scellée, verdict non concluant) sous l'exécuteur factice ; la sonde du
        bac à sable (R5) refuse un exécuteur qui n'isole pas le réseau, ou pas le système de fichiers : étage refusé avant
        tout appel, aucun repli."""
        import socket as sk
        ecoute = sk.socket()
        ecoute.bind(("127.0.0.1", 0))
        ecoute.listen(1)
        ecoute.settimeout(0.3)
        self.addCleanup(ecoute.close)
        port = ecoute.getsockname()[1]
        script = ("import socket\ns = socket.socket()\ns.settimeout(3)\ns.connect(('127.0.0.1', %d))\nprint('RESEAU')\n"
                  "print('RESULTAT: 0.9')\n" % port)
        ad = self.kit({"opus": [self.fiche("Réseau")]}, exp=lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin())
        self.course(ad, "e4", etage=self.etage(nombre=1), proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")])
        r = list(self.par_fiche("e4").values())[0]
        e = r["executions"][0]
        self.assertTrue(e["statut"].startswith("échouée"), e["statut"])
        self.assertNotEqual(e["code"], 0)
        d = os.path.join(self.tmp, "e4", "noyau", "tests-de-mort", r["identifiant_auteur"], "execution-01")
        self.assertIn("Network is unreachable", self.lire(os.path.join(d, "stderr.txt")))
        self.assertNotIn("RESEAU", self.lire(os.path.join(d, "stdout.txt")))
        self.assertEqual(r["verdict"], "non concluant")  # même si le script imprimait un résultat après la tentative
        with self.assertRaises(sk.timeout):
            ecoute.accept()  # le port du noyau n'a reçu aucune connexion
        # la sonde : un exécuteur non isolé est refusé
        ok, motif = ExecuteurNonIsole().disponible()
        self.assertFalse(ok)
        self.assertIn("réseau NON isolé", motif)
        ok, motif = ExecuteurReseauSeul().disponible()
        self.assertFalse(ok)
        self.assertIn("écriture hors du dossier de travail a réussi", motif)
        ok, motif = tdm.ExecuteurFactice().disponible()
        self.assertTrue(ok, motif)
        n = len(ad.appels)
        for executeur in (ExecuteurNonIsole(), ExecuteurReseauSeul()):
            with self.assertRaisesRegex(idn.CourseInterrompue, "bac à sable"):
                self.course(ad, "e4-refus", etage=self.etage(executeur=executeur), proposeurs=[("opus", "claude-opus-5-5")],
                            juges=[("juge-opus", "claude-opus-5-5")])
            self.assertEqual(len(ad.appels), n)  # rien payé, aucun appel
            self.assertFalse(os.path.exists(os.path.join(self.tmp, "e4-refus")))

    # --- 5. écriture hors du dossier -------------------------------------------------------------------------------------------

    def test_v48_05_ecriture_hors_du_dossier_echec_visible(self):
        """Un script qui écrit hors de son dossier de travail échoue (système de fichiers en lecture seule) : aucun fichier
        créé hors du dossier ; une écriture dans le dossier de travail réussit et est scellée parmi les fichiers produits."""
        hors = ("open('../hors-travail.txt', 'w').write('x')\nprint('ECRIT')\nprint('RESULTAT: 0.9')\n")
        dedans = "open('produit.txt', 'w').write('x')\nprint('RESULTAT: 0.9')\n"
        ad = self.kit({"opus": [self.fiche("Hors"), self.fiche("Dedans")]}, exp=lambda f, t, c: bloc_exp(executer(
            hors if f.endswith("-01") else dedans)) if t == 1 else bloc_fin())
        self.course(ad, "e5", etage=self.etage(nombre=2), proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")])
        par = self.par_fiche("e5")
        hors_id = [i for i, r in par.items() if r["executions"][0]["fichiers_produits"] == []][0]
        dedans_id = [i for i in par if i != hors_id][0]
        e = par[hors_id]["executions"][0]
        self.assertTrue(e["statut"].startswith("échouée"))
        d = os.path.join(self.tmp, "e5", "noyau", "tests-de-mort", hors_id)
        self.assertIn("Read-only file system", self.lire(os.path.join(d, "execution-01", "stderr.txt")))
        self.assertFalse(os.path.exists(os.path.join(d, "hors-travail.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "e5", "noyau", "tests-de-mort", "hors-travail.txt")))
        self.assertEqual(par[hors_id]["verdict"], "non concluant")
        e2 = par[dedans_id]["executions"][0]
        self.assertEqual(e2["statut"], "réussie")
        self.assertEqual([p["chemin"] for p in e2["fichiers_produits"]], ["produit.txt"])
        copie = os.path.join(self.tmp, "e5", "noyau", "tests-de-mort", dedans_id, "execution-01", "produits", "produit.txt.copie")  # v50 (CL14-05) : suffixe de copie
        self.assertTrue(idn.verifier_scelle(copie))

    # --- 6. quotas ----------------------------------------------------------------------------------------------------------------

    def test_v48_06_quatrieme_execution_et_seconde_du_tour_refusees(self):
        """Quota de trois exécutions par fiche, une demande refusée comptant : deux exécutions dans un même tour → la
        seconde refusée (et comptée) ; la quatrième demande refusée (quota) ; scripts non lancés pour les refus ; demandes
        mal formées (clé étrangère, type inconnu, script vide) refusées avec leur motif."""
        tours = {1: bloc_exp(executer(script_resultat(0.4))),
                 2: bloc_exp(executer(script_resultat(0.5)), executer(script_resultat(0.6))),  # la seconde du tour : refusée
                 3: bloc_exp(executer(script_resultat(0.7))),  # quatrième demande : quota
                 4: bloc_fin()}
        ad = self.kit({"opus": [self.fiche("Quota")]}, exp=lambda f, t, c: tours[t])
        self.course(ad, "e6", etage=self.etage(nombre=1), proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")])
        r = list(self.par_fiche("e6").values())[0]
        self.assertEqual([(e["numero"], e["statut"]) for e in r["executions"]],
                         [(1, "réussie"), (2, "réussie"), (3, "refusée"), (4, "refusée")])
        self.assertIn("une exécution par tour", r["executions"][2]["motif"])
        self.assertIn("quota : 3 exécutions par fiche", r["executions"][3]["motif"])
        d = os.path.join(self.tmp, "e6", "noyau", "tests-de-mort", r["identifiant_auteur"])
        self.assertTrue(os.path.exists(os.path.join(d, "execution-02", "script.py")))
        self.assertFalse(os.path.exists(os.path.join(d, "execution-03", "script.py")))
        self.assertFalse(os.path.exists(os.path.join(d, "execution-04", "script.py")))
        self.assertEqual(r["lecture_mecanique"]["chiffre"], 0.5)  # la dernière exécution réussie
        # unités
        q = pto.QuotasExperience(3, 12)
        self.assertEqual([q.compter_execution(1)[1] is None, q.compter_execution(1)[1] is None], [True, False])
        self.assertEqual((q.compter_execution(2)[1] is None, q.compter_execution(3)[1] is None), (True, False))
        self.assertEqual(q.restantes(), 0)
        for demande, motif in (({"executer": {"script": "x"}, "x": 1}, "clé étrangère"), ({"deviner": 1}, "demande inconnue"),
                               ({"lire": "a", "executer": {}}, "demande inconnue"), ("x", "objet attendu")):
            self.assertEqual(pto.classer_demande_experience(demande)[0], None, demande)
            self.assertIn(motif, pto.classer_demande_experience(demande)[1])
        self.assertEqual(pto.classer_demande_experience({"executer": {"script": "x"}}), ("executer", None))
        for script, motif in ((None, "script vide"), ("  ", "script vide"), ("x" * (tdm.TAILLE_MAX_SCRIPT + 1), "trop long"),
                              ("a\x00b", "caractère nul")):
            self.assertIn(motif, tdm.garde_script(script))
        self.assertIsNone(tdm.garde_script("print(1)"))
        self.assertEqual([s["signal"] for s in tdm.signaux_script("import socket\nopen('/etc/passwd')")],
                         ["module réseau, processus ou système", "chemin hors du dossier de travail"])

    # --- 7. délai --------------------------------------------------------------------------------------------------------------------

    def test_v48_07_delai_depasse_tue_et_non_concluant(self):
        """Un script qui dort au-delà du délai est tué (groupe de processus) : exécution « tuée (délai) », verdict
        mécanique « non concluant », lecteur honnête aussi ; le processus n'existe plus ensuite (R10)."""
        script = "import os, time\nprint('pid', os.getpid(), flush=True)\nprint('RESULTAT: 0.9', flush=True)\ntime.sleep(60)\n"
        ad = self.kit({"opus": [self.fiche("Lent")]}, exp=lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin())
        debut = time.monotonic()
        self.course(ad, "e7", etage=self.etage(nombre=1, delai_execution_s=1.0, executeur=tdm.ExecuteurFactice(delai_s=1.0)),
                    proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")])
        self.assertLess(time.monotonic() - debut, 25)
        r = list(self.par_fiche("e7").values())[0]
        e = r["executions"][0]
        self.assertEqual((e["statut"], e["delai_depasse"]), ("tuée (délai)", True))
        self.assertEqual(r["lecture_mecanique"]["verdict"], "non concluant")
        self.assertEqual((r["verdict"], r["desaccord"]), ("non concluant", None))
        sortie_standard = os.path.join(self.tmp, "e7", "noyau", "tests-de-mort", r["identifiant_auteur"], "execution-01", "stdout.txt")  # v50 (CL14-04) : le dossier de travail n'est plus gardé
        pid = int(self.lire(sortie_standard).split()[1])
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(sortie_standard), "travail")))
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    # --- 8. lecteur ------------------------------------------------------------------------------------------------------------------

    def test_v48_08_lecteur_hors_format_et_desaccord_valent_non_concluant(self):
        """Toute réponse du lecteur hors des trois mots vaut « non concluant » ; deux verdicts différents aussi ; un lecteur
        qui contredit la lecture mécanique du noyau → « non concluant » avec le désaccord consigné (R4) ; un lecteur
        conforme et d'accord donne son verdict."""
        a = tdm.analyser_verdict_lecteur
        self.assertEqual(a("Je pense qu'elle survit plutôt")["verdict"], "non concluant")
        self.assertIn("hors des trois mots", a("Peut-être")["motif"])
        self.assertEqual(a("")["verdict"], "non concluant")
        self.assertEqual(a(None)["verdict"], "non concluant")
        self.assertEqual(a("VERDICT: survit\nVERDICT: éliminée")["verdict"], "non concluant")
        self.assertIn("plusieurs verdicts", a("VERDICT: survit\nVERDICT: éliminée")["motif"])
        ok = a("VERDICT: survit ; chiffre: 0,4 ; ligne: RESULTAT: 0.4")
        self.assertEqual((ok["verdict"], ok["chiffre"], ok["ligne"]), ("survit", 0.4, "RESULTAT: 0.4"))
        self.assertEqual(a("VERDICT : éliminee")["verdict"], "éliminée")
        reponses = {"muet": "Je ne sais pas.", "contredit": "VERDICT: éliminée ; chiffre: 0,4 ; ligne: RESULTAT: 0.4",
                    "d'accord": "VERDICT: survit ; chiffre: 0,4 ; ligne: RESULTAT: 0.4"}
        fiches = {"opus": [self.fiche("muet"), self.fiche("contredit"), self.fiche("d'accord")]}

        def lec(fiche, consigne):
            nom = section_de(consigne, tdm.TITRE_SECTION_PREREG)["fiche"]["nom"]
            return reponses[nom]
        ad = self.kit(fiches, lec=lec)
        self.course(ad, "e8", etage=self.etage(nombre=3), proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")])
        par = {r["nom"]: r for r in self.etage_de("e8")["par_fiche"]}
        self.assertEqual({n: r["verdict"] for n, r in par.items()}, {"muet": "non concluant", "contredit": "non concluant", "d'accord": "survit"})
        self.assertIsNone(par["muet"]["desaccord"] and None)
        self.assertIn("hors des trois mots", par["muet"]["lecteur"]["motif"])
        self.assertIn("≠ lecture mécanique", par["contredit"]["desaccord"])
        self.assertEqual(par["contredit"]["lecture_mecanique"]["verdict"], "survit")
        self.assertIsNone(par["d'accord"]["desaccord"])

    # --- 9. classement modifié ------------------------------------------------------------------------------------------------------

    def test_v48_09_classement_modifie_pendant_l_etage_arret(self):
        """Le classement est figé (empreinte et sceau) avant l'étage, vérifié après : une modification pendant l'étage arrête
        la course (N-053 : aucune sélection sur le verdict), le manifeste de fin et celui de l'étage le disent ; l'étage ne
        se rejoue jamais."""
        sortie = os.path.join(self.tmp, "e9")

        def effets(fiche, role, tour):
            with open(os.path.join(sortie, "classement.json"), "a", encoding="utf-8") as f:
                f.write("\n")
        ad = self.kit(effets=effets)
        with self.assertRaisesRegex(idn.CourseInterrompue, "classement.json modifié pendant l'étage"):
            self.course(ad, "e9")
        fin = self.fin("e9")
        self.assertIn("classement.json modifié", fin["erreur"])
        etage = self.etage_de("e9")
        self.assertIs(etage["classement_intact"], False)
        self.assertNotEqual(etage["classement_sha256_apres"], etage["classement_sha256_avant"])
        self.assertIn("N-053", etage["arret"])
        self.assertFalse(idn.verifier_scelle(os.path.join(sortie, "classement.json")))
        # jamais rejoué
        with self.assertRaisesRegex(tdm.EtageRefuse, "jamais rejoué|déjà joué"):
            tdm.executer_tests_de_mort(ad, sortie, tranche=tdm.charger_tranche(self.prep()["tranche"], idn.charger_liste_blanche(
                self.prep()["liste_blanche"])), nombre=2, experimentateur=("exp", "claude-opus-5-5"), lecteur=("lec", "claude-fable-5-1"),
                executeur=tdm.ExecuteurFactice())

    # --- 10. changement de modèle ---------------------------------------------------------------------------------------------------

    def test_v48_10_changement_de_modele_de_l_experimentateur_refus(self):
        """Les trois barrières de la v47 s'appliquent à l'étage : options du kit des deux rôles (aucun outil, aucun repli de
        modèle, variables posées) ; un expérimentateur dont le modèle servi change (statut « refus ») → arrêt propre :
        sortie mise à l'écart, manifeste de l'étage et de fin avec le modèle demandé et servi, `statut_course` « refus »,
        dépense sous modèle non autorisé à part, jamais « budget dépassé » ; modèle de l'étage hors des modèles permis
        refusé avant tout appel."""
        from essais.faux_sdk import claude_agent_sdk as faux_sdk
        for role in tdm_roles():
            o = construire_options(os.path.join(self.tmp, "x", "y", "z"), 1.0, 2, url_relais="http://127.0.0.1:9", modele="claude-opus-5-5",
                                   role=role, interdire_lecture=[os.path.join(self.tmp, "x")])
            self.assertEqual((o["tools"], o["allowed_tools"]), ([], []), role)
            self.assertIsNone(o["fallback_model"])
            self.assertEqual(o["env"]["CLAUDE_CODE_NO_MODEL_FALLBACK"], "true")
            self.assertEqual(o["env"]["CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK"], "1")
            self.assertIn("aucun outil", o["system_prompt"].lower() if role == "lecteur_test" else o["system_prompt"])
            self.assertEqual(o["effort"], {"experimentateur_test": "high", "lecteur_test": "medium"}[role])

        class KitRefus(FauxKitEtage):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, **lecture):
                r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)
                if role == "experimentateur_test":
                    return Resultat("", [], 0.9, "refus", "refus (R-764) : modèle servi ≠ modèle demandé",
                                    refus={"motif": "modèle servi 'claude-opus-4-8' ≠ modèle demandé", "modele_demande": modele,
                                           "modele_servi": "claude-opus-4-8", "evenement": "assistant.model"},
                                    modele_servi="claude-opus-4-8", depense_modele_non_autorise_usd=0.9, cout_inconnu=True)
                return r
        c = self.cours()
        ad = KitRefus({"opus": [self.fiche("O1")], "fable": [self.fiche("F1")]},
                      notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        with self.assertRaisesRegex(idn.CourseInterrompue, "refus \\(R-764\\)") as ctx:
            self.course(ad, "e10", etage=self.etage(nombre=1))
        self.assertNotIn("budget", str(ctx.exception).lower())
        fin = self.fin("e10")
        self.assertEqual(fin["statut_course"]["statut"], "refus")
        self.assertEqual((fin["statut_course"]["role"], fin["statut_course"]["modele_servi"]), ("experimentateur_test", "claude-opus-4-8"))
        self.assertEqual(fin["depense_modele_non_autorise_usd"], 0.9)
        self.assertEqual(fin["refus_modele"][0]["modele_demande"], "claude-opus-5-5")
        self.assertEqual(fin["tests_de_mort_exploratoires"]["statut"], "interrompu")
        etage = self.etage_de("e10")
        self.assertIn("refus (R-764)", etage["arret"])
        self.assertEqual(etage["couts"]["claude_usd"], 0.0 + 0.9)  # le coût inconnu compte le plafond lu au relais : ici le déclaré
        sortie = os.path.join(self.tmp, "e10")
        ecart = os.path.join(sortie, "A-L-ECART-modele-non-autorise", "noyau", "tests-de-mort")
        self.assertTrue(os.path.isdir(ecart))
        ident = etage["candidates"][0]
        self.assertFalse(os.path.exists(os.path.join(sortie, "noyau", "tests-de-mort", ident, "experimentateur", "tour-001")))
        self.assertFalse([a for a in ad.appels if a["role"] == "lecteur_test"])
        # modèle de l'étage hors des modèles permis (moteur réel) : refusé avant tout appel
        from pole.adaptateurs import ModeleNonPermis
        with self.assertRaises(ModeleNonPermis):
            idn.exiger_reglages_tests_de_mort(
                self.etage(experimentateur=("exp", "claude-opus-4-8"),
                           executeur=tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3")),
                idn.charger_liste_blanche(self.prep()["liste_blanche"]), moteur="claude-sdk")

    # --- 11. rétrocompatibilité ----------------------------------------------------------------------------------------------------------

    def test_v48_11_retrocompatibilite_octet_pour_octet_avec_la_v47_sans_l_option(self):
        """Sans `etage_tests`, la course de la v48 produit les mêmes sorties que la v47 (empreintes de la v47 reconstruite :
        classement, fiches, notes, lecture, consignes des proposeurs et des juges, `reglages_kit`) ; aucune clé de l'étage
        au manifeste de départ ni de fin ; aucun dossier d'étage ; le gabarit servi est `GABARIT` ; `etage_tests` à
        `{"nombre": 0}` vaut l'étage absent ; un champ `test_de_mort` est hors gabarit sans l'option."""
        c = self.cours()
        c._prep = c.preparer()
        ad = FauxAdaptateur({"opus": [fiche_brute(nom="O1"), fiche_brute(nom="O2", type="approche")], "fable": [fiche_brute(nom="F1")]},
                            notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        c.lancer(ad, "r1", seconde_passe=True)
        sortie = os.path.join(self.tmp, "r1")
        for nom, h in SORTIES_V47_SHA256.items():
            self.assertEqual(idn.sha256_fichier(os.path.join(sortie, nom)), h, nom)
        for nom, h in CONSIGNES_V47_SHA256.items():
            self.assertEqual(idn.sha256_fichier(os.path.join(sortie, nom)), h, nom)
        depart = self.json("r1", "manifeste-depart.json")["reglages"]
        self.assertEqual(hashlib.sha256(json.dumps(depart["reglages_kit"], sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                         REGLAGES_KIT_V47_SHA256)
        self.assertNotIn("tests_de_mort", depart)
        self.assertNotIn("etage_tests_claude_usd", depart["somme_des_plafonds"])
        self.assertEqual(sorted(depart["reglages_kit"]), sorted(["experimentateur", "verificateur", "recombinaison", "synthese",
                                                                  "proposeur", "proposeur_ideation", "juge_ideation"]))
        fin = self.fin("r1")
        self.assertNotIn("tests_de_mort_exploratoires", fin)
        self.assertNotIn("cout_etage_tests_usd", fin["journal"])
        self.assertFalse(os.path.exists(os.path.join(sortie, "noyau", "tests-de-mort")))
        self.assertFalse(os.path.exists(os.path.join(sortie, "manifeste-tests-de-mort.json")))
        self.assertIs(idn.gabarit(False), idn.GABARIT)
        self.assertIs(idn.gabarit(False, False), idn.GABARIT)
        self.assertNotIn("test_de_mort", idn.gabarit(True))
        self.assertIn("test_de_mort", idn.gabarit(False, True))
        self.assertEqual(idn.fiche_maximale(), idn.fiche_maximale(False))
        self.assertNotIn("test_de_mort", idn.fiche_maximale())
        with self.assertRaisesRegex(idn.FicheIdeationInvalide, "champs hors gabarit : test_de_mort"):
            idn.valider_fiche_ideation(self.fiche("X"), "opus", 1)
        # `nombre: 0` vaut l'étage absent
        self.assertIsNone(idn.exiger_reglages_tests_de_mort({"nombre": 0}, {}))
        self.assertIsNone(idn.exiger_reglages_tests_de_mort(None, {}))
        c.lancer(FauxAdaptateur({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                                notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok}), "r2",
                 etage_tests={"nombre": 0})
        self.assertNotIn("tests_de_mort", self.json("r2", "manifeste-depart.json")["reglages"])
        # sans l'option, l'ancien jeu de rôles du kit est inchangé
        from pole.adaptateurs import ROLES, ROLES_ETAGE_TESTS
        self.assertEqual(list(reglages_kit_par_role()), list(ROLES))
        self.assertEqual(list(reglages_kit_par_role(etage_tests=True)), list(ROLES) + list(ROLES_ETAGE_TESTS))

    # --- 12. bac à sable absent ----------------------------------------------------------------------------------------------------------------

    def test_v48_12_bac_a_sable_absent_refuse_sans_repli_et_commande_du_vrai_bac(self):
        """Sans `bwrap`, l'étage est refusé avant tout appel, motif consigné, aucun repli sur un autre exécuteur ; l'étage
        direct sur une course faite est refusé sans rien écrire ; la commande du vrai bac à sable porte l'isolation du réseau,
        la racine en lecture seule, l'environnement vidé, le seul dossier de travail en écriture, la tranche en lecture seule ;
        v49 (CL13-01) : le script n'est plus superutilisateur et n'a aucune capacité (`--unshare-user --uid --gid --cap-drop ALL`),
        `--new-session` y est (le noyau ne lance plus `bwrap` comme chef de session : voir `TestV49`)."""
        absent = tdm.ExecuteurBacASable(chercher=lambda nom: None)
        self.assertIn("bwrap absent", absent.verifier_outils())
        ok, motif = absent.disponible()
        self.assertFalse(ok)
        self.assertIn("aucun repli", motif)
        ad = self.kit()
        with self.assertRaisesRegex(idn.CourseInterrompue, "bwrap absent"):
            self.course(ad, "e12", etage=self.etage(executeur=absent))
        self.assertEqual(ad.appels, [])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "e12")))
        # étage direct, sur une course faite avec l'exécuteur factice : refusé, rien écrit
        self.course(self.kit(), "e12b", etage=self.etage(nombre=1))
        os.rename(os.path.join(self.tmp, "e12b", "noyau", "tests-de-mort"), os.path.join(self.tmp, "e12b-etage-joue"))
        os.rename(os.path.join(self.tmp, "e12b", "manifeste-tests-de-mort.json"), os.path.join(self.tmp, "e12b-manifeste.json"))
        liste = idn.charger_liste_blanche(self.prep()["liste_blanche"])
        with self.assertRaisesRegex(tdm.EtageRefuse, "bac à sable : bwrap absent"):
            tdm.executer_tests_de_mort(self.kit(), os.path.join(self.tmp, "e12b"), tranche=tdm.charger_tranche(self.prep()["tranche"], liste),
                                       nombre=1, experimentateur=("exp", "claude-opus-5-5"), lecteur=("lec", "claude-fable-5-1"), executeur=absent)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "e12b", "noyau", "tests-de-mort")))
        # commande du vrai bac à sable (bwrap factice, rien n'est lancé)
        vrai = tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3", delai_s=5.0)
        travail = os.path.join(self.tmp, "travail-commande")
        os.makedirs(os.path.join(travail, "tranche"))
        cmd = vrai.commande(os.path.join(travail, "script.py"), travail)
        self.assertEqual(cmd[0], "/usr/bin/bwrap")
        for drapeau in ("--unshare-all", "--unshare-net", "--die-with-parent", "--clearenv", "--remount-ro"):
            self.assertIn(drapeau, cmd)
        self.assertIn("--new-session", cmd)
        self.assertNotIn("--share-net", cmd)
        liens = [(cmd[i], cmd[i + 1], cmd[i + 2]) for i, x in enumerate(cmd) if x in ("--bind", "--ro-bind")]
        self.assertIn(("--bind", travail, "/travail"), liens)
        self.assertIn(("--ro-bind", os.path.join(travail, "tranche"), "/travail/tranche"), liens)
        self.assertIn(("--ro-bind", "/usr", "/usr"), liens)
        self.assertEqual([l for l in liens if l[0] == "--bind"], [("--bind", travail, "/travail")])  # seule écriture
        racine_ro = [i for i, x in enumerate(cmd) if x == "--remount-ro" and cmd[i + 1] == "/"]  # v51 : `--remount-ro /dev` d'abord
        self.assertEqual(len(racine_ro), 1)
        self.assertLess(cmd.index("--bind"), racine_ro[0])
        self.assertEqual([cmd[i + 1] for i, x in enumerate(cmd) if x == "--remount-ro"], ["/dev", "/"])
        self.assertEqual(cmd[-5:], ["--", "/usr/bin/python3", "-I", "-B", "/travail/script.py"])
        self.assertEqual(cmd[cmd.index("--chdir") + 1], "/travail")
        d = vrai.description()
        self.assertIn("--unshare-net", d["isolation"])
        self.assertFalse(d["factice"])

    # --- 13. réglages refusés avant tout appel --------------------------------------------------------------------------------------------------------------

    def test_v48_13_reglages_refuses_avant_tout_appel(self):
        """Chaque réglage incohérent de l'étage est refusé avant tout appel et toute écriture : nombre, tranche, expérimentateur
        et lecteur, étiquettes, plafonds, quotas, délai, mémoire, tranche hors liste blanche ou nommée `donnees`, exécuteur
        factice avec le moteur réel."""
        liste = idn.charger_liste_blanche(self.prep()["liste_blanche"])
        ad = self.kit()
        tr = self.prep()["tranche"]
        cas = [({"nombre": 13}, "entier de 0 à 12"), ({"nombre": True}, "entier de 0 à 12"), ({"nombre": 1.5}, "entier de 0 à 12"),
               ({"tranche": None}, "tranche exploratoire"), ({"experimentateur": None}, "un expérimentateur et un seul"),
               ({"experimentateur_externe": ("a", "autre", None)}, "un expérimentateur et un seul"),
               ({"lecteur": None}, "lecteur neuf"), ({"lecteur": ("exp", "claude-fable-5-1")}, "autre étiquette"),
               ({"lecteur": ("lec",)}, "(étiquette, modèle)"), ({"budget_test_usd": 0}, "budget_test_usd"),
               ({"budget_lecteur_usd": float("nan")}, "budget_lecteur_usd"), ({"budget_test_usd": -1}, "budget_test_usd"),
               ({"budget_test_usd": True}, "budget_test_usd"), ({"executions_par_fiche": 0}, "executions_par_fiche"),
               ({"executions_par_fiche": 21}, "executions_par_fiche"), ({"delai_execution_s": 0}, "delai_execution_s"),
               ({"delai_execution_s": 4000}, "delai_execution_s"), ({"delai_execution_s": float("inf")}, "delai_execution_s"),
               ({"memoire_mo": 10}, "memoire_mo"), ({"tranche": os.path.join(self.tmp, "absente")}, "tranche exploratoire refusée"),
               ({"surprise": 1}, "dictionnaire de")]
        for modif, motif in cas:
            with self.assertRaisesRegex(idn.CourseInterrompue, motif, msg=str(modif)):
                self.course(ad, "e13", etage=self.etage(**modif))
        self.assertEqual(ad.appels, [])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "e13")))
        with self.assertRaisesRegex(idn.CourseInterrompue, "dictionnaire de"):
            idn.exiger_reglages_tests_de_mort("deux", liste)
        # étage absent mais d'autres réglages donnés
        with self.assertRaisesRegex(idn.CourseInterrompue, "ne se donnent qu'avec tests_de_mort"):
            idn.exiger_reglages_tests_de_mort({"nombre": 0, "tranche": tr}, liste)
        # tranche hors de la liste blanche (index non listé), tranche dont le chemin porte `donnees`
        autre = os.path.join(self.tmp, "autre-tranche")
        os.makedirs(autre)
        with open(os.path.join(autre, "s.csv"), "w", encoding="utf-8") as f:
            f.write("1\n")
        dfm.ecrire_index(autre, [{"chemin": "s.csv", "titre": "S", "resume": "r"}])
        with self.assertRaisesRegex(idn.CourseInterrompue, "tranche exploratoire refusée"):
            idn.exiger_reglages_tests_de_mort(self.etage(tranche=autre), liste)
        interdit = os.path.join(self.tmp, "donnees", "t")
        os.makedirs(interdit)
        with open(os.path.join(interdit, "s.csv"), "w", encoding="utf-8") as f:
            f.write("1\n")
        dfm.ecrire_index(interdit, [{"chemin": "s.csv", "titre": "S", "resume": "r"}])
        lb2 = os.path.join(self.tmp, "liste-donnees.json")
        idn.construire_liste_blanche([os.path.join(interdit, "index.json")], lb2)
        with self.assertRaisesRegex(idn.CourseInterrompue, "tranche exploratoire refusée"):
            idn.exiger_reglages_tests_de_mort(self.etage(tranche=interdit), idn.charger_liste_blanche(lb2))
        # exécuteur factice avec le moteur réel
        with self.assertRaisesRegex(idn.CourseInterrompue, "exécuteur factice refusé avec le moteur réel"):
            idn.exiger_reglages_tests_de_mort(self.etage(), liste, moteur="claude-sdk")
        with self.assertRaisesRegex(idn.CourseInterrompue, "seule une commande externe"):
            idn.exiger_reglages_tests_de_mort(self.etage(experimentateur=None, experimentateur_externe=("argon", "autre", self.kit()),
                                                         executeur=tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3")),
                                              liste, moteur="claude-sdk")
        # cas sain : normalisé
        r = idn.exiger_reglages_tests_de_mort(self.etage(), liste)
        self.assertEqual((r["nombre"], r["plafond_claude_usd"], r["plafond_externe_usd"]), (2, 1.2, 0.0))
        r = idn.exiger_reglages_tests_de_mort(self.etage(experimentateur=None, experimentateur_externe=("argon", "autre", self.kit())), liste)
        self.assertEqual((r["plafond_claude_usd"], r["plafond_externe_usd"]), (0.2, 1.0))

    # --- 14. sommes -------------------------------------------------------------------------------------------------------------------------------------------

    def test_v48_14_l_etage_entre_dans_les_sommes_et_dans_verifier_reglages(self):
        """Les plafonds de l'étage (fiches × expérimentateur + lecteur) entrent dans la somme des plafonds Claude (ou externe
        pour un expérimentateur d'Argon) ; refus avant tout appel si le total ne suffit pas ; `verifier_reglages` rend
        l'étage, la plus grosse consigne de l'expérimentateur et la tranche dans les consignes de contrôle."""
        ad = self.kit()
        # somme sans étage : 2 proposeurs + 2 juges à 1,0 = 4,0 ; étage : 2 × 0,6 = 1,2
        ad_sans = FauxKitEtage({"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]},
                               notes_par_juge={"juge-fable": self.cours().notes_temoins_ok, "juge-opus": self.cours().notes_temoins_ok})
        self.course(ad_sans, "e14a", etage=False, budget_total_usd=4.0)
        n = len(ad.appels)
        with self.assertRaisesRegex(idn.CourseInterrompue, "somme des plafonds Claude 5.20"):
            self.course(ad, "e14b", budget_total_usd=5.0)
        self.assertEqual(len(ad.appels), n)
        self.course(ad, "e14c", budget_total_usd=5.2)
        prep = self.prep()
        v = idn.verifier_reglages(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"],
                                  temoins=prep["temoins"], budgets=self.cours().budgets(), budget_total_usd=5.2,
                                  proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                                  juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")], etage_tests=self.etage(),
                                  )
        self.assertAlmostEqual(v["somme_claude"], 5.2)
        self.assertEqual(v["tests_de_mort"]["nombre"], 2)
        self.assertGreater(v["tests_de_mort"]["consigne_experimentateur_maximale"], 3 * tdm.TAILLE_MAX_SCRIPT)
        self.assertIn("## Tranche exploratoire", v["texte_controle_externe"])
        self.assertIn('"seuil"', v["texte_controle_externe"])  # le champ test_de_mort au gabarit
        self.assertIn("sonde OK", v["tests_de_mort"]["bac_a_sable"]["sonde"])
        v0 = idn.verifier_reglages(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"],
                                   temoins=prep["temoins"], budgets=self.cours().budgets(), budget_total_usd=5.2,
                                   proposeurs=[("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")],
                                   juges=[("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")])
        self.assertNotIn("tests_de_mort", v0)
        self.assertAlmostEqual(v0["somme_claude"], 4.0)
        # plafond total atteint pendant l'étage → arrêt dur nommé
        with self.assertRaisesRegex(idn.CourseInterrompue, "plafond total atteint avant experimentateur_test"):
            self.course(self.kit(cout=1.0), "e14d", budget_total_usd=4.4, tolerer_somme_claude=True)
        etage = self.etage_de("e14d")
        self.assertIn("plafond total atteint", etage["arret"])

    # --- 15. fiche : champ test_de_mort -----------------------------------------------------------------------------------------------------------------

    def test_v48_15_champ_test_de_mort_de_la_fiche(self):
        """Le champ facultatif `test_de_mort` ({seuil, test, donnees}) : valide sous l'option, absent admis (la fiche est
        valide ; l'étage la refusera), mal formé ou trop long refusé (taille comptée comme refus pour taille)."""
        v = lambda t: idn.valider_fiche_ideation(fiche_brute(test_de_mort=t), "opus", 1, tests_de_mort=True)  # noqa: E731
        f = v(self.champ_test())
        self.assertEqual(f["test_de_mort"], self.champ_test())
        self.assertEqual(list(f).index("test_de_mort"), list(f).index("anteriorite") + 1)
        self.assertNotIn("test_de_mort", idn.valider_fiche_ideation(fiche_brute(), "opus", 1, tests_de_mort=True))
        # empreinte : le champ y entre
        self.assertNotEqual(f["empreinte"], idn.valider_fiche_ideation(fiche_brute(), "opus", 1, tests_de_mort=True)["empreinte"])
        for mal in ("texte", [], {"seuil": "au moins 1"}, {"seuil": "", "test": "t", "donnees": ["a"]},
                    {"seuil": "au moins 1", "test": "t", "donnees": []}, {"seuil": "au moins 1", "test": "t", "donnees": [1]},
                    {"seuil": "au moins 1", "test": "t", "donnees": ["a"], "plus": 1}, {"seuil": 1, "test": "t", "donnees": ["a"]}):
            with self.assertRaises(idn.FicheIdeationInvalide, msg=str(mal)):
                v(mal)
        for long in ({"seuil": "x" * (tdm.TAILLE_MAX_SEUIL + 1), "test": "t", "donnees": ["a"]},
                     {"seuil": "s 1", "test": "x" * (tdm.TAILLE_MAX_TEST + 1), "donnees": ["a"]},
                     {"seuil": "s 1", "test": "t", "donnees": ["a"] * (tdm.MAX_DONNEES + 1)},
                     {"seuil": "s 1", "test": "t", "donnees": ["x" * (tdm.TAILLE_MAX_CHEMIN_DONNEE + 1)]}):
            with self.assertRaises(idn.FicheTropLongue):
                v(long)
        # le pire cas valide : la fiche maximale avec le champ passe la validation
        idn.valider_fiche_ideation(idn.fiche_maximale(True), "opus", 1, tests_de_mort=True)
        self.assertGreater(idn.taille_servie(idn.fiche_maximale(True)), idn.taille_servie(idn.fiche_maximale()))
        # secret dans le champ : caviardé comme tout champ
        f = v({"seuil": "au moins 1", "test": "clé sk-ant-api03-abcdefghijklmnopqrstuvwxyz0123456789", "donnees": ["a"]})
        self.assertNotIn("sk-ant-api03", f["test_de_mort"]["test"])

    # --- 16. seuil et comparateurs ------------------------------------------------------------------------------------------------------------------------

    def test_v48_16_lecture_du_seuil_et_des_comparateurs(self):
        """Le comparateur est lu dans le texte du seuil (le plus tôt), sinon dans le signe de la prédiction ; le nombre est le
        premier qui suit ; virgule décimale et moins typographique ; seuil non chiffré refusé."""
        ls = tdm.lire_seuil
        self.assertEqual(ls("au moins 0,15", "+")[:2], (0.15, "≥"))
        self.assertEqual(ls("≤ 0,05", "+")[:2], (0.05, "≤"))
        self.assertEqual(ls("au plus 2", "+")[:2], (2.0, "≤"))
        self.assertEqual(ls("strictement supérieur à 0,5", "-")[:2], (0.5, ">"))
        self.assertEqual(ls("moins de 3 points", "+")[:2], (3.0, "<"))
        self.assertEqual(ls("−0,2 ou moins", "-")[:2], (-0.2, "≤"))
        self.assertEqual(ls("0,25", "+")[:3], (0.25, "≥", "signe de la prédiction (+)"))
        self.assertEqual(ls("0,25", "-")[:2], (0.25, "≤"))
        self.assertEqual(ls("0,25", "0")[:2], (0.25, "|x| ≤"))
        self.assertEqual(ls("rappel ≥ 0,9 à 1 % de fausses alertes", "+")[:2], (0.9, "≥"))
        self.assertIsNone(ls("à voir", "+")[0])
        self.assertIsNone(ls(None, "+")[0])
        self.assertIsNone(ls("0,25", "?")[0])
        for valeur, comp, seuil, attendu in ((0.3, "≥", 0.3, True), (0.29, "≥", 0.3, False), (0.3, ">", 0.3, False), (0.3, "≤", 0.3, True),
                                              (0.31, "<", 0.3, False), (-0.2, "|x| ≤", 0.25, True), (0.3, "|x| ≤", 0.25, False)):
            self.assertIs(tdm.comparer(valeur, comp, seuil), attendu, (valeur, comp, seuil))
        with self.assertRaises(ValueError):
            tdm.comparer(1, "~", 1)
        self.assertEqual(tdm.lignes_resultat("a\nRESULTAT: 0,4\n  RESULTAT : -1e-3 \nRESULTAT: x\nRESULTAT: 2 3"), ["RESULTAT: 0,4", "RESULTAT : -1e-3"])
        ex = [{"numero": 1, "statut": "réussie", "lignes_resultat": ["RESULTAT: 0.2"]},
              {"numero": 2, "statut": "tuée (délai)", "lignes_resultat": ["RESULTAT: 0.9"]},
              {"numero": 3, "statut": "échouée (code 1)", "lignes_resultat": ["RESULTAT: 0.8"]}]
        self.assertEqual(tdm.chiffre_lu(ex), (0.2, "RESULTAT: 0.2", 1))
        self.assertEqual(tdm.chiffre_lu([]), (None, None, None))
        self.assertEqual(tdm.chiffre_lu([{"numero": 1, "statut": "réussie", "lignes_resultat": []}]), (None, None, 1))

    # --- 17. mesurer_consignes ------------------------------------------------------------------------------------------------------------------------------

    def test_v48_17_mesurer_consignes_avec_etage(self):
        """`mesurer_consignes` mesure, sans appel ni écriture, les consignes de proposition avec la tranche et le champ au
        pire cas, la plus grosse consigne de l'expérimentateur et celle du lecteur ; sans étage, rien de neuf."""
        prep = self.prep()
        args = dict(liste_blanche=prep["liste_blanche"], question=prep["question"], pieces=prep["pieces"], temoins=prep["temoins"],
                    seconde_passe=True, materiau=prep["materiau"], nombre_par_proposeur=4)
        sans = idn.mesurer_consignes(**args)
        avec = idn.mesurer_consignes(**args, etage_tests=self.etage())
        self.assertNotIn("tests_de_mort", sans)
        t = avec["tests_de_mort"]
        self.assertEqual((t["nombre"], t["plafond_etage_claude_usd"]), (2, 1.2))
        self.assertGreater(t["consigne_experimentateur_maximale"], 3 * tdm.TAILLE_MAX_SCRIPT)
        self.assertGreater(t["consigne_lecteur_maximale"], 40_000)
        self.assertGreater(avec["consigne_passe_1"], sans["consigne_passe_1"])
        self.assertGreater(avec["taille_fiche_maximale_servie"], sans["taille_fiche_maximale_servie"])
        self.assertEqual(os.listdir(self.tmp).count("e17"), 0)

    # --- 18. Argon expérimentateur : même consigne ----------------------------------------------------------------------------------------------------------------

    def test_v48_18_experimentateur_externe_meme_consigne_cout_externe(self):
        """Argon (adaptateur externe, par protocole) reçoit exactement la consigne de l'expérimentateur Claude pour une même
        fiche ; son coût est compté « externe » ; ses plafonds entrent dans la somme externe ; le lecteur reste Claude."""
        c = self.cours()
        notes = {"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok}
        fiches = {"opus": [self.fiche("O1")], "fable": [self.fiche("F1")]}
        ad1 = FauxKitEtage(fiches, notes_par_juge=notes)
        self.course(ad1, "e18a", etage=self.etage(nombre=1))
        externe = FauxKitEtage(fiches, notes_par_juge=notes, cout_exp=0.07)
        ad2 = FauxKitEtage(fiches, notes_par_juge=notes)
        self.course(ad2, "e18b", etage=self.etage(nombre=1, experimentateur=None, experimentateur_externe=("argon", "autre-lignee-x", externe)),
                    budget_externe_usd=2.0)
        premiere = lambda ad: [a["consigne"] for a in ad.appels if a["role"] == "experimentateur_test"][0]  # noqa: E731
        self.assertEqual(premiere(ad1), premiere(externe))
        self.assertEqual([a["role"] for a in ad2.appels if a["role"] in ("experimentateur_test", "lecteur_test")], ["lecteur_test"])
        self.assertEqual(len([a for a in externe.appels if a["role"] == "experimentateur_test"]), 2)
        etage = self.etage_de("e18b")
        self.assertEqual(etage["couts"], {"claude_usd": 0.02, "externe_usd": round(2 * 0.07, 6)})
        self.assertTrue(etage["experimentateur"]["externe"])
        fin = self.fin("e18b")
        self.assertAlmostEqual(fin["journal"]["cout_externe_usd"], 0.14)
        self.assertEqual([a["externe"] for a in self.json("e18b", "manifeste-tests-de-mort.json")["reglages"]["journal"]["appels"]],
                         [True, True, False])
        # le plafond externe de l'étage entre dans la somme externe
        with self.assertRaisesRegex(idn.CourseInterrompue, "somme des plafonds externes"):
            self.course(FauxKitEtage(fiches, notes_par_juge=notes), "e18c", budget_externe_usd=0.4,
                        etage=self.etage(nombre=1, experimentateur=None, experimentateur_externe=("argon", "autre-lignee-x", externe)))

    # --- 19. demandes de l'expérimentateur par le protocole -----------------------------------------------------------------------------------------------------

    def test_v48_19_demandes_par_protocole_lecture_tranche_et_refus(self):
        """Lecture d'un fichier de la tranche (servi avec son empreinte), fichier hors tranche refusé, pages du dossier fermé
        refusées sans dossier, clé étrangère refusée, type inconnu refusé ; les réponses sont servies au tour suivant entre
        délimiteurs, jamais comme consigne ; un script trop gros ou vide est refusé et compté."""
        demandes = [{"lire_tranche": "serie-b.csv"}, {"lire_tranche": "../serie-a.csv"}, {"lire": "x.md", "pages": [1, 1]},
                    {"chercher": "motif"}, {"lire_tranche": "serie-a.csv", "pages": [1]}, {"deviner": 1}, executer({"script": 1}),
                    {"executer": {"script": ""}}]
        tours = {1: bloc_exp(*demandes), 2: bloc_fin()}
        ad = self.kit({"opus": [self.fiche("Protocole")]}, exp=lambda f, t, c: tours[t])
        self.course(ad, "e19", etage=self.etage(nombre=1), proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")])
        r = list(self.par_fiche("e19").values())[0]
        consigne2 = [a["consigne"] for a in ad.appels if a["role"] == "experimentateur_test"][1]
        histo = section_de(consigne2, "Ce que le noyau t'a servi")
        reps = histo[0]["reponses"]
        self.assertEqual([x["statut"] for x in reps], ["servie", "refusée", "refusée", "refusée", "refusée", "refusée", "refusée", "refusée"])
        self.assertEqual(reps[0]["texte"], "c\n7\n8\n")
        self.assertEqual(reps[0]["sha256"], idn.sha256_fichier(os.path.join(self.prep()["tranche"], "serie-b.csv")))
        self.assertIn("hors de la tranche exploratoire", reps[1]["motif"])
        self.assertIn("aucun dossier fermé", reps[2]["motif"])
        self.assertIn("clé étrangère", reps[4]["motif"])
        self.assertIn("demande inconnue", reps[5]["motif"])
        self.assertEqual([(e["numero"], e["statut"], e["motif"]) for e in r["executions"]],
                         [(1, "refusée", "script vide"), (2, "refusée", "une exécution par tour : la seconde demande de ce tour "
                                                        "est refusée (et comptée)")])
        self.assertIn("Quotas restants", consigne2)
        self.assertEqual(r["verdict"], "non concluant")

    # --- 20. arrêts, plafond de la fiche, manifeste sur tout chemin -----------------------------------------------------------------------------------------------

    def test_v48_20_arrets_plafond_de_la_fiche_et_manifeste_sur_tout_chemin(self):
        """Plafond en dollars de la fiche atteint → fin des tours (verdict sur ce qui a été exécuté) ; session de
        l'expérimentateur ou du lecteur en erreur → arrêt dur nommé, manifeste de l'étage et de fin écrits ; classement
        illisible (témoins échoués) → étage refusé avant tout appel, course close normalement ; l'étage ne se rejoue pas."""
        # plafond de la fiche : chaque session coûte 0,6 pour un plafond de 0,5
        ad = self.kit({"opus": [self.fiche("Cher")]}, cout_exp=0.6, exp=lambda f, t, c: bloc_exp(executer(script_resultat(0.4))))
        self.course(ad, "e20a", etage=self.etage(nombre=1), proposeurs=[("opus", "claude-opus-5-5")],
                    juges=[("juge-opus", "claude-opus-5-5")], tolerer_somme_claude=True)
        r = list(self.par_fiche("e20a").values())[0]
        self.assertIn("plafond de la fiche", r["fin_des_tours"])
        self.assertEqual((r["tours"], len(r["executions"]), r["verdict"]), (1, 1, "survit"))
        # session de l'expérimentateur en erreur
        for nom, kw, motif in (("e20b", {"statut_exp": "erreur"}, "session experimentateur_test/exp"),
                               ("e20c", {"statut_lec": "erreur"}, "session lecteur_test/lec")):
            ad = self.kit(**kw)
            with self.assertRaisesRegex(idn.CourseInterrompue, motif):
                self.course(ad, nom)
            self.assertTrue(idn.verifier_scelle(os.path.join(self.tmp, nom, "manifeste-tests-de-mort.json")))
            self.assertIn(motif, self.etage_de(nom)["arret"])
            self.assertIn(motif, self.fin(nom)["erreur"])
            self.assertEqual(self.fin(nom)["tests_de_mort_exploratoires"]["statut"], "interrompu")
        # classement illisible : les témoins échouent (notes plates) → étage refusé, course normale
        c = self.cours()
        ad = FauxKitEtage({"opus": [self.fiche("O1")], "fable": [self.fiche("F1")]}, notes_base=2)
        self.course(ad, "e20d")
        fin = self.fin("e20d")
        self.assertEqual(fin["tests_de_mort_exploratoires"]["statut"], "refusé avant tout appel (rien payé)")
        self.assertIn("classement illisible", fin["tests_de_mort_exploratoires"]["motif"])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "e20d", "noyau", "tests-de-mort")))
        self.assertEqual([a for a in ad.appels if a["role"] in ("experimentateur_test", "lecteur_test")], [])

    # --- 21. lanceur ------------------------------------------------------------------------------------------------------------------------------------------------

    def lanceur(self):
        return self.v41().lanceur()

    def v41(self):
        t = TestV41("test_tolerances_separees")
        t.tmp = self.tmp
        return t

    def cmd(self):
        return self.v41().cmd()

    def argv(self, sortie, *options, juge_externe=False):
        prep = self.prep()
        b = [sortie, "--liste-blanche", prep["liste_blanche"], "--question", prep["question"], "--piece", prep["pieces"][0],
             "--temoins", prep["temoins"], "--nombre", "4", "--horodatage", "2026-10-29T12:00:00Z"]
        if juge_externe:
            b += ["--juge-externe", "argon-j=gemini-argon", "--budget-externe-usd", "5"]
        return b + list(options)

    def option_etage(self, n=2, **plus):
        o = ["--tests-de-mort", str(n), "--tranche-exploratoire", self.prep()["tranche"], "--experimentateur", "exp=claude-opus-5-5",
             "--lecteur-test", "lec=claude-fable-5-1", "--executeur-tests", "factice"]
        return o

    def principal(self, argv):
        return self.v41().principal(self.lanceur(), argv)

    def test_v48_21_lanceur(self):
        """Lanceur : options incohérentes refusées (SystemExit 2) ; course simulée avec `--tests-de-mort` : bilan, manifeste de fin,
        étage joué par le cœur ; `--mesurer-consignes` avec étage ; course à juge externe : étage différé, puis joué après le
        bras (`--bras-rapporte-differe --tests-de-mort`) ; sans l'option, ni bilan ni dossier d'étage."""
        lanceur = self.lanceur()
        refus = [(["--tests-de-mort", "0", "--tranche-exploratoire", self.prep()["tranche"]], "ne se donne qu'avec --tests-de-mort"),
                 (["--experimentateur", "exp=claude-opus-5-5"], "ne se donne qu'avec --tests-de-mort"),
                 (["--executeur-tests", "factice"], "ne se donne qu'avec --tests-de-mort"),
                 (["--tests-de-mort", "13"] + self.option_etage()[2:], "∉ [0, 12]"),
                 (["--tests-de-mort", "2", "--experimentateur", "exp=claude-opus-5-5", "--lecteur-test", "lec=claude-fable-5-1"],
                  "exige --tranche-exploratoire"),
                 (["--tests-de-mort", "2", "--tranche-exploratoire", "t", "--lecteur-test", "lec=claude-fable-5-1"], "exactement un expérimentateur"),
                 (["--tests-de-mort", "2", "--tranche-exploratoire", "t", "--experimentateur", "a=m", "--experimentateur-externe", "b=n",
                   "--lecteur-test", "lec=claude-fable-5-1"], "exactement un expérimentateur"),
                 (["--tests-de-mort", "2", "--tranche-exploratoire", "t", "--experimentateur", "a=m"], "exige --lecteur-test"),
                 (self.option_etage()[:-2] + ["--moteur", "claude-sdk", "--executeur-tests", "factice"], "factice : démonstration")]
        for k, (options, motif) in enumerate(refus):
            code, out, err = None, "", ""
            err_io = _io.StringIO()
            with _contextlib.redirect_stderr(err_io), self.assertRaises(SystemExit) as ctx:
                lanceur.principal(self.argv(os.path.join(self.tmp, f"l-refus-{k}"), *options))
            self.assertEqual(ctx.exception.code, 2)
            self.assertIn(motif, err_io.getvalue(), options)
            self.assertFalse(os.path.exists(os.path.join(self.tmp, f"l-refus-{k}")))
        # course simulée complète, étage joué par le cœur
        sortie = os.path.join(self.tmp, "l1")
        code, out, err = self.principal(self.argv(sortie, *self.option_etage(2)))
        self.assertEqual(code, 0, err)
        bilan = json.loads(out)
        self.assertEqual(bilan["tests_de_mort"]["statut"], "joué")
        self.assertEqual(sum(bilan["tests_de_mort"]["comptes"].values()) + bilan["tests_de_mort"]["refusees_a_l_etage"], 2)
        self.assertTrue(bilan["tests_de_mort"]["classement_intact"])
        self.assertEqual(bilan["tests_de_mort"]["statut_epistemique"], "exploratoire")
        fin = json.loads(self.lire(os.path.join(sortie, "manifeste-fin.json")))["reglages"]
        self.assertEqual(fin["tests_de_mort_exploratoires"]["statut"], "joué")
        self.assertTrue(fin["journal"]["cout_fictif"])
        self.assertEqual(json.loads(self.lire(os.path.join(sortie, "manifeste-depart.json")))["reglages"]["tests_de_mort"]["experimentateur"],
                         {"etiquette": "exp", "modele": "claude-opus-5-5", "externe": False})
        # sans l'option : ni bilan ni dossier d'étage
        sortie0 = os.path.join(self.tmp, "l0")
        code, out, err = self.principal(self.argv(sortie0))
        self.assertEqual(code, 0, err)
        self.assertNotIn("tests_de_mort", json.loads(out))
        self.assertFalse(os.path.exists(os.path.join(sortie0, "noyau", "tests-de-mort")))
        # --mesurer-consignes avec étage
        code, out, err = self.principal(self.argv(os.path.join(self.tmp, "l-mesure"), "--mesurer-consignes", *self.option_etage(2)))
        self.assertEqual(code, 0, err)
        m = json.loads(out)["consignes"]["tests_de_mort"]
        self.assertEqual(m["nombre"], 2)
        self.assertGreater(m["consigne_experimentateur_maximale"], 60_000)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "l-mesure")))
        # course à juge externe : étage différé ; puis bras + étage
        sortie2 = os.path.join(self.tmp, "l2")
        code, out, err = self.principal(self.argv(sortie2, *self.option_etage(2), juge_externe=True))
        self.assertEqual(code, 0, err)
        self.assertIn("différé", json.loads(out)["tests_de_mort"]["statut"])
        fin2 = json.loads(self.lire(os.path.join(sortie2, "manifeste-fin.json")))["reglages"]
        self.assertTrue(fin2["tests_de_mort_exploratoires"]["statut"].startswith("différé"))
        self.assertFalse(os.path.exists(os.path.join(sortie2, "noyau", "tests-de-mort")))
        att = self.cmd().attester(os.path.join(self.tmp, "att-l2.json"), sortie2, etiquette="argon-j")
        prep = self.prep()
        bras = [sortie2, "--bras-rapporte-differe", "--juge-externe", "argon-j=gemini-argon", "--attestation-lecture-humaine", att,
                "--liste-blanche", prep["liste_blanche"], "--budget-externe-usd", "5", "--horodatage", "2026-10-29T12:30:00Z"]
        code, out, err = self.principal(bras + self.option_etage(2))
        self.assertEqual(code, 0, err)
        b = json.loads(out)
        self.assertEqual(b["tests_de_mort"]["statut"], "joué")
        self.assertTrue(b["tests_de_mort"]["classement_intact"])
        self.assertTrue(idn.verifier_scelle(os.path.join(sortie2, "manifeste-tests-de-mort.json")))
        # le classement du bras est celui qui a été figé
        fige = json.loads(self.lire(os.path.join(sortie2, "noyau", "tests-de-mort", "classement-fige.json")))
        self.assertEqual(fige["classement_sha256"], idn.sha256_fichier(os.path.join(sortie2, "classement.json")))
        self.assertEqual(fige["retenues_dans_l_ordre"], [l["identifiant_auteur"] for l in json.loads(
            self.lire(os.path.join(sortie2, "classement.json")))["lignes"] if l["eligible"]][:2])
        # liste blanche autre que celle de la course : refus au bras, avant tout appel
        sortie3 = os.path.join(self.tmp, "l3")
        code, out, err = self.principal(self.argv(sortie3, *self.option_etage(2), juge_externe=True))
        self.assertEqual(code, 0, err)
        att3 = self.cmd().attester(os.path.join(self.tmp, "att-l3.json"), sortie3, etiquette="argon-j")
        autre = os.path.join(self.tmp, "autre-liste.json")
        idn.construire_liste_blanche([prep["question"], os.path.join(prep["tranche"], "index.json")], autre)
        code, out, err = self.principal([sortie3, "--bras-rapporte-differe", "--juge-externe", "argon-j=gemini-argon",
                                         "--attestation-lecture-humaine", att3, "--liste-blanche", autre, "--budget-externe-usd", "5"]
                                        + self.option_etage(2))
        self.assertEqual(code, 2, err)
        self.assertFalse(os.path.exists(os.path.join(sortie3, "manifeste-tests-de-mort.json")))


    @essai_reel_bwrap  # v51 (CL15-04) : sans bwrap, échec — jamais ignoré en silence
    def test_v48_22_bac_a_sable_reel_si_bwrap_present(self):
        """Seulement si `bwrap` est installé (v49, CL13-08 : l'essai annoncé par la v48, qui ne jouait que `disponible()`). La
        sonde du noyau passe sur le vrai bac à sable (réseau isolé, écriture hors du dossier refusée, **aucune capacité**,
        remontage et écriture dans la tranche refusés) ; les exécuteurs sans isolation sont refusés ; puis **l'étage entier**
        est joué avec le vrai bac sur trois fiches : un script qui lit la tranche et recalcule son chiffre → « survit » ; un
        script qui écrit hors du dossier de travail (cible factice dans le dossier provisoire) → exécution échouée, rien créé,
        « non concluant » ; un script trop long → « tuée (délai) ». Non rejoué dans la machine de la v49 (pas de `bwrap`)."""
        vrai = executeur_reel(self, 5.0)  # v50 : noyau superutilisateur = utilisateur dédié exigé (variables d'environnement)
        ok, motif = vrai.disponible()
        self.assertTrue(ok, motif)
        self.assertIn("aucune capacité", motif)
        for faux in (ExecuteurNonIsole(), ExecuteurReseauSeul()):
            ok, motif = faux.disponible()
            self.assertFalse(ok, faux.nom)
        hote = os.path.join(self.tmp, "hote-factice")
        os.makedirs(hote)
        cible = os.path.join(hote, "ecrit-par-le-script.txt")
        scripts = [script_calcul(3.0),
                   f"open({cible!r}, 'w').write('x')\nprint('RESULTAT: 0.9')\n",
                   "import time\nprint('RESULTAT: 0.9', flush=True)\ntime.sleep(60)\n"]
        vus = []

        def exp(fiche, tour, consigne):
            if tour == 1:
                vus.append(fiche)
                return bloc_exp(executer(scripts[vus.index(fiche)]))
            return bloc_fin()
        ad = self.kit({"opus": [self.fiche("O1"), self.fiche("O2"), self.fiche("O3")]}, exp=exp)
        debut = time.monotonic()
        self.course(ad, "e22", etage=self.etage(nombre=3, executeur=vrai, delai_execution_s=5.0),
                    proposeurs=[("opus", "claude-opus-5-5")], juges=[("juge-opus", "claude-opus-5-5")])
        self.assertLess(time.monotonic() - debut, 90)
        r0, r1, r2 = self.etage_de("e22")["par_fiche"]
        self.assertEqual((r0["verdict"], r0["recalcul_noyau"]["statut"]), ("survit", "concordant"))
        self.assertEqual(r1["executions"][0]["statut"], "échouée (code 1)")
        self.assertEqual(r1["verdict"], "non concluant")
        self.assertFalse(os.path.exists(cible))
        self.assertEqual(r2["executions"][0]["statut"], "tuée (délai)")
        self.assertEqual(r2["verdict"], "non concluant")
        self.assertEqual(os.listdir(hote), [])



# ======================================================================================================================
# v49 : corrections de la contre-lecture CL13 (Opus neuf) — confinement du script de l'expérimentateur (CL13-01 à 04, 12),
# contrôle du modèle servi (CL13-05 à 07), essai réel conditionnel (CL13-08), moissonneur (CL13-09), « survit » vérifiable
# (CL13-11), traçabilité des modules (CL13-10). Toutes les sondes d'évasion se jouent contre des cibles factices dans des
# dossiers temporaires : jamais contre /usr, /etc ou /root réels.
# ======================================================================================================================

import dataclasses as _dataclasses  # noqa: E402
import resource as _resource  # noqa: E402
import stat as _stat  # noqa: E402
import types as _types  # noqa: E402
from unittest import mock as _mock  # noqa: E402

from pole import relais_moisson as rmo  # noqa: E402

# Faux `bwrap` : un programme Python qui joue le rôle de `bwrap` pour l'exécuteur RÉEL (`ExecuteurBacASable`) sans aucun
# confinement — il consigne ses arguments, ses limites et sa session, fait `setsid` si `--new-session` est demandé (comme
# `bwrap` : refusé à un chef de groupe, ce qui prouve que le noyau ne le lance pas en chef de groupe), puis exécute la
# commande placée après `--` dans le dossier lié sur /travail. **Ce n'est pas une barrière.**
FAUX_BWRAP = """#!@PYTHON@
import json, os, resource, sys
args = sys.argv[1:]
sep = args.index("--")
with open(@JOURNAL@, "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": args, "pid": os.getpid(), "sid_avant": os.getsid(0), "environ": sorted(os.environ),
                        "rlimit_nproc": resource.getrlimit(resource.RLIMIT_NPROC), "rlimit_cpu": resource.getrlimit(resource.RLIMIT_CPU),
                        "rlimit_nofile": resource.getrlimit(resource.RLIMIT_NOFILE), "rlimit_as": resource.getrlimit(resource.RLIMIT_AS)}) + "\\n")
if "--new-session" in args:
    os.setsid()
travail = args[args.index("--bind") + 1]
commande = [travail + a[len("/travail"):] if a.startswith("/travail/") else a for a in args[sep + 1:]]
os.chdir(travail)
os.execv(commande[0], commande)
"""

SORTIE_PRIVILEGES_SAINE = ("UID=65534\nCapEff=0000000000000000\nCapPrm=0000000000000000\nCapBnd=0000000000000000\n"
                           "TEMOIN-IDENTITE=cree\n"  # v51 (CL15-01) : l'identité de l'hôte se lit sur le témoin, plus dans uid_map
                           "REMONTAGE /travail/tranche=refus-errno-1\nREMONTAGE /=refus-errno-1\nECRITURE-TRANCHE=refus\n"
                           "PROCSYS kernel/core_pattern=refus-errno-30\nPROCSYS fs/suid_dumpable=refus-errno-30\n"
                           "PROCSYS-OUVRABLES=0\nUSERNS-IMBRIQUE=refus\nSHM=refus-apres-32-Mo-errno-28\n"
                           "PROCESSUS=refus-apres-1000-errno-11\n"
                           # v51 (CL15-02, 06) : /dev en lecture seule, filtre d'appels système, mémoire du bac entier
                           "DEV=refus-errno-30\nSECCOMP=2\nSYSV-SHM=refus-errno-1\nSYSV-MSG=refus-errno-1\nSYSV-SEM=refus-errno-1\n"
                           "MEMFD=refus-errno-1\nIO-URING=refus-errno-1\nPTRACE=refus\nMEMOIRE-BAC=refus-2-enfants-tues\n")


class ExecuteurBacSimule(tdm.ExecuteurFactice):
    """Faux bac « non factice » pour la sonde : isole le réseau et l'écriture par le prélude (comme l'exécuteur factice) et
    **rend une sortie donnée** à la sonde des privilèges (`SONDE_PRIVILEGES` n'est jamais jouée sur la machine : elle tente un
    remontage de montage, ce qu'on ne fait pas hors d'un vrai bac). `effet(travail)` : écrit dans le dossier de la sonde."""
    nom = "bac-simule"
    factice = False

    def __init__(self, sortie_privileges, code=0, effet=None, hote=(True, "témoin non joué : sortie donnée"), **kw):
        super().__init__(**kw)
        self.sortie_privileges, self.code, self.effet, self.joues = sortie_privileges, code, effet, []
        self.hote = hote

    def uid_hote_attendu(self):
        return None  # la sortie rendue est donnée : l'identité de l'hôte de la machine d'essai n'est pas en jeu

    def controler_hote_apres_sonde(self, r, travail):
        return self.hote  # v51 : le témoin d'identité et le groupe de contrôle sont éprouvés pour de vrai dans test_v51_bac_reel.py

    def evaluer_sonde(self, r):  # v51 : la borne mémoire du bac est attendue comme dans le vrai bac (ce faux n'en a pas)
        return tdm.evaluer_sonde_privileges(r["stdout"], r["code"], r["stderr"], userns_permis=self.userns_imbriques_permis)

    def executer(self, script, travail, delai_s=None, dossier_capture=None):
        with open(script, encoding="utf-8") as f:
            corps = f.read()
        if corps == self.sonde_privileges():
            self.joues.append(travail)
            if self.effet:
                self.effet(travail)
            return {"code": self.code, "stdout": self.sortie_privileges, "stderr": "boum" if self.code else "", "delai_depasse": False}
        return super().executer(script, travail, delai_s=delai_s, dossier_capture=dossier_capture)


@_contextlib.contextmanager
def limite_de_temps(secondes):
    """Un essai qui se bloque (tube nommé ouvert, boucle) échoue au bout de `secondes` au lieu de geler la suite."""
    def sur_alarme(signum, cadre):
        raise TimeoutError(f"essai bloqué plus de {secondes} s")
    ancien = _signal.signal(_signal.SIGALRM, sur_alarme)
    _signal.alarm(secondes)
    try:
        yield
    finally:
        _signal.alarm(0)
        _signal.signal(_signal.SIGALRM, ancien)


def script_calcul(valeur, statistique="moyenne", colonne="a", donnee="serie-a.csv"):
    """Un script qui déclare sa statistique (`CALCUL:`) et imprime le chiffre (`RESULTAT:`)."""
    return (f"lignes = open('tranche/{donnee}', encoding='utf-8').read().splitlines()\n"
            f"print('CALCUL: fichier={donnee}; colonne={colonne}; statistique={statistique}')\nprint('RESULTAT: {valeur}')\n")


class TestV49(CasAvecDossier):
    """v49 (corrections de la contre-lecture CL13) : voir les docstrings, un constat par groupe d'essais."""

    def setUp(self):
        super().setUp()
        self.garde = garde_fou_reseau()
        self.garde.__enter__()
        self.addCleanup(self.garde.__exit__, None, None, None)

    @staticmethod
    def octets(chemin, ecrire=None):
        """Lit (ou écrit, si `ecrire`) un fichier en le fermant : aucun descripteur ne reste ouvert."""
        with open(chemin, "rb" if ecrire is None else "wb") as f:
            return f.read() if ecrire is None else f.write(ecrire)

    def h(self):
        """Les aides de `TestV48` (pièces, tranche, faux kit, course, lectures du manifeste), sur le dossier de cet essai."""
        if not hasattr(self, "_h"):
            self._h = TestV48("test_v48_01_cas_sain_complet")
            self._h.tmp = self.tmp
        return self._h

    PROP = [("opus", "claude-opus-5-5")]
    JUGES = [("juge-opus", "claude-opus-5-5")]

    def etage_simple(self, nom, exp, nombre=1, fiches=None, **modifs):
        """Une course à un proposeur et un juge avec l'étage, l'expérimentateur `exp(fiche, tour, consigne)` ; rend (kit, fiches)."""
        h = self.h()
        ad = h.kit({"opus": fiches or [h.fiche("Une")]}, exp=exp)
        h.course(ad, nom, etage=h.etage(nombre=nombre, **modifs), proposeurs=self.PROP, juges=self.JUGES)
        return ad, h.par_fiche(nom)

    @staticmethod
    def liens_tubes_et_prises(racine):
        """Tout ce qui, sous `racine`, n'est ni un dossier ni un fichier régulier (liens, tubes, prises, périphériques), et tout
        fichier setuid ou setgid : la sortie scellée n'en garde aucun (CL14-04, CL14-02)."""
        trouves = []
        for base, dossiers, noms in os.walk(racine, followlinks=False):
            for n in dossiers + noms:
                chemin = os.path.join(base, n)
                mode = os.lstat(chemin).st_mode
                if _stat.S_ISLNK(mode) or not (_stat.S_ISDIR(mode) or _stat.S_ISREG(mode)) or mode & (_stat.S_ISUID | _stat.S_ISGID):
                    trouves.append(os.path.relpath(chemin, racine))
        return sorted(trouves)

    def arbre_des_octets(self, racine):
        """Tous les octets lisibles sous `racine` (sans suivre de lien), pour chercher un secret dans les sorties scellées."""
        morceaux = []
        for base, _, noms in os.walk(racine):
            for n in noms:
                chemin = os.path.join(base, n)
                if os.path.isfile(chemin) and not os.path.islink(chemin):
                    with open(chemin, "rb") as f:
                        morceaux.append(f.read())
        return b"\n".join(morceaux)

    # --- CL13-01 : aucune capacité de superutilisateur dans le bac à sable ------------------------------------------------

    def test_v49_01_commande_sans_privilege_ni_montage_inscriptible_hors_du_dossier_de_travail(self):
        """La commande de `bwrap` : espace d'utilisateurs obligatoire (`--unshare-user`, pas la variante « -try »), identité
        65534 (jamais 0), `--cap-drop ALL`, `--new-session`, `--die-with-parent`, environnement vidé, **un seul montage
        inscriptible** (le dossier de travail de l'exécution), tout le reste en lecture seule ou lien ; aucun `--cap-add`,
        aucun montage de périphérique ou de système en mémoire inscriptible ; la tranche n'est liée que si c'est un vrai
        dossier (jamais un lien)."""
        travail = os.path.join(self.tmp, "t")
        os.makedirs(os.path.join(travail, "tranche"))
        vrai = tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3")
        cmd = vrai.commande(os.path.join(travail, "script.py"), travail)
        valeur = lambda opt: cmd[cmd.index(opt) + 1]  # noqa: E731
        for drapeau in ("--unshare-all", "--unshare-net", "--unshare-user", "--cap-drop", "--new-session", "--die-with-parent",
                        "--clearenv", "--remount-ro"):
            self.assertIn(drapeau, cmd)
        self.assertEqual(valeur("--cap-drop"), "ALL")
        self.assertEqual((valeur("--uid"), valeur("--gid")), ("65534", "65534"))
        self.assertGreater(min(int(valeur("--uid")), int(valeur("--gid"))), 0)
        for interdit in ("--cap-add", "--share-net", "--unshare-user-try", "--dev-bind", "--dev-bind-try", "--bind-try",
                         "--userns", "--userns2", "--perms"):
            self.assertNotIn(interdit, cmd)
        # v50 : le seul `--tmpfs` est le `/dev/shm` borné (CL14-10) ; `/proc/sys` en lecture seule juste après `/proc` (CL14-01) ;
        # pas d'espace d'utilisateurs imbriqué (CL14-03)
        self.assertEqual([cmd[i + 1] for i, x in enumerate(cmd) if x == "--tmpfs"], ["/dev/shm"])
        self.assertEqual(cmd[cmd.index("--tmpfs") - 2:cmd.index("--tmpfs") + 2], ["--size", str(tdm.TAILLE_MAX_DEV_SHM), "--tmpfs", "/dev/shm"])
        self.assertEqual(cmd[cmd.index("--proc") + 1:cmd.index("--proc") + 6], ["/proc", "--ro-bind", "/proc/sys", "/proc/sys", "--dev"])
        self.assertIn("--disable-userns", cmd)
        self.assertLess(cmd.index("--unshare-user"), cmd.index("--disable-userns"))
        self.assertLess(cmd.index("--disable-userns"), cmd.index("--cap-drop"))
        inscriptibles = [(cmd[i], cmd[i + 1], cmd[i + 2]) for i, x in enumerate(cmd) if x in ("--bind", "--bind-try", "--dev-bind")]
        self.assertEqual(inscriptibles, [("--bind", travail, "/travail")])
        sources_lecture_seule = {cmd[i + 1] for i, x in enumerate(cmd) if x in ("--ro-bind", "--ro-bind-try")}
        self.assertLessEqual(sources_lecture_seule, {"/usr", "/lib", "/lib64", "/bin", "/sbin", "/etc/ld.so.cache", "/etc/alternatives",
                                                     "/etc/localtime", "/etc/python3", "/proc/sys", os.path.join(travail, "tranche")})
        self.assertLess(cmd.index("--bind"), len(cmd) - 1 - cmd[::-1].index("--remount-ro"))  # v51 : le dernier, celui de la racine
        self.assertLess(cmd.index("--unshare-user"), cmd.index("--cap-drop"))
        self.assertEqual(cmd[-5:], ["--", "/usr/bin/python3", "-I", "-B", "/travail/script.py"])
        # une tranche qui est un lien n'est jamais liée (lstat, pas isdir)
        autre = os.path.join(self.tmp, "autre-dossier")
        os.makedirs(autre)
        t2 = os.path.join(self.tmp, "t2")
        os.makedirs(t2)
        os.symlink(autre, os.path.join(t2, "tranche"))
        cmd2 = vrai.commande(os.path.join(t2, "script.py"), t2)
        self.assertNotIn("/travail/tranche", cmd2)
        d = vrai.description()
        for mot in ("--unshare-user", "--cap-drop ALL", "--new-session", "--uid 65534", "--disable-userns", "/proc/sys en lecture seule"):
            self.assertIn(mot, d["isolation"])
        self.assertTrue(d["dossier_de_travail"]["neuf_par_execution"])

    def test_v49_02_sonde_des_privileges_cas_sain_et_artefacts(self):
        """La sonde (R5) lit `CapEff`, `CapPrm`, l'identité, le remontage de la tranche et de la racine, l'écriture dans la
        tranche. Cas sain accepté ; **chaque artefact refuse l'exécuteur**, avec son motif : capacités conservées (le défaut de la
        v48), superutilisateur, remontage réussi (tranche, racine), écriture dans la tranche (aussi vue côté noyau), script joué
        hors du bac, sortie ≠ 0, ligne manquante, valeur illisible. Joué avec un faux bac qui rend la sortie : la sonde réelle
        (qui tente un remontage) n'est jamais jouée sur cette machine."""
        ev = tdm.evaluer_sonde_privileges
        self.assertEqual(ev(SORTIE_PRIVILEGES_SAINE), (True, "privilèges nuls"))
        cas = [("CapEff=0000000000000000", "CapEff=000001fffeffffff", "capacités"),
               ("CapPrm=0000000000000000", "CapPrm=000001ffffffffff", "capacités"),
               ("CapEff=0000000000000000", "CapEff=zz", "capacités"),
               ("UID=65534", "UID=0", "superutilisateur"),
               ("REMONTAGE /travail/tranche=refus-errno-1", "REMONTAGE /travail/tranche=REUSSI", "remonté un montage"),
               ("REMONTAGE /=refus-errno-1", "REMONTAGE /=REUSSI", "remonté un montage"),
               ("ECRITURE-TRANCHE=refus", "ECRITURE-TRANCHE=REUSSIE", "écrit dans la tranche"),
               ("ECRITURE-TRANCHE=refus\n", "", "absente"), ("UID=65534\n", "", "absente"),
               ("REMONTAGE /=refus-errno-1\n", "", "absente")]
        for avant, apres, motif in cas:
            sortie = SORTIE_PRIVILEGES_SAINE.replace(avant, apres)
            self.assertNotEqual(sortie, SORTIE_PRIVILEGES_SAINE, avant)
            ok, m = ev(sortie)
            self.assertFalse(ok, avant)
            self.assertIn(motif, m, avant)
        self.assertIn("HORS-BAC", "HORS-BAC\n")
        self.assertFalse(ev("HORS-BAC\n")[0])
        self.assertIn("hors", ev("HORS-BAC\n")[1].lower() + "hors")
        self.assertFalse(ev(SORTIE_PRIVILEGES_SAINE, code=1, erreur="boum")[0])
        self.assertIn("code 1", ev(SORTIE_PRIVILEGES_SAINE, code=1, erreur="boum")[1])
        self.assertFalse(ev("")[0])
        # `disponible()` complète, avec le faux bac
        ok, motif = ExecuteurBacSimule(SORTIE_PRIVILEGES_SAINE, delai_s=30.0).disponible()
        self.assertTrue(ok, motif)
        self.assertIn("aucune capacité", motif)
        for avant, apres, mot in cas[:7]:
            ex = ExecuteurBacSimule(SORTIE_PRIVILEGES_SAINE.replace(avant, apres), delai_s=30.0)
            ok, motif = ex.disponible()
            self.assertFalse(ok, avant)
            self.assertIn("étage refusé", motif)
            self.assertEqual(len(ex.joues), 1)
        ok, motif = ExecuteurBacSimule(SORTIE_PRIVILEGES_SAINE, code=1, delai_s=30.0).disponible()
        self.assertFalse(ok)
        # écriture dans la tranche vue côté noyau, même si la sortie du script la nie
        def ecrit(travail):
            with open(os.path.join(travail, "tranche", "temoin-ecriture.txt"), "w", encoding="utf-8") as f:
                f.write("x")
        ok, motif = ExecuteurBacSimule(SORTIE_PRIVILEGES_SAINE, effet=ecrit, delai_s=30.0).disponible()
        self.assertFalse(ok)
        self.assertIn("tranche montée en lecture seule", motif)
        # l'exécuteur factice (aucune barrière, dit) n'est pas soumis à la sonde des privilèges ; il reste accepté
        ok, motif = tdm.ExecuteurFactice(delai_s=30.0).disponible()
        self.assertTrue(ok, motif)
        self.assertNotIn("capacité", motif)
        # un exécuteur sans isolation est toujours refusé avant la sonde des privilèges (rien n'est tenté sur la machine)
        ok, motif = ExecuteurNonIsole().disponible()
        self.assertFalse(ok)
        self.assertIn("réseau NON isolé", motif)

    # --- CL13-01, CL13-12 : l'exécuteur réel, joué avec un faux `bwrap` (flux du noyau, sans confinement) ----------------------

    def faux_bwrap(self):
        journal = os.path.join(self.tmp, "faux-bwrap.jsonl")
        chemin = os.path.join(self.tmp, "faux-bwrap")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(FAUX_BWRAP.replace("@PYTHON@", sys.executable).replace("@JOURNAL@", repr(journal)))
        os.chmod(chemin, 0o755)
        return chemin, journal

    def travail_neuf(self, nom, script):
        travail = os.path.join(self.tmp, nom)
        tdm.creer_dossier_neuf(travail)
        chemin = os.path.join(travail, "script.py")
        tdm.ecrire_exclusif(chemin, script.encode("utf-8"))
        return travail, chemin

    def test_v49_03_executeur_reel_avec_faux_bwrap_session_limites_et_arret(self):
        """L'exécuteur réel lance `bwrap` **sans** `start_new_session` (sinon `bwrap --new-session` échouerait : le faux
        `bwrap` fait `setsid` et lèverait `PermissionError` pour un chef de groupe) ; il pose les limites (temps processeur =
        délai arrondi + 5 s, descripteurs 512, mémoire, processus) ; le script ne reçoit que l'environnement minimal ;
        au délai, le bac est tué et n'existe plus ; une commande qui ne démarre pas rend une erreur claire. Le faux `bwrap`
        n'est pas une barrière : seule la plomberie du noyau est éprouvée."""
        faux, journal = self.faux_bwrap()
        ex = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, delai_s=3.0, memoire_mo=256, processus_max=300)
        travail, script = self.travail_neuf("t-ok", "import os\nprint('pid', os.getpid(), flush=True)\nprint('CALCUL: fichier=a; colonne=b; statistique=somme')\nprint('RESULTAT: 0.4')\n")
        with _mock.patch.dict(os.environ, {"CANARI_DU_NOYAU": "sk-ant-api03-FACTICE-CANARI"}):
            r = ex.executer(script, travail, delai_s=3.0, dossier_capture=self.tmp)
        self.assertEqual((r["code"], r["delai_depasse"], r["limites_depassees"]), (0, False, []), r["stderr"])
        self.assertEqual(r["lignes_resultat"], ["RESULTAT: 0.4"])
        self.assertEqual(r["lignes_calcul"], ["CALCUL: fichier=a; colonne=b; statistique=somme"])
        with open(journal, encoding="utf-8") as f:
            trace = [json.loads(l) for l in f if l.strip()][0]
        self.assertIn("--new-session", trace["argv"])
        self.assertNotEqual(trace["sid_avant"], trace["pid"])  # pas chef de session à l'entrée : setsid a pu réussir
        self.assertEqual(trace["rlimit_nproc"], [300, 300])
        self.assertEqual(trace["rlimit_cpu"], [8, 8])  # ceil(3) + 5
        self.assertEqual(trace["rlimit_nofile"], [tdm.DESCRIPTEURS_MAX, tdm.DESCRIPTEURS_MAX])
        self.assertEqual(trace["rlimit_as"], [256 << 20, 256 << 20])
        self.assertEqual(sorted(trace["environ"]), sorted(["PATH", "HOME", "LANG", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED"]))
        self.assertNotIn("CANARI", " ".join(trace["environ"]))
        # délai : le bac est tué, le processus n'existe plus
        travail, script = self.travail_neuf("t-long", "import os, time\nprint(os.getpid(), flush=True)\ntime.sleep(60)\n")
        debut = time.monotonic()
        r = ex.executer(script, travail, delai_s=1.0, dossier_capture=self.tmp)
        self.assertLess(time.monotonic() - debut, 15)
        self.assertTrue(r["delai_depasse"])
        pid = int(r["stdout"].split()[0])
        limite = time.monotonic() + 3
        while time.monotonic() < limite:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        # le processus lancé a bien été tué sans signal envoyé à l'orchestrateur lui-même (nous sommes toujours là)
        # l'exécuteur factice garde son groupe de processus (pas de bwrap) et ne limite pas les processus
        self.assertTrue(tdm.ExecuteurFactice.SESSION_PAR_LE_NOYAU and not tdm.ExecuteurFactice.LIMITER_PROCESSUS)
        self.assertFalse(tdm.ExecuteurBacASable.SESSION_PAR_LE_NOYAU)
        for mauvais in (7, 1.5, True):
            with self.assertRaises(ValueError):
                tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, processus_max=mauvais)

    def test_v49_04_ressources_de_l_hote_bornees(self):
        """CL13-12 : nombre d'entrées, place totale et profondeur du dossier de travail bornés — au parcours (cas sain et
        artefacts) **et pendant l'exécution** : un script qui crée des fichiers sans fin est tué avant le délai, l'exécution est
        « échouée (limites de l'hôte dépassées) » et ne compte jamais comme chiffre lu ; limites posées au processus (temps
        processeur, descripteurs, mémoire) lues par le script."""
        # parcours : cas sain, nombre, place, profondeur, noms invalides
        sain = os.path.join(self.tmp, "sain")
        os.makedirs(os.path.join(sain, "a", "b"))
        for chemin, contenu in (("x.txt", b"x"), ("a/y.txt", b"yy"), ("a/b/z.txt", b"zzz")):
            with open(os.path.join(sain, chemin), "wb") as f:
                f.write(contenu)
        inv = tdm.inventaire_travail(sain)
        self.assertEqual(sorted(inv.fichiers), ["a/b/z.txt", "a/y.txt", "x.txt"])
        self.assertEqual(inv.depassements, [])
        self.assertEqual(inv.fichiers["x.txt"], hashlib.sha256(b"x").hexdigest())
        inv = tdm.inventaire_travail(sain, max_entrees=2)
        self.assertTrue(inv.depassements and "entrées" in inv.depassements[0])
        inv = tdm.inventaire_travail(sain, max_octets=2)
        self.assertTrue(inv.depassements and "octets" in inv.depassements[0])
        profond = os.path.join(self.tmp, "profond")
        os.makedirs(os.path.join(profond, *["d"] * (tdm.PROFONDEUR_MAX_TRAVAIL + 2)))
        self.assertTrue(tdm.inventaire_travail(profond).depassements)
        invalide = os.path.join(self.tmp, "invalide")
        os.makedirs(invalide)
        with open(os.path.join(os.fsencode(invalide), b"caf\xe9.txt"), "wb") as f:
            f.write(b"x")
        with open(os.path.join(invalide, "tab\there.txt"), "wb") as f:
            f.write(b"x")
        inv = tdm.inventaire_travail(invalide)
        self.assertEqual(inv.fichiers, {})
        self.assertEqual(sorted(v["type"] for v in inv.non_copies.values()), ["nom invalide (octets ou caractères de contrôle)"] * 2)
        self.assertTrue(all(c.isprintable() and c.isascii() for c in "".join(inv.non_copies)))
        json.dumps(inv.non_copies, ensure_ascii=False).encode("utf-8")  # consignable sans erreur
        # pendant l'exécution (bornes réduites pour l'essai) : tué avant le délai
        sans_fin = "i = 0\nwhile True:\n    open('f%d' % i, 'w').close()\n    i += 1\n"
        with _mock.patch.object(tdm, "MAX_ENTREES_TRAVAIL", 40), _mock.patch.object(tdm, "PERIODE_SURVEILLANCE_S", 0.05):
            debut = time.monotonic()
            _, par = self.etage_simple("e49r1", lambda f, t, c: bloc_exp(executer(sans_fin)) if t == 1 else bloc_fin(),
                                       executeur=tdm.ExecuteurFactice(delai_s=60.0), delai_execution_s=60.0)
            self.assertLess(time.monotonic() - debut, 30)
        r = list(par.values())[0]
        e = r["executions"][0]
        self.assertEqual(e["statut"], "échouée (limites de l'hôte dépassées)")
        self.assertFalse(e["delai_depasse"])
        self.assertTrue(e["limites_depassees"] and "entrées" in e["limites_depassees"][0])
        self.assertEqual((r["verdict"], r["lecture_mecanique"]["verdict"]), ("non concluant", "non concluant"))
        # place totale : trois fichiers de 600 000 octets pour une borne de 1 Mo
        gros = "for k in range(3):\n    open('g%d' % k, 'wb').write(b'x' * 600000)\nprint('RESULTAT: 0.9')\n"
        with _mock.patch.object(tdm, "TAILLE_MAX_TOTALE_TRAVAIL", 1 << 20):
            _, par = self.etage_simple("e49r2", lambda f, t, c: bloc_exp(executer(gros)) if t == 1 else bloc_fin())
        e = list(par.values())[0]["executions"][0]
        self.assertEqual(e["statut"], "échouée (limites de l'hôte dépassées)")
        self.assertIn("octets", e["limites_depassees"][0])
        self.assertEqual(list(par.values())[0]["lecture_mecanique"]["verdict"], "non concluant")  # le RESULTAT imprimé ne compte pas
        # limites posées au processus du script
        limites = ("import resource\nprint('cpu', resource.getrlimit(resource.RLIMIT_CPU)[0])\n"
                   "print('fichiers', resource.getrlimit(resource.RLIMIT_NOFILE)[0])\n"
                   "print('memoire', resource.getrlimit(resource.RLIMIT_AS)[0])\nprint('RESULTAT: 0.5')\n")
        _, par = self.etage_simple("e49r3", lambda f, t, c: bloc_exp(executer(limites)) if t == 1 else bloc_fin(),
                                   executeur=tdm.ExecuteurFactice(delai_s=30.0, memoire_mo=512), delai_execution_s=30.0, memoire_mo=512)
        sortie = self.h().lire(os.path.join(self.tmp, "e49r3", "noyau", "tests-de-mort", list(par)[0], "execution-01", "stdout.txt"))
        self.assertIn("cpu 35", sortie)
        self.assertIn(f"fichiers {tdm.DESCRIPTEURS_MAX}", sortie)
        self.assertIn(f"memoire {512 << 20}", sortie)

    # --- CL13-02 : le noyau n'écrit jamais en suivant un lien -------------------------------------------------------------------

    def test_v49_05_ecriture_exclusive_sans_suivre_de_lien(self):
        """`ecrire_exclusif`, `creer_dossier_neuf` et `ecrire_dans_travail` : cas sain (fichier régulier unique, droits 0600) ;
        artefacts : un lien (vers un fichier existant, vers une cible absente), un fichier, un tube nommé déjà là → refus, **la
        cible du lien n'est ni écrite ni créée** ; un dossier déjà là (même lien vers un dossier) refusé ; un dossier
        intermédiaire qui est un lien refusé, rien écrit dans la cible ; chemin non propre refusé."""
        d = os.path.join(self.tmp, "w")
        os.makedirs(d)
        hote = os.path.join(self.tmp, "hote.txt")
        with open(hote, "w", encoding="utf-8") as f:
            f.write("CONTENU ORIGINAL DE L'HOTE")
        tdm.ecrire_exclusif(os.path.join(d, "sain.txt"), b"abc")
        st = os.lstat(os.path.join(d, "sain.txt"))
        self.assertEqual((_stat.S_ISREG(st.st_mode), st.st_nlink, st.st_size, _stat.S_IMODE(st.st_mode)), (True, 1, 3, 0o600))
        os.symlink(hote, os.path.join(d, "lien-fichier"))
        absente = os.path.join(self.tmp, "n-existe-pas.txt")
        os.symlink(absente, os.path.join(d, "lien-pendant"))
        with open(os.path.join(d, "existant"), "w", encoding="utf-8") as f:
            f.write("a")
        os.mkfifo(os.path.join(d, "tuyau"))
        with limite_de_temps(20):
            for nom in ("lien-fichier", "lien-pendant", "existant", "tuyau"):
                with self.assertRaises(tdm.EtageInterrompu, msg=nom):
                    tdm.ecrire_exclusif(os.path.join(d, nom), b"ECRASE")
        self.assertEqual(self.h().lire(hote), "CONTENU ORIGINAL DE L'HOTE")
        self.assertFalse(os.path.exists(absente))
        self.assertEqual(self.h().lire(os.path.join(d, "existant")), "a")
        # dossier neuf
        tdm.creer_dossier_neuf(os.path.join(d, "neuf"))
        self.assertTrue(os.path.isdir(os.path.join(d, "neuf")))
        cible_dossier = os.path.join(self.tmp, "cible-dossier")
        os.makedirs(cible_dossier)
        os.symlink(cible_dossier, os.path.join(d, "lien-dossier"))
        for nom in ("neuf", "lien-dossier", "sain.txt"):
            with self.assertRaises(tdm.EtageInterrompu, msg=nom):
                tdm.creer_dossier_neuf(os.path.join(d, nom))
        # dossier intermédiaire qui est un lien
        os.symlink(cible_dossier, os.path.join(d, "tranche"))
        with self.assertRaises(tdm.EtageInterrompu):
            tdm.ecrire_dans_travail(d, "tranche/serie.csv", b"x,y\n")
        self.assertEqual(os.listdir(cible_dossier), [])
        tdm.ecrire_dans_travail(d, "sous/dossier/serie.csv", b"x,y\n")
        self.assertEqual(self.h().lire(os.path.join(d, "sous", "dossier", "serie.csv")), "x,y\n")
        for mauvais in ("../x", "/etc/x", "a//b", "./a", "~x"):
            with self.assertRaises(tdm.EtageInterrompu, msg=mauvais):
                tdm.ecrire_dans_travail(d, mauvais, b"x")

    def test_v49_06_lien_pose_sur_script_ou_sur_l_execution_suivante_n_ecrase_rien(self):
        """L'attaque de CL13-02 jouée contre une cible factice : l'exécution 1 remplace `script.py` par un lien vers un fichier
        de l'hôte (factice, dans le dossier provisoire) ; la v48 aurait écrit le script de l'exécution 2 **à travers le lien**.
        Ici chaque exécution a son dossier de travail neuf : le fichier de l'hôte est intact, l'exécution 2 s'exécute, le lien est
        consigné (« non copié : lien »). Seconde attaque : un lien posé à la place du dossier de l'exécution suivante
        (`../../execution-02`) fait **arrêter l'étage** sans rien écrire dans sa cible (manifestes écrits)."""
        hote = os.path.join(self.tmp, "hote.txt")
        with open(hote, "w", encoding="utf-8") as f:
            f.write("CONTENU ORIGINAL DE L'HOTE")
        s1 = f"import os\nos.remove('script.py')\nos.symlink({hote!r}, 'script.py')\nprint('RESULTAT: 0.4')\n"
        tours = {1: bloc_exp(executer(s1)), 2: bloc_exp(executer(script_resultat(0.5))), 3: bloc_fin()}
        _, par = self.etage_simple("e49l1", lambda f, t, c: tours[t])
        self.assertEqual(self.h().lire(hote), "CONTENU ORIGINAL DE L'HOTE")
        r = list(par.values())[0]
        e1, e2 = r["executions"]
        self.assertEqual((e1["statut"], e2["statut"]), ("réussie", "réussie"))
        self.assertEqual([(x["chemin"], x["type"], x["motif"].split(" vers ")[0]) for x in e1["entrees_non_copiees"]],
                         [("script.py", "lien", "non copié : lien")])
        self.assertEqual(r["lecture_mecanique"]["chiffre"], 0.5)
        base = os.path.join(self.tmp, "e49l1", "noyau", "tests-de-mort", list(par)[0])
        # v50 (CL14-04) : plus de dossier de travail dans la sortie scellée ; le script de chaque exécution reste scellé à côté
        self.assertFalse(os.path.exists(os.path.join(base, "execution-02", "travail")))
        self.assertEqual(self.h().lire(os.path.join(base, "execution-02", "script.py")), script_resultat(0.5))
        # seconde attaque : le dossier de l'exécution suivante est un lien posé par le script
        cible = os.path.join(self.tmp, "cible-dossier")
        os.makedirs(cible)
        # v50 : les dossiers de travail sont frères sous la racine de l'étage (hors de la sortie) ; le script qui les atteint (exécuteur
        # factice : aucune barrière) pose un lien à la place de celui de l'exécution suivante
        s2 = (f"import os\nfor n in os.listdir('..'):\n    if n.endswith('-execution-01'):\n"
              f"        os.symlink({cible!r}, '../' + n[:-len('-execution-01')] + '-execution-02')\nprint('RESULTAT: 0.4')\n")
        tours2 = {1: bloc_exp(executer(s2)), 2: bloc_exp(executer(script_resultat(0.5))), 3: bloc_fin()}
        h = self.h()
        ad = h.kit({"opus": [h.fiche("Lien2")]}, exp=lambda f, t, c: tours2[t])
        with self.assertRaisesRegex(idn.CourseInterrompue, "déjà présent"):
            h.course(ad, "e49l2", etage=h.etage(nombre=1), proposeurs=self.PROP, juges=self.JUGES)
        self.assertEqual(os.listdir(cible), [])
        self.assertTrue(idn.verifier_scelle(os.path.join(self.tmp, "e49l2", "manifeste-tests-de-mort.json")))
        self.assertIn("déjà présent", h.etage_de("e49l2")["arret"])

    # --- CL13-03, CL13-04 : produits lus par lstat, fichiers réguliers seulement ---------------------------------------------

    def test_v49_07_produits_liens_tubes_prises_peripheriques_jamais_ouverts_ni_copies(self):
        """L'attaque de CL13-03 (un lien vers `/proc/self/environ` et un lien vers un fichier secret de l'hôte factice) et celle
        de CL13-04 (un tube nommé) : l'étage **ne se bloque pas**, ne copie ni l'environnement du noyau (une clé factice est
        posée dans l'environnement de l'essai) ni le fichier secret ; liens, tube, prise et périphérique sont consignés avec leur
        genre ; un fichier régulier est copié et scellé ; un lien vers un dossier n'est pas parcouru ; le secret n'apparaît dans
        aucun octet de la sortie scellée."""
        secret = os.path.join(self.tmp, "secret-hote.txt")
        with open(secret, "w", encoding="utf-8") as f:
            f.write("SECRET-FACTICE-DE-L-HOTE")
        dossier_hote = os.path.join(self.tmp, "dossier-hote")
        os.makedirs(dossier_hote)
        with open(os.path.join(dossier_hote, "dedans.txt"), "w", encoding="utf-8") as f:
            f.write("SECRET-DANS-UN-DOSSIER-LIE")
        script = ("import os, socket, stat\n"
                  "os.symlink('/proc/self/environ', 'environ.txt')\n"
                  f"os.symlink({secret!r}, 'secret.txt')\n"
                  f"os.symlink({dossier_hote!r}, 'dossier-lie')\n"
                  "os.mkfifo('tuyau')\n"
                  "s = socket.socket(socket.AF_UNIX); s.bind('prise.sock'); s.close()\n"
                  "try:\n    os.mknod('peripherique', stat.S_IFCHR | 0o600, os.makedev(1, 3))\nexcept OSError:\n    pass\n"
                  "open('regulier.txt', 'w').write('produit sain')\nprint('RESULTAT: 0.4')\n")
        with _mock.patch.dict(os.environ, {"CLE_FACTICE_DU_NOYAU": "sk-ant-api03-FACTICE-CANARI-DU-NOYAU"}), limite_de_temps(90):
            _, par = self.etage_simple("e49p", lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin())
        r = list(par.values())[0]
        e = r["executions"][0]
        self.assertEqual(e["statut"], "réussie")
        self.assertEqual([p["chemin"] for p in e["fichiers_produits"]], ["regulier.txt"])
        genres = {x["chemin"]: x["type"] for x in e["entrees_non_copiees"]}
        self.assertEqual({k: genres[k] for k in ("environ.txt", "secret.txt", "dossier-lie", "tuyau", "prise.sock")},
                         {"environ.txt": "lien", "secret.txt": "lien", "dossier-lie": "lien", "tuyau": "tube nommé", "prise.sock": "prise"})
        if "peripherique" in genres:  # `mknod` n'est permis qu'au superutilisateur
            self.assertEqual(genres["peripherique"], "périphérique caractère")
        self.assertEqual(sorted(genres), sorted(set(genres) & {"environ.txt", "secret.txt", "dossier-lie", "tuyau", "prise.sock", "peripherique"}))
        d = os.path.join(self.tmp, "e49p", "noyau", "tests-de-mort", list(par)[0], "execution-01")
        self.assertEqual(sorted(os.listdir(os.path.join(d, "produits"))), ["regulier.txt.copie", "regulier.txt.copie.sha256"])  # v50 (CL14-05)
        self.assertEqual(self.liens_tubes_et_prises(os.path.join(self.tmp, "e49p")), [])  # v50 (CL14-04)
        tout = self.arbre_des_octets(os.path.join(self.tmp, "e49p"))
        for interdit in (b"SECRET-FACTICE-DE-L-HOTE", b"SECRET-DANS-UN-DOSSIER-LIE", b"FACTICE-CANARI-DU-NOYAU", b"CLE_FACTICE_DU_NOYAU"):
            self.assertNotIn(interdit, tout, interdit)
        # ce que l'expérimentateur et le lecteur voient : noms et genres seulement
        self.assertEqual(r["verdict"], "survit")
        # unités : `ouvrir_regulier` ne suit aucun lien et n'ouvre jamais un tube
        w = os.path.join(self.tmp, "w2")
        os.makedirs(os.path.join(w, "vrai"))
        with open(os.path.join(w, "vrai", "f.txt"), "wb") as f:
            f.write(b"ok")
        os.symlink(os.path.join(w, "vrai"), os.path.join(w, "lien-dossier"))
        os.symlink(os.path.join(w, "vrai", "f.txt"), os.path.join(w, "lien-fichier"))
        os.mkfifo(os.path.join(w, "tuyau"))
        with limite_de_temps(20):
            self.assertEqual(tdm.lire_regulier(w, "vrai/f.txt"), b"ok")
            for relatif in ("lien-dossier/f.txt", "lien-fichier", "tuyau", "absent", "vrai", "vrai/f.txt/x"):
                self.assertIsNone(tdm.ouvrir_regulier(w, relatif), relatif)
                self.assertEqual(tdm.sha256_regulier(w, relatif)[0], None, relatif)
            self.assertIsNone(tdm.lire_regulier(w, "vrai/f.txt", maximum=1))
        self.assertEqual(tdm.sha256_regulier(w, "vrai/f.txt"), (hashlib.sha256(b"ok").hexdigest(), 2))

    def test_v49_08_nom_de_produit_invalide_et_trop_long_ne_fait_rien_planter(self):
        """Un produit dont le nom n'est pas de l'UTF-8 valide, contient un caractère de contrôle ou dépasse
        `TAILLE_MAX_NOM_COPIE` ne fait ni planter l'étage ni écrire un manifeste illisible : il est consigné, non copié ; un
        long nom de fichier régulier est haché mais pas copié."""
        long_nom = "n" * (tdm.TAILLE_MAX_NOM_COPIE + 1) + ".txt"
        script = ("import os\nos.close(os.open(b'caf\\xe9.txt', os.O_CREAT | os.O_WRONLY))\n"
                  "open('a\\tb.txt', 'w').write('x')\n"
                  f"open({long_nom!r}, 'w').write('long')\nopen('normal.txt', 'w').write('ok')\nprint('RESULTAT: 0.4')\n")
        _, par = self.etage_simple("e49n", lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin())
        r = list(par.values())[0]
        e = r["executions"][0]
        self.assertEqual(e["statut"], "réussie")
        self.assertEqual(sorted(p["chemin"] for p in e["fichiers_produits"]), sorted([long_nom, "normal.txt"]))
        copies = {p["chemin"]: p["copie_scellee"] for p in e["fichiers_produits"]}
        self.assertEqual(copies, {long_nom: False, "normal.txt": True})
        self.assertEqual(len([x for x in e["entrees_non_copiees"] if "nom invalide" in x["type"]]), 2)
        self.assertTrue(idn.verifier_scelle(os.path.join(self.tmp, "e49n", "manifeste-tests-de-mort.json")))


    # --- CL13-05 : R-764 pour Argon (commande externe) et défense générique du noyau ----------------------------------------------

    SCRIPT_ARGON = ("import json, os, sys\nsys.stdin.read()\n"
                    "objet = {'texte': os.environ.get('MODELE_DEMANDE_POLE', 'ABSENT'), 'cout_usd': 0.2}\n"
                    "objet.update(%s)\nprint(json.dumps(objet))\n")

    def commande_argon(self, extra, nom="argon.py"):
        chemin = os.path.join(self.tmp, nom)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(self.SCRIPT_ARGON % repr(extra))
        return [sys.executable, "-I", chemin]

    def test_v49_09_commande_externe_modele_servi_exige_ou_facultatif(self):
        """Argon (commande externe) : avec `exiger_modele_servi`, la commande rend `modele_servi` égal au modèle demandé (ou suivi
        d'un suffixe de date) ; sinon statut « refus » (jamais le texte servi), dépense comptée à part pour un modèle autre ou
        absent ; un refus dit par la commande (`refus`, `stop_reason`) est un refus sans dépense « non autorisée » ; modèle
        demandé inconnu = refus ; non exigé, la barrière n'agit que si la commande rend `modele_servi` (dit au manifeste) ;
        la commande reçoit `MODELE_DEMANDE_POLE`."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        modele = "argon-x"

        def jouer(extra, exiger=True, demande=modele):
            ad = AdaptateurCommandeExterne(self.commande_argon(extra), environnement={}, exiger_modele_servi=exiger)
            return ad.lancer("proposeur_ideation", "consigne", self.tmp, 1.0, 1, modele=demande)
        # cas sains : exact et suffixe de date ; la commande a reçu le modèle demandé
        for servi in (modele, modele + "-20261001"):
            r = jouer({"modele_servi": servi})
            self.assertEqual((r.statut, r.texte_final, r.refus, r.cout_declare_usd), ("ok", modele, None, 0.2), servi)
        # artefacts, exigé
        cas = [({"modele_servi": "argon-y"}, "commande.modele_servi", 0.2),
               ({"modele_servi": "argon-xy"}, "commande.modele_servi", 0.2),  # préfixe sans tiret : autre modèle
               ({}, "commande.modele_servi_absent", 0.2),
               ({"modele_servi": ""}, "commande.modele_servi_absent", 0.2),
               ({"modele_servi": 7}, "commande.modele_servi_absent", 0.2),
               ({"modele_servi": modele, "refus": True}, "commande.refus", 0.0),
               ({"modele_servi": modele, "stop_reason": "refusal"}, "commande.refus", 0.0)]
        for extra, evenement, non_autorise in cas:
            r = jouer(extra)
            self.assertEqual(r.statut, "refus", extra)
            self.assertEqual(r.texte_final, "", extra)  # le texte d'un refus ou d'un autre modèle n'est jamais servi
            self.assertEqual(r.refus["evenement"], evenement, extra)
            self.assertIn("R-764", r.erreur)
            self.assertEqual((r.cout_declare_usd, r.depense_modele_non_autorise_usd), (0.2, non_autorise), extra)
            self.assertEqual(r.refus["modele_demande"], modele)
        self.assertEqual(jouer({"modele_servi": "argon-y"}).modele_servi, "argon-y")
        r = jouer({"modele_servi": modele}, demande=None)
        self.assertEqual((r.statut, r.refus["evenement"]), ("refus", "commande.modele_demande_inconnu"))
        # non exigé : la barrière n'agit que si la commande rend `modele_servi`
        self.assertEqual(jouer({}, exiger=False).statut, "ok")
        self.assertEqual(jouer({"modele_servi": modele}, exiger=False).statut, "ok")
        self.assertEqual(jouer({"modele_servi": "argon-y"}, exiger=False).statut, "refus")
        self.assertEqual(jouer({"refus": True}, exiger=False).statut, "refus")
        # description : la barrière absente est dite
        d = AdaptateurCommandeExterne(self.commande_argon({}), environnement={}).description()["controle_modele_servi"]
        self.assertIn("ABSENTE", d)
        d = AdaptateurCommandeExterne(self.commande_argon({}), environnement={}, exiger_modele_servi=True).description()["controle_modele_servi"]
        self.assertIn("exigé", d)
        env = AdaptateurCommandeExterne(self.commande_argon({}), environnement={}).environnement_commande(1.0, "juge_ideation", "argon-x")
        self.assertEqual((env["MODELE_DEMANDE_POLE"], env["ROLE_POLE"]), ("argon-x", "juge_ideation"))
        self.assertNotIn("MODELE_DEMANDE_POLE", AdaptateurCommandeExterne(self.commande_argon({}), environnement={}).environnement_commande(1.0, "x"))
        # le lanceur n'exige `modele_servi` qu'avec le moteur réel
        lanceur = self.h().lanceur()
        for moteur, attendu in (("claude-sdk", True), ("simule", False)):
            args = _types.SimpleNamespace(commande_externe=f"{sys.executable} -I x.py", delai_commande_s=5.0, variable_transmise=[], moteur=moteur)
            self.assertIs(lanceur.adaptateur_commande_externe(args).exiger_modele_servi, attendu, moteur)

    def test_v49_10_defense_generique_du_noyau_sur_le_modele_servi(self):
        """`controle_modele_resultat` : tout adaptateur qui dit son modèle servi est contrôlé par le noyau (identifiant exact ou
        suffixe de date) ; dans la course (proposeur externe) et dans l'étage (expérimentateur externe), un écart arrête
        la course (« refus (R-764) », jamais « budget »), met la sortie à l'écart, compte la session à part, écrit les
        manifestes ; un modèle conforme (suffixe de date) passe."""
        from pole.adaptateurs import controle_modele_resultat
        base = Resultat("x", [], 0.3, "ok")
        self.assertIsNone(controle_modele_resultat("m", base))
        for servi in ("m", "m-20261001"):
            self.assertIsNone(controle_modele_resultat("m", _dataclasses.replace(base, modele_servi=servi)))
        for servi in ("autre", "m2", "mm-20261001"):
            refus = controle_modele_resultat("m", _dataclasses.replace(base, modele_servi=servi))
            self.assertEqual((refus["modele_demande"], refus["modele_servi"], refus["evenement"]), ("m", servi, "resultat.modele_servi"))
        self.assertIsNone(controle_modele_resultat("m", _dataclasses.replace(base, modele_servi="")))
        self.assertIsNone(controle_modele_resultat(None, _dataclasses.replace(base, modele_servi="autre")))
        # dans la course : proposeur externe qui change de modèle
        h = self.h()
        c = h.cours()
        c._prep = {k: v for k, v in h.prep().items() if k != "tranche"}

        class ExterneDeviant(FauxAdaptateur):
            servi = "gemini-autre"

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)
                if role == "proposeur_ideation":
                    return _dataclasses.replace(r, modele_servi=self.servi)
                return r
        fiches = {"opus": [fiche_brute(nom="O1")], "fable": [fiche_brute(nom="F1")]}
        ad = FauxAdaptateur(fiches, notes_par_juge={"juge-fable": c.notes_temoins_ok, "juge-opus": c.notes_temoins_ok})
        budgets = dict(c.budgets())
        budgets[("proposeur_ideation", "gemini-argon")] = 1.0
        ext = ExterneDeviant({"argon": [fiche_brute(nom="A1")]})
        with self.assertRaisesRegex(idn.CourseInterrompue, "refus \\(R-764\\)") as ctx:
            c.lancer(ad, "g49c", budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", ext)], budget_externe_usd=3.0)
        self.assertNotIn("budget", str(ctx.exception).lower())
        fin = json.loads(self.h().lire(os.path.join(self.tmp, "g49c", "manifeste-fin.json")))["reglages"]
        self.assertEqual(fin["statut_course"], {"statut": "refus", "role": "proposeur_ideation", "etiquette": "argon",
                                                "modele_demande": "gemini-argon", "modele_servi": "gemini-autre"})
        self.assertEqual(fin["depense_modele_non_autorise_usd"], 0.5)
        self.assertTrue(os.path.isdir(os.path.join(self.tmp, "g49c", "A-L-ECART-modele-non-autorise", "proposeurs", "argon")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "g49c", "proposeurs", "argon", "passe-1")))
        # un modèle servi conforme (suffixe de date) passe
        ExterneDeviant.servi = "gemini-argon-20261001"
        res = c.lancer(ad, "g49d", budgets=budgets, proposeurs_externes=[("argon", "gemini-argon", ext)], budget_externe_usd=3.0)
        self.assertEqual({f["auteur"] for f in res["fiches"]}, {"opus", "fable", "argon"})
        # dans l'étage : expérimentateur externe qui change de modèle

        class ExperimentateurDeviant(FauxKitEtage):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, **lecture):
                r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)
                return _dataclasses.replace(r, modele_servi="gemini-autre") if role == "experimentateur_test" else r
        externe = ExperimentateurDeviant({"opus": [h.fiche("O1")], "fable": [h.fiche("F1")]}, cout_exp=0.07)
        ad2 = h.kit({"opus": [h.fiche("O1")], "fable": [h.fiche("F1")]})
        with self.assertRaisesRegex(idn.CourseInterrompue, "refus \\(R-764\\)"):
            h.course(ad2, "g49e", budget_externe_usd=2.0,
                     etage=h.etage(nombre=1, experimentateur=None, experimentateur_externe=("argon", "autre-lignee-x", externe)))
        fin = h.fin("g49e")
        self.assertEqual((fin["statut_course"]["statut"], fin["statut_course"]["role"], fin["statut_course"]["modele_servi"]),
                         ("refus", "experimentateur_test", "gemini-autre"))
        self.assertEqual(fin["depense_modele_non_autorise_usd"], 0.07)
        self.assertIn("refus (R-764)", h.etage_de("g49e")["arret"])
        self.assertTrue(idn.verifier_scelle(os.path.join(self.tmp, "g49e", "manifeste-tests-de-mort.json")))
        self.assertFalse([a for a in ad2.appels if a["role"] == "lecteur_test"])  # le lecteur n'est jamais joué

    # --- CL13-06 : message de résultat du kit (stop_reason, model_usage) ----------------------------------------------------------

    def test_v49_11_message_de_resultat_du_kit_stop_reason_et_modeles_factures(self):
        """Défense en profondeur sur le `ResultMessage` : `stop_reason == "refusal"` → refus (événement `result.stop_reason`) ;
        un modèle facturé (coût ou jetons non nuls) autre que le modèle demandé dans `model_usage` → refus
        (`result.model_usage`), dépense comptée ; le modèle demandé (suffixe de date admis), une entrée à zéro, un
        `model_usage` absent ou vide → pas de refus ; une entrée illisible compte comme ayant servi (prudence). Les noms de
        champs lus existent dans le kit réel installé (s'il l'est)."""
        from essais.faux_sdk import claude_agent_sdk as faux_sdk
        K = FauxKitRefus
        opts = faux_sdk.ClaudeAgentOptions(model="claude-opus-5-5")

        def jouer(*messages):
            kit = K([K.AssistantMessage([K.TextBlock("réponse")], "claude-opus-5-5")] + list(messages))
            return kit, asyncio.run(AdaptateurClaudeSDK._executer(kit, "consigne", opts, 5))
        _, (texte, cout, statut, erreur, lecture) = jouer(K.ResultMessage("success", "réponse", 0.3, model_usage={
            "claude-opus-5-5-20261001": {"costUSD": 0.3, "inputTokens": 10, "outputTokens": 5},
            "claude-fable-5-1": {"costUSD": 0.0, "inputTokens": 0, "outputTokens": 0}}))
        self.assertEqual((statut, lecture["refus"], texte), ("ok", None, "réponse"))
        for sans in (None, {}):
            _, (texte, cout, statut, erreur, lecture) = jouer(K.ResultMessage("success", "réponse", 0.3, model_usage=sans))
            self.assertEqual((statut, lecture["refus"]), ("ok", None))
        # stop_reason au message de résultat
        _, (texte, cout, statut, erreur, lecture) = jouer(K.ResultMessage("success", "suite", 0.3, stop_reason="refusal"))
        self.assertEqual((statut, lecture["refus"]["evenement"], texte, lecture["cout_inconnu"]), ("refus", "result.stop_reason", "", True))
        self.assertIn("refusal", erreur)
        _, (_, _, statut, _, lecture) = jouer(K.ResultMessage("success", "suite", 0.3, stop_reason="end_turn"))
        self.assertEqual((statut, lecture["refus"]), ("ok", None))
        # un autre modèle facturé
        usage = {"claude-opus-5-5": {"costUSD": 0.1, "inputTokens": 5, "outputTokens": 5},
                 "claude-opus-4-8": {"costUSD": 0.25, "inputTokens": 1000, "outputTokens": 200}}
        _, (texte, cout, statut, erreur, lecture) = jouer(K.ResultMessage("success", "suite", 0.35, model_usage=usage))
        self.assertEqual((statut, lecture["refus"]["evenement"], lecture["refus"]["modele_servi"], texte), ("refus", "result.model_usage", "claude-opus-4-8", ""))
        self.assertAlmostEqual(lecture["depense_modele_non_autorise_usd"], 0.25)
        self.assertIn("claude-opus-4-8", erreur)
        # jetons sans coût, et entrée illisible : comptent comme ayant servi
        for autre in ({"claude-opus-4-8": {"costUSD": 0.0, "inputTokens": 3}}, {"claude-opus-4-8": "illisible"}, {"claude-opus-4-8": None}):
            _, (_, _, statut, _, lecture) = jouer(K.ResultMessage("success", "suite", 0.3, model_usage=autre))
            self.assertEqual((statut, lecture["refus"]["evenement"]), ("refus", "result.model_usage"), autre)
        # les unités
        self.assertFalse(AdaptateurClaudeSDK._a_servi({"costUSD": 0, "inputTokens": 0, "outputTokens": 0}))
        self.assertTrue(AdaptateurClaudeSDK._a_servi({"cacheReadInputTokens": 4}))
        self.assertTrue(AdaptateurClaudeSDK._a_servi({"costUSD": "x"}))
        # champs du kit réel (si installé) : ceux que le noyau lit
        try:
            import claude_agent_sdk as reel
        except ImportError:
            return
        champs = {f.name for f in _dataclasses.fields(reel.ResultMessage)}
        self.assertLessEqual({"stop_reason", "model_usage", "total_cost_usd", "subtype", "result", "is_error"}, champs)
        self.assertIn("model", {f.name for f in _dataclasses.fields(reel.AssistantMessage)})

    # --- CL13-07 : les modèles de l'étage dans la liste exigée du relais -----------------------------------------------------------

    def test_v49_12_modeles_exiges_du_relais_avec_l_etage(self):
        """`modeles_du_relais` : sans étage, proposeurs et juges ; avec l'étage, aussi l'expérimentateur Claude et le lecteur ;
        l'expérimentateur externe (Argon, non servi par le relais) n'y est pas. `verifier_relais` : la liste du relais doit être
        exactement cet ensemble — l'ensemble de la v48 (sans le lecteur Fable) est refusé, un modèle en plus est refusé."""
        lanceur = self.h().lanceur()
        proposeurs = [("opus", "claude-opus-5-5")]
        juges = [("juge-opus", "claude-opus-5-5")]
        base = dict(tests_de_mort=0, experimentateur=None, experimentateur_externe=None, lecteur_test=None)
        sans = lanceur.modeles_du_relais(_types.SimpleNamespace(**base), proposeurs, juges)
        self.assertEqual(sorted(set(sans)), ["claude-opus-5-5"])
        etage = dict(base, tests_de_mort=2, experimentateur="exp=claude-opus-5-5", lecteur_test="lec=claude-fable-5-1")
        avec = lanceur.modeles_du_relais(_types.SimpleNamespace(**etage), proposeurs, juges)
        self.assertEqual(sorted(set(avec)), ["claude-fable-5-1", "claude-opus-5-5"])
        argon = dict(etage, experimentateur=None, experimentateur_externe="argon=gemini-argon")
        self.assertEqual(sorted(set(lanceur.modeles_du_relais(_types.SimpleNamespace(**argon), proposeurs, juges))),
                         ["claude-fable-5-1", "claude-opus-5-5"])
        # sans modèle unique pour l'expérimentateur : forme « modèle » seul admise
        nu = dict(etage, experimentateur="claude-fable-5-1", lecteur_test="claude-opus-5-5")
        self.assertEqual(sorted(set(lanceur.modeles_du_relais(_types.SimpleNamespace(**nu), proposeurs, juges))),
                         ["claude-fable-5-1", "claude-opus-5-5"])
        # le contrôle du relais
        budgets = {("juge_ideation", "claude-opus-5-5"): 4.0}
        etat = {"plafond_usd": 40, "reserve_par_appel_usd": 4, "depense_usd": 0.0, "modeles_permis": ["claude-opus-5-5", "claude-fable-5-1"]}
        lu = lanceur.verifier_relais(etat, 40.0, budgets, juges, modeles_attendus=avec)
        self.assertEqual(lu["modeles_permis"], ["claude-opus-5-5", "claude-fable-5-1"])
        with self.assertRaisesRegex(idn.CourseInterrompue, "R-764"):  # la liste de la v48 : proposeurs et juges seulement
            lanceur.verifier_relais(etat, 40.0, budgets, juges, modeles_attendus=sans)
        with self.assertRaisesRegex(idn.CourseInterrompue, "R-764"):
            lanceur.verifier_relais(dict(etat, modeles_permis=["claude-opus-5-5"]), 40.0, budgets, juges, modeles_attendus=avec)
        with self.assertRaisesRegex(idn.CourseInterrompue, "tests-de-mort"):
            lanceur.verifier_relais(dict(etat, modeles_permis=["claude-opus-5-5"]), 40.0, budgets, juges, modeles_attendus=avec)

    # --- CL13-09 : compteur journalier persistant, amont arXiv en https --------------------------------------------------------------------------------

    def test_v49_13_compteur_journalier_persistant_cas_sain_et_artefacts(self):
        """Le compteur du jour est un fichier scellé (`compteur-AAAA-MM-JJ.json` + `.sha256`, format de sha256sum) relu au
        redémarrage : appels et refus conservés, plafond tenu après relance. Artefacts (aucun repli) : contenu modifié sans le
        sceau, sceau faux, sceau absent, JSON illisible, valeur négative, booléenne ou fractionnaire, source en trop,
        mauvais jour → `CompteurInvalide`. Changement de jour (UTC) : compteur à zéro, nouveau fichier, l'ancien intact.
        Sans dossier : en mémoire, dit par `etat()`."""
        d = os.path.join(self.tmp, "compteurs")
        with _mock.patch.object(rmo.CompteurJournalier, "_maintenant_jour", staticmethod(lambda: "2026-10-30")):
            c = rmo.CompteurJournalier(2, d)
            self.assertTrue(c.reserver("arxiv") and c.reserver("arxiv"))
            self.assertFalse(c.reserver("arxiv"))
            self.assertTrue(c.reserver("openalex"))
            chemin = os.path.join(d, "compteur-2026-10-30.json")
            octets = self.octets(chemin)
            self.assertEqual(self.octets(chemin + ".sha256").decode("utf-8"),
                             f"{hashlib.sha256(octets).hexdigest()}  compteur-2026-10-30.json\n")
            self.assertEqual(sorted(os.listdir(d)), ["compteur-2026-10-30.json", "compteur-2026-10-30.json.sha256"])  # pas de provisoire
            # relance le même jour : le compteur est relu
            c2 = rmo.CompteurJournalier(2, d)
            etat = c2.etat()
            self.assertEqual((etat["appels"]["arxiv"], etat["refus"]["arxiv"], etat["appels"]["openalex"], etat["persistant"]), (2, 1, 1, True))
            self.assertFalse(c2.reserver("arxiv"))
            self.assertTrue(c2.reserver("openalex"))
            self.assertEqual(rmo.CompteurJournalier(2, d).etat()["appels"]["openalex"], 2)
            # artefacts
            sain = self.octets(chemin)

            def sceller(contenu):
                with open(chemin, "wb") as f:
                    f.write(contenu)
                with open(chemin + ".sha256", "w", encoding="utf-8") as f:
                    f.write(f"{hashlib.sha256(contenu).hexdigest()}  compteur-2026-10-30.json\n")
            sceller(sain)
            rmo.CompteurJournalier(2, d)  # le sceau refait est accepté
            avec_sceau_faux = [("contenu modifié, sceau inchangé", lambda: self.octets(chemin, sain.replace(b'"arxiv": 2', b'"arxiv": 0', 1))),
                               ("sceau faux", lambda: self.octets(chemin + ".sha256", ("0" * 64 + "  compteur-2026-10-30.json\n").encode())),
                               ("sceau absent", lambda: os.remove(chemin + ".sha256")),
                               ("sceau vide", lambda: self.octets(chemin + ".sha256", b""))]
            for nom, abimer in avec_sceau_faux:
                sceller(sain)
                abimer()
                with self.assertRaises(rmo.CompteurInvalide, msg=nom):
                    rmo.CompteurJournalier(2, d)
            sceller(sain)
            os.remove(chemin)  # le fichier a disparu, son sceau reste
            with self.assertRaises(rmo.CompteurInvalide):
                rmo.CompteurJournalier(2, d)
            invalides = [b"pas du json", b"[]", json.dumps({"jour": "2026-10-30", "appels": {"arxiv": -1, "openalex": 0}, "refus": {"arxiv": 0, "openalex": 0}}).encode(),
                         json.dumps({"jour": "2026-10-30", "appels": {"arxiv": True, "openalex": 0}, "refus": {"arxiv": 0, "openalex": 0}}).encode(),
                         json.dumps({"jour": "2026-10-30", "appels": {"arxiv": 1.5, "openalex": 0}, "refus": {"arxiv": 0, "openalex": 0}}).encode(),
                         json.dumps({"jour": "2026-10-30", "appels": {"arxiv": 1, "openalex": 0, "brave": 0}, "refus": {"arxiv": 0, "openalex": 0}}).encode(),
                         json.dumps({"jour": "2026-10-29", "appels": {"arxiv": 1, "openalex": 0}, "refus": {"arxiv": 0, "openalex": 0}}).encode()]
            for contenu in invalides:
                sceller(contenu)
                with self.assertRaises(rmo.CompteurInvalide, msg=contenu):
                    rmo.CompteurJournalier(2, d)
            sceller(sain)
            # changement de jour : compteur à zéro, nouveau fichier, l'ancien intact
            avant = self.octets(chemin)
        with _mock.patch.object(rmo.CompteurJournalier, "_maintenant_jour", staticmethod(lambda: "2026-10-31")):
            c3 = rmo.CompteurJournalier(2, d)
            etat = c3.etat()
            self.assertEqual((etat["jour"], etat["appels"]["arxiv"], etat["appels"]["openalex"]), ("2026-10-31", 0, 0))
            self.assertTrue(c3.reserver("arxiv"))
            self.assertTrue(os.path.exists(os.path.join(d, "compteur-2026-10-31.json.sha256")))
            self.assertEqual(self.octets(chemin), avant)
        with _mock.patch.object(rmo.CompteurJournalier, "_maintenant_jour", staticmethod(lambda: "2026-10-30")):
            self.assertEqual(rmo.CompteurJournalier(2, d).etat()["appels"]["openalex"], 2)  # revenir au jour relit son fichier
        # sans dossier : en mémoire seulement, dit
        m = rmo.CompteurJournalier(1)
        self.assertTrue(m.reserver("arxiv"))
        self.assertFalse(m.etat()["persistant"])
        self.assertFalse(rmo.CompteurJournalier(1).etat()["appels"]["arxiv"])

    def test_v49_14_relais_de_moisson_relance_arxiv_https_et_dossier_obligatoire(self):
        """Dans un vrai processus : le relais relancé sur le même dossier garde le compteur (plafond 2 : deux appels, arrêt du
        processus, relance, le troisième est refusé 429) ; un sceau faux empêche le démarrage ; l'amont réel exige
        `--dossier-compteur` (`servir` lève `RelaisInvalide`, `principal` rend 2, aucun serveur ne démarre) ; arXiv est
        interrogé en https. Amont factice local, aucun réseau."""
        from essais.test_v47_relais_moisson import AmontMoissonFactice, appeler, lancer_relais, requete
        self.assertTrue(rmo.AMONTS["arxiv"].startswith("https://export.arxiv.org/"))
        self.assertFalse(any(v.startswith("http://") for v in rmo.AMONTS.values()))
        amont = AmontMoissonFactice()
        self.addCleanup(amont.arreter)
        d = os.path.join(self.tmp, "compteur-relais")
        procs = []

        def demarrer(nom):
            proc, url, ligne = lancer_relais(amont.url, os.path.join(self.tmp, nom), plafond=2, dossier_compteur=d)
            procs.append(proc)
            return proc, url, ligne
        try:
            proc, url, ligne = demarrer("j1.jsonl")
            self.assertIsNotNone(url, ligne)
            self.assertIn("persistant", ligne)
            self.assertEqual([appeler(url, requete("arxiv", f"monitor diffus {k}", 1))[0] for k in range(2)], [200, 200])
            proc.kill()
            proc.communicate(timeout=10)
            proc, url, ligne = demarrer("j2.jsonl")
            self.assertIsNotNone(url, ligne)
            self.assertEqual(appeler(url, requete("arxiv", "monitor diffus 3", 1))[0], 429)  # le redémarrage n'a pas remis à zéro
            etat = json.loads(appeler(url, "/moisson/etat")[1])
            self.assertEqual((etat["appels"]["arxiv"], etat["refus"]["arxiv"], etat["persistant"]), (2, 1, True))
            proc.kill()
            proc.communicate(timeout=10)
            # sceau faux : le relais ne démarre pas
            fichier = [n for n in os.listdir(d) if n.endswith(".json")][0]
            with open(os.path.join(d, fichier), "ab") as f:
                f.write(b" ")
            proc, url, ligne = demarrer("j3.jsonl")
            self.assertIsNone(url)
            self.assertIn("sceau faux", ligne)
        finally:
            for p in procs:
                if p.poll() is None:
                    p.kill()
                    p.communicate(timeout=10)
        # l'amont réel exige le dossier du compteur
        with self.assertRaisesRegex(RelaisInvalide, "dossier-compteur"):
            rmo.servir("127.0.0.1", 0, 5)
        erreurs = _io.StringIO()
        with _contextlib.redirect_stderr(erreurs):
            self.assertEqual(rmo.principal(["--port", "0"]), 2)
        self.assertIn("dossier-compteur", erreurs.getvalue())

    # --- CL13-11 : « survit » vérifiable quand la métrique le permet -------------------------------------------------------------------------------

    def test_v49_15_statistiques_et_lecture_de_la_ligne_calcul(self):
        """Unités : `lignes_calcul`, `lire_ligne_calcul` (cas sain et artefacts), `statistique_de_colonne` (huit statistiques,
        colonne par nom ou rang, cellules vides ignorées, erreurs dites), tolérance d'affichage."""
        self.assertEqual(tdm.lignes_calcul("a\nCALCUL: fichier=f.csv; colonne=v; statistique=somme\nRESULTAT: 1\nx"),
                         ["CALCUL: fichier=f.csv; colonne=v; statistique=somme"])
        self.assertEqual(tdm.lignes_calcul(""), [])
        self.assertEqual(tdm.lignes_calcul(None), [])
        trop = "".join(f"CALCUL: fichier=f{k}.csv; colonne=v; statistique=somme\n" for k in range(tdm.MAX_LIGNES_CALCUL + 3))
        self.assertEqual(len(tdm.lignes_calcul(trop)), tdm.MAX_LIGNES_CALCUL)
        champs, motif = tdm.lire_ligne_calcul("CALCUL: fichier=serie-a.csv; colonne=a; statistique=moyenne")
        self.assertEqual((champs, motif), ({"fichier": "serie-a.csv", "colonne": "a", "statistique": "moyenne"}, None))
        for ligne, mot in (("CALCUL: fichier=f.csv; colonne=a", "incomplète"), ("CALCUL: n'importe quoi", "illisible"),
                           ("CALCUL: fichier=f.csv; colonne=a; statistique=moyenne; extra=1", "inconnu"),
                           ("CALCUL: fichier=f.csv; fichier=g.csv; colonne=a; statistique=moyenne", "double"),
                           ("CALCUL: fichier=f.csv; colonne=; statistique=moyenne", "vide"),
                           ("CALCUL: fichier=f.csv; colonne=a; statistique=quantile", "statistique inconnue")):
            champs, motif = tdm.lire_ligne_calcul(ligne)
            self.assertIsNone(champs, ligne)
            self.assertIn(mot, motif, ligne)
        csv_ = "v,w\n1,x\n3,y\n5,z\n"
        attendu = {"moyenne": 3.0, "mediane": 3.0, "somme": 9.0, "minimum": 1.0, "maximum": 5.0, "nombre": 3.0, "part_positive": 1.0, "ecart_type": 2.0}
        self.assertEqual(set(attendu), set(tdm.STATISTIQUES))
        for nom, valeur in attendu.items():
            self.assertEqual(tdm.statistique_de_colonne(csv_, "v", nom), (valeur, None), nom)
        self.assertEqual(tdm.statistique_de_colonne(csv_, "0", "somme"), (9.0, None))  # colonne par son rang
        self.assertEqual(tdm.statistique_de_colonne("v\n1\n-2\n0\n", "v", "part_positive"), (1 / 3, None))
        self.assertEqual(tdm.statistique_de_colonne("v,w\n1,\n,\n3,\n", "v", "nombre"), (2.0, None))  # cellules vides ignorées
        for texte, colonne, stat_, mot in (("", "v", "somme", "vide"), ("v\n1\n", "absente", "somme", "introuvable"),
                                            ("v\nabc\n", "v", "somme", "non numérique"), ("v\nnan\n", "v", "somme", "non finie"),
                                            ("v\ninf\n", "v", "somme", "non finie"), ("v,w\n1\n", "w", "somme", "trop courte"),
                                            ("v\n", "v", "somme", "aucune valeur"), ("v,w\n1,x\n\n3,y\n", "v", "somme", "trop courte"), ("v\n1\n", "v", "ecart_type", "deux valeurs"),
                                            ("v\n1\n", "9", "somme", "introuvable")):
            valeur, motif = tdm.statistique_de_colonne(texte, colonne, stat_)
            self.assertIsNone(valeur, texte)
            self.assertIn(mot, motif, texte)
        self.assertEqual(tdm.statistique_de_colonne("v\n1\n2\n3\n", "v", "somme", max_lignes=2)[1], "fichier trop long pour le recalcul")
        self.assertAlmostEqual(tdm._tolerance_d_affichage("RESULTAT: 0.33"), 0.005, places=6)
        self.assertAlmostEqual(tdm._tolerance_d_affichage("RESULTAT: 0,3333"), 0.00005, places=9)
        self.assertIsNone(tdm._tolerance_d_affichage("RESULTAT: 3"))
        self.assertIsNone(tdm._tolerance_d_affichage("RESULTAT: 1e-1"))

    def test_v49_16_recalcul_du_noyau_concordant_discordant_non_recalculable(self):
        """`recalcul_noyau` : concordant à l'arrondi d'affichage près (0,33 pour 1/3), discordant au-delà ; « non demandé » sans
        ligne `CALCUL:` ; « non recalculable » (ligne illisible, statistique inconnue, fichier hors des données du
        préenregistrement, colonne absente) avec l'étiquette « non recalculé » ; « sans chiffre » ; l'exécution lue est celle
        du chiffre."""
        tranche = _types.SimpleNamespace(fichiers={"f.csv": {"texte": "v\n0\n0\n1\n"}, "g.csv": {"texte": "v\n9\n"}})
        prereg = {"donnees": [{"chemin": "f.csv"}], "seuil": {"comparateur": "≥", "valeur": 0.3}}
        calc = "CALCUL: fichier=f.csv; colonne=v; statistique=moyenne"

        def jouer(ligne_calcul, imprime, ligne=None, numero=1):
            execs = [{"numero": 1, "lignes_calcul": ["CALCUL: fichier=f.csv; colonne=v; statistique=somme"] if numero == 2 else []},
                     {"numero": 2, "lignes_calcul": [ligne_calcul] if ligne_calcul else []}]
            meca = {"chiffre": imprime, "ligne": ligne or f"RESULTAT: {imprime}", "execution": numero}
            return tdm.recalcul_noyau(prereg, tranche, execs, meca)
        r = jouer(calc, 0.33, numero=2)
        self.assertEqual((r["statut"], r["etiquette"], r["execution"]), ("concordant", tdm.ETIQUETTE_RECALCULE, 2))
        self.assertAlmostEqual(r["valeur_noyau"], 1 / 3)
        self.assertEqual(jouer(calc, 0.3333, numero=2)["statut"], "concordant")
        self.assertEqual(jouer(calc, 0.3333333333, numero=2)["statut"], "concordant")
        self.assertEqual(jouer(calc, 0.3, numero=2)["statut"], "concordant")  # 1/3 arrondi à une décimale
        for faux in (0.2, 0.34, 0.9, 0.0):
            r = jouer(calc, faux, numero=2)
            self.assertEqual((r["statut"], r["etiquette"]), ("discordant", tdm.ETIQUETTE_NON_RECALCULE), faux)
            self.assertIn("écart", r["motif"])
        r = jouer(calc, 0.33, ligne="RESULTAT: 0,33", numero=2)
        self.assertEqual(r["statut"], "concordant")  # virgule décimale
        r = jouer(None, 0.4, numero=2)
        self.assertEqual((r["statut"], r["etiquette"], r["valeur_noyau"]), ("non demandé", tdm.ETIQUETTE_NON_RECALCULE, None))
        for ligne_calcul, mot in (("CALCUL: n'importe quoi", "illisible"),
                                  ("CALCUL: fichier=f.csv; colonne=v; statistique=quantile", "inconnue"),
                                  ("CALCUL: fichier=g.csv; colonne=v; statistique=somme", "hors des données"),
                                  ("CALCUL: fichier=h.csv; colonne=v; statistique=somme", "hors des données"),
                                  ("CALCUL: fichier=f.csv; colonne=absente; statistique=somme", "introuvable")):
            r = jouer(ligne_calcul, 0.4, numero=2)
            self.assertEqual((r["statut"], r["etiquette"]), ("non recalculable", tdm.ETIQUETTE_NON_RECALCULE), ligne_calcul)
            self.assertIn(mot, r["motif"], ligne_calcul)
        r = tdm.recalcul_noyau(prereg, tranche, [], {"chiffre": None, "ligne": None, "execution": None})
        self.assertEqual(r["statut"], "sans chiffre")
        # la dernière ligne CALCUL: de l'exécution lue fait foi
        execs = [{"numero": 1, "lignes_calcul": ["CALCUL: fichier=f.csv; colonne=v; statistique=somme", calc]}]
        self.assertEqual(tdm.recalcul_noyau(prereg, tranche, execs, {"chiffre": 0.33, "ligne": "RESULTAT: 0.33", "execution": 1})["statut"], "concordant")
        # étiquettes du matériau
        base = {"statut": "testée", "motif": None}
        self.assertEqual(tdm.etiquette_materiau(dict(base, verdict="survit", fiabilite_du_chiffre=tdm.ETIQUETTE_NON_RECALCULE)),
                         "survit (chiffre imprimé par le script, non recalculé)")
        self.assertEqual(tdm.etiquette_materiau(dict(base, verdict="éliminée", fiabilite_du_chiffre=tdm.ETIQUETTE_RECALCULE)),
                         "éliminée (statistique déclarée par le script, recalculée par le noyau)")
        self.assertEqual(tdm.etiquette_materiau(dict(base, verdict="non concluant", fiabilite_du_chiffre=tdm.ETIQUETTE_RECALCULE)), "non concluant")
        self.assertEqual(tdm.etiquette_materiau(dict(base, verdict="survit")), "survit")
        self.assertEqual(tdm.etiquette_materiau({"statut": "refusée à l'étage", "motif": "sans seuil"}), "non testée (sans seuil)")
        # vue du lecteur : le recalcul est joint à l'exécution dont il porte le chiffre, jamais à une autre
        vue = tdm.vue_lecteur([{"numero": 1, "statut": "réussie"}, {"numero": 2, "statut": "réussie"}],
                              {"execution": 2, "statut": "concordant", "valeur_script": 0.33, "valeur_noyau": 1 / 3, "etiquette": tdm.ETIQUETTE_RECALCULE})
        self.assertNotIn("recalcul_noyau", vue[0])
        self.assertEqual(vue[1]["recalcul_noyau"]["statut"], "concordant")
        vue = tdm.vue_lecteur([{"numero": 1, "statut": "réussie"}], {"execution": 1, "statut": "sans chiffre"})
        self.assertNotIn("recalcul_noyau", vue[0])

    def test_v49_17_etage_le_chiffre_imprime_n_est_plus_pris_sur_parole(self):
        """Dans l'étage : script qui déclare sa statistique et dont le chiffre concorde → « survit », matériau « (chiffre
        recalculé par le noyau) » ; script qui imprime un chiffre faux, **dans les deux sens** (R4 : 0,9 pour une moyenne de 3
        n'est pas plus sûr que 0,1) → « non concluant » avec `desaccord`, la lecture mécanique et le lecteur concordant entre
        eux ; script sans `CALCUL:` → « survit » étiqueté « non recalculé » ; `CALCUL:` hors des données → « non recalculable ».
        Le lecteur voit le champ `recalcul_noyau`, jamais le script ; l'expérimentateur sait ce que `CALCUL:` fait."""
        scenarios = [("e49c1", script_calcul(3.0), "survit", "concordant", tdm.ETIQUETTE_RECALCULE),
                     ("e49c2", script_calcul(0.9), "non concluant", "discordant", tdm.ETIQUETTE_NON_RECALCULE),
                     ("e49c3", script_calcul(0.1), "non concluant", "discordant", tdm.ETIQUETTE_NON_RECALCULE),
                     ("e49c4", script_resultat(0.4), "survit", "non demandé", tdm.ETIQUETTE_NON_RECALCULE),
                     ("e49c5", script_calcul(3.0, donnee="serie-a.csv", colonne="inexistante"), "survit", "non recalculable", tdm.ETIQUETTE_NON_RECALCULE),
                     ("e49c6", script_calcul(3.0).replace("serie-a.csv; colonne", "serie-b.csv; colonne"), "survit", "non recalculable", tdm.ETIQUETTE_NON_RECALCULE)]
        for nom, script, verdict, statut, etiquette in scenarios:
            ad, par = self.etage_simple(nom, lambda f, t, c, s=script: bloc_exp(executer(s)) if t == 1 else bloc_fin())
            r = list(par.values())[0]
            self.assertEqual((r["verdict"], r["recalcul_noyau"]["statut"], r["fiabilite_du_chiffre"]), (verdict, statut, etiquette), nom)
            self.assertEqual(r["lecture_mecanique"]["verdict"], "survit" if nom != "e49c3" else "éliminée", nom)
            if statut == "discordant":
                self.assertIn("discordant", r["desaccord"])
                self.assertEqual(r["lecteur"]["verdict"], r["lecture_mecanique"]["verdict"])  # le lecteur et la lecture mécanique concordent : seul le noyau voit
            materiau = self.h().lire(os.path.join(self.tmp, nom, "noyau", "tests-de-mort", "materiau-tests-de-mort.md"))
            self.assertIn(f"- Une (rang 1) : {verdict}" + (f" ({etiquette})" if verdict != "non concluant" else ""), materiau, nom)
            lecteur = [a for a in ad.appels if a["role"] == "lecteur_test"][0]["consigne"]
            vue = section_de(lecteur, "Sortie scellée des exécutions")
            self.assertEqual(vue[0]["recalcul_noyau"]["statut"], statut, nom)
            self.assertNotIn("open('tranche/serie-a.csv'", lecteur)  # le lecteur ne voit pas le script
            self.assertIn("recalcul_noyau", lecteur)
        # le lecteur voit le champ du recalcul pour le cas concordant
        ad, par = self.etage_simple("e49c7", lambda f, t, c: bloc_exp(executer(script_calcul(3.0))) if t == 1 else bloc_fin())
        lecteur = [a for a in ad.appels if a["role"] == "lecteur_test"][0]["consigne"]
        vue = section_de(lecteur, "Sortie scellée des exécutions")
        self.assertEqual(vue[0]["recalcul_noyau"]["statut"], "concordant")
        self.assertEqual(vue[0]["recalcul_noyau"]["valeur_noyau"], 3.0)
        experimentateur = [a for a in ad.appels if a["role"] == "experimentateur_test"][0]["consigne"]
        self.assertIn("CALCUL:", experimentateur)
        self.assertIn("recalcul", experimentateur.lower())
        # le manifeste de l'étage porte le recalcul
        self.assertEqual(list(par.values())[0]["recalcul_noyau"]["valeur_noyau"], 3.0)

    # --- CL13-10 : traçabilité du code modifié ---------------------------------------------------------------------------------------------------------

    def test_v49_18_provenance_du_code_modifie_dit_au_lisezmoi(self):
        """R12 : le LISEZMOI de la v49 liste **chaque fichier de code modifié** avec l'empreinte v48 (celle de
        `EMPREINTES-orchestrateur-pole-v7-v48.txt`, vérifiée) et l'empreinte v49 (celle de `EMPREINTES-orchestrateur-pole-v7-v49.txt`,
        scellée : depuis la v50 le disque a changé, le fichier de la v49 ne change plus) ; tout fichier de l'empreinte v48 dont le
        contenu a changé dans la v49 figure dans le tableau ; aucun fichier du tableau n'est inchangé."""
        from essais.test_v47_relais_moisson import RACINE
        lisezmoi = os.path.join(RACINE, "LISEZMOI-orchestrateur-pole-v7-v49.md")
        self.assertTrue(os.path.exists(lisezmoi), "LISEZMOI de la v49 absent")

        def lire_empreintes(nom):
            sortie = {}
            with open(os.path.join(RACINE, nom), encoding="utf-8") as f:
                for ligne in f:
                    if ligne.strip():
                        empreinte, chemin = ligne.split(None, 1)
                        sortie[chemin.strip()] = empreinte
            return sortie
        v48, v49 = lire_empreintes("EMPREINTES-orchestrateur-pole-v7-v48.txt"), lire_empreintes("EMPREINTES-orchestrateur-pole-v7-v49.txt")
        tableau = {}
        with open(lisezmoi, encoding="utf-8") as f:
            for ligne in f:
                m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|\s*`([0-9a-f]{64})`\s*\|", ligne)
                if m:
                    tableau[m.group(1)] = (m.group(2), m.group(3))
        self.assertTrue(tableau, "tableau de provenance absent du LISEZMOI")
        self.assertIn("essais/test_v7_ideation.py", tableau)
        for chemin, (ancienne, nouvelle) in tableau.items():
            if chemin in v48:
                self.assertEqual(ancienne, v48[chemin], f"empreinte v48 de {chemin} ≠ EMPREINTES v48")
            self.assertNotEqual(ancienne, nouvelle, f"{chemin} : listé mais inchangé")
            self.assertEqual(nouvelle, v49[chemin], f"{chemin} : empreinte v49 ≠ EMPREINTES v49")
        for chemin, empreinte in v48.items():
            if chemin.startswith(("LISEZMOI", "EMPREINTES")):
                self.assertEqual(hashlib.sha256(open(os.path.join(RACINE, chemin), "rb").read()).hexdigest(), empreinte, f"{chemin} : fichier scellé modifié")
                continue
            if v49[chemin] != empreinte:
                self.assertIn(chemin, tableau, f"{chemin} a changé dans la v49 et n'est pas dans le tableau de provenance")

    # --- CL13-01, CL13-08 : essais réels, seulement avec `bwrap` ---------------------------------------------------------------------------------

    @essai_reel_bwrap  # v51 (CL15-04) : sans bwrap, échec — jamais ignoré en silence
    def test_v49_19_evasion_rejouee_dans_le_vrai_bac_cibles_factices(self):
        """Seulement avec `bwrap` : les évasions de la contre-lecture CL13, jouées **contre des cibles factices dans un dossier
        provisoire** (jamais contre le vrai `/usr`, `/etc` ou `/root`), échouent toutes dans le vrai bac : superutilisateur,
        capacités, remontage de la tranche (copie factice), écriture dans la tranche, écriture dans un dossier de l'hôte
        (factice), lecture d'un secret de l'hôte (factice), lecture de l'environnement, `setsid`, réseau."""
        hote = os.path.join(self.tmp, "hote-factice")
        os.makedirs(hote)
        secret = os.path.join(hote, "secret.txt")
        with open(secret, "w", encoding="utf-8") as f:
            f.write("SECRET-FACTICE-DE-L-HOTE")
        sonde = (
            "import ctypes, os, socket\n"
            "def essai(nom, f):\n"
            "    try:\n        resultat = f()\n    except BaseException as e:\n        print(nom, 'refus', type(e).__name__)\n"
            "    else:\n        print(nom, 'REUSSI', resultat)\n"
            "def remonter():\n"
            "    r = ctypes.CDLL(None, use_errno=True).mount(b'none', b'/travail/tranche', None, 32 | 4096, None)\n"
            "    if r != 0:\n        raise OSError(ctypes.get_errno(), 'refus')\n"
            "    return 'monte'\n"
            "print('identifiant', os.getuid())\n"
            "essai('ecrire-hote', lambda: open(%r, 'w').write('x'))\n"
            "essai('lire-secret', lambda: open(%r).read())\n"
            "essai('ecrire-tranche', lambda: open('tranche/nouveau.txt', 'w').write('x'))\n"
            "essai('ecrire-donnee', lambda: open('tranche/serie-a.csv', 'w').write('x'))\n"
            "essai('remonter-tranche', remonter)\n"
            "essai('ecrire-racine', lambda: open('/essai-racine.txt', 'w').write('x'))\n"
            "essai('reseau', lambda: socket.create_connection(('127.0.0.1', 9), 1))\n"
            "print('environ', sorted(os.environ))\n"
            "print('RESULTAT: 0.4')\n") % (os.path.join(hote, "ecrit.txt"), secret)
        _, par = self.etage_simple("e49v", lambda f, t, c: bloc_exp(executer(sonde)) if t == 1 else bloc_fin(),
                                   executeur=executeur_reel(self, 20.0), delai_execution_s=20.0)
        r = list(par.values())[0]
        sortie = self.h().lire(os.path.join(self.tmp, "e49v", "noyau", "tests-de-mort", list(par)[0], "execution-01", "stdout.txt"))
        for ligne in sortie.splitlines():
            self.assertNotIn(" REUSSI", ligne)
        for nom in ("ecrire-hote", "lire-secret", "ecrire-tranche", "ecrire-donnee", "remonter-tranche", "ecrire-racine", "reseau"):
            self.assertIn(f"{nom} refus", sortie)
        self.assertIn("identifiant 65534", sortie)
        self.assertNotIn("SECRET-FACTICE-DE-L-HOTE", sortie)
        self.assertFalse(os.path.exists(os.path.join(hote, "ecrit.txt")))
        self.assertEqual(r["executions"][0]["statut"], "réussie")
        tranche = self.prep_tranche()
        self.assertNotIn("nouveau.txt", os.listdir(tranche))
        self.assertEqual(self.h().lire(os.path.join(tranche, "serie-a.csv")), "a,b\n1,2\n3,4\n5,6\n")

    def prep_tranche(self):
        return self.h().prep()["tranche"]


# ======================================================================================================================
# v50 : corrections de la contre-lecture CL14 (Opus neuf) — identité du script SUR L'HÔTE (CL14-01, CL14-02 : utilisateur
# dédié sans privilège, /proc/sys en lecture seule, borne de processus, aucun fichier setuid), espaces d'utilisateurs
# imbriqués (CL14-03), sortie scellée sans dossier de travail (CL14-04), noms `.sha256` (CL14-05), recalcul strict (CL14-06),
# Argon (CL14-07 à 09), /dev/shm (CL14-10), artefacts de la sonde et essais réels (CL14-11), dossier fermé (CL14-12).
# Aucun essai n'écrit dans un réglage réel du noyau de l'hôte ni hors de dossiers temporaires créés ici : une ouverture en
# écriture de /proc/sys qui réussirait serait un échec d'essai, jamais une écriture.
# ======================================================================================================================

import tempfile as _tempfile  # noqa: E402
import subprocess as _subprocess  # noqa: E402

UID_ESSAI = 64097  # identité sans privilège des essais « utilisateur dédié » (noyau superutilisateur de la machine d'essai seulement)


def utilisateur_dedie_possible():
    """Vrai si les essais peuvent jouer un processus sous l'identité sans privilège `UID_ESSAI` : noyau superutilisateur et
    `setpriv` qui fonctionne. Sinon ces essais sont ignorés (dit)."""
    if os.geteuid() != 0 or not shutil.which("setpriv"):
        return False
    try:
        r = _subprocess.run(["setpriv", "--reuid", str(UID_ESSAI), "--regid", str(UID_ESSAI), "--clear-groups", "--no-new-privs",
                             "--", "/usr/bin/id", "-u"], capture_output=True, timeout=20)
    except (OSError, _subprocess.SubprocessError):
        return False
    return r.returncode == 0 and r.stdout.strip() == str(UID_ESSAI).encode()


def racine_bac_essai(test, uid):
    """v51 (CL15-04) : un dossier racine du bac pour les essais réels — parent provisoire du système (mode 0711, au
    superutilisateur), dossier `bac` à l'utilisateur dédié (0700) ; tous les parents doivent être traversables (sinon échec,
    dit) ; retiré à la fin de l'essai : rien ne reste sur l'hôte."""
    parent = os.path.realpath(_tempfile.mkdtemp(prefix="essai-bac-v51-"))
    test.addCleanup(shutil.rmtree, parent, True)
    os.chmod(parent, 0o711)
    courant = os.path.dirname(parent)
    while True:
        if not os.stat(courant).st_mode & 0o001:
            test.fail(f"dossier provisoire du système non traversable par l'utilisateur dédié ({courant}) : donner "
                      "POLE_ESSAI_RACINE_TRAVAIL_BAC, ou un TMPDIR traversable")
        if courant == "/":
            break
        courant = os.path.dirname(courant)
    bac = os.path.join(parent, "bac")
    os.mkdir(bac, 0o700)
    os.chown(bac, uid, uid)
    return bac


def executeur_reel(test, delai, **kw):
    """Le vrai bac à sable (v50) : un noyau superutilisateur **doit** donner un utilisateur dédié sans privilège et un dossier
    racine à lui, sinon l'étage est refusé ; un noyau non superutilisateur joue le bac sous sa propre identité.
    v51 (CL15-04) : **jamais ignoré en silence**. Sans `bwrap`, l'essai échoue (sauf `POLE_ESSAI_BAC_REEL_NON_JOUE=1`, dit). Sous
    un noyau superutilisateur, les variables `POLE_ESSAI_UTILISATEUR_BAC` et `POLE_ESSAI_RACINE_TRAVAIL_BAC` restent permises ;
    sans elles, l'essai prend l'identité `UID_ESSAI` (sans compte, vérifiée par `setpriv`) et un dossier racine provisoire
    (`racine_bac_essai`), retiré à la fin ; si `setpriv` ne peut pas la prendre, l'essai échoue."""
    if not shutil.which("bwrap"):
        exiger_essai_reel(test, "bwrap absent de cette machine : essai réel à rejouer dans le conteneur de session-depot")
    if os.geteuid() == 0:
        utilisateur, racine = os.environ.get("POLE_ESSAI_UTILISATEUR_BAC"), os.environ.get("POLE_ESSAI_RACINE_TRAVAIL_BAC")
        if not utilisateur:
            if not utilisateur_dedie_possible():
                exiger_essai_reel(test, f"noyau superutilisateur sans setpriv utilisable pour l'identité {UID_ESSAI}")
            utilisateur = UID_ESSAI
        if not racine:
            racine = racine_bac_essai(test, tdm.resoudre_utilisateur_bac(utilisateur)[0])
        return tdm.ExecuteurBacASable(delai_s=delai, utilisateur_bac=utilisateur, racine_travail=racine, **kw)
    return tdm.ExecuteurBacASable(delai_s=delai, **kw)


def en_tant_que(uid, fonction):
    """Joue `fonction()` dans un processus enfant d'identité `uid` (noyau superutilisateur) et rend son résultat (JSON) ; le
    parent garde son identité. L'enfant vérifie son identité avant tout appel : s'il est resté superutilisateur, il n'y a aucun
    appel."""
    lecture, ecriture = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(lecture)
            os.setgroups([])
            os.setgid(uid)
            os.setuid(uid)
            if os.getuid() != uid or os.geteuid() != uid or os.getgid() != uid:
                raise RuntimeError("identité non changée")
            resultat = fonction()
        except BaseException as e:  # noqa: BLE001
            resultat = {"erreur": repr(e)}
        os.write(ecriture, json.dumps(resultat).encode())
        os._exit(0)
    os.close(ecriture)
    morceaux = []
    while True:
        m = os.read(lecture, 65536)
        if not m:
            break
        morceaux.append(m)
    os.close(lecture)
    os.waitpid(pid, 0)
    return json.loads(b"".join(morceaux).decode() or "null")


SCRIPT_ARGON_CODE = ("import json, os, sys\nsys.stdin.read()\nobjet = {'texte': 'JAMAIS SERVI', 'cout_usd': 0.2}\nobjet.update(%s)\n"
                     "print(json.dumps(objet))\nsys.exit(%d)\n")


class TestV50(CasAvecDossier):
    """v50 (corrections de la contre-lecture CL14) : un groupe d'essais par constat ; les essais qui exigent un noyau
    superutilisateur (utilisateur dédié, `setpriv`) ou `bwrap` sont ignorés ailleurs, avec leur motif."""

    def setUp(self):
        super().setUp()
        self.garde = garde_fou_reseau()
        self.garde.__enter__()
        self.addCleanup(self.garde.__exit__, None, None, None)

    def h(self):
        return TestV49.h(self)

    octets = staticmethod(TestV49.octets)
    liens_tubes_et_prises = staticmethod(TestV49.liens_tubes_et_prises)
    PROP = TestV49.PROP
    JUGES = TestV49.JUGES
    SCRIPT_ARGON = TestV49.SCRIPT_ARGON

    def etage_simple(self, nom, exp, nombre=1, fiches=None, **modifs):
        h = self.h()
        ad = h.kit({"opus": fiches or [h.fiche("Une")]}, exp=exp)
        h.course(ad, nom, etage=h.etage(nombre=nombre, **modifs), proposeurs=self.PROP, juges=self.JUGES)
        return ad, h.par_fiche(nom)

    def dossier_systeme_isole(self):
        """Un dossier provisoire qui tient lieu de dossier provisoire du système pour la durée de l'essai : on y voit tout ce que
        l'étage y crée (et doit y retirer)."""
        racine = os.path.join(self.tmp, "tmp-systeme")
        os.makedirs(racine)
        patch = _mock.patch.object(_tempfile, "tempdir", racine)
        patch.start()
        self.addCleanup(patch.stop)
        return racine

    def dossier_traversable(self):
        """Un dossier provisoire du système (le dossier de l'essai est dans le dépôt, que l'utilisateur dédié ne traverse pas)
        traversable par tous, retiré à la fin."""
        base = _tempfile.mkdtemp(prefix="essai-bac-v50-")
        os.chmod(base, 0o711)
        self.addCleanup(shutil.rmtree, base, True)
        return os.path.realpath(base)

    # --- CL14-01, CL14-02 : l'utilisateur dédié -----------------------------------------------------------------------------------

    def test_v50_01_utilisateur_dedie_resolution_et_commande_lancee(self):
        """`resoudre_utilisateur_bac` : un entier, un entier en texte ou un nom ; jamais le superutilisateur, un identifiant
        négatif ou énorme, un booléen, un nom inconnu. `commande_lancee` : sans utilisateur dédié, la commande de `bwrap` seule ;
        avec : `setpriv --reuid U --regid U --clear-groups --no-new-privs --` devant (le noyau superutilisateur ne lance jamais
        `bwrap` lui-même). `description()` dit l'identité sur l'hôte, `--disable-userns`, `/dev/shm`, la borne de processus."""
        r = tdm.resoudre_utilisateur_bac
        self.assertEqual(r(64097), (64097, 64097, None))
        self.assertEqual(r("64097"), (64097, 64097, None))
        self.assertEqual(r(" 7 "), (7, 7, None))
        for mauvais in (0, "0", -1, 2**31, True, False, None, "utilisateur-inconnu-v50-xyz", "", 1.5, [1]):
            with self.assertRaises(ValueError, msg=repr(mauvais)):
                r(mauvais)
        with self.assertRaises(ValueError):
            r("root")  # le superutilisateur, par son nom
        sans = tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3")
        travail = os.path.join(self.tmp, "t")
        os.makedirs(travail)
        self.assertEqual(sans.commande_lancee(os.path.join(travail, "script.py"), travail), sans.commande(os.path.join(travail, "script.py"), travail))
        self.assertIsNone(sans.proprietaire_travail())
        avec = tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3", utilisateur_bac=64097, racine_travail=travail,
                                      chercher=lambda nom: "/usr/bin/" + nom)
        cmd = avec.commande_lancee(os.path.join(travail, "script.py"), travail)
        self.assertEqual(cmd[:8], ["/usr/bin/setpriv", "--reuid", "64097", "--regid", "64097", "--clear-groups", "--no-new-privs", "--"])
        self.assertEqual(cmd[8:], avec.commande(os.path.join(travail, "script.py"), travail))
        self.assertEqual(avec.proprietaire_travail(), (64097, 64097))
        d = avec.description()
        self.assertEqual(d["identite_du_script_sur_l_hote"]["utilisateur_dedie"]["uid"], 64097)
        self.assertEqual(d["espaces_d_utilisateurs_imbriques"], "interdits (--disable-userns)")
        self.assertEqual(d["dev_shm_octets_max"], tdm.TAILLE_MAX_DEV_SHM)
        self.assertTrue(d["dossier_de_travail"]["hors_de_la_sortie"] and d["dossier_de_travail"]["retire_apres_chaque_execution"])
        self.assertTrue(d["borne_de_processus_effective"])
        self.assertIn("utilisateur dédié sans privilège", d["isolation"])
        with _mock.patch.object(tdm, "_euid_noyau", return_value=0):
            self.assertFalse(sans.borne_processus_effective())  # CL14-02 : la borne ne vaut pas pour le superutilisateur
            self.assertTrue(avec.borne_processus_effective())
            self.assertTrue(sans.description()["identite_du_script_sur_l_hote"]["noyau_superutilisateur"])
        with _mock.patch.object(tdm, "_euid_noyau", return_value=1000):
            self.assertTrue(sans.borne_processus_effective())
        permis = tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3", userns_imbriques_permis=True)
        self.assertNotIn("--disable-userns", permis.commande(os.path.join(travail, "script.py"), travail))
        self.assertIn("PERMIS", permis.description()["espaces_d_utilisateurs_imbriques"])
        self.assertNotIn("--disable-userns", permis.description()["isolation"])
        with self.assertRaises(ValueError):
            tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", racine_travail="relatif")

    def test_v50_02_identite_du_noyau_superutilisateur_sans_utilisateur_dedie_refusee(self):
        """CL14-01 : un noyau superutilisateur sans utilisateur dédié est refusé **avant** la sonde (aucun `bwrap` lancé : le
        journal du faux `bwrap` reste vide) ; avec un utilisateur dédié, le dossier racine est exigé, doit être un vrai dossier
        possédé par lui, non inscriptible par le groupe ni les autres ; un utilisateur dédié sous un noyau qui n'est pas
        superutilisateur est refusé ; `setpriv` absent aussi ; sans identité superutilisatrice, aucun utilisateur n'est exigé."""
        faux, journal = TestV49.faux_bwrap(self)
        racine = os.path.join(self.tmp, "racine")
        os.makedirs(racine)
        moi = os.getuid()
        with _mock.patch.object(tdm, "_euid_noyau", return_value=0):
            ex = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable)
            self.assertIn("aucun utilisateur dédié", ex.verifier_identite())
            ok, motif = ex.disponible()
            self.assertFalse(ok)
            self.assertIn("CL14-01", motif)
            self.assertIn("aucun repli", motif)
            self.assertFalse(os.path.exists(journal))  # rien n'a été lancé
            # l'exécuteur factice et le faux bac des essais ne sont pas soumis à l'identité (aucune barrière, dit)
            self.assertIsNone(tdm.ExecuteurFactice().verifier_identite())
            # utilisateur dédié : dossier racine obligatoire, possédé, non inscriptible par d'autres
            u = moi if moi else UID_ESSAI
            sans_racine = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=u)
            self.assertIn("sans dossier de travail racine", sans_racine.verifier_identite())
            absent = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=u, racine_travail=os.path.join(racine, "absent"))
            self.assertIn("illisible", absent.verifier_identite())
            lien = os.path.join(self.tmp, "lien-racine")
            os.symlink(racine, lien)
            self.assertIn("pas un dossier réel", tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=u,
                                                                         racine_travail=lien).verifier_identite())
            os.chmod(racine, 0o700)
            if moi == 0:  # superutilisateur de la machine d'essai : on peut donner le dossier à un autre
                os.chown(racine, UID_ESSAI, UID_ESSAI)
                mauvais_proprio = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=UID_ESSAI + 1, racine_travail=racine)
                self.assertIn("non possédé", mauvais_proprio.verifier_identite())
            bon = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=u if moi else UID_ESSAI, racine_travail=racine)
            if moi:
                self.assertIsNone(tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=UID_ESSAI,
                                                         racine_travail=racine, chercher=lambda n: sys.executable).verifier_identite())
            os.chmod(racine, 0o770)
            self.assertIn("inscriptible par le groupe", tdm.ExecuteurBacASable(
                bwrap=faux, python=sys.executable, utilisateur_bac=u if moi else UID_ESSAI, racine_travail=racine).verifier_identite()
                if moi == 0 else "inscriptible par le groupe")
            os.chmod(racine, 0o700)
        with _mock.patch.object(tdm, "_euid_noyau", return_value=1000):
            ex = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=64097)
            self.assertIn("n'est pas superutilisateur", ex.verifier_identite())
            self.assertIsNone(tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable).verifier_identite())
        absent = tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable, utilisateur_bac=64097, chercher=lambda nom: None)
        self.assertIn("setpriv absent", absent.verifier_outils())
        # un étage avec un exécuteur refusé pour son identité : rien n'est écrit, rien n'est payé (comme pour un bac absent)
        ad = self.h().kit()
        with _mock.patch.object(tdm, "_euid_noyau", return_value=0):
            with self.assertRaisesRegex(idn.CourseInterrompue, "aucun utilisateur dédié"):
                self.h().course(ad, "e50i", etage=self.h().etage(executeur=tdm.ExecuteurBacASable(bwrap=faux, python=sys.executable)))
        self.assertEqual(ad.appels, [])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "e50i")))

    def test_v50_03_sonde_les_nouveaux_artefacts_chacun_refuse_l_executeur(self):
        """R5 : la sonde lit l'identité de l'hôte, `/proc/sys`, l'espace d'utilisateurs imbriqué, `/dev/shm`, la borne de processus
        et l'ensemble limite des capacités. Cas sain accepté ; **chaque artefact refuse l'exécuteur**, avec son motif : identité 0
        de l'hôte (utilisateur et groupe — le défaut de la v49), différente de l'utilisateur dédié attendu, illisible ; `CapBnd`
        non nul ; `core_pattern`, `suid_dumpable` ou un autre réglage ouvert en écriture ; réglages ouvrables en nombre ;
        espace d'utilisateurs imbriqué créé (accepté seulement sur demande explicite) ; `/dev/shm` non borné (accepté : non monté) ;
        borne de processus qui ne tient pas ou non posée ; toute ligne manquante. Joué aussi avec un faux bac qui rend la sortie."""
        ev = tdm.evaluer_sonde_privileges
        self.assertEqual(ev(SORTIE_PRIVILEGES_SAINE), (True, "privilèges nuls"))
        self.assertEqual(ev(SORTIE_PRIVILEGES_SAINE, uid_hote_attendu=64321), (True, "privilèges nuls"))
        # v51 (CL15-01) : plus de UID_HOTE ni GID_HOTE (lus dans uid_map : faux dans le bac) ; le témoin d'identité est exigé, son
        # propriétaire est lu par le noyau sur l'hôte (essais réels de test_v51_bac_reel.py) ; les deux premiers cas gardent leur rang
        cas = [("TEMOIN-IDENTITE=cree", "TEMOIN-IDENTITE=refus-errno-13", "témoin d'identité"),
               ("TEMOIN-IDENTITE=cree", "TEMOIN-IDENTITE=refus-errno-17", "témoin d'identité"),
               ("TEMOIN-IDENTITE=cree", "TEMOIN-IDENTITE=inconnue", "témoin d'identité"), ("TEMOIN-IDENTITE=cree\n", "", "absente"),
               ("TEMOIN-IDENTITE=cree\n", "TEMOIN-IDENTITE\n", "absente"),
               ("CapBnd=0000000000000000", "CapBnd=000001ffffffffff", "capacités"), ("CapBnd=0000000000000000\n", "", "absente"),
               ("PROCSYS kernel/core_pattern=refus-errno-30", "PROCSYS kernel/core_pattern=OUVERT-EN-ECRITURE", "core_pattern"),
               ("PROCSYS fs/suid_dumpable=refus-errno-30", "PROCSYS fs/suid_dumpable=OUVERT-EN-ECRITURE", "suid_dumpable"),
               ("PROCSYS-OUVRABLES=0", "PROCSYS-OUVRABLES=528", "528 réglages"), ("PROCSYS-OUVRABLES=0\n", "", "absente"),
               ("PROCSYS kernel/core_pattern=refus-errno-30\n", "", "absente"),
               ("USERNS-IMBRIQUE=refus", "USERNS-IMBRIQUE=REUSSI", "imbriqué"), ("USERNS-IMBRIQUE=refus\n", "", "absente"),
               ("SHM=refus-apres-32-Mo-errno-28", "SHM=REUSSI-40-Mo", "/dev/shm n'est pas borné"), ("SHM=refus-apres-32-Mo-errno-28\n", "", "absente"),
               ("PROCESSUS=refus-apres-1000-errno-11", "PROCESSUS=REUSSI-1056", "borne de processus"),
               ("PROCESSUS=refus-apres-1000-errno-11", "PROCESSUS=non-borne", "borne de processus"),
               ("PROCESSUS=refus-apres-1000-errno-11\n", "", "absente")]
        for avant, apres, motif in cas:
            sortie = SORTIE_PRIVILEGES_SAINE.replace(avant, apres)
            self.assertNotEqual(sortie, SORTIE_PRIVILEGES_SAINE, avant)
            ok, m = ev(sortie)
            self.assertFalse(ok, avant)
            self.assertIn(motif, m, avant)
        # accepté : /dev/shm non monté ; espace imbriqué sur demande explicite ; mais pas l'identité 0 même alors
        self.assertTrue(ev(SORTIE_PRIVILEGES_SAINE.replace("SHM=refus-apres-32-Mo-errno-28", "SHM=non-monte-errno-2"))[0])
        self.assertTrue(ev(SORTIE_PRIVILEGES_SAINE.replace("USERNS-IMBRIQUE=refus", "USERNS-IMBRIQUE=REUSSI"), userns_permis=True)[0])
        self.assertFalse(ev(SORTIE_PRIVILEGES_SAINE.replace("TEMOIN-IDENTITE=cree", "TEMOIN-IDENTITE=refus-errno-13"), userns_permis=True)[0])
        # v51 (CL15-01) : l'identité attendue ne se compare plus à une ligne imprimée par le script (uid_hote_attendu sans effet) ;
        # elle se compare au propriétaire du témoin, lu sur l'hôte (verifier_temoin_identite)
        self.assertEqual(ev(SORTIE_PRIVILEGES_SAINE, uid_hote_attendu=64097), (True, "privilèges nuls"))
        # tous les autres refus de la v49 tiennent toujours (régression)
        self.assertFalse(ev(SORTIE_PRIVILEGES_SAINE.replace("UID=65534", "UID=0"))[0])
        # `disponible()` complète avec le faux bac : un artefact refuse, le cas sain passe, l'identité attendue est lue
        for avant, apres, motif in cas[:2] + cas[5:6] + cas[7:8] + cas[12:13] + cas[14:15] + cas[16:17]:
            ex = ExecuteurBacSimule(SORTIE_PRIVILEGES_SAINE.replace(avant, apres), delai_s=30.0)
            ok, m = ex.disponible()
            self.assertFalse(ok, avant)
            self.assertIn("étage refusé", m)
            self.assertEqual(len(ex.joues), 1)
        ok, m = ExecuteurBacSimule(SORTIE_PRIVILEGES_SAINE, delai_s=30.0).disponible()
        self.assertTrue(ok, m)
        for mot in ("/proc/sys en lecture seule", "borne de processus tenue", "/dev/shm borné", "ni sur l'hôte"):
            self.assertIn(mot, m)
        # la sonde jouée dans le bac est bien le script qui produit ces lignes
        for cle in ("TEMOIN-IDENTITE", tdm.TEMOIN_IDENTITE, "PROCSYS %s=", "kernel/core_pattern", "fs/suid_dumpable", "PROCSYS-OUVRABLES",
                    "USERNS-IMBRIQUE", "SHM", "PROCESSUS", "CapBnd", "DEV=", "SECCOMP=", "SYSV-SHM", "MEMFD", "IO-URING", "PTRACE", "MEMOIRE-BAC"):
            self.assertIn(cle, tdm.SONDE_PRIVILEGES)
        for absent in ("/proc/self/uid_map", "UID_HOTE", "GID_HOTE"):  # v51 (CL15-01) : l'identité de l'hôte ne se lit plus dans le bac
            self.assertNotIn(absent, tdm.SONDE_PRIVILEGES)
        self.assertNotIn("@", tdm.SONDE_PRIVILEGES)
        self.assertNotIn("write(", tdm.SONDE_PRIVILEGES.split("# CL14-01 : aucun réglage")[1].split("# CL14-03")[0])  # jamais d'écriture dans /proc/sys

    def test_v50_04_sonde_jouee_sous_un_utilisateur_sans_privilege_de_la_machine(self):
        """Le script de la sonde est joué **pour de vrai**, sous l'identité sans privilège `UID_ESSAI` (`setpriv`), dans un
        dossier provisoire, avec une borne de processus basse : il rend toutes les lignes attendues ; `/proc/sys` n'est ouvert en
        écriture nulle part (EACCES), le remontage est refusé, la borne de processus tient (refus avant la borne). Hors du bac,
        l'ensemble limite des capacités n'est pas vide : l'évaluation de la sonde **refuse** ce processus (artefact : un processus
        non confiné). Aucune écriture dans `/proc/sys` ni `/dev/shm`.
        v51 (CL15-01) : l'identité de l'hôte se lit sur le **témoin** créé par le script — propriétaire `UID_ESSAI` lu par le noyau
        (`verifier_temoin_identite` : accepté), artefact « témoin du superutilisateur » refusé ; plus de ligne `UID_HOTE`. (CL15-02, 06)
        hors du bac, sans filtre : `SECCOMP=0`, System V, `memfd`, `ptrace` réussis — refusés par l'évaluation ; joué dans un espace
        IPC jetable (`unshare --ipc`) : aucun objet System V de l'hôte ; `/dev` de la machine refusé à l'utilisateur (aucune écriture) ;
        l'artefact de mémoire du bac entier n'est **pas** joué hors du bac (aucune borne : « non-joue »)."""
        if not utilisateur_dedie_possible():
            exiger_essai_reel(self, "noyau superutilisateur avec setpriv requis pour jouer un processus sans privilège")
        python = "/usr/bin/python3"
        base = self.dossier_traversable()
        travail = os.path.join(base, "t")
        os.mkdir(travail)
        os.chown(travail, UID_ESSAI, UID_ESSAI)
        script = os.path.join(base, "sonde.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(tdm.sonde_pour(travail, fichier_shm=os.path.join(travail, "fichier-shm"), memoire_bac_octets=0))
        os.chmod(script, 0o644)
        enveloppe = ("import os, sys, resource\nassert os.getuid() != 0 and os.geteuid() != 0 and os.getgid() != 0\n"
                     "resource.setrlimit(resource.RLIMIT_NPROC, (40, 40))\nos.chdir(sys.argv[1])\n"
                     "exec(compile(open(sys.argv[2]).read(), 'sonde', 'exec'), {'__name__': '__main__'})\n")
        r = _subprocess.run(["unshare", "--ipc", "--", "setpriv", "--reuid", str(UID_ESSAI), "--regid", str(UID_ESSAI), "--clear-groups",
                             "--no-new-privs", "--", python, "-I", "-c", enveloppe, travail, script], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        valeurs = dict(l.rsplit("=", 1) for l in r.stdout.splitlines() if "=" in l)
        for cle in ("UID", "CapEff", "CapPrm", "CapBnd", "TEMOIN-IDENTITE", "REMONTAGE " + travail + "/tranche", "REMONTAGE /",
                    "ECRITURE-TRANCHE", "PROCSYS kernel/core_pattern", "PROCSYS fs/suid_dumpable", "PROCSYS vm/drop_caches",
                    "PROCSYS kernel/modprobe", "PROCSYS-OUVRABLES", "USERNS-IMBRIQUE", "SHM", "DEV", "SECCOMP", "SYSV-SHM", "SYSV-MSG",
                    "SYSV-SEM", "MEMFD", "IO-URING", "PTRACE", "PROCESSUS", "MEMOIRE-BAC"):
            self.assertIn(cle, valeurs, r.stdout)
        self.assertNotIn("UID_HOTE", valeurs)
        self.assertEqual(valeurs["UID"], str(UID_ESSAI))
        # v51 (CL15-01) : le témoin, lu par le noyau sur l'hôte : propriétaire UID_ESSAI ; accepté pour l'utilisateur dédié attendu
        temoin = os.path.join(travail, tdm.TEMOIN_IDENTITE)
        self.assertEqual(valeurs["TEMOIN-IDENTITE"], "cree")
        self.assertEqual((os.lstat(temoin).st_uid, os.lstat(temoin).st_gid), (UID_ESSAI, UID_ESSAI))
        self.assertTrue(tdm.verifier_temoin_identite(temoin, UID_ESSAI, UID_ESSAI)[0])
        ok, motif = tdm.verifier_temoin_identite(temoin, UID_ESSAI + 1, UID_ESSAI + 1)
        self.assertFalse(ok)
        self.assertIn("≠ attendue", motif)
        os.chown(temoin, 0, 0)  # artefact : le témoin d'un script qui aurait l'identité 0 de l'hôte
        ok, motif = tdm.verifier_temoin_identite(temoin, UID_ESSAI, UID_ESSAI)
        self.assertFalse(ok)
        self.assertIn("identité 0 de l'hôte", motif)
        self.assertEqual(int(valeurs["CapEff"], 16), 0)
        self.assertTrue(valeurs["PROCSYS kernel/core_pattern"].startswith("refus"), valeurs)
        self.assertTrue(all(valeurs["PROCSYS " + n].startswith("refus") for n in ("fs/suid_dumpable", "vm/drop_caches", "kernel/modprobe")))
        self.assertTrue(valeurs["REMONTAGE /"].startswith("refus"))
        self.assertTrue(valeurs["PROCESSUS"].startswith("refus-apres-"), valeurs["PROCESSUS"])  # la borne de 40 tient pour de vrai
        self.assertTrue(valeurs["SHM"].startswith("REUSSI"), valeurs["SHM"])  # un dossier ordinaire n'est pas borné : l'évaluation le dirait
        self.assertFalse(os.path.exists(os.path.join(travail, "fichier-shm")))
        # v51 : hors du bac, rien ne filtre les appels système (évaluation : refus) ; /dev de la machine n'est pas ouvert à l'utilisateur
        self.assertEqual(valeurs["SECCOMP"], "0")
        self.assertTrue(valeurs["DEV"].startswith("refus"), valeurs["DEV"])
        self.assertFalse(os.path.exists("/dev/sonde-dev"))
        for cle in ("SYSV-SHM", "SYSV-MSG", "SYSV-SEM", "MEMFD", "PTRACE"):
            self.assertEqual(valeurs[cle], "REUSSI", cle)
        self.assertTrue(valeurs["IO-URING"].startswith("atteint-errno-"), valeurs["IO-URING"])
        self.assertEqual(valeurs["MEMOIRE-BAC"], "non-joue")
        # artefact : ce processus n'est pas confiné par bwrap (ensemble limite des capacités non vide) → l'évaluation le refuse
        sortie_bac = r.stdout.replace(travail, "/travail")  # ce que la sonde imprimerait dans le bac (même dossier de travail)
        ok, motif = tdm.evaluer_sonde_privileges(sortie_bac, 0, "")
        self.assertFalse(ok)
        self.assertIn("capacités", motif)
        # avec les lignes que seul bwrap peut établir remplacées, le reste de la lecture reste cohérent
        corrige = sortie_bac.replace("CapBnd=" + valeurs["CapBnd"], "CapBnd=0000000000000000")
        corrige = corrige.replace("SHM=" + valeurs["SHM"], "SHM=refus-apres-32-Mo-errno-28")
        # hors du bac, un réglage de /proc/sys s'ouvre en écriture pour un utilisateur sans privilège (ici kernel/ns_last_pid, mode 0666,
        # propre à l'espace de processus) : c'est le montage en lecture seule de /proc/sys du bac qui le ferme ; l'évaluation le compte
        self.assertEqual(valeurs["PROCSYS-OUVRABLES"], "1", valeurs)
        ok, motif = tdm.evaluer_sonde_privileges(corrige, 0, "", uid_hote_attendu=UID_ESSAI, userns_permis=True)
        self.assertFalse(ok)
        self.assertIn("1 réglages de /proc/sys", motif)
        corrige = corrige.replace("PROCSYS-OUVRABLES=1", "PROCSYS-OUVRABLES=0")
        ok, motif = tdm.evaluer_sonde_privileges(corrige, 0, "", uid_hote_attendu=UID_ESSAI, userns_permis=True)
        self.assertFalse(ok)
        self.assertIn("filtre d'appels système absent", motif)  # v51 : la seule garde que le bac ajoute encore : le filtre
        corrige = corrige.replace("SECCOMP=0", "SECCOMP=2")
        corrige = corrige.replace("IO-URING=" + valeurs["IO-URING"], "IO-URING=REUSSI")  # une seule forme à remplacer ci-dessous
        for cle in ("SYSV-SHM", "SYSV-MSG", "SYSV-SEM", "MEMFD", "IO-URING", "PTRACE"):  # l'ordre de l'évaluation
            ok, motif = tdm.evaluer_sonde_privileges(corrige, 0, "", userns_permis=True, memoire_non_bornee_permise=True)
            self.assertFalse(ok)
            self.assertIn(cle, motif)
            corrige = corrige.replace(cle + "=REUSSI", cle + "=refus-errno-1")
        ok, motif = tdm.evaluer_sonde_privileges(corrige, 0, "", userns_permis=True)
        self.assertFalse(ok)
        self.assertIn("mémoire du bac entier n'est pas bornée", motif)  # « non-joue » n'est admis que sur demande explicite
        ok, motif = tdm.evaluer_sonde_privileges(corrige, 0, "", uid_hote_attendu=UID_ESSAI, userns_permis=True,
                                                 memoire_non_bornee_permise=True)
        self.assertTrue(ok, motif)  # tout le reste est cohérent : la seule différence avec le bac est ce que bwrap et le bac établissent

    def test_v50_05_plomberie_de_l_utilisateur_dedie_faux_bwrap_sous_setpriv(self):
        """Noyau superutilisateur et `setpriv` : le faux `bwrap` (aucun confinement) est lancé **sous l'utilisateur dédié** par
        l'exécuteur réel. Le script vu s'exécute sans privilège (uid et gid de l'utilisateur, groupes vides, `setuid(0)` refusé,
        `/proc/sys` fermé en écriture) ; le dossier de travail racine, le dossier de l'exécution et les fichiers que le noyau y
        écrit lui appartiennent (le noyau les écrit sans suivre de lien) ; **la borne de processus tient** (refus avant la
        borne, CL14-02) ; ce que le script laisse — fichier setuid, tube, lien, sous-dossier fermé — est vu par le noyau
        (le fichier setuid est refusé et consigné, jamais haché), puis tout le dossier est retiré, y compris le sous-dossier fermé."""
        if not utilisateur_dedie_possible():
            exiger_essai_reel(self, "noyau superutilisateur avec setpriv requis pour lancer un processus sous un utilisateur dédié")
        base = self.dossier_traversable()
        racine = os.path.join(base, "racine")
        os.mkdir(racine)
        os.chown(racine, UID_ESSAI, UID_ESSAI)
        os.chmod(racine, 0o700)
        faux = os.path.join(base, "faux-bwrap")
        journal = os.path.join(racine, "faux-bwrap.jsonl")
        with open(faux, "w", encoding="utf-8") as f:
            f.write(FAUX_BWRAP.replace("@PYTHON@", "/usr/bin/python3").replace("@JOURNAL@", repr(journal)))
        os.chmod(faux, 0o755)
        ex = tdm.ExecuteurBacASable(bwrap=faux, python="/usr/bin/python3", delai_s=60.0, processus_max=64, utilisateur_bac=UID_ESSAI,
                                    racine_travail=racine)
        self.assertIsNone(ex.verifier_outils())
        self.assertIsNone(ex.verifier_identite())  # le noyau (superutilisateur) a un utilisateur dédié, son dossier racine à lui
        etage = ex.ouvrir_racine_travail()
        self.assertEqual(os.lstat(etage).st_uid, UID_ESSAI)
        self.assertEqual(os.path.dirname(etage), racine)
        travail = os.path.join(etage, "fiche-execution-01")
        prop = ex.proprietaire_travail()
        tdm.creer_dossier_neuf(travail, prop)
        tdm.ecrire_dans_travail(travail, "tranche/a.csv", b"v\n1\n", prop)
        script = ("import os, signal\nprint('ids', os.getuid(), os.geteuid(), os.getgid(), os.getgroups())\n"
                  "try:\n    os.setuid(0)\n    print('SETUID0 REUSSI')\nexcept OSError as e:\n    print('SETUID0 refus', e.errno)\n"
                  "try:\n    os.close(os.open('/proc/sys/kernel/core_pattern', os.O_WRONLY | os.O_NONBLOCK))\n    print('PROCSYS OUVERT')\n"
                  "except OSError as e:\n    print('PROCSYS refus', e.errno)\n"
                  "print('lu', open('tranche/a.csv').read().split())\n"
                  "open('suid', 'w').write('x'); os.chmod('suid', 0o4755)\nos.mkfifo('tuyau'); os.symlink('/proc/self/environ', 'lien')\n"
                  "os.mkdir('ferme'); open('ferme/x', 'w').write('y'); os.chmod('ferme', 0)\n"
                  "enfants = []\ntry:\n    for _ in range(100):\n        pid = os.fork()\n        if pid == 0:\n            signal.pause()\n"
                  "            os._exit(0)\n        enfants.append(pid)\n    print('PROCESSUS REUSSI', len(enfants))\n"
                  "except OSError as e:\n    print('PROCESSUS refus', len(enfants) < 64, e.errno)\n"
                  "for pid in enfants:\n    os.kill(pid, 9)\nfor pid in enfants:\n    os.waitpid(pid, 0)\nprint('RESULTAT: 0.4')\n")
        chemin = os.path.join(travail, "script.py")
        tdm.ecrire_exclusif(chemin, script.encode("utf-8"), proprietaire=prop)
        for rel in ("script.py", "tranche", "tranche/a.csv", ""):
            st = os.lstat(os.path.join(travail, rel))
            self.assertEqual((st.st_uid, st.st_gid), (UID_ESSAI, UID_ESSAI), rel)
        r = ex.executer(chemin, travail, delai_s=60.0, dossier_capture=base)
        self.assertEqual((r["code"], r["delai_depasse"], r["limites_depassees"]), (0, False, []), r["stderr"])
        self.assertEqual(r["commande"][:8], ["/usr/bin/setpriv", "--reuid", str(UID_ESSAI), "--regid", str(UID_ESSAI), "--clear-groups",
                                              "--no-new-privs", "--"] if shutil.which("setpriv") == "/usr/bin/setpriv" else r["commande"][:8])
        sortie = r["stdout"]
        self.assertIn(f"ids {UID_ESSAI} {UID_ESSAI} {UID_ESSAI} []", sortie)
        self.assertIn("SETUID0 refus", sortie)
        self.assertIn("PROCSYS refus", sortie)
        self.assertIn("lu ['v', '1']", sortie)
        self.assertIn("PROCESSUS refus True", sortie)  # la borne de 64 processus tient pour l'utilisateur dédié
        self.assertNotIn("REUSSI", sortie)
        with open(journal, encoding="utf-8") as f:
            trace = [json.loads(l) for l in f if l.strip()][0]
        self.assertEqual(trace["rlimit_nproc"], [64, 64])
        # ce que le noyau voit, en superutilisateur, sans rien suivre
        inv = tdm.inventaire_travail(travail, sauf=("tranche",))
        self.assertEqual(inv.depassements, [])
        self.assertEqual(inv.interdits, ["suid"])
        self.assertEqual(inv.non_copies["suid"]["type"], "fichier setuid ou setgid (refusé)")
        self.assertEqual((inv.non_copies["tuyau"]["type"], inv.non_copies["lien"]["type"]), ("tube nommé", "lien"))
        self.assertIn("ferme/x", inv.fichiers)  # le noyau superutilisateur lit le sous-dossier fermé
        self.assertNotIn("suid", inv.fichiers)
        ok, motif = ex.fermer_racine_travail(etage)
        self.assertTrue(ok, motif)
        self.assertFalse(os.path.exists(etage))
        self.assertEqual(os.listdir(racine), ["faux-bwrap.jsonl"])  # rien d'autre ne reste
        # la sonde elle-même crée ses dossiers sous le dossier racine de l'utilisateur dédié, et les retire
        avant = sorted(os.listdir(racine))
        ok, motif = ex.disponible()
        self.assertFalse(ok)  # le faux bwrap ne confine rien : la sonde refuse (réseau non isolé)
        self.assertEqual(sorted(os.listdir(racine)), avant)

    def test_v50_06_creation_et_ecriture_remises_a_l_utilisateur(self):
        """`creer_dossier_neuf`, `ecrire_exclusif` et `ecrire_dans_travail` remettent ce qu'ils créent à l'identité donnée, sans
        suivre de lien (le fichier par descripteur, le dossier par `lchown`) ; sans identité, rien ne change ; un lien posé avant
        est toujours refusé et sa cible n'est pas touchée."""
        d = os.path.join(self.tmp, "w")
        os.makedirs(d)
        moi = (os.getuid(), os.getgid())
        tdm.creer_dossier_neuf(os.path.join(d, "a"), moi)
        tdm.ecrire_dans_travail(os.path.join(d, "a"), "tranche/x/f.csv", b"1", moi)
        tdm.ecrire_exclusif(os.path.join(d, "a", "g"), b"2", proprietaire=moi)
        for rel in ("", "tranche", "tranche/x", "tranche/x/f.csv", "g"):
            st = os.lstat(os.path.join(d, "a", rel))
            self.assertEqual((st.st_uid, st.st_gid), moi, rel)
        if os.geteuid() == 0:
            autre = (UID_ESSAI, UID_ESSAI)
            tdm.creer_dossier_neuf(os.path.join(d, "b"), autre)
            tdm.ecrire_dans_travail(os.path.join(d, "b"), "tranche/f.csv", b"1", autre)
            tdm.ecrire_exclusif(os.path.join(d, "b", "g"), b"2", proprietaire=autre)
            for rel in ("", "tranche", "tranche/f.csv", "g"):
                st = os.lstat(os.path.join(d, "b", rel))
                self.assertEqual((st.st_uid, st.st_gid), autre, rel)
            hote = os.path.join(self.tmp, "hote.txt")
            with open(hote, "w", encoding="utf-8") as f:
                f.write("HOTE")
            os.symlink(hote, os.path.join(d, "b", "lien"))
            with self.assertRaises(tdm.EtageInterrompu):
                tdm.ecrire_exclusif(os.path.join(d, "b", "lien"), b"X", proprietaire=autre)
            self.assertEqual(self.h().lire(hote), "HOTE")
            self.assertEqual(os.stat(hote).st_uid, 0)  # la cible du lien n'a pas changé de propriétaire
            os.symlink(hote, os.path.join(d, "lien-dossier"))
            with self.assertRaises(tdm.EtageInterrompu):
                tdm.creer_dossier_neuf(os.path.join(d, "lien-dossier"), autre)
            self.assertEqual(os.stat(hote).st_uid, 0)

    # --- CL14-02 : aucun fichier setuid ou setgid ; CL14-12 : dossier fermé ------------------------------------------------------------

    def test_v50_07_inventaire_fichiers_setuid_et_setgid_refuses_et_consignes(self):
        """Un fichier régulier setuid ou setgid n'est ni haché ni copié : il est consigné (`interdits`, `non_copies`) ; un fichier
        ordinaire est relevé ; dans l'étage, le script qui en crée un fait une exécution « échouée (fichier setuid ou setgid) »,
        un incident, un verdict « non concluant » même si le chiffre imprimé passe le seuil, et **aucun** fichier setuid ou setgid
        (ni lien, ni tube, ni prise) ne reste sous la sortie."""
        d = os.path.join(self.tmp, "inv")
        os.makedirs(d)
        for nom, mode in (("suid", 0o4755), ("sgid", 0o2755), ("les-deux", 0o6755), ("ordinaire", 0o644), ("exec", 0o755)):
            with open(os.path.join(d, nom), "wb") as f:
                f.write(b"x")
            os.chmod(os.path.join(d, nom), mode)
        inv = tdm.inventaire_travail(d)
        self.assertEqual(sorted(inv.interdits), ["les-deux", "sgid", "suid"])
        self.assertEqual(sorted(inv.fichiers), ["exec", "ordinaire"])
        self.assertTrue(all(inv.non_copies[n]["type"] == "fichier setuid ou setgid (refusé)" for n in inv.interdits))
        script = "import os\nopen('s', 'w').write('x')\nos.chmod('s', 0o4755)\nopen('ok.txt', 'w').write('ok')\nprint('RESULTAT: 0.9')\n"
        _, par = self.etage_simple("e50s", lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin())
        r = list(par.values())[0]
        e = r["executions"][0]
        self.assertEqual(e["statut"], "échouée (fichier setuid ou setgid)")
        self.assertEqual([p["chemin"] for p in e["fichiers_produits"]], ["ok.txt"])
        self.assertEqual([x["chemin"] for x in e["entrees_non_copiees"]], ["s"])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertTrue(r["incidents"] and "setuid" in r["incidents"][0]["type"])
        self.assertEqual(self.liens_tubes_et_prises(os.path.join(self.tmp, "e50s")), [])

    def test_v50_08_dossier_illisible_est_un_depassement_jamais_ignore(self):
        """CL14-12 : un dossier qui ne peut pas être parcouru (hors disparition en cours de route) est un dépassement, au parcours
        complet comme à la mesure rapide pendant l'exécution ; une entrée disparue est ignorée. Joué avec `scandir` et `stat`
        remplacés (partout), puis, noyau superutilisateur, **pour de vrai** sous l'identité sans privilège avec un
        sous-dossier de mode 000 — le noyau superutilisateur, lui, le lit ; enfin le retrait du dossier de travail rouvre le
        sous-dossier fermé."""
        d = os.path.join(self.tmp, "ill")
        os.makedirs(os.path.join(d, "sous"))
        with open(os.path.join(d, "sous", "f"), "wb") as f:
            f.write(b"x")
        # v51 (CL15-03) : le parcours ouvre chaque sous-dossier par descripteur (`_ouvrir_sous_dossier`) puis le lit par `scandir(fd)` :
        # l'artefact « illisible » (ou « disparu ») se pose sur l'ouverture, plus sur un `scandir` par chemin
        vrai_ouvrir = tdm._ouvrir_sous_dossier

        def scandir_refuse(fd_racine, relatif):
            if str(relatif).endswith("sous"):
                raise PermissionError(13, "Permission denied", relatif)
            return vrai_ouvrir(fd_racine, relatif)

        def scandir_disparu(fd_racine, relatif):
            if str(relatif).endswith("sous"):
                raise FileNotFoundError(2, "No such file or directory", relatif)
            return vrai_ouvrir(fd_racine, relatif)
        with _mock.patch.object(tdm, "_ouvrir_sous_dossier", scandir_refuse):
            inv = tdm.inventaire_travail(d)
            self.assertTrue(inv.depassements and "dossier illisible : non parcouru (sous" in inv.depassements[0], inv.depassements)
            self.assertTrue(tdm.mesure_rapide_travail(d))
        with _mock.patch.object(tdm, "_ouvrir_sous_dossier", scandir_disparu):
            inv = tdm.inventaire_travail(d)
            self.assertEqual(inv.depassements, [])  # disparu pendant le parcours : pas un dépassement
        self.assertEqual(tdm.inventaire_travail(d).depassements, [])
        self.assertEqual(sorted(tdm.inventaire_travail(d).fichiers), ["sous/f"])

        def jouer():
            travail = os.path.join(self.zone_ferme, "travail")
            os.mkdir(os.path.join(travail, "ferme"))
            with open(os.path.join(travail, "ferme", "secret.txt"), "w", encoding="utf-8") as f:
                f.write("x" * 100)
            os.chmod(os.path.join(travail, "ferme"), 0)
            inv_ = tdm.inventaire_travail(travail)
            rapide = tdm.mesure_rapide_travail(travail)
            ok, motif = tdm.supprimer_arbre(travail)
            return {"depassements": inv_.depassements, "fichiers": sorted(inv_.fichiers), "rapide": rapide, "retire": ok,
                    "existe": os.path.exists(travail), "motif": motif}
        self.base_ferme = self.dossier_traversable()
        self.zone_ferme = os.path.join(self.base_ferme, "zone")  # le dossier racine de l'utilisateur : lui seul peut y retirer son travail
        os.mkdir(self.zone_ferme)
        travail = os.path.join(self.zone_ferme, "travail")
        os.mkdir(travail)
        if os.geteuid() == 0:
            if not utilisateur_dedie_possible():
                exiger_essai_reel(self, "setpriv requis pour jouer la partie sous une identité sans privilège")
            os.chown(self.zone_ferme, UID_ESSAI, UID_ESSAI)
            os.chown(travail, UID_ESSAI, UID_ESSAI)
            # le noyau superutilisateur lit un sous-dossier fermé (mode 000) : contraste
            os.mkdir(os.path.join(self.base_ferme, "contraste"))
            os.mkdir(os.path.join(self.base_ferme, "contraste", "ferme"))
            with open(os.path.join(self.base_ferme, "contraste", "ferme", "s"), "wb") as f:
                f.write(b"s")
            os.chmod(os.path.join(self.base_ferme, "contraste", "ferme"), 0)
            inv = tdm.inventaire_travail(os.path.join(self.base_ferme, "contraste"))
            self.assertEqual((inv.depassements, sorted(inv.fichiers)), ([], ["ferme/s"]))
            resultat = en_tant_que(UID_ESSAI, jouer)
        else:
            resultat = jouer()
        self.assertNotIn("erreur", resultat, resultat)
        self.assertTrue(resultat["depassements"] and "dossier illisible" in resultat["depassements"][0], resultat)
        self.assertTrue(resultat["rapide"])
        self.assertEqual(resultat["fichiers"], [])  # le contenu du dossier fermé n'a pas été pris pour absent : il a été signalé
        self.assertTrue(resultat["retire"], resultat)  # le retrait rouvre le sous-dossier fermé
        self.assertFalse(resultat["existe"])

    # --- CL14-04, CL14-05 : la sortie scellée ne garde que les copies déclarées ------------------------------------------------------

    def test_v50_09_dossier_de_travail_hors_de_la_sortie_et_retire(self):
        """CL14-04 : après l'étage (avec des liens vers `/proc/self/environ` et un secret de l'hôte factice, un tube, une prise, un
        gros fichier), la sortie ne contient ni dossier de travail, ni lien, ni tube, ni prise, ni gros fichier ; le dossier
        provisoire où vivaient les dossiers de travail est retiré ; l'inventaire scellé garde noms, genres et empreintes. Même
        quand l'étage s'arrête en route (lien posé sur le dossier de l'exécution suivante), rien ne reste dans le dossier
        provisoire."""
        racine_sys = self.dossier_systeme_isole()
        secret = os.path.join(self.tmp, "secret-hote.txt")
        with open(secret, "w", encoding="utf-8") as f:
            f.write("SECRET-FACTICE-DE-L-HOTE")
        script = ("import os, socket\nos.symlink('/proc/self/environ', 'environ.txt')\n"
                  f"os.symlink({secret!r}, 'secret.txt')\nos.mkfifo('tuyau')\n"
                  "s = socket.socket(socket.AF_UNIX); s.bind('prise.sock'); s.close()\n"
                  "open('gros.bin', 'wb').write(b'x' * 3000000)\nopen('petit.txt', 'w').write('ok')\nprint('RESULTAT: 0.4')\n")
        with limite_de_temps(90):
            _, par = self.etage_simple("e50t", lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin())
        r = list(par.values())[0]
        e = r["executions"][0]
        self.assertEqual(e["statut"], "réussie")
        self.assertTrue(e["travail_retire"])
        sortie = os.path.join(self.tmp, "e50t")
        self.assertEqual(self.liens_tubes_et_prises(sortie), [])
        for base, dossiers, _ in os.walk(sortie):
            self.assertNotIn("travail", dossiers, base)
        self.assertNotIn(b"SECRET-FACTICE-DE-L-HOTE", TestV49.arbre_des_octets(self, sortie))
        taille = sum(os.path.getsize(os.path.join(b, n)) for b, _, noms in os.walk(sortie) for n in noms)
        self.assertLess(taille, 2_500_000)  # le fichier de 3 Mo n'est ni gardé ni copié (copie : 1 Mo au plus, il est plus gros)
        self.assertEqual(sorted(p["chemin"] for p in e["fichiers_produits"]), ["gros.bin", "petit.txt"])
        self.assertEqual({p["chemin"]: p["copie_scellee"] for p in e["fichiers_produits"]}, {"gros.bin": False, "petit.txt": True})
        self.assertEqual(sorted(x["chemin"] for x in e["entrees_non_copiees"]), ["environ.txt", "prise.sock", "secret.txt", "tuyau"])
        self.assertEqual(os.listdir(racine_sys), [])  # le dossier provisoire des dossiers de travail est retiré
        # l'étage s'arrête en route : le dossier provisoire est tout de même retiré
        cible = os.path.join(self.tmp, "cible-dossier")
        os.makedirs(cible)
        s2 = (f"import os\nfor n in os.listdir('..'):\n    if n.endswith('-execution-01'):\n"
              f"        os.symlink({cible!r}, '../' + n[:-len('-execution-01')] + '-execution-02')\nprint('RESULTAT: 0.4')\n")
        tours = {1: bloc_exp(executer(s2)), 2: bloc_exp(executer(script_resultat(0.5))), 3: bloc_fin()}
        h = self.h()
        ad = h.kit({"opus": [h.fiche("Arret")]}, exp=lambda f, t, c: tours[t])
        with self.assertRaisesRegex(idn.CourseInterrompue, "déjà présent"):
            h.course(ad, "e50u", etage=h.etage(nombre=1), proposeurs=self.PROP, juges=self.JUGES)
        self.assertEqual(os.listdir(cible), [])
        self.assertEqual(os.listdir(racine_sys), [])
        self.assertTrue(idn.verifier_scelle(os.path.join(self.tmp, "e50u", "manifeste-tests-de-mort.json")))

    def test_v50_10_noms_sha256_et_noms_voisins_ne_font_plus_tomber_l_etage(self):
        """CL14-05 : un script qui produit `r.txt` **et** `r.txt.sha256` (et `a`, un dossier `a.copie`, un fichier `a.copie.sha256`)
        ne fait plus tomber l'étage : chaque produit est copié et scellé sous `nom_copie` (suffixe `.copie` à chaque composant),
        chaque scellé se vérifie, la deuxième fiche est jouée. Propriétés de `nom_copie` : injective, jamais un compagnon
        `.sha256`, jamais le nom d'une autre copie ; l'ancien comportement (la v49 : `EcrasementInterdit`) est reproduit
        sur `ecrire_scelle` seul."""
        script = ("import os\nopen('r.txt', 'w').write('x')\nopen('r.txt.sha256', 'w').write('y')\nopen('a', 'w').write('1')\n"
                  "os.mkdir('a.copie')\nopen('a.copie/z', 'w').write('2')\nopen('a.copie.sha256', 'w').write('3')\nprint('RESULTAT: 0.4')\n")
        h = self.h()
        fiches = [h.fiche("Un"), h.fiche("Deux")]
        _, par = self.etage_simple("e50n", lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin(), nombre=2, fiches=fiches)
        self.assertEqual(len(par), 2)
        self.assertTrue(all(r["statut"] == "testée" and r["executions"][0]["statut"] == "réussie" for r in par.values()))
        r = list(par.values())[0]
        d = os.path.join(self.tmp, "e50n", "noyau", "tests-de-mort", r["identifiant_auteur"], "execution-01", "produits")
        attendu = ["a.copie", "a.copie.copie/z.copie", "a.copie.sha256.copie", "r.txt.copie", "r.txt.sha256.copie"]
        copies = sorted(os.path.relpath(os.path.join(b, n), d) for b, _, noms in os.walk(d) for n in noms
                        if os.path.exists(os.path.join(b, n + ".sha256")))
        self.assertEqual(copies, attendu)
        for rel in attendu:
            self.assertTrue(idn.verifier_scelle(os.path.join(d, rel)), rel)
        self.assertEqual({p["chemin"]: p["copie"] for p in r["executions"][0]["fichiers_produits"]},
                         {"a": "produits/a.copie", "a.copie/z": "produits/a.copie.copie/z.copie", "a.copie.sha256": "produits/a.copie.sha256.copie",
                          "r.txt": "produits/r.txt.copie", "r.txt.sha256": "produits/r.txt.sha256.copie"})
        # propriétés
        noms = ["r.txt", "r.txt.sha256", "a", "a.copie", "a.copie.sha256", "a/b", "a.copie/b", "a.copie/b.sha256", "d/e/f", "d.copie/e/f", "x.copie.copie"]
        images = [tdm.nom_copie(n) for n in noms]
        self.assertEqual(len(set(images)), len(noms))
        self.assertFalse(any(i.endswith(".sha256") for i in images))
        compagnons = {i + ".sha256" for i in images}
        self.assertFalse(compagnons & set(images))
        self.assertEqual(tdm.nom_copie("a/b.txt"), "a.copie/b.txt.copie")
        # reproduction de l'ancien défaut sur le primitif seul
        ancien = os.path.join(self.tmp, "ancien")
        idn.ecrire_scelle(os.path.join(ancien, "r.txt"), b"x")
        from pole.outils import EcrasementInterdit
        with self.assertRaises(EcrasementInterdit):
            idn.ecrire_scelle(os.path.join(ancien, "r.txt.sha256"), b"y")

    # --- CL14-06 : recalcul strict ---------------------------------------------------------------------------------------------------

    def test_v50_11_recalcul_strict_l_arrondi_ne_fait_jamais_franchir_le_seuil(self):
        """CL14-06 (R4, dans les deux sens) : un script qui imprime `0.5` pour une moyenne de 0,46 au seuil « au moins 0,5 » est
        concordant à l'arrondi près mais le verdict sur la valeur du noyau (« éliminée ») diffère de celui du chiffre imprimé
        (« survit ») : **non concluant** ; idem dans l'autre sens (`0.5` pour 0,54 au seuil « au moins 0,52 »). Les cas qui ne
        franchissent pas le seuil restent « recalculés ». L'étiquette dit ce qui est recalculé : la statistique déclarée par le
        script. Dans l'étage : écart type de `serie-b` (0,7071) imprimé `0.7` aux seuils 0,705 (deux sens de comparaison)."""
        tranche = _types.SimpleNamespace(fichiers={"f.csv": {"texte": "v\n0.4\n0.52\n"}, "g.csv": {"texte": "v\n0.54\n0.54\n"}})

        def jouer(fichier, seuil, comparateur, imprime, ligne=None):
            prereg = {"donnees": [{"chemin": "f.csv"}, {"chemin": "g.csv"}], "seuil": {"comparateur": comparateur, "valeur": seuil}}
            execs = [{"numero": 1, "lignes_calcul": [f"CALCUL: fichier={fichier}; colonne=v; statistique=moyenne"]}]
            meca = {"chiffre": imprime, "ligne": ligne or f"RESULTAT: {imprime}", "execution": 1}
            return tdm.recalcul_noyau(prereg, tranche, execs, meca)
        r = jouer("f.csv", 0.5, "≥", 0.5)  # moyenne 0,46 imprimée 0.5 : survit au chiffre imprimé, éliminée sur la valeur du noyau
        self.assertEqual((r["statut"], r["verdict_sur_valeur_noyau"], r["arrondi_franchit_le_seuil"]), ("concordant", "éliminée", True))
        self.assertAlmostEqual(r["valeur_noyau"], 0.46)
        self.assertIn("fait franchir le seuil", r["motif"])
        r = jouer("g.csv", 0.52, "≥", 0.5)  # moyenne 0,54 imprimée 0.5 : éliminée au chiffre imprimé, survit sur la valeur du noyau
        self.assertEqual((r["statut"], r["verdict_sur_valeur_noyau"], r["arrondi_franchit_le_seuil"]), ("concordant", "survit", True))
        r = jouer("f.csv", 0.3, "≥", 0.5)  # les deux survivent
        self.assertEqual((r["statut"], r["verdict_sur_valeur_noyau"], r["arrondi_franchit_le_seuil"]), ("concordant", "survit", False))
        self.assertEqual(r["etiquette"], tdm.ETIQUETTE_RECALCULE)
        r = jouer("f.csv", 0.5, "≥", 0.4)  # discordant : pas de verdict du noyau
        self.assertEqual((r["statut"], r["verdict_sur_valeur_noyau"], r["arrondi_franchit_le_seuil"]), ("discordant", None, False))
        self.assertEqual(tdm.ETIQUETTE_RECALCULE, "statistique déclarée par le script, recalculée par le noyau")
        self.assertNotEqual(tdm.ETIQUETTE_RECALCULE, "chiffre recalculé par le noyau")
        # dans l'étage
        h = self.h()
        script = script_calcul(0.7, "ecart_type", colonne="c", donnee="serie-b.csv")
        for nom, seuil, attendu_script in (("e50r1", "au moins 0,705", "éliminée"), ("e50r2", "au plus 0,705", "survit")):
            fiche = h.fiche("Bord", test=h.champ_test(donnees=("serie-b.csv",), seuil=seuil))
            ad, par = self.etage_simple(nom, lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin(), fiches=[fiche])
            r = list(par.values())[0]
            self.assertEqual(r["lecture_mecanique"]["verdict"], attendu_script, nom)  # ce que la v49 aurait prononcé, étiqueté « recalculé »
            self.assertEqual((r["verdict"], r["recalcul_noyau"]["statut"], r["recalcul_noyau"]["arrondi_franchit_le_seuil"]), ("non concluant", "concordant", True), nom)
            self.assertIn("recalcul strict", r["desaccord"], nom)
            materiau = self.h().lire(os.path.join(self.tmp, nom, "noyau", "tests-de-mort", "materiau-tests-de-mort.md"))
            self.assertIn("- Bord (rang 1) : non concluant", materiau)
            self.assertNotIn("recalculée par le noyau", materiau)
        # le cas qui ne franchit pas le seuil reste « survit » avec la nouvelle étiquette
        fiche = h.fiche("Franc", test=h.champ_test(donnees=("serie-b.csv",), seuil="au moins 0,5"))
        ad, par = self.etage_simple("e50r3", lambda f, t, c: bloc_exp(executer(script)) if t == 1 else bloc_fin(), fiches=[fiche])
        r = list(par.values())[0]
        self.assertEqual((r["verdict"], r["fiabilite_du_chiffre"]), ("survit", tdm.ETIQUETTE_RECALCULE))
        materiau = self.h().lire(os.path.join(self.tmp, "e50r3", "noyau", "tests-de-mort", "materiau-tests-de-mort.md"))
        self.assertIn("survit (statistique déclarée par le script, recalculée par le noyau)", materiau)

    # --- CL14-08, CL14-09 : Argon, le modèle servi ------------------------------------------------------------------------------------

    def test_v50_12_suffixe_de_date_strict_et_liste_explicite(self):
        """CL14-08 : le modèle servi est le modèle demandé, ou suivi de `-AAAAMMJJ` (date plausible) exactement, ou dans la liste
        explicite des identifiants permis pour ce modèle ; `-mini`, `-lite`, `-latest`, un préfixe `models/`, un suffixe de date
        d'un autre format, un mois ou un jour impossible sont des écarts (R-764). Le noyau et les défenses génériques (course,
        étage, kit) appliquent la même règle."""
        from pole.adaptateurs import AdaptateurCommandeExterne, controle_modele_resultat, modele_conforme
        for demande, servi, attendu in (
                ("claude-opus-5-5", "claude-opus-5-5", True), ("claude-opus-5-5", "claude-opus-5-5-20261001", True),
                ("claude-opus-5-5", "claude-opus-5-5-mini", False), ("claude-opus-5-5", "claude-opus-5-5-lite", False),
                ("claude-opus-5-5", "claude-opus-5-5-latest", False), ("claude-opus-5-5", "claude-opus-5-5-2026", False),
                ("claude-opus-5-5", "claude-opus-5-5-202610011", False), ("claude-opus-5-5", "claude-opus-5-5-20261301", False),
                ("claude-opus-5-5", "claude-opus-5-5-20261032", False), ("claude-opus-5-5", "claude-opus-5-5-2026-10-01", False),
                ("claude-opus-5-5", "claude-opus-5-5-20261001-mini", False), ("claude-opus-5-5", "claude-opus-5-50", False),
                ("claude-opus-5-5", "x-claude-opus-5-5", False), ("gemini-4-argon", "gemini-4-argon-lite", False),
                ("gemini-4-argon", "models/gemini-4-argon", False), ("gemini-4-argon", "gemini-4-argon-20261001", True),
                ("gemini-4-argon", "", False), ("", "gemini-4-argon", False), ("gemini-4-argon", None, False)):
            self.assertEqual(modele_conforme(demande, servi), attendu, (demande, servi))
        self.assertTrue(modele_conforme("gemini-4-argon", "models/gemini-4-argon", ("models/gemini-4-argon",)))
        self.assertFalse(modele_conforme("gemini-4-argon", "models/gemini-4-argon-lite", ("models/gemini-4-argon",)))
        self.assertTrue(AdaptateurClaudeSDK.modele_conforme("claude-opus-5-5", "claude-opus-5-5-20261001"))
        self.assertFalse(AdaptateurClaudeSDK.modele_conforme("claude-opus-5-5", "claude-opus-5-5-mini"))
        res = _types.SimpleNamespace(modele_servi="gemini-4-argon-lite")
        self.assertIsNotNone(controle_modele_resultat("gemini-4-argon", res))
        res = _types.SimpleNamespace(modele_servi="models/gemini-4-argon")
        self.assertIsNotNone(controle_modele_resultat("gemini-4-argon", res))
        self.assertIsNone(controle_modele_resultat("gemini-4-argon", res, {"gemini-4-argon": ("models/gemini-4-argon",)}))
        # la commande externe : liste explicite par modèle demandé
        ad = AdaptateurCommandeExterne(TestV49.commande_argon(self, {"modele_servi": "models/gemini-4-argon"}), environnement={},
                                       exiger_modele_servi=True)
        self.assertEqual(ad.lancer("proposeur_ideation", "c", self.tmp, 1.0, 1, modele="gemini-4-argon").statut, "refus")
        ad = AdaptateurCommandeExterne(TestV49.commande_argon(self, {"modele_servi": "models/gemini-4-argon"}), environnement={},
                                       exiger_modele_servi=True, modeles_servis_permis={"gemini-4-argon": ["models/gemini-4-argon"]})
        self.assertEqual(ad.lancer("proposeur_ideation", "c", self.tmp, 1.0, 1, modele="gemini-4-argon").statut, "ok")
        self.assertEqual(ad.description()["modeles_servis_permis"], {"gemini-4-argon": ["models/gemini-4-argon"]})
        with self.assertRaises(ValueError):
            AdaptateurCommandeExterne(["x"], modeles_servis_permis={"a": "pas-une-liste"})
        with self.assertRaises(ValueError):
            AdaptateurCommandeExterne(["x"], modeles_servis_permis={"": ["a"]})

    def test_v50_13_ecart_de_modele_vu_par_la_commande_est_un_refus(self):
        """CL14-09 : la commande qui voit l'écart elle-même (code 5, `modele_servi` dans la ligne) rend un « refus » (jamais le
        texte, dépense comptée à part), comme sur un code 0 ; une erreur ordinaire (code ≠ 0, ligne sans `modele_servi`, ou avec
        le modèle demandé) reste une « erreur » ; un refus dit par la commande avec un code ≠ 0 est un refus sans dépense
        « non autorisée » ; dans l'étage, l'écart arrête l'étage, la sortie est mise à l'écart et le manifeste l'écrit."""
        from pole.adaptateurs import AdaptateurCommandeExterne
        modele = "argon-x"

        def jouer(extra, code, exiger=True):
            chemin = os.path.join(self.tmp, f"argon-{abs(hash((repr(extra), code, exiger)))}.py")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(SCRIPT_ARGON_CODE % (repr(extra), code))
            ad = AdaptateurCommandeExterne([sys.executable, "-I", chemin], environnement={}, exiger_modele_servi=exiger)
            return ad.lancer("proposeur_ideation", "consigne", self.tmp, 1.0, 1, modele=modele)
        r = jouer({"modele_servi": "argon-y"}, 5)
        self.assertEqual((r.statut, r.texte_final, r.cout_declare_usd, r.depense_modele_non_autorise_usd), ("refus", "", 0.2, 0.2))
        self.assertEqual((r.refus["evenement"], r.modele_servi), ("commande.modele_servi", "argon-y"))
        self.assertIn("code 5", r.erreur)
        r = jouer({"modele_servi": "argon-y"}, 0)  # même sortie, code 0 : le comportement de la v49
        self.assertEqual((r.statut, r.depense_modele_non_autorise_usd), ("refus", 0.2))
        for extra, code in (({}, 5), ({"modele_servi": modele}, 5), ({"modele_servi": modele + "-20261001"}, 1)):
            r = jouer(extra, code)
            self.assertEqual((r.statut, r.refus, r.texte_final), ("erreur", None, ""), (extra, code))
            self.assertEqual(r.cout_declare_usd, 0.2)
        r = jouer({"refus": True}, 5)
        self.assertEqual((r.statut, r.refus["evenement"], r.depense_modele_non_autorise_usd), ("refus", "commande.refus", 0.0))
        r = jouer({"stop_reason": "refusal"}, 2)
        self.assertEqual((r.statut, r.depense_modele_non_autorise_usd), ("refus", 0.0))
        # non exigé : une ligne sans modele_servi reste une erreur ordinaire
        self.assertEqual(jouer({}, 5, exiger=False).statut, "erreur")
        self.assertEqual(jouer({"modele_servi": "argon-y"}, 5, exiger=False).statut, "refus")

    # --- CL14-07 : le lanceur ---------------------------------------------------------------------------------------------------------

    def test_v50_14_lanceur_argon_experimentateur_et_etiquette_refuses_avant_tout_appel(self):
        """CL14-07 : avec le moteur réel, un rôle externe dont le modèle n'est pas celui que la commande demande toujours
        (`gemini-4-argon`, ou `--modele-commande-externe`) est refusé avant tout appel ; `--experimentateur-externe` est refusé
        (dit : non fonctionnel avec la commande réelle, qui n'accepte que le proposeur et le juge) tant que
        `--commande-externe-accepte-experimentateur` n'atteste pas une commande qui l'accepte ; avec le moteur simulé rien ne
        change. Options de la v50 refusées hors de l'étage, avec le bac factice, ou sans expérimentateur externe ; l'exécuteur
        du lanceur reçoit l'utilisateur dédié, le dossier racine et la demande d'espaces imbriqués."""
        import contextlib
        import io
        lanceur = TestLanceurV37("test_options_refusees").lanceur()

        def args(**kw):
            base = dict(moteur="claude-sdk", commande_externe="cmd", experimentateur_externe=None, modele_commande_externe=None,
                        commande_externe_accepte_experimentateur=False, commande_externe_lit_modele=False)
            base.update(kw)
            return _types.SimpleNamespace(**base)
        verifier = lanceur.verifier_commande_externe_reelle
        verifier(args(), [("argon", "gemini-4-argon")], [("argon-j", "gemini-4-argon")])
        with self.assertRaisesRegex(idn.CourseInterrompue, "gemini-argon"):
            verifier(args(), [("argon", "gemini-argon")], [("argon-j", "gemini-4-argon")])
        with self.assertRaisesRegex(idn.CourseInterrompue, "refusé avant tout appel"):
            verifier(args(), [], [("argon-j", "gemini-argon")])
        # v51 (CL15-05) : une autre étiquette déclarée n'est admise que si la commande est attestée lire le modèle demandé
        with self.assertRaisesRegex(idn.CourseInterrompue, "CL15-05"):
            verifier(args(modele_commande_externe="gemini-argon"), [("argon", "gemini-argon")], [("argon-j", "gemini-argon")])
        verifier(args(modele_commande_externe="gemini-4-argon"), [("argon", "gemini-4-argon")], [])  # celle de la commande v2 : sans effet
        verifier(args(modele_commande_externe="gemini-argon", commande_externe_lit_modele=True), [("argon", "gemini-argon")],
                 [("argon-j", "gemini-argon")])  # autre commande, attestée
        verifier(args(moteur="simule"), [("argon", "gemini-argon")], [])  # moteur simulé : aucune contrainte
        verifier(args(commande_externe=None), [("argon", "gemini-argon")], [])
        with self.assertRaises(idn.CourseInterrompue) as cm:
            verifier(args(experimentateur_externe="argon-e=gemini-4-argon"), [], [])
        self.assertIn("NON FONCTIONNEL", str(cm.exception))
        self.assertIn("commande_argon_v2.py", str(cm.exception))
        self.assertIn("experimentateur_test", str(cm.exception))
        self.assertIn("code 2", str(cm.exception))
        verifier(args(experimentateur_externe="argon-e=gemini-4-argon", commande_externe_accepte_experimentateur=True), [], [])
        verifier(args(moteur="simule", experimentateur_externe="argon-e=gemini-argon"), [], [])
        with self.assertRaises(idn.CourseInterrompue):  # l'expérimentateur externe porte lui aussi l'étiquette de la commande
            verifier(args(experimentateur_externe="argon-e=gemini-argon", commande_externe_accepte_experimentateur=True), [], [])
        # arguments de la ligne de commande
        a = lanceur.construire_analyseur()
        analyse = a.parse_args(["S", "--tests-de-mort", "1", "--utilisateur-bac", "64097", "--dossier-travail-bac", "/srv/bac",
                                "--userns-imbriques-permis", "--modele-servi-externe-permis", "gemini-4-argon=models/gemini-4-argon"])
        self.assertEqual((analyse.utilisateur_bac, analyse.dossier_travail_bac, analyse.userns_imbriques_permis, analyse.modele_servi_externe_permis),
                         ("64097", "/srv/bac", True, ["gemini-4-argon=models/gemini-4-argon"]))
        analyse.experimentateur, analyse.lecteur_test, analyse.tranche_exploratoire = "e=claude-opus-5-5", "l=claude-fable-5-1", "t"
        reglages = lanceur.reglages_tests_de_mort(analyse)
        self.assertIsInstance(reglages["executeur"], tdm.ExecuteurBacASable)
        self.assertEqual(reglages["executeur"].utilisateur_bac[:2], (64097, 64097))
        self.assertEqual(reglages["executeur"].racine_travail, "/srv/bac")
        self.assertTrue(reglages["executeur"].userns_imbriques_permis)
        analyse.utilisateur_bac = "0"
        with self.assertRaisesRegex(idn.CourseInterrompue, "bac à sable de l'étage"):
            lanceur.reglages_tests_de_mort(analyse)
        analyse.utilisateur_bac, analyse.dossier_travail_bac, analyse.userns_imbriques_permis = None, None, False
        self.assertIsNone(lanceur.reglages_tests_de_mort(analyse)["executeur"])  # défaut inchangé : le cœur crée l'exécuteur
        adaptateur = lanceur.adaptateur_commande_externe(_types.SimpleNamespace(
            commande_externe="x", delai_commande_s=5.0, variable_transmise=[], moteur="claude-sdk",
            modele_servi_externe_permis=["gemini-4-argon=models/gemini-4-argon", "gemini-4-argon=gemini-4-argon-x"]))
        self.assertEqual(adaptateur.modeles_servis_permis, {"gemini-4-argon": ("models/gemini-4-argon", "gemini-4-argon-x")})
        with self.assertRaises(idn.CourseInterrompue):
            lanceur.adaptateur_commande_externe(_types.SimpleNamespace(
                commande_externe="x", delai_commande_s=5.0, variable_transmise=[], moteur="simule", modele_servi_externe_permis=["sans-egal"]))
        # refus de la ligne de commande : options de la v50 hors de l'étage, avec le bac factice, ou sans expérimentateur externe
        base = [os.path.join(self.tmp, "s"), "--liste-blanche", "l", "--question", "q", "--temoins", "t"]
        etage = ["--tests-de-mort", "1", "--tranche-exploratoire", "t", "--experimentateur", "e=m", "--lecteur-test", "l=m"]
        for options, message in ((["--utilisateur-bac", "64097"], "--utilisateur-bac"), (["--dossier-travail-bac", "/srv/bac"], "--dossier-travail-bac"),
                                 (["--userns-imbriques-permis"], "--userns-imbriques-permis"),
                                 (["--commande-externe-accepte-experimentateur"], "--commande-externe-accepte-experimentateur"),
                                 (etage + ["--executeur-tests", "factice", "--utilisateur-bac", "64097"], "ne valent que pour le bac"),
                                 (etage + ["--commande-externe-accepte-experimentateur"], "ne se donne qu'avec --experimentateur-externe")):
            erreur = io.StringIO()
            with contextlib.redirect_stderr(erreur):
                with self.assertRaises(SystemExit, msg=options) as cm:
                    lanceur.principal(base + options)
            self.assertEqual(cm.exception.code, 2, options)
            self.assertIn(message, erreur.getvalue(), options)

    # --- CL14-11 : essais réels, seulement avec `bwrap` ----------------------------------------------------------------------------------

    @essai_reel_bwrap  # v51 (CL15-04) : sans bwrap, échec — jamais ignoré en silence
    def test_v50_15_bac_reel_evasions_de_cl14_rejouees_cibles_factices(self):
        """Seulement avec `bwrap` (et, noyau superutilisateur, l'utilisateur dédié des variables d'environnement) : les sondes de
        CL14 jouées dans le vrai bac **sans rien écrire dans l'hôte** : ouverture en écriture de `/proc/sys` (jamais d'écriture),
        identité de l'hôte lue dans `uid_map`, espace d'utilisateurs imbriqué, `/dev/shm` borné, borne de processus (tient avant
        1 100 processus), fichier setuid (refusé et consigné par le noyau), liens, tubes, prises, noms `.sha256`, dossier de
        travail retiré. Non joué sur la machine de la v50 (pas de `bwrap`) : **à rejouer** avant tout GO de l'étage."""
        vrai = executeur_reel(self, 30.0)
        ok, motif = vrai.disponible()
        self.assertTrue(ok, motif)
        for mot in ("/proc/sys en lecture seule", "espaces d'utilisateurs imbriqués refusés", "/dev/shm borné", "borne de processus tenue"):
            self.assertIn(mot, motif)
        racine_sys = self.dossier_systeme_isole() if os.geteuid() != 0 else None
        sonde = ("import ctypes, os, resource, signal\n"
                 "def essai(nom, f):\n"
                 "    try:\n        r = f()\n    except BaseException as e:\n        print(nom, 'refus', type(e).__name__)\n"
                 "    else:\n        print(nom, 'REUSSI', r)\n"
                 "def ouvrir(chemin):\n    os.close(os.open(chemin, os.O_WRONLY | os.O_NONBLOCK))\n    return 'ouvert'\n"
                 "def imbrique():\n    pid = os.fork()\n    if pid == 0:\n"
                 "        os._exit(0 if ctypes.CDLL(None).unshare(0x10000000) == 0 else 1)\n    return os.waitpid(pid, 0)[1] == 0 or (_ for _ in ()).throw(OSError('refus'))\n"
                 "def shm():\n    fd = os.open('/dev/shm/essai-v50', os.O_WRONLY | os.O_CREAT | os.O_EXCL)\n    try:\n"
                 "        for _ in range(64):\n            os.write(fd, b'x' * (1 << 20))\n    finally:\n        os.close(fd)\n        os.unlink('/dev/shm/essai-v50')\n    return '64 Mo'\n"
                 "def bombe():\n    e = []\n    try:\n        for _ in range(1100):\n            pid = os.fork()\n            if pid == 0:\n"
                 "                signal.pause()\n                os._exit(0)\n            e.append(pid)\n    finally:\n"
                 "        for pid in e:\n            os.kill(pid, 9)\n        for pid in e:\n            os.waitpid(pid, 0)\n    return len(e)\n"
                 "essai('proc-sys-core-pattern', lambda: ouvrir('/proc/sys/kernel/core_pattern'))\n"
                 "essai('proc-sys-drop-caches', lambda: ouvrir('/proc/sys/vm/drop_caches'))\n"
                 "print('uid_map', open('/proc/self/uid_map').read().split())\n"
                 "essai('espace-imbrique', imbrique)\nessai('shm-64-Mo', shm)\nessai('bombe-1100', bombe)\n"
                 "open('suid', 'w').write('x'); os.chmod('suid', 0o4755)\nopen('r.txt', 'w').write('1'); open('r.txt.sha256', 'w').write('2')\n"
                 "os.symlink('/proc/self/environ', 'environ.txt'); os.mkfifo('tuyau')\nprint('RESULTAT: 0.4')\n")
        proprietaires = []  # v51 (CL15-04) : propriétaire, vu de l'hôte, d'un fichier créé par le script (avant le retrait du dossier)
        vrai_supprimer = tdm.supprimer_arbre

        def supprimer_en_notant(chemin):
            try:
                st = os.lstat(os.path.join(chemin, "r.txt"))
                proprietaires.append((st.st_uid, st.st_gid))
            except OSError:
                pass
            return vrai_supprimer(chemin)
        with _mock.patch.object(tdm, "supprimer_arbre", supprimer_en_notant):
            _, par = self.etage_simple("e50v", lambda f, t, c: bloc_exp(executer(sonde)) if t == 1 else bloc_fin(),
                                       executeur=vrai, delai_execution_s=30.0)
        r = list(par.values())[0]
        e = r["executions"][0]
        d = os.path.join(self.tmp, "e50v", "noyau", "tests-de-mort", list(par)[0], "execution-01")
        sortie = self.h().lire(os.path.join(d, "stdout.txt"))
        for ligne in sortie.splitlines():
            self.assertNotIn(" REUSSI", ligne)
        for nom in ("proc-sys-core-pattern", "proc-sys-drop-caches", "espace-imbrique", "shm-64-Mo", "bombe-1100"):
            self.assertIn(f"{nom} refus", sortie)
        # v51 (CL15-04) : l'assertion de la v50 (« '0', '0', '1' » absent de uid_map) ne pouvait pas échouer (le bac imprime toujours
        # ['65534', '0', '1']) ; l'identité de l'hôte se lit sur le propriétaire, vu de l'hôte, d'un fichier créé par le script
        self.assertIn("['65534', '0', '1']", sortie)  # ce que montre uid_map dans le bac : l'espace intermédiaire de bwrap (CL15-01)
        attendu = (vrai.uid_hote_attendu(), vrai.gid_hote_attendu())
        self.assertEqual(proprietaires, [attendu])
        self.assertNotIn(0, attendu)
        self.assertEqual(e["statut"], "échouée (fichier setuid ou setgid)")
        self.assertEqual(r["verdict"], "non concluant")
        self.assertEqual(self.liens_tubes_et_prises(os.path.join(self.tmp, "e50v")), [])
        self.assertEqual(sorted(os.listdir(os.path.join(d, "produits"))), ["r.txt.copie", "r.txt.copie.sha256", "r.txt.sha256.copie", "r.txt.sha256.copie.sha256"])
        if racine_sys is not None:
            self.assertEqual(os.listdir(racine_sys), [])

    @essai_reel_bwrap  # v51 (CL15-04) : sans bwrap, échec — jamais ignoré en silence
    def test_v50_16_bac_reel_liens_tube_et_noms_sha256_par_l_etage_entier(self):
        """Seulement avec `bwrap` : les essais `test_v49_06` et `test_v49_07` joués avec le **vrai** bac (CL14-11) — un lien posé sur
        `script.py` n'écrase rien, les produits réguliers sont copiés, liens et tubes consignés sans blocage."""
        vrai = executeur_reel(self, 30.0)
        hote = os.path.join(self.tmp, "hote.txt")
        with open(hote, "w", encoding="utf-8") as f:
            f.write("CONTENU ORIGINAL DE L'HOTE")
        s1 = f"import os\nos.remove('script.py')\nos.symlink({hote!r}, 'script.py')\nprint('RESULTAT: 0.4')\n"
        tours = {1: bloc_exp(executer(s1)), 2: bloc_exp(executer("import os\nos.mkfifo('tuyau')\nopen('ok.txt', 'w').write('x')\nprint('RESULTAT: 0.5')\n")),
                 3: bloc_fin()}
        with limite_de_temps(120):
            _, par = self.etage_simple("e50w", lambda f, t, c: tours[t], executeur=vrai, delai_execution_s=30.0)
        r = list(par.values())[0]
        self.assertEqual(self.h().lire(hote), "CONTENU ORIGINAL DE L'HOTE")
        e1, e2 = r["executions"]
        self.assertEqual((e1["statut"], e2["statut"]), ("réussie", "réussie"))
        self.assertEqual([x["type"] for x in e1["entrees_non_copiees"]], ["lien"])
        self.assertEqual([x["type"] for x in e2["entrees_non_copiees"]], ["tube nommé"])
        self.assertEqual([p["chemin"] for p in e2["fichiers_produits"]], ["ok.txt"])
        self.assertEqual(self.liens_tubes_et_prises(os.path.join(self.tmp, "e50w")), [])

    # --- provenance (R12) ------------------------------------------------------------------------------------------------------------------------------

    def test_v50_17_provenance_du_code_modifie_dit_au_lisezmoi(self):
        """R12 : le LISEZMOI de la v50 liste **chaque fichier de code modifié** avec l'empreinte v49 (celle de
        `EMPREINTES-orchestrateur-pole-v7-v49.txt`, vérifiée) et l'empreinte v50 (celle du disque, sauf le fichier d'essais, qui ne
        peut pas contenir sa propre empreinte stable) ; tout fichier de l'empreinte v49 dont le contenu a changé figure dans le
        tableau ; aucun fichier du tableau n'est inchangé ; le code de la v49 est récupérable dans `CODE-orchestrateur-pole-v7-v49.zip`
        (empreintes égales à celles de la liste v49)."""
        import zipfile
        from essais.test_v47_relais_moisson import RACINE
        lisezmoi = os.path.join(RACINE, "LISEZMOI-orchestrateur-pole-v7-v50.md")
        self.assertTrue(os.path.exists(lisezmoi), "LISEZMOI de la v50 absent")
        v49 = {}
        with open(os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v49.txt"), encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip():
                    empreinte, chemin = ligne.split(None, 1)
                    v49[chemin.strip()] = empreinte
        tableau = {}
        with open(lisezmoi, encoding="utf-8") as f:
            for ligne in f:
                m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|\s*`([0-9a-f]{64})`\s*\|", ligne)
                if m:
                    tableau[m.group(1)] = (m.group(2), m.group(3))
        self.assertTrue(tableau, "tableau de provenance absent du LISEZMOI")
        moi = "essais/test_v7_ideation.py"
        self.assertIn(moi, tableau)
        # v51 (R12) : l'arbre de la v50 n'est plus le disque (versions 2 à côté, fichier d'essais v1 retiré de l'arbre actif) : il se lit
        # dans son archive `CODE-orchestrateur-pole-v7-v50.zip`, dont chaque fichier est égal à `EMPREINTES-orchestrateur-pole-v7-v50.txt`
        v50 = {}
        with open(os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v50.txt"), encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip():
                    empreinte, chemin = ligne.split(None, 1)
                    v50[chemin.strip()] = empreinte
        archive_v50 = zipfile.ZipFile(os.path.join(RACINE, "CODE-orchestrateur-pole-v7-v50.zip"))
        self.addCleanup(archive_v50.close)

        def contenu_v50(chemin):
            if chemin in archive_v50.namelist():
                return archive_v50.read(chemin)
            return open(os.path.join(RACINE, chemin), "rb").read()
        for chemin, (ancienne, nouvelle) in tableau.items():
            self.assertEqual(ancienne, v49[chemin], f"empreinte v49 de {chemin} ≠ EMPREINTES v49")
            self.assertNotEqual(ancienne, nouvelle, f"{chemin} : listé mais inchangé")
            self.assertEqual(nouvelle, v50[chemin], f"{chemin} : empreinte v50 ≠ EMPREINTES v50")
            self.assertEqual(nouvelle, hashlib.sha256(contenu_v50(chemin)).hexdigest(), f"{chemin} : empreinte v50 ≠ archive de la v50")
        with zipfile.ZipFile(os.path.join(RACINE, "CODE-orchestrateur-pole-v7-v49.zip")) as z:
            for chemin in tableau:
                self.assertEqual(hashlib.sha256(z.read(chemin)).hexdigest(), v49[chemin], f"{chemin} : le lot zippé de la v49 diffère")
        for chemin, empreinte in v49.items():
            if chemin.startswith(("LISEZMOI", "EMPREINTES")):
                self.assertEqual(hashlib.sha256(open(os.path.join(RACINE, chemin), "rb").read()).hexdigest(), empreinte, f"{chemin} : fichier scellé modifié")
                continue
            actuelle = hashlib.sha256(contenu_v50(chemin)).hexdigest()
            if actuelle != empreinte:
                self.assertIn(chemin, tableau, f"{chemin} a changé depuis la v49 et n'est pas dans le tableau de provenance")


def tdm_roles():
    from pole.adaptateurs import ROLES_ETAGE_TESTS
    return ROLES_ETAGE_TESTS


if __name__ == "__main__":
    unittest.main()
