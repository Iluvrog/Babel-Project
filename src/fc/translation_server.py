from .parameter import get
from .Cache import Cache

from os import system
from requests import post
from time import time



time_cache = time()
cache = Cache()

TRANSLATE_VOID_LIST = ["", " ", "\n", "\n\r", "???", "...", "?!"]
TRANSLATE_SPLIT_LIST = ["\n\r", "\n", "\u3000"]

def open_server(new_terminal = True):
    path = '"' + get("Sugoi", "path") + "/Code/backendServer/Program-Backend/Sugoi-Japanese-Translator/" + '"'
    
    match type_sugoi:= get("Sugoi", "type") :
        case "Offline":
            server = "activateOffline.bat"
        case "OfflineDebug":
            server = "activateOfflineDebug.bat"
        case "Premium":
            server = "activatePremium.bat"
        case "DeepL":
            server = "activateDeepL.bat"
        case "Papago":
            server = "activatePapago.bat"
        case _:
            allowed_type = "{Offline | OfflineDebug | Premium | DeepL | Papago}"
            exit(f"type Sugoi must be {allowed_type} not {type_sugoi}")
    
    if new_terminal:
        command = "cd " + path + " && start " + '"' + server + '"'
    else:
        command = "cd " + path + " && " + '"' + server + '"'
        
    #print(command)
    system(command)
    
def close_server():
    request = {"content": "close server", "message": "close server"}
    post("http://" + get("server", "name") + ":" + str(get("server", "port")), json=request)


###############################################################################


def create_request(sentence):
    match name_server := get("server", "name"):
        case "Sugoi":
            return {"content": sentence, "message": "translate this text"}
        case _:
            allowed_server = "{Sugoi}"
            exit(f"name of the server must be {allowed_server} not {name_server}")
            
def extract_response(response):
    match name_server := get("server", "name"):
        case "Sugoi":
            return response[1:-1]
        case _:
            allowed_server = "{Sugoi}"
            exit(f"name of the server must be {allowed_server} not {name_server}")

def translate_sentence(sentence):
    cache.set_language_in(get("language", "in"))
    cache.set_language_out(get("language", "out"))
    
    if cache.exist(sentence):
        return cache.get(sentence)
    
    if sentence in TRANSLATE_VOID_LIST:
        return sentence
    
    for split in TRANSLATE_SPLIT_LIST:
        if split in sentence:
            trad = translate_chunk(sentence, split)
            cache.add(sentence, trad)
            return trad
    
    request = create_request(sentence)
    try:
        server_name = get("server", "name")
        res = post(get(server_name, "address"), json=request, timeout = 30)
    except Exception as e:
        save_cache()
        raise Exception(f"Exception occurs with the connexion: {e}")
        return None
    
    if res.status_code != 200:
        save_cache()
        raise Exception(f"Get the status code {res.status_code}: {res.text}")
        return None
    
    trad = extract_response(res.text)
    cache.add(sentence, trad)
    
    if time() - 60 > time_cache:
        save_cache()
    
    return trad

def translate_chunk(sentence, split):
    chunks = sentence.split(split)
    for i in range(len(chunks)):
        trad_i = translate_sentence(chunks[i])
        if trad_i is None:
            exit(f"Problem with the translation of '{chunks[i]}': get None")
        chunks[i] = trad_i
        
    return split.join(chunks)

def save_cache():
    global time_cache
    time_cache = time()
    cache.write()

if __name__ == "__main__":
    open_server(False)