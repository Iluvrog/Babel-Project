from translation_server import translate_sentence

from abc import ABC, abstractmethod

class HTMLObject(ABC):
    
    def __init__(self, element):
        self.element = element
        self.translate_cache = None
        self.parts = []
        self._cut()
        
    def _cut(self):
        return
    
    def get_translation(self):
        if not self.translate_cache:
            self.translate_cache = self._make_translation()
        return self.translate_cache
    
    @abstractmethod
    def _make_translation(self):
        pass
    

class HTMLFile(HTMLObject):
     
    #Can have probleme with some comment    
    def _cut(self):
        start = self.element.find("<HTML>")
        end = self.element.rfind("</HTML>")
        self.parts.append(HTMLOther(self.element[:start]))
        self.parts.append(HTMLCore(self.element[start+6:end]))
        self.parts.append(HTMLOther(self.element[end+7:]))
        
    def _make_translation(self):
        res = ""
        
        for part in self.parts:
            res += part.get_translation()
            
        return res
        
class HTMLComment(HTMLObject):
        
    def _make_translation(self):
        return "<!--" + self.element + "-->"
    
class HTMLCore(HTMLObject):
     
    #Can have probleme with some comment    
    def _cut(self):
        startH = self.element.find("<HEAD>")
        endH = self.element.rfind("</HEAD>")
        
        self.parts.append(HTMLOther(self.element[:startH]))
        self.parts.append(HTMLHead(self.element[startH+6:endH]))
        
        
        self.parts.append(HTMLBody(self.element[endH+7:]))
        
    def _make_translation(self):
        res = "<HTML>"
        
        for part in self.parts:
            res += part.get_translation()
            
        res += "</HTML>"
            
        return res

# For now        
class HTMLHead(HTMLObject):
    
    def _make_translation(self):
        return "<HEAD>" + self.element + "</HEAD>"

# For now
class HTMLBody(HTMLObject):
    
    def _cut(self):
        lines = self.element.split("\n")
        if len(lines) == 0:
            return
        
        for i in range(len(lines)):
            line = lines[i]
            if i != len(lines) -1:
                line += "\n"
                
            elements = line.split("<BR>")
            for j in range(len(elements)):
                if j != 0:
                    self.parts.append(HTMLBR())
                    
                element = elements[j]
                if element == "" or element.startswith("<") or element.startswith("\n"):
                    self.parts.append(HTMLOther(element))
                else:
                    self.parts.append(HTMLSentence(element))
    
    def _make_translation(self):
        res = ""
        
        for part in self.parts:
            res += part.get_translation()
            
        return res
    
class HTMLBR(HTMLObject):
    
    def __init__(self):
        super().__init__("")
    
    def _make_translation(self):
        return "<BR>"
    
class HTMLSentence(HTMLObject):
    
    def _make_translation(self):
        trad = translate_sentence(self.element)
        if trad is None:
            exit("Problem translation, check the server")
        return trad
    
class HTMLOther(HTMLObject):
    
    def _make_translation(self):
        return self.element