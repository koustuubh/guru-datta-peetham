# 🕉️ గురు దత్త పీఠం (Guru Datta Peetham) & Rushivani Spiritual E-Commerce Portal

Official full-stack spiritual e-commerce portal, devotee center, and sacred discourse hub for **Guru Datta Peetham Charitable Trust (Reg No. 172/2022)** and the **Rushivani (ఋషివాణి)** YouTube channel, under the guidance of **Guruji Dr. Shanmukha Srinivas (Swamy Kamalananda Naadha)**.

---

## 🌟 Key Features

1. **Sacred Consecrated Store**:
   - Original Karungali Malas (108 Ebony Wood Beads)
   - Natural Black & Red Hakik Malas (Evil eye / Drishti & vitality)
   - Lab-Certified 5-Mukhi Nepali Rudraksha & Rare 1-Mukhi in Pure Silver
   - Sacred Gauri Shankar Rudraksha & Audumbar Wood Japa Malas
   - Consecrated Pure Brass Lord Dattatreya Murtis & Holy Charan Padukas
2. **Real-Time YouTube Integration (@Rushivani)**:
   - **Community Posts**: Direct feeds from `https://www.youtube.com/@Rushivani/posts` with auto CDN images and clickable post links.
   - **Shorts Grid**: Dynamic feed with automatic high-res thumbnails (`hqdefault.jpg`) and direct short links.
   - **Pravachanams & Discourses**: Clickable videos with an inline HD modal player or direct YouTube viewing.
3. **Professional Admin Dashboard (`admin` / `datta123`)**:
   - **Orders & Transactions**: View all devotee orders with UTR numbers, toggle payment verification (`PAID & VERIFIED`), and 1-click WhatsApp messaging.
   - **Items & Rates Management**: Live inline price/rate editor ("Save ₹"), new product addition, and item deletion.
   - **Devotee Issues**: View helpdesk tickets, contact devotees via WhatsApp, and resolve issues.
4. **Checkout & Payments**:
   - Dynamic **NPCI-standard UPI QR Code** pre-filled with order total for PhonePe, GPay, Paytm, and BHIM.
   - 12-digit UPI UTR transaction reference number entry for admin verification.
   - `☑️ This phone number has WhatsApp` checkbox for delivery tracking.
5. **Devotee Experience**:
   - Sign in with Google Account (Google Identity Services GIS).
   - Devotee Helpdesk modal to report queries and order issues.
   - Sticky shrinking navbar on scroll.
   - App-style mobile bottom navigation dock.
6. **Official Community Links**:
   - 🟢 WhatsApp Group: `https://chat.whatsapp.com/KgyjjEVbtuECHJtjUqaFOo`
   - 🔴 YouTube Channel: `https://www.youtube.com/channel/UCLVHMA1p2eglQPnjMxen7ng`
   - 📢 Community Tab: `https://www.youtube.com/channel/UCLVHMA1p2eglQPnjMxen7ng/community`
   - 🌐 Official Website: `https://www.Gurudattapeetham.org`
   - 🔵 Facebook Page: `https://www.facebook.com/RushivaniFB`
   - ✨ **JAI GURU DEVA DATTA**

---

## 🚀 Tech Stack

- **Frontend**: Semantic HTML5, Pure Vanilla CSS3 (Custom Properties, Flexbox, Grid, Touch Momentum), Modern JavaScript (ES6+ Fetch API, LocalStorage).
- **Backend**: Python 3.10+, Flask 3.0+, Werkzeug WSGI server.
- **Database**: Dual-Engine architecture — Oracle DBMS (`python-oracledb` 23ai / 21c XE / FreePDB1) with automatic zero-configuration SQLite fallback (`divine_store.db`).
- **Media**: YouTube Atom RSS feeds and YouTube CDN (`yt3.ggpht.com` & `i.ytimg.com`).

---

## ⚡ Quick Start

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run all 13 automated unit tests
python test_app.py

# 4. Start the portal
python app.py
```

Server starts at: `http://localhost:5001`

---

## 📦 Push to GitHub

To push this repository to your GitHub account (`koustuubh`):

```bash
# 1. Add your remote repository URL (create 'guru-datta-peetham' on GitHub first)
git remote add origin https://github.com/koustuubh/guru-datta-peetham.git

# 2. Push code to main branch
git branch -M main
git push -u origin main
```
