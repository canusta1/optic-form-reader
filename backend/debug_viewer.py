"""
Debug Görüntü Görüntüleyici - Web Arayüzü
Backend işlem yaparken oluşturulan debug görüntülerini görüntüler
"""

from flask import Flask, render_template_string, send_file, jsonify
import os
from datetime import datetime
import glob

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>OMR Debug Görüntüleyici</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
        }
        .image-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        }
        .image-card h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .image-card p {
            color: #666;
            margin-bottom: 15px;
            font-size: 0.95em;
            line-height: 1.6;
        }
        .image-container {
            position: relative;
            width: 100%;
            background: #f5f5f5;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
        }
        .image-container img {
            width: 100%;
            height: auto;
            display: block;
            transition: transform 0.3s;
        }
        .image-container:hover img {
            transform: scale(1.05);
        }
        .image-status {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
        }
        .exists { background: rgba(40, 167, 69, 0.9); }
        .missing { background: rgba(220, 53, 69, 0.9); }
        .no-images {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .no-images h2 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 15px;
        }
        .no-images p {
            color: #666;
            font-size: 1.1em;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .modal-content {
            position: relative;
            margin: 2% auto;
            max-width: 95%;
            max-height: 95vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .modal-content img {
            max-width: 100%;
            max-height: 95vh;
            object-fit: contain;
            border-radius: 10px;
        }
        .close {
            position: absolute;
            top: 20px;
            right: 40px;
            color: white;
            font-size: 50px;
            font-weight: bold;
            cursor: pointer;
            z-index: 1001;
        }
        .close:hover {
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 OMR Debug Görüntüleyici</h1>
            <p>Görüntü işleme adımlarını manuel olarak inceleyin</p>
            <button class="refresh-btn" onclick="manualRefresh()">🔄 Görüntüleri Yenile</button>
            <p style="margin-top: 10px; font-size: 0.9em; color: #999;">Otomatik yenileme kapatıldı - Form analizi tamamlandıktan sonra butona tıklayın</p>
        </div>
        
        <div id="image-grid" class="grid">
            <!-- JavaScript ile doldurulacak -->
        </div>
    </div>

    <!-- Modal -->
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="">
        </div>
    </div>

    <script>
        const debugImages = [
            {
                name: 'debug_edges.jpg',
                title: '1️⃣ Kenar Tespiti (Canny)',
                description: 'Form kenarlarını bulmak için Canny edge detection. Beyaz çizgiler = tespit edilen kenarlar.'
            },
            {
                name: 'debug_contours.jpg',
                title: '2️⃣ Kontür Tespiti',
                description: 'Bulunan kontürler yeşil çizgilerle işaretli. En büyük dikdörtgen = form sınırı.'
            },
            {
                name: 'debug_warped.jpg',
                title: '3️⃣ Perspektif Düzeltme',
                description: 'Form düzleştirildi ve döndürüldü. Artık üstten bakış görünümü.'
            },
            {
                name: 'debug_binary_input_fixed.jpg',
                title: '4️⃣ Binary Görüntü (Threshold)',
                description: 'SİYAH arkaplan + BEYAZ bubblelar. Bu doğru mu kontrol edin! Beyaz pikseller bubble olmalı.'
            },
            {
                name: 'debug_morphed.jpg',
                title: '5️⃣ Morfolojik İşlemler',
                description: 'Gürültü temizlendi, bubblelar netleştirildi. (Not: Şu an kapalı)'
            },
            {
                name: 'debug_bubbles.jpg',
                title: '6️⃣ Tespit Edilen Bubblelar',
                description: 'YEŞİL dikdörtgenler = tespit edilen bubblelar. Kaç tane var? Tümü doğru mu?'
            },
            {
                name: 'debug_rows.jpg',
                title: '7️⃣ Satır Gruplama',
                description: 'Bubblelar satırlara ayrıldı. Her satır farklı renk. Sıralama doğru mu?'
            }
        ];

        async function loadImages() {
            const grid = document.getElementById('image-grid');
            grid.innerHTML = '';
            
            let hasAnyImage = false;
            
            for (const img of debugImages) {
                const exists = await checkImageExists(img.name);
                
                if (exists) {
                    hasAnyImage = true;
                    const card = createImageCard(img, exists);
                    grid.appendChild(card);
                }
            }
            
            if (!hasAnyImage) {
                grid.innerHTML = `
                    <div class="no-images">
                        <h2>📷 Henüz Debug Görüntüsü Yok</h2>
                        <p>Flutter uygulamadan bir form yükleyin ve işlem başlasın.</p>
                        <p style="margin-top: 10px; color: #999;">Görüntüler backend/ klasörüne kaydedilecek.</p>
                    </div>
                `;
            }
        }

        async function checkImageExists(filename) {
            try {
                const response = await fetch('/image/' + filename, { method: 'HEAD' });
                return response.ok;
            } catch {
                return false;
            }
        }

        function createImageCard(imgData, exists) {
            const card = document.createElement('div');
            card.className = 'image-card';
            
            card.innerHTML = `
                <h3>${imgData.title}</h3>
                <p>${imgData.description}</p>
                <div class="image-container" onclick="openModal('/image/${imgData.name}')">
                    ${exists ? `
                        <img src="/image/${imgData.name}?t=${Date.now()}" alt="${imgData.title}">
                        <span class="image-status exists">✓ Mevcut</span>
                    ` : `
                        <div style="padding: 100px; text-align: center; color: #999;">
                            Görüntü bulunamadı
                        </div>
                        <span class="image-status missing">✗ Yok</span>
                    `}
                </div>
            `;
            
            return card;
        }

        function openModal(src) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modal.style.display = 'flex';
            modalImg.src = src;
        }

        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }

        // ESC tuşu ile modal'ı kapat
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });

        // Sayfa yüklendiğinde görüntüleri yükle
        loadImages();

        // Manuel yenileme butonu
        function manualRefresh() {
            loadImages();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/image/<filename>')
def serve_image(filename):
    """Debug görüntüsünü serve et"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/jpeg')
    else:
        return "Görüntü bulunamadı", 404

@app.route('/api/images')
def list_images():
    """Mevcut debug görüntülerini listele"""
    backend_dir = os.path.dirname(__file__)
    debug_images = glob.glob(os.path.join(backend_dir, 'debug_*.jpg'))
    
    images = []
    for img_path in debug_images:
        filename = os.path.basename(img_path)
        stat = os.stat(img_path)
        images.append({
            'filename': filename,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({'images': images})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🔬 OMR DEBUG GÖRÜNTÜLEYİCİ")
    print("="*60)
    print("\n📡 Web arayüzü başlatılıyor...")
    print("🌐 Tarayıcınızda açın: http://127.0.0.1:5001")
    print("\n💡 Kullanım:")
    print("   1. Bu pencereyi açık tutun")
    print("   2. Flutter uygulamadan form yükleyin")
    print("   3. Debug görüntüleri otomatik güncellenecek")
    print("\n⏹️  Durdurmak için: Ctrl+C")
    print("="*60 + "\n")
    
    app.run(debug=False, port=5001, host='0.0.0.0')
