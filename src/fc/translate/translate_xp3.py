from fc.format.XP3 import extractXP3, repackXP3
from .translate_ks import translate_ks
from fc.get_files import get_files

from os import path, makedirs
from tempfile import gettempdir
from shutil import copyfile, copytree, rmtree
from random import randint


TEMP_INPUT = "INPUT"
TEMP_OUTPUT = "OUTPUT"


def translate_xp3(inpath, outpath):
    
    tempdir = path.join(gettempdir(), "STranslate", "xp3", str(randint(0, 99999999)))
    makedirs(tempdir, exist_ok=True)
    
    extract(inpath, tempdir)
    
    translateKS(tempdir)
    
    repack(outpath, tempdir)
    
    rmtree(tempdir)
    
def extract(inpath, tempdir):
    extractXP3.extract(inpath, path.join(tempdir, TEMP_INPUT))
    
def translateKS(tempdir):
    def ignore_files(dir, files):
        return [f for f in files if path.isfile(path.join(dir, f))]
    
    inputdir = path.join(tempdir, TEMP_INPUT)
    outputdir = path.join(tempdir, TEMP_OUTPUT)
    copytree(inputdir, outputdir, ignore = ignore_files)
    
    for file in get_files("*", inputdir):
        output_name = file.replace(inputdir, outputdir)
        if not file.endswith(".ks"):
            copyfile(file, output_name)
            continue
        
        #print(f"\ttranslate {file}")
        translate_ks(file, output_name)
    
def repack(outpath, tempdir):
    repackXP3.repack(path.join(tempdir, TEMP_OUTPUT), outpath)