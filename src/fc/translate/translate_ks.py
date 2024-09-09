from fc.translation_server import translate_sentence



def translate_ks(inpath, outpath):
    
    infile = open(inpath, 'r', encoding = "shift-jis", errors = 'ignore')
    outfile = open(outpath, 'w', encoding = "shift-jis", errors = 'ignore')
    
    text = infile.read()
    
    text = case_name(text)
    text = case_link(text)
    text = case_sentence(text)
    
    text = sanitize(text)
    
    outfile.write(text)
    
    infile.close()
    outfile.close()
    
def split_sentence(sentence, call_line = "", size_max = 70):
    separator = "[r]"
    words = sentence.split(" ")
    lines = []
    
    line = ""
    for word in words:
        if len(line) < size_max:
            line += word + " "
        else:
            line = line[:-1] + separator
            lines.append(line)
            line = word + " "
            
    if line != "":
        lines.append(line[:-1])
        
    for i in range(2, len(lines)-1, 3):
        if call_line.startswith("[name"):
            lines[i] = lines[i].replace("[r]", "」[plc]\n")
        else:
            lines[i] = lines[i].replace("[r]", "[plc]\n")
        lines[i] += call_line
    
    return "\n".join(lines)
    
def case_name(raw):
    base = "[name name="
    
    new = ""
    
    while raw != "":
        if not raw.startswith(base):
            new += raw[0]
            raw = raw[1:]
            continue
        new += base
        raw = raw[len(base):]
        
        end_name = raw.find("]")
        name = raw[:end_name]
        raw = raw[end_name:]
        
        trad_name = translate_sentence(name)
        if trad_name is None:
            raise Exception("Problem translation, check the server")
        new += trad_name
    
    return new

def case_link(raw):
    base = "[link target="
    end_base = "]"
    end = "[endlink]"
    
    new = ""
    while raw != "":
        if not raw.startswith(base):
            new += raw[0]
            raw = raw[1:]
            continue
        
        find_end_base = raw.find(end_base) + len(end_base)
        new += raw[:find_end_base]
        raw = raw[find_end_base:]
        
        find_end_link = raw.find(end)
        sentence = raw[:find_end_link]
        raw = raw[find_end_link + len(end):]
        
        trad_sentence = translate_sentence(sentence)
        if trad_sentence is None:
            raise Exception("Problem translation, check the server")
        new += split_sentence(trad_sentence)
        
        new += end
        
    return new

def case_sentence(text):
    
    end_speech = "[plc]"
    
    raw_lines = text.split("\n")
    new_lines = []
    
    speech = False
    raw = ""
    call_speech = ""
    for line in raw_lines:
        if line.startswith(";"):
            new_lines.append(line)
            continue
        if speech:
            stop_line = line.startswith("[")
            if not stop_line:
                raw += line
            if end_speech in raw or stop_line:
               speech = False
               sentence = raw.replace("[r]", " ")
               sentence = sentence.replace(end_speech, "")
               translation = translate_sentence(sentence)
               if translation is None:
                   raise Exception("Problem translation, check the server")
               translation = translation.replace("[", "『")
               translation = translation.replace("]", "』")
               split = split_sentence(translation, call_speech)
               if not stop_line:
                   split += end_speech
               if split != "":
                   new_lines.append(split)
               if stop_line:
                   new_lines.append(line)
        else:
            new_lines.append(line)
            if line.startswith("[name ") or line.startswith("[x]"):
                call_speech = line
                raw = ""
                speech = True
                
    return "\n".join(new_lines)

def sanitize(text):
    text = text.replace("\2014", "-")
    
    return text