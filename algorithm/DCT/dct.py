import cv2
import numpy as np


class DCT:

    def __init__(self):
        self.Q = 30
        self.Delimiter = '\0'

    def sign(self, image_path, secret_message, output_path):
        # 1. LIRE EN COULEUR (Plus de GRAYSCALE ici)
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            print("Erreur lecture image")
            return

        h, w, _ = img.shape

        # 2. CONVERSION BGR -> YCrCb
        # OpenCV utilise BGR par défaut, on convertit en YCrCb
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

        # 3. SÉPARATION DES CANAUX
        # y = Luminance (Noir et blanc), cr/cb = Couleurs
        y, cr, cb = cv2.split(ycrcb)

        # On va travailler UNIQUEMENT sur le canal Y
        y_float = np.float32(y)

        full_message = secret_message + self.Delimiter
        msg_bin = ''.join(format(ord(i), '08b') for i in full_message)
        msg_idx = 0
        len_msg = len(msg_bin)

        # 4. BOUCLE DCT (Idem avant, mais sur y_float)
        for i in range(0, h, 8):
            for j in range(0, w, 8):
                if msg_idx >= len_msg: break

                block = y_float[i:i+8, j:j+8]
                dct_block = cv2.dct(block)

                coeff = dct_block[4, 4]
                bit = int(msg_bin[msg_idx])

                val = round(coeff / self.Q)
                if val % 2 != bit:
                    val -= 1

                new_coef = val * self.Q
                dct_block[4, 4] = new_coef

                y_float[i:i+8, j:j+8] = cv2.idct(dct_block)
                msg_idx += 1

        # 5. RECONSTITUTION
        # On remet le canal Y au format correct (0-255)
        y_final = np.clip(y_float, 0, 255)
        y_final = np.uint8(y_final)

        # On fusionne Y (modifié) avec Cr et Cb (originaux)
        merged_ycrcb = cv2.merge([y_final, cr, cb])

        # On reconvertit en BGR pour la sauvegarde
        final_img = cv2.cvtColor(merged_ycrcb, cv2.COLOR_YCrCb2BGR)

        cv2.imwrite(output_path, final_img)
        print(f"[DCT] Image signée COULEUR sauvegardée : {output_path}")

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
