from fc.archive.XP3 import extractXP3, repackXP3
from .translate_ks import translate_ks
from fc.get_files import get_files

from os import path, makedirs
from tempfile import gettempdir
from shutil import copyfile, copytree, rmtree

TEMP_INPUT = "INPUT"
TEMP_RAW = "RAW"
TEMP_TRANSLATE = "TRANSLATE"

def patch_xp3(*files, output_dir):
    print("h")
    if not len(files):
        return
    
    patch_name = "patch" + get_patch_number(*files) + ".xp3"
    patch_name = path.join(output_dir, patch_name)
    
    files = sorted(files)
    
    hashdir = str(hash("xp3".join(files)))
    tempdir = path.join(gettempdir(), "STranslate", "xp3_patch", hashdir)
    
    makedirs(path.join(tempdir, TEMP_INPUT), exist_ok=True)
    makedirs(path.join(tempdir, TEMP_RAW), exist_ok=True)
    makedirs(path.join(tempdir, TEMP_TRANSLATE), exist_ok=True)
    
    extract(*files, tempdir = tempdir)
    translateKS(tempdir)
    repack(tempdir, patch_name)
    
    rmtree(tempdir)
    
def extract(*files, tempdir):
    for file in files:
        outname = path.join(tempdir, TEMP_INPUT, str(hash(file)))
        extractXP3.extract(file, outname)
        
        for f in get_files("*.ks", outname):
            f_name = path.basename(f)
            copyfile(f, path.join(tempdir, TEMP_RAW, f_name))
    
def translateKS(tempdir):
    dirpath = path.join(tempdir, TEMP_RAW)
    for file in get_files("*", dirpath):
        print(f"\ttranslate {file}")
        output_name = file.replace(dirpath, path.join(tempdir, TEMP_TRANSLATE))
        translate_ks(file, output_name)
    
def repack(tempdir, patch_path):
    repackXP3.repack(path.join(tempdir, TEMP_TRANSLATE), patch_path)
    
def get_patch_number(*files):
    max_patch = 0
    for file in files:
        file = path.basename(file)
        if not file.startswith("patch") or not file.endswith(".xp3"):
            continue
        if file == "patch.xp3":
            max_patch = max(max_patch, 1)
        else:
           max_patch = max(max_patch, int(file[5:-4]))
           
    max_patch += 1
    if max_patch == 1:
        return ""
    return str(max_patch)