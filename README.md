# 📦 Costco Receipt Analyzer

A complete system to **download, analyze, and visualize** your Costco purchase history (**in-warehouse** and **gas station** purchases)

This repository provides:

- Tools to download **all Costco receipts**  
- A Chrome extension for one-click downloading  
- A Streamlit dashboard for analyzing spending trends  
- Gas analytics, price tracking, merchandise stats, refunds & more  

---

## 🚀 Features

### 🧾 Receipt Downloader  
Two ways to download your Costco receipts:

1. **Manual Script** — paste into browser console  
2. **Chrome Extension** — one-click download

### 📊 Streamlit Dashboards  
Run dashboards in two ways:

1. **Hosted cloud app**:  
   https://costco.streamlit.app/
2. **Local Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

Dashboards include:

- Merchandise spending analytics  
- Gas price trends  
- Item price history  
- Price increases and decreases  
- Monthly spending  
- Refunds + instant savings  
- Executive rewards tracking 
- Item lookup + price table 

---

## 📂 Repository Structure

```
Costco-Analyzer/
│
├── Streamlit Dashboard/
│   ├── streamlit_app.py 
│   ├── helper.py  
│
├── manual_receipt_downloader.js
│
├── Receipt Downloader Extension/
│   ├── popup.html
│   ├── popup.js
│   ├── content.js
│   └── manifest.json
│
└── README.md
```

---

# 🔽 Downloading Costco Receipts

## Option A — **Manual Script (No extension required)**

1. Log in at  
   **https://www.costco.com/myaccount/ordersandpurchases**
2. Right-click → **Inspect**
3. Go to the **Console**
4. Paste the script found at:

```
manual_receipt_downloader.js
```

5. Modify the date range if needed:

```js
const FROM_DATE = "01/01/2023";
const TO_DATE   = "12/31/2025";
```

6. Hit **Enter**

➡️ A `.json` file containing all receipts will automatically download.

---

## Option B — **Chrome Extension (Best user experience)**

### 1. Install the extension manually

1. Open Chrome → visit:  
   **chrome://extensions/**
2. Turn on **Developer Mode**
3. Click **Load Unpacked**
4. Select:

```
Costco-Analyzer/Receipt Downloader Extension/
```

### 2. Use the extension

1. Visit Costco order history at **https://www.costco.com/myaccount/ordersandpurchases** 
2. Click the extension  
3. Choose dates  
4. Press **Download Receipts**

➡️ A JSON file downloads with all receipts.

---

# 📊 Running the Dashboards

## Option 1 — **Hosted Cloud Dashboard**

👉 **https://costco.streamlit.app**

Upload your JSON file.

---

## Option 2 — **Run Locally**

```bash
git clone https://github.com/SanketKumarP/Costco-Analyzer
cd costco-analyzer
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

# 📘 Dashboard Overview

### 🛒 Merchandise Dashboard
- Net spend  
- Refunds  
- 2% Executive rewards  
 
- Monthly spend  
- Most purchased 
- Most expensive items  

### ⛽ Gas Dashboard
- Gallons purchased  
- Average price/gallons  
- Regular vs Premium split  
- Monthly gas trends  
- Gas price history  

### 📈 Price Trends & Lookup
- Price increases/decreases
- Item search  
- Price history  
- Min/max/avg price  
- Price drops & hikes  

---

# 🧩 JSON File Format

Includes:

- Item arrays  
- Fuel quantities  
- Tender arrays  
- Refunds  
- Instant savings  
- Taxes  
- Gas vs warehouse detection  

---

# ⭐ Credits

Created by **Sanket Patel**  
