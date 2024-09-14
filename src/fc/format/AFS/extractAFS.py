from argparse import ArgumentParser
from os import makedirs, path


MAGICCODE = b'AFS\x00'
SIZENAMEMAX = 32

def extract(infile, outdir):
    makedirs(outdir, exist_ok=True)
    
    file = open(infile, 'rb')
    
    # Chech if the file is in the good format
    magic = file.read(4)
    if magic != MAGICCODE:
        raise Exception(f"0x{magic.decode()} get instead of 0x{MAGICCODE.decode()}, no AFS file")
        
    # Get the number of file inside the archive
    nbfile = int.from_bytes(file.read(4), "little")
    
    # Get the offset of the metadata (case V2)
    file.seek(nbfile*8 + 8)
    metadataOffset = int.from_bytes(file.read(4), "little")
    
    # If the offset is 0, it must be stored before the offset of the first entry (case V1)
    if metadataOffset == 0:
        print(f"{infile} seem to be in AFS V1")
        file.seek(8)
        position = int.from_bytes(file.read(4), "little") - 8
        file.seek(position)
        
        metadataOffset = int.from_bytes(file.read(4), "little")
    else:
        print(f"{infile} seem to be in AFS V2")
        
    #Read all the files
    for i in range(nbfile):
        # Read the offset and lenght
        file.seek(8 + i*8)
        fileOffset = int.from_bytes(file.read(4), "little")
        fileLenght = int.from_bytes(file.read(4), "little")
        
        # Read the file name
        file.seek(metadataOffset + i*48)
        filename = file.read(SIZENAMEMAX)
        filename = convert_filename(filename)
        
        dirname = path.join(outdir, path.dirname(filename))
        makedirs(dirname, exist_ok = True)
        
        newfile = open(path.join(outdir, filename), 'wb')
        file.seek(fileOffset)
        print(f"Extract {filename}, size: {fileLenght}")
        newfile.write(file.read(fileLenght))
        newfile.close()
        
    file.close()
        
        
def convert_filename(filebyte):
    res = ""
    for byte in filebyte:
        if byte == 0:
            return res
        res += chr(byte)

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