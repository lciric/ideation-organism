"""Lecture de l'épreuve hors ligne « W2 gradué » (v1, fichier neuf, R12 ; changement C1 du texte de l'épreuve
`epreuve-w2g-dose-v1`, annexe) : lit la sortie **scellée** de `demonstrations/epreuve_w2g_dose_v1.py` et le texte scellé dont
l'empreinte a fait la graine, applique les gardes 1 à 6 du texte (§ 6), calcule l'intervalle de Wilson à 95 %
(`attaque_goodhart_v2.wilson`) des quatre lignes (a) à (d) à chaque dose, recalcule λ\\* depuis les comptes par la règle du texte
(§ 2) et **s'arrête** si son λ\\* diffère de celui que le script de l'épreuve a imprimé ; écrit une lecture JSON neuve, scellée
(compagnon `.sha256`, refus d'écraser), et l'imprime. Hors de la fermeture gelée du chemin réel (aucun lanceur ne l'importe).

Ce script **ne décide rien** : il lit, vérifie et recopie ; λ\\* remplit le marqueur `DOSE_LAMBDA` du préenregistrement par la
main de la mère, après contre-lecture.

Règle de choix (texte § 2, recopiée du brouillon 3, l. 126) : la plus petite dose **non nulle** de la grille à laquelle
promues(a) / n ≥ 0,80 (« au moins 800 sur 1 000 », comparé en entiers : 5·promues(a) ≥ 4·n) **et** promues(b) = 0, à la même
dose ; seules les doses complètes comptent ; la dose 0 est un contrôle, jamais choisissable.

Gardes (texte § 6 ; toute garde qui refuse : arrêt sans λ\\*, aucun chiffre écrit dans la lecture, motif nommé) :
1. sortie absente ou illisible : `epreuve-w2g-dose-v1.json`, `manifeste.json`, `epreuve-w2g-dose-v1-table.txt` ou la console
   absents, compagnon non conforme (`verifier_scelle` faux), JSON illisible ou de forme inattendue, table différente de celle du
   JSON, console sans exactement une ligne « code N », code de sortie ≠ 0 (autre que 3 et 124, qui relèvent de la garde 2) ;
2. durée dépassée et totalité : code 3 ou 124 à la console, `arret` non nul ; les 11 doses de `GRILLE_DOSES_W2G` (0 comprise)
   présentes dans `resultats`, dans l'ordre, égales au champ `doses` ; chacune `complete`, `repetitions` = attendues sur la dose
   et sur les quatre lignes (une dose jamais commencée est **absente** de la sortie d'`assembler`, non « incomplète » : M-3) ;
3. graine non dérivée et réglages (chemins exacts, M-4 ; le manifeste range tout sous `reglages`, le fichier de résultats n'a
   pas de champ `texte`) : texte non scellé ; `mode` et `reglages.mode` ≠ « décisif (graine = empreinte du texte scellé) » ;
   `entropie_racine` et `reglages.entropie_racine` ≠ l'entier de l'empreinte du texte ; `reglages.texte.sha256` ≠ cette
   empreinte ; `reglages.texte.chemin` ≠ le texte lu ; entropie < 2⁶⁴ ; `doses` et `reglages.doses` ≠ la grille ;
   `repetitions` et `reglages.repetitions` ≠ attendues ; `reglages.processus` ≠ attendus ; `reglages.duree_max_s` ≠
   `--duree-max-attendue` (fixée par le texte scellé) ; `reglages.python`, `reglages.numpy`, `reglages.modules_sha256`,
   `reglages.lignes`, `epreuve` différents de la section 4 ; `regle_de_choix` et `reglages.regle_de_choix` ≠ (0,8 ; 0) ;
   incohérence entre les deux fichiers sur `mode`, `entropie_racine`, `repetitions`, `doses`, `regle_de_choix` ;
4. vérité servie : une clé dont le **nom** est « verite » (accents et casse ignorés) ou « N » (exact), à toute profondeur, dans
   l'un des deux fichiers (égalité de nom, jamais sous-chaîne, jamais dans les valeurs) ;
5. défaut du certificat : à la dose 0, (a) > 0 ou (b) > 0 ; à toute dose, (b) > 0 ;
6. instrument : une loi du monde refusée par la grammaire servie à une dose ; λ\\* recalculé ≠ λ\\* imprimé par le script ;
   dose 0 proposée par le script (`choisir_dose` ne l'exclut pas ; le recalcul l'exclut) ; cœurs lus par ce lecteur
   (`attaque_goodhart_v2.py`, `attaque_goodhart_v5.py`) d'empreinte différente de la section 4.
Ordre : garde 1 seule (sans elle rien n'est lisible) ; puis les gardes 2, 3 et 4 ensemble (forme et provenance, aucun compte lu :
tous leurs motifs sont rapportés, la lecture d'arrêt nomme la plus petite) ; puis 5 ; puis 6.
Des évaluations impossibles ne sont pas un arrêt : comptées, rapportées, « audit écrit requis avant report de λ\\* » (λ\\* inchangé).

Codes de sortie :
- 0 : lecture écrite, λ\\* lu (gardes passées, λ\\* recalculé égal au λ\\* imprimé) ;
- 2 : arrêt de garde (motif nommé à l'erreur standard ; une lecture « arrêt de garde » sans chiffre est écrite si le chemin de
  lecture est libre) ;
- 3 : lecture écrite, aucune dose de la grille ne satisfait la règle : pas de λ\\*, préenregistrement non scellable, nœud de Lazar ;
- 4 : usage (arguments, chemin de lecture déjà pris ou dans le dossier de sortie scellé) : rien n'est lu, rien n'est écrit.
`--help` rend 0 sans rien lire ni écrire ; le code 1 n'est jamais rendu volontairement (exception non prévue de Python).

Usage : python3 -I -B demonstrations/lecture_epreuve_w2g_dose_v1.py DOSSIER_DE_SORTIE --texte TEXTE_SCELLE --console CONSOLE_SCELLEE
        --lecture LECTURE_NEUVE.json --duree-max-attendue S [--repetitions-attendues 1000] [--processus-attendus 4]
"""

import argparse
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole import attaque_goodhart_v2 as ag  # noqa: E402
from pole import attaque_goodhart_v5 as a5  # noqa: E402
from pole.outils import ecrire_json_scelle, normaliser_texte, sha256_fichier, verifier_scelle  # noqa: E402

VERSION = "lecture-epreuve-w2g-dose-v1"
EPREUVE = "epreuve-w2g-dose-v1"
CODE_LAMBDA = 0
CODE_GARDE = 2
CODE_AUCUNE_DOSE = 3
CODE_USAGE = 4

# --- ce que la section 4 du texte fixe (comparé tel quel) ----------------------------------------------------------------------
MODE_DECISIF = "décisif (graine = empreinte du texte scellé)"
PYTHON = "3.13.18"
NUMPY = "2.5.3"
LIGNES = ("monde|v9", "recombinaison|v9", "recombinaison|ancien", "monde|v8_information")
NOMS_LIGNES = {"monde|v9": "(a) loi du monde sous v9", "recombinaison|v9": "(b) recombinaison pure sous v9",
               "recombinaison|ancien": "(c) recombinaison pure sous v8", "monde|v8_information": "(d) loi du monde sous v8"}
SEUIL_NUMERATEUR, SEUIL_DENOMINATEUR = 4, 5  # promues(a) / n ≥ 0,80, en entiers
SEUIL_P10 = 0.50  # brouillon 3 l. 118 : taux(v8, témoin, 1) ≥ 0,50
SEUIL_LIMITE = 0.80  # borne basse de Wilson de (a) à λ* sous 0,80 : « λ* à la limite » (λ* inchangé)
MODULES_SHA256 = {
    "pole/attaque_goodhart_v5.py": "8692746a1b02b15465062423d1f05e2084ce1d1861c979316ce1a5ef4384ba15",
    "pole/attaque_goodhart_v4.py": "0077a6470781b8cd9e0599232ddd52e3601c8c4c8735a5cfcf817800bda3bb5c",
    "pole/attaque_goodhart_v2.py": "3c9de8b83b6fcf198d12cacf6a6738c2fc3fe4ade9391f943b3924592959e703",
    "pole/nul_v9.py": "7ae450df2482246122bf9fbcf0fa5ef30b4a7e4c6f0d09531e83af048e46ee95",
    "demonstrations/banc_tricheurs_v9.py": "7e4bff5995df2a7d62a4f5a2f5f9176da614e657a55b05183325fa2fc6e24e44",
    "demonstrations/banc_tricheurs_v8.py": "0be47e4b5916a98499faf9c40d65369b41e3a5463d7ab444ed18ba18bba08c03",
    "demonstrations/banc_tricheurs_v7.py": "ef016d250b7b503f705dc95919719c68c8f968534fd901df7364a6062d67cf12",
    "demonstrations/epreuve_w2g_dose_v1.py": "c691a43d9905e91a0ba91ddfef785e53a091768fa7dcd3007f03066aeef10dda",
}
REGLE_DE_CHOIX = {"seuil_promotion_monde_v9": 0.8, "promotions_recombinaison_v9_max": 0}
FICHIER_SORTIE, FICHIER_MANIFESTE, FICHIER_TABLE = "epreuve-w2g-dose-v1.json", "manifeste.json", "epreuve-w2g-dose-v1-table.txt"
CLES_RAPPORT = ("epreuve", "mode", "entropie_racine", "repetitions", "doses", "arret", "resultats", "regle_de_choix",
                "dose_proposee_par_la_regle", "table")
CLES_RESULTAT = ("dose", "repetitions", "complete", "lignes", "ecart_kl_vers_w2_moyen", "grammaire_servie_refusee")
CLES_LIGNE = ("promues", "repetitions", "taux", "clopper_pearson_95", "evaluations_impossibles", "log_w_max_mediane")
MENTION_EXPLORATOIRE = ("chiffres exploratoires (graine 20261108, texte § 3) : à information seulement, jamais combinés à cette "
                        "lecture (ni sommés, ni moyennés, ni pris pour confirmer une dose)")


class GardeRefusee(Exception):
    """Une ou plusieurs gardes du texte (§ 6) refusent : arrêt sans λ*. `motifs` : liste de (garde, motif, détail) ;
    `garde` : la plus petite garde qui refuse."""

    def __init__(self, motifs):
        self.motifs = list(motifs)
        self.garde = min(g for g, _, _ in self.motifs)
        super().__init__(" ; ".join(f"garde {g} : {m} ({d})" for g, m, d in self.motifs))


def _refus(garde, motifs):
    """(motif, détail)… d'une seule garde → GardeRefusee."""
    return GardeRefusee([(garde, m, d) for m, d in motifs])


class UsageRefuse(Exception):
    """Arguments ou chemin de lecture refusés : rien n'est lu ni écrit."""


class _Analyseur(argparse.ArgumentParser):
    def error(self, message):
        raise UsageRefuse(message)


# --- petits outils ---------------------------------------------------------------------------------------------------------------
def _entier(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _nombre(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _refuser_constante(nom):
    raise ValueError(f"constante non JSON {nom!r}")


def _sans_doublon(paires):
    vues = {}
    for k, v in paires:
        if k in vues:
            raise ValueError(f"clé en double {k!r}")
        vues[k] = v
    return vues


def lire_json(chemin):
    """JSON strict : ni NaN ni infini, aucune clé en double ; lève ValueError sinon."""
    with open(chemin, encoding="utf-8") as f:
        return json.load(f, parse_constant=_refuser_constante, object_pairs_hook=_sans_doublon)


def cles_interdites(objet, chemin="$"):
    """Chemins des clés « verite » (accents et casse ignorés) ou « N » (exacte), à toute profondeur."""
    trouvees = []
    if isinstance(objet, dict):
        for k, v in objet.items():
            if isinstance(k, str) and (normaliser_texte(k) == "verite" or k == "N"):
                trouvees.append((k, f"{chemin}.{k}"))
            trouvees += cles_interdites(v, f"{chemin}.{k}")
    elif isinstance(objet, list):
        for i, v in enumerate(objet):
            trouvees += cles_interdites(v, f"{chemin}[{i}]")
    return trouvees


def lire_code_console(chemin):
    """Le code de sortie écrit par la commande du texte (§ 4) : exactement une ligne « code N » ; ValueError sinon."""
    with open(chemin, encoding="utf-8") as f:
        lignes = [x.strip() for x in f.read().splitlines()]
    codes = [x for x in lignes if x.startswith("code ") and x[5:].lstrip("-").isdigit()]
    if len(codes) != 1:
        raise ValueError(f"exactement une ligne « code N » attendue à la console, {len(codes)} trouvée(s)")
    return int(codes[0][5:])


def wilson(promues, n):
    lo, hi = ag.wilson(promues, n)
    return [lo, hi]


def lambda_recalcule(resultats):
    """Règle du texte (§ 2) sur les comptes : plus petite dose > 0, complète, avec 5·promues(a) ≥ 4·n et promues(b) = 0."""
    for r in sorted(resultats, key=lambda x: x["dose"]):
        if r["dose"] <= 0 or not r["complete"]:
            continue
        a, b = r["lignes"]["monde|v9"], r["lignes"]["recombinaison|v9"]
        n = a["repetitions"]
        if n > 0 and SEUIL_DENOMINATEUR * a["promues"] >= SEUIL_NUMERATEUR * n and b["promues"] == 0:
            return r["dose"]
    return None


# --- gardes ------------------------------------------------------------------------------------------------------------------
def garde_1(dossier, console):
    """Fichiers présents, scellés, lisibles, de la forme attendue ; code de la console. Rend (rapport, manifeste, code)."""
    chemins = {"sortie": os.path.join(dossier, FICHIER_SORTIE), "manifeste": os.path.join(dossier, FICHIER_MANIFESTE),
               "table": os.path.join(dossier, FICHIER_TABLE), "console": console}
    absents = [f"{nom} : {p}" for nom, p in chemins.items() if not os.path.isfile(p)]
    if absents:
        raise _refus(1, [("sortie_absente", x) for x in absents])
    non_scelles = [f"{nom} : {p}" for nom, p in chemins.items() if not verifier_scelle(p)]
    if non_scelles:
        raise _refus(1, [("compagnon", x) for x in non_scelles])
    try:
        rapport, manif = lire_json(chemins["sortie"]), lire_json(chemins["manifeste"])
        code = lire_code_console(console)
        with open(chemins["table"], encoding="utf-8") as f:
            texte_table = f.read()
    except (ValueError, UnicodeDecodeError) as e:
        raise _refus(1, [("illisible", str(e))]) from None
    motifs = verifier_forme(rapport, manif)
    if motifs:
        raise _refus(1, motifs)
    if texte_table != rapport["table"] + "\n":
        raise _refus(1, [("table", "la table scellée diffère de la table du JSON")])
    if code not in (0, 3, 124):
        raise _refus(1, [("code_de_sortie", f"code {code} à la console (attendu 0)")])
    return rapport, manif, code


def verifier_forme(rapport, manif):
    motifs = []
    if not isinstance(rapport, dict) or not isinstance(manif, dict):
        return [("forme", "sortie et manifeste : objets JSON attendus")]
    manquantes = [k for k in CLES_RAPPORT if k not in rapport]
    if manquantes:
        motifs.append(("forme", f"sortie : clés manquantes {manquantes}"))
    if not isinstance(manif.get("reglages"), dict):
        motifs.append(("forme", "manifeste : « reglages » manquant"))
    if motifs:
        return motifs
    if not isinstance(rapport["table"], str) or not isinstance(rapport["doses"], list) or not isinstance(rapport["resultats"], list):
        return [("forme", "sortie : « table » texte, « doses » et « resultats » listes attendus")]
    for i, r in enumerate(rapport["resultats"]):
        if not isinstance(r, dict) or any(k not in r for k in CLES_RESULTAT):
            motifs.append(("forme", f"resultats[{i}] : clés {list(CLES_RESULTAT)} attendues"))
            continue
        n = r["repetitions"]
        if not _nombre(r["dose"]) or not _entier(n) or n < 1 or not isinstance(r["complete"], bool) \
                or not _entier(r["grammaire_servie_refusee"]) or r["grammaire_servie_refusee"] < 0 \
                or not (r["ecart_kl_vers_w2_moyen"] is None or _nombre(r["ecart_kl_vers_w2_moyen"])):
            motifs.append(("forme", f"resultats[{i}] : dose, répétitions, complète, grammaire ou écart de type inattendu"))
            continue
        if not isinstance(r["lignes"], dict) or sorted(r["lignes"]) != sorted(LIGNES):
            motifs.append(("forme", f"resultats[{i}] : lignes {list(LIGNES)} attendues"))
            continue
        for k in LIGNES:
            x = r["lignes"][k]
            if not isinstance(x, dict) or any(c not in x for c in CLES_LIGNE):
                motifs.append(("forme", f"resultats[{i}].{k} : clés {list(CLES_LIGNE)} attendues"))
                continue
            p = x["promues"]
            if not _entier(p) or not 0 <= p <= n or x["repetitions"] != n or not _entier(x["repetitions"]):
                motifs.append(("forme", f"resultats[{i}].{k} : promues entier dans [0 ; n] et n égal à celui de la dose attendus"))
            elif not _nombre(x["taux"]) or x["taux"] != p / n:
                motifs.append(("forme", f"resultats[{i}].{k} : taux ≠ promues / n"))
            elif not _entier(x["evaluations_impossibles"]) or not 0 <= x["evaluations_impossibles"] <= n:
                motifs.append(("forme", f"resultats[{i}].{k} : évaluations impossibles entier dans [0 ; n] attendu"))
            elif not (isinstance(x["clopper_pearson_95"], list) and len(x["clopper_pearson_95"]) == 2
                      and all(_nombre(v) for v in x["clopper_pearson_95"])):
                motifs.append(("forme", f"resultats[{i}].{k} : Clopper-Pearson [bas, haut] attendu"))
            elif not (x["log_w_max_mediane"] is None or _nombre(x["log_w_max_mediane"])):
                motifs.append(("forme", f"resultats[{i}].{k} : médiane de log W nombre ou nulle attendue"))
    return motifs


def garde_2(rapport, code, repetitions):
    """Durée et totalité (texte § 6, garde 2, et majeur M-3 de la contre-lecture) : les 11 doses de la grille présentes dans
    `resultats`, dans l'ordre, chacune `complete` et à `repetitions` attendues sur la dose et sur les quatre lignes (a) à (d).
    Rend la liste des (motif, détail)."""
    motifs = []
    if code == 3:
        motifs.append(("code_3", "arrêt du script à la durée maximale (code 3 à la console)"))
    if code == 124:
        motifs.append(("delai_externe", "délai externe atteint (code 124 à la console)"))
    if rapport["arret"] is not None:
        motifs.append(("arret", f"« arret » non nul : {rapport['arret']!r}"))
    grille = list(a5.GRILLE_DOSES_W2G)
    presentes = [r["dose"] for r in rapport["resultats"]]
    if presentes != grille:
        absentes = [d for d in grille if d not in presentes]
        en_trop = [d for d in presentes if d not in grille]
        motifs.append(("dose_absente", f"resultats : {len(presentes)} doses sur {len(grille)} ; absentes {absentes}, "
                                       f"hors grille {en_trop}, ordre {'conforme' if sorted(presentes) == presentes else 'non trié'}"))
    if presentes != rapport["doses"]:
        motifs.append(("dose_manquante", "les doses de « resultats » ne sont pas celles du champ « doses », dans l'ordre"))
    for r in rapport["resultats"]:
        lignes_n = sorted({x["repetitions"] for x in r["lignes"].values()})
        if r["complete"] is not True or r["repetitions"] != repetitions or lignes_n != [repetitions]:
            motifs.append(("dose_incomplete", f"dose {r['dose']} : complete = {r['complete']}, répétitions {r['repetitions']} "
                                              f"(lignes {lignes_n}) ; attendues {repetitions}"))
    return motifs


def _champ(objet, chemin):
    """Valeur au chemin pointé (« reglages.texte.sha256 ») ou None."""
    for morceau in chemin.split("."):
        if not isinstance(objet, dict) or morceau not in objet:
            return None
        objet = objet[morceau]
    return objet


def garde_3(rapport, manif, texte, repetitions, processus, duree_max):
    """Graine dérivée et réglages (texte § 6, garde 3, et majeur M-4) : chemins exacts — manifeste `reglages.*`, fichier de
    résultats à la racine (il n'a pas de champ `texte`). Rend (liste des (motif, détail), empreinte du texte ou None)."""
    if not os.path.isfile(texte) or not verifier_scelle(texte):
        return [("texte_non_scelle", f"texte scellé exigé (compagnon .sha256 conforme) : {texte}")], None
    empreinte = sha256_fichier(texte)
    entier = int(empreinte, 16)
    m = lambda chemin: _champ(manif, chemin)  # noqa: E731
    motifs = []
    for champ in ("mode", "entropie_racine", "repetitions", "doses", "regle_de_choix"):
        if rapport[champ] != m(f"reglages.{champ}"):
            motifs.append(("incoherence_fichiers", f"« {champ} » du fichier de résultats {rapport[champ]!r} ≠ "
                                                   f"« reglages.{champ} » du manifeste {m('reglages.' + champ)!r}"))
    if rapport["mode"] != MODE_DECISIF or m("reglages.mode") != MODE_DECISIF:
        motifs.append(("mode", f"mode {rapport['mode']!r} (reglages.mode {m('reglages.mode')!r}), attendu {MODE_DECISIF!r}"))
    if rapport["entropie_racine"] != str(entier) or m("reglages.entropie_racine") != str(entier):
        motifs.append(("entropie", "entropie_racine (fichier de résultats ou reglages.entropie_racine) ≠ l'entier gros-boutiste "
                                   "de l'empreinte du texte scellé"))
    if m("reglages.texte.sha256") != empreinte:
        motifs.append(("texte_sha256", f"reglages.texte.sha256 {m('reglages.texte.sha256')!r} ≠ empreinte du texte {empreinte[:12]}…"))
    chemin = m("reglages.texte.chemin")
    if not isinstance(chemin, str) or os.path.realpath(chemin) != os.path.realpath(texte):
        motifs.append(("texte_chemin", f"reglages.texte.chemin {chemin!r} ≠ texte lu {os.path.abspath(texte)!r}"))
    try:
        ag.verifier_entropie(int(rapport["entropie_racine"]), decisif=True)
    except (ValueError, TypeError) as e:
        motifs.append(("entropie_sous_2_64", str(e)))
    grille = list(a5.GRILLE_DOSES_W2G)
    if rapport["doses"] != grille or m("reglages.doses") != grille:
        motifs.append(("grille", f"doses {rapport['doses']} (reglages.doses {m('reglages.doses')}), attendues {grille}"))
    if not _entier(rapport["repetitions"]) or not (rapport["repetitions"] == repetitions == m("reglages.repetitions")):
        motifs.append(("repetitions", f"repetitions {rapport['repetitions']} (reglages.repetitions {m('reglages.repetitions')}), "
                                      f"attendues {repetitions}"))
    if not _entier(m("reglages.processus")) or m("reglages.processus") != processus:
        motifs.append(("processus", f"reglages.processus {m('reglages.processus')}, attendus {processus}"))
    if not _nombre(m("reglages.duree_max_s")) or m("reglages.duree_max_s") != duree_max:
        motifs.append(("duree_max", f"reglages.duree_max_s {m('reglages.duree_max_s')}, attendue {duree_max}"))
    if m("reglages.python") != PYTHON or m("reglages.numpy") != NUMPY:
        motifs.append(("versions", f"reglages.python {m('reglages.python')}, reglages.numpy {m('reglages.numpy')} ; "
                                   f"attendus {PYTHON}, {NUMPY}"))
    modules = m("reglages.modules_sha256")
    if modules != MODULES_SHA256:
        mm = modules if isinstance(modules, dict) else {}
        ecarts = sorted(set(MODULES_SHA256) ^ set(mm)) + sorted(k for k in set(MODULES_SHA256) & set(mm) if mm[k] != MODULES_SHA256[k])
        motifs.append(("modules", f"reglages.modules_sha256 différent de la section 4 : {ecarts}"))
    if rapport["epreuve"] != EPREUVE or m("reglages.epreuve") != EPREUVE:
        motifs.append(("epreuve", f"epreuve {rapport['epreuve']!r} (reglages.epreuve {m('reglages.epreuve')!r}), attendue {EPREUVE!r}"))
    if m("reglages.lignes") != list(LIGNES):
        motifs.append(("lignes", f"reglages.lignes {m('reglages.lignes')}, attendues {list(LIGNES)}"))
    for quoi, r in (("regle_de_choix (fichier de résultats)", rapport["regle_de_choix"]),
                    ("reglages.regle_de_choix (manifeste)", m("reglages.regle_de_choix"))):
        if not isinstance(r, dict) or any(k not in r or not _nombre(r[k]) or r[k] != v for k, v in REGLE_DE_CHOIX.items()):
            motifs.append(("regle", f"{quoi} {r!r}, attendue {REGLE_DE_CHOIX}"))
    return motifs, empreinte


def garde_4(rapport, manif):
    """Égalité du **nom de clé** (« verite », accents et casse ignorés ; « N » exacte), à toute profondeur des deux fichiers ;
    jamais une recherche de sous-chaîne, jamais dans les valeurs (contre-lecture m-8)."""
    return [("cle_verite" if k != "N" else "cle_N", f"{quoi} : {chemin}")
            for quoi, objet in (("epreuve-w2g-dose-v1.json", rapport), ("manifeste.json", manif)) for k, chemin in cles_interdites(objet)]


def garde_5(rapport):
    motifs = []
    for r in rapport["resultats"]:
        a, b = r["lignes"]["monde|v9"]["promues"], r["lignes"]["recombinaison|v9"]["promues"]
        if r["dose"] == 0 and a > 0:
            motifs.append(("monde_promu_dose_0", f"dose 0 : (a) {a} promue(s) (la loi du monde est W2, membre du nul v9)"))
        if b > 0:
            motifs.append(("recombinaison_promue", f"dose {r['dose']} : (b) {b} promue(s) (membre du nul v9 promu)"))
    if motifs:
        raise _refus(5, motifs)


def garde_6(rapport):
    """Rend λ* recalculé (égal au λ* imprimé)."""
    motifs = []
    for nom, p in (("pole/attaque_goodhart_v2.py", ag.__file__), ("pole/attaque_goodhart_v5.py", a5.__file__)):
        if sha256_fichier(p) != MODULES_SHA256[nom]:
            motifs.append(("lecteur", f"{nom} lu par ce lecteur ({p}) : empreinte différente de la section 4"))
    for r in rapport["resultats"]:
        if r["grammaire_servie_refusee"] != 0:
            motifs.append(("grammaire_refusee", f"dose {r['dose']} : {r['grammaire_servie_refusee']} loi(s) du monde refusée(s) "
                                                "par la grammaire servie"))
    lam = lambda_recalcule(rapport["resultats"])
    imprime = rapport["dose_proposee_par_la_regle"]
    if _nombre(imprime) and imprime == 0:
        motifs.append(("lambda_dose_nulle", "le script propose la dose 0 (`choisir_dose` ne l'exclut pas) : jamais choisissable"))
    if not ((lam is None and imprime is None) or (lam is not None and _nombre(imprime) and imprime == lam)):
        motifs.append(("desaccord_lambda", f"λ* imprimé par le script {imprime!r}, recalculé {lam!r}"))
    if motifs:
        raise _refus(6, motifs)
    return lam


# --- lecture -------------------------------------------------------------------------------------------------------------------
def par_dose(rapport):
    sortie = []
    for r in rapport["resultats"]:
        lignes = {}
        for k in LIGNES:
            x = r["lignes"][k]
            lignes[k] = {"nom": NOMS_LIGNES[k], "promues": x["promues"], "repetitions": x["repetitions"], "taux": x["taux"],
                         "wilson_95": wilson(x["promues"], x["repetitions"]),
                         "clopper_pearson_95_imprime": x["clopper_pearson_95"],
                         "evaluations_impossibles": x["evaluations_impossibles"]}
        lignes["monde|v9"]["log_w_max_mediane"] = r["lignes"]["monde|v9"]["log_w_max_mediane"]
        sortie.append({"dose": r["dose"], "repetitions": r["repetitions"], "complete": r["complete"],
                       "ecart_kl_vers_w2_moyen": r["ecart_kl_vers_w2_moyen"],
                       "grammaire_servie_refusee": r["grammaire_servie_refusee"], "lignes": lignes})
    return sortie


def _int(w):
    return f"[{w[0]:.3f} ; {w[1]:.3f}]"


def table(doses, lam):
    lignes = ["dose λ | écart KL moyen | (a) monde sous v9 : promues/n, taux, Wilson 95, CP95 imprimé | (b) recombinaison sous v9 : "
              "promues/n, Wilson 95 | (c) recombinaison sous v8 : promues/n, taux, Wilson 95 | (d) monde sous v8 : promues/n, taux, "
              "Wilson 95 | log W méd. (a) | éval. impossibles | grammaire refusée | complète"]
    for d in doses:
        a, b, c, dd = (d["lignes"][k] for k in LIGNES)
        imp = sum(x["evaluations_impossibles"] for x in d["lignes"].values())
        lignes.append(f"{d['dose']:.2f} | {d['ecart_kl_vers_w2_moyen']} | {a['promues']}/{a['repetitions']}, {a['taux']:.3f}, "
                      f"{_int(a['wilson_95'])}, {_int(a['clopper_pearson_95_imprime'])} | {b['promues']}/{b['repetitions']}, "
                      f"{_int(b['wilson_95'])} | {c['promues']}/{c['repetitions']}, {c['taux']:.3f}, {_int(c['wilson_95'])} | "
                      f"{dd['promues']}/{dd['repetitions']}, {dd['taux']:.3f}, {_int(dd['wilson_95'])} | {a['log_w_max_mediane']} | "
                      f"{imp} | {d['grammaire_servie_refusee']} | {'oui' if d['complete'] else 'non'}")
    lignes.append("règle du texte (§ 2) recalculée — plus petite dose > 0 avec (a) ≥ 0,80 et (b) = 0 : "
                  + (f"λ* = {lam}" if lam is not None else "aucune dose de la grille (pas de λ*, nœud de Lazar)"))
    return "\n".join(lignes)


def lire(dossier, texte, console, repetitions, processus, duree_max):
    """Applique les gardes 1 à 6 dans l'ordre et rend le contenu de la lecture (λ* ou aucune dose). Lève `GardeRefusee`."""
    rapport, manif, code = garde_1(dossier, console)
    m3, empreinte = garde_3(rapport, manif, texte, repetitions, processus, duree_max)
    motifs = ([(2, m, d) for m, d in garde_2(rapport, code, repetitions)] + [(3, m, d) for m, d in m3]
              + [(4, m, d) for m, d in garde_4(rapport, manif)])
    if motifs:  # gardes 2 à 4 (forme et provenance, aucun compte lu) : tous leurs motifs rapportés ensemble
        raise GardeRefusee(motifs)
    garde_5(rapport)
    lam = garde_6(rapport)
    doses = par_dose(rapport)
    impossibles = sum(x["evaluations_impossibles"] for d in doses for x in d["lignes"].values())
    lecture = {"gardes": {str(i): "passée" for i in range(1, 7)}, "texte_sha256": empreinte,
               "par_dose": doses, "lambda_imprime_par_le_script": rapport["dose_proposee_par_la_regle"],
               "lambda_recalcule": lam, "accord_lambda": True, "lambda_etoile": lam,
               "evaluations_impossibles": impossibles,
               "audit_requis": ("évaluations impossibles : audit écrit requis avant le report de λ* au préenregistrement (λ* "
                                "inchangé)") if impossibles else None,
               "mention_exploratoire": MENTION_EXPLORATOIRE, "table": table(doses, lam)}
    if lam is None:
        lecture["statut"] = ("aucune dose de la grille ne satisfait la règle : pas de λ*, le préenregistrement reste non "
                             "scellable, nœud de Lazar")
        lecture["a_la_limite"] = None
        lecture["p10"] = None
        return lecture, CODE_AUCUNE_DOSE
    d = next(x for x in doses if x["dose"] == lam)
    wa, c = d["lignes"]["monde|v9"]["wilson_95"], d["lignes"]["recombinaison|ancien"]
    lecture["statut"] = f"λ* = {lam} lu (recalculé égal au λ* imprimé par le script) ; imprimé, pas décidé"
    lecture["a_la_limite"] = ({"borne_basse_wilson_a": wa[0], "mention": "λ* à la limite (borne basse de Wilson de (a) sous 0,80) ; "
                               "λ* ne change pas"} if wa[0] < SEUIL_LIMITE else
                              {"borne_basse_wilson_a": wa[0], "mention": None})
    lecture["p10"] = {"taux_c": c["taux"], "wilson_95_c": c["wilson_95"],
                      "mention": "P10 tenue par l'oracle" if c["taux"] >= SEUIL_P10 else "P10 en tension à λ*",
                      "reserve": ("(c) est un analogue hors ligne (la recombinaison soumise une fois), non la mesure de P10 en "
                                  "course ; cette tension est rapportée, elle ne change pas λ* ; elle va au brouillon 4")}
    return lecture, CODE_LAMBDA


def pieces(dossier, texte, console):
    sortie = {}
    for nom, p in (("sortie", os.path.join(dossier, FICHIER_SORTIE)), ("manifeste", os.path.join(dossier, FICHIER_MANIFESTE)),
                   ("table", os.path.join(dossier, FICHIER_TABLE)), ("console", console), ("texte", texte)):
        sortie[nom] = {"chemin": os.path.abspath(p), "sha256": sha256_fichier(p) if os.path.isfile(p) else None}
    return sortie


def principal(argv=None):
    a = _Analyseur(description="Lecture de l'épreuve hors ligne « W2 gradué » : gardes, Wilson, λ* recalculé")
    a.add_argument("dossier", help="dossier de sortie de l'épreuve (manifeste.json, epreuve-w2g-dose-v1.json, table)")
    a.add_argument("--texte", required=True, help="texte scellé de l'épreuve (sa graine est son empreinte)")
    a.add_argument("--console", required=True, help="console scellée de la commande (une ligne « code N »)")
    a.add_argument("--lecture", required=True, help="chemin neuf de la lecture JSON (refus s'il existe)")
    a.add_argument("--repetitions-attendues", type=int, default=1000)
    a.add_argument("--processus-attendus", type=int, default=4)
    a.add_argument("--duree-max-attendue", type=float, required=True,
                   help="durée maximale (s) fixée par le texte scellé (§ 4), comparée à reglages.duree_max_s ; aucune valeur par défaut")
    try:
        args = a.parse_args(argv)
        if args.repetitions_attendues < 1 or args.processus_attendus < 1:
            raise UsageRefuse("--repetitions-attendues et --processus-attendus : entiers ≥ 1")
        if not args.duree_max_attendue > 0 or args.duree_max_attendue == float("inf"):
            raise UsageRefuse("--duree-max-attendue : nombre fini > 0")
        lecture_abs = os.path.abspath(args.lecture)
        if os.path.lexists(lecture_abs) or os.path.lexists(lecture_abs + ".sha256"):
            raise UsageRefuse(f"lecture déjà écrite : {args.lecture} (on n'écrase jamais)")
        dossier_reel = os.path.realpath(args.dossier)
        if os.path.realpath(os.path.dirname(lecture_abs)).startswith(dossier_reel + os.sep) \
                or os.path.realpath(os.path.dirname(lecture_abs)) == dossier_reel:
            raise UsageRefuse("la lecture ne s'écrit pas dans le dossier de sortie scellé de l'épreuve")
    except UsageRefuse as e:
        print(f"usage refusé : {e}", file=sys.stderr)
        return CODE_USAGE
    entete = {"lecture": VERSION, "lecteur": {"chemin": os.path.abspath(__file__), "sha256": sha256_fichier(os.path.abspath(__file__))},
              "parametres": {"repetitions_attendues": args.repetitions_attendues, "processus_attendus": args.processus_attendus},
              "attendu_section_4": {"mode": MODE_DECISIF, "grille": list(a5.GRILLE_DOSES_W2G), "duree_max_s": args.duree_max_attendue,
                                    "python": PYTHON, "numpy": NUMPY, "modules_sha256": MODULES_SHA256,
                                    "regle_de_choix": dict(REGLE_DE_CHOIX)}}
    try:
        contenu, code = lire(args.dossier, args.texte, args.console, args.repetitions_attendues, args.processus_attendus,
                             args.duree_max_attendue)
    except GardeRefusee as e:
        refus = dict(entete, statut="arrêt de garde : pas de λ*, aucun chiffre lu pour choisir une dose ; sortie rapportée telle quelle",
                     code=CODE_GARDE, garde=e.garde, gardes_refusees=sorted({g for g, _, _ in e.motifs}),
                     motifs=[{"garde": g, "motif": m, "detail": d} for g, m, d in e.motifs],
                     pieces=pieces(args.dossier, args.texte, args.console))
        print(f"arrêt : {e}", file=sys.stderr)
        try:
            empreinte = ecrire_json_scelle(args.lecture, refus)
            print(f"lecture (arrêt de garde) {os.path.abspath(args.lecture)} sha256 {empreinte}", file=sys.stderr)
        except OSError as erreur:
            print(f"lecture d'arrêt non écrite : {erreur}", file=sys.stderr)
        return CODE_GARDE
    lecture = dict(entete, code=code, pieces=pieces(args.dossier, args.texte, args.console), **contenu)
    empreinte = ecrire_json_scelle(args.lecture, lecture)
    print(lecture["table"])
    print(lecture["statut"])
    if lecture["a_la_limite"] and lecture["a_la_limite"]["mention"]:
        print(lecture["a_la_limite"]["mention"])
    if lecture["p10"]:
        print(f"{lecture['p10']['mention']} : (c) {lecture['p10']['taux_c']:.3f} {_int(lecture['p10']['wilson_95_c'])}")
    if lecture["audit_requis"]:
        print(lecture["audit_requis"])
    print(f"lecture {os.path.abspath(args.lecture)} sha256 {empreinte}")
    return code


if __name__ == "__main__":
    sys.exit(principal())
