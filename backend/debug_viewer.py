
from flask import Flask, render_template_string, send_from_directory, jsonify
import os
from datetime import datetime

app = Flask(__name__)

DEBUG_DIR = os.path.join(os.path.dirname(__file__), '..', 'debug_images')
DEBUG_DIR = os.path.abspath(DEBUG_DIR)

os.makedirs(DEBUG_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMR Debug Görüntüleyici</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .header p { color: #888; font-size: 1rem; }
        .refresh-btn {
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .refresh-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
        }
        .clear-btn {
            background: linear-gradient(90deg, #e74c3c, #c0392b);
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            margin-top: 15px;
            margin-left: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .clear-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(231, 76, 60, 0.4);
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
        }
        .card-header {
            padding: 15px 20px;
            background: rgba(0, 212, 255, 0.1);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .card-header h3 {
            font-size: 1rem;
            color: #00d4ff;
        }
        .card-header span {
            font-size: 0.8rem;
            color: #888;
        }
        .card-body {
            padding: 15px;
        }
        .card-body img {
            width: 100%;
            height: auto;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .card-body img:hover {
            transform: scale(1.02);
        }
        .no-images {
            text-align: center;
            padding: 60px;
            color: #888;
        }
        .no-images svg {
            width: 100px;
            height: 100px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px 40px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-box h2 {
            font-size: 2rem;
            color: #00d4ff;
        }
        .stat-box p { color: #888; }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active { display: flex; }
        .modal img {
            max-width: 95%;
            max-height: 95%;
            border-radius: 10px;
        }
        .modal-close {
            position: fixed;
            top: 20px;
            right: 30px;
            font-size: 40px;
            color: white;
            cursor: pointer;
        }
        
        /* Categories */
        .category {
            margin-bottom: 40px;
        }
        .category-title {
            font-size: 1.3rem;
            margin-bottom: 15px;
            padding-left: 15px;
            border-left: 4px solid #00d4ff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 OMR Debug Görüntüleyici</h1>
        <p>Optik form işleme adımlarını görselleştirin</p>
        <button class="refresh-btn" onclick="location.reload()">🔄 Yenile</button>
        <button class="clear-btn" onclick="clearImages()">🗑️ Temizle</button>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-box">
                <h2>{{ image_count }}</h2>
                <p>Görüntü</p>
            </div>
            <div class="stat-box">
                <h2>{{ category_count }}</h2>
                <p>Kategori</p>
            </div>
        </div>
        
        {% if images %}
            {% for category, imgs in categories.items() %}
            <div class="category">
                <h2 class="category-title">{{ category }}</h2>
                <div class="grid">
                    {% for img in imgs %}
                    <div class="card">
                        <div class="card-header">
                            <h3>{{ img.name }}</h3>
                            <span>{{ img.size }}</span>
                        </div>
                        <div class="card-body">
                            <img src="/debug/{{ img.filename }}" alt="{{ img.name }}" onclick="openModal(this.src)">
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-images">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5-7l-3 3.72L9 13l-3 4h12l-4-5z"/>
                </svg>
                <h2>Henüz görüntü yok</h2>
                <p>Bir optik form analiz ettiğinizde debug görüntüleri burada görünecek.</p>
            </div>
        {% endif %}
    </div>
    
    <div class="modal" id="modal" onclick="closeModal()">
        <span class="modal-close">&times;</span>
        <img id="modal-img" src="">
    </div>
    
    <script>
        function openModal(src) {
            document.getElementById('modal-img').src = src;
            document.getElementById('modal').classList.add('active');
        }
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }
        function clearImages() {
            if (confirm('Tüm debug görüntüleri silinsin mi?')) {
                fetch('/api/clear').then(res => res.json()).then(data => {
                    alert(data.message);
                    location.reload();
                });
            }
        }
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
    </script>
</body>
</html>
"""

def get_image_info(filename):
    """Görüntü bilgilerini al"""
    filepath = os.path.join(DEBUG_DIR, filename)
    size = os.path.getsize(filepath)
    if size > 1024 * 1024:
        size_str = f"{size / (1024 * 1024):.1f} MB"
    elif size > 1024:
        size_str = f"{size / 1024:.1f} KB"
    else:
        size_str = f"{size} B"
    
    # Dosya adından açıklama oluştur
    name_map = {
        '0_orijinal': '📷 Orijinal Görüntü',
        '1a_beyaz_maske': '⬜ Beyaz Maske',
        '1b_kontur': '🔲 Kontur Tespiti',
        '1c_koseler': '📍 Köşe Noktaları',
        '1d_perspektif': '📐 Perspektif Düzeltme',
        '1e_yonelisli': '🔄 Yöneliş Düzeltme',
        '2a_gri': '⚫ Gri Tonlama',
        '2b_canny': '✂️ Canny Kenar',
        '2c_dark': '🌑 Koyu Alanlar',
        '2d_binary': '⬛ Binary',
        'bolge_ad': '👤 Ad Bölgesi',
        'bolge_soyad': '👤 Soyad Bölgesi',
        'bolge_turkce': '📚 Türkçe',
        'bolge_matematik': '🔢 Matematik',
        'bolge_fen': '🔬 Fen Bilimleri',
        'bolge_sosyal': '🌍 Sosyal Bilgiler',
        'circles_': '⭕ Daire Tespiti',
        'bubble_': '💧 Baloncuk Analizi',
    }
    
    name = filename.replace('.jpg', '').replace('.png', '')
    display_name = name
    
    for key, value in name_map.items():
        if key in name:
            display_name = value + ' - ' + name
            break
    
    return {
        'filename': filename,
        'name': display_name,
        'size': size_str
    }

def categorize_images(images):
    """Görüntüleri kategorilere ayır"""
    categories = {
        '1️⃣ Ön İşleme': [],
        '2️⃣ Perspektif Düzeltme': [],
        '3️⃣ Diğer': [],
        '4️⃣ Bölge Çıkarma': [],
        '5️⃣ Baloncuk Tespiti': []
    }
    
    for img in images:
        name = img['filename'].lower()
        if '0_' in name or 'orijinal' in name:
            categories['1️⃣ Ön İşleme'].append(img)
        elif '1' in name[0:2] or 'perspektif' in name or 'kose' in name:
            categories['2️⃣ Perspektif Düzeltme'].append(img)
        elif 'bolge' in name:
            categories['4️⃣ Bölge Çıkarma'].append(img)
        elif 'circle' in name or 'bubble' in name:
            categories['5️⃣ Baloncuk Tespiti'].append(img)
        else:
            categories['3️⃣ Diğer'].append(img)
    
    # Boş kategorileri kaldır
    return {k: v for k, v in categories.items() if v}

@app.route('/')
def index():
    """Ana sayfa - debug görüntülerini listele"""
    images = []
    
    if os.path.exists(DEBUG_DIR):
        for filename in sorted(os.listdir(DEBUG_DIR)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                images.append(get_image_info(filename))
    
    categories = categorize_images(images)
    
    return render_template_string(
        HTML_TEMPLATE,
        images=images,
        categories=categories,
        image_count=len(images),
        category_count=len(categories)
    )

@app.route('/debug/<filename>')
def serve_debug_image(filename):
    """Debug görüntüsünü serve et"""
    return send_from_directory(DEBUG_DIR, filename)

@app.route('/api/images')
def api_images():
    """API: Görüntü listesi"""
    images = []
    if os.path.exists(DEBUG_DIR):
        for filename in sorted(os.listdir(DEBUG_DIR)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                images.append(get_image_info(filename))
    return jsonify({'images': images, 'count': len(images)})

@app.route('/api/clear')
def api_clear():
    """API: Debug görüntülerini temizle (orijinal görüntü hariç)"""
    count = 0
    kept = 0
    # Korunacak dosyalar - ana form görüntüsü
    protected_files = ['0_orijinal.jpg', '0_orijinal.png']
    
    if os.path.exists(DEBUG_DIR):
        for filename in os.listdir(DEBUG_DIR):
            filepath = os.path.join(DEBUG_DIR, filename)
            if os.path.isfile(filepath):
                # Korunan dosyaları silme
                if filename in protected_files:
                    kept += 1
                    continue
                os.remove(filepath)
                count += 1
    return jsonify({
        'cleared': count, 
        'kept': kept,
        'message': f'{count} görüntü silindi, {kept} korundu'
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  🔍 OMR DEBUG GÖRÜNTÜLEYICI")
    print("="*50)
    print(f"\n📂 Debug klasörü: {os.path.abspath(DEBUG_DIR)}")
    print("🌐 Tarayıcıda aç: http://localhost:5001")
    print("\n⚡ Sunucu başlatılıyor...\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
