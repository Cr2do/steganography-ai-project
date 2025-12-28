from algorithm.DCT.dct import DCT
from algorithm.LSB.lsb import LSB
from algorithm.utils import metrics, attack_transform_img_to_jpeg, calcul_capacity_max


def lsb_process(input_image_path, output_image_path, attacked_lsb_path, message):
    print("******************* Test of LSB ****************")

    lsb = LSB()

    lsb.sign(input_image_path, message, output_image_path)

    p , s = metrics(input_image_path, output_image_path)
    print(f'Metric 1 : Visual quality is {p} dB ; SSIm is {s}')

    attack_transform_img_to_jpeg(output_image_path, attacked_lsb_path, 80)

    try:
        p , s = metrics(output_image_path, attacked_lsb_path)
        print(f'Metric 2 : Visual quality is {p} dB ; SSIm is {s}')
        recup = lsb.read(attacked_lsb_path)
        print(f'Message inside is {recup}')
        if message in recup:
            print(f'Success {recup}')
        else:
            print('LSB Not working')
    except:
        print('unable to read file')


def dct_process(input_image_path, output_image_path, attacked_dct_path, message):
    print("******************* Test of DCT ****************")

    dct = DCT()

    dct.sign(input_image_path, message, output_image_path)

    p , s = metrics(input_image_path, output_image_path)
    print(f'Metric 1 : Visual quality is {p} dB ; SSIm is {s}')


    attack_transform_img_to_jpeg(output_image_path, attacked_dct_path, 80)

    try:
        p , s = metrics(output_image_path, attacked_dct_path)
        print(f'Metric 2 : Visual quality is {p} dB ; SSIm is {s}')
        recup = dct.read(attacked_dct_path)
        print(f'Message inside is {recup}')
        if message in recup:
            print(f'Success {recup}')
        else:
            print('DCT Not working')
    except:
        print('unable to read file')

class Main:

    input_image_path = "./assets/results/input.png"
    output_image_path = "./assets/results/output.png"

    attacked_path = './assets/results/attack.jpeg'


    message = 'lorem ipsum'

    capacity = calcul_capacity_max(input_image_path, 1, 8)

    if len(message) > capacity:
        print(f'Message too long; {capacity}')
    else:
        print(f'capacity is : {capacity}')
        dct_algo = DCT()

        recup = dct_algo.read_poc('./assets/results/output.png')
        print(f'Message inside is {recup}')
        if message in recup:
            print(f'Success {recup}')
        else:
            print('DCT Not working')

        #dct_algo.sign_prod(input_image_path, message, output_image_path)
        #dct_algo.read('./assets/results/resize_1.jpg')

        # dct_process(input_image_path, output_image_path, attacked_path, message)

    #lsb_process(input_image_path, output_image_path, attacked_path, message)


Main()



