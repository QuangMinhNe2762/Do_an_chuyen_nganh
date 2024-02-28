import tkinter as tk
from pymongo import MongoClient
import sys
import WineQT_GUI
from tkinter import messagebox as msb
from PIL import ImageTk, Image


def client_():
    dbs = server_entry.get()
    if dbs == "":  # Entry nhập localhost trống
        dbs = "mongodb://localhost:27017/" # localhost mặc định
    client = MongoClient(dbs)
    return client, dbs


def connect_to_database():
    # Kiểm tra kết nối thành công
    client, dbs = client_()
    if "Wine" in client.list_database_names():
        msb.showinfo("Thông báo", "Kết nối thành công!")
        sys.argv.append(dbs)
        window.destroy()
        WineQT_GUI.main()
    else:
        msb.showinfo("Thông báo", "Kết nối không thành công!")


# Tạo cửa sổ
window = tk.Tk()
window.title("Kết nối MongoDB")
window.geometry("400x230+750+250")
window.configure(bg="white")

# Ảnh logo
image_path = "Logo.jpg"  # Đường dẫn đến hình ảnh của bạn
image = Image.open(image_path)
image = image.resize((110, 100))  # Thay đổi kích thước hình ảnh nếu cần
photo = ImageTk.PhotoImage(image)

# Tạo widget Label và hiển thị hình ảnh
label = tk.Label(window, image=photo, bg="white")
label.pack()

# Tạo các widgets
server_label = tk.Label(window, text="Database:", bg="white")
server_label.pack(padx=5, pady=5)

server_entry = tk.Entry(window)
server_entry.pack(padx=5, pady=5)

connect_button = tk.Button(window, text="Kết nối", bg="green", fg="white", font=("Arial", 8),
                           command=connect_to_database)
connect_button.pack(padx=5, pady=5)

notelb = tk.Label(window, text="Mặc định: mongodb://localhost:27017/", bg="white")
notelb.config(font=("Arial", 8))
notelb.place(x=4, y=210)

server_entry.focus()

# Chạy giao diện chính
window.mainloop()
