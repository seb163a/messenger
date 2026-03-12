from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
raeume = {}

HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Secure Room Media</title>
<style>
:root { --bg: #0f172a; --panel: #1e293b; --primary: #10b981; --secondary: #3b82f6; --text: #f8fafc; }
body { background: var(--bg); color: var(--text); font-family: sans-serif; margin: 0; display: flex; justify-content: center; height: 100vh; }
#app { width: 100%; max-width: 500px; background: var(--panel); display: flex; flex-direction: column; }
#login, #chat-ui { display: flex; flex-direction: column; height: 100%; padding: 20px; box-sizing: border-box; }
input { padding: 12px; margin: 5px 0; border-radius: 10px; border: none; background: #334155; color: white; }
button { padding: 12px; border-radius: 10px; border: none; background: var(--primary); color: white; font-weight: bold; cursor: pointer; }
#history { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding: 10px; }
.b { padding: 10px; border-radius: 15px; max-width: 80%; font-size: 14px; position: relative; }
.ich { align-self: flex-end; background: var(--primary); border-bottom-right-radius: 2px; }
.er { align-self: flex-start; background: #334155; border-bottom-left-radius: 2px; }
.name { font-size: 10px; color: var(--secondary); display: block; margin-bottom: 3px; }
img { max-width: 100%; border-radius: 10px; margin-top: 5px; cursor: zoom-in; }
.sys { align-self: center; color: #94a3b8; font-size: 10px; }
#input-area { display: flex; gap: 5px; padding: 15px; background: #0f172a; align-items: center; }
#preview { display: none; padding: 10px; background: #1e293b; border-top: 1px solid var(--primary); }
</style></head>
<body><div id="app">
<div id="login"><h2 style="text-align:center">🗝️ Secret Media Room</h2>
<input id="u" placeholder="Dein Name"><input id="p" type="password" placeholder="Passwort">
<button onclick="L()">Beitreten</button></div>
<div id="chat-ui" style="display:none">
<div id="history"></div>
<div id="preview"><img id="p-img" style="height:50px; width:auto"> <button onclick="clearImg()">X</button></div>
<div id="input-area">
<label style="cursor:pointer; font-size:20px">🖼️<input type="file" id="f" hidden accept="image/*" onchange="pre(this)"></label>
<input id="m" style="flex-grow:1" placeholder="Nachricht..." onkeypress="if(event.key==='Enter') S()">
<button onclick="S()">Senden</button></div></div></div>
<script>
let u, p, lastId = 0, selImg = "";
const enc = t => btoa(unescape(encodeURIComponent(t)));
const dec = t => decodeURIComponent(escape(atob(t)));

function L() {
    u = document.getElementById('u').value.trim(); p = document.getElementById('p').value.trim();
    if(!u || !p) return; document.getElementById('login').style.display='none';
    document.getElementById('chat-ui').style.display='flex';
    setInterval(G, 2000);
}

function pre(input) {
    let reader = new FileReader();
    reader.onload = e => { 
        selImg = e.target.result; 
        document.getElementById('p-img').src = selImg;
        document.getElementById('preview').style.display = 'block';
    };
    reader.readAsDataURL(input.files[0]);
}

function clearImg() { selImg = ""; document.getElementById('preview').style.display = 'none'; }

function add(t, c, name="", imgData="") {
    let d = document.createElement('div'); d.className = 'b ' + c;
    let content = name ? `<span class="name">${name}</span>` : "";
    if(imgData) content += `<img src="${imgData}"><br>`;
    if(t) content += t;
    d.innerHTML = content;
    document.getElementById('history').appendChild(d);
    document.getElementById('history').scrollTop = 999999;
}

function S() {
    let i = document.getElementById('m'); let msg = i.value;
    if(!msg.trim() && !selImg) return;
    add(msg, 'ich', '', selImg);
    fetch('/s/'+p, {method:'POST', headers:{'Content-Type':'application/json'}, 
    body:JSON.stringify({a:u, m:msg.split(' ').map(enc), img:selImg})});
    i.value=''; clearImg();
}

function G() {
    fetch(`/g/${p}/${lastId}`).then(r=>r.json()).then(msgs=>{
        msgs.forEach(m=>{
            if(m.a !== u) {
                let txt = m.m.map(dec).join(' ');
                add(txt, 'er', m.a, m.img);
            }
            lastId = m.id;
        });
    });
}
</script></body></html>
"""

@app.route('/')
def i(): return render_template_string(HTML)

@app.route('/s/<r>', methods=['POST'])
def s(r):
    if r not in raeume: raeume[r] = []
    msg = request.json
    msg['id'] = len(raeume[r]) + 1
    raeume[r].append(msg)
    return jsonify({"ok": True})

@app.route('/g/<r>/<int:last_id>')
def g(r, last_id):
    if r not in raeume: return jsonify([])
    return jsonify([m for m in raeume[r] if m['id'] > last_id])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)