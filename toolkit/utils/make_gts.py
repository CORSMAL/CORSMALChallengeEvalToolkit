
import os
import json

gts = {
    "deformability" : {
        "unit" : None,
        "cup1" : "high",
        "cup2" : "medium",
        "cup3" : "medium",
        "cup4" : "none"
    },
    "transparency" : {
        "unit" : None,
        "cup1" : "medium",
        "cup2" : "low",
        "cup3" : "high",
        "cup4" : "high"
    },
    "width_at_the_top" : {
        "unit" : "cm",
        "cup1" : 7.2,
        "cup2" : 9.7,
        "cup3" : 9.9,
        "cup4" : 8.0
    },
    "width_at_the_bottom" : {
        "unit" : "cm",
        "cup1" : 4.3,
        "cup2" : 6.1,
        "cup3" : 6.5,
        "cup4" : 6.5
    },
    "height" : {
        "unit" : "cm",
        "cup1" : 8.2,
        "cup2" : 12.1,
        "cup3" : 13.6,
        "cup4" : 13.5
    },
    "weight" : {
        "unit" : "g",
        "cup1" : 2.0,
        "cup2" : 10.0,
        "cup3" : 9.0,
        "cup4" : 134.0
    },
    "volume" : {
        "unit" : "ml",
        "cup1" : 179.0,
        "cup2" : 497.0,
        "cup3" : 605.0,
        "cup4" : 354.0
    },
    "filling_amount" : {
        "unit" : "ml",
        "cup1" : 125.0,
        "cup2" : 400.0,
        "cup3" : 450.0,
        "cup4" : 300.0
    }
}

with open(os.path.join('benchmark_groundtruths.json'), 'w') as f:
    json.dump(gts, f, indent=4, sort_keys=False)