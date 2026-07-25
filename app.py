from flask import Flask, render_template_string, request, redirect, url_for
import yt_dlp

app = Flask(__name__)

# Простой HTML-шаблон прямо в коде, чтобы не создавать лишние папки
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>noabstube.com — Видео без рекламы</title>
    <style>
        body {
            background-color: #0f2027;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
        }
        input[type="text"] {
            width: 60%;
            padding: 12px;
            font-size: 16px;
            border-radius: 5px;
            border: none;
            margin-right: 10px;
        }
        button {
            padding: 12px 20px;
            font-size: 16px;
            background-color: #ff0055;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #e0004c;
        }
        .error {
            color: #ff5555;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>noabstube.com</h1>
    <p>Смотри видео с YouTube без рекламы</p>
    
    <form method="POST">
        <input type="text" name="url" placeholder="Вставь ссылку на YouTube..." required>
        <button type="submit">Смотреть</button>
    </form>

    {% if error %}
        <div class="error"><p>{{ error }}</p></div>
    {% endif %}

    {% if video_url %}
        <div style="margin-top: 30px;">
            <h3>Готово! Вот прямая ссылка на видео:</h3>
            <a href="{{ video_url }}" target="_blank" style="color: #00ffcc; font-size: 18px;">Открыть поток / Скачать</a>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
.index():
    video_url = None
    error = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        
        # Настройки yt-dlp с обходом блокировок дата-центров
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
        except Exception as e:
            error = f"Не удалось загрузить видео. Ошибка: {str(e)}"
            
    return render_template_string(HTML_TEMPLATE, video_url=video_url, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
