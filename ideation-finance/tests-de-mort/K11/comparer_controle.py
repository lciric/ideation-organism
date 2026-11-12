#!/usr/bin/env python3
"""K11 -- compare les pages FedInvest retelechargees (donnees/fedinvest_controle/) aux copies de J05 (donnees/fedinvest/).

Pour chaque date : identite octet par octet ; sinon, lignes qui different (diff) et identite du tableau extrait.
Usage : python3 -I comparer_controle.py
"""
import difflib
import hashlib
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import construire  # noqa: E402

A = os.path.join(ICI, "donnees", "fedinvest")
B = os.path.join(ICI, "donnees", "fedinvest_controle")
for f in sorted(os.listdir(B)):
    a, b = open(os.path.join(A, f), "rb").read(), open(os.path.join(B, f), "rb").read()
    ha, hb = hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest()
    if a == b:
        print(f, "identique octet par octet", ha)
        continue
    la, lb = a.decode("utf-8", "replace").splitlines(), b.decode("utf-8", "replace").splitlines()
    diff = [x for x in difflib.unified_diff(la, lb, lineterm="", n=0) if x[:1] in "+-" and x[:3] not in ("+++", "---")]
    import datetime as dt
    d = dt.date.fromisoformat(f[:-5])
    construire.FI_DIR = A
    ta = construire.lire_page(d)
    construire.FI_DIR = B
    tb = construire.lire_page(d)
    construire.FI_DIR = A
    print(f, "DIFFERENT", ha[:12], hb[:12], f"{len(diff)} lignes differentes ;",
          "tableau extrait identique" if ta == tb else "TABLEAU DIFFERENT", f"({len(ta or {})} lignes)")
    for x in diff[:4]:
        print("     ", x[:160])
