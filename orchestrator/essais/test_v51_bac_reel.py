"""Essais de la version 51 de l'orchestrateur (corrections de la contre-lecture CL15) : un groupe par constat.

Chaque correction a un essai **réel sous `bwrap`** (installé sur la machine d'essai) avec un **artefact contre une cible factice
créée par l'essai** et un **cas sain** (R5). Aucun essai réel ne s'ignore en silence (CL15-04) : sans `bwrap`, ou sans noyau
superutilisateur et `setpriv` quand l'essai les exige, il **échoue** ; seule la variable explicite `POLE_ESSAI_BAC_REEL_NON_JOUE=1`
le fait ignorer, avec un motif « ESSAI RÉEL NON JOUÉ » compté au résultat de la suite.

Cibles : dossiers provisoires créés et retirés par les essais (un fichier creux de 300 Mo dans un dossier réservé au
superutilisateur, pour CL15-03) ; jamais `/usr`, `/etc`, `/root` ni un réglage de l'hôte. Aucune écriture dans `/proc/sys`.
Aucun réseau, aucune clé, aucun appel payant. Les groupes de contrôle créés (CL15-02) sont des enfants de celui du processus
d'essai, retirés après chaque exécution ; l'essai `test_v51_15` vérifie qu'il n'en reste aucun.
"""

import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import struct
import subprocess
import tempfile
import time
import types
import unittest
import zipfile
from unittest import mock

from essais import test_v7_ideation_v2 as t7
from essais.aides import CasAvecDossier
from essais.test_v47_relais_moisson import RACINE, garde_fou_reseau
from pole import tests_de_mort as tdm1  # la version 1 (v50), gardée telle quelle : contraste des artefacts seulement
from pole import tests_de_mort_v2 as tdm

UID_ESSAI = t7.UID_ESSAI


def lanceur(nom):
    spec = importlib.util.spec_from_file_location("lanceur_" + nom.replace(".", "_"), os.path.join(RACINE, "demonstrations", nom))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def groupes_restants():
    """Les groupes de contrôle `pole-bac-*` encore présents sous celui du processus d'essai (aucun attendu)."""
    try:
        version, parent = tdm.BorneMemoireBac.localiser()
    except (tdm.EtageRefuse, OSError):
        return []
    return sorted(n for n in os.listdir(parent) if n.startswith(tdm.BorneMemoireBac.PREFIXE))


class TestV51(CasAvecDossier):
    """v51 (contre-lecture CL15) : un groupe d'essais par constat, les essais réels sous le vrai `bwrap`."""

    def setUp(self):
        super().setUp()
        self.garde = garde_fou_reseau()
        self.garde.__enter__()
        self.addCleanup(self.garde.__exit__, None, None, None)

    # --- aides ------------------------------------------------------------------------------------------------------------------

    def exiger_superutilisateur(self):
        if os.geteuid() != 0 or not t7.utilisateur_dedie_possible():
            t7.exiger_essai_reel(self, "noyau superutilisateur avec setpriv requis (utilisateur dédié, groupe de contrôle)")

    @contextlib.contextmanager
    def bac_ouvert(self, ex):
        """La racine de travail de l'exécuteur, ouverte puis fermée (verrou rendu, dossier retiré)."""
        racine = ex.ouvrir_racine_travail()
        try:
            yield racine
        finally:
            ok, motif = ex.fermer_racine_travail(racine)
            self.assertTrue(ok, motif)

    def jouer(self, ex, racine, nom, script, delai=30.0, avant=None):
        """Exécute `script` dans un dossier de travail neuf de la racine ; rend (résultat, dossier de travail)."""
        prop = ex.proprietaire_travail()
        travail = os.path.join(racine, nom)
        tdm.creer_dossier_neuf(travail, prop)
        chemin = os.path.join(travail, "script.py")
        tdm.ecrire_exclusif(chemin, script.encode("utf-8"), proprietaire=prop)
        if avant:
            avant(travail)
        return ex.executer(chemin, travail, delai_s=delai, dossier_capture=racine), travail

    def cible_factice_reservee(self, octets=300 << 20, vide=False):
        """Un dossier **de l'hôte**, réservé au superutilisateur (0700), avec un fichier creux de `octets` (ou vide) : la cible
        factice de CL15-03, que le script du bac ne peut ni voir ni lire. Retiré à la fin."""
        hote = tempfile.mkdtemp(prefix="essai-v51-hote-factice-")
        self.addCleanup(shutil.rmtree, hote, True)
        os.chmod(hote, 0o700)
        if not vide:
            with open(os.path.join(hote, "gros-fichier-creux"), "wb") as f:
                f.truncate(octets)
        return os.path.realpath(hote)

    # --- CL15-01 : identité de l'hôte lue par le noyau (témoin) -------------------------------------------------------------------

    @t7.essai_reel_bwrap
    def test_v51_01_temoin_identite_cas_sain_sous_le_vrai_bac(self):
        """CL15-01, cas sain : sous le vrai `bwrap` (utilisateur dédié sous un noyau superutilisateur), la sonde passe ;
        `uid_map` lu **dans** le bac vaut `65534 0 1` (l'espace intermédiaire de `bwrap` : c'est pourquoi la v50 lisait 0 et
        refusait tout) ; le témoin créé par le script est, **vu de l'hôte**, à l'utilisateur dédié (jamais 0) :
        `verifier_temoin_identite` l'accepte."""
        vrai = t7.executeur_reel(self, 30.0)
        ok, motif = vrai.disponible()
        self.assertTrue(ok, motif)
        self.assertIn("témoin d'identité lu par le noyau", motif)
        script = ("import os\nprint('UID_MAP', open('/proc/self/uid_map').read().split())\nprint('UID', os.getuid())\n"
                  f"open({tdm.TEMOIN_IDENTITE!r}, 'w').write('x')\n")
        with self.bac_ouvert(vrai) as racine:
            r, travail = self.jouer(vrai, racine, "temoin", script)
            self.assertEqual(r["code"], 0, r["stderr"])
            if os.geteuid() == 0:
                self.assertIn("UID_MAP ['65534', '0', '1']", r["stdout"])  # ce que la v50 lisait : 0, quelle que soit l'identité réelle
            self.assertIn("UID 65534", r["stdout"])
            st = os.lstat(os.path.join(travail, tdm.TEMOIN_IDENTITE))
            attendu = (vrai.uid_hote_attendu(), vrai.gid_hote_attendu())
            self.assertEqual((st.st_uid, st.st_gid), attendu)
            self.assertNotIn(0, attendu)
            self.assertEqual(tdm.verifier_temoin_identite(os.path.join(travail, tdm.TEMOIN_IDENTITE), *attendu)[0], True)

    @t7.essai_reel_bwrap
    def test_v51_02_temoin_identite_artefact_bwrap_lance_par_le_superutilisateur(self):
        """CL15-01, artefact (la mutation de CL15) : `bwrap` lancé **par le superutilisateur** (sans `setpriv`), utilisateur dédié
        pourtant déclaré : le script a l'identité 0 de l'hôte. L'étage est refusé ; et, l'évaluation de la sortie de la sonde
        neutralisée, c'est le **témoin** (propriétaire 0:0 lu sur l'hôte) qui le refuse. Contraste : la sonde de la v50, qui lisait
        `uid_map`, refuse aussi le bac sain (CL15-01), parce qu'elle y lit toujours 0. Joué sous le filtre d'appels système et la
        borne mémoire du bac ; `/proc/sys` est en lecture seule (aucune écriture)."""
        self.exiger_superutilisateur()
        base = t7.executeur_reel(self, 30.0)
        racine_root = tempfile.mkdtemp(prefix="essai-v51-racine-root-")  # mutation : racine du superutilisateur (comme CL15)
        self.addCleanup(shutil.rmtree, racine_root, True)
        os.chmod(racine_root, 0o700)

        class SansSetpriv(tdm.ExecuteurBacASable):
            """Mutation de CL15 : `bwrap` lancé par le superutilisateur, racine du superutilisateur, contrôle d'identité contourné
            (l'utilisateur dédié reste déclaré : le noyau attend son identité sur le témoin)."""
            def verifier_identite(self):
                return None

            def proprietaire_travail(self):
                return None

            def ouvrir_racine_travail(self):
                return tempfile.mkdtemp(prefix="etage-travail-", dir=self.racine_travail)

            def commande_lancee(self, script, travail, fd_seccomp=None):
                return self.commande(script, travail, fd_seccomp=fd_seccomp)

        class SansSetprivEvaluationNeutralisee(SansSetpriv):
            def evaluer_sonde(self, r):
                return True, "évaluation neutralisée (mutation)"
        kw = dict(delai_s=30.0, utilisateur_bac=base.utilisateur_bac[0], racine_travail=base.racine_travail)
        kw_root = dict(kw, racine_travail=racine_root)
        ok, motif = SansSetpriv(**kw_root).disponible()
        self.assertFalse(ok)
        self.assertIn("étage refusé", motif)  # la sonde (borne de processus inopérante pour l'identité 0) ou le témoin
        ok, motif = SansSetprivEvaluationNeutralisee(**kw_root).disponible()
        self.assertFalse(ok)
        self.assertIn("identité 0 de l'hôte", motif)
        self.assertIn("propriétaire du témoin 0:0", motif)
        # contraste : la version 1 (v50), sur le même vrai bac **sain**, lit UID_HOTE=0 dans uid_map et refuse (le défaut de CL15-01)
        ok1, motif1 = tdm1.ExecuteurBacASable(**kw).disponible()
        self.assertFalse(ok1)
        self.assertIn("UID_HOTE=0", motif1)
        ok2, motif2 = tdm.ExecuteurBacASable(**kw).disponible()  # la version 2, même bac sain : acceptée
        self.assertTrue(ok2, motif2)

    def test_v51_03_temoin_identite_lecture_sur_l_hote_artefacts(self):
        """CL15-01, lecture du témoin par le noyau (`lstat`, sans suivre de lien) : cas sain (fichier régulier, un seul nom,
        identité attendue) ; artefacts : témoin absent, lien vers un fichier de l'utilisateur dédié, deux noms (lien dur),
        dossier, propriétaire 0 ou groupe 0, autre identité, identité attendue nulle — chacun refusé avec son motif."""
        d = self.sous_dossier("temoins")
        moi_uid, moi_gid = (UID_ESSAI, UID_ESSAI) if os.geteuid() == 0 else (os.geteuid(), os.getegid())
        sain = os.path.join(d, "sain")
        open(sain, "w").close()
        if os.geteuid() == 0:
            os.chown(sain, moi_uid, moi_gid)
        self.assertTrue(tdm.verifier_temoin_identite(sain, moi_uid, moi_gid)[0])
        ok, m = tdm.verifier_temoin_identite(os.path.join(d, "absent"), moi_uid, moi_gid)
        self.assertFalse(ok)
        self.assertIn("absent", m)
        lien = os.path.join(d, "lien")
        os.symlink(sain, lien)
        self.assertFalse(tdm.verifier_temoin_identite(lien, moi_uid, moi_gid)[0])
        dur = os.path.join(d, "dur")
        os.link(sain, dur)
        ok, m = tdm.verifier_temoin_identite(sain, moi_uid, moi_gid)
        self.assertFalse(ok)
        self.assertIn("un seul nom", m)
        os.unlink(dur)
        self.assertFalse(tdm.verifier_temoin_identite(d, moi_uid, moi_gid)[0])
        ok, m = tdm.verifier_temoin_identite(sain, moi_uid + 1, moi_gid)
        self.assertFalse(ok)
        self.assertIn("≠ attendue", m)
        for attendu in ((None, moi_gid), (0, moi_gid), (moi_uid, 0)):
            ok, m = tdm.verifier_temoin_identite(sain, *attendu)
            self.assertFalse(ok)
            self.assertIn("inconnue ou nulle", m)
        if os.geteuid() == 0:
            for proprietaire in ((0, moi_gid), (moi_uid, 0), (0, 0)):
                os.chown(sain, *proprietaire)
                ok, m = tdm.verifier_temoin_identite(sain, moi_uid, moi_gid)
                self.assertFalse(ok, proprietaire)
                self.assertIn("identité 0 de l'hôte", m)

    # --- CL15-02 : mémoire du bac entier, /dev, filtre d'appels système ------------------------------------------------------------

    @t7.essai_reel_bwrap
    def test_v51_04_memoire_du_bac_artefacts_reels_et_cas_sain(self):
        """CL15-02, artefacts de CL15 rejoués dans le vrai bac : 45 Mo écrits dans `/dev` (refus `EROFS`), segment System V de
        256 Mo (refus `EPERM`), `memfd_create` (refus), et **six enfants de 200 Mo** (chacun sous `RLIMIT_AS`, 1,2 Go ensemble
        pour une borne d'1 Go) : le groupe de contrôle en tue au moins un, le noyau le constate sur l'hôte (`oom_kill`), l'exécution
        est « échouée (limites) » avec le motif, le groupe est retiré. Cas sain : `multiprocessing` (deux processus), 1 Mo dans
        `/dev/shm`, `/dev/null`, `/dev/urandom`, 100 Mo alloués : code 0, aucune limite, aucun processus tué."""
        vrai = t7.executeur_reel(self, 60.0)
        attaque = ("import ctypes, os, signal, time, select\nlibc = ctypes.CDLL(None, use_errno=True)\n"
                   "try:\n    open('/dev/cl15', 'wb').write(b'x' * (45 << 20))\n    print('DEV ecrit')\n"
                   "except OSError as e:\n    print('DEV refus', e.errno)\n"
                   "r = libc.shmget(0, ctypes.c_size_t(256 << 20), 0o1000 | 0o600)\nprint('SYSV', r, ctypes.get_errno())\n"
                   "try:\n    os.memfd_create('x')\n    print('MEMFD ecrit')\nexcept OSError as e:\n    print('MEMFD refus', e.errno)\n"
                   "lecture, ecriture = os.pipe()\nenfants = []\n"
                   "for _ in range(6):\n    pid = os.fork()\n    if pid == 0:\n"
                   "        open('/proc/self/oom_score_adj', 'w').write('1000')\n        bloc = b'\\x01' * (200 << 20)\n"
                   "        os.write(ecriture, b'A')\n        signal.pause()\n        os._exit(0)\n    enfants.append(pid)\n"
                   "tues, fin, vivants = 0, time.monotonic() + 20, set(enfants)\n"
                   "while vivants and time.monotonic() < fin:\n    select.select([lecture], [], [], 0.05)\n"
                   "    for pid in list(vivants):\n        p, s = os.waitpid(pid, os.WNOHANG)\n        if p:\n            vivants.discard(pid)\n"
                   "            tues += os.WIFSIGNALED(s) and os.WTERMSIG(s) == 9\n    if tues:\n        break\n"
                   "for pid in vivants:\n    os.kill(pid, 9)\n    os.waitpid(pid, 0)\nprint('TUES', tues)\n")
        sain = ("import multiprocessing, os\n"
                "def carre(x):\n    return x * x\n"
                "if __name__ == '__main__':\n"
                "    with multiprocessing.Pool(2) as p:\n        print('POOL', sum(p.map(carre, range(100))))\n"
                "    open('/dev/shm/essai', 'wb').write(b'x' * (1 << 20)); os.unlink('/dev/shm/essai')\n"
                "    open('/dev/null', 'w').write('x')\n    print('ALEA', len(open('/dev/urandom', 'rb').read(16)))\n"
                "    bloc = b'\\x01' * (100 << 20)\n    print('SAIN OK', len(bloc) >> 20)\n")
        with self.bac_ouvert(vrai) as racine:
            r, _ = self.jouer(vrai, racine, "attaque", attaque)
            self.assertIn("DEV refus 30", r["stdout"])
            self.assertIn("SYSV -1 1", r["stdout"])
            self.assertIn("MEMFD refus 1", r["stdout"])
            tues = int(r["stdout"].split("TUES")[-1].split()[0])
            self.assertGreaterEqual(tues, 1, r["stdout"])
            m = r["memoire_bac"]
            self.assertEqual(m["octets_max"], vrai.memoire_bac_octets())
            self.assertGreaterEqual(m["oom_kill"], 1)
            self.assertLessEqual(m["pic_octets"], m["octets_max"])
            self.assertTrue(m["retire"])
            self.assertTrue(any("mémoire du bac entier atteinte" in x for x in r["limites_depassees"]), r["limites_depassees"])
            r, _ = self.jouer(vrai, racine, "sain", sain)
            self.assertEqual((r["code"], r["limites_depassees"]), (0, []), r["stderr"])
            for attendu in ("POOL 328350", "ALEA 16", "SAIN OK 100"):
                self.assertIn(attendu, r["stdout"])
            self.assertEqual(r["memoire_bac"]["oom_kill"], 0)
        self.assertEqual(groupes_restants(), [])

    @t7.essai_reel_bwrap
    def test_v51_05_mutations_de_la_sonde_dev_filtre_groupe(self):
        """CL15-02, R5 par mutation, sous le vrai `bwrap` : chaque garde nouvelle retirée à tour de rôle fait refuser l'étage par la
        sonde, avec son motif — sans `--remount-ro /dev` (« /dev est inscriptible ») ; sans filtre d'appels système (« filtre
        d'appels système absent ») ; processus lancé hors du groupe de contrôle (« mémoire du bac entier n'est pas bornée »), puis,
        l'évaluation de la sortie neutralisée, le constat du noyau sur l'hôte (« oom_kill = 0 »). Demande explicite
        (`memoire_bac_non_bornee_permise`) : acceptée, dite. Borne trop petite pour la sonde : refusée avant la sonde."""
        base = t7.executeur_reel(self, 30.0)
        kw = dict(delai_s=30.0, utilisateur_bac=base.utilisateur_bac[0] if base.utilisateur_bac else None,
                  racine_travail=base.racine_travail)

        class SansDevLectureSeule(tdm.ExecuteurBacASable):
            def commande(self, script, travail, fd_seccomp=None):
                cmd = super().commande(script, travail, fd_seccomp=fd_seccomp)
                i = cmd.index("--remount-ro")
                assert cmd[i + 1] == "/dev"
                return cmd[:i] + cmd[i + 2:]

        class SansFiltre(tdm.ExecuteurBacASable):
            FILTRE_APPELS = False

        class HorsDuGroupe(tdm.ExecuteurBacASable):
            def _limites(self, delai, borne=None):
                return super()._limites(delai, None)  # mutation : le groupe existe, le processus n'y entre pas

        class HorsDuGroupeEvaluationNeutralisee(HorsDuGroupe):
            def evaluer_sonde(self, r):
                return True, "évaluation neutralisée (mutation)"
        for classe, motif in ((SansDevLectureSeule, "/dev est inscriptible"), (SansFiltre, "filtre d'appels système absent"),
                              (HorsDuGroupe, "mémoire du bac entier n'est pas bornée (REUSSI-5-enfants"),
                              (HorsDuGroupeEvaluationNeutralisee, "oom_kill = 0")):
            ok, m = classe(**kw).disponible()
            self.assertFalse(ok, classe.__name__)
            self.assertIn(motif, m, classe.__name__)
        ok, m = tdm.ExecuteurBacASable(**kw).disponible()  # cas sain, même bac
        self.assertTrue(ok, m)
        self.assertIn("mémoire du bac entier bornée (groupe de contrôle)", m)
        permis = tdm.ExecuteurBacASable(memoire_bac_non_bornee_permise=True, **kw)
        ok, m = permis.disponible()
        self.assertTrue(ok, m)
        self.assertIn("mémoire du bac entier NON bornée (demande explicite)", m)
        self.assertIn("NON BORNÉE", permis.description()["memoire_du_bac_entier"])
        petit = tdm.ExecuteurBacASable(memoire_mo=256, **kw)
        self.assertIn("< 512 Mo", petit.verifier_outils())
        self.assertFalse(petit.disponible()[0])
        self.assertNotIn("< 512 Mo", tdm.ExecuteurBacASable(memoire_mo=256, memoire_bac_non_bornee_permise=True, **kw).verifier_outils() or "")
        self.assertEqual(groupes_restants(), [])

    def test_v51_06_programme_du_filtre_d_appels_systeme(self):
        """CL15-02, CL15-06 : le programme BPF (`programme_seccomp`) **rejoué par un petit interpréteur** : chaque appel refusé
        rend `EPERM` ; `read`, `write`, `fork`, `execve`, `clone`, `mmap`, `openat`, `socketpair` passent ; un appel x32 est refusé ;
        une autre architecture est tuée. Une architecture sans table éprouvée est refusée (aucun filtre deviné), à l'outil comme à
        la construction du programme. La commande porte `--seccomp FD` et `--remount-ro /dev` après le `tmpfs` de `/dev/shm`."""
        programme = tdm.programme_seccomp("x86_64")
        self.assertEqual(len(programme) % 8, 0)
        instr = [struct.unpack("=HBBI", programme[i:i + 8]) for i in range(0, len(programme), 8)]

        def executer_bpf(arch, nr):
            pc = acc = 0
            while True:
                code, jt, jf, k = instr[pc]
                if code == 0x20:
                    acc = {0: nr, 4: arch}[k]
                    pc += 1
                elif code == 0x15:
                    pc += 1 + (jt if acc == k else jf)
                elif code == 0x35:
                    pc += 1 + (jt if acc >= k else jf)
                elif code == 0x06:
                    return k
                else:
                    raise AssertionError(f"instruction inconnue {code:#x}")
        arch = tdm.APPELS_REFUSES["x86_64"][0]
        for nom, nr in tdm.APPELS_REFUSES["x86_64"][2].items():
            self.assertEqual(executer_bpf(arch, nr), 0x00050001, nom)
        for nr in (0, 1, 2, 9, 56, 57, 59, 257, 53, 39, 60, 231, 435):  # read, write, open, mmap, clone, fork, execve, openat, socketpair…
            self.assertEqual(executer_bpf(arch, nr), 0x7FFF0000, nr)
        self.assertEqual(executer_bpf(arch, 0x40000000 | 1), 0x00050001)  # x32
        self.assertEqual(executer_bpf(0x40000003, 1), 0x80000000)  # i386 (int 0x80) : tué
        self.assertEqual(executer_bpf(0xC00000B7, 1), 0x80000000)  # aarch64 : tué
        for nom in ("shmget", "msgget", "semget", "memfd_create", "io_uring_setup", "ptrace", "bpf", "perf_event_open", "keyctl",
                    "add_key", "userfaultfd", "process_vm_readv", "pidfd_getfd"):
            self.assertIn(nom, tdm.APPELS_REFUSES["x86_64"][2])
        with self.assertRaisesRegex(tdm.EtageRefuse, "sans filtre d'appels système éprouvé"):
            tdm.programme_seccomp("aarch64")
        ex = tdm.ExecuteurBacASable(bwrap="/usr/bin/bwrap", python="/usr/bin/python3")
        with mock.patch.object(tdm.os, "uname", return_value=types.SimpleNamespace(machine="riscv64")):
            self.assertIn("architecture 'riscv64'", ex.verifier_outils() or "")
        travail = self.sous_dossier("cmd")
        cmd = ex.commande(os.path.join(travail, "script.py"), travail, fd_seccomp=7)
        self.assertEqual(cmd[cmd.index("--seccomp") + 1], "7")
        self.assertLess(cmd.index("--seccomp"), cmd.index("--"))
        i = cmd.index("--tmpfs")
        self.assertEqual(cmd[i:i + 4], ["--tmpfs", "/dev/shm", "--remount-ro", "/dev"])
        self.assertNotIn("--seccomp", ex.commande(os.path.join(travail, "script.py"), travail))

    # --- CL15-03 : parcours par descripteurs ---------------------------------------------------------------------------------------

    def test_v51_07_lien_substitue_pendant_le_parcours_deterministe(self):
        """CL15-03, artefact rendu déterministe : entre le `lstat` d'un sous-dossier et son ouverture, il est remplacé (a) par un lien
        vers un dossier **de l'hôte** réservé au superutilisateur (cible factice : un fichier creux de 300 Mo), (b) par un autre
        vrai dossier. La version 2 ne parcourt jamais la cible : dépassement « dossier remplacé pendant le parcours », le même
        pour une cible pleine ou vide (aucun oracle), jamais « plus de 268435456 octets ». Contraste : la version 1 (v50), même
        substitution à son `scandir` par chemin, **parcourt** la cible et rend « plus de 268435456 octets » (le défaut de CL15-03).
        Cas sain : sans substitution, aucun dépassement, les fichiers du sous-dossier sont hachés."""
        motifs = {}
        for nom, vide in (("pleine", False), ("vide", True)):
            hote = self.cible_factice_reservee(vide=vide)
            travail = self.sous_dossier("travail-" + nom)
            os.mkdir(os.path.join(travail, "zz"))
            with open(os.path.join(travail, "zz", "a"), "w") as f:
                f.write("a")

            def substituer(racine, relatif, hote=hote):
                if relatif == "zz" and not os.path.islink(os.path.join(racine, "zz")):
                    os.rename(os.path.join(racine, "zz"), os.path.join(racine, "zz-vrai"))
                    os.symlink(hote, os.path.join(racine, "zz"))
            with mock.patch.object(tdm, "_ESSAI_AVANT_OUVERTURE", substituer):
                inv = tdm.inventaire_travail(travail, sauf=("tranche",), hacher=False)
            self.assertEqual(inv.depassements, ["dossier remplacé pendant le parcours : non suivi (zz, CL15-03)"])
            self.assertLess(inv.octets, 1 << 20)
            motifs[nom] = inv.depassements
            # contraste : la version 1 suit le lien (scandir par chemin), parcourt la cible de l'hôte
            os.unlink(os.path.join(travail, "zz"))
            os.rename(os.path.join(travail, "zz-vrai"), os.path.join(travail, "zz"))
            vrai_scandir = os.scandir

            def scandir_v1(chemin, travail=travail, hote=hote):
                if isinstance(chemin, str) and chemin.endswith("/zz") and not os.path.islink(chemin):
                    os.rename(chemin, chemin + "-vrai")
                    os.symlink(hote, chemin)
                return vrai_scandir(chemin)
            with mock.patch.object(tdm1.os, "scandir", scandir_v1):
                inv1 = tdm1.inventaire_travail(travail, sauf=("tranche",), hacher=False)
            if vide:
                self.assertEqual(inv1.depassements, [])  # v50 : cible vide → rien ; pleine → tuée : l'oracle de CL15-03
            else:
                self.assertEqual(inv1.depassements, ["plus de 268435456 octets dans le dossier de travail"])
        self.assertEqual(motifs["pleine"], motifs["vide"])  # v51 : le motif ne dit rien de la cible
        # (b) un autre vrai dossier posé à la place (même nom, autre inode)
        travail = self.sous_dossier("travail-autre")
        os.mkdir(os.path.join(travail, "zz"))

        def remplacer(racine, relatif):
            if relatif == "zz" and not os.path.exists(os.path.join(racine, "zz-ancien")):
                os.rename(os.path.join(racine, "zz"), os.path.join(racine, "zz-ancien"))
                os.mkdir(os.path.join(racine, "zz"))
        with mock.patch.object(tdm, "_ESSAI_AVANT_OUVERTURE", remplacer):
            self.assertEqual(tdm.mesure_rapide_travail(travail), ["dossier remplacé pendant le parcours : non suivi (zz, CL15-03)"])
        # cas sain
        sain = self.sous_dossier("travail-sain")
        os.makedirs(os.path.join(sain, "a", "b"))
        with open(os.path.join(sain, "a", "b", "f.txt"), "w") as f:
            f.write("contenu")
        os.symlink("/proc/self/environ", os.path.join(sain, "a", "lien"))
        inv = tdm.inventaire_travail(sain)
        self.assertEqual(inv.depassements, [])
        self.assertEqual(inv.fichiers, {"a/b/f.txt": hashlib.sha256(b"contenu").hexdigest()})
        self.assertEqual(inv.non_copies["a/lien"], {"type": "lien", "cible": "/proc/self/environ"})
        # la racine elle-même : un lien n'est jamais suivi
        lien_racine = os.path.join(self.tmp, "racine-lien")
        os.symlink(sain, lien_racine)
        self.assertIn("dossier illisible", tdm.inventaire_travail(lien_racine).depassements[0])

    @t7.essai_reel_bwrap
    def test_v51_08_lien_substitue_pendant_la_surveillance_sous_le_vrai_bac(self):
        """CL15-03, la course de CL15 rejouée sous le vrai `bwrap` : 1 500 fichiers, puis le dossier `zz` basculé entre un vrai
        dossier et un lien vers une cible factice de l'hôte (dossier réservé au superutilisateur, fichier creux de 300 Mo), pendant
        4 s. Jamais « plus de 268435456 octets » (la v50 le rendait 3 fois sur 3) ; les seuls motifs possibles sont « dossier
        remplacé pendant le parcours », pour la cible pleine comme pour la vide. Cas sain : 1 500 fichiers et des dossiers sans
        bascule : code 0, aucune limite."""
        vrai = t7.executeur_reel(self, 30.0)
        modele = ("import os, time\nfor i in range(1500):\n    open('f%04d' % i, 'w').close()\nos.mkdir('zz')\nn = 0\n"
                  "fin = time.monotonic() + 4\nwhile time.monotonic() < fin:\n"
                  "    os.rename('zz', 'zz-t')\n    os.symlink(@CIBLE@, 'zz')\n    time.sleep(0.0005)\n    os.unlink('zz')\n"
                  "    os.rename('zz-t', 'zz')\n    n += 1\nprint('bascules', n)\n")
        sain = ("import os\nfor i in range(1500):\n    open('f%04d' % i, 'w').close()\n"
                "for d in ('a', 'a/b', 'c'):\n    os.mkdir(d)\n    open(d + '/x', 'w').write(d)\nprint('SAIN')\n")
        with self.bac_ouvert(vrai) as racine:
            for nom, vide in (("pleine", False), ("vide", True)):
                cible = self.cible_factice_reservee(vide=vide)
                r, _ = self.jouer(vrai, racine, "course-" + nom, modele.replace("@CIBLE@", repr(cible)))
                for motif in r["limites_depassees"]:
                    self.assertIn("dossier remplacé pendant le parcours", motif, (nom, r["limites_depassees"]))
                self.assertFalse(any("octets" in m or "entrées" in m for m in r["limites_depassees"]))
            r, _ = self.jouer(vrai, racine, "sain", sain)
            self.assertEqual((r["code"], r["limites_depassees"]), (0, []), r["stderr"])
            self.assertIn("SAIN", r["stdout"])

    # --- CL15-04 : essais réels jamais ignorés en silence ----------------------------------------------------------------------------

    def test_v51_09_essais_reels_jamais_ignores_en_silence(self):
        """CL15-04 : sans `bwrap` (ou sans ce qu'un essai réel exige), l'essai **échoue** ; avec `POLE_ESSAI_BAC_REEL_NON_JOUE=1`
        seulement, il est ignoré avec le motif « ESSAI RÉEL NON JOUÉ ». Aucun `skipUnless(which("bwrap"))` ne reste dans les essais ;
        l'assertion sans effet de la v50 (`'0', '0', '1'` absent de `uid_map`) est retirée."""
        class Factice(unittest.TestCase):
            def runTest(self):
                pass
        f = Factice()
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(t7.VARIABLE_ESSAIS_REELS_NON_JOUES, None)
            with self.assertRaisesRegex(AssertionError, "jamais ignoré en silence"):
                t7.exiger_essai_reel(f, "bwrap absent")
            with mock.patch.object(t7.shutil, "which", return_value=None):
                with self.assertRaisesRegex(AssertionError, "bwrap absent"):
                    t7.executeur_reel(f, 5.0)
                with self.assertRaisesRegex(AssertionError, "bwrap absent"):
                    t7.essai_reel_bwrap(lambda self: None)(f)
        with mock.patch.dict(os.environ, {t7.VARIABLE_ESSAIS_REELS_NON_JOUES: "1"}):
            with self.assertRaisesRegex(unittest.SkipTest, "ESSAI RÉEL NON JOUÉ"):
                t7.exiger_essai_reel(f, "bwrap absent")
        for nom in sorted(os.listdir(os.path.join(RACINE, "essais"))):
            if nom.endswith(".py"):
                with open(os.path.join(RACINE, "essais", nom), encoding="utf-8") as fichier:
                    texte = fichier.read()
                self.assertNotIn("skipUnless(shutil.which(\"bwrap\")", texte, nom)
                self.assertNotIn("self.assertNotIn(\"'0', '0', '1'\"", texte, nom)

    # --- CL15-05 : Argon --------------------------------------------------------------------------------------------------------------

    def test_v51_10_modele_commande_externe_refuse_sans_attestation(self):
        """CL15-05 : avec le moteur réel, `--modele-commande-externe` autre que `gemini-4-argon` est refusé **avant tout appel** tant
        que `--commande-externe-lit-modele` n'atteste pas une commande qui lit le modèle demandé ; l'attestation sans commande
        externe est une erreur d'options ; le LISEZMOI de la v51 dit que le premier appel réel d'Argon fixe
        `--modele-servi-externe-permis` avec Lazar."""
        l2 = lanceur("ideation_v2.py")

        def args(**kw):
            base = dict(moteur="claude-sdk", commande_externe="cmd", experimentateur_externe=None, modele_commande_externe=None,
                        commande_externe_accepte_experimentateur=False, commande_externe_lit_modele=False)
            base.update(kw)
            return types.SimpleNamespace(**base)
        with self.assertRaisesRegex(l2.idn.CourseInterrompue, "CL15-05"):
            l2.verifier_commande_externe_reelle(args(modele_commande_externe="gemini-5-argon"), [("a", "gemini-5-argon")], [])
        l2.verifier_commande_externe_reelle(args(modele_commande_externe="gemini-5-argon", commande_externe_lit_modele=True),
                                            [("a", "gemini-5-argon")], [])
        l2.verifier_commande_externe_reelle(args(), [("a", "gemini-4-argon")], [])
        l2.verifier_commande_externe_reelle(args(moteur="simule", modele_commande_externe="gemini-5-argon"), [("a", "x")], [])
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                l2.principal([os.path.join(self.tmp, "s"), "--liste-blanche", "l", "--question", "q", "--temoins", "t",
                              "--commande-externe-lit-modele"])
        self.assertEqual(cm.exception.code, 2)
        with open(os.path.join(RACINE, "LISEZMOI-orchestrateur-pole-v7-v51.md"), encoding="utf-8") as f:
            lisezmoi = f.read()
        self.assertIn("--modele-servi-externe-permis", lisezmoi)
        self.assertIn("premier appel réel d'Argon", lisezmoi)

    # --- CL15-06 : surface restante ---------------------------------------------------------------------------------------------------

    @t7.essai_reel_bwrap
    def test_v51_11_ptrace_io_uring_et_chemin_de_l_hote_sous_le_vrai_bac(self):
        """CL15-06, artefacts dans le vrai bac : `ptrace(PTRACE_ATTACH)` du processus 1, `io_uring_setup`, `bpf`,
        `perf_event_open`, `keyctl`, `add_key`, `userfaultfd`, `process_vm_readv`, `kcmp`, `pidfd_getfd` — tous `EPERM` ; le
        processus 1 du bac (`bwrap`) n'a plus le chemin de l'hôte du dossier de travail dans son environnement (`HOME=/`). Cas
        sain dans la même exécution : `fork`, tubes, paires de prises, `getpid` marchent."""
        vrai = t7.executeur_reel(self, 30.0)
        nr = tdm.APPELS_REFUSES["x86_64"][2]
        script = ("import ctypes, os, socket\nlibc = ctypes.CDLL(None, use_errno=True)\n"
                  "def essai(nom, *a):\n    r = libc.syscall(*a)\n    e = ctypes.get_errno()\n"
                  "    if r >= 0 and nom == 'ptrace':\n        libc.syscall(%(ptrace)d, 17, 1, 0, 0)\n"
                  "    print(nom, 'REUSSI' if r >= 0 else 'errno-%%d' %% e)\n"
                  "essai('ptrace', %(ptrace)d, 16, 1, 0, 0)\nessai('io_uring_setup', %(io_uring_setup)d, 1, None)\n"
                  "essai('bpf', %(bpf)d, 0, None, 0)\nessai('perf_event_open', %(perf_event_open)d, None, 0, -1, -1, 0)\n"
                  "essai('keyctl', %(keyctl)d, 0, 0, 0)\nessai('add_key', %(add_key)d, b'user', b'cle-factice', b'x', 1, 0)\n"
                  "essai('userfaultfd', %(userfaultfd)d, 0)\nessai('process_vm_readv', %(process_vm_readv)d, 1, None, 0, None, 0, 0)\n"
                  "essai('kcmp', %(kcmp)d, 1, 1, 0, 0, 0)\nessai('pidfd_getfd', %(pidfd_getfd)d, 0, 0, 0)\n"
                  "print('ENVIRON1', open('/proc/1/environ', 'rb').read().split(b'\\0'))\n"
                  "pid = os.fork()\nif pid == 0:\n    os._exit(7)\nprint('FORK', os.WEXITSTATUS(os.waitpid(pid, 0)[1]))\n"
                  "a, b = socket.socketpair()\na.send(b'p')\nprint('PRISES', b.recv(1))\nr, w = os.pipe()\nos.write(w, b't')\n"
                  "print('TUBE', os.read(r, 1), os.getpid() > 0)\n") % nr
        with self.bac_ouvert(vrai) as racine:
            r, travail = self.jouer(vrai, racine, "surface", script)
            self.assertEqual(r["code"], 0, r["stderr"])
            for nom in ("ptrace", "io_uring_setup", "bpf", "perf_event_open", "keyctl", "add_key", "userfaultfd", "process_vm_readv",
                        "kcmp", "pidfd_getfd"):
                self.assertIn(f"{nom} errno-1\n", r["stdout"])
            self.assertNotIn("REUSSI", r["stdout"])
            environ = r["stdout"].split("ENVIRON1")[1].split("\n")[0]
            self.assertNotIn(racine, environ)
            self.assertNotIn(travail, environ)
            self.assertIn("b'HOME=/'", environ)
            for attendu in ("FORK 7", "PRISES b'p'", "TUBE b't' True"):
                self.assertIn(attendu, r["stdout"])

    # --- CL15-07 : identité dédiée à personne d'autre ---------------------------------------------------------------------------------

    @t7.essai_reel_bwrap
    def test_v51_12_identite_dediee_processus_compte_verrou(self):
        """CL15-07 : (a) un processus de l'hôte sous l'identité dédiée (un `sleep` lancé par l'essai sous `setpriv`) fait refuser
        l'étage au départ (`verifier_identite`, `disponible`) **et** interrompt une exécution (`EtageInterrompu`) ; arrêté par son
        identifiant (R10), l'étage repasse (cas sain). (b) Une identité dont le compte a un interpréteur de commandes est refusée ;
        `nologin` est accepté. (c) Verrou : un second bac du même processus noyau sur la même identité est refusé tant que le
        premier tient sa racine ; rendu, il passe."""
        self.exiger_superutilisateur()
        vrai = t7.executeur_reel(self, 30.0)
        uid = vrai.utilisateur_bac[0]
        self.assertEqual(tdm.processus_de_l_identite(uid), [])
        intrus = subprocess.Popen(["setpriv", "--reuid", str(uid), "--regid", str(uid), "--clear-groups", "--no-new-privs", "--",
                                   "/usr/bin/sleep", "60"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            fin = time.monotonic() + 10
            while intrus.pid not in tdm.processus_de_l_identite(uid) and time.monotonic() < fin:
                time.sleep(0.02)
            self.assertIn(intrus.pid, tdm.processus_de_l_identite(uid))
            self.assertIn("processus de l'hôte ont l'identité dédiée", vrai.verifier_identite())
            ok, motif = vrai.disponible()
            self.assertFalse(ok)
            self.assertIn("CL15-07", motif)
            sain = tdm.ExecuteurBacASable(delai_s=30.0, utilisateur_bac=uid, racine_travail=vrai.racine_travail)
            with mock.patch.object(tdm, "processus_de_l_identite", return_value=[]):  # passer le contrôle de départ seulement
                racine = sain.ouvrir_racine_travail()
            try:
                with self.assertRaisesRegex(tdm.EtageInterrompu, "avant l'exécution"):
                    self.jouer(sain, racine, "intrus", "print('jamais')\n")
            finally:
                sain.fermer_racine_travail(racine)
        finally:
            intrus.kill()  # R10 : par son identifiant
            intrus.wait()
        self.assertEqual(tdm.processus_de_l_identite(uid), [])
        self.assertIsNone(vrai.verifier_identite())
        ok, motif = vrai.disponible()
        self.assertTrue(ok, motif)
        # (b) compte avec interpréteur de commandes
        compte = types.SimpleNamespace(pw_name="compte-factice", pw_shell="/bin/bash")
        with mock.patch("pwd.getpwuid", return_value=compte):
            self.assertIn("interpréteur de commandes", vrai.verifier_identite())
        with mock.patch("pwd.getpwuid", return_value=types.SimpleNamespace(pw_name="compte-factice", pw_shell="/usr/sbin/nologin")):
            self.assertIsNone(vrai.verifier_identite())
        # (c) verrou : un seul bac à la fois par identité
        autre = tdm.ExecuteurBacASable(delai_s=30.0, utilisateur_bac=uid, racine_travail=vrai.racine_travail)
        racine = vrai.ouvrir_racine_travail()
        try:
            with self.assertRaisesRegex(tdm.EtageRefuse, "verrou"):
                autre.ouvrir_racine_travail()
            ok, motif = autre.disponible()
            self.assertFalse(ok)
            self.assertIn("verrou", motif)
        finally:
            vrai.fermer_racine_travail(racine)
        ok, motif = autre.disponible()
        self.assertTrue(ok, motif)

    def test_v51_13_groupe_de_controle_cree_vide_retire(self):
        """CL15-02, plomberie du groupe de contrôle (noyau superutilisateur) : créé neuf sous celui du noyau, borne relue, un
        processus y entre avant son `exec` ; à la fermeture, ce qui reste est tué **par identifiant** (R10) et le groupe retiré ;
        rien ne reste."""
        self.exiger_superutilisateur()
        borne = tdm.BorneMemoireBac(64 << 20).creer()
        try:
            self.assertTrue(os.path.isdir(borne.chemin))
            self.assertTrue(os.path.basename(borne.chemin).startswith("pole-bac-"))
            p = subprocess.Popen(["/usr/bin/sleep", "60"], preexec_fn=borne.entrer, stdin=subprocess.DEVNULL)
            self.assertEqual(borne.processus(), [p.pid])
            self.assertEqual(borne.oom_kills(), 0)
        finally:
            bilan = borne.fermer()
        p.wait()
        self.assertEqual(bilan, {"retire": True, "processus_tues": 1, "motif": None})
        self.assertFalse(os.path.exists(borne.chemin))
        self.assertEqual(p.returncode, -9)
        self.assertEqual(groupes_restants(), [])

    # --- rétrocompatibilité et R12 -----------------------------------------------------------------------------------------------------

    def test_v51_14_retrocompatibilite_lanceur_v1_et_v2_octet_pour_octet(self):
        """Sans `--tests-de-mort`, le lanceur v2 (cœur et étage v2) produit **exactement** les fichiers du lanceur v1 (v50, cœur et
        étage v1, gardés) : même chemin de sortie (la graine du moteur simulé en dépend), course simple et course à seconde
        passe ; tous les fichiers, contrôle compris, comparés octet pour octet."""
        from essais.test_v7_ideation_v2 import TestCourse
        c = TestCourse("test_course_complete")
        c.tmp = self.tmp
        prep = c.preparer()
        for seconde in (False, True):
            vus = {}
            for nom in ("ideation_v1.py", "ideation_v2.py"):
                l = lanceur(nom)
                sortie = os.path.join(self.tmp, "s")
                argv = [sortie, "--liste-blanche", prep["liste_blanche"], "--question", prep["question"], "--piece", prep["pieces"][0],
                        "--temoins", prep["temoins"]] + (["--seconde-passe", "--materiau", prep["pieces"][0]] if seconde else [])
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(l.principal(argv), 0, nom)
                fichiers = {}
                for haut in [x for x in os.listdir(self.tmp) if x == "s" or x.startswith("s-")]:
                    for d, _, noms in os.walk(os.path.join(self.tmp, haut)):
                        for n in noms:
                            p = os.path.join(d, n)
                            with open(p, "rb") as f:
                                fichiers[os.path.relpath(p, self.tmp)] = f.read()
                    shutil.rmtree(os.path.join(self.tmp, haut))
                vus[nom] = fichiers
            self.assertGreater(len(vus["ideation_v1.py"]), 30)
            self.assertEqual(sorted(vus["ideation_v1.py"]), sorted(vus["ideation_v2.py"]))
            for chemin, contenu in vus["ideation_v1.py"].items():
                self.assertEqual(contenu, vus["ideation_v2.py"][chemin], chemin)

    def test_v51_15_r12_la_v50_reste_telle_quelle_et_provenance_de_la_v51(self):
        """R12 : aucun fichier de la v50 n'est modifié — chaque fichier de `EMPREINTES-orchestrateur-pole-v7-v50.txt` présent sur
        le disque a son empreinte v50 ; le seul absent, `essais/test_v7_ideation.py` (v50), est dans `CODE-orchestrateur-pole-v7-
        v50.zip` à son empreinte. Les fichiers nouveaux de la v51 sont au tableau du LISEZMOI v51 avec leur empreinte (le fichier
        d'essais présent ne s'y compare pas : il ne peut pas se contenir) ; chaque version 2 a sa version 1 dans l'arbre ou
        l'archive. Aucun groupe de contrôle `pole-bac-*` ne reste."""
        v50 = {}
        with open(os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v50.txt"), encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip():
                    empreinte, chemin = ligne.split(None, 1)
                    v50[chemin.strip()] = empreinte
        with zipfile.ZipFile(os.path.join(RACINE, "CODE-orchestrateur-pole-v7-v50.zip")) as z:
            archive = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
        absents = []
        for chemin, empreinte in v50.items():
            p = os.path.join(RACINE, chemin)
            if not os.path.exists(p):
                absents.append(chemin)
                self.assertEqual(archive.get(chemin), empreinte, chemin)
                continue
            with open(p, "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), empreinte, f"{chemin} : modifié depuis la v50 (R12)")
        self.assertEqual(absents, ["essais/test_v7_ideation.py"])
        for chemin, empreinte in archive.items():
            self.assertEqual(v50.get(chemin), empreinte, f"{chemin} : l'archive de la v50 ≠ EMPREINTES v50")
        tableau = {}
        with open(os.path.join(RACINE, "LISEZMOI-orchestrateur-pole-v7-v51.md"), encoding="utf-8") as f:
            for ligne in f:
                parties = [x.strip() for x in ligne.split("|")]
                if len(parties) >= 4 and parties[1].startswith("`") and len(parties[3].strip("`")) == 64:
                    tableau[parties[1].strip("`")] = (parties[2].strip("`"), parties[3].strip("`"))
        moi = "essais/test_v51_bac_reel.py"
        for nouveau, version1 in (("pole/tests_de_mort_v2.py", "pole/tests_de_mort.py"), ("pole/ideation_v2.py", "pole/ideation.py"),
                                  ("demonstrations/ideation_v2.py", "demonstrations/ideation_v1.py"),
                                  ("essais/test_v7_ideation_v2.py", "essais/test_v7_ideation.py"), (moi, "—")):
            self.assertIn(nouveau, tableau)
            self.assertEqual(tableau[nouveau][0], version1, nouveau)
            if version1 != "—":
                self.assertTrue(os.path.exists(os.path.join(RACINE, version1)) or version1 in archive, version1)
            if nouveau != moi:
                with open(os.path.join(RACINE, nouveau), "rb") as f:
                    self.assertEqual(hashlib.sha256(f.read()).hexdigest(), tableau[nouveau][1], f"{nouveau} : empreinte ≠ LISEZMOI v51")
        self.assertEqual(groupes_restants(), [])


if __name__ == "__main__":
    unittest.main()
