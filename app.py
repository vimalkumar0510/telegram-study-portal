from flask import Flask, Response, render_template_string, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Apna Telegram Bot Token yahan daalein
BOT_TOKEN = '9277826109:AAGmCkE4H42UTHds4JDeb37Y2FT9bunjNnY'
DATA_FILE = 'database.json'

# Database initialization
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Website Design (Saari videos aur PDFs ki list yahan dikhegi)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mera Private Study Portal</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .item { margin-bottom: 30px; border-bottom: 1px solid #ddd; padding-bottom: 15px; }
        video, iframe { width: 100%; height: 350px; border: none; margin-top: 10px; border-radius: 5px; }
        h3 { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Mera Private Telegram Study Portal</h2>
        <p>Channel me upload karo, yahan automatic aayega!</p>
        <hr>
        {% if items|length == 0 %}
            <p>Abhi koi video ya PDF nahi hai. Channel me upload kijiye!</p>
        {% endif %}
        {% for item in items %}
            <div class="item">
                <h3>{{ item.title }}</h3>
                {% if item.type == 'video' %}
                    <video controls>
                        <source src="/stream?file_id={{ item.file_id }}" type="video/mp4">
                        Aapka browser video support nahi karta.
                    </video>
                {% else %}
                    <iframe src="/stream?file_id={{ item.file_id }}"></iframe>
                {% endif %}
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/stream')
def stream():
    file_id = request.args.get('file_id')
    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    res = requests.get(get_file_url).json()
    
    if 'result' not in res or 'file_path' not in res['result']:
        return "File path not found", 404
        
    file_path = res['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    
    # Telegram se video stream ko proper handle karne ke liye
    req = requests.get(download_url, stream=True)
    
    def generate():
        for chunk in req.iter_content(chunk_size=8192):
            if chunk:
                yield chunk
                
    content_type = 'video/mp4' if ('mp4' in file_path or 'mkv' in file_path) else 'application/pdf'
    return Response(generate(), status=req.status_code, headers=dict(req.headers))

# Telegram Webhook - Channel post ya message ko automatic pakadne ke liye
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    msg = None
    if 'message' in data:
        msg = data['message']
    elif 'channel_post' in data:
        msg = data['channel_post']
        
    if msg:
        title = msg.get('caption', 'Study Material')
        
        file_id = None
        f_type = None
        
        if 'video' in msg:
            file_id = msg['video']['file_id']
            f_type = 'video'
        elif 'document' in msg:
            file_id = msg['document']['file_id']
            f_type = 'pdf'
            if not title or title == 'Study Material':
                title = msg['document'].get('file_name', 'PDF Document')
                
        if file_id and f_type:
            with open(DATA_FILE, 'r') as f:
                items = json.load(f)
                
            # Check karein ki file pehle se database me hai ya nahi
            if not any(i['file_id'] == file_id for i in items):
                items.append({'title': title, 'file_id': file_id, 'type': f_type})
                with open(DATA_FILE, 'w') as f:
                    json.dump(items, f)
                    
    return jsonify({"status": "ok"})

# Telegram se bina download kiye direct stream karne ke liye route
@app.route('/stream')
def stream():
    file_id = request.args.get('file_id')
    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    res = requests.get(get_file_url).json()
    file_path = res['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    
    req = requests.get(download_url, stream=True)
    content_type = 'video/mp4' if 'mp4' in file_path or 'mkv' in file_path else 'application/pdf'
    return Response(req.iter_content(chunk_size=1024), content_type=content_type)

if __name__ == '__main__':
    app.run(debug=True)
