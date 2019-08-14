from utils.loadout_gen import compile_loadout_dict
from utils.decoder import decode
from pprint import pprint

if __name__ == "__main__":

    x = compile_loadout_dict(decode('040c254a50722294006702d8c'))
    pprint(x)