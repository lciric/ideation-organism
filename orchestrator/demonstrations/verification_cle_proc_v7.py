"""Vérification « la clé du relais n'est pas dans /proc » (v7, version 11 ; contre-lecture F-C7, message n° 92 de
session-depot). Pour un processus donné (le relais), lit `/proc/<pid>/environ` et dit si une variable de clé y figure
(par son NOM : la valeur n'est jamais affichée ni écrite). Deux usages :

- `--pid PID` : contrôle d'un relais réel en marche (cas sain attendu : aucune variable de clé ; le relais lancé avec
  `--fichier-cle` n'en porte pas) ;
- `--demonstration` : lance deux sous-processus factices (clé FACTICE, sans valeur réelle) — l'un reçoit la clé par son
  environnement (artefact attendu : visible dans son /proc), l'autre par un fichier à lecture unique (cas sain attendu :
  invisible) — et rend 0 si les deux attendus sont tenus, 3 sinon. R5 : garde testée sur un cas sain et sur un artefact.

Ne lit, n'affiche ni n'écrit aucune valeur de clé. Sortie JSON sur la sortie standard.
"""

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time

NOMS_DE_CLE = re.compile(r"^(ANTHROPIC_API_KEY|RR_[A-Z0-9_]*KEY[A-Z0-9_]*|[A-Z0-9_]*API_KEY[A-Z0-9_]*|[A-Z0-9_]*SECRET[A-Z0-9_]*)$")


def noms_de_cle_dans_proc(pid):
    """Noms des variables de clé présentes dans /proc/<pid>/environ (jamais les valeurs) ; None si illisible."""
    try:
        with open(f"/proc/{pid}/environ", "rb") as f:
            brut = f.read()
    except (PermissionError, FileNotFoundError, ProcessLookupError):
        return None
    noms = []
    for morceau in brut.split(b"\0"):
        if b"=" not in morceau:
            continue
        nom = morceau.split(b"=", 1)[0].decode("utf-8", "replace")
        if NOMS_DE_CLE.match(nom):
            noms.append(nom)
    return sorted(noms)


def _processus_factice(env, args_sup=()):
    code = "import time, sys\nsys.stdout.write('pret\\n'); sys.stdout.flush()\ntime.sleep(30)\n"
    return subprocess.Popen([sys.executable, "-I", "-B", "-c", code, *args_sup], env=env, stdout=subprocess.PIPE, text=True)


def demonstration():
    base = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/tmp")}
    resultats = {}
    # artefact : la clé factice passe par l'environnement du processus
    p1 = _processus_factice(dict(base, ANTHROPIC_API_KEY="FACTICE-sans-valeur"))
    p1.stdout.readline()
    resultats["par_environnement"] = {"noms_dans_proc": noms_de_cle_dans_proc(p1.pid)}
    p1.kill()
    # cas sain : la clé factice passe par un fichier à lecture unique (mode 600), jamais par l'environnement
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".cle") as f:
        f.write("FACTICE-sans-valeur\n")
        chemin = f.name
    os.chmod(chemin, stat.S_IRUSR | stat.S_IWUSR)
    p2 = _processus_factice(dict(base), args_sup=(chemin,))
    p2.stdout.readline()
    resultats["par_fichier"] = {"noms_dans_proc": noms_de_cle_dans_proc(p2.pid), "fichier_supprime_par_le_lecteur": None}
    p2.kill()
    os.remove(chemin)
    sain = resultats["par_fichier"]["noms_dans_proc"] == []
    artefact = bool(resultats["par_environnement"]["noms_dans_proc"])
    resultats["cas_sain_tenu"], resultats["artefact_tenu"] = sain, artefact
    resultats["lecture"] = ("tenu : la clé passée par l'environnement est visible dans /proc, celle passée par fichier ne l'est pas"
                            if sain and artefact else "NON TENU : voir les deux lignes")
    return resultats, 0 if (sain and artefact) else 3


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--pid", type=int, help="processus à contrôler (le relais)")
    a.add_argument("--demonstration", action="store_true")
    args = a.parse_args(argv)
    if args.demonstration:
        resultats, code = demonstration()
    elif args.pid:
        noms = noms_de_cle_dans_proc(args.pid)
        resultats = {"pid": args.pid, "noms_dans_proc": noms,
                     "lecture": ("illisible (autre utilisateur, ou processus absent) : cas sain si c'est un autre utilisateur"
                                 if noms is None else ("aucune variable de clé : cas sain" if not noms else
                                                       "ARTEFACT : variable(s) de clé visible(s) par leur nom"))}
        code = 0 if not noms else 3
    else:
        a.error("--pid ou --demonstration")
    print(json.dumps(resultats, ensure_ascii=False, indent=1))
    return code


if __name__ == "__main__":
    sys.exit(principal())
