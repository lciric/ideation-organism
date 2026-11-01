"""Contrôles fatals du critère de sélection par pari — première expérience du pôle, en simulation à vérité connue.

T1a nul dans 𝓛 → promotion ≤ α ; T6 parasite de Kelly → promotion ≤ α ; batterie de tricheurs scriptés contre le
critère des filles (forme, copie renommée, enveloppe aveugle, fille constante, pari couvert, adimensionnement, jargon
rare ; nul augmenté des parents et de leurs enveloppes, marge 2δ₀) → chacun promu au plus à α ; T1b nul hors de 𝓛
(dérive) → taux rapporté ; T3 paris couverts → promus seulement si leur composante nette est vraie ; T9 disjonction
partitionnée → aucun gain sur le meilleur parent. Un échec de T1a, de T6 ou d'un tricheur invalide le critère. Chaque contrôle compte au moins 1 000 répétitions ;
chaque répétition a sa graine dérivée de la graine maîtresse (règle : `outils.graine_derivee`), consignée au rapport.
Des variantes cassées du critère (artefacts) sont passées dans les mêmes contrôles : un contrôle qui ne les verrait pas
ne garderait rien (R5).
"""

import math
import random
import statistics

from . import selection_pari as sp
from .outils import graine_derivee

Z_UNILATERAL_95 = 1.6448536269514722


def borne_wilson(succes, n, z=Z_UNILATERAL_95):
    """Borne haute unilatérale à 95 % (score de Wilson) d'une proportion."""
    if n == 0:
        return None
    p = succes / n
    centre = p + z * z / (2 * n)
    marge = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + marge) / (1 + z * z / n))


def _dirichlet(rng, k, concentration):
    g = [rng.gammavariate(concentration, 1.0) for _ in range(k)]
    return [round(x / sum(g), 9) for x in g]


def _fixe(p):
    return {"type": "fixe", "probas": list(p)}


def _frequences(issues, k, lissage=0.5):
    return [round((issues.count(i) + lissage) / (len(issues) + k * lissage), 9) for i in range(k)]


def _executer(nom, graine, repetitions, scenario):
    """`scenario(rng)` rend (engagement gelé, loi du monde) ; on tire frais et on évalue."""
    promotions, finales, maxima = 0, [], []
    for r in range(repetitions):
        rng = random.Random(graine_derivee(graine, nom, r))
        gele, loi_monde = scenario(rng)
        ev = sp.evaluer(gele, sp.tirer_frais(gele, loi_monde, graine_derivee(graine, nom, r, "frais")))
        promotions += ev["promue"]
        finales.append(ev["log_richesse_finale"])
        maxima.append(ev["log_richesse_max"])
    return {"controle": nom, "repetitions": repetitions, "promotions": promotions, "taux": promotions / repetitions,
            "borne_haute_95": borne_wilson(promotions, repetitions),
            "log_richesse_finale_mediane": statistics.median(finales), "log_richesse_max_observee": max(maxima)}


TOUS = ("T1a", "T6", "tricheurs", "T1b", "T3", "T9", "artefacts")


def executer_controles(graine=20261026, repetitions=1000, tirages=200, alpha=0.05, k=3, dimension=2, controles=TOUS,
                       delta0=0.01, part_calibrage=50):
    if repetitions < 1000:
        raise ValueError("au moins 1 000 répétitions par contrôle")
    seuil_log = math.log(1 / alpha)

    def engagement(rng, loi, bibliotheque=sp.BIBLIOTHEQUE_STANDARD, instances=None):
        instances = instances or sp.tirer_instances(rng, tirages, dimension)
        return sp.geler_engagement(sp.construire_engagement("controle", loi, instances, k, alpha, bibliotheque, "continu"))

    def t1a(monde):
        def scenario(rng):
            loi = sp.loi_softmax_aleatoire(rng, k, dimension)
            instances = sp.tirer_instances(rng, tirages, dimension)
            lois_monde = {"marginale": _fixe(sp.moyenne_loi(loi, instances)), "uniforme": _fixe([1 / k] * k),
                          "moyenne_glissante": {"type": "moyenne_glissante", "nombre_issues": k, "fenetre": 10,
                                                "lissage": 0.5}}
            return engagement(rng, loi, instances=instances), lois_monde[monde]
        return scenario

    def t1a_artefact(rng):
        pi = _dirichlet(rng, k, 1.0)
        return engagement(rng, _fixe(pi), [{"nom": "uniforme", "type": "uniforme"}]), _fixe(pi)

    def t6(variante):
        def scenario(rng):
            pi = _dirichlet(rng, k, 2.0)
            entrainement = [sp.tirer_categorie(rng, pi) for _ in range(50)]
            pi_ent = _frequences(entrainement, k)
            parasite = {"type": "melange", "composantes": [_fixe(pi), _fixe(pi_ent)], "poids": [0.95, 0.05]}
            membre_ent = {"nom": "marginale_entrainement", "type": "fixe", "probas": pi_ent}
            glissantes = dict(sp.BIBLIOTHEQUE_STANDARD[2])
            bibliotheques = {
                "correct": list(sp.BIBLIOTHEQUE_STANDARD) + [membre_ent],
                "part_separee": [{"nom": "uniforme", "type": "uniforme"}, membre_ent, glissantes],
                "en_ligne": [{"nom": "uniforme", "type": "uniforme"},
                             {"nom": "marginale_en_ligne", "type": "marginale_en_ligne", "lissage": 0.5}, glissantes],
            }
            return engagement(rng, parasite, bibliotheques[variante]), _fixe(pi)
        return scenario

    def t1b(loi_h):
        def scenario(rng):
            a = [0.6, 0.3, 0.1]
            rng.shuffle(a)
            derive = {"type": "derive_lineaire", "debut": a, "fin": list(reversed(a)), "horizon": tirages}
            if loi_h == "oracle_aveugle":
                return engagement(rng, derive), derive
            fausse = sp.loi_softmax_aleatoire(rng, k, dimension)
            return engagement(rng, fausse), derive
        return scenario

    def t3(epsilon, net_vrai):
        def scenario(rng):
            net = sp.loi_softmax_aleatoire(rng, k, dimension)
            instances = sp.tirer_instances(rng, tirages, dimension)
            pi = sp.moyenne_loi(net, instances)
            couvert = {"type": "melange", "composantes": [_fixe(pi), net], "poids": [1 - epsilon, epsilon]}
            return engagement(rng, couvert, instances=instances), (net if net_vrai else _fixe(pi))
        return scenario

    r = {"parametres": {"graine_maitresse": graine, "repetitions": repetitions, "tirages_par_repetition": tirages,
                        "alpha": alpha, "seuil_richesse": 1 / alpha, "nombre_issues": k, "dimension": dimension,
                        "lecture": "continue (promotion dès que W_t ≥ 1/α, inégalité de Ville)",
                        "delta0_filles": delta0, "part_calibrage_filles": part_calibrage,
                        "regle_des_graines": "graine_derivee(graine_maitresse, contrôle, répétition[, 'frais'])"}}
    if "T1a" in controles:
        r["T1a"] = [_executer(f"T1a-nul-{m}", graine, repetitions, t1a(m))
                    for m in ("marginale", "uniforme", "moyenne_glissante")]
    if "T6" in controles:
        r["T6"] = _executer("T6-parasite-de-Kelly", graine, repetitions, t6("correct"))
    if "tricheurs" in controles:
        r["tricheurs"] = controle_tricheurs(graine, repetitions, tirages, alpha, k, dimension, delta0, part_calibrage)
    if "T1b" in controles:
        r["T1b"] = [_executer(f"T1b-derive-{h}", graine, repetitions, t1b(h)) for h in ("oracle_aveugle", "loi_fausse")]
    if "T3" in controles:
        r["T3"] = [dict(_executer(f"T3-couvert-eps{e}-net-{'vrai' if v else 'faux'}", graine, repetitions, t3(e, v)),
                        epsilon=e, composante_nette_vraie=v) for e in (0.05, 0.2) for v in (False, True)]
    if "T9" in controles:
        r["T9"] = controle_t9(graine, repetitions, tirages, alpha, k, dimension)
    if "artefacts" in controles:
        r["artefacts"] = [
            _executer("T1a-artefact-bibliotheque-uniforme-seule", graine, repetitions, t1a_artefact),
            _executer("T6-artefact-denominateur-part-separee", graine, repetitions, t6("part_separee")),
            _executer("T6-artefact-denominateur-en-ligne", graine, repetitions, t6("en_ligne")),
        ]
    r["verdicts"] = juger(r, alpha, seuil_log)
    return r


TRICHEURS = ("forme", "copie_renommee", "enveloppe_aveugle", "fille_constante", "pari_couvert", "adimensionnement",
             "jargon_rare")
MONDES_FILLES = ("parent_A_vrai", "parents_vrais_par_sous_population", "nul_aveugle", "melange_des_parents")
OPERATEUR_FICTIF = "hyperfibration de Kodaira-Spencer tronquée"


def loi_tricheur(nom, p1, p2, q_ent, rng):
    """Fille scriptée sans contenu nouveau (aucun appel de modèle). Le texte n'entre jamais dans l'évaluateur."""
    if nom in ("forme", "copie_renommee", "jargon_rare"):
        return dict(p1)
    if nom == "enveloppe_aveugle":
        if rng.random() < 0.5:
            w = round(rng.random(), 3)
            return {"type": "melange", "composantes": [p1, p2], "poids": [w, round(1 - w, 3)]}
        return {"type": "enveloppe", "lois": [p1, p2]}
    if nom == "fille_constante":
        return _fixe(q_ent)
    if nom == "pari_couvert":
        e = rng.choice([0.05, 0.2])
        return {"type": "melange", "composantes": [_fixe(q_ent), p1], "poids": [1 - e, e]}
    if nom == "adimensionnement":
        f = [round(0.5 + 2 * rng.random(), 3) for _ in p1["poids"][0]]
        interne = {"type": "softmax", "poids": [[w * fj for w, fj in zip(ligne, f)] for ligne in p1["poids"]],
                   "biais": list(p1["biais"])}
        return {"type": "echelle", "facteurs": f, "loi": interne}
    raise ValueError(nom)


def _monde_fille(nom, p1, p2, instances):
    if nom == "parent_A_vrai":
        return p1
    if nom == "parents_vrais_par_sous_population":
        return {"type": "par_sous_population", "lois": {"0": p1, "1": p2}}
    if nom == "nul_aveugle":
        return _fixe(sp.moyenne_loi(p1, instances))
    return {"type": "melange", "composantes": [p1, p2], "poids": [0.5, 0.5]}


def _essai_fille(graine, nom, r, tirages, alpha, k, dimension, delta0, part_calibrage, nul_augmente=True):
    rng = random.Random(graine_derivee(graine, "fille", nom, r))
    p1, p2, p3 = (sp.loi_softmax_aleatoire(rng, k, dimension) for _ in range(3))
    instances = sp.tirer_instances(rng, part_calibrage + tirages, dimension)
    monde_nom = rng.choice(MONDES_FILLES)
    if nom == "fille_neuve":
        monde_nom = "parent_A_vrai_et_loi_neuve"
        monde = {"type": "par_sous_population", "lois": {"0": p1, "1": p3}}
        loi = {"type": "si_sinon", "condition": {"sous_population": 0}, "si": p1, "sinon": p3}
    else:
        monde = _monde_fille(monde_nom, p1, p2, instances)
    entrainement = sp.tirer_instances(rng, 100, dimension)
    issues_ent = [sp.tirer_categorie(rng, sp.proba(monde, x, [], 0)) for x in entrainement]
    q_ent = _frequences(issues_ent, k)
    if nom != "fille_neuve":
        loi = loi_tricheur(nom, p1, p2, q_ent, rng)
    standard = list(sp.BIBLIOTHEQUE_STANDARD) + [{"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}]
    if nul_augmente:
        biblio = sp.bibliotheque_fille({"A": p1, "B": p2}, dimension, standard, q_ent, nombre_issues=k)
        gele = sp.geler_engagement(sp.construire_engagement("fille", loi, instances, k, alpha, biblio, "continu",
                                                            part_calibrage=part_calibrage, delta0=delta0))
    else:
        gele = sp.geler_engagement(sp.construire_engagement("fille", loi, instances[part_calibrage:], k, alpha, standard,
                                                            "continu"))
    ev = sp.evaluer(gele, sp.tirer_frais(gele, monde, graine_derivee(graine, "fille", nom, r, "frais")))
    return monde_nom, ev


def controle_tricheurs(graine, repetitions, tirages, alpha, k, dimension, delta0, part_calibrage):
    """Batterie de tricheurs scriptés contre le critère des filles (nul augmenté des parents et enveloppes, marge 2δ₀)."""
    sortie = {"tricheurs": [], "temoin_positif": None, "artefacts": []}
    for nom in TRICHEURS + ("fille_neuve",):
        promotions, par_monde = 0, {}
        for r in range(repetitions):
            monde_nom, ev = _essai_fille(graine, nom, r, tirages, alpha, k, dimension, delta0, part_calibrage)
            promotions += ev["promue"]
            compte = par_monde.setdefault(monde_nom, [0, 0])
            compte[0] += ev["promue"]
            compte[1] += 1
        ligne = {"controle": f"tricheur-{nom}" if nom != "fille_neuve" else "temoin-positif-fille-neuve",
                 "repetitions": repetitions, "promotions": promotions, "taux": promotions / repetitions,
                 "borne_haute_95": borne_wilson(promotions, repetitions),
                 "par_monde": {m: {"promotions": c[0], "repetitions": c[1]} for m, c in sorted(par_monde.items())}}
        if nom == "fille_neuve":
            sortie["temoin_positif"] = ligne
        else:
            sortie["tricheurs"].append(ligne)
    for nom in ("forme", "enveloppe_aveugle"):
        promotions = sum(_essai_fille(graine, nom, r, tirages, alpha, k, dimension, delta0, part_calibrage,
                                      nul_augmente=False)[1]["promue"] for r in range(repetitions))
        sortie["artefacts"].append({"controle": f"artefact-nul-sans-parents-{nom}", "repetitions": repetitions,
                                    "promotions": promotions, "taux": promotions / repetitions,
                                    "borne_haute_95": borne_wilson(promotions, repetitions)})
    return sortie


def controle_t9(graine, repetitions, tirages, alpha, k, dimension):
    """Fille = concaténation si/sinon de deux parents ; et témoin positif : fille qui prédit du neuf sur une partie."""
    gains_naifs, promotions_concat, max_logw_concat, promotions_neuve = [], 0, -math.inf, 0
    for r in range(repetitions):
        rng = random.Random(graine_derivee(graine, "T9", r))
        p1, p2, p3 = (sp.loi_softmax_aleatoire(rng, k, dimension) for _ in range(3))
        instances = sp.tirer_instances(rng, tirages, dimension)
        nul_fille = sp.bibliotheque_fille({"A": p1, "B": p2}, dimension)
        for neuve in (False, True):
            monde = {"type": "par_sous_population", "lois": {"0": p1, "1": p3 if neuve else p2}}
            fille = {"type": "si_sinon", "condition": {"sous_population": 0}, "si": p1, "sinon": p3 if neuve else p2}
            gele = sp.geler_engagement(sp.construire_engagement("T9", fille, instances, k, alpha, nul_fille, "continu"))
            tirages_frais = sp.tirer_frais(gele, monde, graine_derivee(graine, "T9", r, neuve, "frais"))
            ev = sp.evaluer(gele, tirages_frais)
            if neuve:
                promotions_neuve += ev["promue"]
                continue
            promotions_concat += ev["promue"]
            max_logw_concat = max(max_logw_concat, ev["log_richesse_max"])
            issues = tirages_frais["issues"]
            den, _ = sp.trajectoire_denominateur(sp.BIBLIOTHEQUE_STANDARD, issues, instances, k)
            naif = {nom: sp.trajectoire_loi(l, issues, instances)[-1] - den[-1] for nom, l in
                    (("fille", fille), ("A", p1), ("B", p2))}
            gains_naifs.append(naif["fille"] - max(naif["A"], naif["B"]))
    return {"controle": "T9-disjonction-partitionnee", "repetitions": repetitions,
            "promotions_concatenation_nul_etendu": promotions_concat,
            "taux_concatenation_nul_etendu": promotions_concat / repetitions,
            "log_richesse_max_concatenation_nul_etendu": max_logw_concat,
            "gain_naif_sur_meilleur_parent_median": statistics.median(gains_naifs),
            "part_gain_naif_positif": sum(g > 0 for g in gains_naifs) / repetitions,
            "temoin_positif_fille_neuve_taux_promotion": promotions_neuve / repetitions}


def juger(r, alpha, seuil_log):
    v = {}
    if "T1a" in r:
        t1a_max = max(c["taux"] for c in r["T1a"])
        v["T1a"] = {"critere": f"taux de promotion ≤ α = {alpha} dans chaque nul de 𝓛", "taux_max": t1a_max,
                    "passe": t1a_max <= alpha}
    if "T6" in r:
        v["T6"] = {"critere": f"taux de promotion du parasite ≤ α = {alpha}", "taux": r["T6"]["taux"],
                   "passe": r["T6"]["taux"] <= alpha}
    if "T1b" in r:
        oracle = r["T1b"][0]["taux"]
        v["T1b"] = {"critere": f"rapporter ; au-delà de 2α = {2 * alpha}, la bibliothèque ne suffit pas",
                    "taux_oracle_aveugle": oracle, "bibliotheque_suffit": oracle <= 2 * alpha}
    if "T3" in r:
        faux = [c["taux"] for c in r["T3"] if not c["composante_nette_vraie"]]
        v["T3"] = {"critere": f"paris couverts à composante nette fausse promus au plus à α = {alpha}",
                   "taux_max_net_faux": max(faux), "passe": max(faux) <= alpha,
                   "puissance_net_vrai": {str(c["epsilon"]): c["taux"] for c in r["T3"] if c["composante_nette_vraie"]}}
    if "T9" in r:
        t9 = r["T9"]
        v["T9"] = {"critere": "concaténation si/sinon des parents : aucune promotion contre le nul étendu (aucun gain "
                              "sur le meilleur parent)", "taux": t9["taux_concatenation_nul_etendu"],
                   "passe": t9["taux_concatenation_nul_etendu"] <= alpha
                   and t9["log_richesse_max_concatenation_nul_etendu"] <= 1e-9}
    if "tricheurs" in r:
        promus = {t["controle"]: t["taux"] for t in r["tricheurs"]["tricheurs"] if t["taux"] > alpha}
        v["tricheurs"] = {"critere": f"aucun tricheur scripté promu au-delà de α = {alpha}", "passe": not promus,
                          "tricheurs_promus_au_dela_de_alpha": promus,
                          "taux_max": max(t["taux"] for t in r["tricheurs"]["tricheurs"]),
                          "puissance_fille_neuve": r["tricheurs"]["temoin_positif"]["taux"]}
    if "artefacts" in r:
        v["artefacts_detectes"] = {a["controle"]: a["taux"] > alpha for a in r["artefacts"]}
        if "tricheurs" in r:
            v["artefacts_detectes"].update({a["controle"]: a["taux"] > alpha for a in r["tricheurs"]["artefacts"]})
    echecs = [n for n in ("T1a", "T6", "tricheurs") if n in v and not v[n]["passe"]]
    manquants = [n for n in ("T1a", "T6", "tricheurs") if n not in v]
    v["echecs_fatals"], v["controles_fatals_non_executes"] = echecs, manquants
    v["critere_invalide"] = bool(echecs or manquants)
    return v


def rapport_markdown(r, horodatage):
    v, p = r["verdicts"], r["parametres"]
    lignes = []
    if v["critere_invalide"]:
        lignes.append("# LE CRITÈRE EST INVALIDÉ : échec fatal (" + ", ".join(v["echecs_fatals"] + [
            n + " non exécuté" for n in v["controles_fatals_non_executes"]]) + ")\n")
    else:
        lignes.append("# Contrôles fatals du critère par pari : T1a, T6 et la batterie de tricheurs passent "
                      "(simulation, vérité connue)\n")
    lignes.append(f"Horodatage : {horodatage['valeur']} ({horodatage['source']}). Graine maîtresse {p['graine_maitresse']}, "
                  f"{p['repetitions']} répétitions par contrôle, {p['tirages_par_repetition']} tirages frais par répétition, "
                  f"α = {p['alpha']} (seuil de richesse {p['seuil_richesse']:.0f}), lecture {p['lecture']}.")
    lignes.append("Simulation seulement : ces taux valent pour les mondes synthétiques décrits, rien au-delà.\n")
    lignes.append("| contrôle | promotions | taux | borne haute 95 % | log W max observé |")
    lignes.append("|---|---|---|---|---|")
    lignes_tricheurs = r["tricheurs"]["tricheurs"] + [r["tricheurs"]["temoin_positif"]] + r["tricheurs"]["artefacts"]
    for c in r["T1a"] + [r["T6"]] + lignes_tricheurs + r["T1b"] + r["T3"] + r["artefacts"]:
        maximum = c.get("log_richesse_max_observee")
        lignes.append(f"| {c['controle']} | {c['promotions']}/{c['repetitions']} | {c['taux']:.4f} | "
                      f"{c['borne_haute_95']:.4f} | {'—' if maximum is None else format(maximum, '.3f')} |")
    t9 = r["T9"]
    lignes.append(f"\nT9 (disjonction partitionnée) : concaténation promue {t9['promotions_concatenation_nul_etendu']}/"
                  f"{t9['repetitions']} contre le nul étendu (log W max {t9['log_richesse_max_concatenation_nul_etendu']:.3f}) ; "
                  f"contre 𝓛 seul, gain médian sur le meilleur parent {t9['gain_naif_sur_meilleur_parent_median']:.2f} nats "
                  f"(positif dans {t9['part_gain_naif_positif']:.0%} des répétitions) ; témoin positif (fille qui prédit du "
                  f"neuf) promu dans {t9['temoin_positif_fille_neuve_taux_promotion']:.1%} des répétitions.\n")
    lignes.append("## Verdicts\n")
    lignes.append(f"- T1a : {'passe' if v['T1a']['passe'] else 'ÉCHOUE'} (taux max {v['T1a']['taux_max']:.4f}).")
    lignes.append(f"- T6 : {'passe' if v['T6']['passe'] else 'ÉCHOUE'} (taux {v['T6']['taux']:.4f}).")
    t = v["tricheurs"]
    lignes.append(f"- Tricheurs scriptés (filles sans contenu nouveau, nul augmenté des parents et enveloppes, marge "
                  f"2δ₀ = {2 * p['delta0_filles']}) : {'passe' if t['passe'] else 'ÉCHOUE'} (taux max {t['taux_max']:.4f}"
                  + (f" ; promus au-delà de α : {t['tricheurs_promus_au_dela_de_alpha']}" if not t["passe"] else "")
                  + f") ; puissance sur une fille réellement neuve : {t['puissance_fille_neuve']:.3f}.")
    lignes.append(f"- T1b : taux de l'oracle aveugle de la dérive {v['T1b']['taux_oracle_aveugle']:.4f} — "
                  + ("la bibliothèque suffit (≤ 2α)." if v["T1b"]["bibliotheque_suffit"] else
                     "**la bibliothèque ne suffit pas** contre une dérive non modélisée (> 2α) : une fiche aveugle au "
                     "domaine qui suit la dérive serait promue ; il faut ajouter une famille de dérive à 𝓛 ou borner "
                     "les mondes où le pôle s'applique."))
    lignes.append(f"- T3 : {'passe' if v['T3']['passe'] else 'ÉCHOUE'} (net faux, taux max {v['T3']['taux_max_net_faux']:.4f} ; "
                  f"puissance net vrai : {v['T3']['puissance_net_vrai']}).")
    lignes.append(f"- T9 : {'passe' if v['T9']['passe'] else 'ÉCHOUE'} (taux {v['T9']['taux']:.4f}).")
    lignes.append("- Artefacts (critères cassés) détectés : "
                  + ", ".join(f"{n} → {'détecté' if d else 'NON détecté'}" for n, d in v["artefacts_detectes"].items()) + ".")
    return "\n".join(lignes) + "\n"
