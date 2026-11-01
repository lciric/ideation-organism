"""Essais de la version 0.7.0, version 5 : corrections des huit défauts de plomberie du premier lancement réel (a).

Lecture : `../premier-lancement-reel/lecture-lancement-reel-a-v1.md` (`9305a3b4…`). Chaque défaut a son cas sain et son
artefact (R5) :
1. un agent qui écrit lui-même `reponse.txt`, `consigne.txt`, `lecons.json` (leçon de mémoire de (a)) ne casse plus rien ;
2. une erreur de l'orchestrateur ne compte pas comme un essai (jamais « retirée » par la plomberie) ;
3. la qualité distingue témoins jugés, promus, en erreur ; trois états des dents ;
4. une erreur après l'expérimentateur garde son coût, et sa réservation n'est libérée qu'une fois ;
5. le dossier du vérificateur ne reçoit ni réponse, ni consigne, ni empreinte orpheline ; sa consigne dit qu'il n'y a pas
   de verdict chiffré à confirmer sous le pari ;
6. la garde sépare le code du shell (les cinq faux positifs reproduits passent ; les accès hors du dossier restent
   refusés) ;
7. moteur réel refusé sans bac à sable actif (sauf faux moteur, ou exception écrite hors de root) ;
8. réserve du relais par appel au-dessus du coût maximal vu en (a), dépassements comptés.
Et l'arrêt du pôle quand la moitié au moins des fiches lancées sont en erreur de l'orchestrateur.
"""

import json
import os
import types
import unittest

from essais.test_cycle import CasGeneration
from essais.test_v7_banque import banque_jouet, fiche_banque, loi_trait
from pole.adaptateurs import BacASableInactif, etat_bac_a_sable, exiger_bac_a_sable
from pole.cycle import Budget, ConfigGeneration, Generation, cumuler_qualite
from pole.fiche import RegistreGel
from pole.garde_outils import evaluer_commande
from pole.monde_banque import MondeBanque
from pole.pole import executer_pole
from pole.relais_reel import RESERVE_PAR_APPEL_DEFAUT, Compteur
from pole.simulation import AdaptateurSimule, MondeSimule

NOMS_RESERVES = ("reponse.txt", "consigne.txt", "lecons.json")
MARQUE_PANNE = "PANNE-SIMULEE"


class AgentQuiEcritLesNomsReserves(AdaptateurSimule):
    """Suit une leçon de mémoire du type de (a) : écrit lui-même les noms que l'orchestrateur se réservait."""

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        os.makedirs(dossier, exist_ok=True)
        for nom in NOMS_RESERVES:
            chemin = os.path.join(dossier, nom)
            if not os.path.exists(chemin):
                with open(chemin, "w", encoding="utf-8") as f:
                    f.write("écrit par l'agent\n")
        return super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)


class AgentEnPanne(AdaptateurSimule):
    """Lève (erreur de l'orchestrateur simulée) pour le rôle donné quand la consigne porte la marque, ou toujours."""

    def __init__(self, *args, toujours=False, role_en_panne="experimentateur", **kwargs):
        super().__init__(*args, **kwargs)
        self.toujours, self.role_en_panne = toujours, role_en_panne

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        if role == self.role_en_panne and (self.toujours or MARQUE_PANNE in consigne):
            raise RuntimeError("panne simulée de la plomberie")
        return super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)


def config_banque(**modifs):
    reglages = dict(selection="pari", taille_plan=100, taille_plan_filles=100, urne=False, part_calibrage=12,
                    multiplicite="e-bh", budget_generation_usd=50.0,
                    politique_redite="refus")  # v11 : banque jouet à une tranche, héritage coupé (contre-lecture C3)
    reglages.update(modifs)
    return ConfigGeneration(**reglages).valider()


class NomsReservesEtTraces(CasGeneration):
    """Défauts 1 et 5 : la course de (a), rejouée en simulation avec des agents qui écrivent les noms réservés."""

    def test_agent_qui_ecrit_les_noms_reserves_ne_casse_rien(self):
        chemin = os.path.join(self.tmp, "banque.json")
        banque_jouet(chemin, n=360)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        population = [fiche_banque("P1", loi_trait(0)), fiche_banque("P2", loi_trait(1), enonce="L'issue suit le bruit")]
        temoins = [fiche_banque("TV", loi_trait(0, force=1.0), enonce="Témoin vrai", temoin="vraie"),
                   fiche_banque("TF", loi_trait(1, force=1.0), enonce="Témoin faux", temoin="fausse")]
        config = config_banque(propositions_par_generation=2)
        adaptateur = AgentQuiEcritLesNomsReserves(graine=3, monde=MondeSimule(3))
        racine = os.path.join(self.tmp, "course")
        bilan = executer_pole(population, temoins, adaptateur, config, 2, 200.0, racine, monde_noyau=monde)
        self.assertEqual(bilan["generations_executees"], 2, bilan["arret"])
        for g in (0, 1):
            with open(os.path.join(racine, "journal", f"generation-{g:02d}.json"), encoding="utf-8") as f:
                journal = json.load(f)
            self.assertEqual(journal["erreurs_orchestrateur"]["fiches"], [], f"génération {g}")
            self.assertFalse([i for i, v in journal["fiches"].items() if "erreur de l'orchestrateur" in str(v.get("motif"))])
        base = os.path.join(racine, "archive", "generations", "generation-00")
        fiches = sorted(d for d in os.listdir(base) if d.startswith("G0-F"))
        self.assertTrue(fiches)
        verifiees = 0
        for ident in fiches:
            exp, traces_exp = os.path.join(base, ident, "experience"), os.path.join(base, ident, "traces-experience")
            if not os.path.isdir(exp):
                continue  # témoin jugé sans agent, ou refusé avant gel
            with open(os.path.join(exp, "reponse.txt"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "écrit par l'agent\n", "le fichier de l'agent n'est pas écrasé")
            for nom in ("consigne.txt", "reponse.txt"):
                self.assertTrue(os.path.isfile(os.path.join(traces_exp, nom)), (ident, nom))
                self.assertTrue(os.path.isfile(os.path.join(traces_exp, nom + ".sha256")), (ident, nom))
            with open(os.path.join(traces_exp, "consigne.txt"), encoding="utf-8") as f:
                self.assertIn("n'écris aucun fichier de réponse", f.read())
            verif = os.path.join(base, ident, "verification")
            if os.path.isdir(verif):
                verifiees += 1
                presents = set(os.listdir(verif))  # le vérificateur simulé écrit lui aussi les noms réservés
                for nom in ("reponse.txt.sha256", "consigne.txt.sha256"):
                    self.assertNotIn(nom, presents, (ident, "défaut 5 : aucune empreinte orpheline"))
                with open(os.path.join(base, ident, "traces-verification", "consigne.txt"), encoding="utf-8") as f:
                    self.assertIn("aucun verdict chiffré à confirmer", f.read())
                self.assertTrue(os.path.isfile(os.path.join(base, ident, "traces-verification", "reponse.txt")))
        self.assertGreater(verifiees, 0)
        self.assertTrue(os.path.isfile(os.path.join(base, "traces-synthese", "lecons.json")))
        self.assertTrue(os.path.isfile(os.path.join(base, "synthese", "lecons.json")), "celui de l'agent, intact")
        self.assertTrue(os.path.isfile(os.path.join(base, "traces-proposeur", "consigne.txt")))
        self.assertTrue(os.path.isfile(os.path.join(base, "traces-proposeur", "reponse.txt")))


class CopiePourRejeu(CasGeneration):
    def test_ni_reponse_ni_consigne_ni_leurs_empreintes(self):
        """Défaut 5 : les fichiers exclus du rejeu et leurs compagnons restent hors du dossier du vérificateur ; les autres
        fichiers et leurs compagnons y sont copiés."""
        from pole.cycle import _copier_pour_rejeu
        from pole.outils import ecrire_scelle
        source, cible = self.sous_dossier("experience"), os.path.join(self.tmp, "verification")
        for nom in ("reponse.txt", "consigne.txt", "fiche.json", "engagement.json", "tirages.json", "mesures.json"):
            ecrire_scelle(os.path.join(source, nom), "x")
        with open(os.path.join(source, "code.py"), "w", encoding="utf-8") as f:
            f.write("print(1)\n")
        _copier_pour_rejeu(source, cible, 10_000)
        self.assertEqual(sorted(os.listdir(cible)), ["code.py", "mesures.json", "mesures.json.sha256"])


class ErreursDeLOrchestrateur(CasGeneration):
    def _course(self, adaptateur, generations, temoins_sans_agent=True, population=None):
        chemin = os.path.join(self.tmp, "banque.json")
        banque_jouet(chemin, n=360)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        population = population or [
            fiche_banque("P1", loi_trait(1, force=-1.2), enonce=f"Fiche {MARQUE_PANNE} à rebours du bruit"),
            fiche_banque("P2", loi_trait(0, force=0.8), enonce="Fiche saine sur le trait utile"),
            fiche_banque("P3", loi_trait(1), enonce="Fiche saine sur le bruit")]
        temoins = [fiche_banque("TV", loi_trait(0, force=1.0), enonce="Témoin vrai", temoin="vraie"),
                   fiche_banque("TF", loi_trait(1, force=1.0), enonce="Témoin faux", temoin="fausse")]
        racine = os.path.join(self.tmp, "course")
        bilan = executer_pole(population, temoins, adaptateur, config_banque(temoins_sans_agent=temoins_sans_agent),
                              generations, 300.0, racine, monde_noyau=monde)
        with open(os.path.join(racine, "archive", "index.json"), encoding="utf-8") as f:
            return bilan, json.load(f), racine

    def test_erreur_ne_compte_pas_comme_un_essai(self):
        """Défaut 2 : la fiche en panne trois générations de suite reste indécise et rejouable, jamais retirée."""
        bilan, index, _ = self._course(AgentEnPanne(graine=3, monde=MondeSimule(3)), 3)
        en_panne = [e for e in index.values() if MARQUE_PANNE in (e.get("enonce") or "")]
        self.assertEqual(len(en_panne), 1)
        e = en_panne[0]
        self.assertEqual(e["statut"], "indecise", e["historique"])
        self.assertEqual(e["essais"], 0)
        self.assertGreaterEqual(len(e["historique"]), 2)
        self.assertTrue(all(h.get("erreur_orchestrateur") for h in e["historique"]))
        self.assertNotIn("erreurs de l'orchestrateur", bilan["arret"] or "", "une fiche sur trois : pas d'arrêt")

    def test_arret_quand_la_moitie_des_fiches_est_en_erreur(self):
        bilan, _, racine = self._course(AgentEnPanne(graine=3, monde=MondeSimule(3), toujours=True), 3)
        self.assertTrue(bilan["arret"].startswith("erreurs de l'orchestrateur"), bilan["arret"])
        self.assertEqual(bilan["generations_executees"], 1)
        with open(os.path.join(racine, "journal", "generation-00.json"), encoding="utf-8") as f:
            journal = json.load(f)
        self.assertEqual(len(journal["erreurs_orchestrateur"]["fiches"]), journal["erreurs_orchestrateur"]["lancees"])

    def test_erreur_apres_l_experimentateur_garde_son_cout_et_un_seul_reglement(self):
        """Défaut 4 : la trace de l'orchestrateur est occupée d'avance (artefact) ; l'erreur survient après le règlement
        de l'expérimentateur. Son coût reste dans l'issue, la réservation n'est libérée qu'une fois."""
        chemin = os.path.join(self.tmp, "banque.json")
        banque_jouet(chemin, n=360)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        f = fiche_banque("P1", loi_trait(0))
        occupe = os.path.join(self.tmp, "archive", "generations", "generation-00", "P1", "traces-experience",
                              "reponse.txt")
        os.makedirs(os.path.dirname(occupe))
        with open(occupe, "w", encoding="utf-8") as fo:
            fo.write("occupé\n")
        budget = Budget(20.0)
        g = Generation(0, AdaptateurSimule(graine=3, monde=MondeSimule(3)), config_banque(), self.tmp, RegistreGel(),
                       budget, monde_noyau=monde)
        r = g.executer([f])
        issue = r["issues"]["P1"]
        self.assertTrue(issue.get("erreur_orchestrateur"), issue.get("motif"))
        self.assertIn("EcrasementInterdit", issue["motif"])
        self.assertGreater(issue["couts"]["experimentateur"], 0.0)
        self.assertAlmostEqual(budget.engage, 0.0, places=9)
        self.assertAlmostEqual(budget.depense, issue["couts"]["experimentateur"], places=9)
        self.assertEqual(f.statut, "indecise")
        self.assertEqual(f.essais, 0)


class Qualite(CasGeneration):
    def test_temoin_vrai_en_erreur_dents_non_mesurees_puis_dents(self):
        """Défaut 3 : artefact — le témoin vrai est en erreur : « dents non mesurées », jamais « 0 % éliminées » seul ;
        cas sain — témoins jugés par le noyau seul : le témoin vrai est promu, « dents »."""
        chemin = os.path.join(self.tmp, "banque.json")
        banque_jouet(chemin, n=360)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        vrai = fiche_banque("TV", loi_trait(0, force=1.0), enonce=f"Témoin vrai {MARQUE_PANNE}", temoin="vraie")
        faux = fiche_banque("TF", loi_trait(1, force=1.0), enonce="Témoin faux", temoin="fausse")
        g = Generation(0, AgentEnPanne(graine=3, monde=MondeSimule(3)), config_banque(), self.sous_dossier("a"),
                       RegistreGel(), Budget(20.0), monde_noyau=monde)
        q = g.executer([vrai, faux])["qualite"]
        self.assertEqual(q["etat_dents"], "dents non mesurées")
        self.assertFalse(q["sans_dents"])
        self.assertEqual((q["temoins_vrais_juges"], q["temoins_en_erreur"], q["vraies_promues"]), (0, 1, 0))
        self.assertIsNone(q["taux_vraies_promues"])
        self.assertEqual(q["temoins_vrais_testes"], 1, "clé historique (servis) gardée pour les lecteurs existants")
        vrai2 = fiche_banque("TV", loi_trait(0, force=1.0), enonce="Témoin vrai", temoin="vraie")
        faux2 = fiche_banque("TF", loi_trait(1, force=1.0), enonce="Témoin faux", temoin="fausse")
        g2 = Generation(0, AdaptateurSimule(graine=3, monde=MondeSimule(3)), config_banque(temoins_sans_agent=True),
                        self.sous_dossier("b"), RegistreGel(), Budget(20.0), monde_noyau=monde)
        q2 = g2.executer([vrai2, faux2])["qualite"]
        self.assertEqual(q2["etat_dents"], "dents", q2["detail"])
        self.assertEqual(q2["taux_vraies_promues"], 1.0)
        total = cumuler_qualite([q, q2])
        self.assertEqual((total["temoins_vrais_juges"], total["vraies_promues"], total["temoins_en_erreur"]), (1, 1, 1))
        self.assertEqual(total["etat_dents"], "dents")


class GardeCodeEtShell(unittest.TestCase):
    """Défaut 6 : les cinq faux positifs de (a), reproduits à l'identique par la garde v7 version 4, passent ; les accès
    hors du dossier, par le code comme par le shell, restent refusés."""

    DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp")
    SAINES = {
        "division /len": "python3 - <<'EOF'\nimport json\nt=json.load(open('tirages.json'))\nprint(sum(t['issues'])/len(t['issues']))\nEOF",
        "division /120": "python3 - <<'EOF'\nk=3\nprint(round((k+1)/120, 3))\nEOF",
        "set(…)": "python3 - <<'EOF'\nprint(set([1,2]))\nEOF",
        "(~m)": "python3 - <<'EOF'\nimport numpy as np\nm=np.array([True])\nprint((~m).sum())\nEOF",
        "a / b dans -c": "python3 -c \"a=[1,2]; print(sum(a) / len(a))\"",
        "heredoc puis shell": "python3 -I - <<'FIN'\nprint(1)\nFIN\nls -la",
        "écriture d'un script": "cat > rejeu.py <<'EOF'\nimport sys\nprint(len(sys.argv) / 2)\nEOF\npython3 -I rejeu.py",
        "littéraux sans chemin": "python3 -c \"import re; print(re.split(r'/+', 'a//b'), '/'.join(['a', 'b']), '/v1/x')\"",
        "délimiteur à tirets": "python3 - <<-EOF\n\tprint(1)\n\tEOF",
    }
    INTERDITES = {
        "open('/etc/passwd') dans le code": "python3 - <<'EOF'\nprint(open('/etc/passwd').read())\nEOF",
        "corps lu par un shell": "bash <<'EOF'\ncat /etc/passwd\nEOF",
        "substitution dans un corps non cité": "cat <<EOF\n$(cat /etc/passwd)\nEOF",
        "chemin de root dans -c": "python3 -c \"open('/root/.ssh/id_rsa').read()\"",
        "dossier personnel": "python3 -c \"open('~/.bashrc')\"",
        "expanduser": "python3 -c \"import os; print(os.path.expanduser('x'))\"",
        "remontée": "python3 -c \"import os; os.chdir('../..')\"",
        "bash -c": "bash -c 'cat /etc/passwd'",
        "redirection sans fin": "python3 - <<'EOF'\nprint(1)\n",
        "redirection sans corps": "python3 - <<'EOF'",
        "environnement dans le code": "python3 - <<'EOF'\nimport os\nprint(os.environ)\nEOF",
        "shell après le corps": "python3 - <<'EOF'\nprint(1)\nEOF\ncat /etc/passwd",
        "corps reçu par une commande inconnue": "timeout 5 sh <<'EOF'\nls /root\nEOF",
        "<< dans une chaîne sur plusieurs lignes": "python3 -c \"\nx = 1 << 2\n\"\ncat /etc/shadow",
        "/proc par le code": "python3 -c \"print(open('/proc/1/status').read())\"",
    }

    def test_saines_acceptees(self):
        os.makedirs(self.DOSSIER, exist_ok=True)
        for nom, commande in self.SAINES.items():
            with self.subTest(nom=nom):
                autorise, motif = evaluer_commande(commande, self.DOSSIER)
                self.assertTrue(autorise, motif)

    def test_interdites_refusees(self):
        os.makedirs(self.DOSSIER, exist_ok=True)
        for nom, commande in self.INTERDITES.items():
            with self.subTest(nom=nom):
                autorise, motif = evaluer_commande(commande, self.DOSSIER)
                self.assertFalse(autorise, motif)


class BacASable(unittest.TestCase):
    """Défaut 7."""

    @staticmethod
    def _chercher(presents):
        return lambda nom: f"/usr/bin/{nom}" if nom in presents else None

    @staticmethod
    def _executer(code=0, erreur=None):
        def executer(*args, **kwargs):
            if erreur:
                raise erreur
            return types.SimpleNamespace(returncode=code)
        return executer

    def test_etat(self):
        self.assertTrue(etat_bac_a_sable(self._chercher({"bwrap", "socat"}), self._executer(0))[0])
        actif, motif = etat_bac_a_sable(self._chercher({"bwrap"}), self._executer(0))
        self.assertFalse(actif)
        self.assertIn("socat", motif)
        self.assertFalse(etat_bac_a_sable(self._chercher({"bwrap", "socat"}), self._executer(1))[0])
        self.assertFalse(etat_bac_a_sable(self._chercher({"bwrap", "socat"}), self._executer(erreur=OSError("x")))[0])

    def test_exigence(self):
        inactif = lambda: (False, "dépendances absentes")  # noqa: E731
        actif = lambda: (True, "ok")  # noqa: E731
        self.assertTrue(exiger_bac_a_sable(None, etat=actif)["actif"])
        with self.assertRaises(BacASableInactif):
            exiger_bac_a_sable(None, etat=inactif)
        with self.assertRaises(BacASableInactif):
            exiger_bac_a_sable(None, accepter_sans=True, motif_sans="  ", etat=inactif, euid=lambda: 1000)
        with self.assertRaises(BacASableInactif):
            exiger_bac_a_sable(None, accepter_sans=True, motif_sans="essai", etat=inactif, euid=lambda: 0)
        accepte = exiger_bac_a_sable(None, accepter_sans=True, motif_sans="agents sous un autre utilisateur",
                                     etat=inactif, euid=lambda: 1000)
        self.assertEqual(accepte["accepte_sans_bac_a_sable"], "agents sous un autre utilisateur")
        faux = types.SimpleNamespace(EST_FAUX_SDK=True)
        self.assertFalse(exiger_bac_a_sable(faux, etat=inactif)["actif"], "faux moteur : aucun agent réel")
        vrai = types.SimpleNamespace()
        with self.assertRaises(BacASableInactif):
            exiger_bac_a_sable(vrai, etat=inactif)


class ReserveDuRelais(unittest.TestCase):
    """Défaut 8."""

    def test_reserve_et_depassements(self):
        self.assertGreater(RESERVE_PAR_APPEL_DEFAUT, 0.266)
        c = Compteur(10.0)
        self.assertTrue(c.reserver())
        c.regler(0.30)
        self.assertEqual(c.etat()["appels_au_dessus_de_la_reserve"], 0)
        self.assertTrue(c.reserver())
        c.regler(0.55)
        etat = c.etat()
        self.assertEqual(etat["appels_au_dessus_de_la_reserve"], 1)
        self.assertAlmostEqual(etat["depassement_max_usd"], 0.15, places=6)
        self.assertAlmostEqual(etat["engage_usd"], 0.0, places=9)


if __name__ == "__main__":
    unittest.main()
