try:
    from .parameter import get
except ImportError:
    from parameter import get

from threading import Lock
from os import path
from json import load, dumps
from shutil import copyfile


class Singleton():
    
    _lock: Lock = Lock()
    _instance = {}
    
    def __new__(self, *args, **kwargs):
        with self._lock:
            if self not in self._instance:
                instance = super().__new__(self, *args, **kwargs)
                self._instance[self] = instance
        return self._instance[self]
    
class Cache(Singleton):
    
    _init = False
    
    def __init__(self):
        
        if self._init:
            return
        self._init = True
        
        self.cache = {}
        self.cache_file = path.join(path.expanduser("~"), "Babel_project", "CACHE", "cache.json")
        cache_path = None
        if path.exists(self.cache_file) and path.isfile(self.cache_file):
            cache_path = self.cache_file
        elif path.exists(self.cache_file + ".back") and path.isfile(self.cache_file + ".back"):
            cache_path = self.cache_file + ".back"
            
        if cache_path:
            cache_dict = open(cache_path,'r')
            self.cache = load(cache_dict)
            cache_dict.close()
            
        self.language_in = get("language", "in")
        self.language_out = get("language", "out")
            
    def exist(self, key):
        with self._lock:
            if not self.language_in in self.cache:
                #○print(1, self.language_in)
                return False
            if not key in self.cache[self.language_in]:
                #print(2, key)
                return False
            if not self.language_out in self.cache[self.language_in][key]:
                #print(3, self.language_out)
                return False
            return True
    
    def get(self, key):
        with self._lock:
            return self.cache[self.language_in][key][self.language_out]
    
    def add(self, key, value):
        with self._lock:
            if not self.language_in in self.cache:
                self.cache[self.language_in] = {}
            if not key in self.cache[self.language_in]:
                self.cache[self.language_in][key] = {}
            self.cache[self.language_in][key][self.language_out] = value
            
    def set_language_in(self, language):
        with self._lock:
            self.language_in = language

    def set_language_out(self, language):
        with self._lock:
            self.language_out = language        
        
    def write(self):
        with self._lock:
            print("Write cache")
            if path.exists(self.cache_file) and path.isfile(self.cache_file):
                copyfile(self.cache_file, self.cache_file + ".back")
            cache_file = open(self.cache_file, 'w')
            cache_file.write(dumps(self.cache, indent=0))
            cache_file.close()