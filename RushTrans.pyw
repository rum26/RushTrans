import json
import os

documents = os.path.join(os.environ["USERPROFILE"], "Documents")
print(documents)

if os.path.exists(f"{documents}/pdict.json"):
    with open(f"{documents}/pdict.json", 'r', encoding='UTF-8') as fb:
        Pdict = json.load(fb)
else:
    Pdict = {}


def save_pdict():
    with open(f"{documents}/pdict.json", "w", encoding="UTF-8") as f:
        json.dump(Pdict, f, ensure_ascii=False, indent=2)
