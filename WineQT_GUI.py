import sys
import csv
import tkinter as tk
from tkinter import ttk
import joblib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient
import tkinter.filedialog as fd
import pandas as pd
from tkinter import messagebox as msb


def main():
    # Tạo khung chính
    root = tk.Tk()
    root.title("Dự đoán chất lượng rượu vang")
    root.geometry("700x620+750+250")

    # -------------------------------------------------Kết nối MongoDB--------------------------------------------------
    # Kết nối tới MongoDB
    client = MongoClient(sys.argv[1])
    db = client['Wine']  # Tên database
    collection = db['ThongSo']  # Tên collection

    # ----------------------------------------------------------TAB-----------------------------------------------------
    # Tạo một Tab Control
    tab = ttk.Notebook(root)

    # Tạo Tab 1
    tab1 = ttk.Frame(tab)
    tab.add(tab1, text='Giao diện chính')

    # Tạo Tab 2
    tab2 = ttk.Frame(tab)
    tab.add(tab2, text='Dự đoán nhiều')

    # Hiển thị Tab Control
    tab.pack(expand=1, fill='both')
    def close():
        sys.exit()
    root.protocol("WM_DELETE_WINDOW", close)
    # -------------------------------------------------------GROUPBOX---------------------------------------------------
    # Groupbox dự đoán
    grb_pt = tk.LabelFrame(tab1, text="Dự đoán", padx=10, pady=10)
    grb_pt.place(x=350, y=10)

    # Groupbox trực quan
    grb_tq = tk.LabelFrame(tab1, text="Thống kê", padx=10, pady=10)
    grb_tq.place(x=350, y=280)

    # Groupbox chất lượng kém
    grb_k = tk.LabelFrame(tab1, text="Chất lượng kém", padx=10, pady=10)
    grb_k.place(x=20, y=10)

    # Groupbox chất lượng trung bình
    grb_tb = tk.LabelFrame(tab1, text="Chất lượng trung bình", padx=10, pady=10)
    grb_tb.place(x=20, y=200)

    # Groupbox chất lượng cao
    grb_c = tk.LabelFrame(tab1, text="Chất lượng cao", padx=10, pady=10)
    grb_c.place(x=20, y=390)

    # Groupbox cho dữ liệu dự đoán không nhãn
    grb_klb = tk.LabelFrame(tab2, text="Dự đoán chất lương rượu", padx=10, pady=10)
    grb_klb.pack()

    # ------------------------------------------Tạo thành phần cho GROUPBOX Phân tích-----------------------------------

    # Chỉ cho phép nập số nguyên hoặc số thực
    def valiDate_number_input_float(new_value):
        if not new_value:
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    check_float = root.register(valiDate_number_input_float)

    # Làm mới lại form
    def reset_form():
        entchlor.delete(0, "end")
        ent_sulphates.delete(0, "end")
        ent_alcohol.delete(0, "end")
        ent_volatile.delete(0, "end")
        truyvan(kem, '0')
        truyvan(tb, '1')
        truyvan(cao, '2')
        upDate_chart()
        btnluu.config(state="disabled")

    def dudoan():
        # Kiểm tra entry phải nhập đầy đủ
        if str(entchlor.get()).strip() == "" or str(ent_alcohol.get()).strip() == "" \
                or str(ent_sulphates.get()).strip() == "" or str(ent_volatile.get()).strip() == "":
            msb.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin")
        else:
            # Tải mô hình từ file
            model = joblib.load(".\\Model\\wine_model.pkl")

            # Tải trình chuẩn hóa
            sc = joblib.load(".\\Model\\scaler.pkl")

            # Lấy giá trị từ các entry
            volatile = float(ent_volatile.get())
            chlorides = float(entchlor.get())
            sulphates = float(ent_sulphates.get())
            alcohol = float(ent_alcohol.get())

            # Tạo mảng đầu vào với nhãn tương ứng
            arr = pd.DataFrame([[volatile, chlorides, sulphates, alcohol]],
                               columns=['volatile acidity', 'chlorides', 'sulphates', 'alcohol'])
            # Chuẩn hóa dữ liệu đầu vào
            arr_sc = sc.transform(arr)

            # Dự đoán chất lượng rượu
            pre = model.predict(arr_sc)

            if np.mean(pre) == 0:
                kq = "Kém"
            elif np.mean(pre) == 1:
                kq = "Trung bình"
            else:
                kq = "Cao"

            # Hiển thị dự đoán lên entry kết quả
            entKQ_var.set(kq)
            btnluu.config(state="active")

    # Hàn lưu dữ liệu vào csdl
    def luu_csdl():
        if str(entchlor.get()).strip() == "" or str(ent_alcohol.get()).strip() == "" \
                or str(ent_sulphates.get()).strip() == "" or str(ent_volatile.get()).strip() == "":
            msb.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin")
        else:
            try:
                # Mã hóa kết quả lại thành số
                kq = entKQ.get()
                if kq == 'Kém':
                    kq = "0"
                elif kq == 'Trung bình':
                    kq = "1"
                else:
                    kq = "2"

                # Tạo tài liệu mới
                document = {
                    "volatile acidity": ent_volatile.get(),
                    "chlorides": entchlor.get(),
                    "sulphates": ent_sulphates.get(),
                    "alcohol": ent_alcohol.get(),
                    "quality": kq
                }
                # Lưu tài liệu vào collection
                collection.insert_one(document)
                msb.showinfo("Thông bao", "Lưu thành công")
                reset_form()
                btnluu.config(state="disabled")  # Tắt button lưu
            except:
                msb.showerror("Lỗi", "Lưu thất bại vui lòng kiểm tra lại!")

    lbchlor = tk.Label(grb_pt, text="chlorides:")
    entchlor_var = tk.StringVar()
    entchlor = tk.Entry(grb_pt, textvariable=entchlor_var, validate='key', validatecommand=(check_float, '%P'))
    lbsul = tk.Label(grb_pt, text="sulphates:")
    ent_sulphates_var = tk.StringVar()
    ent_sulphates = tk.Entry(grb_pt, textvariable=ent_sulphates_var, validate='key',
                             validatecommand=(check_float, '%P'))
    lbalcohol = tk.Label(grb_pt, text="alcohol:")
    ent_alcohol_var = tk.StringVar()
    ent_alcohol = tk.Entry(grb_pt, textvariable=ent_alcohol_var, validate='key', validatecommand=(check_float, '%P'))
    lbvolatile = tk.Label(grb_pt, text="volatile acidity:")
    ent_volatile_var = tk.StringVar()
    ent_volatile = tk.Entry(grb_pt, textvariable=ent_volatile_var, validate='key', validatecommand=(check_float, '%P'))

    entKQ_var = tk.StringVar(value="Kết quả")
    entKQ = tk.Entry(tab1, width=53, state="readonly", textvariable=entKQ_var, justify='center')

    btndudoan = tk.Button(grb_pt, text="Dự đoán", bg="#00BFFF", command=dudoan)
    btnluu = tk.Button(grb_pt, text="Lưu vào CSDL", bg="#00BFFF", command=luu_csdl)
    btnluu.config(state="disabled")
    btnreset = tk.Button(grb_pt, text="Làm mới", command=reset_form, bg="#00BFFF")

    # Thiết lập vị trị cho các phần tử trong groupbox
    lbchlor.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    entchlor.grid(row=1, column=1, padx=5, pady=5)
    lbsul.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    ent_sulphates.grid(row=2, column=1, padx=5, pady=5)
    lbalcohol.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    ent_alcohol.grid(row=3, column=1, padx=5, pady=5)
    lbvolatile.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    ent_volatile.grid(row=0, column=1, padx=5, pady=5)
    entKQ.place(x=350, y=230)

    btndudoan.grid(row=7, column=0, padx=5, pady=5)
    btnluu.grid(row=7, column=1, padx=5, pady=5)
    btnreset.grid(row=7, column=2, padx=5, pady=5)

    # -------------------------------------------------TREEVIEW------------------------------------------------
    # Khởi tạo treeview
    kem = ttk.Treeview(grb_k, height=5)  # Treeview châ lượng rượu kém
    tb = ttk.Treeview(grb_tb, height=5)  # Treeview châ lượng rượu trung bình
    cao = ttk.Treeview(grb_c, height=5)  # Treeview châ lượng rượu cao
    no_label = ttk.Treeview(grb_klb, height=60)  # Treeview châ lượng rượu chưa gán nhãn

    # Tạo treeview và load dữ liệu
    def create_treeview(trv_tg, name_grp):
        # Tạo scrollbar cuộn dọc
        scr_doc = ttk.Scrollbar(name_grp, orient="vertical", command=trv_tg.yview)
        trv_tg.configure(yscrollcommand=scr_doc.set)
        scr_doc.pack(side="right", fill="y")

        # Tạo scrollbar cuộn ngang
        scr_ngang = ttk.Scrollbar(name_grp, orient="horizontal", command=trv_tg.xview)
        trv_tg.configure(xscrollcommand=scr_ngang.set)
        scr_ngang.pack(side="bottom", fill="x")
        trv_tg.pack()

        # Thêm cột vào Treeview
        trv_tg["columns"] = ("col1", "col2", "col3", "col4")
        trv_tg.column("#0", width=0, minwidth=0)
        trv_tg.column("col1", width=70, minwidth=80, anchor="center")
        trv_tg.column("col2", width=70, minwidth=80, anchor="center")
        trv_tg.column("col3", width=70, minwidth=80, anchor="center")
        trv_tg.column("col4", width=70, minwidth=80, anchor="center")
        trv_tg.heading("col1", text="volatile acidity")
        trv_tg.heading("col2", text="chlorides")
        trv_tg.heading("col3", text="sulphates")
        trv_tg.heading("col4", text="alcohol")

        # Nếu treeview là hiển thị dữ liệu chưa gán nhãn
        if trv_tg == no_label:
            trv_tg["columns"] = ("col1", "col2", "col3", "col4", "col5")
            trv_tg.column("#0", width=0, minwidth=0)
            trv_tg.column("col1", width=70, minwidth=80, anchor="center")
            trv_tg.column("col2", width=70, minwidth=80, anchor="center")
            trv_tg.column("col3", width=70, minwidth=80, anchor="center")
            trv_tg.column("col4", width=70, minwidth=80, anchor="center")
            trv_tg.column("col5", width=70, minwidth=80, anchor="center")
            trv_tg.heading("col1", text="volatile acidity")
            trv_tg.heading("col2", text="chlorides")
            trv_tg.heading("col3", text="sulphates")
            trv_tg.heading("col4", text="alcohol")
            trv_tg.heading("col5", text="quality")

    def truyvan(trv_tg, dk_find):
        trv_tg.delete(*trv_tg.get_children())
        query = {"quality": dk_find}  # Điều kiện tìm kiếm quality = 0 hoặc 1 hoạc 2
        projection = {'volatile acidity': 1, 'chlorides': 1, 'sulphates': 1, 'alcohol': 1}
        data = collection.find(query, projection)

        for doc in data:
            values = (
                doc['volatile acidity'],
                doc['chlorides'],
                doc['sulphates'],
                doc['alcohol']
            )
            trv_tg.insert("", "end", values=values)

    # Hiển thị lên entry khi select 1 dòng trên treeview kém
    def select_trvkem(event):
        select_item = kem.focus()
        values = kem.item(select_item, "values")

        ent_volatile_var.set(values[0])
        entchlor_var.set(values[1])
        ent_sulphates_var.set(values[2])
        ent_alcohol_var.set(values[3])

    # Hiển thị lên entry khi select 1 dòng trên treeview trung bình
    def select_trvtb(event):
        select_item = tb.focus()
        values = tb.item(select_item, "values")

        ent_volatile_var.set(values[0])
        entchlor_var.set(values[1])
        ent_sulphates_var.set(values[2])
        ent_alcohol_var.set(values[3])

    # Hiển thị lên entry khi select 1 dòng trên treeview cao
    def select_trvcao(event):
        select_item = cao.focus()
        values = cao.item(select_item, "values")

        ent_volatile_var.set(values[0])
        entchlor_var.set(values[1])
        ent_sulphates_var.set(values[2])
        ent_alcohol_var.set(values[3])

    # ----------------------------------------------TRỰC QUAN SỐ LƯỢNG--------------------------------------------------
    fig, ax = plt.subplots(figsize=(3, 2.55))
    # Tạo đối tượng Canvas Tkinter
    canvas = FigureCanvasTkAgg(fig, master=grb_tq)

    def query_data():
        # Lấy số lượng dữ liệu ban đầu
        count_0 = collection.count_documents({"quality": '0'})
        count_1 = collection.count_documents({"quality": '1'})
        count_2 = collection.count_documents({"quality": '2'})
        return count_0, count_1, count_2

    def trucquan():
        # Tạo dữ liệu đồ thị cột
        labels = ['Kém', 'Trung bình', 'Cao']
        counts = query_data()
        ax.bar(labels, counts, color=['red', 'gray', 'blue'])
        ax.set_yticklabels([])  # Bỏ đếm số lươợng trên cột y
        ax.set_yticks([])  # Bỏ dấu gạch mức số lượng trên y
        # Hiển thị số lượng tương ứng trên đầu mỗi cột
        for i, v in enumerate(counts):
            ax.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=8, fontweight='bold', color='black',
                    bbox=dict(facecolor='white', edgecolor='none', pad=0.1))

    # Hàm cập nhật đồ thị khi thêm dữ liệu
    def upDate_chart():
        ax.clear()
        trucquan()
        canvas.draw()

    # -----------------------------------------------------TAB2---------------------------------------------------------
    # Import dữ liệu từ file csv vào mongodb và load lên treeview để dự đoán
    def import_csv():
        # Xóa dữ liệu cũ trong treeview (nếu có)
        no_label.delete(*no_label.get_children())
        # Đường dẫn đến file csv
        file_path = fd.askopenfilename(filetypes=[('CSV Files', '*.csv')])

        if file_path:
            # Đọc dữ liệu từ file CSV
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)  # Lấy header từ dòng đầu tiên trong csv
                no_label['columns'] = header  # Thiết lập các cột cho treeview
                for i, col in enumerate(header):
                    no_label.heading(col, text=col)  # Thiết lập header cho các cột
                    no_label.column(col, width=80)  # Thiết lập kích thước cho mỗi cột
                for row in reader:
                    no_label.insert('', 'end', values=row)  # Thêm một dòng dữ liệu vào treeview
            dudoan_button.config(state="active")
        else:
            msb.showerror("Lỗi", "Bạn vui lòng kiểm tra lại!")

    def update_attended():
        # Tải mô hình từ file
        model = joblib.load(".\\Model\\wine_model.pkl")

        # Tải trình chuẩn hóa
        sc = joblib.load(".\\Model\\scaler.pkl")

        # Lặp qua từng dòng trong Treeview
        for item in no_label.get_children():
            # Lấy giá trị của từng cột trên dòng đó
            row_data = []
            for column in range(0, 4):
                value = no_label.item(item)['values'][column]
                row_data.append(value)

            # Tạo mảng đầu vào với nhãn tương ứng
            arr = pd.DataFrame([row_data],
                               columns=['volatile acidity', 'chlorides', 'sulphates', 'alcohol'])
            # Chuẩn hóa dữ liệu đầu vào
            arr_sc = sc.transform(arr)

            # Dự đoán
            pre = model.predict(arr_sc)
            if np.mean(pre) == 0:
                kq = "Kém"
            elif np.mean(pre) == 1:
                kq = "Trung bình"
            else:
                kq = "Cao"
            # Set nhãn dự đoán cho cột quality trên dòng đó
            no_label.set(item, column=4, value=kq)

            save_button.config(state="active")
            dudoan_button.config(state="disabled")

    def save_to_mongodb():
        header = ['volatile acidity', 'chlorides', 'sulphates', 'alcohol', 'quality']
        # Lưu dữ liệu từ TreeView vào MongoDB
        for child in no_label.get_children():
            values = no_label.item(child)["values"]
            data = {header[i]: values[i] if header[i] != 'quality' else map_quality(values[i]) for i in
                    range(len(header))}
            collection.insert_one(data)

        msb.showinfo("Thông báo", "Lưu dữ liệu thành công")
        reset_form()
        save_button.config(state="disabled")

    def map_quality(value):
        if value == 'Kém':
            return '0'
        elif value == 'Trung bình':
            return '1'
        elif value == 'Cao':
            return '2'
        else:
            return value

    import_button = tk.Button(grb_klb, text="Import CSV", command=import_csv, bg="#00BFFF")
    import_button.pack(padx=5, pady=5)

    dudoan_button = tk.Button(grb_klb, text="Dự đoán", bg="#00BFFF", command=update_attended)
    dudoan_button.pack(padx=5, pady=5)
    dudoan_button.config(state="disabled")

    save_button = tk.Button(grb_klb, text="Lưu", bg="#00BFFF", command=save_to_mongodb)
    save_button.pack(padx=5, pady=5)
    save_button.config(state="disabled")

    # ----------------------------------------------------GỌI THỰC THI--------------------------------------------------
    trucquan()
    # Vẽ đối tượng
    canvas.draw()
    # Định vị đối tượng Canvas
    canvas.get_tk_widget().pack()
    create_treeview(kem, grb_k)
    create_treeview(tb, grb_tb)
    create_treeview(cao, grb_c)
    create_treeview(no_label, grb_klb)
    truyvan(kem, "0")
    truyvan(tb, "1")
    truyvan(cao, "2")
    kem.bind("<<TreeviewSelect>>", select_trvkem)
    tb.bind("<<TreeviewSelect>>", select_trvtb)
    cao.bind("<<TreeviewSelect>>", select_trvcao)

    # Chạy ứng dụng
    root.mainloop()
