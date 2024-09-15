from os import path, makedirs, listdir, system, remove
from json import load, dumps
from html import escape
from shutil import rmtree

HOME = None
CACHE_DIR = None
PROJECTS_DIR = None

JSONFILE = ".projectdata.json"
PARENTPATH = ".."

class Project():
    
    def __init__(self, pathdir):
        self.path = pathdir
        self.data = load(open(path.join(self.path, JSONFILE), 'r'))
        self.name = self.data["name"] if "name" in self.data else f"No name: {path.split(self.path)[-1]}"
        self.insidepath = []
        
    def get_files(self):
        actualpath = path.join(self.path, *self.insidepath)
        files = listdir(actualpath)
        if self.insidepath == []:
            files.remove(JSONFILE)
        return [file for file in files if path.isfile(path.join(actualpath,file))]
    
    def get_dirs(self):
        actualpath = path.join(self.path, *self.insidepath)
        dirs = listdir(actualpath)
        if self.insidepath != []:
            dirs.append(PARENTPATH)
        return [dir for dir in dirs if path.isdir(path.join(actualpath,dir))]
    
    def get_actual_path(self):
        return path.join(self.path, *self.insidepath)
    
    def update_path(self, dir):
        if dir == PARENTPATH:
            self.insidepath = self.insidepath[:-1]
        else:
            self.insidepath.append(dir)
            
    def open(self, file):
        absolute_path = path.join(self.path, *self.insidepath, file)
        system('"' + absolute_path + '"')
        
    def delete(self, file, dir = False):
        absolute_path = path.join(self.path, *self.insidepath, file)
        
        if dir:
            rmtree(absolute_path)
        else:
            remove(absolute_path)
        

def create_home_directory():
    global HOME, CACHE_DIR, PROJECTS_DIR
    if HOME:
        return
    
    makedirs(HOME := path.join(path.expanduser("~"), "Babel_project"), exist_ok=True)
    makedirs(CACHE_DIR := path.join(HOME, "CACHE"), exist_ok=True)
    makedirs(PROJECTS_DIR := path.join(HOME, "PROJECTS"), exist_ok=True)
    return HOME

def test_HOME():
    if not HOME:
        create_home_directory()

def list_projects():
    test_HOME()
        
    projects = []
    for project in listdir(PROJECTS_DIR):
        project = path.join(PROJECTS_DIR, project)
        if path.isfile(project):
            continue
        project_json = path.join(project, JSONFILE)
        if path.exists(project_json) and path.isfile(project_json):
            projects.append(Project(project))
            
    return projects

def create_project(name):
    if name in [p.name for p in list_projects()]:
        raise Exception(f"Project '{name}' already exists")
        return
        
    dirname = escape(name)
    
    while path.exists(dirpath := path.join(PROJECTS_DIR, dirname)):
        dirname += "0"
    
    makedirs(dirpath)
    with open(path.join(dirpath, JSONFILE), 'w') as file:
        file.write(dumps({"name": name}, indent=0))
        
    return get_project(name)
        
def get_project(name):
    for project in list_projects():
        if project.name == name:
            return project
    return None