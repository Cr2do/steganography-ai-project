import os
import cv2
from ..signal_processing.stego_dct import DCTSteganography

# Import Computer Vision module
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .fiducial import FiducialMarker

def attack_convert_format(image_path, output_path):
    img = cv2.imread(image_path)
    if img is None: return False
    if output_path.lower().endswith(('.jpg', '.jpeg')):
        cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    else:
        cv2.imwrite(output_path, img)
    return True

def attack_rotate(image_path, output_path, angle=15):
    """Simulates a rotation attack."""
    img = cv2.imread(image_path)
    if img is None: return False
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h))
    cv2.imwrite(output_path, rotated)
    return True

def test_algo_cv(algo, algo_name, input_image, secret_text):
    print(f"\n=== Testing {algo_name} with Computer Vision ===")
    
    # 1. Prepare Image with Markers
    print("Adding invisible markers...")
    img = cv2.imread(input_image)
    fiducial = FiducialMarker()
    img_marked = fiducial.add_markers(img)
    marked_path = f"output/{algo_name}_marked.png"
    cv2.imwrite(marked_path, img_marked)
    
    # 2. Embed Text into Marked Image
    output_path = f"output/{algo_name}_stego_cv.png"
    print(f"Embedding text into {output_path}...")
    algo.embed(marked_path, secret_text, output_path)
    
    # 3. Attack: Rotation (15 degrees)
    attacked_path = f"output/{algo_name}_rotated.png"
    print("Applying Rotation Attack (15 degrees)...")
    attack_rotate(output_path, attacked_path, angle=15)
    
    # 4. Rectify Image using Computer Vision
    print("Rectifying image...")
    img_attacked = cv2.imread(attacked_path)
    img_rectified = fiducial.detect_and_rectify(img_attacked)
    
    if img_rectified is not None:
        rectified_path = f"output/{algo_name}_rectified.png"
        cv2.imwrite(rectified_path, img_rectified)
        print("Image rectified successfully.")
        
        # 5. Extract from Rectified Image
        recovered = algo.extract(rectified_path)
        print(f"Recovered after Rotation+Rectification: {recovered}")
    else:
        print("Failed to rectify image (markers not found).")

def main():
    if not os.path.exists("output"):
        os.makedirs("output")

    input_image = "../assets/christmas.jpg"
    if not os.path.exists(input_image):
        print("Input image not found.")
        return

    print(f"Using input image: {input_image}")
    secret_text = "12345678"
    
    # Test DCT with Computer Vision
    test_algo_cv(DCTSteganography(), "dct", input_image, secret_text)

if __name__ == "__main__":
    main()
