import cv2
import numpy as np


class DCT:

    def __init__(self):
        self.Q = 30
        self.Delimiter = '\0'

    def sign(self, image_path, secret_message, output_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape


        img = np.float32(img)

        full_message = secret_message + self.Delimiter

        # Conversion message en binaire
        msg_bin = ''.join(format(ord(i), '08b') for i in full_message)
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

                val  = round(coeff / self.Q)

                if val % 2 != bit:
                    val -= 1

                new_coef = val * self.Q

                dct_block[4, 4] = new_coef

                # Inverse DCT
                img[i:i+8, j:j+8] = cv2.idct(dct_block)
                msg_idx += 1

        # Sauvegarde (Attention: le format image doit supporter les floats ou on perd de l'info en convertissant en int)
        # Pour le test, on sauvegarde en PNG pour ne pas compresser deux fois

        img_final = np.clip(img, 0, 255)
        img_final = np.uint8(img_final)

        cv2.imwrite(output_path, img_final)
        print(f"[DCT] Image signée sauvegardée : {output_path}")

    def read(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        img = np.float32(img)

        msg_bin = ""
        decoded_text = ""

        # On enlève la limite arbitraire de 10 caractères
        # On lit tant qu'on a des blocs dans l'image
        for i in range(0, h, 8):
            for j in range(0, w, 8):
                block = img[i:i+8, j:j+8]
                dct_block = cv2.dct(block)

                # --- EXTRACTION ---
                coeff = dct_block[4, 4]
                val = round(coeff / self.Q)

                # On ajoute le bit trouvé
                msg_bin += str(int(val % 2))

                # --- VÉRIFICATION DU DÉLIMITEUR (Nouveau) ---
                # Dès qu'on a 8 nouveaux bits (un octet complet)
                if len(msg_bin) >= 8:
                    # On convertit ces 8 bits en caractère
                    byte = msg_bin[:8]
                    char_code = int(byte, 2)

                    found_char = chr(char_code)
                    # SI LE CARACTÈRE EST LE DÉLIMITEUR (0), ON STOPPE TOUT
                    if found_char == self.Delimiter:
                        return decoded_text

                    # Sinon, on ajoute la lettre au texte final
                    decoded_text += found_char

                    # On vide le tampon binaire pour recommencer les 8 prochains
                    msg_bin = ""

        return decoded_text.rstrip('\x00')
