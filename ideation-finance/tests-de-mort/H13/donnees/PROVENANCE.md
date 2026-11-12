# H13 — provenance des fichiers bruts

Tous les fichiers de ce dossier sont enregistrés tels que reçus (octets bruts, aucune retouche). Téléchargés le 2026-11-12 (heures UTC) par `telecharger.py` (agent utilisateur par défaut de Python `urllib`), sauf D1, D1b et D5, pris avec `curl` (agent par défaut). Le sha256, la taille et le nombre de lignes ci-dessous ont été recalculés sur les fichiers présents sur disque au moment d'écrire ce tableau ; ils sont identiques à ceux notés au téléchargement dans `journal_telechargement.tsv` (journal tenu par le script, pas un fichier brut).

Nombre de lignes = nombre de caractères de fin de ligne (`wc -l`), en-tête compris.

## Adresses

| Source | Adresse ou modèle d'adresse |
|---|---|
| D1 | `https://alfred.stlouisfed.org/series/downloaddata?seid=PAYEMS` |
| D1b (recoupement de l'étape 2, non nommé « D » par la préinscription) | `https://alfred.stlouisfed.org/series/downloaddata?seid=UNRATE` |
| D2, lots 01 à 37 | `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS,…(n fois)&vintage_date=AAAA-MM-JJ,…(n dates)` ; n = 12 (6 pour le lot 37) ; les dates sont les 438 dates de D1 du 1989-12-08 au 2026-03-06, dans l'ordre, 12 par lot ; les dates de chaque lot se lisent dans son en-tête |
| D3, lots 01 à 37 | même adresse avec `id=UNRATE,…` ; les dates sont les 435 dates de publication de l'étape 2, dans l'ordre, 12 par lot (3 pour le lot 37) |
| D4 | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2` |
| D5 | `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` |

L'adresse exacte de chaque lot est dans la dernière colonne de `journal_telechargement.tsv`.

## Ordre

D1, puis D2, puis D3, puis D1b ; `emploi_intermediaire.csv` écrit et haché à 19:02:33Z (voir `../journal.md`) ; D4 (19:02:49Z) et D5 (19:04:30Z) seulement ensuite.

## Fichiers

| Fichier | Téléchargé (UTC) | Octets | Lignes | sha256 |
|---|---|---:|---:|---|
| `D1_PAYEMS_downloaddata.html` | 2026-11-12T18:55:36Z | 99957 | 1623 | `d2d58ef3439022b528f0287b8f4213927ce8afefa1a1f71a7352a905c1eff059` |
| `D2_PAYEMS_lot_01.csv` | 2026-11-12T18:56:06Z | 52027 | 623 | `3819af1cb817487028bb010cf3cabc306c680ec34f1b51872af3c2bc83266056` |
| `D2_PAYEMS_lot_02.csv` | 2026-11-12T18:56:09Z | 53167 | 635 | `640e9155c5736afc884d901acebe4aa284794fa9f631e2afca7a09e6d9b8cd51` |
| `D2_PAYEMS_lot_03.csv` | 2026-11-12T18:56:13Z | 54307 | 647 | `b7a3440e73e81c48c8642d8a79f50daba1097c53647801115fa0d1e346f65f40` |
| `D2_PAYEMS_lot_04.csv` | 2026-11-12T18:56:16Z | 55441 | 659 | `0779a4109f433d54bac9176c577a0f0d3be37d07ba90d79759a32bd7066c2c7a` |
| `D2_PAYEMS_lot_05.csv` | 2026-11-12T18:56:19Z | 56575 | 671 | `5124e6cc2fbe8430a32ddc1af4541cbb946c6561cd3e0c9263b221dcd6ffc535` |
| `D2_PAYEMS_lot_06.csv` | 2026-11-12T18:56:23Z | 57715 | 683 | `c1017c2673eeee6411df87c1f7b052b91a62ebfd84acfc6d7d449c6b3c9ffd3e` |
| `D2_PAYEMS_lot_07.csv` | 2026-11-12T18:56:26Z | 58855 | 695 | `41cc89d3cd5e6c5fd062b07fef6c78e6689c6f7814dd65a114ee2e0d6a6de53f` |
| `D2_PAYEMS_lot_08.csv` | 2026-11-12T18:56:30Z | 59995 | 707 | `1a4f536293a0637fc54dd0574dc4e074510970b76033954382e93f31afa276d5` |
| `D2_PAYEMS_lot_09.csv` | 2026-11-12T18:56:34Z | 61135 | 719 | `01f9ce078ef017d68f63322ea66bc4c6c3b0a68431ae2b0ab800155e34b6fb01` |
| `D2_PAYEMS_lot_10.csv` | 2026-11-12T18:56:37Z | 62275 | 731 | `7739f719d056e7cf674e4e17071e5402091281584a6744ee30d35cc6eedb7588` |
| `D2_PAYEMS_lot_11.csv` | 2026-11-12T18:56:41Z | 63415 | 743 | `7e11686ab17ddf4144cc75e5c7404923833f8f3c4d436fb2babaa411bd01c1a2` |
| `D2_PAYEMS_lot_12.csv` | 2026-11-12T18:56:44Z | 64555 | 755 | `4bf04847079de7bd5493bb63fc2b66a8faa1f6fda674557ec227e10d96a8d807` |
| `D2_PAYEMS_lot_13.csv` | 2026-11-12T18:56:48Z | 65695 | 767 | `ba2239b2cc8b17b1e5d3f3879ff81a90d9ff290b17561dbcecff40deb2dd5cc4` |
| `D2_PAYEMS_lot_14.csv` | 2026-11-12T18:56:52Z | 66751 | 778 | `a3369b2df1095974fccf9291f722292819189936e16b89f90b80347cc05bde27` |
| `D2_PAYEMS_lot_15.csv` | 2026-11-12T18:56:56Z | 67797 | 789 | `b30002a9ce7faf3859ec8b25f35d457e5566b90db5da75295b66a12e2a706055` |
| `D2_PAYEMS_lot_16.csv` | 2026-11-12T18:57:00Z | 68937 | 801 | `901767d3c51aae693772add07af60422b63f9cd95f650cb31aca029aca7f04d9` |
| `D2_PAYEMS_lot_17.csv` | 2026-11-12T18:57:04Z | 70077 | 813 | `722d50dbb1b25ba4f9202c739e2275b47bb428be26a0531a3065d6305a9944fd` |
| `D2_PAYEMS_lot_18.csv` | 2026-11-12T18:57:08Z | 71217 | 825 | `288a56dbcf32908e92727aa138ea15837e480e87b24309357e57c59b47bfe40c` |
| `D2_PAYEMS_lot_19.csv` | 2026-11-12T18:57:11Z | 72357 | 837 | `9e4236e62a89ed9f94858f26f6d403b1598a3f31e678000191b6db4da1b756bd` |
| `D2_PAYEMS_lot_20.csv` | 2026-11-12T18:57:15Z | 73497 | 849 | `a5532f6a478600bae77d51b780ab1b2961fab017debf0962fd067332ef257a32` |
| `D2_PAYEMS_lot_21.csv` | 2026-11-12T18:57:19Z | 74637 | 861 | `9f86e64ad3b0e46d0ededc37b5ffc5f445b0c29810f496c8c5873f71065931f8` |
| `D2_PAYEMS_lot_22.csv` | 2026-11-12T18:57:23Z | 75777 | 873 | `cfdb54ed59eb0c83186d09765aa3720961f3b56c10b665b63d9609c26499456e` |
| `D2_PAYEMS_lot_23.csv` | 2026-11-12T18:57:26Z | 76917 | 885 | `f6d52ff183fede7a6d83797d9d10f99258b1a12deda90a4294257d5c0a41f03f` |
| `D2_PAYEMS_lot_24.csv` | 2026-11-12T18:57:30Z | 78057 | 897 | `2a535df6dc15803eb9fc02ef302efedb61b8f82d1627ab8127fd8aaffd79a40b` |
| `D2_PAYEMS_lot_25.csv` | 2026-11-12T18:57:34Z | 79197 | 909 | `e66de8e05aa9e12088f7055b127911fb293c5712949535d3326ac6898d8082d6` |
| `D2_PAYEMS_lot_26.csv` | 2026-11-12T18:57:37Z | 80337 | 921 | `03fa674a599b08f896c9634b47f6e1111a1fba1a226388098336cbb48891c7cb` |
| `D2_PAYEMS_lot_27.csv` | 2026-11-12T18:57:41Z | 81477 | 933 | `0e13d5a8a9bbe96b6359142bba78917b937bdd5273e68b6376253f12f9a229c5` |
| `D2_PAYEMS_lot_28.csv` | 2026-11-12T18:57:45Z | 82617 | 945 | `ad227d16ec36da354f7dd6fbe51dd92ba76cfabbf5ae6cd8b69d9950d331974b` |
| `D2_PAYEMS_lot_29.csv` | 2026-11-12T18:57:49Z | 83757 | 957 | `828f78fa3d0bf6b4c7ceb8b7a3aecd1871a4a159d7464c3bf301d90d766c67b6` |
| `D2_PAYEMS_lot_30.csv` | 2026-11-12T18:57:53Z | 84897 | 969 | `460385bc7e40aed572d1d866cebfdb5254e5dcebd4e9060f7ae9c2538ebb5342` |
| `D2_PAYEMS_lot_31.csv` | 2026-11-12T18:57:56Z | 85990 | 980 | `c128cad8b9624487292df059384ea3ab5c4c6631ba12ce1b6f7b60840394f790` |
| `D2_PAYEMS_lot_32.csv` | 2026-11-12T18:58:00Z | 87082 | 992 | `a3685ffb2f9768161b47442d7bbf3d3dce4dce335c1fa619690e9ec2add6897e` |
| `D2_PAYEMS_lot_33.csv` | 2026-11-12T18:58:03Z | 88222 | 1004 | `056516322973e2caed5970eef462f5279fc039f94ae1516344d519e38ad13f5c` |
| `D2_PAYEMS_lot_34.csv` | 2026-11-12T18:58:07Z | 89362 | 1016 | `5e8368f28085e681201fba0a40e671182c690d8598ea09b3bbd4631a3c6adeff` |
| `D2_PAYEMS_lot_35.csv` | 2026-11-12T18:58:11Z | 90502 | 1028 | `d3a3e797af1fa10d9001ccd94ddfb0b8a4e93b5523f388f7317e15889bf18eb0` |
| `D2_PAYEMS_lot_36.csv` | 2026-11-12T18:58:15Z | 91642 | 1040 | `6e63c7ef6531f3bc80892dae545b1abd399f8ecb1cb49fa3589577b86fe959e9` |
| `D2_PAYEMS_lot_37.csv` | 2026-11-12T18:58:18Z | 52011 | 1047 | `5bbf1065f44c6e79aad990085de0cb4314d7e1f4892b88a51c6120dcef1e430b` |
| `D3_UNRATE_lot_01.csv` | 2026-11-12T18:58:33Z | 30457 | 515 | `f5ea0eaaa4a96414c2843c12863a837b59da17792d6538346768d5eb39c2d781` |
| `D3_UNRATE_lot_02.csv` | 2026-11-12T18:58:37Z | 31165 | 527 | `e129b50787aa50ff2ebbc114b3bd25e7f4ad3ea09720e9b8ae4244ed88c90223` |
| `D3_UNRATE_lot_03.csv` | 2026-11-12T18:58:40Z | 31873 | 539 | `116feef5189195374cace9d4d52bb3b960d62650e4316d3e539938b78807cc4a` |
| `D3_UNRATE_lot_04.csv` | 2026-11-12T18:58:44Z | 32581 | 551 | `6925992c58fc82d2de3e45eb18a6bcd906cc2e6f1ec2f26d04de32dee6a8fc92` |
| `D3_UNRATE_lot_05.csv` | 2026-11-12T18:58:48Z | 33289 | 563 | `b6192140a36263c2cdba36fa0b606d950c999b0cd252ec4a28617363389d8ef2` |
| `D3_UNRATE_lot_06.csv` | 2026-11-12T18:58:51Z | 33997 | 575 | `679b68f614394301dcb81ecb9f34c34da0c8c5e91f78f1518ed27eb72f1fd387` |
| `D3_UNRATE_lot_07.csv` | 2026-11-12T18:58:55Z | 34705 | 587 | `0354c319c6fec54d9e9dc6ae2a79296fe7b78acc80f7c65794b3fe17c0296517` |
| `D3_UNRATE_lot_08.csv` | 2026-11-12T18:58:58Z | 35413 | 599 | `955b499da5f2b1f0f656941198f9aeea78cb3e9186cb2fe69c8f24d71f6ff686` |
| `D3_UNRATE_lot_09.csv` | 2026-11-12T18:59:02Z | 36121 | 611 | `963143da786609c24febe207dfe71a0e3a5b7595cde8b18ea8b7d8ffcc87b96f` |
| `D3_UNRATE_lot_10.csv` | 2026-11-12T18:59:05Z | 36829 | 623 | `9358fb65c898fbaa727d48575d9de00791dc45c77cc469ce5f47b956f1d789d8` |
| `D3_UNRATE_lot_11.csv` | 2026-11-12T18:59:10Z | 37537 | 635 | `433132ed2a39e61bc23c88f81490ca0b7d37af44dd0cf515132904f675e1ad26` |
| `D3_UNRATE_lot_12.csv` | 2026-11-12T18:59:22Z | 38245 | 647 | `e7b53b018098d1f1743de5ce1de11905faae2ee39f16d946e9021c3a8e50a429` |
| `D3_UNRATE_lot_13.csv` | 2026-11-12T18:59:26Z | 38953 | 659 | `862cc228ddb7977de5b8f35b33e6ff55d1490c399b37340a7e264bf6dd0c3441` |
| `D3_UNRATE_lot_14.csv` | 2026-11-12T18:59:46Z | 39661 | 671 | `6269ba6721fb8501297b63534e0003634b36652d79d6a3360eaa339c5977bf93` |
| `D3_UNRATE_lot_15.csv` | 2026-11-12T18:59:50Z | 40369 | 683 | `df16b9ed5bf9f4c04e7b77d68d0cda79fc8c624b55c109fe307d133729b316d8` |
| `D3_UNRATE_lot_16.csv` | 2026-11-12T18:59:53Z | 41077 | 695 | `b016e1cd46c9019de5091462a791d59569c81470628da24fecb8621b270157f9` |
| `D3_UNRATE_lot_17.csv` | 2026-11-12T19:00:04Z | 41785 | 707 | `acbf4c3bb2e5774e9b5645103cb1dd0ed7c42260e806075ebe62d76104f9d6cd` |
| `D3_UNRATE_lot_18.csv` | 2026-11-12T19:00:08Z | 42493 | 719 | `c6deff24958cbe30d18165bd90212fd2553c0bfb9c44a645d8644a95e424aa64` |
| `D3_UNRATE_lot_19.csv` | 2026-11-12T19:00:11Z | 43201 | 731 | `4ab5ce155951709e6c5eceba8d15e15ed3c72bc1baa91df1760af480104df06c` |
| `D3_UNRATE_lot_20.csv` | 2026-11-12T19:00:15Z | 43910 | 743 | `a049b45ef25088005aed8781ec1a19787ed86871937eac43a02ba996e9cf2e74` |
| `D3_UNRATE_lot_21.csv` | 2026-11-12T19:00:18Z | 44652 | 755 | `3f841aa7f4316e7249a454f6e8100b730309c7b1f3ea448c1c58f9b49674eac9` |
| `D3_UNRATE_lot_22.csv` | 2026-11-12T19:00:22Z | 45339 | 767 | `ccd39d5aec9fb4f475c524e1f0521c2aff026955f31f6a3ad3ad98c39bf9d0f6` |
| `D3_UNRATE_lot_23.csv` | 2026-11-12T19:00:25Z | 46045 | 779 | `11ac445344f12ad3feafb302f796a2e52cd0ff2edfdd916b63d323b81deab077` |
| `D3_UNRATE_lot_24.csv` | 2026-11-12T19:00:28Z | 46753 | 791 | `ff71443cda73bca1d47b925f7e4a396accb98920fc333078407c4d28ee8136c3` |
| `D3_UNRATE_lot_25.csv` | 2026-11-12T19:00:32Z | 47461 | 803 | `0d411cb5cac521ab33d887a103a044b02bf7ee72d9c09d1f37ff9517384eaa22` |
| `D3_UNRATE_lot_26.csv` | 2026-11-12T19:00:35Z | 48169 | 815 | `e3347af329a80698b6831c5721f1f4ae433c5f4520fcce13d3be59d02fcd7d1a` |
| `D3_UNRATE_lot_27.csv` | 2026-11-12T19:00:39Z | 48877 | 827 | `9bfec568ba23d682dbd832f60f5b7edc7be83cb2db0ac9f7e9b2a4f692fa5ff2` |
| `D3_UNRATE_lot_28.csv` | 2026-11-12T19:00:42Z | 49585 | 839 | `3449c91f563d2cb7b966b1a74a94fa828e90b6d0c1950c71a23c0fdbad162a69` |
| `D3_UNRATE_lot_29.csv` | 2026-11-12T19:00:46Z | 50293 | 851 | `246deb633ced63058af597b3a08aaf52ecd6ca4ebf6f6d53ef95ce80c56e3fe4` |
| `D3_UNRATE_lot_30.csv` | 2026-11-12T19:00:49Z | 51001 | 863 | `4ba3a7fb8364e26615ec108a251c16e9276fc23e1d001ecda0827f8ac7045a2d` |
| `D3_UNRATE_lot_31.csv` | 2026-11-12T19:00:53Z | 51731 | 875 | `5a19789ed99b2c5680392c8f8a1dc8c1cc4029cc6f68a6df89d4ab187bb3dcfb` |
| `D3_UNRATE_lot_32.csv` | 2026-11-12T19:00:56Z | 52465 | 887 | `c8152a63a18d93365673ae41d533793cd0e060172cc19d0c3f28926ca5f4afab` |
| `D3_UNRATE_lot_33.csv` | 2026-11-12T19:01:00Z | 53173 | 899 | `d488440a83c7da3db61675a4b564933728a491150611dfbfb772be5e6fa065fe` |
| `D3_UNRATE_lot_34.csv` | 2026-11-12T19:01:03Z | 53881 | 911 | `9ba092170d4ed2a4d952bbce9a1c9622dfe52f2308f1ab425d55d6b27e3eee7f` |
| `D3_UNRATE_lot_35.csv` | 2026-11-12T19:01:06Z | 54589 | 923 | `73453d60a48052cda0336e40f398ca04d6d5d94a995e1d5712d2b7966d345f32` |
| `D3_UNRATE_lot_36.csv` | 2026-11-12T19:01:10Z | 55320 | 936 | `a05c54515a0e73aea0822d807da5d55c295155e745c416dfc8eaa766c132daa6` |
| `D3_UNRATE_lot_37.csv` | 2026-11-12T19:01:13Z | 21666 | 939 | `7e4247f38474d326caecdf9c27615d2ab3ffe249da61b1177d99c7643bbb4355` |
| `D1b_UNRATE_downloaddata.html` | 2026-11-12T19:02:43Z | 95116 | 1563 | `224973f74a0b17d71d925015630b994de48de20a802cf034d9ece47a138f61a1` |
| `D4_DGS2.csv` | 2026-11-12T19:02:49Z | 209520 | 13161 | `4d4ee579aa22639298cb3667a693b402b1c3e6e13869d9de9bbf3f71cf937128` |
| `D5_feds200628.csv` | 2026-11-12T19:04:30Z | 16672370 | 17073 | `dfaad994aeaf232bcc3204aec4b30c0f0bbb4db410f8985d55c15390a73ff2bd` |
