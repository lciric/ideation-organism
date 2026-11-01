"""Graines de la v53 (R9) : `numpy.random.SeedSequence`, dérivées par tâche, consignées au manifeste.

Le cœur du pôle (v0 à v52b) dérive ses graines par SHA-256 en bibliothèque standard (`outils.graine_derivee`) ; la v53 suit
R9 et le préenregistrement du pré-pilote (brouillon 6, « Graines ») : racine du run fixée avant tout tirage, puis
`SeedSequence(racine, spawn_key=(cle_de_tache(nom),))`, où `cle_de_tache` est **la même fonction** que celle de
`src/controle_ia/manifeste.py` (8 premiers octets de SHA-256 du nom de tâche, gros-boutiste). numpy ≥ 1.25 est exigé
(refus sinon, aucun repli sur la dérivation de la bibliothèque standard).

Chaque tirage passe par `Graines.generateur(tache)` ; la liste des tâches tirées et l'état de contrôle de chacune
(`generate_state(2)`) sont rendus par `Graines.manifeste()`, écrit au manifeste du run.
"""

import hashlib

VERSION = "graines-v53"
NUMPY_MINIMAL = (1, 25)


class GrainesRefusees(RuntimeError):
    pass


def cle_de_tache(tache):
    """Identique à `controle_ia.manifeste.cle_de_tache` (src/controle_ia/manifeste.py, ligne 33)."""
    return int.from_bytes(hashlib.sha256(tache.encode("utf-8")).digest()[:8], "big")


def _numpy():
    try:
        import numpy as np
    except ImportError as e:  # aucun repli silencieux (R5)
        raise GrainesRefusees("numpy absent : R9 exige numpy.random.SeedSequence (numpy ≥ 1.25)") from e
    morceaux = []
    for m in np.__version__.split(".")[:2]:
        chiffres = "".join(c for c in m if c.isdigit())
        morceaux.append(int(chiffres or 0))
    if tuple(morceaux) < NUMPY_MINIMAL:
        raise GrainesRefusees(f"numpy {np.__version__} < 1.25 : R9 exige numpy ≥ 1.25")
    return np


class Graines:
    """Racine entière du run, fixée avant tout tirage ; un générateur par tâche nommée (noms uniques par run)."""

    def __init__(self, racine):
        if isinstance(racine, bool) or not isinstance(racine, int) or racine < 0:
            raise GrainesRefusees(f"racine des graines : entier ≥ 0 (reçu {racine!r})")
        self.np = _numpy()
        self.racine = racine
        self._taches = {}

    def sequence(self, tache):
        if not isinstance(tache, str) or not tache:
            raise GrainesRefusees("nom de tâche : chaîne non vide")
        ss = self.np.random.SeedSequence(self.racine, spawn_key=(cle_de_tache(tache),))
        self._taches.setdefault(tache, [int(x) for x in ss.generate_state(2)])
        return ss

    def generateur(self, tache):
        return self.np.random.default_rng(self.sequence(tache))

    def permutation(self, tache, n):
        return [int(i) for i in self.generateur(tache).permutation(n)]

    def jeton_opaque(self, tache, octets=8):
        """Identifiant opaque (hexadécimal) tiré par la tâche : ni classe, ni fournisseur, ni bras n'y sont lisibles."""
        return bytes(int(x) for x in self.generateur(tache).integers(0, 256, size=octets)).hex()

    def manifeste(self):
        return {"version": VERSION, "numpy": self.np.__version__, "racine": self.racine,
                "regle": "numpy.random.SeedSequence(racine, spawn_key=(cle_de_tache(tache),)) ; cle_de_tache = 8 premiers "
                         "octets de SHA-256 du nom (src/controle_ia/manifeste.py)",
                "taches": {t: {"spawn_key": [str(cle_de_tache(t))], "etat_controle": e} for t, e in sorted(self._taches.items())}}
