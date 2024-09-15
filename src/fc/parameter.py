from json import load, dump
from os.path import join

GLOBAL_VARS = None

def read_json(path = "config.json"):
    global GLOBAL_VARS
    try:
        GLOBAL_VARS = load(open(path, encoding='utf-8'))
    except FileNotFoundError:
        GLOBAL_VARS = load(open(join("..", path), encoding='utf-8'))
        
def get(*strings):
    if GLOBAL_VARS == None:
        read_json()
    d = GLOBAL_VARS
    not_found = False
    for s in strings:
        try:
            if s in d:
                d = d[s]
            else:
                not_found = True
        except:
            not_found = True
        if not_found:
            print("/!\\Can't find the config " + str(strings))
            return None
    return d

def update(value, *path):
    global GLOBAL_VARS
    d = GLOBAL_VARS
    for p in path[:-1]:
        d = d[p]
    d[path[-1]] = value
    save()
    
def save(path = "config.json"):
    file = open(path, 'w')
    file.write(dump(GLOBAL_VARS, indent=2))
    file.close()