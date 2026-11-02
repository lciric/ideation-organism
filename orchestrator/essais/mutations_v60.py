"""Banc de mutations de la v60 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**) — réserve
par empreinte des données tenues à l'écart (`pole/reserve_tenue_a_l_ecart_v60.py`) et oracle du tour fermé
(`pole/oracle_tour_ferme_v60.py`) et lecture gelée (`pole/lecture_tour_ferme_v60.py`) ; essais
`essais/test_v60_reserve_tenue_a_l_ecart.py`, `essais/test_v60_oracle_tour_ferme.py`, `essais/test_v60_lecture_tour_ferme.py`.

Mécanique du banc v56 (`mutations_v56.appliquer` : recompilation en mémoire, substitution, raison attendue de l'échec, défaut du
banc distingué, restauration, témoin avant et après). Seules les mutations de la v60 sont jouées. Aucun fichier n'est modifié.

  python3 -I -B essais/mutations_v60.py [--raisons]      (depuis le dossier orchestrator)
"""

import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v56 as m56  # noqa: E402
from pole import lecture_tour_ferme_v60 as LE  # noqa: E402
from pole import oracle_tour_ferme_v60 as OR  # noqa: E402
from pole import reserve_tenue_a_l_ecart_v60 as RV  # noqa: E402

m55 = m56.m55
T = "essais.test_v60_reserve_tenue_a_l_ecart."
TO = "essais.test_v60_oracle_tour_ferme."
TL = "essais.test_v60_lecture_tour_ferme."
PAS_LEVEE = r"ReserveRefusee not raised"

MUTATIONS_V60 = [
    ("v60 la règle change (module 2 au lieu de 3)", RV, "tache_reservee", "% MODULE == 0", "% 2 == 0",
     [T + "Regle"], r"(True|False) != (True|False)"),
    ("v60 une sortie existante est réutilisée (garde R12 sautée)", RV, "reserver", "if os.path.lexists(sortie):", "if False:",
     [T + "GardesEntree"], r"FileExistsError"),
    ("v60 un lien symbolique est accepté en entrée", RV, "_lire_entree", "if not stat.S_ISREG(st.st_mode):", "if False:",
     [T + "GardesEntree"], PAS_LEVEE),
    ("v60 un identifiant en double est accepté", RV, "reserver", "if ident in vus:", "if False:", [T + "GardesEntree"],
     PAS_LEVEE),
    ("v60 une réserve dégénérée est acceptée", RV, "reserver", "if not t or not reste:", "if False:", [T + "GardesEntree"],
     PAS_LEVEE),
    ("v60 l'empreinte des sorties n'est pas vérifiée au montage", RV, "_lire_verifie", "if sha != sha_attendue:", "if False:",
     [T + "Verification"], PAS_LEVEE),
    ("v60 la règle n'est pas recalculée sur le reste au montage", RV, "verifier_reserve",
     "if any(tache_reservee(e[cle]) for e in reste):", "if False:", [T + "Verification"], PAS_LEVEE),
    ("v60 la liste des tâches réservées n'est pas contre-vérifiée", RV, "verifier_reserve",
     "if sorted({e[cle] for e in t}) != list(taches):", "if False:", [T + "Verification"], PAS_LEVEE),
    ("v60 oracle : G_arch oublie la mise en commun linéaire de l'archive", OR.Oracle, "gain_archive",
     "[self.gain(l) for l in lois] + [self.melange_ajuste(lois)[0]]", "[self.gain(l) for l in lois]",
     [TO + "Mesures"], r"not greater than"),
    ("v60 oracle : G_arch oublie les lois tempérées et inclinées", OR.Oracle, "gain_archive",
     "candidats += [self.temperee_inclinee(l)[0] for l in lois]", "candidats += []", [TO + "Mesures"],
     r"not less than"),
    ("v60 classement : la nouveauté contre l'archive (ΔG) est ignorée", OR, "classer",
     "informative = gain_nat >= G0 and delta_gain_nat >= G0", "informative = gain_nat >= G0", [TO + "Classement"],
     r"False is not true|True is not false"),
    ("v60 classement : une carte du bras recopie-mélange peut être une vraie découverte", OR, "classer",
     'fd = ps and (bras == "recopie_melange" or not informative)', "fd = ps and (not informative)", [TO + "Classement"],
     r"False is not true|True is not false"),
    ("v60 lecture : T2 tolère toute perte de la loi plantée", LE, "lire_etage1",
     'sum(c.get("verdict") == "survit" for c in vraie) >= len(vraie) - 1', 'sum(c.get("verdict") == "survit" for c in vraie) >= 0',
     [TL + "Etage1"], r"True is not false"),
    ("v60 lecture : T5 ignore les fausses découvertes du hasard", LE, "lire_etage1",
     'bras["aleatoire"].get("fd", 0) <= 1 and', "True and", [TL + "Etage1"], r"True is not false"),
    ("v60 lecture : « discrimine » sans écart positif (borne de Newcombe ignorée)", LE, "lire_etage1",
     "elif diff is not None and diff[0] > 0:", "elif diff is not None:", [TL + "Etage1"], r"False is not true"),
    ("v60 lecture : une survivante de génération 2 (T relue) compte comme décisive", LE, "lire_etage2",
     'if c.get("generation") == 1 and ps(c)]', "if ps(c)]", [TL + "Etage2"], r"'P' != 'Z'"),
    ("v60 lecture : promotion comptée sans contre-calcul concordant", LE, "lire_etage2",
     ' \\\n            and c.get("contre_calcul_ok") is True', "", [TL + "Etage2"], r"'P' != 'Z'"),
]


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    noms = sorted({x for m in MUTATIONS_V60 for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS_V60:
        try:
            restaurer = m56.appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  {libelle} : {e}")
            continue
        try:
            n, echecs = m55.jouer(essais)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
        verdict = m55.classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec")
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {m55._derniere_ligne(txt)}")
    apres = m55.jouer(noms)
    total = len(MUTATIONS_V60)
    print(f"mutations v60 : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
