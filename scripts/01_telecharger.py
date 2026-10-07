"""
01_telecharger.py
================
Question 3 : "Pourquoi le taux de chomage augmente sans cesse au Maroc ?"

Telecharge les series de la Banque Mondiale (API officielle) pour le Maroc
et les assemble en un seul fichier CSV propre.

Source : https://api.worldbank.org  (World Development Indicators)
Usage   : python 01_telecharger.py
"""

import json
import time
from pathlib import Path

import pandas as pd
import requests

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
PAYS = "MAR"  # code ISO3 du Maroc
DATE_DEBUT = 1990
DATE_FIN = 2025
URL_API = f"https://api.worldbank.org/v2/country/{PAYS}/indicator"
TIMEOUT = 40
MAX_TENTATIVES = 3

# Chaque indicateur : (code World Bank, nom de colonne dans le CSV, libelle)
INDICATEURS = {
    "SL.UEM.TOTL.ZS":    ("chomage_total",      "Taux de chomage total (% de la population active)"),
    "SL.UEM.TOTL.FE.ZS": ("chomage_femmes",     "Taux de chomage des femmes (%)"),
    "SL.UEM.TOTL.MA.ZS": ("chomage_hommes",     "Taux de chomage des hommes (%)"),
    "SL.UEM.1524.ZS":    ("chomage_jeunes",     "Taux de chomage des 15-24 ans (%)"),
    "SL.UEM.1524.FE.ZS": ("chomage_jeunes_f",   "Taux de chomage des jeunes femmes 15-24 ans (%)"),
    "SL.UEM.1524.MA.ZS": ("chomage_jeunes_h",   "Taux de chomage des jeunes hommes 15-24 ans (%)"),
    "SL.TLF.CACT.ZS":    ("taux_activite",      "Taux d'activite total (% de la population 15+)"),
    "SL.TLF.CACT.FE.ZS": ("taux_activite_f",    "Taux d'activite des femmes (%)"),
    "SL.EMP.TOTL.SP.ZS": ("ratio_emploi",       "Ratio emploi / population active (%)"),
    "NY.GDP.PCAP.KD":    ("pib_habitant_usd",   "PIB par habitant en dollars constants"),
    "NY.GDP.MKTP.KD.ZG": ("croissance_pib",     "Croissance annuelle du PIB (%)"),
}

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DATA = RACINE / "data"
DOSSIER_BRUT = DOSSIER_DATA / "brut"


# --------------------------------------------------------------------------
# Telechargement
# --------------------------------------------------------------------------
def telecharger_indicateur(code: str) -> pd.DataFrame:
    """Recupere une serie temporelle depuis l'API Banque Mondiale."""
    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            reponse = requests.get(
                f"{URL_API}/{code}",
                params={
                    "format": "json",
                    "per_page": 1000,
                    "date": f"{DATE_DEBUT}:{DATE_FIN}",
                },
                timeout=TIMEOUT,
            )
            reponse.raise_for_status()
            donnees = reponse.json()

            # index 0 = metadonnees, index 1 = observations
            if len(donnees) < 2 or not donnees[1]:
                print(f"  [vide] {code}")
                return pd.DataFrame(columns=["annee", "valeur"])

            observations = donnees[1]
            cadre = pd.DataFrame(
                {
                    "annee": [int(o["date"]) for o in observations],
                    "valeur": [o["value"] for o in observations],
                }
            )
            cadre = cadre.dropna(subset=["valeur"]).sort_values("annee")
            print(f"  [ok]   {code}  ->  {len(cadre)} observations "
                  f"({cadre['annee'].min()}-{cadre['annee'].max()})")
            return cadre

        except Exception as erreur:
            print(f"  [essai {tentative}/{MAX_TENTATIVES}] {code} : {erreur}")
            time.sleep(3)

    raise RuntimeError(f"Impossible de telecharger l'indicateur {code}")


# --------------------------------------------------------------------------
# Construction du dataset final
# --------------------------------------------------------------------------
def main() -> None:
    DOSSIER_DATA.mkdir(parents=True, exist_ok=True)
    DOSSIER_BRUT.mkdir(parents=True, exist_ok=True)

    print(f"Telchargement des donnees Banque Mondiale - Maroc ({DATE_DEBUT}-{DATE_FIN})\n")

    colonnes = {}
    metadonnees = {}

    for code, (colonne, libelle) in INDICATEURS.items():
        cadre = telecharger_indicateur(code)

        # archive brute : la source est ainsi conservee et verifiable
        brut = DOSSIER_BRUT / f"{code}.csv"
        cadre.to_csv(brut, index=False)

        colonnes[colonne] = cadre.set_index("annee")["valeur"].rename(colonne)
        metadonnees[code] = {
            "colonne": colonne,
            "libelle": libelle,
            "url_api": f"{URL_API}/{code}?format=json&date={DATE_DEBUT}:{DATE_FIN}",
            "n_observations": int(len(cadre)),
            "periode": (
                f"{int(cadre['annee'].min())}-{int(cadre['annee'].max())}"
                if len(cadre) else "vide"
            ),
        }
        time.sleep(0.6)  # menager l'API

    # fusion sur l'annee
    dataset = pd.concat(colonnes.values(), axis=1).sort_index()
    dataset.index.name = "annee"
    dataset = dataset.round(3).reset_index()

    chemin_csv = DOSSIER_DATA / "JOB-01_chomage_maroc.csv"
    dataset.to_csv(chemin_csv, index=False, encoding="utf-8")

    # tracabilite : quelles colonnes viennent de quel indicateur
    with open(DOSSIER_DATA / "JOB-01_metadonnees.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "pays": "Maroc",
                "code_pays": PAYS,
                "source": "World Bank - World Development Indicators",
                "url_source": "https://data.worldbank.org/country/morocco",
                "api": "https://api.worldbank.org/v2",
                "telecharge_le": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "periode": f"{DATE_DEBUT}-{DATE_FIN}",
                "lignes": int(len(dataset)),
                "colonnes": int(dataset.shape[1]),
                "indicateurs": metadonnees,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nDataset assemblé : {chemin_csv.relative_to(RACINE)}")
    print(f"  {dataset.shape[0]} lignes x {dataset.shape[1]} colonnes")
    print(f"  annee {dataset['annee'].min()} -> {dataset['annee'].max()}")
    print("\nApercu des 5 dernieres annees :")
    print(dataset.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()