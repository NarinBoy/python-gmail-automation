import os
import base64
import json
import threading
import mimetypes
import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Config Files
CLIENT_SECRET_FILE = 'client_secret.json'
CONFIG_FILE = 'config.json'
TEMPLATE_FILE_1DAY = 'email_template_1day.html'  # เทมเพลตสำหรับเดินทาง 1 วัน
TEMPLATE_FILE_2DAY = 'email_template_2day.html'  # เทมเพลตสำหรับเดินทาง 2 วัน

THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

selected_file_path = ""

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return {"to_email": "", "cc_emails": []}

def load_template(template_file, travel_dates_thai, travel_dates_numeric):
    try:
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                content = content.replace("{travel_dates_thai}", travel_dates_thai)
                return content.replace("{travel_dates_numeric}", travel_dates_numeric)
    except Exception as e:
        print(f"Error loading template: {e}")
    return f"ขออนุมัติเดินทางวันที่ {travel_dates_thai}"

def save_token(creds):
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception:
            creds = None  # token.json อ่านไม่ได้ → ขอสิทธิ์ใหม่
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_token(creds)
        except Exception:
            creds = None  # refresh token หมดอายุ/ถูกเพิกถอน → ขอสิทธิ์ใหม่
    if not creds or not creds.valid:
        if not os.path.exists(CLIENT_SECRET_FILE):
            raise FileNotFoundError(f"ไม่พบไฟล์ {CLIENT_SECRET_FILE}")
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        save_token(creds)
    return build('gmail', 'v1', credentials=creds)

# --- Date helpers ---

def format_thai_date(d):
    # ปีพุทธศักราช = ค.ศ. + 543
    return f"{d.day} {THAI_MONTHS[d.month - 1]} {d.year + 543}"

def format_numeric_date(d):
    return f"{d.strftime('%d/%m')}/{d.year + 543}"

def build_travel_dates():
    # คืนค่า (วันที่แบบไทย, วันที่แบบตัวเลข, ไฟล์เทมเพลต) ตามโหมด 1/2 วัน
    d1 = cal1.get_date()
    if day_count_var.get() == 2:
        d2 = cal2.get_date()
        return (
            f"{format_thai_date(d1)} และ {format_thai_date(d2)}",
            f"{format_numeric_date(d1)} และ {format_numeric_date(d2)}",
            TEMPLATE_FILE_2DAY,
        )
    return format_thai_date(d1), format_numeric_date(d1), TEMPLATE_FILE_1DAY

# --- GUI callbacks ---

def select_file():
    global selected_file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        selected_file_path = file_path
        file_label.config(text=os.path.basename(file_path), fg=TEXT_MAIN)

def reset_file():
    global selected_file_path
    selected_file_path = ""
    file_label.config(text="ยังไม่ได้เลือกไฟล์", fg=TEXT_SUB)

def set_day_mode(n):
    day_count_var.set(n)
    update_day_mode()

def _style_segment(btn, selected):
    if selected:
        btn.config(bg=ACCENT, fg="white", activebackground=ACCENT, activeforeground="white")
    else:
        btn.config(bg=BG_WHITE, fg=TEXT_SUB, activebackground=SEG_HOVER, activeforeground=TEXT_MAIN)

def _segment_hover(btn, value, entering):
    # hover เฉพาะปุ่มฝั่งที่ยังไม่ถูกเลือก
    if day_count_var.get() != value:
        btn.config(bg=SEG_HOVER if entering else BG_WHITE)

def update_day_mode():
    # จัดสีปุ่ม segmented และแสดง/ซ่อนช่องวันที่สองตามโหมด
    one_day = day_count_var.get() == 1
    _style_segment(btn_seg1, selected=one_day)
    _style_segment(btn_seg2, selected=not one_day)
    if one_day:
        lbl_from.config(text="วันที่:")
        lbl_to.grid_remove()
        cal2.grid_remove()
    else:
        lbl_from.config(text="เริ่ม:")
        lbl_to.grid()
        cal2.grid()
    refresh_summary()

def refresh_summary(event=None):
    try:
        travel_dates_thai, _, _ = build_travel_dates()
        summary_dates.config(text=travel_dates_thai)
    except Exception:
        summary_dates.config(text="—")

def add_hover(btn, normal_bg, hover_bg):
    def on_enter(_):
        if str(btn['state']) != 'disabled':
            btn.config(bg=hover_bg)
    def on_leave(_):
        if str(btn['state']) != 'disabled':
            btn.config(bg=normal_bg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def set_status(kind, text):
    colors = {"idle": TEXT_SUB, "sending": ACCENT, "success": GREEN, "error": RED}
    status_label.config(text=text, fg=colors.get(kind, TEXT_SUB))

# --- Send flow ---

def send_email():
    config = load_config()
    to_email = (config.get("to_email") or "").strip()
    cc_emails = config.get("cc_emails") or []
    if not to_email:
        set_status("error", "ไม่พบอีเมลผู้รับ (to_email) ใน config.json")
        return

    try:
        travel_dates_thai, travel_dates_numeric, template_file = build_travel_dates()
    except Exception:
        set_status("error", "วันที่ไม่ถูกต้อง กรุณาเลือกวันที่ใหม่")
        return

    # โหมด 2 วัน: ถามยืนยันก่อนถ้าวันที่สองซ้ำหรือย้อนหลังวันแรก
    if day_count_var.get() == 2:
        d1, d2 = cal1.get_date(), cal2.get_date()
        if d2 <= d1:
            problem = "เป็นวันเดียวกับวันแรก" if d2 == d1 else "อยู่ก่อนวันแรก"
            if not messagebox.askyesno(
                "ตรวจสอบวันที่",
                f"วันที่ที่สอง ({format_thai_date(d2)}) {problem}\nยืนยันจะส่งตามนี้หรือไม่?",
            ):
                return

    # ปิดปุ่มระหว่างส่งเพื่อกันการกดซ้ำ แล้วส่งบนเธรดแยกไม่ให้หน้าจอค้าง
    btn_send.config(state="disabled", bg=ACCENT_DISABLED, cursor="arrow")
    set_status("sending", "กำลังส่งอีเมล...")
    threading.Thread(
        target=send_worker,
        args=(to_email, cc_emails, travel_dates_thai, travel_dates_numeric,
              template_file, selected_file_path),
        daemon=True,
    ).start()

def send_worker(to_email, cc_emails, travel_dates_thai, travel_dates_numeric, template_file, attach_path):
    # ทำงานบนเธรดแยก — ห้ามแตะ widget ตรงๆ จากฟังก์ชันนี้ ให้ส่งผลผ่าน root.after เท่านั้น
    try:
        service = get_gmail_service()
        html_body = load_template(template_file, travel_dates_thai, travel_dates_numeric)

        message = MIMEMultipart()
        message['to'] = to_email
        if cc_emails:
            message['cc'] = ", ".join(cc_emails)
        message['subject'] = "ขออนุมัติเดินทางไปปฏิบัติงานสำหรับนักศึกษาฝึกงาน"
        message.attach(MIMEText(html_body, 'html'))

        if attach_path:
            content_type, _ = mimetypes.guess_type(attach_path)
            main_type, sub_type = (content_type or 'application/octet-stream').split('/', 1)
            with open(attach_path, 'rb') as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attach_path))
            message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        error = None
    except Exception as e:
        error = str(e)
    try:
        root.after(0, send_done, error, travel_dates_thai)
    except RuntimeError:
        pass  # หน้าต่างถูกปิดไปแล้วระหว่างส่ง

def send_done(error, travel_dates_thai):
    btn_send.config(state="normal", bg=ACCENT, cursor="hand2")
    if error:
        set_status("error", f"ส่งไม่สำเร็จ: {error}")
    else:
        set_status("success", f"✓ ส่งสำเร็จแล้ว ({travel_dates_thai})")

# --- GUI Setup ---
root = tk.Tk()
root.title("ระบบส่งเมลขออนุมัติเดินทาง")
root.configure(bg="#FFFFFF")
root.resizable(False, False)  # ขนาดหน้าต่างพอดีเนื้อหา

BG_WHITE = "#FFFFFF"
BORDER_GRAY = "#E2E8F0"
TEXT_MAIN = "#1A202C"
TEXT_SUB = "#718096"
ACCENT = "#2563EB"           # น้ำเงินหลัก
ACCENT_HOVER = "#1D4ED8"
ACCENT_DISABLED = "#93C5FD"  # สีปุ่มส่งระหว่างกำลังส่ง
SEG_HOVER = "#EFF6FF"        # hover ของปุ่ม segmented ฝั่งที่ยังไม่ถูกเลือก
BTN_GRAY = "#F7FAFC"
BTN_GRAY_HOVER = "#EDF2F7"
GREEN = "#16A34A"
RED = "#DC2626"

header_font = ("Sarabun", 15, "bold")
sub_font = ("Sarabun", 10, "bold")
normal_font = ("Sarabun", 10)
small_font = ("Sarabun", 9)

main_frame = tk.Frame(root, bg=BG_WHITE, padx=28, pady=22)
main_frame.pack(fill="both", expand=True)

# ตรึงความกว้างขั้นต่ำของเนื้อหา ไม่ให้หน้าต่างกว้างกระโดดตอนสลับโหมด 1/2 วัน
tk.Frame(main_frame, bg=BG_WHITE, height=1, width=380).pack()

tk.Label(main_frame, text="ส่งเมลขออนุมัติเดินทาง", font=header_font, fg=TEXT_MAIN, bg=BG_WHITE).pack(pady=(0, 16))

def make_card(title):
    card = tk.Frame(main_frame, bg=BG_WHITE, highlightbackground=BORDER_GRAY, highlightthickness=1, padx=16, pady=14)
    card.pack(fill="x", pady=(0, 10))
    tk.Label(card, text=title, font=sub_font, fg=TEXT_MAIN, bg=BG_WHITE).pack(anchor="w", pady=(0, 10))
    return card

# Section 1: Dates
section_dates = make_card("📅  วันที่เดินทาง")

day_count_var = tk.IntVar(value=1)

seg_frame = tk.Frame(section_dates, bg=BORDER_GRAY, highlightbackground=BORDER_GRAY, highlightthickness=1)
seg_frame.pack(fill="x", pady=(0, 12))
seg_frame.columnconfigure((0, 1), weight=1, uniform="segment")
btn_seg1 = tk.Button(seg_frame, text="1 วัน", font=sub_font, relief="flat", bd=0, pady=5,
                     cursor="hand2", command=lambda: set_day_mode(1))
btn_seg2 = tk.Button(seg_frame, text="2 วัน", font=sub_font, relief="flat", bd=0, pady=5,
                     cursor="hand2", command=lambda: set_day_mode(2))
btn_seg1.grid(row=0, column=0, sticky="ew")
btn_seg2.grid(row=0, column=1, sticky="ew", padx=(1, 0))  # เว้น 1px ให้เห็นเส้นแบ่งกลาง
btn_seg1.bind("<Enter>", lambda e: _segment_hover(btn_seg1, 1, True))
btn_seg1.bind("<Leave>", lambda e: _segment_hover(btn_seg1, 1, False))
btn_seg2.bind("<Enter>", lambda e: _segment_hover(btn_seg2, 2, True))
btn_seg2.bind("<Leave>", lambda e: _segment_hover(btn_seg2, 2, False))

date_grid = tk.Frame(section_dates, bg=BG_WHITE)
date_grid.pack(fill="x")
lbl_from = tk.Label(date_grid, text="วันที่:", font=normal_font, bg=BG_WHITE, fg=TEXT_MAIN, width=5, anchor="w")
lbl_from.grid(row=0, column=0, sticky="w", pady=4)
cal1 = DateEntry(date_grid, width=14, background=ACCENT, foreground='white', borderwidth=0,
                 date_pattern='dd/mm/yyyy', font=normal_font)
cal1.grid(row=0, column=1, padx=(10, 0), pady=4, sticky="w")
lbl_to = tk.Label(date_grid, text="ถึง:", font=normal_font, bg=BG_WHITE, fg=TEXT_MAIN, width=5, anchor="w")
lbl_to.grid(row=1, column=0, sticky="w", pady=4)
cal2 = DateEntry(date_grid, width=14, background=ACCENT, foreground='white', borderwidth=0,
                 date_pattern='dd/mm/yyyy', font=normal_font)
cal2.grid(row=1, column=1, padx=(10, 0), pady=4, sticky="w")
for cal in (cal1, cal2):
    cal.bind("<<DateEntrySelected>>", refresh_summary)
    cal.bind("<FocusOut>", refresh_summary)

# Section 2: Attachment
section_file = make_card("📎  ไฟล์แนบเอกสาร")
file_btn_frame = tk.Frame(section_file, bg=BG_WHITE)
file_btn_frame.pack(fill="x")
btn_pick = tk.Button(file_btn_frame, text="เลือกไฟล์", command=select_file, bg=BTN_GRAY, fg=TEXT_MAIN,
                     font=normal_font, relief="flat", highlightbackground=BORDER_GRAY, highlightthickness=1,
                     padx=18, cursor="hand2", activebackground=BTN_GRAY_HOVER)
btn_pick.pack(side="left", padx=(0, 8))
btn_clear = tk.Button(file_btn_frame, text="ล้าง", command=reset_file, bg=BG_WHITE, fg=TEXT_SUB,
                      font=normal_font, relief="flat", padx=10, cursor="hand2", activebackground=BTN_GRAY)
btn_clear.pack(side="left")
add_hover(btn_pick, BTN_GRAY, BTN_GRAY_HOVER)
add_hover(btn_clear, BG_WHITE, BTN_GRAY)
file_label = tk.Label(section_file, text="ยังไม่ได้เลือกไฟล์", font=small_font, fg=TEXT_SUB, bg=BG_WHITE,
                      wraplength=320, justify="left")
file_label.pack(anchor="w", pady=(8, 0))

# Section 3: Summary (สรุปผู้รับและวันที่ก่อนส่ง)
section_summary = make_card("📨  สรุปก่อนส่ง")
summary_grid = tk.Frame(section_summary, bg=BG_WHITE)
summary_grid.pack(fill="x")

def _summary_row(row, key, value):
    tk.Label(summary_grid, text=key, font=small_font, fg=TEXT_SUB, bg=BG_WHITE,
             width=7, anchor="nw").grid(row=row, column=0, sticky="nw", pady=1)
    lbl = tk.Label(summary_grid, text=value, font=small_font, fg=TEXT_MAIN, bg=BG_WHITE,
                   wraplength=265, justify="left", anchor="w")
    lbl.grid(row=row, column=1, sticky="w", pady=1)
    return lbl

_config = load_config()
_to_text = (_config.get("to_email") or "").strip() or "— (ตั้งค่าใน config.json)"
_cc_list = _config.get("cc_emails") or []
_cc_text = ", ".join(_cc_list) if _cc_list else "—"
_summary_row(0, "ถึง:", _to_text)
_summary_row(1, "สำเนา:", _cc_text)
summary_dates = _summary_row(2, "วันที่:", "—")

# Section 4: Send button + inline status
btn_send = tk.Button(main_frame, text="ส่งอีเมล", command=send_email, bg=ACCENT, fg="white",
                     font=("Sarabun", 11, "bold"), relief="flat", bd=0, pady=11, cursor="hand2",
                     activebackground=ACCENT_HOVER, activeforeground="white")
btn_send.pack(fill="x", pady=(8, 0))
add_hover(btn_send, ACCENT, ACCENT_HOVER)

status_label = tk.Label(main_frame, text=" ", font=small_font, fg=TEXT_SUB, bg=BG_WHITE,
                        wraplength=350, justify="center")
status_label.pack(fill="x", pady=(8, 0))

footer = tk.Label(main_frame, text="ส่งผ่าน Gmail API", font=("Sarabun", 8), fg="#CBD5E0", bg=BG_WHITE)
footer.pack(side="bottom", pady=(10, 0))

# ตั้งค่าเริ่มต้น: โหมด 1 วัน (ซ่อนช่อง "ถึง") + เติมสรุปวันที่ครั้งแรก
update_day_mode()

root.mainloop()
