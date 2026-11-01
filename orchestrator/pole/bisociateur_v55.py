"""Bisociateur, version 55 — au-dessus de `bisociateur_v54` (inchangé, R12). Corrige CL19-09 (I-9).

En v54, `contre_lecture` devait citer deux chaînes de 64 hexadécimaux distinctes et `approbation_lazar` un `R-NNN` : `000…0`,
`111…1` et `R-000` passaient, et la vérification annoncée par l'annexe § 9.5 (« la différence entre le brouillon relu et
l'annexe scellée est limitée aux lignes de contre-lecture et d'approbation ») n'existait pas.

`lire_annexe_meta_v55` exige en plus deux pièces de configuration (`bisociateur.meta.annexe.brouillon_relu` et
`.rapport_contre_lecture`, chacune `{chemin, sha256}`), recalcule leurs empreintes, vérifie que **les deux** sont citées dans
`contre_lecture`, refuse `R-0…0`, puis compare le brouillon relu à l'annexe : textes hors blocs JSON identiques, blocs JSON
identiques une fois retirés `contre_lecture` et `approbation_lazar` des paramètres. Tout écart : A20, bras méta « non
produit (annexe non conforme) », jamais un arrêt.
"""

import json
import re

from . import bisociateur_v54 as b54
from .bisociateur_v54 import BisociationRefusee
from .outils import sha256_fichier

VERSION = "bisociateur-v55"
CHAMPS_LIBRES = ("contre_lecture", "approbation_lazar")
BLOC = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)


def _morceaux(texte):
    blocs, hors = [], BLOC.split(texte)
    textes = hors[0::2]
    for brut in hors[1::2]:
        try:
            blocs.append(json.loads(brut))
        except ValueError:
            raise BisociationRefusee("A20/I-9 : bloc JSON illisible dans l'annexe ou le brouillon relu") from None
    return textes, blocs


def _sans_champs_libres(bloc):
    b = json.loads(json.dumps(bloc))
    p = b.get("parametres_bras_meta")
    if isinstance(p, dict):
        for k in CHAMPS_LIBRES:
            p.pop(k, None)
    return b


def difference_limitee(texte_relu, texte_annexe):
    """Vrai si l'annexe ne diffère du brouillon relu que par `contre_lecture` et `approbation_lazar` ; lève sinon."""
    t1, b1 = _morceaux(texte_relu)
    t2, b2 = _morceaux(texte_annexe)
    if [x.strip() for x in t1] != [x.strip() for x in t2] or len(b1) != len(b2):
        raise BisociationRefusee("A20/I-9 : l'annexe diffère du brouillon relu hors des champs de contre-lecture et d'approbation")
    for x, y in zip(b1, b2):
        if _sans_champs_libres(x) != _sans_champs_libres(y):
            raise BisociationRefusee("A20/I-9 : paramètres de l'annexe différents de ceux du brouillon relu")
    return True


def lire_annexe_meta_v55(chemin, sha256_attendu, *, definitions, texte_consigne_lecteur=None, brouillon_relu=None,
                         rapport=None):
    """v54 (A20, I-3, I-4, I-6, I-9 de forme) puis I-9 sur pièces : `brouillon_relu`, `rapport` = (chemin, sha256)."""
    p, jeu = b54.lire_annexe_meta_v54(chemin, sha256_attendu, definitions=definitions, texte_consigne_lecteur=texte_consigne_lecteur)
    for quoi, piece in (("brouillon relu", brouillon_relu), ("rapport de contre-lecture", rapport)):
        if not piece or not piece[0] or not piece[1]:
            raise BisociationRefusee(f"A20/I-9 : {quoi} non fourni (pièce de configuration exigée, annexe § 9.5)")
        if sha256_fichier(piece[0]) != piece[1]:
            raise BisociationRefusee(f"A20/I-9 : {quoi} à empreinte différente de celle écrite")
        if piece[1] not in p["contre_lecture"]:
            raise BisociationRefusee(f"A20/I-9 : contre_lecture ne cite pas l'empreinte du {quoi}")
    if brouillon_relu[1] == rapport[1]:
        raise BisociationRefusee("A20/I-9 : brouillon relu et rapport de même empreinte")
    if not any(int(d) > 0 for d in re.findall(r"\bR-(\d{3,})\b", p["approbation_lazar"])):
        raise BisociationRefusee("A20/I-9 : approbation_lazar : identifiant de décision R-NNN non nul exigé")
    with open(brouillon_relu[0], "r", encoding="utf-8") as f:
        relu = f.read()
    with open(chemin, "r", encoding="utf-8") as f:
        annexe = f.read()
    difference_limitee(relu, annexe)
    return p, jeu


__all__ = ("lire_annexe_meta_v55", "difference_limitee", "BisociationRefusee")
