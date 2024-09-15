try:
    from ImageAbs import ImageAbs
except ImportError:
    from .ImageAbs import ImageAbs
    
from PIL import Image


MODE = "RGBA"

def read(input_path):
    im = Image.open(input_path)
    
    return ImageAbs(list(im.getdata()), *im.size)

def write(output_path, imageAbs, format):
    mode = MODE
    if format == "JPEG":
        mode = "RGB"
    
    im = Image.new(mode = mode, size = (imageAbs.width, imageAbs.height))
    
    data = imageAbs.data
    #if format == "JPEG":
    #    data = [d[:3] for d in data]
    
    im.putdata(data)
    
    
    
    im.save(fp = output_path, format = format)