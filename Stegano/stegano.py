from bitstring import BitArray
from PIL import Image
import numpy as np
from  base64 import b64encode, b64decode
import logging


def encryption(img_name, logger):
    
    logger.info('started Encryption')

    string   = input("your message: ")
    b_arr    = bytearray(string, encoding=ENCODING)
    bits_str = BitArray(bytes=b_arr).bin
    bits_arr = [int(i) for i in bits_str]

    original      = Image.open(img_name)
    width, height = original.size

    seed          = np.random.randint(100000)
    random_gen    = np.random.RandomState(seed)
    width_offset  = random_gen.choice(width, len(bits_arr), replace=False)
    height_offset = random_gen.choice(height, len(bits_arr), replace=False)

    logger.info('seed: {}, len bits_arr: {}'.format(seed, len(bits_arr)))
    
    key_seed = b64encode(str(seed).encode(ENCODING)).decode()
    key_len  = b64encode(str(len(bits_arr)).encode(ENCODING)).decode()
    
    logger.info('seed key: {}, len key: {}'.format(key_seed, key_len))

    steg = original

    idx = 0
    for i in range(len(bits_arr)):
        w, h = int(width_offset[i]), int(height_offset[i])
        r, g, b = original.getpixel((w, h))[:3]
        if bits_arr[idx] == 0:
            r &= 254
        else:
            r |= 1
        steg.putpixel((width_offset[i], height_offset[i]), (r, g, b))
        idx += 1

    print('seed key: {}, len key: {}'.format(key_seed, key_len))
    
    logger.info('saving')
    steg.save('encripted.png')
    logger.info('finished Encryption')
    
    return key_seed, key_len


def decryption(img_name, logger):
    
    logger.info('started Decryption')
    
    key_seed = input('key seed: ')
    key_len  = input('key len: ')

    seed     = int(b64decode(key_seed).decode())
    arr_len  = int(b64decode(key_len).decode())

    logger.info('seed: {}, len bits_arr: {}'.format(seed, arr_len))

    container = Image.open(img_name)
    width, height = container.size

    random_gen    = np.random.RandomState(seed)
    width_offset  = random_gen.choice(width, arr_len, replace=False)
    height_offset = random_gen.choice(height, arr_len, replace=False)

    bits_arr = []

    for i in range(arr_len):
        w, h = int(width_offset[i]), int(height_offset[i])
        r, g, b = container.getpixel((w, h))[:3]
        if r & 1 == 1:
            bits_arr.append(1) 
        else:
            bits_arr.append(0)

    bits_str = ''.join(str(i) for i in bits_arr)
    b_arr = BitArray(bin = bits_str).tobytes()
    print('your message: {}'.format(b_arr.decode(ENCODING)))
    logger.info('finished Decryption')


if __name__ == "__main__":
    
    try:
        ENCODING = 'utf-8'
        img_name = input('image name: ')

        logging.basicConfig(filename='app.log', level=logging.INFO, format="%(name)s - %(asctime)s — %(levelname)s — %(message)s")
        logger = logging.getLogger('stegano')
        logger.disabled = False

        act = input('Encryption(1)/Decryption(2):')
        if int(act) == 1:
            key_seed, key_len = encryption(img_name, logger)
        elif int(act) == 2:
            decryption(img_name, logger)
        else:
            print('Thanks for watching!')
    except Exception as e:
        print('Something went wrong.\nThe error: {}'.format(e))



