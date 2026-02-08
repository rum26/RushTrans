import tkinter as tk
import ctypes
from ctypes import wintypes

# ======================
# Windows acrylic blur
# ======================

def enable_blur(hwnd):
    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", ctypes.c_int),
            ("AccentFlags", ctypes.c_int),
            ("GradientColor", ctypes.c_int),
            ("AnimationId", ctypes.c_int),
        ]

    class WINCOMPATTRDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", ctypes.c_int),
            ("Data", ctypes.POINTER(ACCENTPOLICY)),
            ("SizeOfData", ctypes.c_size_t),
        ]

    accent = ACCENTPOLICY()
    accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND
    accent.GradientColor = 0xAA000000  # alpha + black

    data = WINCOMPATTRDATA()
    data.Attribute = 19
    data.Data = ctypes.pointer(accent)
    data.SizeOfData = ctypes.sizeof(accent)

    user32 = ctypes.windll.user32
    user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))


# ======================
# Main window
# ======================

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-alpha", 0.92)
root.configure(bg="#050505")

screen_width = root.winfo_screenwidth()
window_width = int(screen_width / 2)
x_position = int((screen_width - window_width) / 2)

root.geometry(f"{window_width}x45+{x_position}+10")

# включаем blur (ТОЛЬКО после создания окна)
root.update()
hwnd = wintypes.HWND(root.winfo_id())
enable_blur(hwnd)

# ======================
# Drag window (киберпанк overlay всегда draggable)
# ======================

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_motion(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")

root.bind("<ButtonPress-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", on_motion)

# ======================
# UI
# ======================

main = tk.Frame(root, bg="#050505")
main.pack(fill="both", expand=True, padx=15, pady=8)

# cyberpunk текст
label = tk.Label(
    main,
    text="NEURAL LINK ONLINE",
    fg="#00FFF0",
    bg="#050505",
    font=("Consolas", 14, "bold")
)
label.pack(side="left")

# неоновая нижняя линия
glow = tk.Frame(root, bg="#00FFF0", height=3)
glow.pack(side="bottom", fill="x")

root.mainloop()
