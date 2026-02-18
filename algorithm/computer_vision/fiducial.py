import cv2
import numpy as np

class FiducialMarker:
    """
    Generates and detects 4 distinct invisible fiducial markers for geometric synchronization.
    Uses ORB feature matching to find markers and rectify the image.
    """
    def __init__(self, size=64):
        self.size = size
        self.markers = []
        self.kps = []
        self.descs = []
        
        # Create 4 distinct noise patterns (TL, TR, BL, BR)
        # Using fixed seed for reproducibility
        np.random.seed(42)
        for i in range(4):
            marker = np.random.randint(0, 256, (size, size), dtype=np.uint8)
            self.markers.append(marker)

            orb = cv2.ORB_create(nfeatures=500)
            kp, des = orb.detectAndCompute(marker, None)
            self.kps.append(kp)
            self.descs.append(des)
        
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def add_markers(self, image):
        """Adds 4 distinct invisible markers to the 4 corners of the image."""
        h, w = image.shape[:2]
        img_float = image.astype(np.float32)
        
        margin = 20
        # Positions: TL, TR, BL, BR
        positions = [
            (margin, margin),
            (margin, w - self.size - margin),
            (h - self.size - margin, margin),
            (h - self.size - margin, w - self.size - margin)
        ]
        
        alpha = 0.15 # Increased visibility slightly for robustness (15%)
        
        for i, (y, x) in enumerate(positions):
            roi = img_float[y:y+self.size, x:x+self.size]
            marker = self.markers[i]

            if len(roi.shape) == 3:
                marker_3ch = cv2.merge([marker, marker, marker])
                blended = cv2.addWeighted(roi, 1.0, marker_3ch.astype(np.float32), alpha, 0)
                img_float[y:y+self.size, x:x+self.size] = blended
            else:
                blended = cv2.addWeighted(roi, 1.0, marker.astype(np.float32), alpha, 0)
                img_float[y:y+self.size, x:x+self.size] = blended
                
        return np.clip(img_float, 0, 255).astype(np.uint8)

    def detect_and_rectify(self, image):
        """
        Detects markers, computes homography, and unwarps the image.
        Returns the rectified image or None if failed.
        """
        orb = cv2.ORB_create(nfeatures=2000)
        kp_img, des_img = orb.detectAndCompute(image, None)
        
        if des_img is None or len(kp_img) < 4:
            return None
            
        src_pts = [] # Points found in the distorted image
        dst_pts = [] # Canonical points (where they should be)
        
        h, w = image.shape[:2]
        # We assume target canonical size is roughly the current size
        # Or we could fix it to 512x512 if we knew the original aspect ratio.
        canonical_h, canonical_w = h, w

        margin = 20
        # Canonical centers of the 4 markers
        canonical_centers = [
            (margin + self.size/2, margin + self.size/2), # TL
            (margin + self.size/2, canonical_w - self.size/2 - margin), # TR
            (canonical_h - self.size/2 - margin, margin + self.size/2), # BL
            (canonical_h - self.size/2 - margin, canonical_w - self.size/2 - margin) # BR
        ]

        found_count = 0

        for i in range(4):
            if self.descs[i] is None: continue

            matches = self.bf.match(self.descs[i], des_img)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Keep top matches
            good_matches = matches[:20]
            if len(good_matches) < 4: continue

            # Extract points in the image
            pts = np.float32([kp_img[m.trainIdx].pt for m in good_matches])

            # Calculate centroid of this marker cluster
            centroid = np.mean(pts, axis=0)

            # Add correspondence: Distorted Point -> Canonical Point
            src_pts.append(centroid)
            # Note: canonical_centers is (y, x), but points are (x, y)
            cy, cx = canonical_centers[i]
            dst_pts.append([cx, cy])
            found_count += 1

        if found_count < 4:
            print(f"Only found {found_count} markers. Cannot rectify.")
            return None
        
        print("Found 4 markers. Rectifying...")
        src = np.float32(src_pts)
        dst = np.float32(dst_pts)
        
        # Calculate Homography: src (distorted) -> dst (canonical)
        H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
        
        if H is not None:
            rectified = cv2.warpPerspective(image, H, (canonical_w, canonical_h))
            return rectified

        return None
