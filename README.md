# Gmail Approval Sender (GUI Version)

สคริปต์ Python สำหรับส่งอีเมลขออนุมัติเดินทางผ่าน Gmail API พร้อมหน้าจอ UI ที่สวยงามและใช้งานง่าย

## 🌟 คุณสมบัติ
- **Date Picker:** เลือกวันที่เดินทางได้จากปฏิทิน ไม่ต้องพิมพ์เอง
- **Clean UI:** หน้าจอออกแบบสไตล์ Minimal ขาว-เทา สะอาดตา อ่านง่าย
- **Dynamic Content:** โหลดอีเมลผู้รับจากไฟล์ภายนอก และใช้เทมเพลต HTML แยกส่วน
- **Attachment Support:** รองรับการแนบไฟล์เอกสาร (PDF, รูปภาพ ฯลฯ)
- **Secure:** ใช้ Gmail API มาตรฐานความปลอดภัยสูงจาก Google

## 📁 โครงสร้างไฟล์
- `send_gmail_gui.py`: ไฟล์สคริปต์หลัก (UI & Logic)
- `config.json`: เก็บรายชื่ออีเมลผู้รับ (To, CC)
- `email_template.html`: โครงสร้างหน้าตาอีเมลแบบ HTML
- `client_secret_xxx.json`: ไฟล์กุญแจ API จาก Google Cloud (ห้ามแชร์)
- `.gitignore`: ไฟล์สำหรับป้องกันการอัพโหลดไฟล์ความลับขึ้น GitHub

## 🛠 การติดตั้ง (Setup)
1. ติดตั้ง Python 3.x ในเครื่อง
2. ติดตั้ง Library ที่จำเป็นผ่าน Terminal:
   ```powershell
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib tkcalendar
   ```

## 🚀 วิธีใช้งาน
1. เตรียมไฟล์ `client_secret_xxx.json` ไว้ในโฟลเดอร์เดียวกับสคริปต์
2. ตั้งค่าอีเมลผู้รับใน `config.json`
3. แก้ไขเนื้อหาหรือดีไซน์อีเมลใน `email_template.html` (ถ้ามี)
4. สั่งรันโปรแกรม:
   ```powershell
   python send_gmail_gui.py
   ```
5. ในการรันครั้งแรก ระบบจะให้ยืนยันสิทธิ์ผ่านเว็บเบราว์เซอร์

## 🔒 ความปลอดภัย (Security)
- **ห้าม** นำไฟล์ `config.json`, `token.json` และ `client_secret*.json` ขึ้นระบบจัดการเวอร์ชัน (เช่น Git) เด็ดขาด เพราะมีข้อมูลส่วนตัวและกุญแจ API ที่อาจรั่วไหลได้
- ไฟล์ `.gitignore` ของโปรเจกต์ตั้งค่าให้ติดตามเฉพาะไฟล์ `*.py` เท่านั้น (ละเว้นไฟล์อื่นทั้งหมด) ดังนั้นไฟล์ความลับเหล่านี้จึงถูกกันออกจาก Git ให้โดยอัตโนมัติอยู่แล้ว

---
*Created with ❤️ by Gemini CLI Assistant*
"# python-gmail-automation" 
