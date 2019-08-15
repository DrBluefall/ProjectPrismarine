from utils.loadout_gen import *
from utils.decoder import decode
from pprint import pprint

if __name__ == "__main__":

    x = compile_loadout_dict(decode('0409254a529224a529674a529'))
    img = generate_image(x)
    img.show()