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