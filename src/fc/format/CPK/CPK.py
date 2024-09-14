try:
    from .UTF import UTF
    from .File import FileTable, FileEntry
except ImportError:
    from UTF import UTF
    from File import FileTable, FileEntry
    
CPKCODE = b"CPK "
UTFCODE = b"@UTF"
TOCCODE = b"TOC "
ETOCCODE = b"ETOC"
ITOCCODE = b"ITOC"
GTOCCODE = b"GTOC"

ENDIAN = "little"

def read_data(file):
    filetable = FileTable()
    
    # Chech if the file is in the good format
    magic = file.read(4)
    if magic != CPKCODE:
        raise Exception(f"{magic} get instead of {CPKCODE}, no CPK file")
        
    utf_packet, utf_size, isUTFencrypted = readUTFData(file)
        
    filetable.append(FileEntry(FileName = "CPK_HDR", FileOffsetPos = file.tell() + 0x10,
                               FileSize = utf_size, Encrypted = isUTFencrypted,
                               FileType = "CPK"))
        
    utf = UTF(utf_packet)
    
    #utf.print_data()
    
    TocOffset = utf.get_Column_Data2(0, "TocOffset", 3)
    TocOffsetPos = utf.get_Column_Position(0, "TocOffset")
    TocOffsetType = utf.get_Column_Type(0, "TocOffset")
    
    EtocOffset = utf.get_Column_Data2(0, "EtocOffset", 3)
    EtocOffsetPos = utf.get_Column_Position(0, "EtocOffset")
    EtocOffsetType = utf.get_Column_Type(0, "EtocOffset")
    
    ItocOffset = utf.get_Column_Data2(0, "ItocOffset", 3)
    ItocOffsetPos = utf.get_Column_Position(0, "ItocOffset")
    ItocOffsetType = utf.get_Column_Type(0, "ItocOffset")
    
    GtocOffset = utf.get_Column_Data2(0, "GtocOffset", 3)
    GtocOffsetPos = utf.get_Column_Position(0, "GtocOffset")
    GtocOffsetType = utf.get_Column_Type(0, "GtocOffset")
    
    ContentOffset = utf.get_Column_Data2(0, "ContentOffset", 3)
    ContentOffsetPos = utf.get_Column_Position(0, "ContentOffset")
    ContentOffsetType = utf.get_Column_Type(0, "ContentOffset")
    filetable.append(create_file_entry("CONTENT_OFFSET", ContentOffset, ContentOffsetType,
                                       ContentOffsetPos, "CPK", "CONTENT", False))
    
    Files = utf.get_Column_Data2(0, "Files", 2) # What is the purpose of the var ???
    Align = utf.get_Column_Data2(0, "Align", 1)
    
    if TocOffset != 0xFFFFFFFFFFFFFFFF:
        #print("toc")
        filetable.append(create_file_entry("TOC_HDR", TocOffset, TocOffsetType, TocOffsetPos, "CPK", "HDR", False))
        readTOCData(file, TocOffset, ContentOffset, filetable)
        
    if EtocOffset != 0xFFFFFFFFFFFFFFFF:
        #print("etoc")
        filetable.append(create_file_entry("ETOC_HDR", EtocOffset, EtocOffsetType, EtocOffsetPos, "CPK", "HDR", False))
        readETOCdata(file, EtocOffset, filetable)
        
    if ItocOffset != 0xFFFFFFFFFFFFFFFF:
        #print("itoc")
        filetable.append(create_file_entry("ITOC_HDR", ItocOffset, ItocOffsetType, ItocOffsetPos, "CPK", "HDR", False))
        readITOCdata(file, ItocOffset, ContentOffset, Align, filetable)
        
    if GtocOffset != 0xFFFFFFFFFFFFFFFF:
        #print("gtoc")
        filetable.append(create_file_entry("GTOC_HDR", GtocOffset, GtocOffsetType, GtocOffsetPos, "CPK", "HDR", False))
        readGTOCdata(file, GtocOffset, filetable)
        
    return filetable
    
def create_file_entry(FileName, FileOffset, FileOffsetType, FileOffsetPos, TOCName, FileType, encrypted):
    return FileEntry(FileName = FileName, FileOffset = FileOffset, FileOffsetType = FileOffsetType,
                     FileOffsetPos = FileOffsetPos, TOCName = TOCName, FileType = FileType,
                     Encrypted = encrypted)

def readUTFData(file):
    unk1 = file.read(4) # What it does ??? Seem to be 0xff000000 in my first example
    
    utf_size = int.from_bytes(file.read(8), "little")
    utf_packet = file.read(utf_size)
    
    isUTFencrypted = False
    if utf_packet[:4] != UTFCODE:
        isUTFencrypted = True
        utf_packet = decryptUTF(utf_packet)
        
    return utf_packet, utf_size, isUTFencrypted
        
def decryptUTF(data):
    result = bytearray()
    
    m = 0x0000655f
    t = 0x00004115
    
    for b in data:
        result.append(b ^ (m & 0xff)) # I take only the last byte
        m = (m*t) % 2<<32
        
    return bytes(result)

def readTOCData(file, TOCOffset, ContentOffset, filetable):
    
    addOffset = min(TOCOffset, ContentOffset)
    
    file.seek(TOCOffset)
    
    magic = file.read(4)
    if magic != TOCCODE:
        raise Exception(f"{magic} get instead of {TOCCODE}, no TOC data")
        
    TOC_packet, TOC_size, isUTFencrypted = readUTFData(file)
    
    TOC_entry = filetable.get_file_by_name("TOC_HDR")
    TOC_entry.Encrypted = isUTFencrypted
    TOC_entry.FileSize = TOC_size
    
    files = UTF(TOC_packet)
    for i in range(files.nb_rows):
        filetable.append(FileEntry(
            TOCName = "TOC",
            DirName = files.get_Column_Data(i, "DirName"),
            FileName = files.get_Column_Data(i, "FileName"),
            FileSize = files.get_Column_Data(i, "FileSize"),
            FileSizePos = files.get_Column_Data(i, "FileSizePos"),
            FileSizeType = files.get_Column_Data(i, "FileSizeType"),
            ExtractSize = files.get_Column_Data(i, "ExtractSize"),
            ExtractSizePos = files.get_Column_Data(i, "ExtractSizePos"),
            ExtractSizeType = files.get_Column_Data(i, "ExtractSizeType") + addOffset,
            FileOffset = files.get_Column_Data(i, "FileOffset"),
            FileOffsetPos = files.get_Column_Data(i, "FileOffsetPos"),
            FileOffsetType = files.get_Column_Data(i, "FileOffsetType"),
            ID = files.get_Column_Data(i, "ID"),
            UserString = files.get_Column_Data(i, "UserString"),
            FileType = "FILE",
            Offset = addOffset
            ))
        
def readETOCdata(file, ETOCOffset, filetable):
    file.seek(ETOCOffset)
    
    magic = file.read(4)
    if magic != ETOCCODE:
        raise Exception(f"{magic} get instead of {ETOCCODE}, no ETOC data")
        
    ETOC_packet, ETOC_size, isUTFencrypted = readUTFData(file)
    
    ETOC_entry = filetable.get_file_by_name("ETOC_HDR")
    ETOC_entry.Encrypted = isUTFencrypted
    ETOC_entry.FileSize = ETOC_size
    
    files = UTF(ETOC_packet)
    
    fileEntries = filetable.get_all_FILE()
    for i in range(len(fileEntries)):
        fileEntries[i].DirName = files.get_Column_Data(i, "LocalDir")

def readITOCdata(file, ITOCOffset, ContentOffset, Align, filetable):
    
    file.seek(ITOCOffset)
    
    magic = file.read(4)
    if magic != ITOCCODE:
        raise Exception(f"{magic} get instead of {ITOCCODE}, no ITOC data")
        
    ITOC_packet, ITOC_size, isUTFencrypted = readUTFData(file)
    
    ITOC_entry = filetable.get_file_by_name("ITOC_HDR")
    ITOC_entry.Encrypted = isUTFencrypted
    ITOC_entry.FileSize = ITOC_size
    
    files = UTF(ITOC_packet)
    
    DataL = files.get_Column_Data(0, "DataL")
    DataLPos = files.get_Column_Position(0, "DataL")
    
    DataH = files.get_Column_Data(0, "DataH")
    DataHPos = files.get_Column_Position(0, "DataH")
    
    IDs = []
    
    SizeTable = {}
    SizeTypeTable = {}
    SizePosTable = {}
    
    CSizeTable = {}
    CSizeTypeTable = {}
    CSizePosTable = {}
    
    if DataL is not None:
        
        utfDataL = UTF(DataL)
        
        for i in range(utfDataL.nb_rows):
            
            ID = utfDataL.get_Column_Data(i, "ID")
            SizeTable[ID] = utfDataL.get_Column_Data(i, "FileSize")
            SizePosTable[ID] = utfDataL.get_Column_Position(i, "FileSize") + DataLPos
            SizeTypeTable[ID] = utfDataL.get_Column_Type(i, "FileSize")
            
            if utfDataL.get_Column_Data(i, "ExtractSize") is not None:
                CSizeTable[ID] = utfDataL.get_Column_Data(i, "ExtractSize")
                CSizePosTable[ID] = utfDataL.get_Column_Position(i, "ExtractSize") + DataLPos
                CSizeTypeTable[ID] = utfDataL.get_Column_Type(i, "ExtractSize")
                
            IDs.append(ID)
            
    if DataH is not None:
        
        utfDataH = UTF(DataH)
        
        for i in range(utfDataH.nb_rows):
            
            ID = utfDataH.get_Column_Data(i, "ID")
            SizeTable[ID] = utfDataH.get_Column_Data(i, "FileSize")
            SizePosTable[ID] = utfDataH.get_Column_Position(i, "FileSize") + DataHPos
            SizeTypeTable[ID] = utfDataH.get_Column_Type(i, "FileSize")
            
            if utfDataH.get_Column_Data(i, "ExtractSize") is not None:
                CSizeTable[ID] = utfDataH.get_Column_Data(i, "ExtractSize")
                CSizePosTable[ID] = utfDataH.get_Column_Position(i, "ExtractSize") + DataHPos
                CSizeTypeTable[ID] = utfDataH.get_Column_Type(i, "ExtractSize")
                
            IDs.append(ID)
            
    IDs.sort()
    
    baseOffset = ContentOffset
    
    for ID in IDs:
        
        temp = FileEntry()
        temp.TOCName = "ITOC"
        temp.FileName = str(ID).zfill(4) # I do a padding with 4 zeros
        temp.FileType = "FILE"
        temp.FileOffset = baseOffset
        temp.ID = ID
        
        value = SizeTable[ID]
        temp.FileSize = value
        temp.FileSizePos = SizePosTable[ID]
        temp.FileSizeType = SizeTypeTable[ID]
        if ID in CSizeTable:
            temp.ExtractSize = CSizeTable[ID]
            temp.ExtractSizePos = CSizePosTable[ID]
            temp.ExtractSizeType = CSizeTypeTable[ID]
            
        filetable.append(temp)
        
        if (value % Align) == 0:
            baseOffset += value
        else:
            baseOffset += value - (Align - (value % Align))

# What does this function ?!
def readGTOCdata(file, GTOCOffset, filetable):
    
    file.seek(GTOCOffset)
    
    magic = file.read(4)
    if magic != GTOCCODE:
        raise Exception(f"{magic} get instead of {GTOCCODE}, no GTOC data")
        
    # Skip header
    file.read(0xc)
    
def decrompressCRILAYLA(chunk):
    
    result = bytearray()
    
    uncompressed_size = int.from_bytes(chunk[8:12], ENDIAN)
    uncompressed_header_offset = int.from_bytes(chunk[12:16], ENDIAN)
    
    result += chunk[uncompressed_header_offset + 0x10 : uncompressed_header_offset + 0x110]
    result += bytes(uncompressed_size) # I add some 0
    
    ref_values = {}
    ref_values["input_offset"] = len(chunk) - 0x100 - 1
    ref_values["bit_pool"] = 0
    ref_values["bits_left"] = 0
    
    output_end = 0x100 + uncompressed_size - 1
    bytes_output = 0
    vle_lens = [2, 3, 5, 8]
    
    while bytes_output < uncompressed_size:
        
        if get_next_bits(chunk, ref_values, 1) > 0:
            backreference_offset = output_end - bytes_output + get_next_bits(chunk, ref_values, 13) + 3
            backreference_length = 3
            
            didBreak = False
            for vle_level in range(len(vle_lens)):
                
                this_level = get_next_bits(chunk, ref_values, vle_lens[vle_level])
                backreference_length += this_level
                
                if this_level != ((1 << vle_lens[vle_level]) - 1):
                    didBreak = True
                    break
                
            if not didBreak:
                
                this_level = 255
                
                while this_level == 255:
                    this_level = get_next_bits(chunk, ref_values, 8)
                    backreference_length += this_level
                    
            for i in range(backreference_length):
                result[output_end - bytes_output] = result[backreference_offset]
                backreference_offset -= 1
                bytes_output += 1
        
        else:
            # verbatim byte
            result[output_end - bytes_output] = get_next_bits(chunk, ref_values, 8)
            bytes_output += 1
    
    return bytes(result)

def get_next_bits(input, ref_values, bit_count):
    
    out_bits = 0
    
    num_bits_produced = 0
    
    while num_bits_produced < bit_count:
        
        if ref_values["bits_left"] == 0:
            ref_values["bit_pool"] = input[ref_values["input_offset"]]
            ref_values["bits_left"] = 8
            ref_values["input_offset"] -= 1
            
        bits_this_round = min(bit_count - num_bits_produced, ref_values["bits_left"])
        
        out_bits <<= bits_this_round
        out_bits |= (ref_values["bit_pool"] >> (ref_values["bits_left"] - bits_this_round)) & ((1 << bits_this_round) - 1)
        
        ref_values["bits_left"] -= bits_this_round
        
        num_bits_produced += bits_this_round
    
    return out_bits