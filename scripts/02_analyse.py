"""
02_analyse.py
=============
Question 3 : "Pourquoi le taux de chomage augmente sans cesse au Maroc ?"

Lit les deux jeux de donnees, calcule quelques statistiques et genere
les quatre figures du rapport.

Sources des donnees
  JOB-01 : Banque Mondiale / OIT  (estimation modelisee)  -> longue serie 1991-2025
  JOB-02 : HCP, Enquete Nationale sur l'Emploi (officiel)  -> donnees recentes 2023-2025

Usage : python 02_analyse.py
"""

import matplotlib

matplotlib.use("Agg")  # rendu sans fenetre (compatible VS Code / CI)

import matplotlib.pyplot as plt
import pandas as pd

RACINE = __import__("pathlib").Path(__file__).resolve().parent.parent
DOSSIER_DATA = RACINE / "data"
DOSSIER_GRAPHIQUES = RACINE / "graphs"

# --- charte graphique ------------------------------------------------------
BLEU = "#1f4e79"
ROUGE = "#c0392b"
VERT = "#1e8449"
ORANGE = "#d68910"
GRIS = "#7f8c8d"
BLEU_CLAIR = "#5dade2"

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "font.size": 10,
        "font.family": "DejaVu Sans",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


# ==========================================================================
# Chargement
# ==========================================================================
def charger():
    """Charge et prepare les deux jeux de donnees."""
    chemin_oms = DOSSIER_DATA / "JOB-01_chomage_maroc.csv"
    chemin_hcp = DOSSIER_DATA / "JOB-02_chomage_hcp.csv"

    # Le fichier Banque Mondiale est produit par 01_telecharger.py :
    # on donne la bonne commande plutot qu'une erreur technique incompréhensible.
    if not chemin_oms.exists():
        raise SystemExit(
            f"Fichier de donnees introuvable :\n  {chemin_oms}\n\n"
            "Il doit etre genere au prealable par :\n"
            "  python scripts/01_telecharger.py"
        )
    if not chemin_hcp.exists():
        raise SystemExit(
            f"Fichier de donnees introuvable :\n  {chemin_hcp}\n\n"
            "Ce fichier est livre avec le projet et ne doit pas etre supprime."
        )

    oms = pd.read_csv(chemin_oms).sort_values("annee")
    hcp_brut = pd.read_csv(chemin_hcp)
    # pivot : annee x indicateur
    hcp = hcp_brut.pivot(index="annee", columns="indicateur", values="valeur").sort_index()

    return oms, hcp


# ==========================================================================
# Figure 1 - Le paradoxe central
# ==========================================================================
def figure1_paradoxe(oms: pd.DataFrame) -> None:
    """Le chomage total BAISSE, celui des jeunes MONTE. C'est le coeur du rapport."""
    d = oms.dropna(subset=["chomage_total", "chomage_jeunes"])

    fig, ax = plt.subplots(figsize=(11, 5.5))

    ax.plot(d["annee"], d["chomage_jeunes"],
            color=ROUGE, linewidth=2.6, marker="o", markersize=4.5,
            label="Chomage des 15-24 ans")
    ax.plot(d["annee"], d["chomage_total"],
            color=BLEU, linewidth=2.6, marker="o", markersize=4.5,
            label="Chomage total (15 ans et +)")

    # remplissage de l'ecart : la "prime de chomage des jeunes"
    ax.fill_between(d["annee"], d["chomage_total"], d["chomage_jeunes"],
                    color=ROUGE, alpha=0.12)

    # reperes
    for annee, texte, couleur, dy in [
        (1995, "Pique du chomage total\n14,05 %", BLEU, -1.9),
        (2004, "Creux du chomage\ndes jeunes : 15,44 %", VERT, 1.1),
        (2020, "Covid-19", GRIS, -2.4),
    ]:
        if annee in set(d["annee"]):
            valeur = float(d.loc[d["annee"] == annee, "chomage_total"].iloc[0]) \
                if texte.startswith("Pique") else \
                float(d.loc[d["annee"] == annee, "chomage_jeunes"].iloc[0])
            ax.annotate(texte, xy=(annee, valeur), xytext=(annee - 3.4, valeur + dy),
                        fontsize=8.5, color=couleur, weight="bold",
                        arrowprops=dict(arrowstyle="->", color=couleur, lw=1.1))

    ax.annotate("", xy=(2025, 21.88), xytext=(2025, 9.00),
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=2))
    ax.text(2025.15, 15.5, "Ecart\n+ 12,9 pts", color=ORANGE,
            fontsize=9, weight="bold", va="center")

    ax.set_title("Figure 1 - Le chomage total baisse, celui des jeunes augmente\n"
                 "Maroc, 1991-2025 (source : Banque Mondiale / OIT)",
                 fontsize=12, weight="bold", pad=14)
    ax.set_xlabel("Annee")
    ax.set_ylabel("Taux de chomage (% de la population active)")
    ax.set_xlim(1990, 2028)
    ax.legend(loc="lower left", frameon=False, fontsize=9.5)
    ax.text(0.995, 0.03, "Surface = amplitude de la prime de chomage des jeunes",
            transform=ax.transAxes, ha="right", fontsize=8, color=GRIS, style="italic")

    fig.savefig(DOSSIER_GRAPHIQUES / "fig1_paradoxe_chomage.png")
    plt.close(fig)
    print("  [ok] fig1_paradoxe_chomage.png")


# ==========================================================================
# Figure 2 - Le mecanisme : la sortie du marche du travail
# ==========================================================================
def figure2_activite(oms: pd.DataFrame) -> None:
    """La cause reelle : les gens sortent du marche du travail, ils ne sont plus comptes."""
    d = oms.dropna(subset=["taux_activite"]).sort_values("annee")

    fig, ax = plt.subplots(figsize=(11, 5.5))

    ax.fill_between(d["annee"], 0, d["taux_activite"], color=BLEU_CLAIR, alpha=0.35)
    ax.plot(d["annee"], d["taux_activite"], color=BLEU, linewidth=2.6,
            marker="o", markersize=4, label="Taux d'activite (% de la population 15+)")

    if "ratio_emploi" in d.columns:
        ax.plot(d["annee"], d["ratio_emploi"], color=VERT, linewidth=2.4,
                marker="s", markersize=3.5, label="Taux d'emploi (% de la population 15+)")

    if "taux_activite_f" in d.columns:
        ax.plot(d["annee"], d["taux_activite_f"], color=ORANGE, linewidth=2.4,
                marker="^", markersize=3.5, label="Taux d'activite des femmes")

    premier = d.iloc[0]
    dernier = d.iloc[-1]
    ax.annotate(f"{premier['taux_activite']:.1f} %",
                xy=(premier["annee"], premier["taux_activite"]),
                xytext=(premier["annee"] + 0.4, premier["taux_activite"] + 1.6),
                fontsize=9, weight="bold", color=BLEU)
    ax.annotate(f"{dernier['taux_activite']:.1f} %",
                xy=(dernier["annee"], dernier["taux_activite"]),
                xytext=(dernier["annee"] - 0.5, dernier["taux_activite"] - 2.8),
                fontsize=9, weight="bold", color=BLEU)

    perte = dernier["taux_activite"] - premier["taux_activite"]
    ax.annotate(f"{perte:.1f} points perdus\nsur 34 ans",
                xy=(1996.5, 33.5), fontsize=12, weight="bold", color=ROUGE,
                bbox=dict(boxstyle="round,pad=0.55", fc="white", ec=ROUGE, lw=1.5))

    ax.set_title("Figure 2 - L'effondrement du taux d'activite\n"
                 "Maroc, 1990-2025 (source : Banque Mondiale / OIT)",
                 fontsize=12, weight="bold", pad=14)
    ax.set_xlabel("Annee")
    ax.set_ylabel("Taux (% de la population agee de 15 ans et plus)")
    ax.set_ylim(0, 62)
    ax.set_xlim(1989, 2026.5)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    ax.text(0.005, 0.955,
            "Moins d'actifs = moins de chomeurs comptes.\n"
            "L'explication du taux qui baisse.",
            transform=ax.transAxes, va="top", fontsize=9, color=ROUGE, weight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc="#fdf2f2", ec=ROUGE, lw=1))

    fig.savefig(DOSSIER_GRAPHIQUES / "fig2_taux_activite.png")
    plt.close(fig)
    print("  [ok] fig2_taux_activite.png")


# ==========================================================================
# Figure 3 - Aucune categorie ne baisse : le chomage se concentre
# ==========================================================================
def figure3_categories(hcp: pd.DataFrame) -> None:
    """Officiel HCP : ce qui monte et ce qui baisse entre 2024 et 2025."""
    paires = [
        ("chomage_jeunes_15_24", "Jeunes 15-24 ans"),
        ("chomage_femmes", "Femmes"),
        ("chomage_diplomes", "Diplomes"),
        ("chomage_25_34", "25-34 ans"),
        ("chomage_35_44", "35-44 ans"),
        ("chomage_hommes", "Hommes"),
        ("chomage_45_plus", "45 ans et +"),
        ("chomage_total", "TOTAL"),
    ]

    libelles, variations = [], []
    for cle, libelle in paires:
        if cle in hcp.columns and 2024 in hcp.index and 2025 in hcp.index:
            v24, v25 = float(hcp.loc[2024, cle]), float(hcp.loc[2025, cle])
            libelles.append(libelle)
            variations.append(v25 - v24)

    couleurs = [ROUGE if v > 0 else VERT for v in variations]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    positions = range(len(libelles))
    barres = ax.barh(positions, variations, color=couleurs, height=0.62, edgecolor="white")

    for barre, variation in zip(barres, variations):
        suffixe = " pt" if abs(variation) >= 1 else " point"
        decalage = 0.045 if variation >= 0 else -0.045
        ax.text(variation + decalage, barre.get_y() + barre.get_height() / 2,
                f"{variation:+.1f}{suffixe}".replace(".", ","),
                va="center", ha="left" if variation >= 0 else "right",
                fontsize=9, weight="bold",
                color=ROUGE if variation > 0 else VERT)

    ax.axvline(0, color="#2c3e50", linewidth=1.3)
    ax.set_yticks(list(positions))
    ax.set_yticklabels(libelles)
    ax.invert_yaxis()
    ax.set_xlabel("Variation du taux de chomage entre 2024 et 2025 (en points)")
    ax.set_xlim(-1.3, 1.6)
    ax.set_title("Figure 3 - Le chomage ne baisse QUE pour les hommes et les seniors\n"
                 "HCP, Enquete Nationale sur l'Emploi, 2024 -> 2025",
                 fontsize=12, weight="bold", pad=14)
    ax.grid(axis="y", visible=False)
    ax.text(0.995, 0.03,
            "Rouge = hausse   |   Vert = baisse\nLe total baisse parce que les hommes representent\n"
            "la moitie de la population active",
            transform=ax.transAxes, ha="right", fontsize=8, color=GRIS, style="italic")

    fig.savefig(DOSSIER_GRAPHIQUES / "fig3_categories_hcp.png")
    plt.close(fig)
    print("  [ok] fig3_categories_hcp.png")


# ==========================================================================
# Figure 4 - La qualite de l'emploi se degrade
# ==========================================================================
def figure4_qualite(hcp: pd.DataFrame) -> None:
    """Meme quand le chomage baisse, la qualite de l'emploi se degrade."""
    series = [
        ("sous_emploi", "Taux de sous-emploi", ORANGE),
        ("chomage_plus_dun_an", "Chomeurs depuis plus d'un an", ROUGE),
        ("primo_demandeurs", "Primo-demandeurs d'emploi", "#8e44ad"),
        ("sous_emploi_revenu", "Sous-emploi lie au revenu", "#16a085"),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))

    for cle, libelle, couleur in series:
        if cle not in hcp.columns:
            continue
        d = hcp[cle].dropna().sort_index()
        if len(d) < 2:
            continue
        evolution = (d.iloc[-1] - d.iloc[0]) / d.iloc[0] * 100
        ax.plot(d.index, d.values, color=couleur, linewidth=2.6, marker="o",
                markersize=6, label=f"{libelle}  ({evolution:+.0f} %)")

    if "duree_moyenne_chomage" in hcp.columns:
        d = hcp["duree_moyenne_chomage"].dropna().sort_index()
        if len(d) >= 2:
            evolution = d.iloc[-1] - d.iloc[0]
            ax.plot(d.index, d.values, color=BLEU, linewidth=2.6, marker="s",
                    markersize=6, linestyle="--",
                    label=f"Duree moyenne du chomage  ({evolution:+.0f} mois)")

    ax.set_title("Figure 4 - La qualite de l'emploi se degrade\n"
                 "HCP, 2023-2025 - en %, sauf la duree moyenne en mois",
                 fontsize=12, weight="bold", pad=14)
    ax.set_xlabel("Annee")
    ax.set_ylabel("Taux (%) / duree (mois)")
    ax.set_xticks(sorted(set(hcp.index)))
    ax.set_xlim(2022.7, 2025.6)
    ax.set_ylim(0, 72)
    ax.legend(loc="center left", frameon=False, fontsize=9)
    ax.text(0.015, 0.30,
            "Le chomage baisse de 0,3 point en 2025,\n"
            "mais celui qui dure et la sous-emploi\n"
            "augmentent sur la meme periode.",
            transform=ax.transAxes, ha="left", va="top", fontsize=9,
            color=ROUGE, weight="bold",
            bbox=dict(boxstyle="round,pad=0.45", fc="#fdf2f2", ec=ROUGE, lw=1))

    fig.savefig(DOSSIER_GRAPHIQUES / "fig4_qualite_emploi.png")
    plt.close(fig)
    print("  [ok] fig4_qualite_emploi.png")


# ==========================================================================
# Statistiques affichees dans le rapport
# ==========================================================================
def statistiques(oms: pd.DataFrame, hcp: pd.DataFrame) -> None:
    print("\n" + "=" * 68)
    print("STATISTIQUES CLES POUR LE RAPPORT")
    print("=" * 68)

    d = oms.dropna(subset=["chomage_total"])
    dj = oms.dropna(subset=["chomage_jeunes"])

    def v(annee, col):
        return float(d.loc[d["annee"] == annee, col].iloc[0])

    print(f"\n[1] Le chomage total BAISSE")
    print(f"    1991 : {v(1991,'chomage_total'):.2f} %")
    print(f"    2025 : {v(2025,'chomage_total'):.2f} %")
    print(f"    ecart : {v(2025,'chomage_total') - v(1991,'chomage_total'):+.2f} points")

    print(f"\n[2] Le chomage des jeunes AUGMENTE depuis 2004")
    print(f"    2004 : {v(2004,'chomage_jeunes'):.2f} %")
    print(f"    2025 : {v(2025,'chomage_jeunes'):.2f} %")
    print(f"    ecart : {v(2025,'chomage_jeunes') - v(2004,'chomage_jeunes'):+.2f} points")

    print(f"\n[3] La prime de chomage des jeunes s'envole")
    print(f"    1991 : {v(1991,'chomage_jeunes')/v(1991,'chomage_total'):.2f} fois la moyenne")
    print(f"    2025 : {v(2025,'chomage_jeunes')/v(2025,'chomage_total'):.2f} fois la moyenne")
    print(f"    ecart 2025 : {v(2025,'chomage_jeunes') - v(2025,'chomage_total'):+.2f} points")

    print(f"\n[4] Le taux d'activite s'effondre")
    print(f"    1991 : {v(1991,'taux_activite'):.2f} %")
    print(f"    2025 : {v(2025,'taux_activite'):.2f} %")
    print(f"    ecart : {v(2025,'taux_activite') - v(1991,'taux_activite'):+.2f} points")

    print(f"\n[5] L'activite des femmes recule")
    print(f"    pic 2008 : {float(oms['taux_activite_f'].max()):.2f} %")
    print(f"    2025     : {v(2025,'taux_activite_f'):.2f} %")

    print(f"\n[6] Chiffres officiels HCP 2024 -> 2025")
    for cle, libelle in [
        ("chomage_total", "chomage total"),
        ("chomage_jeunes_15_24", "chomage 15-24 ans"),
        ("chomage_femmes", "chomage femmes"),
        ("chomage_hommes", "chomage hommes"),
        ("sous_emploi", "sous-emploi"),
        ("primo_demandeurs", "primo-demandeurs"),
        ("chomage_plus_dun_an", "chomage > 1 an"),
        ("duree_moyenne_chomage", "duree moyenne (mois)"),
        ("emplois_crees", "emplois crees"),
    ]:
        if cle in hcp.columns and 2024 in hcp.index and 2025 in hcp.index:
            a, b = float(hcp.loc[2024, cle]), float(hcp.loc[2025, cle])
            fleche = "HAUSSE" if b > a else ("baisse" if b < a else "stable")
            print(f"    {libelle:24s} {a:>10,.1f} -> {b:>10,.1f}   ({fleche})")

    print(f"\n[7] Correlation chomage total / taux d'activite")
    corr = oms[["chomage_total", "taux_activite"]].dropna().corr().iloc[0, 1]
    print(f"    r = {corr:+.3f}  (positive : les deux baissent ensemble)")
    print("=" * 68)


# ==========================================================================
def main() -> None:
    DOSSIER_GRAPHIQUES.mkdir(parents=True, exist_ok=True)
    oms, hcp = charger()

    print(f"Donnees chargees : OMS {oms.shape[0]} lignes | HCP {hcp.shape[0]} annees")
    print("\nGeneration des figures...")

    figure1_paradoxe(oms)
    figure2_activite(oms)
    figure3_categories(hcp)
    figure4_qualite(hcp)

    statistiques(oms, hcp)
    print(f"\n{len(list(DOSSIER_GRAPHIQUES.glob('*.png')))} figures dans graphs/")


if __name__ == "__main__":
    main()