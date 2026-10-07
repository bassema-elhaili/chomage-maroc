"""
compresser_support.py
====================
Reduit la taille de support-de-cours.pdf sans degrader le texte.

Pourquoi le fichier est deja gros
---------------------------------
Les 27 visuels des diapositives representent 1 673 Ko sur 2 440 Ko, soit
69 % du fichier. Mais PowerPoint les a deja compressees en FlateDecode, qui
est efficace sur des visuels de type capture d'ecran. Les reconvertir telles
quelles en JPEG n'apporte donc presque rien : le script mesure plusieurs
strategies et ne conserve que la meilleure, image par image.

Strategies comparees (liquidation : largeur en pixels, qualite JPEG) :
    1024 px / q55   - equilibre, ~44 % de gain
    1024 px / q70   - plus doux
    pleine taille / q50 et q65

Regle appliquee : une image n'est jamais remplacee par une version plus
lourde que l'original. Le texte reste en vectoriel, la selection et la
recherche plein texte sont intactes.

Usage : python compresser_support.py
"""

import io
from pathlib import Path

import pikepdf
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "support-de-cours.pdf"
SORTIE = RACINE / "support-de-cours-compresse.pdf"

SEUIL_PIXELS = 50_000                  # en dessous : logo, on ignore
STRATEGIES = [(1024, 55), (1024, 70), (None, 50), (None, 65)]


def encoder(donnees: Image.Image, largeur: int | None, qualite: int) -> bytes:
    """Encode une image PIL en JPEG, avec reduction eventuelle."""
    if largeur and donnees.width > largeur:
        ratio = largeur / donnees.width
        donnees = donnees.resize(
            (largeur, max(1, int(donnees.height * ratio))), Image.LANCZOS
        )
    tampon = io.BytesIO()
    donnees.save(tampon, format="JPEG", quality=qualite, optimize=True)
    return tampon.getvalue()


def reduire_images(pdf: pikepdf.Pdf) -> tuple[int, int]:
    nb = 0
    gagne = 0

    for page in pdf.pages:
        for _nom, obj in page.get_images().items():
            try:
                image = pikepdf.PdfImage(obj)
                avant = len(obj.read_raw_bytes())
            except Exception:
                continue

            if image.width * image.height < SEUIL_PIXELS:
                continue

            try:
                donnees = image.as_pil_image()
            except Exception:
                continue
            if donnees.mode not in ("RGB", "L"):
                donnees = donnees.convert("RGB")

            # on teste toutes les strategies et on garde la plus petite
            meilleure = avant
            for largeur, qualite in STRATEGIES:
                taille = len(encoder(donnees, largeur, qualite))
                meilleure = min(meilleure, taille)

            if meilleure >= avant:
                continue  # aucune strategie ne gagne : on ne touche a rien

            # on reencodage avec la strategie gagnante
            taille_cible, (gagnante_l, gagnante_q) = min(
                (
                    (len(encoder(donnees, l, q)), (l, q))
                    for l, q in STRATEGIES
                ),
                key=lambda t: t[0],
            )

            xobject = obj
            try:
                xobject.write(
                    encoder(donnees, gagnante_l, gagnante_q),
                    filter=pikepdf.Name.DCTDecode,
                )
                xobject["/Width"] = image.width
                xobject["/Height"] = image.height
                xobject["/BitsPerComponent"] = 8
                xobject["/ColorSpace"] = pikepdf.Name.DeviceRGB
                xobject["/Interpolate"] = True
                if "/DecodeParms" in xobject:
                    del xobject["/DecodeParms"]
            except Exception:
                continue

            nb += 1
            gagne += avant - taille_cible

    return nb, gagne


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Fichier introuvable : {SOURCE}")

    avant_ko = SOURCE.stat().st_size / 1024

    pdf = pikepdf.open(SOURCE)
    nb, gagne_octets = reduire_images(pdf)

    pdf.save(
        SORTIE,
        compress_streams=True,
        object_stream_mode=pikepdf.ObjectStreamMode.generate,
        linearize=True,
    )
    pdf.close()

    apres_ko = SORTIE.stat().st_size / 1024

    print(f"Source        : {SOURCE.name}  ({avant_ko:.0f} Ko)")
    print(f"Images reenc. : {nb}")
    print(f"  gain images : {gagne_octets / 1024:.0f} Ko")
    print(f"Resultat      : {SORTIE.name}  ({apres_ko:.0f} Ko)")
    print(f"  gain total  : {(1 - apres_ko / avant_ko) * 100:.1f} %")
    print("\nTexte conserve en vectoriel : selection et recherche intactes.")


if __name__ == "__main__":
    main()