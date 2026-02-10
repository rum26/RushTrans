from deep_translator.exceptions import RequestError, TooManyRequests
from requests.exceptions import ConnectionError, Timeout
from deep_translator import GoogleTranslator
from win32com.client import Dispatch
import tkinter as tk
import pyperclip
import requests
import keyboard
import time
import json
import sys
import os


last_copy_time = 0
current_label = None
copy_handler = None


def show_start(text1, text2):
    # Создаем временное окно уведомления
    notify = tk.Tk()
    notify.overrideredirect(True)
    notify.attributes('-alpha', 1)
    notify.attributes('-topmost', True)
    x = (notify.winfo_screenwidth() - 300) // 2
    notify.geometry(f"300x80+{x}+100")
    notify.configure(bg='#2d5a27')
    title = tk.Label(notify, text=text1,
                     font=("Segoe UI", 12, "bold"),
                     bg='#2d5a27', fg='white')
    title.pack(pady=8)
    msg = tk.Label(notify, text=text2,
                   font=("Segoe UI", 9),
                   bg='#2d5a27', fg='white',
                   justify="center")
    msg.pack(pady=(0, 10))

    def fade_out():
        alpha = 0.9

        def step():
            nonlocal alpha
            alpha -= 0.05
            if alpha > 0:
                notify.attributes('-alpha', alpha)
                notify.after(60, step)
            else:
                notify.destroy()

        step()

    notify.after(6000, fade_out)


def ensure_autostart():
    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_path = os.path.join(startup_folder, "RushTrans.pyw.lnk")
    if os.path.exists(shortcut_path):
        return
    script_path = os.path.abspath(sys.argv[0])
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = pythonw
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.WindowStyle = 7
    show_start("RushTrans добавлен в автозагрузку!", "v080226.19")
    time.sleep(3)


ensure_autostart()
patch_documents = os.path.join(os.environ["USERPROFILE"], "Documents")


if os.path.exists(f"{patch_documents}/pdict.json"):
    text_add = "Run RushTrans . . ."
    text_msg = "v080226.19"
    show_start(text_add, text_msg)
    with open(f"{patch_documents}/pdict.json", 'r', encoding='UTF-8') as fb:
        Pdict = json.load(fb)
else:
    try:
        Pdict = requests.get('https://raw.githubusercontent.com/rum26/RushTrans/refs/heads/main/pdict.json').json()
        text_add = "✓ Словарь загружен!"
        text_msg = "v080226.19"
        show_start(text_add, text_msg)
        with open(f"{patch_documents}/pdict.json", "w", encoding="UTF-8") as f:
            json.dump(Pdict, f, ensure_ascii=False, indent=2)

    except Exception as ex:
        print(ex)
        Pdict = {}
        text_add = "✓ Словарь создан!"
        text_msg = "v080226.19"
        show_start(text_add, text_msg)


def save_pdict():
    with open(f"{patch_documents}/pdict.json", "w", encoding="UTF-8") as file:
        json.dump(Pdict, file, ensure_ascii=False, indent=2)


if os.path.exists("tmp.json"):
    with open("tmp.json", 'r', encoding='UTF-8') as fb:
        data = json.load(fb)
    for wrd, trans in data.items():
        wrd = wrd.lower()
        if Pdict.get(wrd) is None:
            print(f"{wrd} : {trans}")
            Pdict[wrd] = trans
    save_pdict()
    with open("tmp.json", "w", encoding="UTF-8") as f:
        json.dump({}, f)


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
    if ',' not in answer:
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


def close_window(_):
    root.destroy()


root.overrideredirect(True)
root.attributes("-alpha", 0.1)
screen_width = root.winfo_screenwidth()
window_width = int(screen_width / 2)
x_position = int((screen_width - window_width) / 2)
root.geometry(f"{window_width}x30+{x_position}+0")
root.configure(bg="black")
bottom_line = tk.Frame(root, bg="#40E0D0", height=1)
bottom_line.pack(side="bottom", fill="x")


def update_label_text(text, clr):
    global current_label
    # Удаляем старый label если есть
    if current_label:
        current_label.destroy()

    current_label = tk.Label(
        root,
        text=text,
        bg="black",
        fg=clr,
        font=("Consolas", 16, "bold"),
        justify="center",
        anchor="center"
    )
    current_label.pack(expand=True, fill='both')
    current_label.after(6000, current_label.destroy)


def main(text):
    root.attributes("-alpha", 0.85)
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
        root.attributes("-alpha", 0.1)
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
