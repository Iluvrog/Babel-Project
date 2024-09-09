from Translator.TranslatorAbs import TranslatorAbs
from Translator.HTMLObject import HTMLFile
from parameter import get


class TranslatorHTML(TranslatorAbs):
        
    def set_file(self, file_name, encoding = "shift_jis"):
        self.file_name = file_name
        self.encoding = encoding
        
    def set_encoding(self, encoding):
        self.encoding = encoding
        
    def translate(self, input_dir = None, output_dir = None):
        if input_dir is None:
            input_dir = get("path", "input")
        if output_dir is None:
            output_dir = get("path", "output")
            
        output_name = self.file_name.replace(input_dir, output_dir)
        
        input_file = open(self.file_name, 'r', encoding = self.encoding)
        output_file = open(output_name, 'w', encoding = self.encoding)
        
        file_text = input_file.read()
        
        file = HTMLFile(file_text)
        
        translation = file.get_translation()
        translation = self._sanitize_translation(translation)
        
        output_file.write(translation)
        
        input_file.close()
        output_file.close()
        
    def _sanitize_translation(self, translation):
        translation.replace("’", "'")
        
        return translation

            
