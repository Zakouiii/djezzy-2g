from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)
app.secret_key = "dz-save-secret-2025"

INSTAGRAM_URL = "https://www.instagram.com/_u.wej"
TIKWM_API = "https://tikwm.com/api/"

HEADERS_TIKWM = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ar,fr;q=0.9,en;q=0.8",
    "Referer": "https://tikwm.com/",
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


def try_tikwm(url, max_retries=3):
    """يحاول TikWM مع إعادة المحاولة"""
    last_error = "فشل الاتصال"

    for attempt in range(max_retries):
        try:
            r = requests.get(
                TIKWM_API,
                params={"url": url, "hd": "1"},
                headers=HEADERS_TIKWM,
                timeout=30,
            )

            ct = r.headers.get("Content-Type", "")
            if "json" not in ct:
                print(f"[المحاولة {attempt+1}] رد غير JSON: {r.text[:200]}")
                last_error = "الخدمة مشغولة، جرّب بعد قليل"
                time.sleep(2)
                continue

            try:
                data = r.json()
            except Exception as e:
                print(f"[المحاولة {attempt+1}] خطأ JSON: {e}")
                last_error = "رد غير صالح"
                time.sleep(2)
                continue

            if data.get("code") != 0:
                msg = data.get("msg") or "فشل جلب الفيديو"
                print(f"[المحاولة {attempt+1}] code != 0: {msg}")
                last_error = msg
                time.sleep(2)
                continue

            return data, None

        except requests.exceptions.Timeout:
            print(f"[المحاولة {attempt+1}] Timeout")
            last_error = "انتهت مدة الانتظار"
            time.sleep(2)
        except Exception as e:
            print(f"[المحاولة {attempt+1}] خطأ: {e}")
            last_error = f"خطأ: {e}"
            time.sleep(2)

    return None, last_error


def fix_url(u):
    """يصلح الروابط النسبية (//...)"""
    if not u:
        return ""
    if u.startswith("//"):
        return "https:" + u
    return u


@app.route("/api/tiktok", methods=["POST"])
def api_tiktok():
    url = request.form.get("url", "").strip()

    if not url:
        return jsonify({"status": "error", "message": "الرجاء إدخال رابط"}), 400

    if "tiktok.com" not in url and "vt.tiktok" not in url:
        return jsonify({"status": "error", "message": "رابط غير صالح"}), 400

    data, err = try_tikwm(url)

    if err:
        return jsonify({"status": "error", "message": err}), 502

    video_data = data.get("data", {})
    if not video_data:
        return jsonify({"status": "error", "message": "لم يتم إيجاد الفيديو"}), 400

    # بناء النتيجة
    result = {
        "status": "ok",
        "title": video_data.get("title", "") or "فيديو تيك توك",
        "thumbnail": fix_url(video_data.get("cover")
                             or video_data.get("origin_cover", "")),
        "video_id": str(video_data.get("id", "")),
        "downloads": [],
    }

    # الروابط
    play_url = fix_url(video_data.get("play", ""))
    hd_url = fix_url(video_data.get("hdplay", ""))
    music_url = fix_url(video_data.get("music", ""))

    # MP4 عادي
    if play_url:
        result["downloads"].append({
            "type": "mp4",
            "label": "📹 تحميل MP4 (بدون علامة مائية)",
            "url": play_url,
        })

    # MP4 HD
    if hd_url and hd_url != play_url:
        result["downloads"].append({
            "type": "mp4_hd",
            "label": "🎬 تحميل MP4 HD",
            "url": hd_url,
        })

    # MP3
    if music_url:
        result["downloads"].append({
            "type": "mp3",
            "label": "🎵 تحميل الصوت MP3",
            "url": music_url,
        })

    if not result["downloads"]:
        return jsonify({
            "status": "error",
            "message": "لم يتم إيجاد روابط تحميل"
        }), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
