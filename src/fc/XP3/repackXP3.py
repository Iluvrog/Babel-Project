#!/usr/bin/env python

# KiriKiri .XP3 archive repacking tool
#
#   Packs a directory of files into an .XP3 archive, including any
# subdirectory structure.
#
# Last modified 2006-07-08, Edward Keyes, ed-at-insani-dot-org
#
# Later (20/02/2016) adapted to NekoPara Vol. 0/1/2 Steam/non-Steam
# EDIT (28/02/2016): As of now it should handle everything the old script
# supported and more, with the exception of the exotic Fate encryption
# the old one used to support.
# Good news though: Fate Realta Nua support seems flawless!
# -SmilingWolf

#
# 2024/03/13 rewrited in python3, Iluvrog
#

import os, zlib, hashlib
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

# Writes a file entry data structure to the file.
def write_entry(outfile, entry):
    if entry['encrypted'] != 0:
        outfile.write(entry['nekoname'])
        write_unsigned(outfile, 4 + 2 + len(entry['filepath']), LONG_LENGTH)
        write_unsigned(outfile, entry['nekokey'])
        write_unsigned(outfile, len(entry['filepath']) / 2, SHORT_LENGTH)
        outfile.write(entry['filepath'])
    else:
        entry['fakefilepath'] = entry['filepath']
    outfile.write(b'File')
    write_unsigned(outfile, len(entry['fakefilepath']) + 20 + len(entry['segments']) * 28 + 62, LONG_LENGTH)
    outfile.write(b'time')
    write_unsigned(outfile, 8, LONG_LENGTH)
    write_unsigned(outfile, 0, LONG_LENGTH)
    outfile.write(b'adlr')
    write_unsigned(outfile, 4, LONG_LENGTH)
    write_unsigned(outfile, entry['adler'])
    outfile.write(b'segm')
    write_unsigned(outfile, len(entry['segments']) * 28, LONG_LENGTH)
    for segment in entry['segments']:
        write_unsigned(outfile, segment['compressed'])
        write_unsigned(outfile, segment['offset'], LONG_LENGTH)
        write_unsigned(outfile, segment['origsize'], LONG_LENGTH)
        write_unsigned(outfile, segment['compsize'], LONG_LENGTH)
    outfile.write(b'info')
    write_unsigned(outfile, len(entry['fakefilepath']) + 22, LONG_LENGTH)
    write_unsigned(outfile, entry['encrypted'])
    write_unsigned(outfile, entry['origsize'], LONG_LENGTH)
    write_unsigned(outfile, entry['compsize'], LONG_LENGTH)
    write_unsigned(outfile, len(entry['fakefilepath']) / 2, SHORT_LENGTH)
    outfile.write(entry['fakefilepath'])

# Performs standard types of XP3 encryption on a file.  This is dentical to
# the decrypt function except for the error message since it's all XOR.
def encrypt(outfile, masterkey, bakkey0, bakkey1, firstxor, filekey):
        xorkey = filekey ^ masterkey
        newkey0 = xorkey & 0xFF
        newkey1 = xorkey >> 24 ^ xorkey >> 16 ^ xorkey >> 8 ^ xorkey
        newkey1 = newkey1 & 0xFF
        if firstxor == 1 and newkey0 == 0:
            newkey0 = bakkey0
        if newkey1 == 0:
            newkey1 = bakkey1
        outfile.seek(0)
        data = array('B', outfile.read())
        if firstxor == 1:
            data[0] ^= newkey0
        for i in range(len(data)):
            data[i] ^= newkey1
        outfile.seek(0)
        outfile.write(data.tostring())

def properlower(string):
    for i in range(0, len(string), 2):
        if string[i] >= 0x41 and string[i] <= 0x5A and string[i+1] == 0x00:
            string = string[:i] + chr(string[i] + 0x20).encode() + string[i+1:]
    return string

def repack(dirname, outfile, encryption = 'none'):
    arcfile = open(outfile, 'wb')
    
    masterkey, bakkey0, bakkey1, firstxor = getEncParams(encryption)
    
    # Write header
    write_string(arcfile, b'XP3\x0D\x0A\x20\x0A\x1A\x8B\x67\x01')
    write_unsigned(arcfile, 0, LONG_LENGTH)  # Placeholder for index offset
    
    # Scan for files, write them and collect the index as we go
    indexbuffer = BytesIO()
    for (dirpath, dirs, filenames) in os.walk(dirname):
        assert dirpath.startswith(dirname)
        newpath = dirpath[len(dirname):]    # Strip off base directory
        if newpath.startswith(os.sep):      # and possible slash
            newpath = newpath[len(os.sep):]
        pathcomponents = newpath.split(os.sep)
        newpath = '/'.join(pathcomponents)  # Slashes used inside XP3
        for filename in filenames:
            entry = {}
            segment = {}
            if newpath != '':
                filepath = newpath + '/' + filename
            else:
                filepath = filename
            entry['filepath'] = filepath.encode('utf-16le')
            md5name = hashlib.md5()
            # md5name.update(filepath.lower().encode('utf-16le'))
            md5name.update(properlower(entry['filepath']))
            md5name = md5name.hexdigest()
            md5name = md5name.encode('utf-16le')
            entry['fakefilepath'] = md5name
            localfilepath = os.path.join(dirpath, filename)
            infile = open(localfilepath, 'rb')
            data = infile.read()
            infile.close()
            entry['origsize'] = segment['origsize'] = len(data)
            # Convert to unsigned 32-bit integer
            entry['adler'] = entry['nekokey']= zlib.adler32(data) + 0x0100000000 & 0x00FFFFFFFF
            if encryption != 'none':
                if encryption == 'neko_vol1' or encryption == 'neko_vol1_steam':
                    entry['nekoname'] = b'eliF'
                elif encryption == 'neko_vol0' or encryption == 'neko_vol0_steam':
                    entry['nekoname'] = b'neko'
                else:
                    entry['nekoname'] = b'unkn'
                entry['encrypted'] = 0x0080000000
                tempbuffer = BytesIO()
                tempbuffer.write(data)
                encrypt(tempbuffer, masterkey, bakkey0, bakkey1, firstxor, entry['nekokey'])
                data = tempbuffer.getvalue()
                tempbuffer.close()
            else:
                entry['encrypted'] = 0
            compressed = zlib.compress(data, 9)
            if len(compressed) < 0.95 * len(data):  # Don't store compressed if we
                segment['compressed'] = 1           # gain just a few percent from it
                data = compressed
            else:
                segment['compressed'] = 0
            entry['compsize'] = segment['compsize'] = len(data)
            segment['offset'] = arcfile.tell()
            entry['segments'] = [segment]   # Always using a list of one segment
            write_entry(indexbuffer, entry)
            print('Packing %s (%d -> %d bytes)' % \
                (entry['filepath'].decode('utf-16le'),
                 entry['origsize'], entry['compsize']))
            arcfile.write(data)
    
    # Now write the index and go back and put its offset in the header
    indexoffset = arcfile.tell()
    data = indexbuffer.getvalue()
    compressed = zlib.compress(data, 9)
    arcfile.write(b'\x01')
    write_unsigned(arcfile, len(compressed), LONG_LENGTH)
    write_unsigned(arcfile, len(data), LONG_LENGTH)
    arcfile.write(compressed)
    arcfile.seek(11)  # Length of header
    write_unsigned(arcfile, indexoffset, LONG_LENGTH)
    
    indexbuffer.close()
    arcfile.close()

def parse():
    parser = ArgumentParser(description = "Repack XP3")
    parser.add_argument("indir", type = str)
    parser.add_argument("outfile", type = str)
    parser.add_argument("encryption", type = str, default = 'none', nargs = '?')
    
    return parser.parse_args()

def main():
    args = parse()
    repack(args.indir, args.outfile, args.encryption)

if __name__ == "__main__":
    main()