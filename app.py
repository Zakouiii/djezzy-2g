from flask import Flask, request, jsonify, Response
import uuid, time, os

app = Flask(__name__)

API_KEY = "zakaria-website-key-2026"
DEVICE_KEY = "zakaria-device-key-2026"

pending = {}
results = {}
devices = {}

system_state = {
    "maintenance": False,
    "closed": False,
    "message": ""
}

INDEX_HTML = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🎁 خدمات جيزي</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #E60000 0%, #990000 100%);
    padding: 20px;
    min-height: 100vh;
    display: flex;
    align-items: flex-start;
    justify-content: center;
  }
  .box {
    max-width: 460px; width: 100%; background: #fff;
    border-radius: 24px; padding: 30px 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,.3);
    margin-top: 10px;
  }
  .logo-wrap { text-align: center; margin-bottom: 12px; }
  .logo-circle {
    width: 80px; height: 80px;
    margin: 0 auto;
    background: linear-gradient(135deg, #E60000, #990000);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 40px;
    box-shadow: 0 8px 20px rgba(230,0,0,.3);
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
  h1 { color: #E60000; text-align: center; margin: 12px 0 6px; font-size: 22px; font-weight: 800; }
  .sub { text-align: center; color: #666; font-size: 13px; margin-bottom: 20px; line-height: 1.6; }
  .sub .highlight { color: #4CAF50; font-weight: 700; }
  label { display: block; margin: 14px 0 6px; color: #333; font-size: 14px; font-weight: 600; }
  input {
    width: 100%; padding: 14px 16px; border: 2px solid #eee;
    border-radius: 12px; font-size: 16px; font-family: inherit;
    transition: all .2s;
  }
  input:focus { outline: none; border-color: #E60000; box-shadow: 0 0 0 4px rgba(230,0,0,.1); }
  button {
    width: 100%; padding: 14px; background: #E60000; color: #fff;
    border: none; border-radius: 12px; font-size: 16px;
    font-weight: 700; margin-top: 12px; cursor: pointer;
    transition: all .2s; font-family: inherit;
  }
  button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(230,0,0,.3); }
  button:disabled { opacity: .5; cursor: not-allowed; }
  .success-btn { background: #4CAF50; }
  .success-btn:hover:not(:disabled) { box-shadow: 0 8px 20px rgba(76,175,80,.3); }
  .activate-btn { background: linear-gradient(135deg, #FF9800, #F57C00); }
  .activate-btn:hover:not(:disabled) { box-shadow: 0 8px 20px rgba(255,152,0,.3); }
  .balance-btn { background: linear-gradient(135deg, #2196F3, #1976D2); }
  .balance-btn:hover:not(:disabled) { box-shadow: 0 8px 20px rgba(33,150,243,.3); }
  .logout-btn { background: #9E9E9E; }
  .logout-btn:hover:not(:disabled) { box-shadow: 0 8px 20px rgba(158,158,158,.3); }

  #status, #status2 {
    margin-top: 16px; padding: 14px; border-radius: 12px;
    text-align: center; font-size: 14px; font-weight: 600;
    display: none; line-height: 1.6;
  }
  .ok { background: #e8f5e9; color: #2e7d32; display: block !important; }
  .err { background: #ffebee; color: #c62828; display: block !important; }
  .info { background: #e3f2fd; color: #1565c0; display: block !important; }
  .warning { background: #fff8e1; color: #e65100; display: block !important; }

  .welcome-card {
    background: linear-gradient(135deg, #FFF8E1, #FFECB3);
    border: 2px solid #FFD54F; border-radius: 14px;
    padding: 14px; margin: 16px 0; text-align: center;
  }
  .welcome-card .title { color: #E65100; font-weight: 800; font-size: 15px; margin-bottom: 6px; }
  .welcome-card .text { color: #6D4C00; font-size: 13px; line-height: 1.6; }

  .info-section {
    display: none; margin-top: 20px; padding: 20px;
    background: #f9f9f9; border-radius: 16px; border: 2px solid #eee;
  }
  .info-section h3 { color: #E60000; font-size: 18px; margin: 0 0 16px; text-align: center; }
  .balance-card {
    background: linear-gradient(135deg, #E60000, #990000);
    color: #fff; padding: 20px; border-radius: 14px;
    text-align: center; margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(230,0,0,.2);
  }
  .balance-card .amount { font-size: 34px; font-weight: 900; margin: 8px 0; }
  .balance-card .currency { font-size: 14px; opacity: 0.9; }
  .product-card {
    background: #fff; padding: 14px; border-radius: 12px;
    border-right: 5px solid #4CAF50; margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
  }
  .product-card .name { font-weight: 700; color: #333; margin-bottom: 6px; font-size: 15px; }
  .product-card .detail { color: #666; font-size: 13px; margin: 3px 0; }
  .product-card .remaining { color: #4CAF50; font-weight: 700; font-size: 14px; margin-top: 6px; }

  .footer {
    text-align: center; margin-top: 24px;
    padding-top: 20px; border-top: 1px solid #eee;
  }
  .channel-card {
    background: linear-gradient(135deg, #0088cc, #006699);
    color: #fff; padding: 20px; border-radius: 14px;
    text-align: center; margin-bottom: 16px;
    box-shadow: 0 8px 20px rgba(0,136,204,.3);
    position: relative; overflow: hidden;
  }
  .channel-card .icon { font-size: 40px; margin-bottom: 8px; }
  .channel-card .title { font-weight: 800; font-size: 16px; margin-bottom: 6px; }
  .channel-card .desc { font-size: 12px; opacity: .95; margin-bottom: 12px; line-height: 1.6; }
  .channel-card a {
    display: inline-block; background: #fff; color: #0088cc;
    padding: 10px 24px; border-radius: 10px;
    text-decoration: none; font-weight: 700; font-size: 14px;
    transition: all .2s;
  }
  .channel-card a:hover { transform: scale(1.05); }
  .disclaimer {
    background: #fff8e1; border: 1px solid #ffcc80;
    border-radius: 12px; padding: 14px; margin-bottom: 16px;
    font-size: 12px; color: #6d4c00; line-height: 1.7;
    text-align: right;
  }
  .disclaimer strong { color: #E65100; }
  .rights { color: #999; font-size: 11px; margin-bottom: 12px; }
  .tg-btn {
    display: flex; align-items: center; justify-content: center;
    gap: 8px; padding: 12px; background: #0088cc;
    color: #fff; border-radius: 10px; text-decoration: none;
    font-size: 13px; font-weight: 700; transition: all .2s;
    margin-top: 8px;
  }
  .tg-btn:hover { background: #006699; transform: translateY(-2px); }
  .tg-icon { width: 20px; height: 20px; fill: #fff; }

  .maintenance-page { display: none; text-align: center; padding: 20px; }
  .maintenance-icon {
    font-size: 80px; margin-bottom: 20px;
    animation: bounce 1.5s infinite;
  }
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }
  .maintenance-title { color: #E60000; font-size: 22px; font-weight: 800; margin-bottom: 12px; }
  .maintenance-desc { color: #666; font-size: 14px; line-height: 1.8; margin-bottom: 20px; }
  .maintenance-time {
    background: #FFF3E0; padding: 12px; border-radius: 10px;
    color: #E65100; font-weight: 700; margin-bottom: 20px;
  }
  .benefits {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px; margin: 16px 0;
  }
  .benefit {
    background: #f5f5f5; padding: 10px; border-radius: 10px;
    text-align: center; font-size: 12px; color: #333;
  }
  .benefit .emoji { display: block; font-size: 20px; margin-bottom: 4px; }
</style>
</head>
<body>
<div class="box">

  <!-- صفحة الصيانة -->
  <div id="maintenancePage" class="maintenance-page">
    <div class="maintenance-icon">🔧</div>
    <div class="maintenance-title">الموقع تحت الصيانة</div>
    <div class="maintenance-desc">
      نعمل حالياً على تحسين الموقع وإصلاح بعض المشاكل.<br>
      سنعود قريباً جداً بإذن الله.
    </div>
    <div class="maintenance-time" id="maintenanceTime">
      ⏰ العودة المتوقعة: قريباً
    </div>
    <button onclick="retryConnection()" style="background:#4CAF50;">
      🔄 إعادة المحاولة
    </button>
    <div class="welcome-card" style="margin-top:16px;">
      <div class="title">💚 نشكرك على صبرك</div>
      <div class="text">يمكنك متابعة قناتنا على تيليجرام لمعرفة آخر التحديثات</div>
    </div>
    <a href="https://t.me/mrnsk0" target="_blank" class="tg-btn">
      <svg class="tg-icon" viewBox="0 0 24 24">
        <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z"/>
      </svg>
      انضم لقناة Telegram
    </a>
  </div>

  <!-- المحتوى الرئيسي -->
  <div id="mainContent">
    <div class="logo-wrap"><div class="logo-circle">🎁</div></div>
    <h1>خدمات جيزي</h1>
    <p class="sub">
      ⚡ تفعيل العروض + عرض الرصيد<br>
      <span class="highlight">🔒 آمن - سريع - موثوق</span>
    </p>

    <div class="welcome-card">
      <div class="title">✨ مرحباً بك! ✨</div>
      <div class="text">
        منصتك الأم لتفعيل عروض جيزي مجاناً<br>
        ⚡ سهل، سريع، ومجاني 100%
      </div>
    </div>

    <div class="benefits">
      <div class="benefit"><span class="emoji">🎁</span> عروض مجانية</div>
      <div class="benefit"><span class="emoji">⚡</span> سرعة فائقة</div>
      <div class="benefit"><span class="emoji">🔒</span> أمان تام</div>
      <div class="benefit"><span class="emoji">💯</span> مجاني 100%</div>
    </div>

    <!-- تسجيل الدخول -->
    <div id="loginSection">
      <label>📱 رقم هاتفك</label>
      <input id="phone" type="tel" placeholder="077XX XX XXX" maxlength="10" />
      <p style="font-size:11px;color:#999;margin:6px 0 0;text-align:center;">أدخل الرقم بصيغة 0XXXXXXXXX</p>
      <button id="btnOtp" onclick="sendOtp()">📩 إرسال رمز التحقق</button>
      <label>🔐 الرمز المُستلم</label>
      <input id="otp" type="text" placeholder="أدخل الرمز المكوّن من 6 أرقام" maxlength="6" />
      <button id="btnLogin" class="success-btn" onclick="doLogin()" disabled>✅ تسجيل الدخول</button>
      <div id="status"></div>
    </div>

    <!-- المستخدم -->
    <div id="userSection" style="display:none;">
      <div style="margin-top:16px;padding:14px;border-radius:12px;text-align:center;font-size:14px;font-weight:700;background:linear-gradient(135deg,#e8f5e9,#c8e6c9);color:#2e7d32;border:2px solid #4CAF50;">
        ✅ تم تسجيل الدخول بنجاح
      </div>
      <button id="btnActivate" class="activate-btn" onclick="activate()">🎉 تفعيل 2 جيجا مجاناً</button>
      <button id="btnBalance" class="balance-btn" onclick="getBalance()">💰 عرض الرصيد والباقات</button>
      <div id="status2"></div>
      <div id="infoSection" class="info-section">
        <h3>📊 معلومات حسابك</h3>
        <div id="balanceContent"></div>
      </div>
      <button class="logout-btn" onclick="logout()">🚪 تسجيل خروج</button>
    </div>

    <!-- الفوتر -->
    <div class="footer">
      <div class="channel-card">
        <div class="icon">📢</div>
        <div class="title">🎉 انضم إلى قناتنا!</div>
        <div class="desc">احصل على آخر التحديثات، العروض الحصرية، والدعم المباشر</div>
        <a href="https://t.me/mrnsk0" target="_blank">📩 انضم الآن</a>
      </div>

      <div class="disclaimer">
        ⚠️ <strong>تنبيه مهم:</strong><br>
        هذا الموقع لا يُستخدم لأي اختراق حسابات. هو مجرد واجهة تربط خدمات جيزي الرسمية بشكل خفيف وسريع، ليتمكن المستخدم من إدارة حسابه بسهولة.
      </div>

      <div class="rights">© 2026 - جميع الحقوق محفوظة</div>

      <a href="https://t.me/mrnsk0" target="_blank" class="tg-btn">
        <svg class="tg-icon" viewBox="0 0 24 24">
          <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z"/>
        </svg>
        📢 قناة Telegram
      </a>
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
  el.innerHTML = msg;
  el.className = cls || 'info';
  el.style.display = 'block';
}

function showMaintenance(message) {
  document.getElementById('maintenancePage').style.display = 'block';
  document.getElementById('mainContent').style.display = 'none';
  if (message) {
    document.getElementById('maintenanceTime').textContent = '⏰ ' + message;
  }
}

function hideMaintenance() {
  document.getElementById('maintenancePage').style.display = 'none';
  document.getElementById('mainContent').style.display = 'block';
}

function formatPhone(input) {
  input = input.trim().replace(/\s/g, '');
  if (input.startsWith('0')) return '213' + input.substring(1);
  if (input.startsWith('213')) return input;
  return '213' + input;
}

async function checkSystemStatus() {
  try {
    const r = await fetch(HOST + '/system-status', { cache: 'no-store' });
    const data = await r.json();
    if (data.maintenance || data.closed) {
      showMaintenance(data.message || 'نعمل على تحسين الموقع...');
      return false;
    } else {
      hideMaintenance();
      return true;
    }
  } catch (e) {
    return true;
  }
}

async function checkDeviceOnline() {
  try {
    const r = await fetch(HOST + '/status', { cache: 'no-store' });
    const data = await r.json();
    return data.devices_online > 0;
  } catch (e) {
    return false;
  }
}

// ✅ تحليل رسائل الخطأ من API جيزي (مع status)
function analyzeError(errorMsg, statusCode) {
  const msg = (errorMsg || '').toLowerCase();
  const code = parseInt(statusCode) || 0;

  // ✅ نجاح
  if (code === 200 && (msg.includes('successfully') || msg.includes('activated') || msg.includes('success'))) {
    return { type: 'ok', title: '🎉 تم التفعيل بنجاح', message: 'تم تفعيل العرض على رقمك.' };
  }

  // 401 / مفعّل من قبل / غير مؤهل
  if (code === 401 || msg.includes('401') || msg.includes('unauthorized') || msg.includes('not eligible') || msg.includes('already')) {
    return {
      type: 'warning',
      title: '⚠️ عرض مفعّل من قبل',
      message: 'يبدو أن هذا العرض مفعّل مسبقاً على رقمك، أو أن رقمك غير مؤهل للحصول عليه.'
    };
  }

  // Flexy / شرط 1 دينار
  if (msg.includes('flexy') || msg.includes('insufficient') || msg.includes('1g') || msg.includes('1 dzd') || msg.includes('1 dinar') || msg.includes('balance')) {
    return {
      type: 'warning',
      title: '💳 شرط Flexy غير متوفر',
      message: 'يجب أن يكون لديك رصيد Flexy بقيمة 1 دينار على الأقل لتفعيل العرض.'
    };
  }

  // 400
  if (code === 400 || msg.includes('400') || msg.includes('bad request')) {
    return {
      type: 'warning',
      title: '⚠️ طلب غير صحيح',
      message: 'يرجى التحقق من بياناتك أو رقم هاتفك، ثم حاول مرة أخرى.'
    };
  }

  // 403
  if (code === 403 || msg.includes('403') || msg.includes('forbidden')) {
    return {
      type: 'warning',
      title: '🚫 غير مؤهل',
      message: 'رقمك غير مؤهل لهذا العرض حالياً، أو لا يستوفي الشروط المطلوبة.'
    };
  }

  // 404
  if (code === 404 || msg.includes('404') || msg.includes('not found')) {
    return {
      type: 'err',
      title: '❌ العرض غير متوفر',
      message: 'هذا العرض لم يعد متاحاً حالياً، يرجى المحاولة لاحقاً.'
    };
  }

  // 429
  if (code === 429 || msg.includes('429') || msg.includes('too many')) {
    return {
      type: 'warning',
      title: '⏳ الرجاء الانتظار',
      message: 'لقد حاولت عدة مرات، يرجى الانتظار قليلاً قبل المحاولة مرة أخرى.'
    };
  }

  // 500
  if (code === 500 || msg.includes('500') || msg.includes('internal')) {
    return {
      type: 'warning',
      title: '🔧 الموقع تحت الصيانة',
      message: 'حدث خطأ في السيرفر، يرجى المحاولة لاحقاً.'
    };
  }

  return {
    type: 'err',
    title: '❌ فشل التفعيل',
    message: errorMsg || 'حدث خطأ غير متوقع، يرجى المحاولة لاحقاً.'
  };
}

async function sendRequest(action, payload) {
  const systemOk = await checkSystemStatus();
  if (!systemOk) throw new Error('__MAINTENANCE__:الموقع تحت الصيانة حالياً، سنعود قريباً');

  let r;
  try {
    r = await fetch(HOST + '/api/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Api-Key': API_KEY },
      body: JSON.stringify({ action, payload, token: currentToken }),
      cache: 'no-store'
    });
  } catch (e) {
    throw new Error('__MAINTENANCE__:تعذر الاتصال بالخادم، جاري الصيانة');
  }

  if (!r.ok) throw new Error('__MAINTENANCE__:الخادم تحت الصيانة، حاول لاحقاً');

  const { id } = await r.json();

  let checkCount = 0;
  for (let i = 0; i < 60; i++) {
    await new Promise(res => setTimeout(res, 1500));
    checkCount++;

    if (checkCount % 7 === 0) {
      const deviceOk = await checkDeviceOnline();
      if (!deviceOk) {
        throw new Error('__MAINTENANCE__:التطبيق تحت الصيانة، يرجى المحاولة بعد قليل');
      }
    }

    let rr;
    try {
      rr = await fetch(HOST + '/api/result/' + id, {
        headers: { 'X-Api-Key': API_KEY },
        cache: 'no-store'
      });
    } catch (e) {
      continue;
    }

    if (rr.status === 404) {
      throw new Error('__MAINTENANCE__:الخادم تحت الصيانة، يرجى إعادة المحاولة');
    }

    const data = await rr.json();

    if (data.status === 'done') return data.data;

    if (data.status === 'not_found') {
      throw new Error('__MAINTENANCE__:الخادم تحت الصيانة، يرجى إعادة المحاولة');
    }

    if (i > 45) {
      throw new Error('__MAINTENANCE__:الخدمة بطيئة حالياً، جاري الصيانة');
    }
  }

  throw new Error('__MAINTENANCE__:انتهت المهلة، التطبيق تحت الصيانة');
}

function handleError(e, elId) {
  const msg = e.message || '';

  if (msg.startsWith('__MAINTENANCE__:')) {
    const userMsg = msg.replace('__MAINTENANCE__:', '');
    setStatus(elId, '🔧 ' + userMsg, 'err');
    if (msg.includes('الموقع تحت الصيانة')) {
      showMaintenance('سيعود الموقع قريباً بإذن الله');
    }
  } else {
    const analysis = analyzeError(msg, 0);
    setStatus(elId, `<strong>${analysis.title}</strong><br>${analysis.message}`, analysis.type);
  }
}

async function sendOtp() {
  const rawPhone = document.getElementById('phone').value.trim();
  if (!rawPhone) return setStatus('status', '⚠️ أدخل رقمك', 'err');
  if (rawPhone.length < 9) return setStatus('status', '⚠️ الرقم غير صحيح', 'err');

  const phone = formatPhone(rawPhone);
  setStatus('status', '⏳ جاري الإرسال...', 'info');
  document.getElementById('btnOtp').disabled = true;

  try {
    await sendRequest('send_otp', { phone });
    setStatus('status', '✅ تم إرسال الرمز، تحقق من رسائلك', 'ok');
    document.getElementById('btnLogin').disabled = false;
    currentPhone = phone;
  } catch (e) {
    handleError(e, 'status');
  } finally {
    document.getElementById('btnOtp').disabled = false;
  }
}

async function doLogin() {
  const rawPhone = document.getElementById('phone').value.trim();
  const otp = document.getElementById('otp').value.trim();
  if (!otp) return setStatus('status', '⚠️ أدخل الرمز', 'err');

  const phone = formatPhone(rawPhone);
  currentPhone = phone;

  setStatus('status', '⏳ جاري التحقق...', 'info');
  document.getElementById('btnLogin').disabled = true;

  try {
    const res = await sendRequest('login', { phone, otp });
    if (!res.access_token) throw new Error('401 unauthorized');

    currentToken = res.access_token;
    localStorage.setItem('djezzy_token', currentToken);
    localStorage.setItem('djezzy_phone', phone);

    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('userSection').style.display = 'block';
  } catch (e) {
    handleError(e, 'status');
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

    // ✅ استخرج status و message من الاستجابة
    const status = res.status || 0;
    const message = res.message || res.error || '';

    // ✅ فحص النجاح أولاً — status 200 مع successfully أو activated
    if (status === 200 && (message.toLowerCase().includes('successfully') || message.toLowerCase().includes('activated'))) {
      setStatus('status2',
        '🎉 <strong>تم تفعيل 2 جيجا بنجاح!</strong><br>' +
        'تم إضافة الباقة إلى رقمك، تحقق من رصيدك في تطبيق جيزي.',
        'ok'
      );
      return;
    }

    // ❌ فشل — نحلل السبب
    const analysis = analyzeError(message, status);
    setStatus('status2', `<strong>${analysis.title}</strong><br>${analysis.message}`, analysis.type);

  } catch (e) {
    handleError(e, 'status2');
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

    const status = res.status || 0;
    const message = res.message || res.error || '';

    // ✅ نجاح
    if (status === 200 || res.mainBalance !== undefined || res.products) {
      displayBalance(res);
      setStatus('status2', '✅ تم جلب المعلومات بنجاح', 'ok');
      return;
    }

    // ❌ فشل
    const analysis = analyzeError(message, status);
    setStatus('status2', `<strong>${analysis.title}</strong><br>${analysis.message}`, analysis.type);

  } catch (e) {
    handleError(e, 'status2');
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
        <div class="currency">دينار جزائري (DZD)</div>
      </div>
    `;
  }

  if (data.products && data.products.length > 0) {
    html += '<h4 style="color:#333;margin:16px 0 10px;">📦 الباقات النشطة:</h4>';

    for (const product of data.products) {
      const name = (product.commercialName && (product.commercialName.ar || product.commercialName.en)) || product.code || 'باقة';
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

          let remainingText = `${remaining} ${unit}`;
          let totalText = `${total} ${unit}`;

          if (unit === 'MB') {
            remainingText = `${(remaining / 1024).toFixed(2)} GB`;
            totalText = `${(total / 1024).toFixed(2)} GB`;
          }

          html += `<div class="remaining">📊 المتبقي: ${remainingText} من ${totalText}</div>`;
        }
      }

      html += `</div>`;
    }
  } else {
    html += '<p style="text-align:center;color:#999;padding:20px;">لا توجد باقات نشطة حالياً</p>';
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
  setStatus('status', '✅ تم تسجيل الخروج بنجاح', 'ok');
}

async function retryConnection() {
  const ok = await checkSystemStatus();
  if (ok) {
    hideMaintenance();
    setStatus('status', '✅ تم استئناف الخدمة', 'ok');
  } else {
    setStatus('status', '🔧 ما زلنا تحت الصيانة، حاول لاحقاً', 'err');
  }
}

window.onload = function() {
  checkSystemStatus();
  setInterval(checkSystemStatus, 30000);

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


@app.route('/system-status')
def system_status():
    return jsonify({
        "maintenance": system_state["maintenance"],
        "closed": system_state["closed"],
        "message": system_state["message"]
    })


@app.route('/admin/maintenance/<state>')
def set_maintenance(state):
    if state == "on":
        system_state["maintenance"] = True
        system_state["message"] = "سيعود الموقع بعد ساعات قليلة"
    else:
        system_state["maintenance"] = False
        system_state["message"] = ""
    return jsonify(system_state)


@app.route('/api/request', methods=['POST'])
def add_request():
    if request.headers.get('X-Api-Key') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
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
    device_id = (request.json or {}).get("device_id")
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
    results[req_id] = (request.json or {}).get("data", {})
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
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
