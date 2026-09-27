from flask import Flask, render_template, request, Response, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)
app.secret_key = "change-this-secret-key-12345"

TARGET_BASE = "https://takipcikutusu.com"
PROXY_PREFIX = "/proxy"

# رؤوس مشابهة للمتصفح لتجنب الحظر
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,fr;q=0.9,en;q=0.8",
    "Referer": TARGET_BASE,
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/member")
def member():
    """صفحة العرض داخل موقعك"""
    return render_template("member.html", proxy_url=f"{PROXY_PREFIX}/member")

@app.route(f"{PROXY_PREFIX}/<path:path>", methods=["GET", "POST"])
def proxy(path):
    """البروكسي: يجلب الموقع الأصلي ويعرضه داخل موقعك"""
    target_url = f"{TARGET_BASE}/{path}"
    
    # تمرير معاملات الاستعلام
    if request.query_string:
        target_url += "?" + request.query_string.decode()

    try:
        if request.method == "POST":
            r = requests.post(target_url, data=request.form, headers=HEADERS,
                              cookies=request.cookies, timeout=20, allow_redirects=False)
        else:
            r = requests.get(target_url, headers=HEADERS,
                             cookies=request.cookies, timeout=20, allow_redirects=False)
    except Exception as e:
        return f"<h2>خطأ في الاتصال بالموقع الأصلي</h2><p>{e}</p>", 502

    # معالجة الروابط داخل HTML لتوجيهها إلى البروكسي
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
        
        html = str(soup)
    else:
        html = r.content

    # إعداد الاستجابة مع تمرير الكوكيز
    resp = Response(html, status=r.status_code, content_type=content_type or "text/html")
    for cookie in r.cookies:
        resp.set_cookie(cookie.name, cookie.value, domain=None)
    
    # إزالة الرؤوس التي تمنع العرض
    resp.headers.pop("X-Frame-Options", None)
    resp.headers.pop("Content-Security-Policy", None)
    
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
