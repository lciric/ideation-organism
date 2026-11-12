# Jeu planté de la boucle réelle v65 (à blanc)

Bloc à recopier tel quel dans le texte scellé ; son empreinte (sha256 des octets du JSON entre les deux lignes de clôture) est `jeu_plante_sha256` du plan gelé.

<!-- jeu-plante-v65 : début -->
```json
{
 "archive_de_depart": {
  "K1": {
   "biais": [
    0.0,
    0.941698,
    0.721847
   ],
   "poids": [
    [
     0.0,
     0.0
    ],
    [
     -0.834964,
     0.0
    ],
    [
     -0.242046,
     0.0
    ]
   ],
   "type": "softmax"
  }
 },
 "fausses": {
  "F1": {
   "biais": [
    0.0,
    0.941698,
    0.721847
   ],
   "poids": [
    [
     0.0,
     0.0
    ],
    [
     -0.834964,
     0.0
    ],
    [
     -0.242046,
     0.0
    ]
   ],
   "type": "softmax"
  },
  "F2": {
   "composantes": [
    {
     "biais": [
      0.0,
      0.941698,
      0.721847
     ],
     "poids": [
      [
       0.0,
       0.0
      ],
      [
       -0.834964,
       0.0
      ],
      [
       -0.242046,
       0.0
      ]
     ],
     "type": "softmax"
    },
    {
     "probas": [
      1.0,
      1.0,
      1.0
     ],
     "type": "fixe"
    }
   ],
   "poids": [
    0.8,
    0.2
   ],
   "type": "melange"
  },
  "F3": {
   "composantes": [
    {
     "biais": [
      0.0,
      0.941698,
      0.721847
     ],
     "poids": [
      [
       0.0,
       0.0
      ],
      [
       -0.834964,
       0.0
      ],
      [
       -0.242046,
       0.0
      ]
     ],
     "type": "softmax"
    },
    {
     "probas": [
      0.3,
      0.4,
      0.3
     ],
     "type": "fixe"
    }
   ],
   "poids": [
    0.8,
    0.2
   ],
   "type": "melange"
  },
  "F4": {
   "base": {
    "biais": [
     0.0,
     0.941698,
     0.721847
    ],
    "poids": [
     [
      0.0,
      0.0
     ],
     [
      -0.834964,
      0.0
     ],
     [
      -0.242046,
      0.0
     ]
    ],
    "type": "softmax"
   },
   "inclinaison": [
    0.0,
    0.05,
    -0.05
   ],
   "puissance": 1.2,
   "type": "transformee"
  }
 },
 "instruments": {
  "T-ELIM": {
   "base": {
    "biais": [
     -0.082681,
     0.10575,
     -0.944897
    ],
    "poids": [
     [
      0.833437,
      0.861085
     ],
     [
      -0.583145,
      3.13424
     ],
     [
      1.296203,
      -2.574519
     ]
    ],
    "type": "softmax"
   },
   "puissance": 1.25,
   "type": "transformee"
  },
  "T-MAL": {
   "biais": [
    -0.082681,
    0.10575,
    -0.944897
   ],
   "poids": [
    [
     0.833437,
     0.861085
    ],
    [
     -0.583145,
     3.13424
    ],
    [
     1.296203,
     -2.574519
    ]
   ],
   "type": "softmax"
  }
 },
 "version": "jeu-plante-boucle-reelle-v65",
 "vraies": {
  "V1": {
   "biais": [
    -0.082681,
    0.10575,
    -0.944897
   ],
   "poids": [
    [
     0.833437,
     0.861085
    ],
    [
     -0.583145,
     3.13424
    ],
    [
     1.296203,
     -2.574519
    ]
   ],
   "type": "softmax"
  },
  "V2": {
   "biais": [
    -0.082681,
    0.10575,
    -0.944897
   ],
   "poids": [
    [
     0.0,
     0.861085
    ],
    [
     0.0,
     3.13424
    ],
    [
     0.0,
     -2.574519
    ]
   ],
   "type": "softmax"
  },
  "V3": {
   "base": {
    "biais": [
     -0.082681,
     0.10575,
     -0.944897
    ],
    "poids": [
     [
      0.833437,
      0.861085
     ],
     [
      -0.583145,
      3.13424
     ],
     [
      1.296203,
      -2.574519
     ]
    ],
    "type": "softmax"
   },
   "puissance": 0.08,
   "type": "transformee"
  },
  "V4": {
   "composantes": [
    {
     "biais": [
      -0.082681,
      0.10575,
      -0.944897
     ],
     "poids": [
      [
       0.833437,
       0.861085
      ],
      [
       -0.583145,
       3.13424
      ],
      [
       1.296203,
       -2.574519
      ]
     ],
     "type": "softmax"
    },
    {
     "probas": [
      1.0,
      1.0,
      1.0
     ],
     "type": "fixe"
    }
   ],
   "poids": [
    0.15,
    0.85
   ],
   "type": "melange"
  }
 }
}
```
<!-- jeu-plante-v65 : fin -->
