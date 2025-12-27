import cv2
import numpy as np


class LSB:

    _final_delimiter = '1111111111111110'

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

        binary_message = self.to_bin(secret_message) + self._final_delimiter

        data_index = 0
        binary_len = len(binary_message)

        rows, cols, _ = img.shape

        # On parcourt les pixels
        for i in range(rows):
            for j in range(cols):
                pixel = img[i, j]

                # Récupération des valeurs RGB en binaire
                # Note: OpenCV est en BGR (Blue, Green, Red)
                r = self.to_bin(pixel[2])
                g = self.to_bin(pixel[1])
                b = self.to_bin(pixel[0])

                # On modifie le canal Bleu (index 0)
                if data_index < binary_len:
                    # On remplace le dernier bit du bleu
                    # int(..., 2) convertit du binaire vers un entier base 10
                    pixel[0] = int(b[:-1] + binary_message[data_index], 2)
                    data_index += 1
                else:
                    # Si le message est fini, on sauvegarde et on quitte
                    cv2.imwrite(output_path, img)
                    print(f"[LSB] Image signée sauvegardée : {output_path}")
                    return

        # Si on arrive ici, c'est que l'image est trop petite pour le message
        cv2.imwrite(output_path, img)
        print("[LSB] Attention : Image potentiellement trop petite, message tronqué ?")

    def read(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Impossible de lire l'image.")

        binary_data = ""

        for row in img:
            for pixel in row:
                # On récupère juste le binaire du canal bleu (pixel[0])
                b_bin = self.to_bin(pixel[0])
                binary_data += b_bin[-1] # On garde le dernier bit

        # Découpage en octets (8 bits)
        all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]

        decoded_data = ""
        for byte in all_bytes:
            # On arrête de décoder si on n'a pas 8 bits complets (fin du fichier)
            if len(byte) < 8: break

            char_code = int(byte, 2)
            decoded_data += chr(char_code)

            # Vérification du délimiteur 'ÿþ' (correspondant à 1111111111111110)
            if decoded_data.endswith("ÿþ"):
                # On retourne tout SAUF les 2 derniers caractères (le délimiteur)
                return decoded_data[:-2]

        return decoded_data # Retourne tout si pas de délimiteur trouvé