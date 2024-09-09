from .translate_ks import translate_ks
from .translate_xp3 import translate_xp3
from fc.Cache import Cache

from .patch_xp3 import patch_xp3

from os import path


def translate(*files):
    fail = 0
    failed = []
    
    for file in files:
        basename = path.split(file)[-1]
        if basename == "":
            basename = path.split(file)[-2]
        ext = basename.split(".")[-1]
        name = basename[:-len(ext)-1]
        dirname = path.dirname(file)
        outputname = path.join(dirname, ".".join([name, "translate", ext]))
        
        match ext:
            case "ks":
                translate_ks(file, outputname)
            case "xp3":
                translate_xp3(file, outputname)
            case _:
                print(f"Can't translate {basename}, check the extension")
                fail += 1
                failed.append(basename)
                #continue
           
    Cache().write()
    return fail, failed
    
def patch(*files, actual_dir):
    if len(files) == 0:
        return 0
    
    ext = ""
    for file in files:
        if file.endswith("/"):
            return -1
        file_ext = path.basename(file).split(".")[-1]
        if ext == "":
            ext = file_ext
        if file_ext != ext:
            return -1
        
    match ext:
        case "xp3":
            patch_xp3(*files, output_dir = actual_dir)
        case _:
            print(f"Can't patch extension {ext}, check extension")
            return -1
    
    Cache().write()
    return 0