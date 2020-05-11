import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", 'pygame', 'pygame_menu', 'pyAesCrypt', 'socket', 'random', 'os', 'time', 'json', 'io', 'logging']}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Math Dragon",
        version = "0.1",
        description = "Math Dragon",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Math_Dragon.pyw", base=base, icon='icon.ico')])
