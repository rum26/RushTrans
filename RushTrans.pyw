from deep_translator.exceptions import RequestError, TooManyRequests
from requests.exceptions import ConnectionError, Timeout
from deep_translator import GoogleTranslator
import tkinter as tk
import pyperclip
import keyboard
import time
import json
import os


last_copy_time = 0
current_label = None
copy_handler = None
documents = os.path.join(os.environ["USERPROFILE"], "Documents")

if os.path.exists(f"{documents}/pdict.json"):
    with open(f"{documents}/pdict.json", 'r', encoding='UTF-8') as fb:
        Pdict = json.load(fb)
else:
    Pdict = {}


def save_pdict():
    with open(f"{documents}/pdict.json", "w", encoding="UTF-8") as f:
        json.dump(Pdict, f, ensure_ascii=False, indent=2)


def translate_word_auto(word):
    try:
        # пытаемся перевести на русский
        translation = GoogleTranslator(source='auto', target='ru').translate(word)
        # если слово переведено идентично (значит, оно уже русское), переводим на английский
        if translation.lower() == word.lower():
            time.sleep(1)
            translation = GoogleTranslator(source='auto', target='en').translate(word)
            # наверное я хочу так назвать переменную
            translation = translation.lower()
        return translation
    except RequestError:
        return "❌ ошибка: RequestError"
    except TooManyRequests:
        return "❌ ошибка: TooManyRequests"
    except ConnectionError:
        return "❌ ошибка: ConnectionError"
    except Timeout:
        return "❌ ошибка: Timeout"


def text_processing(text):
    if '_' in text:
        text = text.replace('_', ' ')
    text = text.lower()

    if Pdict.get(text):
        answer = Pdict[text]
        clr = "#40E0D0"  # фраза из словаря
    else:
        answer = translate_word_auto(text)
        Pdict[text] = answer
        Pdict[answer] = text
        save_pdict()
        clr = 'yellow'  # фраза из интернета.
    answer = answer.replace(' ', '_')
    return answer, clr


def copy_and_paste(text):
    if copy_handler:
        time.sleep(0.1)
        pyperclip.copy(text)
        time.sleep(0.1)
        keyboard.send('alt+tab')
        time.sleep(0.1)
        keyboard.press_and_release('ctrl+v')


root = tk.Tk()


def close_window(event):
    root.destroy()


root.overrideredirect(True)
root.attributes("-alpha", 0.7)

screen_width = root.winfo_screenwidth()
window_width = int(screen_width / 3)
x_position = int((screen_width - window_width) / 2)
root.geometry(f"{window_width}x30+{x_position}+0")
root.configure(bg="black")


def update_label_text(text, clr):
    global current_label
    # Удаляем старый label если есть
    if current_label:
        current_label.destroy()

    # Создаем новый label с новым текстом
    current_label = tk.Label(
        root,
        text=text,
        bg="black",
        fg=clr,
        font=("Segoe UI", 18),
        justify="center",
    )
    current_label.pack(expand=True, fill='both')
    current_label.after(6000, current_label.destroy)


def main(text):
    global copy_handler
    copy_handler = True
    answer, clr = text_processing(text)
    root.attributes('-topmost', True)
    root.lift()
    update_label_text(answer, clr)
    root.bind('<Button-1>', lambda event: copy_and_paste(answer))

    def disable_copy():
        global copy_handler
        copy_handler = None
        root.attributes('-topmost', False)
        root.lower()
    root.after(6000, disable_copy)


def on_copy():
    global last_copy_time
    now = time.time()
    if now - last_copy_time < 0.5:
        text = pyperclip.paste().strip()
        if len(text.split()) > 5:
            return
        main(text)
    last_copy_time = now


keyboard.add_hotkey("ctrl+c", on_copy)


root.bind('<Button-3>', close_window)
root.mainloop()
