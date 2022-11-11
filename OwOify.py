from TextToOwO.owo import text_to_owo as owo
from os import listdir
from os.path import isfile, join
import os

onlyfiles = [f for f in listdir("./Files") if isfile(join("./Files", f))]
here = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists('OwO-out/'):
        try:
            os.makedirs('OwO-out/')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

def owoIfy(FileName, here):
    filename = os.path.join(here, 'Files/' + FileName)
    output = os.path.join(here, 'OwO-out/' + FileName)
    print("OwOing " + FileName)
    #with open("Files/" + FileName + ".txt", "r", encoding='utf-8-sig') as f:
    with open(filename, "r", encoding='utf-8-sig') as f:
        text = f.read()
        f.close()
    #split file into lines
    lines = text.splitlines()
    
    for i in range(len(lines)):
        lines[i] = owo(lines[i])
    #print(lines)
    
    # reassemble lines into a single text file
    for i in range(len(lines)):
        lines[i] = lines[i] + "\n"
    text = "".join(lines)
    try:
        with open(output, "w", encoding='utf-8-sig') as f:
            f.write(text)
            f.close()
    except:
        print("Error OwOing " + FileName)
        pass

for i in range(len(onlyfiles)):
    owoIfy(onlyfiles[i], here)
#print(onlyfiles)