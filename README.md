**Let's Assemble Random Bops (LARB)**
-------------------------------------

*Utility for EN Hip Dance Club KKU*

---
Please ensure to install dependencies library with

*$ pip install yt-dlp moviepy sanitize-filename*

---

This executable Python file will download videos from Toutube
with retrieved data in */data/entry.csv* and follow settings in
*settings.json*

Please keep in mind to check *settings.json* before execute

CSV can be varied but these are needed columns (defined in *settings.json*)
- song_title
- song_artist
- url (www.youtube.com/watch?v=VIDEO_ID)
- start_ts (hh:mm:ss)
- end_ts (hh:mm:ss)
- is_mirrored (OPTIONAL)

Available space needed is varied from 100MB to 3GB
depends on songs amount in CSV and mp3_only mode

<br>
<br>

**Let's Assemble Random Bops (LARB)**
-------------------------------------

*เครื่องมือของชุมนุม EN Hip Dance Club KKU*

---
กรุณา install dependencies ให้ครบ ด้วยคำสั่ง

*$ pip install yt-dlp moviepy sanitize-filename*

---

ไฟล์ Python นี้จะทำงานโดยการดาวน์โหลดวีดิโอจาก Youtube
ตามข้อมูลที่ได้จาก */data/entry.csv* และตามการตั้งค่าใน
*settings.json*

กรุณาตรวจสอบ *settings.json* ก่อนเริ่มการทำงานทุกครั้ง

ตำแหน่งคอลัมน์ใน CSV เปลี่ยนแปลงได้ แต่ต้องมีคอลัมน์ที่มีข้อมูลเหล่านี้ (ระบุไว้ใน *settings.json*)
- song_title
- song_artist
- url (www.youtube.com/watch?v=VIDEO_ID)
- start_ts (hh:mm:ss)
- end_ts (hh:mm:ss)
- is_mirrored (ไม่บังคับ)

พื้นที่ว่างที่ต้องการมีตั้งแต่ 100MB ถึง 3GB
ขึ้นอยู่กับจำนวนเพลงในไฟล์ CSV และการตั้งค่า mp3_only
