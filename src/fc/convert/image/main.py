try:
    import standart
    import XTX
except ImportError:
    from . import standart, XTX
 

from argparse import ArgumentParser
from os.path import splitext
    
STANDART_FORMAT = ["JPEG", "JPG", "PNG"]

def get_function(format, read):
    
    format = format.upper()
    
    if format in STANDART_FORMAT:
        module = standart
        if not read:
            return lambda path_out, im: module.write(path_out, im, format)
    else:
        match format:
            case "XTX":
                module = XTX
            case _:
                raise Exception(f"Format {format} not supported")
                
    if read:
        return module.read
    return module.write

def convert(path_in, format_in, path_out, format_out):
    
    read = get_function(format_in, True)
    write = get_function(format_out, False)
    
    im = read(path_in)
    write(path_out, im)
    
def parse():
    parser = ArgumentParser(prog = "Convert Image",
                            description="Convert image to another format",
                            epilog="Supported format: JPEG PNG")
    
    parser.add_argument("input_path",
                        help="The path to the input image")
    parser.add_argument("output_path",
                        help="The path to the output image")
    parser.add_argument("--input_format",
                        help="The format of the input image (optionnal)")
    parser.add_argument("--output_format",
                        help="The format of the output image (optionnal)")
    
    return parser.parse_args()
    
def main():
    
    args = parse()
    
    input_path = args.input_path
    output_path = args.output_path
    
    input_format = args.input_format if args.input_format else splitext(input_path)[-1][1:]
    output_format = args.output_format if args.output_format else splitext(output_path)[-1][1:]
    
    convert(input_path, input_format, output_path, output_format)
    
if __name__ == "__main__":
    main()