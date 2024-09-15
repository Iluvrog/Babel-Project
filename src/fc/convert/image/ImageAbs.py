import builtins


class ImageAbs():
    
    def __init__(self, data, width, height):
        
        self.width = width
        self.height = height
        
        self.data = self.format_data(data)
        
        if len(self.data) != self.width * self.height:
            raise Exception(f"width and height mean {self.width*self.height} pixels but data has {len(self.data)} pixels")
        
    def format_data(self, data):
        
        match type(data):
            case builtins.list | builtins.tuple:
                return [self.format_pixel(p) for p in data]
            case _:
                return [self.format_pixel(data) for _ in range(self.width*self.height)]
        
    def format_pixel(self, pixel):
        
        match type(pixel):
            case builtins.int:
                self.check_format_int_pixel(pixel)
                return (pixel, pixel, pixel, 255)
        
            case builtins.float:
                return self.format_pixel(int(pixel*255))
        
            case builtins.list | builtins.tuple:
                
                match len(pixel):
                    case 1:
                        return self.format_pixel(pixel[0])
                    
                    case 3 | 4:
                        res = tuple()
                        
                        for i in range(len(pixel)):
                            c = pixel[i]
                            
                            match type(c):
                                case builtins.int:
                                    self.check_format_int_pixel(c)
                                    res += (c,)
                                case builtins.float:
                                    c = int(c*255)
                                    self.check_format_int_pixel(c)
                                    res += (c,)
                                case _:
                                    raise Exception(f"type inside {type(pixel)} pixel must be nt or float, not {type(c)}")
                                    
                        if len(res) == 3:
                            res += (255,)
                            
                        return res
                    
                    case _:
                        raise Exception(f"{type(pixel)} number of elements must be 1, 3 or 4, not {len(pixel)}")
            
            case _:
                raise Exception(f"Type of ImageAbs data pixel must be int, float, list or tuple, not {type(pixel)}")
                
    def check_format_int_pixel(self, value):
        if 255 < value < 0:
            raise Exception(f"int in pixel value must be between 0 and 255, not {value}")