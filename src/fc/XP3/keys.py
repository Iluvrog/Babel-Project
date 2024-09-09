import json
import os

keys = None

def getEncParams(Encryption):
    global keys
    if not keys:
        pathdir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(pathdir, "keys.json")
        file = open(path, 'r')
        keys = json.load(file)
        file.close()
    if not Encryption in keys:
        print('Check that you\'re spelling the encryption type correctly')
        print('Defaulting to no encryption')
        return 0, 0, 0, 0
    k = keys[Encryption]
    return int(k["MasterKey"], 16), int(k["BakKey0"], 16),\
        int(k["BakKey1"], 16), int(k["FirstXor"], 16)