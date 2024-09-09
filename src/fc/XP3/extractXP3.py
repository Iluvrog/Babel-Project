#!/usr/bin/env python

# KiriKiri .XP3 archive extraction tool
#
#   Extracts an .XP3 archive to a directory of files, including any
# subdirectory structure.  Does aggressive error-checking, so some
# assertions may have to be disabled with nonstandard XP3 files.
#
# Last modified 2006-07-08, Edward Keyes, ed-at-insani-dot-org
#
# Later (20/02/2016) adapted to NekoPara Vol. 0/1/2 Steam/non-Steam
# EDIT (28/02/2016): As of now it should handle everything the old script
# supported and more, with the exception of the exotic Fate encryption
# the old one used to support.
# Good news though: Fate Realta Nua support seems flawless!
# EDIT (25/09/2016): Well, NOW Fate Realta Nua support is flawless.
# Refactored part of the code to support files beginning with and EXE
# stub. Also switched the variable names to camel case. I like it much
# more that lowercase. This is gonna look horrible in the GIT commit lol
# -SmilingWolf

#
# 2024/03/13 rewrited in python3, Iluvrog
#

import os, struct, zlib, hashlib
from array import array
from io import BytesIO
from argparse import ArgumentParser

try:
    from .insani import *
except ImportError:
    from insani import *
    
try:
    from .keys import getEncParams
except ImportError:
    from keys import getEncParams


def ParseExeHeader(InFile):
    # Position ourselves at the beginning of the e_lfanew field
    # of the DOS Header. This field tells us where the PE
    # Header starts.
    InFile.seek(0x3C, 0)
    e_lfanew = struct.unpack('<I', InFile.read(4))[0]
    InFile.seek(e_lfanew, 0)
    # Just verify we're where we want to be with a quick assert.
    PESignature = InFile.read(4)
    assert (PESignature == 'PE\x00\x00')
    # Then proceed forward and read the NumberOfSections field.
    InFile.seek(2, 1)
    NumberOfSections = struct.unpack('<H', InFile.read(2))[0]
    # Skip some fields, then read the SizeOfOptionalHeaders.
    InFile.seek(12, 1)
    SizeOfOptionalHeaders = struct.unpack('<H', InFile.read(2))[0]
    # Skip one more field, then jump past the OptionalHeaders.
    InFile.seek(2, 1)
    InFile.seek(SizeOfOptionalHeaders, 1)
    # Skip all the sections but the last. We need its RawSize and
    # RawAddress to know where the exe stub ends.
    InFile.seek(40 * (NumberOfSections - 1), 1)
    InFile.seek(16, 1)
    RawSize = struct.unpack('<I', InFile.read(4))[0]
    RawAddress = struct.unpack('<I', InFile.read(4))[0]
    return RawAddress + RawSize

def DefineEncParams(Encryption):
    return getEncParams(Encryption)

def ProperLower(String):
    for i in range(0, len(String), 2):
        if ord(String[i]) >= 0x41 and ord(String[i]) <= 0x5A and ord(String[i + 1]) == 0:
            String = String[:i] + chr(ord(String[i]) + 0x20) + String[i + 1:]
    return String

# Reads a file Entry and creates a Data structure from it.
def ReadNekoEntry(InFile):
    Result = {}
    NekoLen = read_unsigned(InFile, LONG_LENGTH)
    CurPos = InFile.tell()
    Result['NekoKey'] = read_unsigned(InFile)
    FilenameLength = read_unsigned(InFile, SHORT_LENGTH)
    FilePath = array('B')
    for i in range(FilenameLength * 2):
        FilePath.append(read_unsigned(InFile, BYTE_LENGTH))
    Result['FilePath'] = FilePath.tostring()
    InFile.seek(CurPos + NekoLen, 0)
    MD5Name = hashlib.md5()
    MD5Name.update(ProperLower(Result['FilePath']))
    MD5Name = MD5Name.hexdigest()
    MD5Name = MD5Name.encode('utf-16le')
    Result['FakeFilePath'] = MD5Name
    return Result

def ReadFileEntry(InFile, HeaderOffset):
    fTime = 0
    fAdlr = 0
    fSegm = 0
    fInfo = 0
    Result = {}
    OrigPos = InFile.tell()
    Entrylength = read_unsigned(InFile, LONG_LENGTH)
    while InFile.tell() < OrigPos + Entrylength:
        SectName = InFile.read(4)
        if SectName == b'time':
            InFile.seek(16, 1)
            fTime = 1
        elif SectName == b'adlr':
            assert read_unsigned(InFile, LONG_LENGTH) == 4
            Result['Adler'] = read_unsigned(InFile)
            fAdlr = 1
        elif SectName == b'segm':
            NumSegments = read_unsigned(InFile, LONG_LENGTH) // 28  # 28 bytes per seg.
            Result['Segments'] = []
            CompSize = OrigSize = 0
            for i in range(NumSegments):
                segment = {}
                segment['Compressed'] = read_unsigned(InFile)
                segment['Offset'] = read_unsigned(InFile, LONG_LENGTH) + HeaderOffset
                segment['OrigSize'] = read_unsigned(InFile, LONG_LENGTH)
                segment['CompSize'] = read_unsigned(InFile, LONG_LENGTH)
                CompSize += segment['CompSize']
                OrigSize += segment['OrigSize']
                Result['Segments'].append(segment)
            fSegm = 1
        elif SectName == b'info':
            InfoLength = read_unsigned(InFile, LONG_LENGTH)
            CurPos = InFile.tell()
            Result['Encrypted'] = read_unsigned(InFile)
            Result['OrigSize'] = read_unsigned(InFile, LONG_LENGTH)
            Result['CompSize'] = read_unsigned(InFile, LONG_LENGTH)
            FilenameLength = read_unsigned(InFile, SHORT_LENGTH)
            Result['FakeFilePath'] = u''
            for i in range(FilenameLength):
                Result['FakeFilePath'] += chr(read_unsigned(InFile, SHORT_LENGTH))
            Result['FakeFilePath'] = Result['FakeFilePath'].encode('utf-16le')
            InFile.seek(CurPos + InfoLength, 0)
            fInfo = 1
    assert fAdlr == 1 and fSegm == 1 and fInfo == 1
#   assert InfoLength == (FilenameLength + 1) * 2 + 22
#   assert CompSize == Result['CompSize']
#   assert OrigSize == Result['OrigSize']
#   assert Entrylength == FilenameLength*2+NumSegments*28+62
    return Result

# Performs standard types of XP3 decryption on a file.
def NekoDecrypt(OutFile, MasterKey, BakKey0, BakKey1, FirstXor, FileKey):
    XorKey = FileKey ^ MasterKey
    NewKey0 = XorKey & 0xFF
    NewKey1 = XorKey >> 24 ^ XorKey >> 16 ^ XorKey >> 8 ^ XorKey
    NewKey1 = NewKey1 & 0xFF
    if FirstXor == 1 and NewKey0 == 0:
        NewKey0 = BakKey0
    if NewKey1 == 0:
        NewKey1 = BakKey1
    OutFile.seek(0)
    Data = array('B', OutFile.read())
    if FirstXor == 1:
        Data[0] ^= NewKey0
    for i in range(len(Data)):
        Data[i] ^= NewKey1
    OutFile.seek(0)
    OutFile.write(Data.tostring())

def extract(infile, DirName, Encryption = 'none'):
    ArcSign = b'XP3\x0D\x0A\x20\x0A\x1A\x8B\x67\x01'
    
    InFile = open(infile, 'rb')
    FileSize = os.stat(infile).st_size
    
    MasterKey, BakKey0, BakKey1, FirstXor = DefineEncParams(Encryption)
    
    Header = InFile.read(3)
    if (Header == 'MZP'):
        ArchiveStart = ParseExeHeader(InFile)
    else:
        ArchiveStart = 0
    
    InFile.seek(ArchiveStart, 0)
    LastSignature = InFile.read(4096).rfind(ArcSign)
    HeaderOffset = LastSignature + ArchiveStart
    
    InFile.seek(HeaderOffset, 0)
    InFile.seek(len(ArcSign), 1)
    IndexOffset = struct.unpack('<q', InFile.read(8))[0]
    
    InFile.seek(HeaderOffset, 0)
    InFile.seek(IndexOffset, 1)
    # To keep compatibility with legacy xp3 files we check if the current byte is 0x80
    # This is a constant defined inside KiriKiriZ itself.
    IndexContinue = InFile.read(1)
    InFile.seek(-1, 1)
    if IndexContinue == b'\x80':
        InFile.seek(9, 1)
        IndexOffset = HeaderOffset + struct.unpack('<q', InFile.read(8))[0]
        InFile.seek(IndexOffset, 0)
    
    assert_string(InFile, '\x01', ERROR_WARNING)
    CompSize = read_unsigned(InFile, LONG_LENGTH)
    OrigSize = read_unsigned(InFile, LONG_LENGTH)
    assert IndexOffset + CompSize + 17 == FileSize
    
    Uncompressed = zlib.decompress(InFile.read(CompSize))
    assert len(Uncompressed) == OrigSize
    IndexBuffer = BytesIO(Uncompressed)
    
    NekoArray = []
    FileArray = []
    while IndexBuffer.tell() < OrigSize:
        SectName = IndexBuffer.read(4)
        if SectName == b'neko' or SectName == b'eliF':
            Entry = ReadNekoEntry(IndexBuffer)
            NekoArray.append(Entry)
        elif SectName == b'File':
            Entry = ReadFileEntry(IndexBuffer, HeaderOffset)
            FileArray.append(Entry)
    
    for i in range(len(FileArray)):
        j = 0
        NekoFound = 0
        while j < len(NekoArray) and NekoFound == 0:
            FileMD5 = FileArray[i]['FakeFilePath']
            NekoMD5 = NekoArray[j]['FakeFilePath']
            if FileMD5 == NekoMD5:
                FileArray[i]['NekoKey'] = NekoArray[j]['NekoKey']
                FileArray[i]['FilePath'] = NekoArray[j]['FilePath']
                NekoFound = 1
            else:
                j += 1
        if FileArray[i]['Encrypted'] != 0 and not 'FilePath' in FileArray[i]:
            # for some reason the Encrypted byte was set, but the section with the infos
            # for the decryption is missing. Extract the file raw and avoid raising exceptions
            FileArray[i]['Encrypted'] = 0
        if FileArray[i]['Encrypted'] == 0:
            FileArray[i]['FilePath'] = FileArray[i]['FakeFilePath']
        if len(FileArray[i]['FilePath']) > 0x100:
            # if the name is that long it most likely is the copyright infringiment notice.
            # this is not the best solution actually , but for the love of god, this is a python script!
            # if you have any problem you can use notepad and edit away a couple lines, the script
            # can already handle the 'can't write a file with such an effing long name' situation gracefully.
            FileArray[i]['FilePath'] = 'do_not_copy.txt'.encode('utf-16le')
    
        EncDecPath = FileArray[i]['FilePath'].decode('utf-16le').encode('utf-8')
        print('Extracting %s (%d -> %d bytes)' % (EncDecPath.decode(errors = "ignore"), FileArray[i]['CompSize'], FileArray[i]['OrigSize']))
        # Paths inside the XP3 use forward slashes as separators
        PathComponents = EncDecPath.split(b'/')
        FilePath = DirName
        for Elem in PathComponents:
            if not os.path.isdir(FilePath):  # Create directory if it's not there
                os.mkdir(FilePath)  # Won't do this for the final filename
            FilePath = os.path.join(FilePath, Elem.decode())
    
        OutBuffer = BytesIO()
        # Initialize checksum for incremental updates
        Adler = zlib.adler32(b'')
        for segment in FileArray[i]['Segments']:
            InFile.seek(segment['Offset'])
            if segment['Compressed']:
                Data = zlib.decompress(InFile.read(segment['CompSize']))
            else:
                Data = InFile.read(segment['CompSize'])
            assert len(Data) == segment['OrigSize']
            OutBuffer.write(Data)
        if FileArray[i]['Encrypted'] and Encryption != 'none':
            NekoDecrypt(OutBuffer, MasterKey, BakKey0, BakKey1, FirstXor, FileArray[i]['NekoKey'])
        elif FileArray[i]['Encrypted'] and Encryption == 'none':
            print('The file is encrypted, but no encryption type was specified. Dumping it raw...')
        # With NekoPara the Adler32 has to be calculated on the decrypted file
        Adler = zlib.adler32(OutBuffer.getvalue(), Adler)
        if Adler + 0x0100000000 & 0x00FFFFFFFF != FileArray[i]['Adler']:
            # Convert to unsigned 32-bit integer
            print('Checksum error, but continuing...')
        try:
            # Why worry about exceptions?  There's a known problem with archives
            # including a "do not copy this!" file with a huge filename that many
            # filesystems will choke on.  We still want to continue if we hit that.
            OutFile = open(FilePath, 'wb')
            OutFile.write(OutBuffer.getvalue())
            OutFile.close()
        except IOError:
            print('Problems writing %s, but continuing...' % FilePath)
    
    IndexBuffer.close()
    InFile.close()

def parse():
    parser = ArgumentParser(description = "Extract XP3")
    parser.add_argument("infile", type = str)
    parser.add_argument("outdir", type = str)
    parser.add_argument("encryption", type = str, default = 'none', nargs = '?')
    
    return parser.parse_args()

def main():
    args = parse()
    extract(args.infile, args.outdir, args.encryption)

if __name__ == "__main__":
    main()