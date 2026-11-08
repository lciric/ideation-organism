# Plan et jeu planté du mode à blanc de la v65 (exploratoire, non scellé)

Mêmes blocs que ceux du texte scellé de la course (plan gelé, jeu planté) ; lus par les mêmes fonctions.

<!-- plan-gele-v65 : début -->
generations: 2
bras: reel_seul
cartes_par_proposeur: 6
m_e_bh: 22
plafond_modeles_usd: 40
plafond_kimi_usd: 33
plafond_argon_usd: 7
plafond_machine_usd: 5
duree_h: 72
d9: mecanique
configuration_sha256: c5ba60638a472048bcd538f5c5e928b83d2052db14eee9590c47abd7e5d164ea
go: GO-2026-11-08-02
monde_sha256: fdf4d5c1ca0d2971b416ee5f694deff7a4696fe5defb3a6a1843dffef1231877
heritage_depart_sha256: 61d47d6f109b8e14ddfcfc385ed72c981c4df6d4843ffa21f9e06096ef115288
jeu_plante_sha256: 9d1250350e2438ddaa1c8183973710b01506f81e646d9d60338ef2a21a2af15a
<!-- plan-gele-v65 : fin -->

<!-- jeu-plante-v65 : début -->
```json
{"fausses":{"F1":{"ligne_du_banc":"T17s","loi":{"biais":[0.0,0.941698,0.721847],"poids":[[0.0,0.0],[-0.834964,0.0],[-0.242046,0.0]],"type":"softmax"}},"F2":{"ligne_du_banc":"T03u","loi":{"composantes":[{"biais":[0.0,0.941698,0.721847],"poids":[[0.0,0.0],[-0.834964,0.0],[-0.242046,0.0]],"type":"softmax"},{"probas":[1.0,1.0,1.0],"type":"fixe"}],"poids":[0.8,0.2],"type":"melange"}},"F3":{"ligne_du_banc":"T03b","loi":{"composantes":[{"biais":[0.0,0.941698,0.721847],"poids":[[0.0,0.0],[-0.834964,0.0],[-0.242046,0.0]],"type":"softmax"},{"probas":[0.3,0.4,0.3],"type":"fixe"}],"poids":[0.8,0.2],"type":"melange"}},"F4":{"ligne_du_banc":"T05s","loi":{"base":{"biais":[0.0,0.941698,0.721847],"poids":[[0.0,0.0],[-0.834964,0.0],[-0.242046,0.0]],"type":"softmax"},"inclinaison":[0.0,0.05,-0.05],"puissance":1.2,"type":"transformee"}}},"instruments":{"T-ELIM":{"loi":{"base":{"biais":[-0.082681,0.10575,-0.944897],"poids":[[0.833437,0.861085],[-0.583145,3.13424],[1.296203,-2.574519]],"type":"softmax"},"puissance":1.25,"type":"transformee"},"seuil":"au moins 2,0"},"T-MAL":{"loi":{"biais":[-0.082681,0.10575,-0.944897],"poids":[[0.833437,0.861085],[-0.583145,3.13424],[1.296203,-2.574519]],"type":"softmax"},"sans_statistique":true}},"version":"jeu-plante-v65","vraies":{"V1":{"biais":[-0.082681,0.10575,-0.944897],"poids":[[0.833437,0.861085],[-0.583145,3.13424],[1.296203,-2.574519]],"type":"softmax"},"V2":{"biais":[-0.082681,0.10575,-0.944897],"poids":[[0.0,0.861085],[0.0,3.13424],[0.0,-2.574519]],"type":"softmax"},"V3":{"base":{"biais":[-0.082681,0.10575,-0.944897],"poids":[[0.833437,0.861085],[-0.583145,3.13424],[1.296203,-2.574519]],"type":"softmax"},"puissance":0.08,"type":"transformee"},"V4":{"composantes":[{"biais":[-0.082681,0.10575,-0.944897],"poids":[[0.833437,0.861085],[-0.583145,3.13424],[1.296203,-2.574519]],"type":"softmax"},{"probas":[1.0,1.0,1.0],"type":"fixe"}],"poids":[0.15,0.85],"type":"melange"}}}
```
<!-- jeu-plante-v65 : fin -->
