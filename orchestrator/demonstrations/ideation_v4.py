"""Course d'idéation de l'organisme : lanceur, **version 4** (orchestrateur v52b) — le lanceur de la version 2
(`demonstrations/ideation_v2.py`) **tel quel** (R12 : aucun octet changé), dont l'étage de tests de mort est pris dans
`pole/tests_de_mort_v3.py` (correction de CL16-01 : borne mémoire minimale du bac relevée à 768 Mo).

- Sans `--tests-de-mort`, ce lanceur fait exactement ce que fait la version 2 (mêmes arguments, mêmes sorties).
- Avec `--tests-de-mort N` et `--executeur-tests bwrap`, le bac à sable est **toujours** construit ici, depuis la version 3 de
  l'étage (la version 2 laissait le cœur construire le bac par défaut de `pole/tests_de_mort_v2.py` quand ni utilisateur dédié,
  ni dossier racine, ni option du bac n'étaient donnés) : une borne `--memoire-test-mo` sous 768 Mo est refusée avant la sonde,
  avant tout appel.
- Le mode « juges seulement » reste au lanceur de la version 3 (`demonstrations/ideation_v3.py`), qui refuse `--tests-de-mort`.
- Les lanceurs v1 et v2 restent dans l'arbre (R12) : lancer l'étage par eux donne la borne de 512 Mo de la version 2, à laquelle
  la sonde s'auto-tue (refus, sans risque : CL16-01). Pour l'étage, utiliser ce lanceur.

  python -I -B demonstrations/ideation_v4.py SORTIE_NEUVE … --tests-de-mort N --executeur-tests bwrap --memoire-test-mo 1024 …
"""

import importlib.util
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

_spec = importlib.util.spec_from_file_location("ideation_v2_lanceur_pour_v4", os.path.join(ICI, "ideation_v2.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)  # instance propre à ce lanceur : le module `ideation_v2.py` chargé ailleurs n'est pas touché

from pole import tests_de_mort_v3 as idn_tests  # noqa: E402  (v52b : version 3 de l'étage, CL16-01)

_reglages_v2 = base.reglages_tests_de_mort


def reglages_tests_de_mort(args, externe=None):
    """v52b : les réglages de l'étage de la version 2, avec le vrai bac toujours construit depuis la version 3 de l'étage."""
    r = _reglages_v2(args, externe)
    if r is not None and args.executeur_tests == "bwrap" and not isinstance(r["executeur"], idn_tests.ExecuteurBacASable):
        try:
            r["executeur"] = idn_tests.ExecuteurBacASable(
                delai_s=args.delai_execution_s, memoire_mo=args.memoire_test_mo, utilisateur_bac=args.utilisateur_bac,
                racine_travail=args.dossier_travail_bac, userns_imbriques_permis=args.userns_imbriques_permis,
                memoire_bac_non_bornee_permise=getattr(args, "memoire_bac_non_bornee_permise", False))
        except ValueError as e:
            raise base.idn.CourseInterrompue(f"bac à sable de l'étage : {e}") from e
    return r


# Le lanceur v2 lit ces deux noms à l'appel, dans son propre espace : sur cette instance seulement, ils désignent la version 3.
base.idn_tests = idn_tests
base.reglages_tests_de_mort = reglages_tests_de_mort


def principal(argv=None):
    return base.principal(argv)


if __name__ == "__main__":
    sys.exit(principal())
