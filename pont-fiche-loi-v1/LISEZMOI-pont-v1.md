# Pont « fiche de course → fiche-loi du pôle » — LISEZMOI v1

Lignée conv-audit, rédacteur neuf (Opus), 1er novembre 2026, de 09:24 à 09:48 UTC (relevés `date -u`). Décision de Lazar
R-1037 (registre de la branche conv-audit, l. 1001). Aucun commit, aucun compagnon `.sha256` écrit (scellement laissé à
l'appelant), aucun fichier existant modifié, rien lu sous `donnees/`, dossier `bras-attaque-v1/` non ouvert, aucun appel de
réseau ni de modèle.

## État

| pièce | rôle | SHA-256 |
|---|---|---|
| `conception-pont-fiche-loi-v1.md` | conception : objets, traduction, trois sorties, qui traduit, gardes R5, coût, changements de l'orchestrateur, préenregistrement court du premier essai, cinq décisions, antériorités | `5161e199e15dacc728d4b2e7b1769f700e0a293c05fb26d402dfe40d25c4a974` |
| `pont_v1.py` | module, bibliothèque standard ; appels de modèle injectés | `9fb2d9366e7764d4fc810b921e8565ca2dcae9af5f1b30ec8866efeb5d3eb692` |
| `essais/test_pont_v1.py` | 82 essais (cas sain et artefact par garde) | `4e31189b8eeaaa10b9af80637a518865426a2b6d910566ec691226e5e99e1f40` |

Consigne figée du traducteur (`pont_v1.CONSIGNE_TRADUCTEUR`, 2 404 caractères) :
`fd7aa5f2fc92967b2f8b9e9ca161676b8bdfd696431b73a0307b28bb5517e2e4`.

**Essais** (Python 3.13.18, pytest 9.1.1, `python3 -I -B`, depuis un dossier temporaire vide, sans cache) :
- seuls : **77 réussis, 5 ignorés** — les 5 ignorés sont le groupe de compatibilité v56, ignoré avec son motif
  (« PONT_POLE_V56 absent ») ;
- avec `PONT_POLE_V56=<dossier où l'archive v56 est dépliée>` : **82 réussis** — la proposition du pont passe la **vraie**
  `proposeur.valider_proposition` (stratégie ajoutée au catalogue le temps de l'essai), les trois formes de loi passent
  `selection_pari.valider_loi` et donnent les mêmes probabilités que `selection_pari.proba` (à 10⁻¹² près), le contraste passe
  `pari_apparie.verifier_coefficients` et `engagement_apparie.construire` sur une banque de scores synthétique ; sans la
  stratégie au catalogue, la vraie garde refuse et le pont renvoie N11.
- **Banc de mutations** (script hors dépôt, dossier temporaire) : 25 mutations, **25 tuées** ; une survivante au premier
  passage (« effet nul accepté », couverte en profondeur par le contrôle de divergence) a été tuée par un essai ajouté.

Jouer : `cd <dossier vide> && python3 -I -B -m pytest -q -p no:cacheprovider <ce dossier>/essais/test_pont_v1.py`.

## Ce qui reste

1. **Tes décisions** D-P1 à D-P4 (proposer avec recommandation, défaut sous 48 heures) et **D-P5** (nœud : premier essai, devis
   et GO chez session-depot) — conception § h.
2. **Contre-lecture R2** (« œil neuf », par un modèle d'une autre famille que l'auteur) du module, des essais et du
   préenregistrement court (§ g), puis scellement.
3. **Couche v57** de l'orchestrateur (§ f) : `pole/pont_v1.py` copié, `proposeur_v57.py` (stratégie acceptée du pont seul),
   `etage_pont_v57.py`, `catalogue_public_v57.py`, configuration et budget des rôles « traducteur » et « contre_traducteur »,
   lignes R5 au départ. Rien de cela n'est écrit ici.
4. **Témoins du pont** (6) à écrire par un metteur en forme tiers ; **tirage des 10 fiches** de la course 1 par session-depot.
5. **Épreuve fraîche** (banque sœur ou épisodes honnêtes de couche 2) : sans elle, aucune sortie 1 décisive (D-P4).
6. **Antériorités** (§ i) à lire sur PDF empreinté, POPPER d'abord.

## Pièces lues (SHA-256 calculés ici ; compagnons vérifiés quand ils existent)

| pièce (depuis la racine du dépôt) | SHA-256 | compagnon |
|---|---|---|
| `brouillons/canal-reprise-releve-v1/envois/pole-scientifique-automatique-v1/integration-proposeurs-ia-v1.md` | `974b2dbe17b76975f8e9198f5852a36513f8a428b44874740e31395b34124184` | conforme |
| `…/conception-pole-scientifique-v1.md` | `a4f94148c9c55b76f208edecd7220b51a8e21ca69f52e50c7f2abb6484b81b52` | conforme |
| `…/programme-conception-organisme-v7.md` | `b7cd2f56bf99357caf51493ca0ed966753711926c91c094f971197b29c7192fd` | **absent** (R11 : vérifié sur disque) |
| `…/question-mere-course-v1/question-mere-course-ideation-v3.md` | `1b08e17fddcf13ea34c913f267fe3f02bfba8c62a1af507954cfd460de60f8f0` | conforme |
| `…/question-mere-course-v1/recoupement-v1/question-course-2-defense-fusion-v5.md` (texte I, l. 1-80) | `a750144963913ba1c3dcf3eed5d4f8322d7d0246135e17c95ac8e7253c2dd680` | conforme |
| `…/generation-0/synthese-generation-0-v1.md` | `51a32aec567842d4a41fa59290f04478bac9213070180c83b769219c18d2303c` | conforme |
| `…/premier-lancement-reel/lecture-lancement-reel-a-bis-v1.md` | `cc475e042c15870e526ce322997dcec801652a9cfd79f3020d00f2bca538d9e4` | conforme |
| `…/demonstration-couche1-v7/lecture-couche1-v7-v2.md` | `e2946dd65c573fa00ce8eac90bf1640269b1a800efe6531adb2a9cce108d2c9e` | conforme |
| `…/couche1bis-lecture-v2/lecture-couche1bis-v2.md` (verdict seul) | `347b62fdc122325e09612c2d185318390213e0b70a9c06d62b25e9b0d491db12` | conforme |
| `…/demonstration-couche1-proposeur-v7/lecture-couche1-proposeur-v7-v1.md` (verdict seul) | `6053476b85ea089ce308f3ccb2666112b68a04403589d6e8b6278fa98dde1608` | conforme |
| `docs/notes/ideation-organisme-v1/explication-organisme-v1/dossier-factuel-organisme-v1.md` | `0751fc8cf4aa0a9eaccb23d80cb06220fa3db9805092bd1d854bc68fce7ae250` | conforme |
| `docs/notes/ideation-organisme-v1/orchestrateur-v56/CODE-orchestrateur-pole-v7-v56.zip` | `29b1b38cfee5e279a06c947fdf1f855628b574e81e44c2d7e48a029151c1b24c` | conforme |
| `docs/notes/ideation-organisme-v1/orchestrateur-v56/LISEZMOI-orchestrateur-pole-v7-v56.md` | `3e32709ad5f46016461b10b4ab8594e657433d36272f555c07c4f7f97e43d506` | conforme |
| `registres/decisions.md` (ligne 1001, R-1037 ; fichier de 1 005 lignes au moment de la lecture) | `7cdacbccbda0177a566cee9df5508e63241bdbfe0f988c1c5711facb863ed220` | absent (registre vivant) |

Fichiers lus **dans l'archive v56**, dépliée hors du dépôt (dossier temporaire de la session) :

| fichier de l'archive | SHA-256 |
|---|---|
| `pole/__init__.py` | `f7341b965ddba1e0fb21b44d9068f59650d5c77e3175f2b6b7ca879219fa5c9b` |
| `pole/fiche.py` | `ec018f147196222268d91358ce2038bb35bf76069e6bf8928dea9e3db59d1074` |
| `pole/selection_pari.py` | `359928110d757cd54cc0d2773910c7360895b68cac5d17e0e4b4e9933ef306bc` |
| `pole/proposeur.py` | `a77018584ec5d20c25224fc675c412c4606ba3a6ce8dfde6e469a651a425a2ea` |
| `pole/proposeurs_references.py` | `6ed7e56fb1a1f7441467281d414b892176e73a1ffa528db090684cb6cf20805c` |
| `pole/monde_banque.py` | `33088eb9088549a20ffd489687928a1f1469d1df85a025db29bc9ce3f93e7b18` |
| `pole/monde_banque_scores.py` (l. 1-130) | `58d4fee878fe7957e163a6b5b791adf8895eb2e136aad55502c011b314bccb28` |
| `pole/pari_apparie.py` (en-tête, `verifier_coefficients`) | `ec6c2cf64d0c9a3bcb3484f2bc58ca986c89e97829bd45fdb96cbc42bf094fef` |
| `pole/engagement_apparie.py` (l. 1-140) | `fd80872a2e4770a334528b37ccfca6913e093afb350649fe42949b8e93764b0e` |
| `pole/fiches_v53.py` | `7cfcf8329c66c7a37ceb2992cc96e21aedbfa0a10525467672794090a128eda6` |
| `pole/fiches_v54.py` | `1ab0796dd5d9de14ea84953b0307a065572bc300ebe45209ca207d7880bbaebf` |
| `pole/tests_de_mort_v2.py` (en-tête) | `363a3725885da08412f25b28defba7a8d204d883c3637f1de1df83686d93a41a` |
| `pole/tests_de_mort_v3.py` | `ea05eb55f9d179501fb091d25298deaf36cd66ad16fd65bdca4dcf5e4ba74bba` |
| `pole/etage_entre_generations_v53.py` (l. 1-90) | `d568d25bf7d96011cfdcda12e7bc2c1933a61827b237f8c8c363b4055122ad4b` |
| `pole/etage_entre_generations_v56.py` | `f0c80e2d9801d4a928574f7f442e2950c2d130d77015b30102911bfa87dd6eba` |
| `pole/noyau_v56.py` (en-tête) | `eb5a003e8f23b0882e5588fe537e8b65b890f0d7d19560896be4e85a0731543b` |
| `pole/cycle.py` (l. 255-470) | `798f039042e3ee1f18df5c566f5a0ddee5dac5c98225c8ce621e267174c8ee18` |
| `pole/ideation_v2.py` (en-tête, gabarit l. 380-500) | `67d2ad3591b21601ece4101154138f532ba519024761beb8c9738181f8f3fefc` |
| `pole/outils.py` (fonctions d'empreinte) | `966d9553026aad1eb7d97fa677334f1b59f22a39f15eef95134d63bc47634444` |
| `demonstrations/banc_tricheurs_v7.py` (en-tête) | `ef016d250b7b503f705dc95919719c68c8f968534fd901df7364a6062d67cf12` |
| `exemples/banque-t05-v2.json` (**structure seulement** : clés, noms des traits et des moniteurs, effectifs par partie ; aucune issue lue) | `f26cc85794f0e65bca6217911f862414f1489195b9bf3ada51d22a3af0fe0d71` |
| `exemples/construire_banque_t05_v3.py` (en-tête) | `dff00005b80e8bfdd5cf3198336cbaebd0ca21752dc1c0d983835cc71f7fdaeb` |
| `essais/aides_v53.py` (liste des champs d'essai) | `4aaddd698fe1400430e59d5449541acde8f7a6346169a1978d533e948b79c51e` |

## Réserves

1. Exploratoire, non opposable ; modèles factices ; compatibilité v56 jouée sur des banques synthétiques seulement.
2. Format de la course 1 SUPPOSÉ (gabarit de `ideation_v2.py`) ; noms des champs de la course 2 injectés par la configuration.
3. Parts attendues des sorties et coûts : SUPPOSÉ jusqu'au premier essai ; approximations de puissance dites (conception § d).
4. `programme-conception-organisme-v7.md` n'a pas de compagnon `.sha256` : son empreinte ci-dessus est celle lue ce jour.
5. Antériorités non vérifiées sur PDF (R7).
