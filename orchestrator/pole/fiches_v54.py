"""Fiches et garde A4, version 54 — au-dessus de `fiches_v53` (format des fiches inchangé).

CL18-06 : la garde v53 ne reconnaissait que le mot entier (« témoin » attrapé, « témoins », « fusionnée », « bisociations »
non). Mode injecté (`a4.mode`) :
- `mot_entier` : comportement v53 ;
- `prefixe` : l'étiquette (normalisée : minuscules, accents retirés) doit commencer un mot ; pluriels et dérivés sont
  attrapés (« témoins », « fusions », « fusionnée », « exploratoires », « bisociations »). Les variantes qui ne sont pas des
  dérivés (« Gu et Krenn ») s'écrivent dans la liste injectée.

CL18-12 : `garde_consigne` porte sur **l'entrée complète servie** (pièces comprises), pas seulement sur la fiche ; un mot
interdit dans une pièce est toujours un arrêt (ce n'est pas la faute de la fiche). L'action sur une fiche (`a4.action`) est
décidée par l'orchestrateur : arrêt de la génération, ou fiche exclue et comptée (incident consigné).
"""

import json
import re

from .fiches_v53 import EtiquetteDansEntree, FicheRefusee, fiches_du_texte, preparer, vue_servie  # noqa: F401
from .outils import empreinte_objet, normaliser_texte

VERSION = "fiches-course-2-v54"
MODES = ("mot_entier", "prefixe")


def motif(etiquette, mode):
    n = normaliser_texte(etiquette)
    if not n:
        return None
    if mode == "mot_entier":
        return re.compile(r"(?<![0-9a-z])" + re.escape(n) + r"(?![0-9a-z])")
    if mode == "prefixe":
        return re.compile(r"(?<![0-9a-z])" + re.escape(n))
    raise ValueError(f"a4.mode inconnu : {mode!r} (aucun défaut)")


def trouver(texte, etiquettes_interdites, mode):
    plat = normaliser_texte(texte if isinstance(texte, str) else json.dumps(texte, ensure_ascii=False))
    return sorted(e for e in etiquettes_interdites if (m := motif(e, mode)) is not None and m.search(plat))


def garde(texte, etiquettes_interdites, mode, quoi="une entrée servie"):
    trouvees = trouver(texte, etiquettes_interdites, mode)
    if trouvees:
        raise EtiquetteDansEntree(f"A4 : étiquette interdite dans {quoi} (" + ", ".join(trouvees) + ") : arrêt, entrée à reconstruire")
    return True


def corps_fiche(fiche, identifiant_servi=None):
    vue = vue_servie(fiche)
    if identifiant_servi is not None:
        vue = dict(vue, identifiant=identifiant_servi)
    return json.dumps(vue, ensure_ascii=False, indent=1)


def entree_une_fiche(consigne_figee, fiche, etiquettes_interdites, mode, identifiant_servi=None):
    """Consigne figée + une seule fiche anonyme ; A4 sur la fiche, puis sur l'entrée complète (CL18-12)."""
    corps = corps_fiche(fiche, identifiant_servi)
    garde(corps, etiquettes_interdites, mode, "la fiche servie")
    entree = consigne_figee.rstrip() + "\n\n## La fiche\n```json\n" + corps + "\n```\n"
    garde(entree, etiquettes_interdites, mode, "l'entrée complète (consigne figée comprise)")
    return entree


def empreinte_contenu(fiche):
    """Empreinte recalculée sur le contenu présent (CL18-05)."""
    return empreinte_objet(fiche["contenu"])


def texte_plat(fiche):
    """Texte d'une fiche pour les contrôles par programme (ancres, longueur, indices de forme) : valeurs des champs, dans l'ordre
    des clés, une par ligne, récursivement."""
    morceaux = []

    def aplatir(v):
        if isinstance(v, dict):
            for k in v:
                aplatir(v[k])
        elif isinstance(v, list):
            for x in v:
                aplatir(x)
        elif v is not None:
            morceaux.append(str(v))
    aplatir(fiche["contenu"] if "contenu" in fiche else fiche)
    return "\n".join(morceaux)
