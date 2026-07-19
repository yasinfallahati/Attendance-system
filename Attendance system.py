import cv2
import os
import pandas as pd
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image

#تنظیمات مسیرها 
desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
DATA_FOLDER = os.path.join(desktop_path, "Attendance_Data")
ACTIVE_LOGS = os.path.join(DATA_FOLDER, "active")

for folder in [DATA_FOLDER, ACTIVE_LOGS]:
    if not os.path.exists(folder): os.makedirs(folder)

DB_PATH = "attendance_db.csv"
ADMIN_PASS = "yasin..f..1389"

if not os.path.exists(DB_PATH):
    pd.DataFrame(columns=["Name", "Time", "Date"]).to_csv(DB_PATH, index=False, encoding='utf-8-sig')

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("yasin Face ID")
        self.root.geometry("500x650")
        
        self.bg_dark = "#0a192f"      
        self.bg_card = "#172a45"      
        self.accent_cyan = "#00f2ff"
        self.btn_color = "#1d3557"     
        
        self.root.configure(bg=self.bg_dark)
        self.setup_ui()
        self.root.after(500, self.load_models)

    def setup_ui(self):
        # هدر
        header = tk.Frame(self.root, bg=self.bg_dark)
        header.pack(pady=35, fill="x")
        tk.Label(header, text="YASIN FALLAHATI", font=("Arial", 24, "bold"), bg=self.bg_dark, fg=self.accent_cyan).pack()
        tk.Label(header, text="سیستم هوشمند حضور و غیاب (نسخه نهایی)", font=("Tahoma", 10), bg=self.bg_dark, fg="#8892b0").pack(pady=5)

        # کارت اصلی
        self.main_card = tk.Frame(self.root, bg=self.bg_card, padx=30, pady=35, highlightbackground="#233554", highlightthickness=1)
        self.main_card.pack(padx=40, pady=10, fill="both", expand=True)

        self.create_styled_btn("👤   ثبت‌نام کاربر جدید (فارسی/انگلیسی)", self.register_face, "#457b9d")
        self.create_styled_btn("📷   شروع اسکن چهره و ثبت ورود", self.mark_attendance, "#2a9d8f")
        self.create_styled_btn("⚙️   ورود به پنل مدیریت", self.open_admin, "#1d3557")

        self.status_var = tk.StringVar(value="در حال آماده‌سازی...")
        tk.Label(self.root, textvariable=self.status_var, bg="#020c1b", fg="#8892b0", font=("Tahoma", 9), pady=5).pack(side=tk.BOTTOM, fill="x")

    def load_models(self):
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.status_var.set("سیستم آماده به کار")
        except:
            self.status_var.set("خطا در لود مدل!")

    def create_styled_btn(self, text, command, hover_color):
        btn = tk.Button(self.main_card, text=text, command=command, bg=self.btn_color, fg="white", font=("Tahoma", 10, "bold"), width=25, height=2, bd=0, cursor="hand2")
        btn.pack(pady=15, fill="x")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.btn_color))

    def train_model(self):
        path = DATA_FOLDER
        image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
        if not image_paths: return None
        faces, ids, name_map = [], [], {}
        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path).convert('L')
            faces.append(np.array(img, 'uint8'))
            ids.append(i)
            # خواندن نام فایل به صورت یونیکد برای پشتیبانی فارسی
            name_map[i] = os.path.basename(img_path).split('.')[0]
        self.recognizer.train(faces, np.array(ids))
        return name_map

    def register_face(self):
        name = simpledialog.askstring("ثبت‌نام", "نام کاربر (می‌توانید فارسی وارد کنید):")
        if not name: return
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 242, 255), 2)
            cv2.imshow("Registration - Press 'S' to Save", frame)
            if cv2.waitKey(1) & 0xFF == ord('s') and len(faces) > 0:
                # ذخیره تصویر با نام فارسی
                cv2.imencode('.jpg', gray[y:y+h, x:x+w])[1].tofile(os.path.join(DATA_FOLDER, f"{name}.jpg"))
                messagebox.showinfo("موفقیت", f"کاربر {name} با موفقیت ثبت شد.")
                break
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cap.release()
        cv2.destroyAllWindows()

    def mark_attendance(self):
        name_map = self.train_model()
        if not name_map:
            messagebox.showerror("خطا", "دیتابیس خالی است!")
            return
        cap = cv2.VideoCapture(0)
        found_name = None
        while True:
            ret, frame = cap.read()
            if not ret: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                id_num, conf = self.recognizer.predict(gray[y:y+h, x:x+w])
                if conf < 70:
                    found_name = name_map[id_num]
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imshow("Scanning... Press 'Q' to Quit", frame)
            if cv2.waitKey(1) & 0xFF == ord('q') or found_name: break
        cap.release()
        cv2.destroyAllWindows()

        if found_name:
            now = datetime.now()
            # ذخیره در CSV با انکودینگ مناسب فارسی
            new_data = pd.DataFrame([[found_name, now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d")]])
            new_data.to_csv(DB_PATH, mode='a', header=False, index=False, encoding='utf-8-sig')
            
            # ایجاد لاگ متنی
            log_path = os.path.join(ACTIVE_LOGS, f"{found_name}_{now.strftime('%H%M%S')}.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"نام: {found_name}\nزمان: {now}")
            
            messagebox.showinfo("تایید", f"خوش آمدید {found_name}")

    def open_admin(self):
        passwd = simpledialog.askstring("امنیت", "رمز عبور مدیر:", show='*')
        if passwd == ADMIN_PASS:
            admin_win = tk.Toplevel(self.root)
            admin_win.title("پنل مدیریت گزارشات")
            admin_win.geometry("600x550")
            admin_win.configure(bg=self.bg_dark)

            # دکمه‌های کنترلی ادمین
            ctrl_frame = tk.Frame(admin_win, bg=self.bg_dark)
            ctrl_frame.pack(pady=10)
            
            tk.Button(ctrl_frame, text="📥 خروجی اکسل (Desktop)", command=self.export_to_excel, bg="#f4a261", font=("Tahoma", 9, "bold")).pack(side=tk.LEFT, padx=10)
            tk.Button(ctrl_frame, text="🔄 به‌روزرسانی لیست", command=lambda: refresh(), bg=self.accent_cyan, font=("Tahoma", 9, "bold")).pack(side=tk.LEFT, padx=10)

            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview", background=self.bg_card, foreground="white", fieldbackground=self.bg_card)
            
            cols = ("نام کاربر", "ساعت ورود", "تاریخ")
            tree = ttk.Treeview(admin_win, columns=cols, show='headings')
            for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center")
            tree.pack(expand=True, fill='both', padx=20, pady=10)
            
            def refresh():
                for i in tree.get_children(): tree.delete(i)
                if os.path.exists(DB_PATH):
                    df = pd.read_csv(DB_PATH, encoding='utf-8-sig')
                    for val in df.values: tree.insert("", "end", values=list(val))
            refresh()
        else:
            messagebox.showerror("خطا", "رمز اشتباه است!")

    def export_to_excel(self):
        try:
            df = pd.read_csv(DB_PATH, encoding='utf-8-sig')
            file_path = os.path.join(desktop_path, f"گزارش_تردد_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
            df.to_excel(file_path, index=False)
            messagebox.showinfo("موفقیت", f"فایل اکسل با موفقیت روی دسکتاپ ذخیره شد:\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("خطا", f"مشکل در ساخت اکسل: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.mainloop()
