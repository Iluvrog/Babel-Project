from translation_server import translate_sentence

from abc import ABC, abstractmethod

class TranslatorAbs(ABC):
    
    def __init__(self):
        self.file_name = ""
        self.encoding = "utf-8"
        
        self.hash = "0"
        self.dir_temp = ""
        self.parts = []
    
    @abstractmethod
    def set_file(self, file_name, encoding = "utf-8"):
        pass
        
    @abstractmethod
    def translate(self, input_dir = None, output_dir = None):
        pass
    
    def translate_sentence(self, sentence):
        trad = translate_sentence(sentence)
        return trad