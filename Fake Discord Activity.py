import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from pypresence import Presence
import threading
import time
import webbrowser
import sys, os

# --- Функция для корректного пути к ресурсам ---
def resource_path(relative_path):
    """ Получает правильный путь к файлу, работает и в exe, и в скрипте """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- UI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("Fake Discord Activity")
root.geometry("500x700")
root.grid_rowconfigure(tuple(range(0, 10)), weight=1)
root.grid_columnconfigure(0, weight=1)

# --- Discord Logo ---
try:
    image = Image.open(resource_path("discord_logo.png")).resize((80, 80))
    discord_logo_img = CTkImage(light_image=image, size=(80, 80))
    discord_logo = ctk.CTkLabel(root, text="", image=discord_logo_img, bg_color="transparent")
    discord_logo.grid(row=0, column=0, pady=10)
except FileNotFoundError:
    print("Логотип Discord не найден, пропускаем.")

# --- Параметры ---
small_gap = 5
large_gap = 20

# --- Анимация рамки ---
def animate_border(entry, start_color, end_color, steps=5, delay=5):
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0,2,4))
    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    for i in range(steps):
        ratio = (i+1)/steps
        new_rgb = tuple(int(start_rgb[j] + (end_rgb[j]-start_rgb[j])*ratio) for j in range(3))
        entry.configure(border_color=rgb_to_hex(new_rgb))
        entry.update()
        entry.after(delay)

def on_focus_in(entry):
    threading.Thread(target=animate_border, args=(entry, entry._border_color, "#5865f2")).start()
def on_focus_out(entry):
    threading.Thread(target=animate_border, args=(entry, entry._border_color, "#1f1f1f")).start()

# --- Вставка текста из буфера обмена ---
def enable_paste(entry):
    entry.bind("<Control-v>", lambda e: entry.insert(ctk.END, root.clipboard_get()))
    entry.bind("<Button-3>", lambda e: entry.insert(ctk.END, root.clipboard_get()))
    entry.bind("<Command-v>", lambda e: entry.insert(ctk.END, root.clipboard_get()))

# --- Импутбоксы ---
entry_client = ctk.CTkEntry(root, width=300, height=50, corner_radius=43,
                             placeholder_text="Client ID", border_width=2, border_color="#1f1f1f")
entry_client.grid(row=1, column=0, pady=small_gap)
entry_client.bind("<FocusIn>", lambda e: on_focus_in(entry_client))
entry_client.bind("<FocusOut>", lambda e: on_focus_out(entry_client))

entry_top = ctk.CTkEntry(root, width=300, height=50, corner_radius=43,
                         placeholder_text="Верхняя строка", border_width=2, border_color="#1f1f1f")
entry_top.grid(row=2, column=0, pady=small_gap)
entry_top.bind("<FocusIn>", lambda e: on_focus_in(entry_top))
entry_top.bind("<FocusOut>", lambda e: on_focus_out(entry_top))

entry_bottom = ctk.CTkEntry(root, width=300, height=50, corner_radius=43,
                            placeholder_text="Нижняя строка", border_width=2, border_color="#1f1f1f")
entry_bottom.grid(row=3, column=0, pady=small_gap)
entry_bottom.bind("<FocusIn>", lambda e: on_focus_in(entry_bottom))
entry_bottom.bind("<FocusOut>", lambda e: on_focus_out(entry_bottom))

# --- Включаем вставку для всех Entry ---
for e in [entry_client, entry_top, entry_bottom]:
    enable_paste(e)

# --- Сообщения об ошибке и подключении ---
status_label = ctk.CTkLabel(root, text="", text_color="red")
status_label.grid(row=4, column=0, pady=5)

# --- RPC глобальная переменная ---
rpc = None

# --- Кнопка обновления ---
def on_enter(e):
    btn_update.configure(fg_color="#4752c4")
def on_leave(e):
    btn_update.configure(fg_color="#5865f2")
def on_click(event):
    original_height = btn_update._current_height
    shrink_height = int(original_height*0.9)
    btn_update.configure(height=shrink_height)
    btn_update.update()
    root.after(100, lambda: btn_update.configure(height=original_height))

def update_presence(client_id):
    global rpc
    if not client_id:
        status_label.configure(text="❌ Введите Client ID", text_color="red")
        return

    def connect_and_update():
        global rpc
        try:
            # переподключение
            if rpc:
                try:
                    rpc.close()
                except:
                    pass

            rpc = Presence(client_id)
            rpc.connect()
            state = entry_bottom.get()
            details = entry_top.get()
            rpc.update(state=state, details=details)
            status_label.configure(text="🎮 Активность обновлена", text_color="green")
        except Exception as e:
            status_label.configure(text=f"Ошибка: {e}", text_color="red")

    threading.Thread(target=connect_and_update).start()

btn_update = ctk.CTkButton(root, text="Обновить активность",
                           width=300, height=50, corner_radius=43,
                           fg_color="#5865f2", hover_color="#5865f2",
                           command=lambda: update_presence(entry_client.get()))
btn_update.grid(row=5, column=0, pady=0)
btn_update.bind("<Enter>", on_enter)
btn_update.bind("<Leave>", on_leave)
btn_update.bind("<Button-1>", on_click)

# --- Гиперссылка под кнопкой ---
def open_link(event):
    webbrowser.open("https://www.youtube.com/@MrJool1809")
link_label = ctk.CTkLabel(root, text="Как использовать?", text_color="#5865f2", cursor="hand2")
link_label.grid(row=6, column=0, pady=5)
link_label.bind("<Button-1>", open_link)

# --- Поток keep_alive ---
def keep_alive():
    while True:
        time.sleep(15)
        if rpc:
            try:
                rpc.update(state=entry_bottom.get(), details=entry_top.get())
            except:
                pass

threading.Thread(target=keep_alive, daemon=True).start()

root.mainloop()
