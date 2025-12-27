import cv2
import numpy as np


class DCT:
    def sign(self, image_path, secret_message, output_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) # On travaille en gris pour simplifier le PoC
        h, w = img.shape
        img = np.float32(img)

        # Conversion message en binaire
        msg_bin = ''.join(format(ord(i), '08b') for i in secret_message)
        msg_idx = 0

        # Découpage en blocs 8x8
        for i in range(0, h, 8):
            for j in range(0, w, 8):
                if msg_idx >= len(msg_bin): break

                # Récupération du bloc
                block = img[i:i+8, j:j+8]

                # Application de la DCT
                dct_block = cv2.dct(block)

                # Insertion dans un coefficient moyen (ex: position 4,4)
                # Si bit=1, on rend le coeff pair, sinon impair (méthode simplifiée)
                coeff = dct_block[4, 4]
                bit = int(msg_bin[msg_idx])

                if bit == 0:
                    dct_block[4, 4] = coeff - (coeff % 2)
                else:
                    dct_block[4, 4] = coeff - (coeff % 2) + 1

                # Inverse DCT
                img[i:i+8, j:j+8] = cv2.idct(dct_block)
                msg_idx += 1

        # Sauvegarde (Attention: le format image doit supporter les floats ou on perd de l'info en convertissant en int)
        # Pour le test, on sauvegarde en PNG pour ne pas compresser deux fois
        cv2.imwrite(output_path, img)
        print(f"[DCT] Image signée sauvegardée : {output_path}")

    def read(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        img = np.float32(img)

        msg_bin = ""

        for i in range(0, h, 8):
            for j in range(0, w, 8):
                block = img[i:i+8, j:j+8]
                dct_block = cv2.dct(block)

                # Lecture du coefficient 4,4
                coeff = dct_block[4, 4]

                # On arrondit pour récupérer la parité
                val = round(coeff)
                msg_bin += str(val % 2)

        # Conversion binaire -> texte (limitée aux 5 premiers caractères pour le test)
        chars = []
        for k in range(0, 40, 8): # On lit juste 5 lettres
            byte = msg_bin[k:k+8]
            chars.append(chr(int(byte, 2)))
        return "".join(chars)
