"""Caviardage des secrets avant toute écriture dans l'archive, le journal ou la mémoire.

Garde de dernier recours : un agent qui aurait lu une clé et l'aurait recopiée dans sa réponse ou dans un fichier ne
doit pas la faire entrer dans l'archive du pôle. Les motifs visent des formes connues de clés et les affectations
explicites ; un secret sans forme reconnaissable passe (limite connue, écrite au LISEZMOI).
"""

import re

REMPLACEMENT = "[CAVIARDÉ]"

MOTIFS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}"), "clé de l'interface Anthropic"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), "clé de forme sk-"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "jeton GitHub"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "jeton GitHub"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "identifiant de clé AWS"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"), "jeton Slack"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "clé privée"),
    (re.compile(r"(?i)\b(api[_\-]?key|secret|token|password|passwd|jeton|mot[_\- ]de[_\- ]passe)(\s*[:=]\s*[\"']?)"
                r"(?!\[CAVIARDÉ\])[^\s\"',;]{8,}"), "affectation de secret"),
]


def caviarder(texte):
    """Rend (texte caviardé, nombre de remplacements)."""
    if not isinstance(texte, str):
        return texte, 0
    total = 0
    for motif, _ in MOTIFS:
        if motif.groups >= 2:
            texte, n = motif.subn(lambda m: m.group(1) + m.group(2) + REMPLACEMENT, texte)
        else:
            texte, n = motif.subn(REMPLACEMENT, texte)
        total += n
    return texte, total


def contient_secret(texte):
    return isinstance(texte, str) and any(m.search(texte) for m, _ in MOTIFS)


def caviarder_objet(objet):
    """Caviarde récursivement les chaînes d'un objet JSON ; rend (objet, nombre de remplacements)."""
    if isinstance(objet, str):
        return caviarder(objet)
    if isinstance(objet, list):
        total, sortie = 0, []
        for element in objet:
            propre, n = caviarder_objet(element)
            sortie.append(propre)
            total += n
        return sortie, total
    if isinstance(objet, dict):
        total, sortie = 0, {}
        for cle, valeur in objet.items():
            propre, n = caviarder_objet(valeur)
            sortie[cle] = propre
            total += n
        return sortie, total
    return objet, 0
