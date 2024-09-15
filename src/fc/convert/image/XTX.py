try:
    from ImageAbs import ImageAbs
except ImportError:
    from .ImageAbs import ImageAbs


XTXMAGIC = b"xtx\0"

def read(input_path):
    
    file = open(input_path, 'rb')
    
    # Get image metadata
    
    magic = file.read(4)
    if magic != XTXMAGIC:
        header_size = int.from_bytes(magic, "little")
        if header_size > 0x1000: # Just a big value
            raise Exception(f"{input_path} doesn't seem to be an xtx file, th eheader is not {XTXMAGIC} but {magic} and the size of the header seem oo big {header_size}")
            
        file.seek(header_size)
        old_magic = magic
        magic = file.read(4)
        
        if magic != XTXMAGIC:
            raise Exception(f"The magic number must be {XTXMAGIC} but get instead {old_magic} and {magic}, not XTX file")
            
    format = int.from_bytes(file.read(1))
    file.read(3) # 8 after the start or header_size
        
    aligned_width = int.from_bytes(file.read(4), "big", signed = True)
    aligned_height = int.from_bytes(file.read(4), "big", signed = True) # 0x10 after
    if aligned_width <= 0 or aligned_height <= 0:
        raise Exception(f"aligned_widht and aligned_height must be > 0 but get instead {hex(aligned_width)} and {hex(aligned_height)}")
            
    width = int.from_bytes(file.read(4), "big") # 0x14
    height = int.from_bytes(file.read(4), "big") # 0x18
    OffsetX = int.from_bytes(file.read(4), "big", signed = True) # 0x1c
    OffsetY = int.from_bytes(file.read(4), "big", signed = True) # 0x20
        
    # Read the file depending of the format
    
    match format:
        case 0:
            output = readTex0(file, width, height, aligned_width, aligned_height)
        case 1:
            output = readTex1(file, width, height, aligned_width, aligned_height)
        case 2:
            output = readTex2(file, width, height, aligned_width, aligned_height)
        case _:
            raise Exception(f"Format of XTX image must be 0, 1 or 2, not {format}")
            
    file.close()
            
    return ImageAbs(output, width, height)
    
def readTex0(file, width, height, aligned_width, aligned_height):
    
    output_stride = width
    
    output = [(0, 0, 0, 0)] * output_stride * height
    
    total = aligned_width * aligned_height
    
    texture = file.read(total*4)
    
    src = 0
    for i in range(total):
        
        y = getY(i, aligned_width, 4)
        x = getX(i, aligned_width, 4)
        
        if y < height and x < width:
            dst = output_stride * y + x
            
            # BGRA
            output[dst] = (texture[src+1], texture[src+2], texture[src+3], texture[src])
        
        src += 4
        
    return output
    
def readTex1(file, width, height, aligned_width, aligned_height):
    raise Exception("XTX read format 1 not yet implemeted")
    
def readTex2(file, width, height, aligned_width, aligned_height):
    raise Exception("XTX read format 2 not yet implemeted")

def getY(i, width, level):
    
    v1 = (level >> 2) + (level >> 1 >> (level >> 2))
    v2 = i << v1
    v3 = (v2 & 0x3F) + ((v2 >> 2) & 0x1C0) + ((v2 >> 3) & 0x1FFFFE00)
    return ((v3 >> 4) & 1) + ((((v3 & ((level << 6) - 1) & -0x20) + ((((v2 & 0x3F) + ((v2 >> 2) & 0xC0)) & 0xF) << 1)) >> (v1 + 3)) & -2) + ((((v2 >> 10) & 2) + ((v3 >> (v1 + 6)) & 1) + (int((v3 >> (v1 + 7)) / ((width + 31) >> 5)) << 2)) << 3)

def getX(i, width, level):
    v1 = (level >> 2) + (level >> 1 >> (level >> 2))
    v2 = i << v1
    v3 = (v2 & 0x3F) + ((v2 >> 2) & 0x1C0) + ((v2 >> 3) & 0x1FFFFE00)
    return ((((level << 3) - 1) & ((v3 >> 1) ^ (v3 ^ (v3 >> 1)) & 0xF)) >> v1) + ((((((v2 >> 6) & 0xFF) + ((v3 >> (v1 + 5)) & 0xFE)) & 3) + (((v3 >> (v1 + 7)) % (((width + 31)) >> 5)) << 2)) << 3)


def write(output_path, imageAbs, format = 0):
    raise Exception("XTX.write not yet implemented")
    
def writeTex0():
    raise Exception("XTX write format 0 not yet implemeted")
    
def writeTex1():
    raise Exception("XTX write format 1 not yet implemeted")
    
def writeTex2():
    raise Exception("XTX write format 2 not yet implemeted")