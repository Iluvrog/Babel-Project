from argparse import ArgumentParser
from os import makedirs, path

MAGICCODE = b'GPDA'
ENTRY_SIZE = 0x10

def extract(infile, outdir, mode = 64):
    if mode != 32 and mode != 64:
        raise Exception(f"mode must be 32 or 64, not {mode}")
        
    makedirs(outdir, exist_ok=True)
    
    file = open(infile, 'rb')
    
    header = file.read(16)
    magic = header[:4]
    
    if magic != MAGICCODE:
        raise Exception(f"magic must be {MAGICCODE.decode()} not {magic.decode()}")
        
    if mode == 32:
        archivesize = int.from_bytes(header[4:8], "little")
    else:
        archivesize = int.from_bytes(header[4:12], "little")
        
    nbfiles = int.from_bytes(header[12:], "little")
    if nbfiles == 0:
        return
    
    filesinfo = file.read(ENTRY_SIZE * nbfiles)
    
    for i in range(nbfiles):
        
        info = filesinfo[i*ENTRY_SIZE:(i+1)*ENTRY_SIZE]
        
        if mode == 32:
            offset = int.from_bytes(info[0:4], "little")
        else:
            offset = int.from_bytes(info[0:8], "little")
            
        size = int.from_bytes(info[8:12], "little")
        
        offsetname = int.from_bytes(info[12:], "little")
        
        file.seek(offsetname)
        sizename = int.from_bytes(file.read(4), "little")
        name = file.read(sizename).decode()
        
        file.seek(offset)
        
        print(f"Extract {name}")
        fullname = path.join(outdir, name)
        fullname = check_fullname(fullname)
        file_out = open(fullname, 'wb')
        file_out.write(file.read(size))
        file_out.close()
        
    file.close()
    
def check_fullname(fullname):
    if not path.exists(fullname):
        return fullname
    
    split_ext = fullname.rfind(".")
    ext = fullname[split_ext + 1:]
    name_without_ext = fullname[:split_ext]
    
    replica = 1
    while path.exists(name_without_ext + " (" + str(replica) + ")." + ext):
        replica += 1
        
    fullname =  name_without_ext + " (" + str(replica) + ")." + ext
    return fullname
        
def parse():
    parser = ArgumentParser(description = "Extract GPDA")
    parser.add_argument("infile", type = str)
    parser.add_argument("outdir", type = str)
    parser.add_argument("mode", type = int, choices=[32, 64], default = 64, nargs='?')
    
    return parser.parse_args()

def main():
    args = parse()
    
    extract(args.infile, args.outdir, args.mode)
    
if __name__ == "__main__":
    main()