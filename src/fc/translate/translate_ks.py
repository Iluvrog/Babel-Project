from fc.translation_server import translate_sentence



def translate_ks(inpath, outpath):
    
    infile = open(inpath, 'r', encoding = "shift-jis", errors = 'ignore')
    outfile = open(outpath, 'w', encoding = "shift-jis", errors = 'ignore')
    
    text = infile.read()
    
    text = translate_text(text)
    
    outfile.write(text)
    
    infile.close()
    outfile.close()
    
def split_sentence(sentence, size_max = 45):
    separator = "[r]"
    words = sentence.split(" ")
    lines = []
    
    line = ""
    for word in words:
        if len(line) + len(word) < size_max:
            line += word + " "
        else:
            line = line[:-1] + separator
            lines.append(line)
            line = word + " "
            
    if line != "":
        lines.append(line[:-1])
        
    for i in range(2, len(lines)-1, 3):
        lines[i] = lines[i].replace("[r]", "[p][cm]")
    
    return "\n".join(lines)
    

def translate_text(text):
    
    lines = text.split("\n")
    
    trad_lines = []
    
    start_skip = [";", "*"]
    
    isInMacro = 0
    isIf = False
    isScript = False
    
    actual_line = ""
    
    actual_macro = ""
    
    for line in lines:
        
        if isIf:
            trad_lines.append(line)
            if line == "@endif" or line == "[endif]":
                isIf = False
            continue
        
        if isScript:
            trad_lines.append(line)
            if line == "@endscript" or line == "[endscript]":
                isScript = False
            continue
        
        if len(line) == 0:
            trad_lines.append(line)
            continue
        
        if line[0] in start_skip:
            trad_lines.append(line)
            continue
        
        if line[0] == "@":
            if actual_line != "":
                trad_lines.append(trad_sentence(actual_line))
                actual_line = ""
            trad_lines.append(trad_macro(line))
            if line.startswith("@iscript"):
                isScript = True
            if line.startswith("@if "):
                isIf = True
            continue
        
        for i in range(len(line)):
            
            char = line[i]
            
            if not isInMacro and char == "[" and (i == len(line)-1 or line[i+1] != "["):
                
                isInMacro += 1
                
                actual_macro = "["
                continue
            
            if isInMacro:
                actual_macro += char
                
                if char == "[":
                    isInMacro += 1
                
                if char == "]":
                    
                    isInMacro -= 1
                    
                    if not isInMacro:
                        if actual_macro == "[r]":
                            actual_macro = ""
                            if actual_line != "":
                                actual_line += " "
                            continue
                        
                        if actual_line != "":
                            
                            trad_lines.append(trad_sentence(actual_line))
                            actual_line = ""
                          
                        trad_lines.append(trad_macro(actual_macro))
                        
                        if actual_macro.startswith("[if "):
                            isIf = True
                        if actual_macro == "[iscript]":
                            isScript = True
                            
                        actual_macro = ""
                        continue
            else: 
                
                actual_line += char
               
        if actual_line != "" and actual_line[-1] != " ":
            actual_line += " "
            
        if actual_line != "":
            trad_lines += trad_sentence(actual_line)
            actual_line = ""

    return "\n".join(trad_lines)

def trad_macro(macro):
    
    # If I create a maco
    create_macro = "macro "
    if macro[1:1+len(create_macro)] == create_macro:
        return macro
    
    # If I don't have a name arg in macro
    name_args = [" name ", " name="]
    pos_name = -1
    
    for name in name_args:
        pos_name = macro.find(name)
        if pos_name != -1:
            break
      
    if pos_name == -1:
        return macro
    
    # If I have a name arg
    equal_pos = macro[pos_name:].find("=")
    if equal_pos == -1:
        return macro
    equal_pos += pos_name
    
    trad_macro = macro[:equal_pos+1]
    macro = macro[equal_pos+1:]
    name = ""
    
    while macro.startswith(" "):
        trad_macro += " "
        macro = macro[1:]
      
    end_name_char = " "
    if macro.startswith("'") or macro.startswith('"'):
        trad_macro += macro[0]
        end_name_char = macro[0]
        macro = macro[1:]
        
    end_name_pos = macro.find(end_name_char)
    
    name = macro[:end_name_pos]
    macro = macro[end_name_pos:]
    
    if name != "%name":
        trad_macro += translate_sentence(name)
    else:
        trad_macro += name
    trad_macro += macro
    
    return trad_macro

def trad_sentence(line):
    
    line = line.replace("[r]", " ")
    line = line.replace("\n", " ")
    
    while "  " in line:
        line = line.replace("  ", " ")
        
    line = translate_sentence(line)
    
    return split_sentence(line)