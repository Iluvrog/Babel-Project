from argparse import ArgumentParser
from os import path, listdir

import pycdlib

def repack(indir, outfile):
    # A-Z + a-z + 0-9 + _
    pycdlib.pycdlib._allowed_d1_characters = set(tuple(range(65, 91)) + tuple(range(97, 123)) + tuple(range(48, 58)) + tuple((ord(b'_'),)))
    
    iso = pycdlib.PyCdlib()
    iso.new(interchange_level = 3)
    
    repack_dir(iso, indir)
    
    iso.write(outfile)
    iso.close()

   
def repack_dir(iso, actual_real_path, actual_iso_path = "/"):
    for element in listdir(actual_real_path):
        element_path = path.join(actual_real_path, element)
        if path.isdir(element_path):
            iso.add_directory(actual_iso_path + element)
            repack_dir(iso, element_path, actual_iso_path + element + "/")
        elif path.isfile(element_path):
            print(f"pack {actual_iso_path + element}")
            iso.add_file(element_path, iso_path = actual_iso_path + element)

def parse():
    parser = ArgumentParser(description = "Extract XP3")
    parser.add_argument("indir", type = str)
    parser.add_argument("outfile", type = str)
    
    return parser.parse_args()

def main():
    args = parse()
    
    repack(args.indir, args.outfile)
    
if __name__ == "__main__":
    main()
     