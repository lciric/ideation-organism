"""Essais de l'orchestrateur v52b : correction du constat CL16-01 (borne mémoire minimale du bac, contre-lecture CL16).

CL16-01 : à la borne minimale que la version 2 de l'étage autorise (512 Mo), la sonde des privilèges `disponible()` est tuée
par le groupe de contrôle du bac (code 137) et l'étage est refusé. Aucun essai ne jouait la sonde réelle à cette borne (R5).

- `test_v52b_01` (garde, sans exécution) : la borne minimale est relevée au-dessus de la plus basse mesurée qui tient (640 Mo) ;
  cas sain (à la borne : la garde laisse passer) et artefact (un mégaoctet de moins : refus avant la sonde, motif CL16-01).
- `test_v52b_02` (réel, sous le vrai `bwrap`, utilisateur dédié) : la sonde complète tient **à exactement** la borne minimale,
  trois passages ; aucun groupe de contrôle ni processus de l'utilisateur dédié ne reste.
- `test_v52b_03` (lanceur v4) : avec l'étage et `--executeur-tests bwrap`, le bac est toujours celui de la version 3, même sans
  option du bac (la version 2 laissait alors le cœur construire le bac de la version 2) ; le lanceur v2 n'est pas touché.
- `test_v52b_04` : la version 3 de l'étage est la version 2 telle quelle, sauf la borne et le bac ; le fichier de la version 2
  garde son empreinte de la v51 (R12).

Sans la correction (`ETAGE = tdm2`, sans `ideation_v4.py`), les essais 01, 02 et 03 échouent. Sans `bwrap`, l'essai réel
échoue (jamais ignoré en silence, CL15-04), sauf `POLE_ESSAI_BAC_REEL_NON_JOUE=1`. Aucun réseau, aucune clé, aucun appel payant ;
cibles : dossiers provisoires retirés à la fin.
"""

import hashlib
import importlib.util
import os
import shutil
import time
import types

from essais import test_v7_ideation_v2 as t7
from essais.aides import CasAvecDossier
from essais.test_v47_relais_moisson import RACINE, garde_fou_reseau
from pole import tests_de_mort_v2 as tdm2
from pole import tests_de_mort_v3 as tdm3

ETAGE = tdm3  # l'étage essayé ; la démonstration « sans la correction » met ici `tdm2`
BORNE_LA_PLUS_BASSE_QUI_TIENT_MO = 640  # CL16 (3/3) et session v52b : refus à 512, 544, 576, 608 ; accepté à 640, 768, 1 024
EMPREINTE_ETAGE_V2_V51 = "363a3725"  # préfixe de `pole/tests_de_mort_v2.py` au tableau du LISEZMOI v51 (CL16)


def lanceur(nom):
    spec = importlib.util.spec_from_file_location("lanceur_v52b_" + nom.replace(".", "_"), os.path.join(RACINE, "demonstrations", nom))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def groupes_restants():
    try:
        _version, parent = tdm2.BorneMemoireBac.localiser()
    except (tdm2.EtageRefuse, OSError):
        return []
    return sorted(n for n in os.listdir(parent) if n.startswith(tdm2.BorneMemoireBac.PREFIXE))


def processus_de(uid):
    trouves = []
    for nom in os.listdir("/proc"):
        if nom.isdigit():
            try:
                if os.stat(os.path.join("/proc", nom)).st_uid == uid:
                    trouves.append(int(nom))
            except OSError:
                pass
    return trouves


def executeur_reel_etage(test, etage, memoire_mo, delai=30.0):
    """Comme `t7.executeur_reel`, mais pour l'étage `etage` et la borne `memoire_mo` donnés."""
    if not shutil.which("bwrap"):
        t7.exiger_essai_reel(test, "bwrap absent de cette machine : essai réel à rejouer dans le conteneur de session-depot")
    if os.geteuid() == 0:
        utilisateur, racine = os.environ.get("POLE_ESSAI_UTILISATEUR_BAC"), os.environ.get("POLE_ESSAI_RACINE_TRAVAIL_BAC")
        if not utilisateur:
            if not t7.utilisateur_dedie_possible():
                t7.exiger_essai_reel(test, f"noyau superutilisateur sans setpriv utilisable pour l'identité {t7.UID_ESSAI}")
            utilisateur = t7.UID_ESSAI
        if not racine:
            racine = t7.racine_bac_essai(test, etage.resoudre_utilisateur_bac(utilisateur)[0])
        return etage.ExecuteurBacASable(delai_s=delai, memoire_mo=memoire_mo, utilisateur_bac=utilisateur, racine_travail=racine)
    return etage.ExecuteurBacASable(delai_s=delai, memoire_mo=memoire_mo)


class TestV52bBorneMemoire(CasAvecDossier):

    def setUp(self):
        super().setUp()
        self.garde = garde_fou_reseau()
        self.garde.__enter__()
        self.addCleanup(self.garde.__exit__, None, None, None)

    def faux_bwrap(self):
        """Un fichier qui tient lieu de `bwrap` pour la garde seule (jamais exécuté ici)."""
        chemin = os.path.join(self.tmp, "bwrap-factice")
        with open(chemin, "w") as f:
            f.write("#!/bin/false\n")
        os.chmod(chemin, 0o755)
        return chemin

    def test_v52b_01_borne_minimale_relevee_cas_sain_et_artefact(self):
        """CL16-01 : la borne minimale dépasse la plus basse mesurée qui tient ; à la borne, la garde laisse passer (cas sain) ;
        un mégaoctet de moins, et à 512 Mo (la borne de la version 2), elle refuse avant toute sonde, motif CL16-01 (artefact).
        Une borne levée sur demande expresse (`memoire_bac_non_bornee_permise`) n'est pas concernée."""
        self.assertGreaterEqual(ETAGE.MEMOIRE_BAC_MIN_MO, BORNE_LA_PLUS_BASSE_QUI_TIENT_MO)
        bwrap = self.faux_bwrap()

        def motif(mo, **kw):
            ex = ETAGE.ExecuteurBacASable(bwrap=bwrap, delai_s=5.0, memoire_mo=mo, **kw)
            return ex.verifier_outils()
        self.assertIsNone(motif(ETAGE.MEMOIRE_BAC_MIN_MO))
        self.assertIsNone(motif(ETAGE.MEMOIRE_MO_DEFAUT))
        for mo in (ETAGE.MEMOIRE_BAC_MIN_MO - 1, 512, BORNE_LA_PLUS_BASSE_QUI_TIENT_MO - 32):
            m = motif(mo)
            self.assertIsNotNone(m, f"{mo} Mo : la garde laisse passer une borne où la sonde s'auto-tue (CL16-01)")
            self.assertIn("CL16-01", m)
            self.assertIn(f"{mo} Mo", m)
        self.assertIsNone(motif(512, memoire_bac_non_bornee_permise=True))

    @t7.essai_reel_bwrap
    def test_v52b_02_sonde_reelle_a_exactement_la_borne_minimale(self):
        """CL16-01 (R5) : sous le vrai `bwrap`, utilisateur dédié, groupe de contrôle du bac à exactement `MEMOIRE_BAC_MIN_MO`, la
        sonde complète passe (dont l'artefact `MEMOIRE-BAC` : enfants tués par le groupe), trois fois sur trois ; rien ne reste."""
        for passage in range(3):
            ex = executeur_reel_etage(self, ETAGE, ETAGE.MEMOIRE_BAC_MIN_MO)
            ok, motif = ex.disponible()
            self.assertTrue(ok, f"passage {passage + 1}, {ETAGE.MEMOIRE_BAC_MIN_MO} Mo : {motif}")
            self.assertIn("mémoire du bac entier bornée (groupe de contrôle)", motif)
        fin = time.monotonic() + tdm2.DELAI_RETRAIT_GROUPE_S + 5
        while (groupes_restants() or (os.geteuid() == 0 and processus_de(t7.UID_ESSAI))) and time.monotonic() < fin:
            time.sleep(0.2)
        self.assertEqual(groupes_restants(), [])
        if os.geteuid() == 0:
            self.assertEqual(processus_de(t7.UID_ESSAI), [])

    def test_v52b_03_lanceur_v4_construit_toujours_le_bac_de_la_version_3(self):
        """Le lanceur v4 : avec l'étage et `--executeur-tests bwrap`, sans option du bac comme avec, le bac est celui de la
        version 3 et refuse 512 Mo (motif CL16-01) ; sans l'étage, aucun réglage (la version 2) ; exécuteur factice inchangé ;
        l'instance du lanceur v2 chargée à part garde la version 2 (rien n'est changé hors du lanceur v4)."""
        l4 = lanceur("ideation_v4.py")
        l2 = lanceur("ideation_v2.py")
        self.assertIs(l4.base.idn_tests, tdm3)
        self.assertIs(l2.idn_tests, tdm2)
        bwrap = self.faux_bwrap()

        def args(**kw):
            d = dict(tests_de_mort=1, experimentateur=None, experimentateur_externe=None, executeur_tests="bwrap",
                     delai_execution_s=5.0, memoire_test_mo=512, utilisateur_bac=None, dossier_travail_bac=None,
                     userns_imbriques_permis=False, memoire_bac_non_bornee_permise=False, tranche_exploratoire=None,
                     lecteur_test=None, budget_test_usd=0.5, budget_lecteur_test_usd=0.1, executions_par_fiche=1)
            d.update(kw)
            return types.SimpleNamespace(**d)
        self.assertIsNone(l4.reglages_tests_de_mort(args(tests_de_mort=0)))
        for a in (args(), args(dossier_travail_bac=self.tmp)):
            r = l4.base.reglages_tests_de_mort(a, None)  # le nom que lit `principal` de la version 2, sur l'instance du v4
            ex = r["executeur"]
            self.assertIsInstance(ex, tdm3.ExecuteurBacASable)
            ex.bwrap = bwrap
            self.assertIn("CL16-01", ex.verifier_outils())
            self.assertEqual(ex.description()["memoire_bac_min_mo"], tdm3.MEMOIRE_BAC_MIN_MO)
        r2 = l2.reglages_tests_de_mort(args(), None)
        self.assertIsNone(r2["executeur"])  # la version 2 : le cœur construit son bac par défaut (borne de 512 Mo)
        f = l4.reglages_tests_de_mort(args(executeur_tests="factice"), None)["executeur"]
        self.assertTrue(f.factice)

    def test_v52b_04_version_3_egale_la_version_2_sauf_la_borne(self):
        """R12 : `pole/tests_de_mort_v2.py` garde son empreinte de la v51 ; la version 3 rend les mêmes objets que la version 2 pour
        tout ce que le cœur et le lanceur lisent, sauf `ExecuteurBacASable` (sous-classe) et `MEMOIRE_BAC_MIN_MO`."""
        with open(os.path.join(RACINE, "pole", "tests_de_mort_v2.py"), "rb") as f:
            self.assertTrue(hashlib.sha256(f.read()).hexdigest().startswith(EMPREINTE_ETAGE_V2_V51))
        self.assertEqual(tdm3.MEMOIRE_BAC_MIN_MO_V2, 512)
        self.assertTrue(issubclass(tdm3.ExecuteurBacASable, tdm2.ExecuteurBacASable))
        self.assertIsNot(tdm3.ExecuteurBacASable, tdm2.ExecuteurBacASable)
        for nom in ("BUDGET_LECTEUR_USD_DEFAUT", "BUDGET_TEST_USD_DEFAUT", "DELAI_EXECUTION_S_DEFAUT", "EXECUTIONS_PAR_FICHE_DEFAUT",
                    "ExecuteurFactice", "MEMOIRE_MO_DEFAUT", "NOMBRE_MAX", "TITRE_SECTION_PREREG", "comparer", "sonde_pour",
                    "evaluer_sonde_privileges", "ENFANTS_ESSAI_MEMOIRE", "BorneMemoireBac", "EtageRefuse", "resoudre_utilisateur_bac"):
            self.assertIs(getattr(tdm3, nom), getattr(tdm2, nom), nom)
