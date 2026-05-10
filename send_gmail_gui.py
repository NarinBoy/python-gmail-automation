import os
import base64
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Config Files
CLIENT_SECRET_FILE = 'client_secret.json'
CONFIG_FILE = 'config.json'
TEMPLATE_FILE = 'email_template.html'

selected_file_path = ""

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return {"to_email": "", "cc_emails": []}

def load_template(travel_dates):
    try:
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                return content.replace("{travel_dates}", travel_dates)
    except Exception as e:
        print(f"Error loading template: {e}")
    return f"ขออนุมัติเดินทางวันที่ {travel_dates}"

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(f"ไม่พบไฟล์ {CLIENT_SECRET_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def select_file():
    global selected_file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        selected_file_path = file_path
        file_label.config(text=os.path.basename(file_path), fg="#2D3748")

def reset_file():
    global selected_file_path
    selected_file_path = ""
    file_label.config(text="ยังไม่ได้เลือกไฟล์", fg="#718096")

def send_email():
    try:
        config = load_config()
        if not config["to_email"]:
            messagebox.showwarning("คำเตือน", "ไม่พบข้อมูลอีเมลใน config.json")
            return

        service = get_gmail_service()
        
        d1 = cal1.get_date()
        d2 = cal2.get_date()
        date1_str = f"{d1.strftime('%d/%m')}/{d1.year + 543}"
        date2_str = f"{d2.strftime('%d/%m')}/{d2.year + 543}"
        travel_dates_text = f"{date1_str} และ {date2_str}"

        html_body = load_template(travel_dates_text)

        subject = "ขออนุมัติเดินทางไปปฏิบัติงานสำหรับนักศึกษาฝึกงาน"
        message = MIMEMultipart()
        message['to'] = config["to_email"]
        message['cc'] = ", ".join(config["cc_emails"])
        message['subject'] = subject

        message.attach(MIMEText(html_body, 'html'))

        if selected_file_path:
            content_type, _ = mimetypes.guess_type(selected_file_path)
            main_type, sub_type = (content_type or 'application/octet-stream').split('/', 1)
            with open(selected_file_path, 'rb') as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(selected_file_path))
            message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        messagebox.showinfo("สำเร็จ", f"ส่งอีเมลเรียบร้อยแล้ว!\nสำหรับวันที่: {travel_dates_text}")
        
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถส่งเมลได้: {str(e)}")

# --- GUI Setup ---
root = tk.Tk()
root.title("ระบบส่งเมลขออนุมัติเดินทาง")
root.geometry("480x600")
root.configure(bg="#FFFFFF")

BG_WHITE = "#FFFFFF"
BORDER_GRAY = "#E2E8F0"
TEXT_MAIN = "#1A202C"
TEXT_SUB = "#718096"
BTN_GRAY = "#F7FAFC"
BTN_DARK = "#2D3748"

header_font = ("Sarabun", 16, "bold")
sub_font = ("Sarabun", 10, "bold")
normal_font = ("Sarabun", 10)

main_frame = tk.Frame(root, bg=BG_WHITE, padx=40, pady=30)
main_frame.pack(fill="both", expand=True)

tk.Label(main_frame, text="ส่งเมลขออนุมัติเดินทาง", font=header_font, fg=TEXT_MAIN, bg=BG_WHITE).pack(pady=(0, 30))

# Section 1: Dates
section1 = tk.Frame(main_frame, bg=BG_WHITE, highlightbackground=BORDER_GRAY, highlightthickness=1, padx=20, pady=20)
section1.pack(fill="x", pady=(0, 15))
tk.Label(section1, text="วันที่เดินทาง", font=sub_font, fg=TEXT_MAIN, bg=BG_WHITE).pack(anchor="w", pady=(0, 15))
date_grid = tk.Frame(section1, bg=BG_WHITE)
date_grid.pack(fill="x")
tk.Label(date_grid, text="เริ่ม:", font=normal_font, bg=BG_WHITE, fg=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=5)
cal1 = DateEntry(date_grid, width=15, background='#2D3748', foreground='white', borderwidth=0, date_pattern='dd/mm/yyyy')
cal1.grid(row=0, column=1, padx=(15, 0), pady=5)
tk.Label(date_grid, text="ถึง:", font=normal_font, bg=BG_WHITE, fg=TEXT_MAIN).grid(row=1, column=0, sticky="w", pady=5)
cal2 = DateEntry(date_grid, width=15, background='#2D3748', foreground='white', borderwidth=0, date_pattern='dd/mm/yyyy')
cal2.grid(row=1, column=1, padx=(15, 0), pady=5)

# Section 2: Attachment
section2 = tk.Frame(main_frame, bg=BG_WHITE, highlightbackground=BORDER_GRAY, highlightthickness=1, padx=20, pady=20)
section2.pack(fill="x", pady=15)
tk.Label(section2, text="ไฟล์แนบเอกสาร", font=sub_font, fg=TEXT_MAIN, bg=BG_WHITE).pack(anchor="w", pady=(0, 15))
file_btn_frame = tk.Frame(section2, bg=BG_WHITE)
file_btn_frame.pack(fill="x")
tk.Button(file_btn_frame, text="เลือกไฟล์", command=select_file, bg=BTN_GRAY, fg=TEXT_MAIN, font=normal_font, relief="flat", highlightbackground=BORDER_GRAY, highlightthickness=1, padx=20).pack(side="left", padx=(0, 8))
tk.Button(file_btn_frame, text="ล้าง", command=reset_file, bg=BG_WHITE, fg=TEXT_SUB, font=normal_font, relief="flat", padx=10).pack(side="left")
file_label = tk.Label(section2, text="ยังไม่ได้เลือกไฟล์", font=("Sarabun", 9), fg=TEXT_SUB, bg=BG_WHITE)
file_label.pack(anchor="w", pady=(12, 0))

# Section 3: Send
btn_send = tk.Button(main_frame, text="ส่งอีเมล", command=send_email, bg=BTN_DARK, fg="white", font=("Sarabun", 11, "bold"), relief="flat", pady=14, cursor="hand2")
btn_send.pack(fill="x", pady=(30, 0))

footer = tk.Label(main_frame, text="Gmail API Access Control", font=("Sarabun", 8), fg="#CBD5E0", bg=BG_WHITE)
footer.pack(side="bottom", pady=(20, 0))

root.mainloop()
