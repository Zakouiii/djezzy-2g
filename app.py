from flask import Flask, request, jsonify, Response
import uuid, time

app = Flask(__name__)

API_KEY = "zakaria-website-key-2026"
DEVICE_KEY = "zakaria-device-key-2026"

pending = {}
results = {}
devices = {}


INDEX_HTML = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🎁 خدمات جيزي</title>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: system-ui, -apple-system, sans-serif;
    background: linear-gradient(135deg, #E60000 0%, #990000 100%);
    margin: 0; padding: 20px; min-height: 100vh;
    display: flex; align-items: flex-start; justify-content: center;
  }
  .box {
    max-width: 440px; width: 100%; background: #fff;
    border-radius: 20px; padding: 30px 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,.3);
    margin-top: 20px;
  }
  .logo { text-align: center; font-size: 50px; margin-bottom: 8px; }
  h1 { color: #E60000; text-align: center; margin: 0 0 8px; font-size: 22px; }
  .sub { text-align: center; color: #666; font-size: 13px; margin-bottom: 20px; }
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
  .balance-btn { background: #2196F3; }
  .telegram-btn { background: #0088cc; }
  .channel-btn { background: #0088cc; }
  
  #status { margin-top: 16px; padding: 14px; border-radius: 12px;
            text-align: center; font-size: 14px; font-weight: 600; display: none; }
  .ok { background: #e8f5e9; color: #2e7d32; display: block !important; }
  .err { background: #ffebee; color: #c62828; display: block !important; }
  .info { background: #e3f2fd; color: #1565c0; display: block !important; }

  /* قسم المعلومات */
  .info-section {
    display: none;
    margin-top: 20px;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 16px;
    border: 2px solid #eee;
  }
  .info-section h3 {
    color: #E60000;
    font-size: 18px;
    margin: 0 0 16px;
    text-align: center;
  }
  .balance-card {
    background: linear-gradient(135deg, #E60000, #990000);
    color: #fff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 16px;
  }
  .balance-card .amount {
    font-size: 32px;
    font-weight: bold;
    margin: 8px 0;
  }
  .balance-card .currency {
    font-size: 14px;
    opacity: 0.8;
  }
  .product-card {
    background: #fff;
    padding: 14px;
    border-radius: 10px;
    border-right: 4px solid #4CAF50;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
  }
  .product-card .name {
    font-weight: 600;
    color: #333;
    margin-bottom: 6px;
    font-size: 15px;
  }
  .product-card .detail {
    color: #666;
    font-size: 13px;
    margin: 3px 0;
  }
  .product-card .remaining {
    color: #4CAF50;
    font-weight: 600;
    font-size: 14px;
  }
  .footer {
    text-align: center;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid #eee;
  }
  .footer .developer {
    color: #666;
    font-size: 12px;
    margin-bottom: 8px;
  }
  .telegram-links {
    display: flex;
    gap: 8px;
    margin-top: 12px;
  }
  .telegram-links button {
    flex: 1;
    font-size: 13px;
    padding: 10px;
    margin-top: 0;
  }
</style>
</head>
<body>
<div class="box">
  <div class="logo">🎁</div>
  <h1>خدمات جيزي</h1>
  <p class="sub">تفعيل العروض + عرض الرصيد</p>

  <!-- قسم تسجيل الدخول -->
  <div id="loginSection">
    <label>📱 رقم هاتفك</label>
    <input id="phone" type="tel" placeholder="0779625183" maxlength="10" />
    <p style="font-size:11px;color:#999;margin:4px 0 0;">أدخل الرقم بصيغة 0XXXXXXXXX</p>

    <button id="btnOtp" onclick="sendOtp()">📩 إرسال الرمز</button>

    <label>🔐 الرمز المُستلم</label>
    <input id="otp" type="text" placeholder="أدخل الرمز" maxlength="6" />

    <button id="btnLogin" class="success-btn" onclick="doLogin()" disabled>✅ تسجيل الدخول</button>

    <div id="status"></div>
  </div>

  <!-- قسم المستخدم (يظهر بعد تسجيل الدخول) -->
  <div id="userSection" style="display:none;">
    <div id="statusUser" style="margin-top:16px;padding:14px;border-radius:12px;text-align:center;font-size:14px;font-weight:600;background:#e8f5e9;color:#2e7d32;">
      ✅ تم تسجيل الدخول
    </div>

    <button id="btnActivate" class="activate-btn" onclick="activate()">🎉 تفعيل 2 جيجا</button>
    <button id="btnBalance" class="balance-btn" onclick="getBalance()">💰 عرض الرصيد والباقات</button>

    <div id="status2" style="margin-top:16px;padding:14px;border-radius:12px;text-align:center;font-size:14px;font-weight:600;display:none;"></div>

    <div id="infoSection" class="info-section">
      <h3>📊 معلومات حسابك</h3>
      <div id="balanceContent"></div>
    </div>

    <button onclick="logout()" style="background:#999;margin-top:16px;">🚪 تسجيل خروج</button>
  </div>

  <!-- الفوتر — روابط المطور -->
  <div class="footer">
    <div class="developer">👨‍💻 المطور: @volkov_off</div>
    <div class="telegram-links">
      <button class="telegram-btn" onclick="openTelegram('https://t.me/volkov_off')">
        📩 المطور
      </button>
      <button class="channel-btn" onclick="openTelegram('https://t.me/mrnsk0')">
        📢 القناة
      </button>
    </div>
  </div>
</div>

<script>
const HOST = window.location.origin;
const API_KEY = "zakaria-website-key-2026";
let currentToken = "";
let currentPhone = "";

function setStatus(elId, msg, cls) {
  const el = document.getElementById(elId);
  el.textContent = msg;
  el.className = cls || 'info';
  if (cls) el.style.display = 'block';
}

function openTelegram(url) {
  window.open(url, '_blank');
}

// تحويل الرقم: 0779625183 → 213779625183
function formatPhone(input) {
  input = input.trim().replace(/\s/g, '');
  if (input.startsWith('0')) {
    return '213' + input.substring(1);
  }
  if (input.startsWith('213')) {
    return input;
  }
  return '213' + input;
}

async function sendRequest(action, payload) {
  const r = await fetch(HOST + '/api/request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Api-Key': API_KEY },
    body: JSON.stringify({ action, payload })
  });
  if (!r.ok) throw new Error('فشل الاتصال');
  const { id } = await r.json();
  
  for (let i = 0; i < 60; i++) {
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
  const rawPhone = document.getElementById('phone').value.trim();
  if (!rawPhone) return setStatus('status', 'أدخل رقمك', 'err');
  
  const phone = formatPhone(rawPhone);
  setStatus('status', '⏳ جاري الإرسال...', 'info');
  document.getElementById('btnOtp').disabled = true;
  
  try {
    await sendRequest('send_otp', { phone });
    setStatus('status', '✅ تم إرسال الرمز، تحقق من رسائلك', 'ok');
    document.getElementById('btnLogin').disabled = false;
    currentPhone = phone;
  } catch (e) {
    setStatus('status', '❌ ' + e.message, 'err');
  } finally {
    document.getElementById('btnOtp').disabled = false;
  }
}

async function doLogin() {
  const rawPhone = document.getElementById('phone').value.trim();
  const otp = document.getElementById('otp').value.trim();
  if (!otp) return setStatus('status', 'أدخل الرمز', 'err');
  
  const phone = formatPhone(rawPhone);
  currentPhone = phone;
  
  setStatus('status', '⏳ جاري التحقق...', 'info');
  document.getElementById('btnLogin').disabled = true;
  
  try {
    const res = await sendRequest('login', { phone, otp });
    if (!res.access_token) throw new Error('فشل تسجيل الدخول');
    
    currentToken = res.access_token;
    localStorage.setItem('djezzy_token', currentToken);
    localStorage.setItem('djezzy_phone', phone);
    
    // انتقل للصفحة الثانية
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('userSection').style.display = 'block';
    
  } catch (e) {
    setStatus('status', '❌ ' + e.message, 'err');
    document.getElementById('btnLogin').disabled = false;
  }
}

async function activate() {
  setStatus('status2', '⏳ جاري تفعيل 2 جيجا...', 'info');
  document.getElementById('btnActivate').disabled = true;
  
  try {
    const res = await sendRequest('activate_2g', { 
      token: currentToken, 
      phone: currentPhone 
    });
    if (res.error) throw new Error(res.message || res.error);
    setStatus('status2', '🎉 تم التفعيل بنجاح!', 'ok');
  } catch (e) {
    setStatus('status2', '❌ ' + e.message, 'err');
  } finally {
    document.getElementById('btnActivate').disabled = false;
  }
}

async function getBalance() {
  setStatus('status2', '⏳ جاري جلب المعلومات...', 'info');
  document.getElementById('btnBalance').disabled = true;
  
  try {
    const res = await sendRequest('get_balance', { 
      token: currentToken, 
      phone: currentPhone 
    });
    
    if (res.error) throw new Error(res.message || res.error);
    
    displayBalance(res);
    setStatus('status2', '✅ تم جلب المعلومات', 'ok');
  } catch (e) {
    setStatus('status2', '❌ ' + e.message, 'err');
  } finally {
    document.getElementById('btnBalance').disabled = false;
  }
}

function displayBalance(data) {
  const section = document.getElementById('infoSection');
  const content = document.getElementById('balanceContent');
  
  let html = '';
  
  if (data.mainBalance !== undefined) {
    html += `
      <div class="balance-card">
        <div>💰 الرصيد الرئيسي</div>
        <div class="amount">${data.mainBalance}</div>
        <div class="currency">دينار جزائري</div>
      </div>
    `;
  }
  
  if (data.products && data.products.length > 0) {
    html += '<h4 style="color:#333;margin:16px 0 10px;">📦 الباقات النشطة:</h4>';
    
    for (const product of data.products) {
      const name = product.commercialName?.ar || product.commercialName?.en || product.code || 'باقة';
      const expiry = product.expiryAt || 'غير محدد';
      
      html += `
        <div class="product-card">
          <div class="name">🎁 ${name}</div>
          <div class="detail">⏰ ينتهي: ${expiry}</div>
      `;
      
      if (product.balances && product.balances.length > 0) {
        for (const bal of product.balances) {
          const remaining = bal.remaining || 0;
          const total = bal.totalAmount || 0;
          const unit = bal.usageUnit || '';
          html += `
            <div class="remaining">
              📊 المتبقي: ${remaining} ${unit} من ${total} ${unit}
            </div>
          `;
        }
      }
      
      html += `</div>`;
    }
  } else {
    html += '<p style="text-align:center;color:#999;padding:20px;">لا توجد باقات نشطة</p>';
  }
  
  content.innerHTML = html;
  section.style.display = 'block';
}

function logout() {
  currentToken = "";
  currentPhone = "";
  localStorage.removeItem('djezzy_token');
  localStorage.removeItem('djezzy_phone');
  document.getElementById('loginSection').style.display = 'block';
  document.getElementById('userSection').style.display = 'none';
  document.getElementById('infoSection').style.display = 'none';
  document.getElementById('btnLogin').disabled = true;
  document.getElementById('phone').value = '';
  document.getElementById('otp').value = '';
  setStatus('status', '✅ تم تسجيل الخروج', 'ok');
}

// عند التحميل — استعد الجلسة
window.onload = function() {
  const saved = localStorage.getItem('djezzy_token');
  const savedPhone = localStorage.getItem('djezzy_phone');
  if (saved && savedPhone) {
    currentToken = saved;
    currentPhone = savedPhone;
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('userSection').style.display = 'block';
  }
};
</script>
</body>
</html>
"""


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
        "token": data.get("token", ""),
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
