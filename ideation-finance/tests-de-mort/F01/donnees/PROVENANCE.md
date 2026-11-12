# F01 — Provenance des données brutes

Source unique nommée par la préinscription : Open Source Asset Pricing (Chen et Zimmermann), version 2026.10,
branche `Data-Release-2026.10` du dépôt Hugging Face `OpenSourceAP/CrossSection`. Aucun compte, aucun jeton.
Téléchargement par `curl -sS -L` (jusqu'à cinq essais espacés prévus ; le premier essai a suffi pour chaque fichier).
Les fichiers sont conservés tels que reçus, sans aucune modification.

| Fichier local | Adresse exacte | Date et heure (UTC) | HTTP | Essais | Octets | sha256 | Lignes |
|---|---|---|---|---|---|---|---|
| `SignalDoc.csv` | `https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/Data-Release-2026.10/SignalDoc.csv` | 2026-11-12 16:01:58 | 200 | 1 | 183 100 | `0ceb11020c2138c2477b732948beaac2e67ccaad8428753e3a79af2bb5ea0178` | 331 lignes de données + 1 en-tête ; 29 colonnes ; 212 `Predictor`, 114 `Placebo`, 5 `Drop` |
| `PredictorLSretWide.parquet` | `https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/Data-Release-2026.10/Portfolios/Full%20Sets%20OP/PredictorLSretWide.parquet` | 2026-11-12 16:01:59 | 200 | 1 | 1 439 671 | `fc01df25d4383153cb3ae9e0dd730cc34b6d15a5207abeff09f34beda45bca58` | 1 200 lignes (mois, de 1926-01 à 2025-12) ; 213 colonnes (`date` de type `date32[day]` + 212 colonnes `double`) ; 175 529 rendements présents, 78 871 cases vides |
| `Release Notes 2026.10.md` (pour mémoire, non utilisé par les scripts) | `https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/Data-Release-2026.10/Release%20Notes%202026.10.md` | 2026-11-12 16:01:59 | 200 | 1 | 12 112 | `b349234f44b93df298a8f883099a7d9c67bea59a790e1c114741b7be8d663e33` | 129 lignes de texte |

Tailles attendues par la préinscription (§ 3) : 183 100 et 1 439 671 octets — **identiques** aux tailles reçues.

Lecture du Parquet : `pyarrow` 26.0.1 installé par `pip install pyarrow` (absent de la machine, comme prévu par la préinscription).
