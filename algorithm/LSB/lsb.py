import cv2
import numpy as np


class LSB:

    def __init__(self):
        # On utilise le caractère NULL standard, comme pour le DCT
        self.delimiter = '\0'

    def to_bin(self, data):
        """
        Convertit data en binaire :
        - Si c'est un STRING (le message) -> convertit chaque lettre en binaire
        - Si c'est un INT (un pixel) -> convertit le chiffre directement
        """
        if isinstance(data, str):
            return ''.join(format(ord(i), '08b') for i in data)
        elif isinstance(data, (int, np.integer)):
            return format(data, '08b')
        else:
            raise TypeError("Type non supporté pour la conversion binaire")

    def sign(self, image_path, secret_message, output_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Impossible de lire l'image à : {image_path}")

        # 1. On ajoute le délimiteur au message TEXTE d'abord
        full_message = secret_message + self.delimiter

        # 2. On convertit le tout en binaire
        binary_message = self.to_bin(full_message)

        data_index = 0
        binary_len = len(binary_message)
        rows, cols, _ = img.shape

        # 3. On parcourt les pixels
        for i in range(rows):
            for j in range(cols):
                pixel = img[i, j]

                # Récupération du binaire du canal Bleu
                b = self.to_bin(pixel[0])

                if data_index < binary_len:
                    # On remplace le dernier bit
                    # On prend tout sauf le dernier bit (b[:-1]) et on ajoute le bit du message
                    pixel[0] = int(b[:-1] + binary_message[data_index], 2)
                    data_index += 1
                else:
                    # FINI ! On sauvegarde et on arrête la boucle immédiatement
                    cv2.imwrite(output_path, img)
                    print(f"[LSB] Image signée sauvegardée avec succès : {output_path}")
                    return

        # Gestion d'erreur si image trop petite
        cv2.imwrite(output_path, img)
        print("[LSB] Attention : Image trop petite, message tronqué.")

    def read(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Impossible de lire l'image.")

        binary_byte = ""  # Tampon pour stocker les 8 bits en cours
        decoded_text = "" # Message final

        for row in img:
            for pixel in row:
                # On récupère le binaire du canal bleu
                b_bin = self.to_bin(pixel[0])

                # On récupère le dernier bit
                binary_byte += b_bin[-1]

                # Si on a 8 bits, on tente de faire un caractère
                if len(binary_byte) == 8:
                    char_code = int(binary_byte, 2)
                    character = chr(char_code)

                    # EST-CE LE DÉLIMITEUR ?
                    if character == self.delimiter:
                        return decoded_text # OUI -> On s'arrête net !

                    # NON -> On ajoute au message et on vide le tampon
                    decoded_text += character
                    binary_byte = ""

        return decoded_text # Retourne ce qu'on a trouvé si pas de délimiteur (ex: message cassé)