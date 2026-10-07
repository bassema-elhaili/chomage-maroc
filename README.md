# Le chômage au Maroc — Analyse de données

**Question traitée :** *« Pourquoi le taux de chômage augmente sans cesse au Maroc ? »*

Projet de **Base de données & Data Science** — traitement d'un jeu de données public,
génération de graphiques avec Python et rédaction d'une analyse.

> ## ⚠️ Le résultat principal
>
> **Les données contredisent la prémisse de la question.**
> Le taux de chômage total marocain **n'augmente pas sans cesse : il a baissé de 4,50 points
> entre 1991 et 2025** (13,50 % → 9,00 %, source Banque Mondiale / OIT).
>
> Ce qui augmente réellement : **le chômage des jeunes** (+ 6,44 points depuis 2004)
> et **la prime de chomage des jeunes**, passée de × 1,46 à × 2,43.
>
> Et la baisse du total s'explique en partie par un artefact : **le taux d'activité
> s'effondre** (− 7,27 points), donc les gens quittent le marché du travail au lieu
> de trouver un emploi.

---

## Le rapport

👉 **[`rapport/rapport.md`](rapport/rapport.md)** — l'analyse complète
(problématique, méthode, résultats, interprétation, limites, conclusion)

---

## Contenu du dépôt

```
chomage-maroc/
├── README.md                    ← ce fichier
├── requirements.txt             ← dépendances Python
├── photo.jpg                    ← photo (consigne n°4)
├── support-de-cours.pdf         ← support de cours, 63 slides, compressé (consigne n°4)
├── cv.pdf                       ← CV au format ATS, 1 page (consigne n°3)
│
├── data/
│   ├── JOB-01_chomage_maroc.csv ← dataset Banque Mondiale (36 lignes, 11 indicateurs)
│   ├── JOB-02_chomage_hcp.csv   ← chiffres officiels HCP 2023-2025
│   ├── JOB-01_metadonnees.json  ← traçabilité : quel indicateur vient d'où
│   ├── SOURCES.md               ← ⚠️ liens vers TOUTES les sources
│   └── brut/                    ← réponses brutes de l'API (1 CSV par indicateur)
│
├── scripts/
│   ├── 01_telecharger.py        ← télécharge les données depuis l'API
│   ├── 02_analyse.py            ← génère les 4 graphiques + les statistiques
│   └── compresser_support.py    ← réduit la taille du support de cours
│
├── graphs/
│   ├── fig1_paradoxe_chomage.png
│   ├── fig2_taux_activite.png
│   ├── fig3_categories_hcp.png
│   └── fig4_qualite_emploi.png
│
└── rapport/
    └── rapport.md
```

---

## Les 4 graphiques

| Figure | Sujet | Message |
|---|---|---|
| **1** | Chômage total vs 15-24 ans, 1991-2025 | Le total baisse, les jeunes montent |
| **2** | Taux d'activité et d'emploi, 1990-2025 | − 7,27 points : l'explication de la baisse |
| **3** | Variation par catégorie, HCP 2024→2025 | Le total baisse *seulement* pour les hommes et les seniors |
| **4** | Qualité de l'emploi, 2023-2025 | Le chômage baisse mais le sous-emploi et la longue durée montent |

---

## Comment reproduire les résultats

### Prérequis

- Python 3.10 ou plus récent
- Une connexion Internet (pour le téléchargement des données)

### Installation

```bash
cd chomage-maroc
pip install -r requirements.txt
```

### Exécution

```bash
# Étape 1 : télécharge les données depuis l'API Banque Mondiale
python scripts/01_telecharger.py

# Étape 2 : génère les 4 graphiques et affiche les statistiques
python scripts/02_analyse.py
```

Les figures sont régénérées dans `graphs/` et les statistiques clés sont affichées
dans le terminal (elles sont également reprises dans le rapport).

---

## Sources

| Source | Usage | Lien |
|---|---|---|
| **Banque Mondiale / OIT** | Série longue 1991-2025, 11 indicateurs | <https://data.worldbank.org/country/morocco> |
| **HCP** — Enquête Nationale sur l'Emploi | Chiffres officiels 2023-2025, segmentation détaillée | <https://www.hcp.ma/Marche-du-travail_r423.html> |

⚠️ **À lire absolument :** les deux sources ne donnent pas le même taux de chômage
pour la même année (9,0 % contre 13,0 % en 2025) car leurs méthodologies diffèrent.
Le détail de cette différence est expliqué dans le rapport et dans
[`data/SOURCES.md`](data/SOURCES.md). **Ne compare jamais les deux séries directement.**

---

## Avertissement sur la question posée

Ce travail ne cherche pas à confirmer la question, mais à la **tester**.
C'est une démarche scientifique : si l'hypothèse est infirmée par les données,
il faut le dire et expliquer pourquoi les données racontent autre chose.

C'est ce qui a été fait ici, et c'est la partie la plus intéressante du résultat.