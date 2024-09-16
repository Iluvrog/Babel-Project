try:
    from .CPK import read_data, decrompressCRILAYLA
except ImportError:
    from CPK import read_data, decrompressCRILAYLA

from argparse import ArgumentParser
from os import makedirs, path



CRILAYLA = b"CRILAYLA"

def extract(infile, outdir):
    
    makedirs(outdir, exist_ok=True)
    
    file = open(infile, 'rb')
    
    file_table = read_data(file)
    
    entries = file_table.get_all_FILE()
    for entry in entries:
        extract_file(file, entry, outdir)
        
    file.close()
    
def extract_file(file, entry, outdir):
    
    if entry.DirName != "":
        outdir = path.join(outdir, entry.DirName)
        makedirs(outdir, exist_ok=True)
        
    file.seek(entry.FileOffset)
    isComp = file.read(8)
    file.seek(entry.FileOffset)
    
    chunk = file.read(entry.FileSize)
    if isComp == CRILAYLA:
        chunk = decrompressCRILAYLA(chunk)
    
    print(f"Extract {path.join(entry.DirName, entry.FileName)}")
    new_file = open(path.join(outdir, entry.FileName), 'wb')
    new_file.write(chunk)
    new_file.close()
    

def parse():
    parser = ArgumentParser(description = "Extract CPK")
    parser.add_argument("infile", type = str)
    parser.add_argument("outdir", type = str)
    
    return parser.parse_args()

def main():
    args = parse()
    
    extract(args.infile, args.outdir)
    
if __name__ == "__main__":
    main()