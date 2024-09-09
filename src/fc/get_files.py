from os import walk, path
from fnmatch import fnmatch


def get_files(pattern, path_dir):
    result = []
    for root, dirs, files in walk(path_dir):
        for name in files:
            if fnmatch(name, pattern):
                result.append(path.join(root, name))
    return result

# Need chardet
def get_encoding(file_name):
    from chardet.universaldetector import UniversalDetector
    
    detector = UniversalDetector()
    
    file = open(file_name, 'rb')
    for line in file:
        detector.feed(line)
        if detector.done:
            break
    
    file.close()
    detector.close()
    return detector.result["encoding"]