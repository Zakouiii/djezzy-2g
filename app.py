from flask import Flask, request, jsonify, Response
import uuid, time

app = Flask(__name__)

# ============================================
#  الإعدادات — غيّرها لقيم سرية
# ============================================
API_KEY = "zakaria-website-key-2026"
DEVICE_KEY = "zakaria-device-key-2026"

# ============================================
#  الذاكرة
# ============================================
pending = {}
results = {}
devices = {}


# ============================================
#  HTML مدمج — الصفحة الرئيسية
# ============================================
INDEX_HTML = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🎁 تفعيل 2 جيجا - جيزي</title>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: system-ui, -apple-system, sans-serif;
    background: linear-gradient(135deg, #E60000 0%, #990000 100%);
    margin: 0; padding: 20px; min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
  }
  .box {
    max-width: 420px; width: 100%; background: #fff;
    border-radius: 20px; padding: 30px 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,.3);
  }
  .logo { text-align: center; font-size: 60px; margin-bottom: 10px; }
  h1 { color: #E60000; text-align: center; margin: 0 0 8px; font-size: 24px; }
  .sub { text-align: center; color: #666; font-size: 14px; margin-bottom: 24px; }
  label { display: block; margin: 12px 0 6px; color: #333; font-size: 14px; font-weight: 600; }
  input {
    width: 100%; padding: 14px; border: 2px solid #eee;
    border-radius: 12px; font-size: 16px;
  }
  input:focus { outline: none; border-color: #E60000; }
  button {
    width: 100%; padding: 14px; background: #E60000; color: #fff;
    border: none; border-radius: 12px; font-size: 16px;
    font-weight: 600; margin-top: 12px; cursor: pointer;
  }
  button:disabled { opacity: .5; cursor: not-allowed; }
  .success-btn { background: #4CAF50; }
  .activate-btn { background: #FF9800; }
  #status { margin-top: 20px; padding: 14px; border-radius: 12px;
            text-align: center; font-size: 14px; font-weight: 600; display: none; }
  .ok { background: #e8f5e9; color: #2e7d32; display: block !important; }
  .err { background: #ffebee; color: #c62828; display: block !important; }
  .info { background: #e3f2fd; color: #1565c0; display: block !important; }
</style>
</head>
<body>
<div class="box">
  <div class="logo">🎁</div>
  <h1>تفعيل 2 جيجا مجاناً</h1>
  <p class="sub">جيزي الجزائر - GIFTWALKWIN</p>

  <label>📱 رقم هاتفك</label>
  <input id="phone" type="tel" placeholder="213XXXXXXXXX" />

  <button id="btnOtp" onclick="sendOtp()">📩 إرسال الرمز</button>

  <label>🔐 الرمز المُستلم</label>
  <input id="otp" type="text" placeholder="أدخل الرمز" maxlength="6" />

  <button id="btnLogin" class="success-btn" onclick="doLogin()" disabled>✅ تسجيل الدخول</button>
  <button id="btnActivate" class="activate-btn" onclick="activate()" disabled>🎉 تفعيل 2 جيجا</button>

  <div id="status"></div>
</div>

<script>
const HOST = window.location.origin;
const API_KEY = "zakaria-website-key-2026";

function setStatus(msg, cls) {
  const el = document.getElementById('status');
  el.textContent = msg;
  el.className = cls || 'info';
}

async function sendRequest(action, payload) {
  const r = await fetch(HOST + '/api/request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Api-Key': API_KEY },
    body: JSON.stringify({ action, payload })
  });
  if (!r.ok) throw new Error('فشل الاتصال');
  const { id } = await r.json();
  for (let i = 0; i < 40; i++) {
    await new Promise(res => setTimeout(res, 1500));
    const rr = await fetch(HOST + '/api/result/' + id, {
      headers: { 'X-Api-Key': API_KEY }
    });
    const data = await rr.json();
    if (data.status === 'done') return data.data;
    if (data.status === 'not_found') throw new Error('انتهت الجلسة');
  }
  throw new Error('انتهت المهلة');
}

async function sendOtp() {
  const phone = document.getElementById('phone').value.trim();
  if (!phone) return setStatus('أدخل رقمك', 'err');
  setStatus('⏳ جاري الإرسال...', 'info');
  document.getElementById('btnOtp').disabled = true;
  try {
    await sendRequest('send_otp', { phone });
    setStatus('✅ تم إرسال الرمز', 'ok');
    document.getElementById('btnLogin').disabled = false;
  } catch (e) {
    setStatus('❌ ' + e.message, 'err');
  } finally {
    document.getElementById('btnOtp').disabled = false;
  }
}

async function doLogin() {
  const phone = document.getElementById('phone').value.trim();
  const otp = document.getElementById('otp').value.trim();
  if (!otp) return setStatus('أدخل الرمز', 'err');
  setStatus('⏳ جاري التحقق...', 'info');
  document.getElementById('btnLogin').disabled = true;
  try {
    const res = await sendRequest('login', { phone, otp });
    if (!res.access_token) throw new Error('فشل تسجيل الدخول');
    localStorage.setItem('token', res.access_token);
    setStatus('✅ تم تسجيل الدخول', 'ok');
    document.getElementById('btnActivate').disabled = false;
  } catch (e) {
    setStatus('❌ ' + e.message, 'err');
    document.getElementById('btnLogin').disabled = false;
  }
}

async function activate() {
  const token = localStorage.getItem('token');
  const phone = document.getElementById('phone').value.trim();
  setStatus('⏳ جاري التفعيل...', 'info');
  document.getElementById('btnActivate').disabled = true;
  try {
    const res = await sendRequest('activate_2g', { token, phone });
    if (res.error) throw new Error(res.message || res.error);
    setStatus('🎉 تم التفعيل بنجاح!', 'ok');
  } catch (e) {
    setStatus('❌ ' + e.message, 'err');
    document.getElementById('btnActivate').disabled = false;
  }
}
</script>
</body>
</html>
"""


# ============================================
#  المسارات
# ============================================

@app.route('/')
def index():
    return Response(INDEX_HTML, mimetype='text/html; charset=utf-8')


@app.route('/api/request', methods=['POST'])
def add_request():
    if request.headers.get('X-Api-Key') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    req_id = str(uuid.uuid4())
    pending[req_id] = {
        "id": req_id,
        "action": data.get("action"),
        "payload": data.get("payload", {}),
        "created_at": time.time()
    }
    return jsonify({"id": req_id, "status": "queued"})


@app.route('/api/result/<req_id>', methods=['GET'])
def get_result(req_id):
    if request.headers.get('X-Api-Key') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    if req_id in results:
        result = results[req_id]
        del results[req_id]
        return jsonify({"status": "done", "data": result})
    if req_id in pending:
        return jsonify({"status": "pending"})
    return jsonify({"status": "not_found"}), 404


@app.route('/api/device/register', methods=['POST'])
def register_device():
    if request.headers.get('X-Device-Key') != DEVICE_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    device_id = request.json.get("device_id")
    devices[device_id] = {"id": device_id, "last_seen": time.time()}
    return jsonify({"status": "registered"})


@app.route('/api/device/fetch', methods=['GET'])
def fetch_pending():
    if request.headers.get('X-Device-Key') != DEVICE_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    device_id = request.headers.get('X-Device-Id')
    if device_id in devices:
        devices[device_id]["last_seen"] = time.time()
    return jsonify({"requests": list(pending.values())})


@app.route('/api/device/result/<req_id>', methods=['POST'])
def device_send_result(req_id):
    if request.headers.get('X-Device-Key') != DEVICE_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    results[req_id] = request.json.get("data", {})
    if req_id in pending:
        del pending[req_id]
    return jsonify({"status": "ok"})


@app.route('/status')
def status():
    return jsonify({
        "devices_online": len([d for d in devices.values()
                               if time.time() - d["last_seen"] < 60]),
        "pending_requests": len(pending),
        "total_devices": len(devices)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
