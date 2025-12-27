from skimage.metrics import structural_similarity as ssim
import cv2


def attack_transform_img_to_jpeg(input_path, output_path, quality=50):
    """Simule une compression JPEG (comme Instagram/WhatsApp)"""
    img = cv2.imread(input_path)
    # quality: 0 à 100. 50 est une compression forte.
    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    print(f"ATTACK : Compression JPEG (Qualité {quality}) appliquée.")

def metrics(original_path, stego_path):
    """Calcule si l'image est moche (PSNR/SSIM)"""
    img1 = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(stego_path, cv2.IMREAD_GRAYSCALE)

    # PSNR
    psnr = cv2.PSNR(img1, img2)

    # SSIM
    score, diff = ssim(img1, img2, full=True)

    return psnr, score



def calcul_capacity_max(image_path, bits_par_bloc=1, taille_bloc=8):
    """
    Calcule combien de caractères peuvent être cachés dans une image selon la méthode par blocs.

    :param image_path: Chemin de l'image
    :param bits_par_bloc: Nombre de bits cachés par bloc (ex: 1 pour ta DCT actuelle)
    :param taille_bloc: Dimension du carré (ex: 8 pour 8x8 pixels)
    :return: Le nombre entier de caractères maximum
    """
    # 1. Chargement de l'image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erreur : Impossible d'ouvrir l'image {image_path}")
        return 0

    # On récupère Hauteur et Largeur
    # shape retourne (hauteur, largeur, canaux)
    height, width = img.shape[:2]

    # 2. Calcul du nombre de blocs complets
    # On utilise // pour la division entière (on ignore les bords incomplets)
    blocs_en_hauteur = height // taille_bloc
    blocs_en_largeur = width // taille_bloc

    nombre_total_blocs = blocs_en_hauteur * blocs_en_largeur

    # 3. Calcul de la capacité
    capacite_bits = nombre_total_blocs * bits_par_bloc

    # 4. Conversion en caractères (1 caractère = 8 bits)
    capacite_caracteres = capacite_bits // 8

    # --- Affichage des détails (Optionnel, pour le debug) ---
    print(f"--- Calcul de capacité pour : {image_path} ---")
    print(f" * Dimensions image   : {width} x {height} px")
    print(f" * Grille de blocs    : {blocs_en_largeur} x {blocs_en_hauteur} = {nombre_total_blocs} blocs")
    print(f" * Capacité binaire   : {capacite_bits} bits")
    print(f" * Capacité texte     : {capacite_caracteres} caractères")
    print("-------------------------------------------------")

    return capacite_caracteres