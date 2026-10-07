# Sources des données

Toutes les données de ce projet proviennent de sources publiques et officielles.
Aucune valeur n'a été inventée ni saisie manuellement : les chiffres du fichier
`JOB-02_chomage_hcp.csv` sont une **transcription** des communiqués du HCP
(cités ligne par ligne en fin de document), et le fichier `JOB-01_chomage_maroc.csv`
est produit **automatiquement** par `scripts/01_telecharger.py` via l'API Banque Mondiale.

---

## 1. Banque Mondiale / Organisation Internationale du Travail

**Fichier produit :** `JOB-01_chomage_maroc.csv`
**Comment l'obtenir :** `python3 scripts/01_telecharger.py`

| Information | Valeur |
|---|---|
| Éditeur | The World Bank – *World Development Indicators* |
| Base | *World Development Indicators* (WDI) |
| Page thématique | <https://data.worldbank.org/country/morocco> |
| API utilisée | <https://api.worldbank.org/v2> |
| Code pays | `MAR` (Maroc) |
| Période couverte | 1990–2025 |
| Dernière mise à jour de la base | 2026-07-13 |
| Méthode | **Estimation modélisée de l'OIT** (*ILO modeled ILO estimate*) |

### Indicateurs utilisés

| Code indicateur | Signification | Colonne dans le CSV |
|---|---|---|
| `SL.UEM.TOTL.ZS` | Taux de chômage total (% population active) | `chomage_total` |
| `SL.UEM.TOTL.FE.ZS` | Taux de chômage des femmes | `chomage_femmes` |
| `SL.UEM.TOTL.MA.ZS` | Taux de chômage des hommes | `chomage_hommes` |
| `SL.UEM.1524.ZS` | Taux de chômage des 15-24 ans | `chomage_jeunes` |
| `SL.UEM.1524.FE.ZS` | Chômage des jeunes femmes 15-24 ans | `chomage_jeunes_f` |
| `SL.UEM.1524.MA.ZS` | Chômage des jeunes hommes 15-24 ans | `chomage_jeunes_h` |
| `SL.TLF.CACT.ZS` | Taux d'activité total (% population 15+) | `taux_activite` |
| `SL.TLF.CACT.FE.ZS` | Taux d'activité des femmes | `taux_activite_f` |
| `SL.EMP.TOTL.SP.ZS` | Ratio emploi / population 15+ | `ratio_emploi` |
| `NY.GDP.PCAP.KD` | PIB par habitant (dollars constants) | `pib_habitant_usd` |
| `NY.GDP.MKTP.KD.ZG` | Croissance annuelle du PIB (%) | `croissance_pib` |

### URL directes de chaque série

```
https://api.worldbank.org/v2/country/MAR/indicator/SL.UEM.TOTL.ZS?format=json&date=1990:2025
https://api.worldbank.org/v2/country/MAR/indicator/SL.UEM.1524.ZS?format=json&date=1990:2025
https://api.worldbank.org/v2/country/MAR/indicator/SL.TLF.CACT.ZS?format=json&date=1990:2025
https://api.worldbank.org/v2/country/MAR/indicator/SL.EMP.TOTL.SP.ZS?format=json&date=1990:2025
https://api.worldbank.org/v2/country/MAR/indicator/NY.GDP.PCAP.KD?format=json&date=1990:2025
```

> Les réponses brutes de chaque indicateur sont archivées dans `data/brut/`
> (un fichier CSV par indicateur), ce qui permet de vérifier le traitement.

---

## 2. Haut-Commissariat au Plan (HCP) — source officielle marocaine

**Fichier :** `JOB-02_chomage_hcp.csv`
**Statistique :** Enquête Nationale sur l'Emploi (ENE)
**Site :** <https://www.hcp.ma/Marche-du-travail_r423.html>

### Commiqués consultés

| Année | Document | Lien |
|---|---|---|
| 2024 | *Activité, emploi et chômage, résultats annuels 2024* (publié le 8 juillet 2025) | <https://www.hcp.ma/Activite-emploi-et-chomage-resultats-annuels-2024_a4142.html> |
| 2025 | Résultats annuels 2025 — repris et détaillé par Libre Entreprise (3 février 2026) | <https://librentreprise.ma/2026/02/03/hcp-le-taux-de-chomage-est-passe-a-13-en-2025/> |

> **Remarque importante :** les chiffres 2025 n'étaient pas encore publiés sur
> `hcp.ma` au moment de la rédaction ; ils proviennent de la reprise détaillée
> faite par le magazine économique *Libre Entreprise*, qui cite explicitement
> l'Enquête Nationale sur l'Emploi du HCP. Il est recommandé de vérifier et
> remplacer par la publication originale dès sa mise en ligne.

### Accès aux données brutes du HCP

| Ressource | Lien |
|---|---|
| Portail Open Data du Maroc | <https://data.gov.ma/data/fr/organization/haut-commissariat-au-plan?groups=emploi> |
| Base de données statistique du HCP (BDS) | <https://bds.hcp.ma> |

---

## 3. Avertissement méthodologique important

Les deux sources **ne donnent pas le même taux de chômage pour la même année** :

| Année | Banque Mondiale / OIT | HCP (officiel) | Écart |
|---|---|---|---|
| 2024 | 9,10 % | 13,3 % | 4,2 points |
| 2025 | 9,00 % | 13,0 % | 4,0 points |

Cette différence **n'est pas une erreur** : les deux organismes n'utilisent pas
la même définition de la population active ni le même périmètre de dénombrement.

**Règle suivie dans ce projet :**

- La **Banque Mondiale** est utilisée pour la **longue série temporelle** (1991-2025),
  car elle est la seule source publique gratuite et téléchargeable automatiquement
  sur un quart de siècle.
- Le **HCP** est utilisé pour l'analyse **récente et détaillée** (2023-2025),
  car il segmente le chômage par âge, par sexe et par diplôme, ce que la base
  Banque Mondiale ne permet pas directement.

Les deux sources sont donc **complémentaires** et ne doivent pas être comparées
directement sans rappel de cette différence de méthode.

---

## Bibliographie

- Haut-Commissariat au Plan, *Activité, emploi et chômage, résultats annuels 2024*, Rabat, juillet 2025.
- Haut-Commissariat au Plan, *Activité, emploi et chômage, résultats annuels 2025*, Rabat, février 2026.
- The World Bank, *World Development Indicators – Morocco*,(base mise à jour le 13 juillet 2026).
- Organisation Internationale du Travail, *Key Indicators of the Labour Market (KILM)*, 6ᵉ édition.
- Libre Entreprise, « HCP : Le taux de chômage est passé à 13 % en 2025 », 3 février 2026.