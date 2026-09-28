from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = "zak-tools-secret-2025"

INSTAGRAM_URL = "https://www.instagram.com/_u.wej"
SAVETIK_API = "https://savetik.co/api/ajaxSearch"

HEADERS_SAVETIK = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://savetik.co",
    "Referer": "https://savetik.co/ar",
}


@app.context_processor
def inject_globals():
    return {"instagram_url": INSTAGRAM_URL}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tiktok")
def tiktok():
    return render_template("tiktok.html")


@app.route("/api/tiktok", methods=["POST"])
def api_tiktok():
    url = request.form.get("url", "").strip()

    if not url:
        return jsonify({"status": "error", "message": "الرجاء إدخال رابط"}), 400

    if "tiktok.com" not in url and "vt.tiktok" not in url:
        return jsonify({"status": "error", "message": "رابط غير صالح"}), 400

    try:
        r = requests.post(
            SAVETIK_API,
            data={"q": url, "lang": "ar", "cftoken": ""},
            headers=HEADERS_SAVETIK,
            timeout=40,
        )
    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "message": "انتهت مدة الانتظار، جرّب مرة أخرى"}), 504
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ في الاتصال: {e}"}), 502

    ct = r.headers.get("Content-Type", "")
    if "json" not in ct:
        return jsonify({
            "status": "error",
            "message": "الخدمة مشغولة حالياً، جرّب بعد قليل"
        }), 502

    try:
        data = r.json()
    except Exception:
        return jsonify({"status": "error", "message": "رد غير صالح من الخادم"}), 502

    if data.get("status") != "ok":
        return jsonify({"status": "error", "message": "فشل جلب الفيديو"}), 400

    html = data.get("data", "")
    soup = BeautifulSoup(html, "html.parser")

    result = {
        "status": "ok",
        "title": "",
        "thumbnail": "",
        "video_id": "",
        "downloads": [],
    }

    h3 = soup.find("h3")
    if h3:
        result["title"] = h3.get_text(strip=True)

    img = soup.find("img")
    if img and img.get("src"):
        result["thumbnail"] = img["src"]

    hidden = soup.find("input", {"id": "TikTokId"})
    if hidden:
        result["video_id"] = hidden.get("value", "")

    for a in soup.find_all("a", class_=re.compile("tik-button-dl")):
        text = a.get_text(strip=True)
        href = a.get("href", "")
        if not href or "snapcdn" not in href:
            continue

        if "MP3" in text:
            result["downloads"].append({
                "type": "mp3",
                "label": "🎵 تحميل الصوت MP3",
                "url": href,
            })
        elif "HD" in text:
            result["downloads"].append({
                "type": "mp4_hd",
                "label": "🎬 تحميل MP4 HD",
                "url": href,
            })
        elif "MP4" in text:
            result["downloads"].append({
                "type": "mp4",
                "label": "📹 تحميل MP4",
                "url": href,
            })

    if not result["downloads"]:
        return jsonify({
            "status": "error",
            "message": "لم يتم إيجاد روابط تحميل، الفيديو قد يكون محذوفاً أو خاصاً"
        }), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
