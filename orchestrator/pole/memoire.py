"""Mémoire du pôle : index de l'archive, garde de redite, bibliothèque de protocoles, calibration, leçons.

La mémoire ne contient que des champs tirés de l'archive du pôle (liste blanche), caviardés ; jamais de clé, jamais
rien d'autre. Les témoins sont indexés pour l'audit mais exclus de tout ce qui est servi aux agents (gabarits,
leçons, garde de redite) : un témoin reconnaissable cesserait de mesurer.

Version 0.4.0 (`orchestrateur-pole-v4`), en sélection par pari, d'après les essais de la mémoire (pistes 1 et 2,
`../memoire-v1/lecture-essais-memoire-v1.md`) :
- **identité d'une hypothèse = sa signature prédictive brute** : la loi engagée, évaluée sur une sonde fixe de 256
  instances tirée une fois par le pôle (graine du pôle) et jamais montrée aux agents ; deux fiches sont de la même classe
  si la divergence de Kullback-Leibler moyenne de la nouvelle à l'ancienne, sur la sonde, est au plus 0,30 nat (seuil de
  la piste 1, réglé à 5 % de fausses fusions entre lois tirées au hasard) ;
- **héritage de la preuve, pas de refus** : une redite d'une éliminée repart du log W cumulé de sa classe (le produit
  des e-valeurs sur des tirages frais reste une e-valeur : Ville borne la promotion de la classe par α sur toute la suite
  des retentatives) ; une redite d'une survivante est refusée (réplication, jamais une découverte) ; une seule épreuve par
  classe et par génération ;
- le texte reste la garde des fiches sans loi (sélection « seuil »).

Version 0.5.0 (`orchestrateur-pole-v5`) : le seuil de la signature tient **5 % de fausses fusions par fiche**, et non plus
par paire : une nouvelle fiche est comparée à toute l'archive (m signatures), le seuil est donc le quantile d'ordre
0,05 / m de la divergence entre deux lois tirées au hasard (loi de référence : softmax de force 1,5, celle du monde
simulé ; 2 000 paires, sur la sonde du pôle), plafonné à 0,30 nat. Démonstration v4 : à deux traits et seuil fixe, 31 à
39 vraies filles neuves fusionnées à tort sur 20 courses.
"""

import collections
import math
import random
import re

from .caviardage import caviarder, caviarder_objet
from .outils import empreinte_objet, graine_derivee, normaliser_texte

SEUIL_SIGNATURE = 0.30  # nat : piste 1 (`resultats-memoire-v1.json`, seuil « brut » 0,299 à 5 % de fausses fusions)
TAILLE_SONDE = 256
PAIRES_DE_REFERENCE = 2000
RISQUE_FUSION_PAR_FICHE = 0.05

STATUTS_TRANCHES = ("survit", "eliminee")


def trigrammes(texte):
    t = f" {normaliser_texte(texte)} "
    return {t[i:i + 3] for i in range(len(t) - 2)}


def jaccard(a, b):
    ta, tb = trigrammes(a), trigrammes(b)
    if not ta and not tb:
        return 1.0
    return len(ta & tb) / len(ta | tb)


def signature_prediction(d):
    """Ce qui fait la prédiction : signe, valeur, métrique normalisée, seuil — et la loi engagée en sélection par pari."""
    pred = d.get("prediction") or {}
    loi = d.get("loi_predictive")
    return (pred.get("signe"), float(pred.get("valeur", 0.0)), normaliser_texte(d.get("metrique", "")),
            float(d.get("seuil", 0.0)), empreinte_objet(loi) if loi else None)


def brier(paires):
    """Score de Brier de prévisions p contre issues y ∈ {0, 1} : moyenne de (p − y)²."""
    paires = list(paires)
    if not paires:
        return None
    return sum((p - y) ** 2 for p, y in paires) / len(paires)


MOTS_DU_NOYAU = re.compile(r"(?i)\b(log\s*W|richesse|issue[s]?|verdict[s]?|promu[es]*|tirages?|mesures?\.json|e-?valeur)\b")
LISTE_DE_NOMBRES = re.compile(r"(?:-?\d+(?:[.,]\d+)?\s*[,;]\s*){4,}-?\d+")  # cinq nombres ou plus, séparés par , ou ;


def filtrer_canal_de_texte(texte):
    """v7, version 11 (contre-lecture du socle, C6) : les leçons sont un canal de texte entre agents ; une ligne qui porte
    des issues recopiées (liste d'au moins cinq nombres) ou le vocabulaire du noyau (log W, richesse, issue, verdict,
    promu, tirages, e-valeur) est retirée avant archivage. Les leçons parlent de science, jamais de ce que le juge a vu ;
    un résumé qui cite quelques comptes (causes, désaccords) passe."""
    gardees = []
    for ligne in str(texte).splitlines():
        if MOTS_DU_NOYAU.search(ligne) or LISTE_DE_NOMBRES.search(ligne):
            continue
        gardees.append(ligne)
    return "\n".join(gardees)


class Memoire:
    POLITIQUES_REDITE = ("heritage", "refus", "rien")

    def __init__(self, active=True, seuil_redite=0.5, seuil_severe=0.05, nb_gabarits=3, longueur_lecon=1500, graine=0,
                 seuil_signature=SEUIL_SIGNATURE, politique_redite="heritage", generateur_reference=None):
        self.active = active
        # v7, version 12 (contre-lecture F-C4 iii) : la référence des divergences (qui calibre le seuil de fusion à 5 % de
        # fausses fusions par fiche) se tire au gabarit du monde quand il en a un (lois plus douces, dimension 4 : avec la
        # référence de force 1,5 en dimension 2, 116 paires sur 780 de lois du gabarit fusionnaient, et 21 propositions sur
        # 26 étaient refusées « classe déjà éprouvée »). `generateur_reference(rng, k, d) -> loi` ; défaut : softmax de force 1,5.
        self.generateur_reference = generateur_reference
        self.seuil_redite = seuil_redite
        self.seuil_severe = seuil_severe
        self.nb_gabarits = nb_gabarits
        self.longueur_lecon = longueur_lecon
        self.index = {}
        self.lecons = []
        # Mémoire prédictive (v4) : sondes par (issues, dimension), signatures, classes, épreuves en cours.
        if politique_redite not in self.POLITIQUES_REDITE:
            raise ValueError(f"politique de redite : une parmi {self.POLITIQUES_REDITE}")
        self.graine, self.seuil_signature, self.politique_redite = graine, seuil_signature, politique_redite
        self._sondes, self._signatures, self._references = {}, {}, {}
        self.classes, self.classe_de, self.en_cours = {}, {}, {}

    # --- (0) mémoire prédictive : signature brute, classes, héritage de la preuve ----------------------------------
    def _sonde(self, k, d):
        if (k, d) not in self._sondes:
            from . import selection_pari as sp
            rng = random.Random(graine_derivee(self.graine, "sonde-memoire", k, d))
            self._sondes[(k, d)] = sp.tirer_instances(rng, TAILLE_SONDE, d)
        return self._sondes[(k, d)]

    def signature(self, fiche):
        """Loi engagée évaluée sur la sonde (liste de vecteurs de probabilités), ou None sans loi."""
        if not fiche.loi_predictive:
            return None
        from . import selection_pari as sp
        espace = fiche.espace_instances or {}
        k, d = int(espace.get("nombre_issues", 3)), int(espace.get("dimension", 2))
        # v7, version 11 (contre-lecture C4) : le moniteur entre dans la signature. Sans lui, une loi éliminée sur un
        # moniteur léguait sa preuve à la même loi proposée sur un autre (autres issues : le produit n'est plus une
        # e-valeur), et une loi promue sur un moniteur interdisait sa transposition sur un autre.
        moniteur = espace.get("moniteur")
        return (k, d, moniteur, [sp.proba(fiche.loi_predictive, x, [], 0) for x in self._sonde(k, d)])

    def _reference(self, k, d):
        """Divergences triées entre deux lois softmax tirées au hasard (force 1,5), sur la sonde du pôle."""
        if (k, d) not in self._references:
            from . import selection_pari as sp
            rng = random.Random(graine_derivee(self.graine, "reference-signature", k, d))
            sonde, valeurs = self._sonde(k, d), []
            tirer = self.generateur_reference or (lambda r, kk, dd: sp.loi_softmax_aleatoire(r, kk, dd))
            for _ in range(PAIRES_DE_REFERENCE):
                la, lb = tirer(rng, k, d), tirer(rng, k, d)
                sa = (k, d, None, [sp.proba(la, x, [], 0) for x in sonde])  # v11 : signature à quatre champs (moniteur)
                sb = (k, d, None, [sp.proba(lb, x, [], 0) for x in sonde])
                valeurs.append(self.divergence_moyenne(sa, sb))
            self._references[(k, d)] = sorted(valeurs)
        return self._references[(k, d)]

    def seuil_effectif(self, k, d):
        """Seuil de fusion pour une nouvelle fiche : 5 % de fausses fusions par fiche contre les m signatures archivées."""
        m = sum(1 for s in self._signatures.values() if s is not None and s[:2] == (k, d))
        if m == 0:
            return self.seuil_signature
        ref = self._reference(k, d)
        rang = int(RISQUE_FUSION_PAR_FICHE / m * len(ref))
        return min(self.seuil_signature, ref[rang] if rang > 0 else ref[0] * 0.5)

    @staticmethod
    def divergence_moyenne(sa, sb):
        if sa is None or sb is None or sa[:3] != sb[:3]:  # même nombre d'issues, dimension ET moniteur (v11)
            return math.inf
        return sum(sum(p * math.log(p / q) for p, q in zip(u, v) if p > 0) for u, v in zip(sa[3], sb[3])) / len(sa[3])

    def chercher_classe(self, fiche):
        """(classe, divergence) de l'entrée archivée la plus proche par la signature, si elle est sous le seuil."""
        sig = self.signature(fiche)
        if sig is None:
            return None, None
        meilleur = (None, math.inf)
        for ident, autre in sorted(self._signatures.items()):
            kl = self.divergence_moyenne(sig, autre)
            if kl < meilleur[1]:
                meilleur = (ident, kl)
        if meilleur[0] is None or meilleur[1] > self.seuil_effectif(sig[0], sig[1]):
            return None, None
        return self.classe_de[meilleur[0]], round(meilleur[1], 6)

    def heritage(self, identifiant):
        """Preuve héritée par une fiche acceptée comme redite (log W cumulé de sa classe), ou None."""
        classe = self.en_cours.get(identifiant)
        if classe is None or self.politique_redite != "heritage":
            return None
        return {"classe": classe, "cumul": self.classes[classe]["cumul"], "epreuves": self.classes[classe]["epreuves"]}

    def _garde_signature(self, fiche):
        classe, kl = self.chercher_classe(fiche)
        if classe is None:
            return {"accepte": True, "motif": "aucune classe proche par la signature prédictive", "proches": []}
        c = self.classes[classe]
        proches = [(classe, kl)]
        if c["promue"]:
            return {"accepte": False, "motif": f"redite d'une survivante (classe {classe}, divergence {kl}) : réplication, "
                                               "jamais une découverte", "proches": proches, "classe": classe}
        if self.politique_redite == "refus":
            return {"accepte": False, "motif": f"redite d'une éliminée (classe {classe}, divergence {kl}) : refusée "
                                               "(politique « refus »)", "proches": proches, "classe": classe}
        if classe in self.en_cours.values():
            return {"accepte": False, "motif": f"classe {classe} déjà éprouvée dans cette génération (une épreuve par "
                                               "classe et par génération)", "proches": proches, "classe": classe}
        self.en_cours[fiche.identifiant] = classe
        motif = (f"redite d'une éliminée (classe {classe}, divergence {kl}) : héritage de la preuve, log W cumulé "
                 f"{round(c['cumul'], 4)}" if self.politique_redite == "heritage" else
                 f"redite d'une éliminée (classe {classe}, divergence {kl}) : retestée depuis zéro (politique « rien »)")
        return {"accepte": True, "motif": motif, "proches": proches, "classe": classe, "cumul": c["cumul"]}

    def nouvelle_generation(self):
        self.en_cours = {}

    # --- (1) index de l'archive -------------------------------------------------------------------------------
    def indexer(self, fiche, issue, generation):
        code = issue.get("code") or {}
        entree = {
            "identifiant": fiche.identifiant, "enonce": fiche.enonce, "statut": fiche.statut,
            "verdict_declare": issue.get("verdict_declare"), "verdict_final": issue.get("verdict_final"),
            "motif": issue.get("motif"), "desaccord": bool(issue.get("desaccord")),
            "severite_attendue": fiche.severite_attendue,
            "aptitude": fiche.aptitude() if fiche.statut == "survit" else None,
            "prediction": fiche.prediction, "metrique": fiche.metrique, "seuil": fiche.seuil,
            "loi_predictive": fiche.loi_predictive, "espace_instances": fiche.espace_instances,
            "protocole": fiche.protocole, "domaines": list(fiche.domaines), "operateurs": list(fiche.operateurs),
            "code": {"chemin": code.get("chemin"), "sha256": code.get("sha256")},
            "generation": generation, "source": issue.get("famille_source", fiche.famille_source()),
            "temoin": fiche.temoin is not None, "verite_temoin": fiche.temoin, "parents": list(fiche.parents),
        }
        self.index[fiche.identifiant] = caviarder_objet(entree)[0]
        if fiche.temoin is None and fiche.loi_predictive:
            self._indexer_classe(fiche, issue)
        return self.index[fiche.identifiant]

    def _indexer_classe(self, fiche, issue):
        pari = issue.get("pari") or {}
        teste = "log_richesse_finale" in pari
        if fiche.identifiant not in self.classe_de:
            classe = self.en_cours.get(fiche.identifiant)
            if classe is None and not teste and fiche.statut != "survit":
                return  # refusée avant le test, ou sans épreuve : n'ouvre pas de classe
            if classe is None:
                classe = fiche.identifiant
                self.classes[classe] = {"membres": [], "cumul": 0.0, "epreuves": 0, "promue": False}
            self.classe_de[fiche.identifiant] = classe
            self._signatures[fiche.identifiant] = self.signature(fiche)
            self.classes[classe]["membres"].append(fiche.identifiant)
        c = self.classes[self.classe_de[fiche.identifiant]]
        if teste and not pari.get("compte_dans_la_classe"):
            c["cumul"] += pari["log_richesse_finale"]
            c["epreuves"] += 1
            pari["compte_dans_la_classe"] = True
        c["promue"] = c["promue"] or fiche.statut == "survit"

    def _entrees(self, temoins=False):
        return [e for _, e in sorted(self.index.items()) if temoins or not e["temoin"]]

    # --- (2) garde de redite ----------------------------------------------------------------------------------
    def chercher_redites(self, enonce):
        proches = []
        for e in self._entrees():
            if e["statut"] == "eliminee":
                j = jaccard(enonce, e["enonce"])
                if j >= self.seuil_redite:
                    proches.append((e["identifiant"], round(j, 4)))
        return sorted(proches, key=lambda x: (-x[1], x[0]))

    def garde_redite(self, fiche):
        """Une redite d'une éliminée est refusée, sauf si `ce_qui_change[id]` est rempli et que la prédiction diffère.

        Fiche à loi engagée (sélection par pari, v4) : garde par la signature prédictive et héritage de la preuve."""
        if not self.active:
            return {"accepte": True, "motif": "mémoire inactive", "proches": []}
        if fiche.loi_predictive:
            return self._garde_signature(fiche)
        proches = self.chercher_redites(fiche.enonce)
        refus = []
        for ident, j in proches:
            justification = (fiche.ce_qui_change or {}).get(ident, "").strip()
            if not justification:
                refus.append(f"{ident} (jaccard {j}) : champ « ce qui change par rapport à {ident} » absent")
            elif signature_prediction(fiche.vers_dict()) == signature_prediction(self.index[ident]):
                refus.append(f"{ident} (jaccard {j}) : prédiction identique à celle de l'éliminée")
        if refus:
            return {"accepte": False, "motif": "redite d'une éliminée : " + " ; ".join(refus), "proches": proches}
        motif = "aucune éliminée proche" if not proches else "redite justifiée par une prédiction nouvelle"
        return {"accepte": True, "motif": motif, "proches": proches}

    # --- (3) bibliothèque de protocoles -----------------------------------------------------------------------
    def gabarits(self):
        severes = [e for e in self._entrees() if e["statut"] == "survit" and e["severite_attendue"] <= self.seuil_severe]
        severes.sort(key=lambda e: (e["severite_attendue"], e["identifiant"]))
        return [{"identifiant": e["identifiant"], "protocole": e["protocole"], "metrique": e["metrique"],
                 "severite_attendue": e["severite_attendue"]} for e in severes[:self.nb_gabarits]]

    # --- (4) registre de calibration --------------------------------------------------------------------------
    def registre_calibration(self):
        groupes = collections.defaultdict(list)
        for e in self._entrees(temoins=True):
            if e["statut"] in STATUTS_TRANCHES:
                groupes[e["source"]].append(e)
        registre = {}
        for source, entrees in sorted(groupes.items()):
            paires = [(e["severite_attendue"], 1.0 if e["statut"] == "survit" else 0.0) for e in entrees]
            nulles = [p for p, e in zip(paires, entrees) if e["verite_temoin"] == "fausse"]
            survie = sum(y for _, y in paires) / len(paires)
            moyenne = sum(p for p, _ in paires) / len(paires)
            registre[source] = {
                "nombre_de_fiches": len(paires), "brier": brier(paires), "severite_annoncee_moyenne": moyenne,
                "survie_observee": survie, "exces_de_survie": survie - moyenne,
                "nombre_sous_nul_connu": len(nulles), "brier_sous_nul_connu": brier(nulles),
            }
        return {"par_source": registre,
                "lecture": ("Brier de la sévérité annoncée (probabilité de survie sous le nul) contre la survie observée. "
                            "Sous un nul connu (témoins faux), c'est une mesure de calibration ; ailleurs, l'écart mêle "
                            "calibration et proportion d'hypothèses vraies : seuls les témoins tranchent.")}

    # --- (5) leçons de génération -----------------------------------------------------------------------------
    def resume_pour_synthese(self, generation):
        entrees = [e for e in self._entrees() if e["generation"] <= generation]
        motifs = collections.Counter(e["motif"] or "?" for e in entrees if e["statut"] != "survit")
        par_domaine = collections.defaultdict(lambda: [0, 0])
        for e in entrees:
            if e["statut"] in STATUTS_TRANCHES:
                for d in e["domaines"]:
                    par_domaine[d][0] += e["statut"] == "eliminee"
                    par_domaine[d][1] += 1
        return {
            "generation": generation,
            "comptes_par_statut": dict(collections.Counter(e["statut"] for e in entrees)),
            "causes_frequentes": motifs.most_common(5),
            "elimination_par_domaine": {d: {"eliminees": v[0], "tranchees": v[1]} for d, v in sorted(par_domaine.items())},
            "protocoles_qui_ont_fonctionne": self.gabarits(),
            "desaccords_experimentateur_verificateur": sum(e["desaccord"] for e in entrees),
            "redites_refusees": sum(e["statut"] == "refusee (redite)" for e in entrees),
        }

    def ajouter_lecon(self, generation, texte):
        propre = filtrer_canal_de_texte(caviarder(str(texte))[0]).strip()[:self.longueur_lecon]
        self.lecons.append({"generation": generation, "texte": propre})
        return propre

    def derniere_lecon(self):
        return self.lecons[-1] if self.lecons else None

    def texte_consigne(self, role):
        """Ce que la mémoire sert à un agent : gabarits (expérimentateurs) et dernière leçon (tous)."""
        if not self.active:
            return ""
        morceaux = []
        if role == "experimentateur":
            gabarits = self.gabarits()
            if gabarits:
                lignes = [f"- [{g['identifiant']}] sévérité annoncée {g['severite_attendue']} ; métrique : {g['metrique']} ; "
                          f"protocole : {g['protocole']}" for g in gabarits]
                morceaux.append("Gabarits de protocoles ayant survécu à un test sévère :\n" + "\n".join(lignes))
        lecon = self.derniere_lecon()
        if lecon and role in ("experimentateur", "recombinaison"):
            morceaux.append(f"Leçons de la génération {lecon['generation']} :\n{lecon['texte']}")
        return "\n\n".join(morceaux)

    def instantane(self):
        return {"active": self.active, "seuil_redite": self.seuil_redite, "seuil_severe": self.seuil_severe,
                "index": self.index, "lecons": self.lecons, "gabarits": self.gabarits(),
                "calibration": self.registre_calibration(), "seuil_signature": self.seuil_signature,
                "politique_redite": self.politique_redite, "classes": self.classes}
