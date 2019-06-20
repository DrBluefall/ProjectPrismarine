"""Run a script from inside of bin, without needing to install the package."""
import sys
import importlib


def main():
    """Run the script inside of bin."""
    for arg in sys.argv[1:]:
        bin_module = importlib.import_module("bin." + arg)

    while True:
        function = input("Evaluate which function from the module: ")
        print(eval("bin_module." + function))


if __name__ == '__main__':
    main()
