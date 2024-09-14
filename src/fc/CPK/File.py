


class FileTable():
    
    def __init__(self):
        
        self.table = []
        
    def append(self, entry):
        
        if type(entry) is not FileEntry:
            raise Exception(f"FileTable can only append FileEntry, no {type(entry)}")
            
        self.table.append(entry)
        
    def get_file_by_name(self, Name):
        
        candidates = [e for e in self.table if e.FileName == Name]
        
        if len(candidates) == 0:
            raise Exception(f"FileTable, 0 FileEntry with name {Name}")
        if len(candidates) > 1:
            print(f"[WARNING] - {len(candidates)} FileEntry with name {Name}, select only first")
        return candidates[0]
    
    def get_all_FILE(self):
        
        return [e for e in self.table if e.FileType == "FILE"]

class FileEntry():
    
    def __init__(self, DirName = "", FileName = "", FileSize = -1, FileSizePos = -1,
                 FileSizeType = -1, ExtractSize = -1, ExtractSizePos = -1, ExtractSizeType = -1,
                 FileOffset = -1, FileOffsetPos = -1, FileOffsetType = -1, Offset = -1,
                 ID = "", UserString = "", UpdateDateTime = 0, LocalDir = "",
                 TOCName = "", Encrypted = False, FileType = ""):
        
        self.DirName = DirName
        self.FileName = FileName
        self.FileSize = FileSize
        self.FileSizePos = FileSizePos
        self.FileSizeType = FileSizeType
        self.ExtractSize = ExtractSize
        self.ExtractSizePos = ExtractSizePos
        self.ExtractSizeType = ExtractSizeType
        self.FileOffset = FileOffset
        self.FileOffsetPos = FileOffsetPos
        self.FileOffsetType = FileOffsetType
        self.Offset = Offset
        self.ID = ID
        self.UserString = UserString
        self.UpdateDateTime = UpdateDateTime
        self.LocalDir = LocalDir
        self.TOCName = TOCName
        self.Encrypted = Encrypted
        self.FileType = FileType