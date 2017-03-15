import os
import sys
from syntax_analysis import SyntaxAnalyst


# search all files under this directory.
def _getfile(file_name):
    for name in os.listdir(os.getcwd()):
        if os.path.isdir(name):
            pre_dir = os.getcwd()
            os.chdir(name)
            res = _getfile(file_name)
            os.chdir(pre_dir)
            if res is not None:
                return res
        else:
            if name == file_name and os.path.isfile(name):
                return os.path.abspath(name)
    return None

# filename = 'sample_code0'
if len(sys.argv) > 1:
    filename = _getfile(sys.argv[1])
else:
    filename = _getfile(input('Input file name:\n'))
assert (filename is not None)
print(os.getcwd())
sa = SyntaxAnalyst(filename)
sa.execute()
