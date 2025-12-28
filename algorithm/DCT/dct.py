import cv2
import numpy as np
from collections import Counter


class DCT:

    def __init__(self):
        # Q = 30 est bien pour JPEG 80. Pour JPEG 50, essaie Q=50.
        self.Q = 60
        self.Delimiter = '\0'

    def sign(self, image_path, secret_message, output_path):
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            print("Erreur lecture image")
            return

        # Conversion YCbCr
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y_float = np.float32(y)
        h, w = y.shape

        # --- STRATÉGIE DE REDONDANCE ---
        # On prépare le message complet une fois
        full_message = secret_message + self.Delimiter
        msg_bin = ''.join(format(ord(i), '08b') for i in full_message)

        # On va écrire ce message en boucle
        len_msg = len(msg_bin)
        msg_idx = 0

        total_blocks = (h // 8) * (w // 8)
        print(f"Information : On va écrire le message environ {total_blocks // len_msg} fois dans l'image.")

        for i in range(0, h, 8):
            for j in range(0, w, 8):
                # Récupération du bloc
                block = y_float[i:i + 8, j:j + 8]

                # Si le bloc est incomplet (bord de l'image), on saute
                if block.shape != (8, 8): continue

                dct_block = cv2.dct(block)

                # --- CHOIX DU COEFFICIENT ROBUSTE ---
                # (4,4) est moyen. (3,3) ou (2,2) résistent mieux au JPEG fort
                # On reste sur (4,4) pour l'instant, mais tu peux changer ici
                coeff = dct_block[4, 4]

                # On prend le bit courant et on avance l'index (en boucle avec %)
                bit = int(msg_bin[msg_idx % len_msg])

                val = round(coeff / self.Q)
                if val % 2 != bit:
                    val -= 1

                new_coef = val * self.Q
                dct_block[4, 4] = new_coef

                y_float[i:i + 8, j:j + 8] = cv2.idct(dct_block)

                msg_idx += 1  # On passe au bit suivant (et ça recommencera au début automatiquement)

        # Sauvegarde
        y_final = np.clip(y_float, 0, 255).astype(np.uint8)
        merged_ycrcb = cv2.merge([y_final, cr, cb])
        final_img = cv2.cvtColor(merged_ycrcb, cv2.COLOR_YCrCb2BGR)

        # Sauvegarde en qualité maximale pour ne pas perdre la signature tout de suite
        cv2.imwrite(output_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
        print(f"[DCT] Image signée (Redondante) sauvegardée : {output_path}")

    def read_poc(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None: return "Erreur lecture"

        y_float = np.float32(img)
        h_orig, w_orig = y_float.shape

        print("🕵️ Recherche de la grille de synchronisation (Cela peut prendre un moment)...")

        best_message = "Message introuvable"
        max_votes = 0

        # ON TESTE TOUS LES DÉCALAGES POSSIBLES (0 à 7 pixels)
        # C'est la méthode "Brute Force Synchronization"
        for shift_y in range(8):
            for shift_x in range(8):

                # On ignore les bords si l'image est trop petite pour ce shift
                if h_orig - shift_y < 8 or w_orig - shift_x < 8:
                    continue

                candidates = []
                current_msg = ""
                bits_stream = ""

                # --- 1. Extraction rapide des bits pour ce décalage ---
                # On utilise des slices numpy pour aller vite
                # On prend un sous-tableau décalé de shift_y, shift_x
                sub_img = y_float[shift_y:, shift_x:]
                h, w = sub_img.shape

                # On parcourt par pas de 8
                for i in range(0, h, 8):
                    for j in range(0, w, 8):
                        block = sub_img[i:i + 8, j:j + 8]
                        # On saute les blocs incomplets (bords droits/bas)
                        if block.shape != (8, 8): continue

                        dct_block = cv2.dct(block)

                        # On lit le bit
                        val = round(dct_block[4, 4] / self.Q)
                        bits_stream += str(int(val % 2))

                # --- 2. Reconstruction du message ---
                # (Même logique que le script précédent)
                for k in range(0, len(bits_stream), 8):
                    byte = bits_stream[k:k + 8]
                    if len(byte) < 8: break

                    try:
                        char_code = int(byte, 2)
                        char = chr(char_code)

                        if char == self.Delimiter:
                            if len(current_msg) > 1:  # Filtre les messages trop courts (bruit)
                                candidates.append(current_msg)
                            current_msg = ""
                        elif 32 <= char_code <= 126:  # Caractères imprimables seulement
                            current_msg += char
                        else:
                            current_msg = ""  # Reset sur bruit
                    except:
                        pass

                # --- 3. Comptage des votes pour ce décalage ---
                if candidates:
                    most_common = Counter(candidates).most_common(1)
                    msg, count = most_common[0]

                    # Si ce décalage donne de meilleurs résultats que les précédents
                    if count > max_votes:
                        max_votes = count
                        best_message = msg
                        # Optionnel : Afficher qu'on a trouvé une meilleure piste
                        # print(f"  -> Piste prometteuse (Shift {shift_x},{shift_y}) : '{msg}' trouvé {count} fois")

        print(f"✅ Résultat Final : '{best_message}' (Validé par {max_votes} blocs)")
        return best_message

    # def read(self, image_path):
    #     img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) # On lit juste Y (Luminance)
    #     if img is None: return "Erreur"
    #
    #     y_float = np.float32(img)
    #     h, w = y_float.shape
    #
    #     bits_stream = ""
    #
    #     # 1. Extraction de TOUS les bits de l'image
    #     for i in range(0, h, 8):
    #         for j in range(0, w, 8):
    #             block = y_float[i:i+8, j:j+8]
    #             if block.shape != (8, 8): continue
    #
    #             dct_block = cv2.dct(block)
    #             coeff = dct_block[4, 4]
    #
    #             val = round(coeff / self.Q)
    #             bits_stream += str(int(val % 2))
    #
    #     # 2. Reconstruction et Vote
    #     # On sait que le message se termine par '\0'.
    #     # On va chercher toutes les chaines qui finissent par '\0'
    #
    #     candidates = []
    #     current_char_bits = ""
    #     current_msg = ""
    #
    #     # On parcourt le flux de bits octet par octet
    #     for k in range(0, len(bits_stream), 8):
    #         byte = bits_stream[k:k+8]
    #         if len(byte) < 8: break
    #
    #         try:
    #             char_code = int(byte, 2)
    #             char = chr(char_code)
    #
    #             if char == self.Delimiter:
    #                 # Message trouvé ! On l'ajoute à la liste et on reset
    #                 if len(current_msg) > 0: # On ignore les messages vides
    #                     candidates.append(current_msg)
    #                 current_msg = ""
    #             else:
    #                 # On filtre les caractères bizarres pour éviter le bruit pur
    #                 # On garde seulement les caractères imprimables (facultatif mais aide)
    #                 if 32 <= char_code <= 126:
    #                     current_msg += char
    #                 else:
    #                     # Si on tombe sur un caractère "non-texte", c'est probablement du bruit
    #                     # On reset pour ne pas polluer le candidat
    #                     current_msg = ""
    #         except:
    #             pass
    #
    #     # 3. LE VOTE (Trouver le message le plus fréquent)
    #     if not candidates:
    #         return "Aucun message valide trouvé (Trop de compression/Crop ?)"
    #
    #     # Counter compte les occurrences : [('Hello', 50), ('Helxo', 2), ...]
    #     most_common = Counter(candidates).most_common(1)
    #     best_message, count = most_common[0]
    #
    #     print(f"📊 Analyse Statistique : Le message '{best_message}' a été trouvé {count} fois.")
    #
    #     return best_message
