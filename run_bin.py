"""
Run a script from inside of bin, without needing to install the package.

Usage:
    `python(v) run_bin.py mymodule myfolder.mymodule`

    You import a module by passing in an argument of the filepath
    (from inside of bin). It supports multiple file imports
    and from within subfolders. The path is inside of bin, so the
    argv "mymodule" will be imported at "bin/mymodule".

"""
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
