from flask import Flask, request, render_template_string
import yt_dlp

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NoAds Tube & Downloader</title>
    <style>
        * { box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            margin: 0; 
            padding: 20px;
            display: flex; 
            flex-direction: column; 
            align-items: center;
            min-height: 100vh;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            width: 100%;
            max-width: 600px;
            text-align: center;
            box-shadow: 0 15px 25px rgba(0,0,0,0.5);
            margin-top: 2vh;
        }

        h1 { margin: 0 0 5px 0; font-size: 28px; }
        .accent { color: #ff4757; }
        .subtitle { color: #b2bec3; font-size: 14px; margin-bottom: 25px; }

        input {
            width: 100%; padding: 15px; margin-bottom: 15px;
            border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2); color: white; 
            outline: none; font-size: 16px; transition: 0.3s;
        }
        input:focus { border-color: #ff4757; box-shadow: 0 0 10px rgba(255, 71, 87, 0.3); }

        .btn-main {
            width: 100%; padding: 15px; border: none; border-radius: 12px;
            background: linear-gradient(45deg, #ff4757, #ff6b81);
            color: white; font-size: 16px; font-weight: bold;
            cursor: pointer; transition: all 0.3s ease;
        }
        .btn-main:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 71, 87, 0.6); }

        video { 
            width: 100%; border-radius: 15px; margin-top: 25px; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.4); outline: none; background: black;
        }
        
        .download-box {
            background: rgba(0, 0, 0, 0.2); padding: 20px;
            border-radius: 15px; margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        select {
            width: 100%; padding: 12px; border-radius: 8px; margin-bottom: 15px;
            background: #203a43; color: white; border: 1px solid #b2bec3; outline: none;
        }
        .btn-dl {
            display: inline-block; width: 100%; padding: 12px; text-decoration: none;
            background: #2ecc71; color: white; font-weight: bold; border-radius: 8px;
        }
        .btn-dl:hover { background: #27ae60; }

        /* Стили для истории */
        .history-box {
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 15px;
            margin-top: 20px;
            text-align: left;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .history-box h3 { margin-top: 0; font-size: 16px; color: #ff6b81; text-align: center; }
        .history-list { list-style: none; padding: 0; margin: 0; }
        .history-item {
            padding: 8px 10px; margin-bottom: 8px; background: rgba(255,255,255,0.05);
            border-radius: 8px; cursor: pointer; white-space: nowrap; overflow: hidden;
            text-overflow: ellipsis; font-size: 13px; transition: 0.2s;
        }
        .history-item:hover { background: rgba(255,255,255,0.15); color: #ff4757; }

        .tutorial {
            background: rgba(0,0,0,0.3); border-left: 4px solid #ff4757;
            padding: 20px; margin-top: 30px; border-radius: 0 15px 15px 0;
            text-align: left; font-size: 14px; line-height: 1.6;
        }
        .tutorial h3 { margin-top: 0; color: #ff6b81; }
        
        .error { color: #ff4757; margin-top: 15px; font-weight: bold; }
        
        .footer {
            margin-top: 30px;
            color: #b2bec3;
            font-size: 14px;
        }
        .footer span {
            color: #ff4757;
            font-weight: bold;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>NoAds <span class="accent">Tube</span></h1>
        <div class="subtitle">Смотри и скачивай без ограничений</div>
        
        <form method="POST" onsubmit="saveToHistory()">
            <input type="text" id="url-input" name="url" placeholder="Вставь ссылку на видео..." required>
            <button type="submit" class="btn-main">Обработать ссылку</button>
        </form>
        
        {% if video_url %}
            <video controls autoplay>
                <source src="{{ video_url }}" type="video/mp4">
            </video>
            
            <div class="download-box">
                <h3 style="margin-top: 0;">Скачать на телефон</h3>
                <select id="quality-select" onchange="updateLink()">
                    {% for f in formats %}
                        <option value="{{ f.url }}">{{ f.label }}</option>
                    {% endfor %}
                </select>
                <a id="download-btn" href="{{ formats[0].url }}" class="btn-dl" target="_blank">📥 Скачать выбранное качество</a>
            </div>
        {% elif error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        <!-- Блок истории -->
        <div class="history-box" id="history-container" style="display: none;">
            <h3>⏱️ История просмотров</h3>
            <ul class="history-list" id="history-list"></ul>
        </div>

        <div class="tutorial">
            <h3>📖 Как этим пользоваться?</h3>
            <ol style="padding-left: 20px; margin: 0;">
                <li>Открой обычный YouTube и скопируй ссылку на нужное видео.</li>
                <li>Вставь ссылку в поле выше и нажми <b>Обработать ссылку</b>.</li>
                <li>Видео появится в плеере — смотри без рекламы или выбирай качество для скачивания!</li>
                <li>Кликай по прошлым ссылкам в истории ниже, чтобы не вводить их заново.</li>
            </ol>
        </div>
        
        <div class="footer">
            Developed by <span>Tempers1337</span>
        </div>
    </div>

    <script>
        function updateLink() {
            var select = document.getElementById("quality-select");
            var btn = document.getElementById("download-btn");
            btn.href = select.value;
        }

        // Сохранение ссылки в localStorage при отправке формы
        function saveToHistory() {
            let url = document.getElementById("url-input").value;
            if (!url) return;
            
            let history = JSON.parse(localStorage.getItem("tube_history")) || [];
            
            // Удаляем дубликат, если ссылка уже была
            history = history.filter(item => item !== url);
            
            // Добавляем в начало списка
            history.unshift(url);
            
            // Оставляем максимум последние 5 штук
            if (history.length > 5) {
                history.pop();
            }
            
            localStorage.setItem("tube_history", JSON.stringify(history));
        }

        // Загрузка истории при открытии страницы
        window.onload = function() {
            let history = JSON.parse(localStorage.getItem("tube_history")) || [];
            let container = document.getElementById("history-container");
            let list = document.getElementById("history-list");
            
            if (history.length > 0) {
                container.style.display = "block";
                list.innerHTML = "";
                
                history.forEach(url => {
                    let li = document.createElement("li");
                    li.className = "history-item";
                    li.innerText = url;
                    // При клике на историю ссылка подставляется в инпут
                    li.onclick = function() {
                        document.getElementById("url-input").value = url;
                    };
                    list.appendChild(li);
                });
            }
        };
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    error_msg = None
    formats_list = []
    
    if request.method == 'POST':
        url = request.form['url']
        ydl_opts = {'quiet': True}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'url' in info:
                    video_url = info['url']
                
                for f in info.get('formats', []):
                    if f.get('protocol') in ['http', 'https']:
                        res = f.get('resolution') or f.get('format_note') or 'Неизвестно'
                        ext = f.get('ext', 'mp4')
                        vcodec = f.get('vcodec', 'none')
                        acodec = f.get('acodec', 'none')
                        
                        if vcodec != 'none' and acodec != 'none':
                            type_label = "Видео + Звук"
                            if not video_url: video_url = f.get('url')
                        elif vcodec != 'none':
                            type_label = "Без звука"
                        elif acodec != 'none':
                            type_label = "Только звук (Аудио)"
                        else:
                            continue
                            
                        label = f"{res} - .{ext} ({type_label})"
                        formats_list.append({'url': f.get('url'), 'label': label})
                
                formats_list.reverse()
                
        except Exception as e:
            error_msg = "Не удалось загрузить видео. Проверь ссылку."
            print(f"Ошибка: {e}")
            
    return render_template_string(HTML, video_url=video_url, error=error_msg, formats=formats_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
