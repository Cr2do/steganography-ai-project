import os
import cv2
from stego_dct import DCTSteganography
from stego_dwt_svd import DWTSVDSteganography
from attacks import attack_jpeg_compression, attack_resize, attack_crop, attack_noise

def test_algo(algo, algo_name, input_image, secret_text):
    print(f"\n=== Testing {algo_name} ===")
    output_path = f"output/{algo_name}_stego.png" 
    
    # 1. Embed
    print(f"Embedding text...")
    algo.embed(input_image, secret_text, output_path)
    
    # 2. Extract (No Attack)
    print("Extracting (No Attack)...")
    recovered = algo.extract(output_path)
    print(f"Recovered: {recovered[:50]}..." if len(recovered) > 50 else f"Recovered: {recovered}")
    
    # 3. Attack: JPEG Compression
    attacked_path = f"output/{algo_name}_jpeg.jpg"
    print("Applying JPEG Attack (Quality 80)...")
    attack_jpeg_compression(output_path, attacked_path, quality=80)
    recovered = algo.extract(attacked_path)
    print(f"Recovered after JPEG: {recovered[:50]}..." if len(recovered) > 50 else f"Recovered after JPEG: {recovered}")

    # 4. Attack: Resize (Scale 0.5 and back)
    attacked_path = f"output/{algo_name}_resize.png"
    print("Applying Resize Attack (0.5x)...")
    attack_resize(output_path, attacked_path, scale=0.5)
    
    img_attacked = cv2.imread(attacked_path)
    if img_attacked is not None:
        img_orig = cv2.imread(output_path)
        h, w = img_orig.shape[:2]
        img_restored = cv2.resize(img_attacked, (w, h))
        cv2.imwrite(f"output/{algo_name}_resize_restored.png", img_restored)
        
        recovered = algo.extract(f"output/{algo_name}_resize_restored.png")
        print(f"Recovered after Resize+Restore: {recovered[:50]}..." if len(recovered) > 50 else f"Recovered after Resize+Restore: {recovered}")

    # 5. Attack: Crop
    attacked_path = f"output/{algo_name}_crop.png"
    print("Applying Crop Attack (Center)...")
    attack_crop(output_path, attacked_path, crop_percent=0.1)
    recovered = algo.extract(attacked_path)
    print(f"Recovered after Crop: {recovered[:50]}..." if len(recovered) > 50 else f"Recovered after Crop: {recovered}")

def main():
    if not os.path.exists("output"):
        os.makedirs("output")

    input_image = "assets/input.jpg" 
    if not os.path.exists(input_image):
        if os.path.exists("../assets"):
             files = [f for f in os.listdir("../assets") if f.endswith(".jpg") or f.endswith(".png")]
             if files:
                 input_image = os.path.join("../assets", files[0])
             else:
                 print("No input image found.")
                 return
        else:
             print("No input image found.")
             return

    print(f"Using input image: {input_image}")
    secret_text = "Confidential Data 123"
    
    # Test DCT
    test_algo(DCTSteganography(), "dct", input_image, secret_text)
    
    # Test DWT-SVD
    test_algo(DWTSVDSteganography(), "dwt_svd", input_image, secret_text)

if __name__ == "__main__":
    main()
