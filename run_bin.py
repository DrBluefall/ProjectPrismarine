"""
Run a script from inside of bin, without needing to install the package.

Usage:
    `python(v) run_bin.py mymodule`

    - You import a module by passing in an argument of the filepath (from inside of bin).
    - It supports file imports and from within subfolders.
    - The path is inside of bin, so the argv "mymodule" will be imported at "bin/mymodule".

"""
import sys
import importlib


def main():
    """Run the script inside of bin."""
    try:
        bin_module = importlib.import_module("bin." + sys.argv[1])  # pylint: disable=W0612
    except (TypeError, IndexError):
        raise AttributeError("You did not specify the module.")

    print("Type the function you want to run.")
    while True:
        function = input('\n> ')
        eval("bin_module." + function)  # pylint: disable=W0123


if __name__ == '__main__':
    main()
