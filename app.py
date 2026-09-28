from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import requests
import time
import re

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
                last_error = "الخدمة مشغولة، جرّب بعد قليل"
                time.sleep(2)
                continue
            try:
                data = r.json()
            except Exception:
                last_error = "رد غير صالح"
                time.sleep(2)
                continue
            if data.get("code") != 0:
                last_error = data.get("msg") or "فشل جلب الفيديو"
                time.sleep(2)
                continue
            return data, None
        except requests.exceptions.Timeout:
            last_error = "انتهت مدة الانتظار"
            time.sleep(2)
        except Exception as e:
            last_error = f"خطأ: {e}"
            time.sleep(2)
    return None, last_error


def fix_url(u):
    if not u:
        return ""
    if u.startswith("//"):
        return "https:" + u
    return u


def sanitize_filename(name, max_len=60):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return (name[:max_len] or "tiktok_video")


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

    title = video_data.get("title", "") or "tiktok_video"
    safe_name = sanitize_filename(title)

    result = {
        "status": "ok",
        "title": video_data.get("title", "") or "فيديو تيك توك",
        "thumbnail": fix_url(video_data.get("cover") or video_data.get("origin_cover", "")),
        "video_id": str(video_data.get("id", "")),
        "safe_name": safe_name,
        "downloads": [],
    }

    play_url = fix_url(video_data.get("play", ""))
    hd_url = fix_url(video_data.get("hdplay", ""))
    music_url = fix_url(video_data.get("music", ""))

    if play_url:
        result["downloads"].append({
            "type": "mp4",
            "label": "📹 تحميل MP4 (بدون علامة مائية)",
            "url": play_url,
            "filename": safe_name + ".mp4",
        })

    if hd_url and hd_url != play_url:
        result["downloads"].append({
            "type": "mp4_hd",
            "label": "🎬 تحميل MP4 HD",
            "url": hd_url,
            "filename": safe_name + "_HD.mp4",
        })

    if music_url:
        result["downloads"].append({
            "type": "mp3",
            "label": "🎵 تحميل الصوت MP3",
            "url": music_url,
            "filename": safe_name + ".mp3",
        })

    if not result["downloads"]:
        return jsonify({"status": "error", "message": "لم يتم إيجاد روابط تحميل"}), 400

    return jsonify(result)


@app.route("/download")
def download():
    """يمرّر الملف من TikWM إلى المستخدم مع Content-Disposition: attachment"""
    video_url = request.args.get("url", "").strip()
    filename = request.args.get("filename", "video.mp4").strip()

    if not video_url:
        return "الرابط مفقود", 400

    # تنظيف اسم الملف
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
    if not filename:
        filename = "video.mp4"

    try:
        # جلب الملف من المصدر
        r = requests.get(
            video_url,
            headers={
                "User-Agent": HEADERS_TIKWM["User-Agent"],
                "Referer": "https://www.tiktok.com/",
            },
            stream=True,
            timeout=60,
        )
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "application/octet-stream")
        content_length = r.headers.get("Content-Length")

        def generate():
            for chunk in r.iter_content(chunk_size=64 * 1024):
                if chunk:
                    yield chunk

        # بناء الرؤوس
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": content_type,
            "Cache-Control": "no-cache",
        }
        if content_length:
            headers["Content-Length"] = content_length

        return Response(
            stream_with_context(generate()),
            headers=headers,
        )

    except Exception as e:
        return f"خطأ في التحميل: {e}", 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
