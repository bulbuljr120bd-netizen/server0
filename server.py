"""
╔══════════════════════════════════════════════════════════════════╗
║                    POOR GRIEF — LICENSE ADMIN PANEL              ║
║              Flask Server + Web Dashboard + Device Binding       ║
║                    DEVICE ID IS MANDATORY                        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import json
import secrets
import hashlib
import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ─────────── Database File ───────────
DB_FILE = "licenses_db.json"
ADMIN_USER = "poorgrief"
ADMIN_PASS_HASH = hashlib.sha256("PoorGrief@2025#Admin".encode()).hexdigest()


def load_db():
    if not os.path.exists(DB_FILE):
        save_db({"licenses": {}})
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


def generate_key():
    parts = [secrets.token_hex(2).upper() for _ in range(4)]
    return "-".join(parts)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════
#                    ADMIN LOGIN PAGE HTML
# ═══════════════════════════════════════════════════════════════════

ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POOR GRIEF — Admin Login</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'JetBrains Mono', monospace;
            background: linear-gradient(135deg, #06060f 0%, #0a0b14 50%, #0d0f1a 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            position: relative;
            overflow: hidden;
        }
        
        body::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 20% 50%, rgba(0,242,255,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(112,0,255,0.08) 0%, transparent 50%);
            animation: rotate 20s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .login-card {
            position: relative;
            background: rgba(13, 15, 26, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 30px;
            padding: 50px 40px;
            width: 450px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(0,242,255,0.1);
            transition: all 0.3s ease;
        }
        
        .login-card:hover {
            border-color: rgba(0, 242, 255, 0.5);
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 60px rgba(0,242,255,0.2);
        }
        
        .logo-text {
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(135deg, #00f2ff, #7000ff, #ff00d6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }
        
        .subtitle {
            text-align: center;
            color: #4a5078;
            font-size: 11px;
            letter-spacing: 4px;
            margin-bottom: 40px;
        }
        
        .form-group { margin-bottom: 25px; }
        
        .form-group label {
            display: block;
            color: #00f2ff;
            font-size: 11px;
            letter-spacing: 2px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .form-group input {
            width: 100%;
            padding: 14px 18px;
            background: #0a0c18;
            border: 1px solid #1a1f35;
            border-radius: 12px;
            color: #c8d0e8;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        
        .form-group input:focus {
            border-color: #00f2ff;
            box-shadow: 0 0 15px rgba(0,242,255,0.2);
        }
        
        .login-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #00f2ff, #00c8ff);
            border: none;
            border-radius: 12px;
            color: #000;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 3px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,242,255,0.4);
        }
        
        .error-msg {
            text-align: center;
            color: #ff3131;
            font-size: 12px;
            margin-top: 20px;
            padding: 10px;
            background: rgba(255,49,49,0.1);
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo-text">⚡ POOR GRIEF ⚡</div>
        <div class="subtitle">ADMIN CONTROL PANEL v2.0</div>
        <form method="POST">
            <div class="form-group">
                <label>🔐 USERNAME</label>
                <input type="text" name="username" placeholder="Enter username..." required>
            </div>
            <div class="form-group">
                <label>🔑 PASSWORD</label>
                <input type="password" name="password" placeholder="Enter password..." required>
            </div>
            <button type="submit" class="login-btn">ACCESS PANEL</button>
            {% if error %}
            <div class="error-msg">❌ {{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════
#                   ADMIN DASHBOARD PAGE HTML
# ═══════════════════════════════════════════════════════════════════

ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POOR GRIEF — Admin Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'JetBrains Mono', monospace;
            background: #06060f;
            color: #c8d0e8;
            min-height: 100vh;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at 10% 20%, rgba(0,242,255,0.02) 0%, transparent 50%),
                        radial-gradient(ellipse at 90% 80%, rgba(112,0,255,0.02) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }
        
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 40px;
            background: rgba(10, 12, 24, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0, 242, 255, 0.2);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-brand {
            font-family: 'Orbitron', sans-serif;
            font-size: 22px;
            font-weight: 900;
            background: linear-gradient(135deg, #00f2ff, #7000ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .nav-right { display: flex; align-items: center; gap: 25px; }
        
        .nav-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            color: #00ff88;
            letter-spacing: 1px;
        }
        
        .nav-status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        .logout-btn {
            padding: 8px 24px;
            background: transparent;
            border: 1px solid #ff3131;
            border-radius: 8px;
            color: #ff3131;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .logout-btn:hover {
            background: #ff3131;
            color: #fff;
            box-shadow: 0 0 15px rgba(255,49,49,0.3);
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 30px 40px; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 25px;
            margin-bottom: 35px;
        }
        
        .stat-card {
            background: rgba(13, 15, 26, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: rgba(0, 242, 255, 0.5);
            box-shadow: 0 10px 30px rgba(0,242,255,0.1);
        }
        
        .stat-number {
            font-family: 'Orbitron', sans-serif;
            font-size: 42px;
            font-weight: 900;
            margin-bottom: 10px;
        }
        
        .stat-card:nth-child(1) .stat-number { color: #00f2ff; text-shadow: 0 0 20px rgba(0,242,255,0.3); }
        .stat-card:nth-child(2) .stat-number { color: #00ff88; text-shadow: 0 0 20px rgba(0,255,136,0.3); }
        .stat-card:nth-child(3) .stat-number { color: #ff3131; text-shadow: 0 0 20px rgba(255,49,49,0.3); }
        .stat-card:nth-child(4) .stat-number { color: #ffa500; text-shadow: 0 0 20px rgba(255,165,0,0.3); }
        
        .stat-label {
            color: #4a5078;
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        .section-card {
            background: rgba(13, 15, 26, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            transition: all 0.3s;
        }
        
        .section-card:hover {
            border-color: rgba(0, 242, 255, 0.4);
        }
        
        .section-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: #00f2ff;
            letter-spacing: 2px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, #00f2ff, transparent);
        }
        
        .gen-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            align-items: end;
        }
        
        .field-group label {
            display: block;
            color: #00f2ff;
            font-size: 10px;
            letter-spacing: 2px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .field-group input, .field-group select {
            width: 100%;
            padding: 12px 15px;
            background: #0a0c18;
            border: 1px solid #1a1f35;
            border-radius: 10px;
            color: #c8d0e8;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            outline: none;
            transition: all 0.3s;
        }
        
        .field-group input:focus, .field-group select:focus {
            border-color: #00f2ff;
            box-shadow: 0 0 10px rgba(0,242,255,0.2);
        }
        
        .required-star {
            color: #ff3131;
            margin-left: 5px;
        }
        
        .gen-btn {
            padding: 12px 25px;
            background: linear-gradient(135deg, #00f2ff, #00c8ff);
            border: none;
            border-radius: 10px;
            color: #000;
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .gen-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,242,255,0.4);
        }
        
        .key-display {
            display: none;
            margin-top: 25px;
            padding: 25px;
            background: linear-gradient(135deg, rgba(0,242,255,0.05), rgba(112,0,255,0.05));
            border: 1px solid #00ff88;
            border-radius: 15px;
            text-align: center;
            animation: fadeIn 0.5s ease;
        }
        
        .key-display.show { display: block; }
        
        .key-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            font-weight: 900;
            color: #00ff88;
            letter-spacing: 4px;
            margin: 15px 0;
            word-break: break-all;
        }
        
        .copy-key-btn {
            padding: 10px 30px;
            background: transparent;
            border: 1px solid #00ff88;
            border-radius: 8px;
            color: #00ff88;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .copy-key-btn:hover {
            background: #00ff88;
            color: #000;
            box-shadow: 0 0 15px rgba(0,255,136,0.3);
        }
        
        .table-wrapper {
            overflow-x: auto;
            border-radius: 15px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        thead th {
            padding: 15px;
            background: rgba(10, 12, 24, 0.8);
            color: #00f2ff;
            font-size: 11px;
            letter-spacing: 2px;
            text-align: left;
            border-bottom: 1px solid #00f2ff;
        }
        
        tbody td {
            padding: 15px;
            border-bottom: 1px solid rgba(26, 31, 53, 0.5);
            font-size: 12px;
        }
        
        tbody tr:hover {
            background: rgba(0, 242, 255, 0.05);
        }
        
        .key-cell {
            font-family: 'Orbitron', sans-serif;
            color: #00f2ff;
            font-weight: 700;
            font-size: 11px;
        }
        
        .device-cell {
            color: #7a80a0;
            font-size: 10px;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-family: monospace;
        }
        
        .badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            display: inline-block;
        }
        
        .badge-active { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
        .badge-blocked { background: rgba(255,49,49,0.15); color: #ff3131; border: 1px solid rgba(255,49,49,0.3); }
        .badge-expired { background: rgba(255,165,0,0.15); color: #ffa500; border: 1px solid rgba(255,165,0,0.3); }
        
        .action-btn {
            padding: 6px 12px;
            border: none;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            cursor: pointer;
            transition: all 0.2s;
            margin: 2px;
        }
        
        .btn-copy { background: rgba(0,242,255,0.2); color: #00f2ff; border: 1px solid rgba(0,242,255,0.3); }
        .btn-copy:hover { background: #00f2ff; color: #000; }
        
        .btn-block { background: rgba(255,49,49,0.2); color: #ff3131; border: 1px solid rgba(255,49,49,0.3); }
        .btn-block:hover { background: #ff3131; color: #fff; }
        
        .btn-active { background: rgba(0,255,136,0.2); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
        .btn-active:hover { background: #00ff88; color: #000; }
        
        .btn-delete { background: rgba(255,107,107,0.2); color: #ff6b6b; border: 1px solid rgba(255,107,107,0.3); }
        .btn-delete:hover { background: #ff6b6b; color: #fff; }
        
        .empty-state {
            text-align: center;
            padding: 60px;
            color: #2a2f48;
            font-size: 14px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .toast {
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 15px 25px;
            background: rgba(13, 15, 26, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid #00ff88;
            border-radius: 10px;
            color: #00ff88;
            font-size: 12px;
            z-index: 9999;
            display: none;
            animation: fadeIn 0.3s ease;
        }
        
        @media (max-width: 1000px) {
            .gen-grid { grid-template-columns: repeat(2, 1fr); }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .container { padding: 20px; }
        }
        
        @media (max-width: 600px) {
            .stats-grid { grid-template-columns: 1fr; }
            .gen-grid { grid-template-columns: 1fr; }
            .navbar { flex-direction: column; gap: 15px; }
        }
    </style>
</head>
<body>

<div class="toast" id="toast"></div>

<nav class="navbar">
    <div class="nav-brand">⚡ POOR GRIEF — CONTROL CENTER v2.0</div>
    <div class="nav-right">
        <span class="nav-status">SYSTEM ONLINE</span>
        <form action="/admin/logout" method="post" style="display:inline">
            <button class="logout-btn" type="submit">LOGOUT</button>
        </form>
    </div>
</nav>

<div class="container">
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number" id="st-total">{{ stats.total }}</div>
            <div class="stat-label">TOTAL LICENSES</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="st-active">{{ stats.active }}</div>
            <div class="stat-label">ACTIVE</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="st-blocked">{{ stats.blocked }}</div>
            <div class="stat-label">BLOCKED</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="st-expired">{{ stats.expired }}</div>
            <div class="stat-label">EXPIRED</div>
        </div>
    </div>
    
    <!-- Generate Key Section - Device ID MANDATORY -->
    <div class="section-card">
        <div class="section-title">🔑 GENERATE NEW LICENSE</div>
        <form id="genForm" onsubmit="return generateKey(event)">
            <div class="gen-grid">
                <div class="field-group">
                    <label>👤 CLIENT NAME</label>
                    <input type="text" id="gen-name" placeholder="User name..." required>
                </div>
                <div class="field-group">
                    <label>📊 PLAN</label>
                    <select id="gen-plan">
                        <option value="basic">BASIC</option>
                        <option value="pro">PRO</option>
                        <option value="premium">PREMIUM</option>
                    </select>
                </div>
                <div class="field-group">
                    <label>⏱️ VALIDITY</label>
                    <select id="gen-days">
                        <option value="7">7 DAYS</option>
                        <option value="30" selected>30 DAYS</option>
                        <option value="90">90 DAYS</option>
                        <option value="180">6 MONTHS</option>
                        <option value="365">1 YEAR</option>
                        <option value="3650">LIFETIME</option>
                    </select>
                </div>
                <div class="field-group">
                    <label>📱 MAX DEVICES</label>
                    <select id="gen-devices">
                        <option value="1" selected>1 DEVICE</option>
                        <option value="2">2 DEVICES</option>
                        <option value="3">3 DEVICES</option>
                        <option value="5">5 DEVICES</option>
                    </select>
                </div>
                <div class="field-group">
                    <label>🔒 DEVICE ID <span style="color:#ff3131;">*REQUIRED*</span></label>
                    <input type="text" id="gen-device-id" placeholder="Paste Device ID here..." required>
                </div>
                <button type="submit" class="gen-btn">⚡ GENERATE LICENSE</button>
            </div>
        </form>
        <div class="key-display" id="keyDisplay">
            <div style="color:#4a5078;font-size:11px;letter-spacing:2px;">✨ NEW LICENSE GENERATED ✨</div>
            <div class="key-value" id="newKeyValue"></div>
            <div style="color:#00ff88;font-size:10px;margin-top:5px;" id="boundDeviceDisplay"></div>
            <button class="copy-key-btn" onclick="copyNewKey()">📋 COPY TO CLIPBOARD</button>
        </div>
    </div>
    
    <!-- License Table -->
    <div class="section-card">
        <div class="section-title">📋 ALL LICENSES</div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>LICENSE KEY</th>
                        <th>CLIENT</th>
                        <th>PLAN</th>
                        <th>DEVICE ID</th>
                        <th>STATUS</th>
                        <th>EXPIRES</th>
                        <th>ACTIONS</th>
                    </tr>
                </thead>
                <tbody id="licTbody">
                    {% if licenses|length == 0 %}
                    <tr><td colspan="7" class="empty-state">✨ No licenses yet. Generate your first license above! ✨</td></tr>
                    {% endif %}
                    {% for key, lic in licenses.items() %}
                    <tr id="row-{{ key }}">
                        <td class="key-cell">{{ key }}</td>
                        <td>{{ lic.user_name or '—' }}</td>
                        <td>{{ lic.plan|upper }}</td>
                        <td class="device-cell" title="{{ lic.device_id or 'Not bound' }}">
                            {% if lic.device_id %}
                                🔒 {{ (lic.device_id)[:30] }}{% if lic.device_id|length > 30 %}...{% endif %}
                            {% else %}
                                🔓 Not bound
                            {% endif %}
                        </td>
                        <td>
                            {% if lic.status == 'blocked' %}
                                <span class="badge badge-blocked">BLOCKED</span>
                            {% elif lic.expired %}
                                <span class="badge badge-expired">EXPIRED</span>
                            {% else %}
                                <span class="badge badge-active">ACTIVE</span>
                            {% endif %}
                        </td>
                        <td style="font-size:11px;">{{ lic.expires_at[:10] }}</td>
                        <td>
                            <button class="action-btn btn-copy" onclick="copyText('{{ key }}')">COPY</button>
                            {% if lic.status == 'active' %}
                                <button class="action-btn btn-block" onclick="toggleKey('{{ key }}')">BLOCK</button>
                            {% else %}
                                <button class="action-btn btn-active" onclick="toggleKey('{{ key }}')">ACTIVATE</button>
                            {% endif %}
                            <button class="action-btn btn-delete" onclick="deleteKey('{{ key }}')">DELETE</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
</div>

<script>
function showToast(msg, isError = false) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.style.borderColor = isError ? '#ff3131' : '#00ff88';
    t.style.color = isError ? '#ff3131' : '#00ff88';
    t.style.display = 'block';
    setTimeout(() => t.style.display = 'none', 3000);
}

function copyText(text) {
    navigator.clipboard.writeText(text);
    showToast('✅ Copied: ' + text);
}

function copyNewKey() {
    const k = document.getElementById('newKeyValue').textContent;
    navigator.clipboard.writeText(k);
    showToast('✅ License key copied to clipboard!');
}

async function generateKey(e) {
    e.preventDefault();
    
    const deviceIdValue = document.getElementById('gen-device-id').value.trim();
    
    // Device ID is MANDATORY - without it, license will NOT be generated
    if (!deviceIdValue) {
        showToast('❌ DEVICE ID IS REQUIRED! License cannot be generated without Device ID.', true);
        document.getElementById('gen-device-id').style.borderColor = '#ff3131';
        return;
    }
    
    document.getElementById('gen-device-id').style.borderColor = '';
    
    const body = {
        user_name: document.getElementById('gen-name').value,
        plan: document.getElementById('gen-plan').value,
        days_valid: parseInt(document.getElementById('gen-days').value),
        max_devices: parseInt(document.getElementById('gen-devices').value),
        device_id: deviceIdValue
    };
    
    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        const data = await res.json();
        
        if (data.success) {
            document.getElementById('newKeyValue').textContent = data.license_key;
            document.getElementById('boundDeviceDisplay').innerHTML = '🔒 Bound to: ' + data.device_id.substring(0, 25) + '...';
            document.getElementById('keyDisplay').classList.add('show');
            showToast('🔒 License generated with Device Binding! (Device locked)', false);
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast('❌ ' + (data.error || 'Failed to generate key'), true);
        }
    } catch (error) {
        showToast('❌ Server error: ' + error, true);
    }
}

async function toggleKey(key) {
    try {
        await fetch('/api/toggle/' + key, { method: 'POST' });
        location.reload();
    } catch (error) {
        showToast('❌ Failed to toggle license', true);
    }
}

async function deleteKey(key) {
    if (confirm('⚠️ Delete license ' + key + '? This action cannot be undone!')) {
        try {
            await fetch('/api/delete/' + key, { method: 'POST' });
            location.reload();
        } catch (error) {
            showToast('❌ Failed to delete license', true);
        }
    }
}

setInterval(() => {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            if (data.total !== undefined) {
                document.getElementById('st-total').textContent = data.total;
                document.getElementById('st-active').textContent = data.active;
                document.getElementById('st-blocked').textContent = data.blocked;
                document.getElementById('st-expired').textContent = data.expired;
            }
        })
        .catch(err => console.log('Stats refresh failed'));
}, 30000);
</script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════
#                          ROUTES
# ═══════════════════════════════════════════════════════════════════

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        p_hash = hashlib.sha256(p.encode()).hexdigest()
        if u == ADMIN_USER and p_hash == ADMIN_PASS_HASH:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Invalid credentials"
    return render_template_string(ADMIN_LOGIN_HTML, error=error)


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = load_db()
    licenses = db.get("licenses", {})
    now = datetime.datetime.now().isoformat()
    
    stats = {"total": 0, "active": 0, "blocked": 0, "expired": 0}
    for key, lic in licenses.items():
        stats["total"] += 1
        lic["expired"] = lic.get("expires_at", "") < now
        if lic.get("status") == "blocked":
            stats["blocked"] += 1
        elif lic["expired"]:
            stats["expired"] += 1
        else:
            stats["active"] += 1
    
    return render_template_string(ADMIN_DASHBOARD_HTML, licenses=licenses, stats=stats)


@app.route("/api/stats", methods=["GET"])
@admin_required
def api_stats():
    db = load_db()
    licenses = db.get("licenses", {})
    now = datetime.datetime.now().isoformat()
    
    stats = {"total": 0, "active": 0, "blocked": 0, "expired": 0}
    for lic in licenses.values():
        stats["total"] += 1
        if lic.get("status") == "blocked":
            stats["blocked"] += 1
        elif lic.get("expires_at", "") < now:
            stats["expired"] += 1
        else:
            stats["active"] += 1
    
    return jsonify(stats)


@app.route("/api/generate", methods=["POST"])
@admin_required
def api_generate():
    data = request.json
    db = load_db()
    
    # Device ID is MANDATORY - without it, license will NOT be generated
    device_id = data.get("device_id", "").strip()
    if not device_id:
        return jsonify({
            "success": False, 
            "error": "DEVICE ID IS REQUIRED! License cannot be generated without Device ID."
        }), 400
    
    key = generate_key()
    days = data.get("days_valid", 30)
    expires = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
    
    db["licenses"][key] = {
        "user_name": data.get("user_name", ""),
        "plan": data.get("plan", "basic"),
        "max_devices": data.get("max_devices", 1),
        "device_id": device_id,
        "status": "active",
        "created_at": datetime.datetime.now().isoformat(),
        "expires_at": expires,
        "last_used": ""
    }
    save_db(db)
    
    return jsonify({
        "success": True,
        "license_key": key,
        "expires_at": expires,
        "device_id": device_id
    })


@app.route("/api/toggle/<key>", methods=["POST"])
@admin_required
def api_toggle(key):
    db = load_db()
    if key in db["licenses"]:
        lic = db["licenses"][key]
        lic["status"] = "blocked" if lic["status"] == "active" else "active"
        if lic["status"] == "blocked":
            lic["device_id"] = ""
        save_db(db)
        return jsonify({"success": True, "status": lic["status"]})
    return jsonify({"success": False}), 404


@app.route("/api/delete/<key>", methods=["POST"])
@admin_required
def api_delete(key):
    db = load_db()
    if key in db["licenses"]:
        del db["licenses"][key]
        save_db(db)
        return jsonify({"success": True})
    return jsonify({"success": False}), 404


@app.route("/api/verify", methods=["POST"])
def api_verify():
    data = request.json
    key = data.get("license_key", "").strip()
    device_id = data.get("device_id", "").strip()
    
    db = load_db()
    lic = db["licenses"].get(key)
    
    if not lic:
        return jsonify({"valid": False, "message": "❌ Invalid license key!"})
    
    if lic["status"] == "blocked":
        return jsonify({"valid": False, "message": "🚫 License blocked by admin!"})
    
    now = datetime.datetime.now().isoformat()
    if lic.get("expires_at", "") < now:
        return jsonify({"valid": False, "message": "⏰ License expired!"})
    
    # Device Binding Logic - Device ID must match exactly
    stored_device = lic.get("device_id", "")
    
    if not stored_device:
        # This should never happen because device_id is mandatory during generation
        lic["device_id"] = device_id
        lic["last_used"] = now
        save_db(db)
        return jsonify({
            "valid": True,
            "message": "✅ License activated!",
            "plan": lic["plan"],
            "user_name": lic["user_name"],
            "expires_at": lic["expires_at"]
        })
    
    if stored_device != device_id:
        return jsonify({
            "valid": False,
            "message": f"🔒 LICENSE LOCKED! This key is bound to another device.\n\nYour Device ID: {device_id[:30]}...\nExpected Device ID: {stored_device[:30]}..."
        })
    
    lic["last_used"] = now
    save_db(db)
    
    return jsonify({
        "valid": True,
        "message": "✅ License verified successfully!",
        "plan": lic["plan"],
        "user_name": lic["user_name"],
        "expires_at": lic["expires_at"]
    })


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  ⚡ POOR GRIEF — LICENSE ADMIN PANEL v2.0 ⚡")
    print("=" * 60)
    print("  🌐 Admin Panel: http://localhost:5000/admin")
    print("  👤 Username: poorgrief")
    print("  🔑 Password: PoorGrief@2025#Admin")
    print("  📱 Device Binding: ✅ ENABLED (MANDATORY)")
    print("  ⚠️  Device ID is REQUIRED to generate license")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)