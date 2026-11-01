"""Fiches de la course 2 (v53) : contenu au format du texte I (champs obligatoires injectés, DEP1), identifiant opaque,
métadonnées tenues à part et jamais servies (A4).

Une fiche est `{"ident", "contenu", "empreinte", "meta"}` : `contenu` est ce que le proposeur a écrit (vérifié contre la
liste injectée des champs obligatoires) ; `empreinte` = SHA-256 du JSON canonique du contenu ; `meta` porte la case
(texte, bras), le fournisseur, la passe et l'origine (proposition ou fusion) — rien de `meta` n'entre dans une entrée de
juge, d'aiguilleur, de lecteur d'étiquettes ou de metteur en fusion. `garde_etiquettes` (A4, garde R5 ligne 2) refuse toute
entrée servie qui porte une étiquette interdite (liste injectée : « témoin », « exploratoire », « fusion », noms de bras ou de
règle, noms de fournisseurs…), mot entier après normalisation.
"""

import json
import re

from .caviardage import caviarder_objet
from .outils import empreinte_objet, extraire_bloc_json, normaliser_texte

VERSION = "fiches-course-2-v53"
CLES_META = ("ident", "meta", "empreinte", "case", "fournisseur", "passe", "origine", "bras", "classe", "temoin")


class FicheRefusee(ValueError):
    pass


class EtiquetteDansEntree(RuntimeError):
    """A4 : arrêt ; entrées reconstruites ; aucune notation conservée."""


def valider_contenu(brut, champs_obligatoires):
    if not isinstance(brut, dict):
        raise FicheRefusee("fiche non dictionnaire")
    internes = sorted(set(brut) & set(CLES_META))
    if internes:
        raise FicheRefusee("champs réservés au noyau dans la fiche : " + ", ".join(internes))
    manquants = [c for c in champs_obligatoires if brut.get(c) in (None, "", [], {})]
    if manquants:
        raise FicheRefusee("champs obligatoires manquants : " + ", ".join(manquants))
    contenu, _ = caviarder_objet(json.loads(json.dumps(brut, ensure_ascii=False)))
    return contenu


def preparer(brut, champs_obligatoires, *, ident, case, fournisseur, passe, origine="proposition"):
    contenu = valider_contenu(brut, champs_obligatoires)
    return {"ident": ident, "contenu": contenu, "empreinte": empreinte_objet(contenu),
            "meta": {"case": list(case), "fournisseur": fournisseur, "passe": passe, "origine": origine}}


def fiches_du_texte(texte, cle="fiches"):
    """Les fiches d'une réponse : bloc JSON `{"fiches": [...]}` (dernier bloc qui porte la clé)."""
    bloc = extraire_bloc_json(texte, cle)
    if bloc is None or not isinstance(bloc.get(cle), list):
        raise FicheRefusee(f"bloc JSON {{{cle}: [...]}} absent")
    return bloc[cle]


def vue_servie(fiche):
    """Ce qu'un lecteur reçoit : le contenu seul (aucune métadonnée)."""
    return json.loads(json.dumps(fiche["contenu"], ensure_ascii=False))


def _motif(etiquette):
    n = normaliser_texte(etiquette)
    return re.compile(r"(?<![0-9a-z])" + re.escape(n) + r"(?![0-9a-z])") if n else None


def garde_etiquettes(texte_entree, etiquettes_interdites):
    """A4 : lève `EtiquetteDansEntree` si une étiquette interdite apparaît (mot entier, après normalisation)."""
    plat = normaliser_texte(texte_entree if isinstance(texte_entree, str) else json.dumps(texte_entree, ensure_ascii=False))
    trouvees = [e for e in etiquettes_interdites if (m := _motif(e)) is not None and m.search(plat)]
    if trouvees:
        raise EtiquetteDansEntree("A4 : étiquette interdite dans une entrée servie (" + ", ".join(sorted(trouvees))
                                  + ") : arrêt, entrée à reconstruire")
    return True


def entree_une_fiche(consigne_figee, fiche, etiquettes_interdites, identifiant_servi=None):
    """Consigne figée (pièce empreintée) + une seule fiche anonyme ; la garde A4 porte sur la fiche servie."""
    vue = vue_servie(fiche)
    if identifiant_servi is not None:
        vue = dict(vue, identifiant=identifiant_servi)
    corps = json.dumps(vue, ensure_ascii=False, indent=1)
    garde_etiquettes(corps, etiquettes_interdites)
    return consigne_figee.rstrip() + "\n\n## La fiche\n```json\n" + corps + "\n```\n"
