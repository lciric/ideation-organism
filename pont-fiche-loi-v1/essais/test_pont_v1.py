"""Essais du pont fiche de course -> fiche-loi (v1). Modèles factices injectés ; aucun réseau, aucun appel de modèle.

Chaque garde a un cas sain et au moins un cas artefact (R5). Le dernier groupe (compatibilité avec le vrai code de
l'orchestrateur v56) ne se joue que si `PONT_POLE_V56` désigne le dossier où l'archive v56 a été dépliée ; sinon il est
ignoré avec son motif (jamais en silence).

Jouer : python3 -I -B -m pytest -q -p no:cacheprovider CHEMIN/essais/test_pont_v1.py
"""

import copy
import json
import math
import os
import random
import sys

import pytest

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))

import pont_v1 as pv  # noqa: E402

TRAITS = ["longueur", "actions_valides", "dispersion"]
CATALOGUE = {
    "banques": {"banque-demo": {"traits": TRAITS, "sous_populations": 2,
                                "moniteurs": {"juge:RIGUEUR": {"nombre_issues": 3, "epreuve": 2000},
                                              "juge:BALANCE": {"nombre_issues": 2, "epreuve": 40}}}},
    "banques_scores": {"scores-demo": {"cellules": ["S_blanche", "B_noire"], "epreuve_unites": 600}},
}
CONNU = {"type": "softmax", "poids": [[0.2, 0.0, 0.0], [0.0, 0.1, 0.0], [-0.2, 0.0, 0.1]], "biais": [0.1, 0.0, -0.1]}
CANARI = "CANARI-7f3a9c"

# Fiche au format du texte I de la course 2 (noms de champs illustratifs : la correspondance réelle est injectée).
FICHE = {
    "axe": "3",
    "hypothese": "La note de rigueur du juge dépend de la dispersion des jetons par action, au-delà de la longueur.",
    "prediction": {"metrique": "log-rapport de cotes de la note haute", "valeur": "0,8 par écart type de dispersion",
                   "unite": "nat"},
    "critere_de_mort": "log-rapport de cotes inférieur à 0,2 sur 300 épisodes",
    "statistique": "écart type des jetons par action, par épisode",
    "comparaison": "rappel à 1 % de 0,45 contre 0,38 pour le comparateur boîte noire",
    "comparaison_forte": "rappel à 1 % de 0,60 contre 0,20 pour le comparateur boîte noire",
    "variante": "un effet de 4,5 serait extrême",
    "vis_a_vis": "faille : juges sensibles à la forme",
}
# Fiche au format du gabarit d'idéation de la course 1 (`pole/ideation_v2.py`, SUPPOSÉ être celui de la course 1).
FICHE_COURSE_1 = {
    "nom": "rigueur et dispersion", "type": "question",
    "enonce": "La dispersion des jetons par action prédit-elle la note de rigueur ?",
    "loi_predictive": {"espace_instances": "épisodes notés, quelques centaines",
                       "prediction": "log-rapport de cotes 0,8 de la note haute par écart type", "signe": "+",
                       "metrique": "note de rigueur"},
    "perte_traduction": "la rigueur perçue n'est pas la rigueur",
}


def noyau(**k):
    base = {"predicteurs_connus": {"banque-demo|juge:RIGUEUR": CONNU}, "registre_lectures": [],
            "epreuves_fraiches": {"banque-demo": True, "scores-demo": True}}
    base.update(k)
    return base


def spec_monotone(**k):
    s = {"sortie": "loi", "forme": "monotone_un_trait", "cible": {"banque": "banque-demo", "moniteur": "juge:RIGUEUR"},
         "traits": ["dispersion"], "issue_visee": 2, "sens": "+", "effet": {"valeur": 0.8, "source": "prediction.valeur"},
         "perte_traduction": "la fiche parle de rigueur en général ; la loi ne lit qu'un moniteur"}
    s.update(k)
    return s


def spec_contraste(**k):
    s = {"sortie": "loi", "forme": "contraste_apparie", "cible": {"banque_scores": "scores-demo"},
         "cellule_a": "S_blanche", "cellule_b": "B_noire", "sens": "+",
         "tau": {"valeur": 0.01, "source": "programme:tau_G1"}, "delta": {"valeur": 0.05, "source": "programme:delta_G1"},
         "effet": {"operation": "difference", "termes": [{"valeur": 0.60, "source": "comparaison_forte"},
                                                         {"valeur": 0.20, "source": "comparaison_forte"}], "valeur": 0.4},
         "perte_traduction": "une seule famille ; la fiche en vise plusieurs"}
    s.update(k)
    return s


def renvoi_traducteur(code, raison="sans prédiction sur des épisodes"):
    return {"sortie": "non_testable", "raison_code": code, "raison": raison}


def reponse(spec):
    return "Traduction.\n```json\n" + json.dumps({"traduction": spec}, ensure_ascii=False) + "\n```\n"


class Modele:
    """Modèle factice : rend un texte fixé, compte ses appels, garde ses entrées."""

    def __init__(self, texte):
        self.texte, self.appels, self.entrees = texte, 0, []

    def __call__(self, entree):
        self.appels += 1
        self.entrees.append(entree)
        return self.texte


AFF = {"famille_auteur": "google", "traducteur": "opus-5.5", "contre_traducteur": "kimi-k3.1-pro"}


def lancer(spec_a, spec_b="meme", *, fiche=FICHE, catalogue=CATALOGUE, noy=None, canaris=(), aff=AFF, **k):
    a = Modele(spec_a if isinstance(spec_a, str) else reponse(spec_a))
    if isinstance(spec_b, str) and spec_b == "meme":
        b = Modele(a.texte)
    else:
        b = Modele(spec_b if isinstance(spec_b, str) else reponse(spec_b))
    r = pv.traduire_fiche(fiche, catalogue=catalogue, noyau=noyau() if noy is None else noy, traduire=a,
                          contre_traduire=b, affectation=aff, canaris=canaris, **k)
    json.dumps(r, ensure_ascii=False)  # la sortie est toujours sérialisable (à sceller par l'orchestrateur)
    return r, a, b


# --- les trois sorties ------------------------------------------------------------------------------------------------

class TestSorties:
    def test_sortie_banque_existante_cas_sain(self):
        r, a, b = lancer(spec_monotone())
        assert r["sortie"] == pv.SORTIE_BANQUE, r
        assert (a.appels, b.appels, r["appels"]) == (1, 1, 2)
        fl = r["fiche_loi"]
        assert fl["base"] == "connu:juge:RIGUEUR" and fl["proposition"]["strategie"] == pv.STRATEGIE
        assert pv.garde_forme_interne(fl["proposition"], CATALOGUE["banques"]["banque-demo"])
        assert len(fl["enonce"]) <= 400 and len(fl["empreinte_specification"]) == 64
        assert r["puissance"]["suffisante"] and r["comparaison"]["accord"]
        # la loi = le connu + 0,8 sur (issue 2, trait « dispersion ») ; rien d'autre ne change
        loi = fl["proposition"]["loi_predictive"]
        assert loi["poids"][2][2] == pytest.approx(0.9) and loi["poids"][0] == CONNU["poids"][0]

    def test_les_deux_modeles_recoivent_la_meme_entree_sans_epreuve(self):
        r, a, b = lancer(spec_monotone())
        assert a.entrees == b.entrees
        texte = a.entrees[0]
        assert pv.CONSIGNE_TRADUCTEUR.splitlines()[0] in texte
        for interdit in ("issues", "predicteurs_connus", "registre_lectures", "epreuves_fraiches", "verdict"):
            assert f'"{interdit}"' not in texte

    def test_format_course_1(self):
        s = spec_monotone(effet={"valeur": 0.8, "source": "loi_predictive.prediction"})
        r, _, _ = lancer(s, fiche=FICHE_COURSE_1, aff={"famille_auteur": "anthropic", "traducteur": "kimi-k3.1-pro",
                                                       "contre_traducteur": "argon"})
        assert r["sortie"] == pv.SORTIE_BANQUE, r

    def test_couche_3_moniteur_a_construire(self):
        s = spec_monotone(cible={"banque": "banque-demo", "moniteur": {"a_construire": {"source": "statistique"}}})
        r, _, _ = lancer(s)
        assert r["sortie"] == pv.SORTIE_COUCHE_3, r
        assert any("moniteur" in x for x in r["demande_couche_3"]["manque"])
        assert r["fiche_loi"]["proposition"] is None and "aucun mode" in r["demande_couche_3"]["niveau"]

    def test_couche_3_puissance_insuffisante(self):
        s = spec_monotone(cible={"banque": "banque-demo", "moniteur": "juge:BALANCE"}, issue_visee=1)
        r, _, _ = lancer(s)
        assert r["sortie"] == pv.SORTIE_COUCHE_3, r
        assert r["demande_couche_3"]["effectif_epreuve_requis"] > 40
        assert any(d.startswith("base_sans_predicteur_connu") for d in r["drapeaux"])

    def test_non_testable_par_accord(self):
        r, a, b = lancer(renvoi_traducteur("N3"))
        assert r["sortie"] == pv.SORTIE_RENVOI and r["renvoi"]["code"] == "N3" and r["renvoi"]["famille"] == "fiche"
        assert r["appels"] == 2

    def test_non_testable_codes_differents_drapeau(self):
        r, _, _ = lancer(renvoi_traducteur("N1"), renvoi_traducteur("N2"))
        assert r["renvoi"]["code"] == "N1" and any("codes de renvoi" in d for d in r["drapeaux"])

    def test_contraste_banque_existante(self):
        r, _, _ = lancer(spec_contraste())
        assert r["sortie"] == pv.SORTIE_BANQUE, r
        e = r["fiche_loi"]["engagement"]
        assert e["contrastes"]["meilleure_contre_comparateur"]["coefficients"] == {"S_blanche": 1.0, "B_noire": -1.0}
        assert e["garde"] == {"a": "S_blanche", "b": "B_noire", "delta": 0.05} and e["tau"] == 0.01

    def test_contraste_effet_faible_couche_3(self):
        s = spec_contraste(effet={"operation": "difference", "termes": [{"valeur": 0.45, "source": "comparaison"},
                                                                         {"valeur": 0.38, "source": "comparaison"}],
                                  "valeur": 0.07})
        r, _, _ = lancer(s)
        assert r["sortie"] == pv.SORTIE_COUCHE_3 and r["demande_couche_3"]["effectif_epreuve_requis"] > 600

    def test_contraste_sens_inverse_normalise(self):
        s = spec_contraste(cellule_a="B_noire", cellule_b="S_blanche", sens="-")
        r, _, _ = lancer(spec_contraste(), s)
        assert r["sortie"] == pv.SORTIE_BANQUE and r["comparaison"]["accord"]

    def test_determinisme(self):
        r1, _, _ = lancer(spec_monotone())
        r2, _, _ = lancer(spec_monotone())
        assert r1["empreintes"] == r2["empreintes"] and r1["fiche_loi"] == r2["fiche_loi"]


# --- G1 : loi qui prédit ce qu'elle a vu (rétrodiction) ---------------------------------------------------------------

class TestG1Retrodiction:
    def test_sain_lecture_d_un_autre_constat(self):
        noy = noyau(registre_lectures=[{"banque": "banque-demo", "moniteur": "juge:RIGUEUR", "traits": ["longueur"]}])
        r, _, _ = lancer(spec_monotone(), noy=noy)
        assert r["sortie"] == pv.SORTIE_BANQUE and "constat_deja_lu" not in r["drapeaux"]

    def test_artefact_constat_deja_lu_renvoye_vers_epreuve_fraiche(self):
        noy = noyau(registre_lectures=[{"banque": "banque-demo", "moniteur": "juge:RIGUEUR", "traits": ["dispersion"],
                                        "sens": "-"}])
        r, _, _ = lancer(spec_monotone(), noy=noy)
        assert r["sortie"] == pv.SORTIE_COUCHE_3 and "constat_deja_lu" in r["drapeaux"]
        assert any("rétrodiction" in m for m in r["demande_couche_3"]["manque"])

    def test_artefact_constat_deja_lu_contraste(self):
        noy = noyau(registre_lectures=[{"banque_scores": "scores-demo", "cellules": ["B_noire", "S_blanche"]}])
        r, _, _ = lancer(spec_contraste(), noy=noy)
        assert r["sortie"] == pv.SORTIE_COUCHE_3 and "constat_deja_lu" in r["drapeaux"]

    def test_artefact_forme_qui_enregistre(self):
        r, a, b = lancer(spec_monotone(forme="deterministe"))
        assert r["renvoi"]["code"] == "N6" and r["renvoi"]["famille"] == "pont" and b.appels == 0

    def test_artefact_loi_calendrier_refusee_par_la_garde_de_forme(self):
        p = {"enonce": "x", "strategie": pv.STRATEGIE, "moniteur": "juge:BALANCE", "domaines": ["d"], "operateurs": ["o"],
             "loi_predictive": {"type": "calendrier", "probas": [[0.9, 0.1], [0.1, 0.9]]}}
        with pytest.raises(pv.FormeRefusee) as e:
            pv.garde_forme_interne(p, CATALOGUE["banques"]["banque-demo"])
        assert e.value.code == "N6"

    def test_politique_epreuve_lue(self):
        noy = noyau(epreuves_fraiches={"banque-demo": False})
        r, _, _ = lancer(spec_monotone(), noy=noy)
        assert r["sortie"] == pv.SORTIE_COUCHE_3 and any("épreuve fraîche" in m for m in r["demande_couche_3"]["manque"])
        r2, _, _ = lancer(spec_monotone(), noy=noy, politique_epreuve="reutilisee_declaree")
        assert r2["sortie"] == pv.SORTIE_BANQUE and any(d.startswith("exposition_declaree") for d in r2["drapeaux"])
        with pytest.raises(ValueError):
            lancer(spec_monotone(), politique_epreuve="au_choix")


# --- G2 : loi vide ----------------------------------------------------------------------------------------------------

class TestG2Vide:
    def test_artefact_effet_nul(self):
        s = spec_monotone(effet={"operation": "difference", "termes": [{"valeur": 0.45, "source": "comparaison"},
                                                                        {"valeur": 0.45, "source": "comparaison"}],
                                 "valeur": 0.0})
        r, _, _ = lancer(s)
        assert r["renvoi"]["code"] == "N5" and r["renvoi"]["famille"] == "fiche"

    def test_artefact_effet_nul_sans_loi_numerique(self):
        # cible à construire : aucune loi compilée, seule la garde « effet nul » peut voir le vide
        s = spec_monotone(cible={"banque": "banque-demo", "moniteur": {"a_construire": {"source": "statistique"}}},
                          effet={"operation": "difference", "termes": [{"valeur": 0.45, "source": "comparaison"},
                                                                        {"valeur": 0.45, "source": "comparaison"}],
                                 "valeur": 0.0})
        r, _, _ = lancer(s)
        assert r["renvoi"]["code"] == "N5"

    def test_artefact_cellules_identiques(self):
        r, _, _ = lancer(spec_contraste(cellule_b="S_blanche"))
        assert r["renvoi"]["code"] == "N5"

    def test_artefact_loi_egale_a_sa_base(self):
        r, _, _ = lancer(spec_monotone())
        c = {"signature": r["fiche_loi"]["signature"], "loi": CONNU, "base": CONNU, "nom_base": "connu"}
        sonde = pv.sonde_par_defaut(CATALOGUE["banques"]["banque-demo"])
        motif, d = pv.garde_vide(c, sonde)
        assert motif and "égale à sa base" in motif and d == 0.0

    def test_sain_loi_non_vide(self):
        r, _, _ = lancer(spec_monotone())
        sonde = pv.sonde_par_defaut(CATALOGUE["banques"]["banque-demo"])
        c = {"signature": r["fiche_loi"]["signature"], "loi": r["fiche_loi"]["proposition"]["loi_predictive"],
             "base": CONNU, "nom_base": "connu"}
        motif, d = pv.garde_vide(c, sonde)
        assert motif is None and d > pv.KL_VIDE


# --- G3 : loi ou traduction qui lit la partie d'épreuve ---------------------------------------------------------------

class TestG3LectureEpreuve:
    def test_sain_canari_absent(self):
        r, a, b = lancer(spec_monotone(), canaris=[CANARI])
        assert r["sortie"] == pv.SORTIE_BANQUE and r["incident"] is None and a.appels == b.appels == 1

    def test_artefact_issues_dans_le_catalogue_aucun_appel(self):
        cat = copy.deepcopy(CATALOGUE)
        cat["banques"]["banque-demo"]["issues"] = {"e1": 2}
        a = Modele(reponse(spec_monotone()))
        with pytest.raises(pv.LectureEpreuveInterdite):
            pv.traduire_fiche(FICHE, catalogue=cat, noyau=noyau(), traduire=a, contre_traduire=a, affectation=AFF)
        assert a.appels == 0

    def test_artefact_canari_dans_la_fiche_aucun_appel(self):
        fiche = dict(FICHE, hypothese=FICHE["hypothese"] + " " + CANARI)
        a = Modele(reponse(spec_monotone()))
        with pytest.raises(pv.LectureEpreuveInterdite):
            pv.traduire_fiche(fiche, catalogue=CATALOGUE, noyau=noyau(), traduire=a, contre_traduire=a,
                              affectation=AFF, canaris=[CANARI])
        assert a.appels == 0

    def test_artefact_metadonnee_de_fiche(self):
        a = Modele(reponse(spec_monotone()))
        with pytest.raises(pv.LectureEpreuveInterdite):
            pv.traduire_fiche(dict(FICHE, ident="F-07"), catalogue=CATALOGUE, noyau=noyau(), traduire=a,
                              contre_traduire=a, affectation=AFF)
        assert a.appels == 0

    def test_artefact_enveloppe_modifiee(self):
        entree = pv.construire_entree(FICHE, CATALOGUE)
        pv.garde_entree(entree)
        for cle, valeur in (("juge", "selection_pari"), ("verdicts", [])):
            with pytest.raises(pv.LectureEpreuveInterdite):
                pv.garde_entree(dict(entree, **{cle: valeur}))
        with pytest.raises(pv.LectureEpreuveInterdite):
            pv.garde_entree(dict(entree, consigne=entree["consigne"] + " Lis aussi l'épreuve."))

    def test_artefact_canari_dans_la_reponse(self):
        texte = reponse(spec_monotone()) + f"\n(vu dans l'épreuve : {CANARI})"
        r, a, b = lancer(texte, canaris=[CANARI])
        assert r["renvoi"]["code"] == "N7" and r["incident"] and b.appels == 0

    def test_artefact_canari_dans_la_contre_traduction(self):
        r, a, b = lancer(spec_monotone(), reponse(spec_monotone()) + CANARI, canaris=[CANARI])
        assert r["renvoi"]["code"] == "N7" and r["incident"]

    def test_artefact_trait_d_identite(self):
        r, _, b = lancer(spec_monotone(traits=["identifiant"]))
        assert r["renvoi"]["code"] == "N7" and b.appels == 0

    def test_artefact_condition_sur_un_champ_d_episode(self):
        loi = {"type": "si_sinon", "condition": {"identifiant": "e17"}, "si": CONNU, "sinon": CONNU}
        with pytest.raises(pv.FormeRefusee) as e:
            pv.valider_loi_gabarit(loi, 3, 3)
        assert e.value.code == "N7"


# --- traçabilité des chiffres -----------------------------------------------------------------------------------------

class TestTracabilite:
    def test_sain_pourcentage_et_virgule(self):
        assert 0.45 in pv.nombres_du_texte("rappel à 1 % de 0,45") and 0.01 in pv.nombres_du_texte("1 %")

    @pytest.mark.parametrize("effet", [
        {"valeur": 0.9, "source": "prediction.valeur"},                      # chiffre inventé
        {"valeur": 0.8, "source": "prediction.inexistant"},                  # source absente
        {"operation": "difference", "termes": [{"valeur": 0.45, "source": "comparaison"},
                                               {"valeur": 0.38, "source": "comparaison"}], "valeur": 0.1},  # mal recalculé
        {"operation": "exponentielle", "termes": [{"valeur": 0.8, "source": "prediction.valeur"}], "valeur": 2.2},
        {"valeur": 0.05, "source": "programme:alpha_secret"},                # constante inconnue
    ])
    def test_artefacts(self, effet):
        r, _, b = lancer(spec_monotone(effet=effet))
        assert r["renvoi"]["code"] == "N9" and b.appels == 0

    def test_artefact_objet_a_construire_sans_source(self):
        s = spec_monotone(cible={"banque": "banque-demo", "moniteur": {"a_construire": {"source": "sonde_inventee"}}})
        r, _, _ = lancer(s)
        assert r["renvoi"]["code"] == "N9"

    def test_artefact_constante_du_programme_falsifiee(self):
        r, _, _ = lancer(spec_contraste(delta={"valeur": 0.2, "source": "programme:delta_G1"}))
        assert r["renvoi"]["code"] == "N9"


# --- contre-traduction ------------------------------------------------------------------------------------------------

def _compile(spec, fiche=FICHE):
    s = pv.valider_specification(spec, fiche)
    return pv.compiler(s, CATALOGUE, noyau())


class TestContreTraduction:
    SONDE = pv.sonde_par_defaut(CATALOGUE["banques"]["banque-demo"])

    def test_sain_identique(self):
        c = _compile(spec_monotone())
        r = pv.comparer_lois(c, copy.deepcopy(c), self.SONDE)
        assert r["accord"] and r["kl_sym_moyen"] == 0.0

    def test_sain_effet_proche(self):
        s = spec_monotone(effet={"valeur": 0.45, "source": "comparaison"})  # 0,8 contre 0,45 : rapport 1,78 <= 2
        r = pv.comparer_lois(_compile(spec_monotone()), _compile(s), self.SONDE)
        assert r["accord"] and r["kl_sym_moyen"] > 0

    @pytest.mark.parametrize("autre", [
        {"sens": "-"}, {"traits": ["longueur"]}, {"issue_visee": 1},
        {"cible": {"banque": "banque-demo", "moniteur": "juge:BALANCE"}, "issue_visee": 1},
        {"forme": "interaction_deux_traits", "traits": ["dispersion", "longueur"]},
        {"effet": {"valeur": 0.2, "source": "critere_de_mort"}},  # effet 4 fois plus petit
    ])
    def test_artefacts_desaccord(self, autre):
        r = pv.comparer_lois(_compile(spec_monotone()), _compile(spec_monotone(**autre)), self.SONDE)
        assert not r["accord"] and r["ecarts"]

    def test_artefact_genres_differents(self):
        r = pv.comparer_lois(_compile(spec_monotone()), _compile(spec_contraste()))
        assert not r["accord"]

    def test_pipeline_sens_inverse(self):
        r, _, _ = lancer(spec_monotone(), spec_monotone(sens="-"))
        assert r["renvoi"]["code"] == "N8" and "sens" in r["renvoi"]["detail"]

    def test_pipeline_loi_contre_renvoi(self):
        r, _, _ = lancer(spec_monotone(), renvoi_traducteur("N1"))
        assert r["renvoi"]["code"] == "N8"

    def test_pipeline_contre_traducteur_refuse(self):
        r, _, _ = lancer(spec_monotone(), "Je ne peux pas aider à cela.")
        assert r["renvoi"]["code"] == "N8" and "N10" in r["renvoi"]["detail"]


# --- affectation des modèles ------------------------------------------------------------------------------------------

class TestAffectation:
    def test_sain_regle_croisee(self):
        for famille in ("google", "moonshot", "anthropic"):
            a = pv.affectation_recommandee(famille)
            f = pv.verifier_affectation(a["famille_auteur"], a["traducteur"], a["contre_traducteur"])
            assert len({f["auteur"], f["traducteur"], f["contre_traducteur"]}) == 3

    @pytest.mark.parametrize("auteur,trad,contre", [
        ("google", "argon", "kimi-k3.1-pro"),       # traducteur de la famille de l'auteur
        ("google", "opus-5.5", "fable-5.1"),        # contre-traducteur de la famille du traducteur
        ("moonshot", "opus-5.5", "kimi-k3.1-pro"),  # contre-traducteur de la famille de l'auteur
        ("google", "mistral-x", "kimi-k3.1-pro"),   # famille inconnue
        ("inconnue", "opus-5.5", "kimi-k3.1-pro"),
    ])
    def test_artefacts(self, auteur, trad, contre):
        with pytest.raises(pv.AffectationRefusee):
            pv.verifier_affectation(auteur, trad, contre)

    def test_artefact_aucun_appel(self):
        a = Modele(reponse(spec_monotone()))
        with pytest.raises(pv.AffectationRefusee):
            pv.traduire_fiche(FICHE, catalogue=CATALOGUE, noyau=noyau(), traduire=a, contre_traduire=a,
                              affectation={"famille_auteur": "anthropic", "traducteur": "opus-5.5",
                                           "contre_traducteur": "argon"})
        assert a.appels == 0


# --- refus et hors format ---------------------------------------------------------------------------------------------

class TestRefus:
    @pytest.mark.parametrize("texte", [
        "Je ne peux pas aider à cela.",
        reponse({"sortie": "peut-etre"}),
        reponse(renvoi_traducteur("N5")),          # code réservé au programme
        reponse(spec_monotone(sens="++")),
        reponse(spec_monotone(perte_traduction="")),
    ])
    def test_artefacts_n10_sans_second_appel(self, texte):
        r, a, b = lancer(texte)
        assert r["renvoi"]["code"] == "N10" and a.appels == 1 and b.appels == 0

    def test_sain_bloc_parmi_du_texte(self):
        r, _, _ = lancer("Préambule.\n```json\n{\"autre\": 1}\n```\n" + reponse(spec_monotone()))
        assert r["sortie"] == pv.SORTIE_BANQUE


# --- garde de forme du noyau ------------------------------------------------------------------------------------------

class TestGardeForme:
    DESC = CATALOGUE["banques"]["banque-demo"]

    def _prop(self, **k):
        r, _, _ = lancer(spec_monotone())
        p = copy.deepcopy(r["fiche_loi"]["proposition"])
        p.update(k)
        return p

    def test_sain(self):
        assert pv.garde_forme_interne(self._prop(), self.DESC)

    @pytest.mark.parametrize("modif", [
        {"moniteur": "juge:INCONNU"}, {"strategie": "monotone_un_trait"}, {"enonce": "x" * 401},
        {"domaines": []}, {"loi_predictive": {"type": "softmax", "poids": [[9.0, 0, 0]] * 3, "biais": [0, 0, 0]}},
        {"loi_predictive": {"type": "softmax", "poids": [[0.0, 0.0]] * 3, "biais": [0, 0, 0]}},
    ])
    def test_artefacts(self, modif):
        with pytest.raises(pv.FormeRefusee):
            pv.garde_forme_interne(self._prop(**modif), self.DESC)

    def test_artefact_champ_hors_gabarit(self):
        with pytest.raises(pv.FormeRefusee):
            pv.garde_forme_interne(dict(self._prop(), temoin="vraie"), self.DESC)

    def test_artefact_poids_hors_borne_dans_le_pont(self):
        r, _, b = lancer(spec_monotone(effet={"valeur": 4.5, "source": "variante"}))
        assert r["renvoi"]["code"] == "N11" and b.appels == 0

    def test_artefact_loi_brute_du_traducteur(self):
        r, _, _ = lancer(spec_monotone(loi_predictive={"type": "fixe", "probas": [1, 1, 1]}))
        assert r["renvoi"]["code"] == "N11"

    def test_artefact_issue_hors_moniteur(self):
        r, _, _ = lancer(spec_monotone(issue_visee=3))
        assert r["renvoi"]["code"] == "N11"

    def test_garde_du_noyau_injectee(self):
        vus = []
        r, _, _ = lancer(spec_monotone(), garde_forme_noyau=lambda p, banque: vus.append((p["moniteur"], banque)))
        assert r["sortie"] == pv.SORTIE_BANQUE and vus == [("juge:RIGUEUR", "banque-demo")]

        def refuse(p, banque):
            raise ValueError("stratégie non déclarée ou hors catalogue")
        r2, _, _ = lancer(spec_monotone(), garde_forme_noyau=refuse)
        assert r2["renvoi"]["code"] == "N11" and "hors catalogue" in r2["renvoi"]["detail"]

    def test_formes_interaction_et_sous_populations(self):
        r, _, _ = lancer(spec_monotone(forme="interaction_deux_traits", traits=["dispersion", "longueur"]))
        assert r["sortie"] == pv.SORTIE_BANQUE and r["fiche_loi"]["proposition"]["loi_predictive"]["type"] == "si_sinon"
        s = spec_monotone(forme="difference_sous_populations", traits=[], sous_population_visee=1,
                          effet={"valeur": 4.5, "source": "variante"})
        r2, _, _ = lancer(s)
        assert r2["sortie"] == pv.SORTIE_BANQUE, r2
        loi = r2["fiche_loi"]["proposition"]["loi_predictive"]
        assert loi["type"] == "par_sous_population" and loi["lois"]["1"]["biais"][2] == pytest.approx(4.4)
        r3, _, _ = lancer(spec_monotone(forme="difference_sous_populations", traits=[], sous_population_visee=2))
        assert r3["renvoi"]["code"] == "N11"


# --- compatibilité avec le vrai code de l'orchestrateur v56 (si déplié) -----------------------------------------------

POLE = os.environ.get("PONT_POLE_V56")
compat = pytest.mark.skipif(not POLE or not os.path.isdir(os.path.join(POLE or "", "pole")),
                            reason="PONT_POLE_V56 absent : archive v56 non dépliée, compatibilité non jouée (dit)")


@compat
class TestCompatibiliteV56:
    @pytest.fixture(autouse=True)
    def _pole(self, monkeypatch, tmp_path):
        monkeypatch.syspath_prepend(POLE)
        from pole import engagement_apparie, monde_banque, monde_banque_scores, pari_apparie, proposeur, selection_pari
        self.ea, self.mb, self.mbs, self.pa, self.prop, self.sp = (engagement_apparie, monde_banque, monde_banque_scores,
                                                                   pari_apparie, proposeur, selection_pari)
        monkeypatch.setitem(proposeur.CATALOGUE, pv.STRATEGIE, "traduction d'une fiche de course (pont v1)")
        rng = random.Random(20261101)
        lignes = [{"identifiant": f"i{i}", "tache": f"t{i // 2}", "z": [round(rng.gauss(0, 1), 4) for _ in TRAITS],
                   "g": i % 2, "partie": "calibrage" if i < 40 else "epreuve", "issues": {"juge:RIGUEUR": rng.randrange(3)}}
                  for i in range(60)]
        chemin = tmp_path / "banque-compat.json"
        chemin.write_text(json.dumps({"nom": "banque-demo", "traits": TRAITS, "sous_populations": 2,
                                      "moniteurs": {"juge:RIGUEUR": {"nombre_issues": 3}}, "instances": lignes}))
        self.monde = monde_banque.MondeBanque(str(chemin), graine=7, nul_informe=False)

    def _garde_reelle(self, p, banque):
        fiche = self.prop.valider_proposition(p, self.monde, 0.05, "pont-essai-01", "opus-essai")
        assert fiche.loi_predictive == p["loi_predictive"] and fiche.espace_instances["moniteur"] == p["moniteur"]

    @pytest.mark.parametrize("modif", [
        {}, {"forme": "interaction_deux_traits", "traits": ["dispersion", "longueur"]},
        {"forme": "difference_sous_populations", "traits": [], "sous_population_visee": 1,
         "effet": {"valeur": 4.5, "source": "variante"}},
    ])
    def test_garde_reelle_du_noyau_et_proba(self, modif):
        r, _, _ = lancer(spec_monotone(**modif), garde_forme_noyau=self._garde_reelle)
        assert r["sortie"] == pv.SORTIE_BANQUE, r
        loi = r["fiche_loi"]["proposition"]["loi_predictive"]
        self.sp.valider_loi(loi, 3, len(TRAITS))
        for x in pv.sonde_par_defaut(CATALOGUE["banques"]["banque-demo"]):
            assert pv.proba(loi, x) == pytest.approx(self.sp.proba(loi, x, [], 0), abs=1e-12)

    def test_garde_reelle_refuse_sans_la_strategie(self, monkeypatch):
        monkeypatch.delitem(self.prop.CATALOGUE, pv.STRATEGIE)
        r, _, _ = lancer(spec_monotone(), garde_forme_noyau=self._garde_reelle)
        assert r["renvoi"]["code"] == "N11" and "catalogue" in r["renvoi"]["detail"]

    def test_contraste_accepte_par_l_engagement_apparie(self):
        r, _, _ = lancer(spec_contraste())
        e = r["fiche_loi"]["engagement"]
        coeff = e["contrastes"]["meilleure_contre_comparateur"]["coefficients"]
        assert self.pa.verifier_coefficients(coeff, 0.0)
        rng = random.Random(3)
        episodes = []
        for i in range(160):
            partie = "calibrage" if i < 120 else "epreuve"
            for et in (("honnete",) if partie == "calibrage" else ("honnete", "sabote")):
                episodes.append({"id": f"e{i}-{et}", "unite": f"u{i}", "etiquette": et, "partie": partie, "strates": {},
                                 "scores": {"S_blanche": rng.random(), "B_noire": rng.random()}})
        monde = self.mbs.MondeBanqueScores({"cellules": ["S_blanche", "B_noire"], "episodes": episodes}, graine=5)
        eng = self.ea.construire(monde, e["contrastes"], e["tau"], garde=e["garde"])
        assert eng["type"] == "apparie" and eng["cle_heritage"]["garde"][0]["delta"] == 0.05
