
# Імпортуємо бібліотеки, які потрібні для роботи програми
from customtkinter import *  # Створення вікна та кнопок
from PIL import Image        # Робота із зображеннями
import io                    # Робота з файлами в пам'яті
import base64                # Перетворення зображень у текст
import os                    # Робота з назвами файлів
from socket import *         # З'єднання між комп'ютерами
import threading             # Одночасна робота декількох процесів

# Встановлюємо світлу тему програми
set_appearance_mode("Light")


# Головний клас програми LogiTalk
class LogiTalkApp(CTk):
    def __init__(self):
        super().__init__()

        # Налаштування головного вікна
        self.title("LogiTalk")
        self.geometry("700x450")
        self.minsize(500, 350)
        self.resizable(True, True)

        # Кольори елементів програми
        self.COLOR_MENU_BG = "#E9EBEE"
        self.COLOR_MENU_BORDER = "#CCD0D5"
        self.COLOR_BTN_NORMAL = "#3B5998"
        self.COLOR_BTN_HOVER = "#2D4373"
        self.COLOR_TEXT_DIM = "#4B4F56"

        self.menu_is_open = False
        self.configure(fg_color="#FFFFFF")

        # Завантажуємо фонове зображення
        self.bg_image = CTkImage(light_image=Image.open("background.png"), dark_image=Image.open("background.png"),
                                 size=(700, 450))
        self.bg_label = CTkLabel(self, text="", image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.bg_label.lower()

        # Викликаємо зміну розміру фону при зміні вікна
        self.bind("<Configure>", self.resize_bg)

        # Підключаємося до сервера
        self.sock = None
        self.connect_to_server()

        # Створюємо кнопку надсилання повідомлень
        self.btn_send = CTkButton(self, text=">", width=40, height=40, corner_radius=20, fg_color=self.COLOR_BTN_NORMAL,
                                  hover_color=self.COLOR_BTN_HOVER, text_color="white", command=self.click_send)
        self.btn_send.pack(side="bottom", anchor="e", padx=10, pady=10)

        # Створюємо кнопку для надсилання фотографій
        self.btn_img = CTkButton(self, text="🖼", width=40, height=40, corner_radius=20, fg_color=self.COLOR_BTN_NORMAL,
                                 hover_color=self.COLOR_BTN_HOVER, text_color="white", command=self.open_image)
        self.btn_img.pack(side="bottom", anchor="e", padx=(10, 0), pady=(0, 10))
        self.btn_img.place_forget()
        self.btn_send.pack(side="bottom", anchor="e", padx=10, pady=10)

        # Розміщуємо кнопки праворуч
        self.btn_send.pack_forget()
        self.btn_img.pack_forget()
        self.btn_send.pack(side="right", padx=10, pady=10)
        self.btn_img.pack(side="right", padx=(0, 5), pady=10)

        # Поле для введення повідомлення
        self.entry_message = CTkEntry(self, placeholder_text="Введіть повідомлення:", height=40, corner_radius=20,
                                      border_width=1, fg_color="white", border_color=self.COLOR_MENU_BORDER,
                                      text_color="#1C1E21", placeholder_text_color="#8D949E")
        self.entry_message.pack(side="bottom", fill="x", padx=(10, 10), pady=(0, 10))

        # Дозволяємо надсилати повідомлення клавішею Enter
        self.entry_message.bind("<Return>", lambda event: self.click_send())

        # Створюємо область для відображення повідомлень
        self.chat_scroll_frame = CTkScrollableFrame(self, fg_color="transparent")
        self.chat_scroll_frame.pack(side="top", fill="both", expand=True, padx=(10, 10), pady=(10, 0))

        # Створюємо меню налаштувань
        self.frame_menu = CTkFrame(self, width=160, corner_radius=0, fg_color=self.COLOR_MENU_BG,
                                   border_color=self.COLOR_MENU_BORDER, border_width=1)

        # Напис та поле для введення імені
        self.lbl_name = CTkLabel(self.frame_menu, text="Ім'я", font=("Arial", 14, "bold"),
                                 text_color=self.COLOR_TEXT_DIM)
        self.lbl_name.place(x=15, y=65)

        self.entry_name = CTkEntry(self.frame_menu, width=130, corner_radius=5, fg_color="white",
                                   border_color=self.COLOR_MENU_BORDER, text_color="#1C1E21")
        self.entry_name.place(x=15, y=100)

        # Завантажуємо іконку налаштувань
        self.menu_icon = CTkImage(light_image=Image.open("settings.png"), dark_image=Image.open("settings.png"),
                                  size=(26, 26))

        # Створюємо кнопку відкриття меню
        self.btn_menu = CTkButton(self, text="", image=self.menu_icon, width=42, height=42, command=self.toggle_menu,
                                  corner_radius=21, fg_color=self.COLOR_BTN_NORMAL, hover_color=self.COLOR_BTN_HOVER)
        self.btn_menu.place(x=10, y=10)

    # Функція підключення до сервера
    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))

            # Запускаємо окремий потік для отримання повідомлень
            threading.Thread(target=self.recv_message, daemon=True).start()
        except:
            pass

    # Функція отримання повідомлень від сервера
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                # Розділяємо отримані повідомлення за рядками
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        if self.sock:
            self.sock.close()

    # Функція обробки отриманих повідомлень
    def handle_line(self, line):
        if not line:
            return

        # Визначаємо тип повідомлення
        parts = line.split("@", 3)
        msg_type = parts[0]

        # Якщо отримали звичайний текст
        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")

        # Якщо отримали зображення
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    # Декодуємо зображення та відкриваємо його
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(200, 200))
                    self.add_message(f"{author} надіслав фото: {filename}", img=ctk_img)
                except Exception as e:
                    self.add_message(f"Помилка зображення: {e}")
        else:
            self.add_message(line)

    # Функція надсилання текстового повідомлення
    def send_message(self, message):
        try:
            if self.sock:
                name = self.entry_name.get() or "Анонім"
                full_message = f"TEXT@{name}@{message}\n"
                self.sock.send(full_message.encode())
        except:
            pass

    # Функція перевірки та надсилання повідомлення
    def click_send(self):
        msg = self.entry_message.get()
        if msg.strip():
            self.send_message(msg)
            self.entry_message.delete(0, END)

    # Функція вибору та надсилання зображення
    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            # Читаємо файл і перетворюємо його у формат Base64
            with open(file_name, "rb") as f:
                raw = f.read()
                b64_data = base64.b64encode(raw).decode()

                # Отримуємо назву файлу та ім'я користувача
                short_name = os.path.basename(file_name)
                name = self.entry_name.get() or "Анонім"

                # Формуємо повідомлення із зображенням
                data = f"IMAGE@{name}@{short_name}@{b64_data}\n"
                self.sock.sendall(data.encode())
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")

    # Функція додавання повідомлення до чату
    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_scroll_frame, fg_color="#E9EBEE", corner_radius=10)
        message_frame.pack(pady=5, anchor="w", fill="x")

        # Визначаємо ширину тексту залежно від розміру вікна
        wraplenght_size = self.winfo_width() - 100
        if wraplenght_size < 200:
            wraplenght_size = 200

        # Відображаємо текст повідомлення
        lbl_msg = CTkLabel(message_frame, text=message, wraplength=wraplenght_size, justify="left",
                           text_color="#1C1E21")
        lbl_msg.pack(padx=10, pady=5, anchor="w")

        # Якщо є зображення, показуємо його
        if img:
            lbl_img = CTkLabel(message_frame, text="", image=img)
            lbl_img.pack(padx=10, pady=5, anchor="w")

        # Прокручуємо чат до останнього повідомлення
        self.chat_scroll_frame.update_idletasks()
        self.chat_scroll_frame._parent_canvas.yview_moveto(1.0)

    # Функція зміни розміру фонового зображення
    def resize_bg(self, event):
        if event.widget == self and event.width > 10 and event.height > 10:
            self.bg_image.configure(size=(event.width, event.height))

    # Функція відкриття та закриття меню налаштувань
    def toggle_menu(self):
        if not self.menu_is_open:
            self.frame_menu.place(x=0, y=0, relheight=1.0)
            self.btn_menu.place(x=118, y=10)
            self.btn_menu.lift()
            self.btn_menu.configure(
                fg_color=self.COLOR_MENU_BG,
                hover_color=self.COLOR_MENU_BORDER,
                border_width=1,
                border_color=self.COLOR_MENU_BORDER
            )
            self.menu_is_open = True
        else:
            self.frame_menu.place_forget()
            self.btn_menu.place(x=10, y=10)
            self.btn_menu.configure(
                fg_color=self.COLOR_BTN_NORMAL,
                hover_color=self.COLOR_BTN_HOVER,
                border_width=0
            )
            self.menu_is_open = False


# Створюємо об'єкт програми та запускаємо її
app = LogiTalkApp()
app.mainloop()
