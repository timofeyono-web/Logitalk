

from customtkinter import *  
from PIL import Image        
import io                    
import base64                
import os                    
from socket import *         
import threading            


set_appearance_mode("Light")



class LogiTalkApp(CTk):
    def __init__(self):
        super().__init__()

        
        self.title("LogiTalk")
        self.geometry("700x450")
        self.minsize(500, 350)
        self.resizable(True, True)

       
        self.COLOR_MENU_BG = "#E9EBEE"
        self.COLOR_MENU_BORDER = "#CCD0D5"
        self.COLOR_BTN_NORMAL = "#3B5998"
        self.COLOR_BTN_HOVER = "#2D4373"
        self.COLOR_TEXT_DIM = "#4B4F56"

        self.menu_is_open = False
        self.configure(fg_color="#FFFFFF")

        
        self.bg_image = CTkImage(light_image=Image.open("background.png"), dark_image=Image.open("background.png"),
                                 size=(700, 450))
        self.bg_label = CTkLabel(self, text="", image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.bg_label.lower()

        
        self.bind("<Configure>", self.resize_bg)

        
        self.sock = None
        self.connect_to_server()

        
        self.btn_send = CTkButton(self, text=">", width=40, height=40, corner_radius=20, fg_color=self.COLOR_BTN_NORMAL,
                                  hover_color=self.COLOR_BTN_HOVER, text_color="white", command=self.click_send)
        self.btn_send.pack(side="bottom", anchor="e", padx=10, pady=10)

       
        self.btn_img = CTkButton(self, text="🖼", width=40, height=40, corner_radius=20, fg_color=self.COLOR_BTN_NORMAL,
                                 hover_color=self.COLOR_BTN_HOVER, text_color="white", command=self.open_image)
        self.btn_img.pack(side="bottom", anchor="e", padx=(10, 0), pady=(0, 10))
        self.btn_img.place_forget()
        self.btn_send.pack(side="bottom", anchor="e", padx=10, pady=10)

        
        self.btn_send.pack_forget()
        self.btn_img.pack_forget()
        self.btn_send.pack(side="right", padx=10, pady=10)
        self.btn_img.pack(side="right", padx=(0, 5), pady=10)

        
        self.entry_message = CTkEntry(self, placeholder_text="Введіть повідомлення:", height=40, corner_radius=20,
                                      border_width=1, fg_color="white", border_color=self.COLOR_MENU_BORDER,
                                      text_color="#1C1E21", placeholder_text_color="#8D949E")
        self.entry_message.pack(side="bottom", fill="x", padx=(10, 10), pady=(0, 10))

        
        self.entry_message.bind("<Return>", lambda event: self.click_send())

        
        self.chat_scroll_frame = CTkScrollableFrame(self, fg_color="transparent")
        self.chat_scroll_frame.pack(side="top", fill="both", expand=True, padx=(10, 10), pady=(10, 0))

       
        self.frame_menu = CTkFrame(self, width=160, corner_radius=0, fg_color=self.COLOR_MENU_BG,
                                   border_color=self.COLOR_MENU_BORDER, border_width=1)

       
        self.lbl_name = CTkLabel(self.frame_menu, text="Ім'я", font=("Arial", 14, "bold"),
                                 text_color=self.COLOR_TEXT_DIM)
        self.lbl_name.place(x=15, y=65)

        self.entry_name = CTkEntry(self.frame_menu, width=130, corner_radius=5, fg_color="white",
                                   border_color=self.COLOR_MENU_BORDER, text_color="#1C1E21")
        self.entry_name.place(x=15, y=100)

        
        self.menu_icon = CTkImage(light_image=Image.open("settings.png"), dark_image=Image.open("settings.png"),
                                  size=(26, 26))

        
        self.btn_menu = CTkButton(self, text="", image=self.menu_icon, width=42, height=42, command=self.toggle_menu,
                                  corner_radius=21, fg_color=self.COLOR_BTN_NORMAL, hover_color=self.COLOR_BTN_HOVER)
        self.btn_menu.place(x=10, y=10)

    
    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))

            
            threading.Thread(target=self.recv_message, daemon=True).start()
        except:
            pass

    
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        if self.sock:
            self.sock.close()

    
    def handle_line(self, line):
        if not line:
            return

        
        parts = line.split("@", 3)
        msg_type = parts[0]

        
        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")

        
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                   
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(200, 200))
                    self.add_message(f"{author} надіслав фото: {filename}", img=ctk_img)
                except Exception as e:
                    self.add_message(f"Помилка зображення: {e}")
        else:
            self.add_message(line)

    
    def send_message(self, message):
        try:
            if self.sock:
                name = self.entry_name.get() or "Анонім"
                full_message = f"TEXT@{name}@{message}\n"
                self.sock.send(full_message.encode())
        except:
            pass

    
    def click_send(self):
        msg = self.entry_message.get()
        if msg.strip():
            self.send_message(msg)
            self.entry_message.delete(0, END)

    
    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            
            with open(file_name, "rb") as f:
                raw = f.read()
                b64_data = base64.b64encode(raw).decode()

                
                short_name = os.path.basename(file_name)
                name = self.entry_name.get() or "Анонім"

                
                data = f"IMAGE@{name}@{short_name}@{b64_data}\n"
                self.sock.sendall(data.encode())
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")

    
    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_scroll_frame, fg_color="#E9EBEE", corner_radius=10)
        message_frame.pack(pady=5, anchor="w", fill="x")

        
        wraplenght_size = self.winfo_width() - 100
        if wraplenght_size < 200:
            wraplenght_size = 200

       
        lbl_msg = CTkLabel(message_frame, text=message, wraplength=wraplenght_size, justify="left",
                           text_color="#1C1E21")
        lbl_msg.pack(padx=10, pady=5, anchor="w")

       
        if img:
            lbl_img = CTkLabel(message_frame, text="", image=img)
            lbl_img.pack(padx=10, pady=5, anchor="w")

        
        self.chat_scroll_frame.update_idletasks()
        self.chat_scroll_frame._parent_canvas.yview_moveto(1.0)


    def resize_bg(self, event):
        if event.widget == self and event.width > 10 and event.height > 10:
            self.bg_image.configure(size=(event.width, event.height))

    
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



app = LogiTalkApp()
app.mainloop()
