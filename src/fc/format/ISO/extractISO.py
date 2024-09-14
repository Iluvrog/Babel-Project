from argparse import ArgumentParser
from os import makedirs, path

from pycdlib import PyCdlib


def extract(infile, outpath):
    
    iso = PyCdlib()
    iso.open(infile)
    
    print("udf", iso.has_udf())
    print("rock_ridge", iso.has_rock_ridge())
    print("joliet", iso.has_joliet())
    
    extract_dir(iso, outpath)

def extract_dir(iso, actual_real_path, actual_iso_path = "/"):
    makedirs(actual_real_path, exist_ok=True)
    
    for child in iso.list_children(iso_path=actual_iso_path):
        name = child.file_identifier().decode()
        if name in ['..', '.']:
            continue
        if child.is_dir():
            extract_dir(iso, path.join(actual_real_path, name), actual_iso_path +  ("/" if actual_iso_path != "/" else "") + name)
        elif child.is_symlink():
            pass #DOIT
        else: #Is a file
            print(f"extract {(actual_iso_path if actual_iso_path != '/' else '') + '/' + name}")
            iso.get_file_from_iso(path.join(actual_real_path, name),  iso_path = actual_iso_path +  "/" + name)

def parse():
    parser = ArgumentParser(description = "Extract XP3")
    parser.add_argument("infile", type = str)
    parser.add_argument("outdir", type = str)
    
    return parser.parse_args()

def main():
    args = parse()
    
    extract(args.infile, args.outdir)
    
if __name__ == "__main__":
    main()
    
    
    
    









"""
def extract(infile, outdir):
    file = open(infile, 'rb')
    
    file.seek(16*2048)
    
    while (check_volume_descritpor(volume_descriptor := file.read(2048))) != 0xff:
        print(volume_descriptor)
    
def check_volume_descritpor(volume_descriptor):
    if volume_descriptor[0] not in [0x00, 0x01, 0x02, 0x03, 0xff]:
        print(f"[WARNING] - Not good type, get '0x{volume_descriptor[0]:X}' instead of '0x0/0x1/0x2/0x3/0x255'")
    if volume_descriptor[1:6] != b'CD001':
        print(f"[WARNING] - Not good identifier, get '0x{volume_descriptor[1:6]:X}' instead of '0xCD001'")
    if volume_descriptor[6] != 0x01:
        print(f"[WARNING] - Not good version, get '0x{volume_descriptor[6]:X}' insed of 0x01")
        
    return volume_descriptor[0]
"""  