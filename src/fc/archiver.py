from .AFS.extractAFS import extract as extractAFS
from .AFS.repackAFS import repack as repackAFS

from .ISO.extractISO import extract as extractISO
from .ISO.extractISO import repack as repackISO

from .XP3.extractXP3 import extract as extractXP3
from .XP3.repackXP3 import repack as repackXP3

from os import path, makedirs
from tempfile import gettempdir
from random import randint
from shutil import copyfile, copytree, rmtree



def extract(infile, outdir = None):
    filename = path.basename(infile)
    
    if not outdir:
        basedir = path.dirname(infile)
        split = filename.split(".")[:-1]
        outdir = path.join(basedir, ".".join(split))
    
    ext = filename.split(".")[-1]
    
    match ext:
        case "afs":
            extractAFS(infile, outdir)
        case "iso":
            extractISO(infile, outdir)
        case "xp3":
            extractXP3(infile, outdir)
        case _:
            raise Exception(f"Cannot find extract function for extension {ext}")
        

def pack(indir, outfile):
    print(outfile)
    filename = path.basename(outfile)
    ext = filename.split(".")[-1]
    
    match ext:
        case "afs":
            repackAFS(indir, outfile)
        case "iso":
            repackISO(indir, outfile)
        case "xp3":
            repackXP3(indir, outfile)
        case _:
            raise Exception(f"Cannot find pack function for extension {ext}")
            
def pack_from_list(*infiles, outfile):
    tempdirbase = gettempdir()
    stringpah = "!".join(infiles)
    tempdir = path.join(tempdirbase, str(hash(stringpah)) + str(randint(100000, 999999)))
    
    makedirs(tempdir)
    
    for file in infiles:
        if path.isfile(file):
            copyfile(file, path.join(tempdir, path.basename(file)))
        elif path.isdir(file):
            copytree(file, path.join(tempdir, path.basename(file)))
            
    pack(tempdir, outfile)
    
    rmtree(tempdir)