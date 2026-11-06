from flask import Flask, Response, render_template_string, request
import requests

app = Flask(__name__)

# Yahan apna Telegram Bot Token daalein
BOT_TOKEN = '9277826109:AAGmCkE4H42UTHds4JDeb37Y2FT9bunjNnY'

# HTML Website Design
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
        video, iframe { width: 100%; height: 400px; border: none; margin-top: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Mera Private Telegram Study Portal</h2>
        <p>Bina download kiye direct Telegram se stream ho raha hai.</p>

        <h3>Video Lecture</h3>
        <video controls>
            <source src="/stream-video?file_id=YAHAN_VIDEO_FILE_ID" type="video/mp4">
            Aapka browser video support nahi karta.
        </video>

        <h3>PDF Notes</h3>
        <iframe src="/stream-pdf?file_id=YAHAN_PDF_FILE_ID"></iframe>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/stream-video')
def stream_video():
    file_id = request.args.get('file_id')
    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    res = requests.get(get_file_url).json()
    file_path = res['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    
    req = requests.get(download_url, stream=True)
    return Response(req.iter_content(chunk_size=1024), content_type='video/mp4')

@app.route('/stream-pdf')
def stream_pdf():
    file_id = request.args.get('file_id')
    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    res = requests.get(get_file_url).json()
    file_path = res['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    
    req = requests.get(download_url, stream=True)
    return Response(req.iter_content(chunk_size=1024), content_type='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
