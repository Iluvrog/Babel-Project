from argparse import ArgumentParser
from os import path, listdir

MAGICCODE = b'AFS\x00'
SIZENAMEMAX = 32
SIZEFILETOTALMAX = 1<<32

def repack(indir, outfile, version = 2):
    files = get_files(indir)
    sizes = []
    for file in files:
        file = path.join(indir, file)
        sizes.append(path.getsize(file))
    totalsize = sum(sizes)
    
    # Raise Exception if files to big
    # May cause an error if metadataOffset exced 1<<32B but file not
    if totalsize >= SIZEFILETOTALMAX:
        raise Exception(f"Size of files mustn't excess {SIZEFILETOTALMAX - 1} but values {totalsize}")
    
    for file in files:
        if len(file) > SIZENAMEMAX:
            raise Exception(f"{file} name excess {SIZENAMEMAX} characters (values {len(file)})")
    
    file_out = open(outfile, 'wb')
    file_out.write(MAGICCODE)
    
    nbfiles = len(files)
    file_out.write(nbfiles.to_bytes(4, "little"))
    
    for i in range(len(files)):
        size = sizes[i]
        offset = 8 + 8*len(files) + 4 + sum(sizes[:i])
        
        file_out.write(offset.to_bytes(4, 'little'))
        file_out.write(size.to_bytes(4, 'little'))
        
    metadataoffset = 8 + 8*len(files) + 4 + sum(sizes)
    file_out.write(metadataoffset.to_bytes(4, 'little'))
    
    for file in files:
        file_in = open(path.join(indir, file), 'rb')
        file_out.write(file_in.read())
        file_in.close()
        
    for file in files:
        size = len(file)
        file_out.write(file.encode())
        file_out.write(b'\x00'*(48-size))
        
    file_out.close()
        
def get_files(indir):
    res = []
    for file in listdir(indir):
        if path.isfile(path.join(indir, file)):
            res.append(file)
        elif path.isdir(path.join(indir, file)):
            deep = get_files(path.join(indir, file))
            for deepfile in deep:
                res.append(file + "/" + deepfile)
    return res

def parse():
    parser = ArgumentParser(description = "Repack XP3")
    parser.add_argument("indir", type = str)
    parser.add_argument("outfile", type = str)
    parser.add_argument("version", type = int, choices=[1, 2], default = 2, nargs = '?')
    
    return parser.parse_args()

def main():
    args = parse()
    
    repack(args.indir, args.outfile, args.version)
    
if __name__ == "__main__":
    main()