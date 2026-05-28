URL PARAMETER FINDER

Simple and fast website crawler for discovering URLs containing GET parameters.

---

Features

- Internal Website Crawling
- Automatic URL Parameter Discovery
- GET Parameter Extraction
- JavaScript URL Detection
- Form Action Enumeration
- iframe Source Detection
- Image URL Analysis
- Data Attribute Extraction
- Internal Link Enumeration
- Domain Restriction (same target only)
- Auto Redirect Handling
- Duplicate URL Filtering
- BeautifulSoup Parsing Mode (accurate)
- Regex Mode (fast & lightweight)
- Crawl Limit Control
- Real-Time Found Logger
- Auto Save Results to file
- Session Reuse for performance
- Crawl statistics report

---

Requirements

pip install requests beautifulsoup4

---

Usage

python finder.py


---

Modes

1. BeautifulSoup Mode (Recommended)

- More accurate
- Better HTML parsing
- Finds deeper structured links

2. Regex Mode (Fast)

- Lightweight
- Faster execution
- Suitable for Termux / low-end devices

---

Example Output

[FOUND] https://example.com/news.php?id=1
[FOUND] https://example.com/view.php?post=25

Selesai!
Total ditemukan : 2 URL
Halaman di-crawl: 45
Tersimpan di    : found_params_example_com.txt

---

Output File

Automatically saved as:

found_params_domain_YYYYMMDD_HHMMSS.txt

Example:

https://example.com/news.php?id=1
https://example.com/view.php?post=25
https://example.com/search.php?q=test

---

Platform Support

Platform| Status
Termux (Android)| ✅ Supported
Pydroid 3 (Android)| ✅ Supported

---

Termux Installation

pkg update && pkg upgrade -y
pkg install python -y
pip install requests beautifulsoup4

Run:

python finder.py

---

Pydroid 3 Installation

Install dependencies inside Pydroid terminal:

pip install requests beautifulsoup4

Then run script directly.

---

Supported Sources

Crawler extracts URLs from:

- "<a href>"
- "<form action>"
- "<script src>"
- "<iframe src>"
- "<img src>"
- "<link href>"
- JavaScript code
- Event handlers
- Data attributes

---

Notes

- Only works within the same domain
- Filters static files (images, CSS, JS, videos)
- Designed for reconnaissance / URL discovery only
- Does NOT include exploitation or attack features

---

Disclaimer

This tool is intended for educational purposes and authorized security testing only.
Use only on systems you own or have explicit permission to test.

Misuse is strictly discouraged.

---

Author

Dev : Ohang
Telegram : Cyber Operation Culture MY
