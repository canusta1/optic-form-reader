from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
import cv2
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import traceback

from database import Database
from form_templates import list_templates, get_template
from image_processor import OptikFormOkuyucu

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'optic-form-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = Database()
form_okuyucu = OptikFormOkuyucu(debug_mode=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    try:
        token = auth_header.split(' ')[1]
        return verify_token(token)
    except:
        return None

def verify_token(token):
    """JWT token doğrula"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def get_current_user():
    """Request'ten kullanıcı bilgisini al"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1]
        return verify_token(token)
    except:
        return None



@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if not all([username, email, password, full_name]):
            return jsonify({'error': 'Tüm alanlar gerekli'}), 400
        
        user_id = db.create_user(username, email, password, full_name)
        
        if user_id:
            return jsonify({
                'success': True,
                'message': 'Kayıt başarılı'
            }), 201
        else:
            return jsonify({'error': 'Kullanıcı adı veya e-posta zaten kullanımda'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Kullanıcı adı ve şifre gerekli'}), 400
        
        user = db.verify_user(username, password)
        
        if user:
            token = generate_token(user['id'])
            return jsonify({
                'success': True,
                'token': token,
                'user': user
            })
        else:
            return jsonify({'error': 'Kullanıcı adı veya şifre hatalı'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/answer-keys', methods=['POST'])
def create_answer_key():
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    try:
        data = request.get_json()
        
        exam_name = data.get('exam_name')
        school_type = data.get('school_type')
        form_template = data.get('form_template', 'simple')
        subjects = data.get('subjects')
        
        if not all([exam_name, subjects]):
            return jsonify({'error': 'Eksik bilgi'}), 400
        
        # Aynı isimde cevap anahtarı var mı kontrol et
        existing_key = db.get_answer_key_by_name(user_id, exam_name)
        
        if existing_key:
            # Mevcut cevap anahtarını güncelle
            success = db.update_answer_key(
                existing_key['id'], user_id, school_type, subjects, form_template
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'answer_key_id': existing_key['id'],
                    'updated': True,
                    'message': f'"{exam_name}" cevap anahtarı güncellendi'
                }), 200
            else:
                return jsonify({'error': 'Cevap anahtarı güncellenemedi'}), 500
        else:
            # Yeni cevap anahtarı oluştur
            answer_key_id = db.create_answer_key(
                user_id, exam_name, school_type, subjects, form_template
            )
            
            if answer_key_id:
                return jsonify({
                    'success': True,
                    'answer_key_id': answer_key_id,
                    'updated': False,
                    'message': f'"{exam_name}" cevap anahtarı oluşturuldu'
                }), 201
            else:
                return jsonify({'error': 'Cevap anahtarı oluşturulamadı'}), 500
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/form-templates', methods=['GET'])
def get_form_templates():
    try:
        templates = list_templates()
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/answer-keys', methods=['GET'])
def get_answer_keys():
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    try:
        keys = db.get_answer_keys(user_id)
        return jsonify({'success': True, 'answer_keys': keys})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/answer-keys/<int:answer_key_id>', methods=['GET'])
def get_answer_key_detail(answer_key_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    try:
        key = db.get_answer_key_details(answer_key_id)
        return jsonify({'success': True, 'answer_key': key})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/answer-keys/by-name/<exam_name>', methods=['GET'])
def get_answer_key_by_name(exam_name):
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    try:
        key = db.get_answer_key_by_name(user_id, exam_name)
        if key:
            # Detaylı bilgiyi al
            detailed_key = db.get_answer_key_details(key['id'])
            return jsonify({'success': True, 'answer_key': detailed_key, 'found': True})
        else:
            return jsonify({'success': True, 'answer_key': None, 'found': False, 'message': f'"{exam_name}" bulunamadı'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/read-optic-form', methods=['POST'])
def read_optic_form():
    print("\n📥 Form okuma isteği alındı...")
    
    user_id = get_current_user()
    if not user_id:
        print("❌ Yetkisiz erişim")
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    print(f"✅ Kullanıcı ID: {user_id}")
    
    try:
        # Dosya kontrolü
        if 'file' not in request.files:
            return jsonify({'error': 'Dosya bulunamadı'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Geçersiz dosya formatı (Sadece jpg, jpeg, png)'}), 400
        
        print(f"📄 Dosya: {file.filename}")
        
        # Cevap anahtarı ID'si
        answer_key_id = request.form.get('answer_key_id')
        if not answer_key_id:
            return jsonify({'error': 'Cevap anahtarı ID gerekli'}), 400
        
        print(f"🔑 Cevap anahtarı ID: {answer_key_id}")
        
        # Dosyayı kaydet
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"💾 Dosya kaydedildi: {filepath}")
        
        # Cevap anahtarını al
        answer_key = db.get_answer_key_details(int(answer_key_id))
        if not answer_key:
            return jsonify({'error': 'Cevap anahtarı bulunamadı'}), 404
        
        print(f"📋 Cevap anahtarı: {answer_key.get('exam_name')}")
        
        #  GÖRÜNTÜ İŞLEME - Optik formu oku
        print("\n Görüntü işleme başlıyor...")
        okuma_sonucu = form_okuyucu.form_oku(filepath)
        
        if not okuma_sonucu['success']:
            return jsonify({
                'error': okuma_sonucu.get('error', 'Form okunamadı')
            }), 400
        
        # Öğrenci bilgileri
        student_info = okuma_sonucu['student_info']
        student_answers = okuma_sonucu['answers']
        
        print(f" Öğrenci: {student_info.get('name', '')} {student_info.get('surname', '')}")
        print(f" Okunan cevap sayısı: {len(student_answers)}")
        
        # CEVAPLARI KARŞILAŞTIR
        print("\n Cevaplar karşılaştırılıyor...")
        karsilastirma = compare_answers(answer_key, student_answers)
        
        print(f" Doğru: {karsilastirma['correct_count']}")
        print(f" Yanlış: {karsilastirma['total_questions'] - karsilastirma['correct_count'] - sum(1 for a in student_answers.values() if a == 'BOŞ')}")
        print(f" Boş: {sum(1 for a in student_answers.values() if a == 'BOŞ')}")
        print(f" Başarı: %{karsilastirma['success_rate']}")
        
        # SONUÇLARI KAYDET
        student_name = student_info.get('name', '')
        student_surname = student_info.get('surname', '')
        full_name = f"{student_name} {student_surname}".strip() or 'Bilinmiyor'
        
        student_data = {
            'name': full_name,
            'number': student_info.get('student_number', 'Bilinmiyor'),
            'total_score': karsilastirma['total_score'],
            'success_rate': karsilastirma['success_rate']
        }
        
        print(f" Sonuçlar veritabanına kaydediliyor...")
        result_id = db.save_student_result(
            int(answer_key_id),
            student_data,
            karsilastirma['detailed_answers'],
            filepath
        )
        print(f" Kaydedildi (ID: {result_id})")
        
        # Yanıt
        response = {
            'success': True,
            'result_id': result_id,
            'student_name': full_name,
            'student_number': student_data['number'],
            'total_score': karsilastirma['total_score'],
            'success_rate': karsilastirma['success_rate'],
            'subject_scores': karsilastirma['subject_scores'],
            'details': f"{karsilastirma['correct_count']}/{karsilastirma['total_questions']} doğru"
        }
        
        print(f"\n İşlem tamamlandı!\n")
        return jsonify(response)
        
    except Exception as e:
        print(f"\n HATA: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def compare_answers(answer_key, student_answers):
    total_score = 0
    correct_count = 0
    total_questions = 0
    subject_scores = {}
    detailed_answers = []
    
    question_counter = 1
    
    for subject in answer_key['subjects']:
        subject_id = subject['id']
        subject_name = subject['subject_name']
        correct_answers = subject['answers']
        points = subject['points']
        
        subject_score = 0
        subject_correct = 0
        
        for i, correct_answer in enumerate(correct_answers):
            student_answer = student_answers.get(question_counter, 'BOŞ')
            
            is_correct = (student_answer == correct_answer)
            points_earned = points[i] if is_correct else 0
            
            if is_correct:
                correct_count += 1
                subject_correct += 1
                subject_score += points_earned
                total_score += points_earned
            
            detailed_answers.append({
                'subject_id': subject_id,
                'question_number': question_counter,
                'student_answer': student_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'points_earned': points_earned
            })
            
            question_counter += 1
            total_questions += 1
        
        subject_scores[subject_name] = {
            'score': subject_score,
            'correct': subject_correct,
            'total': len(correct_answers)
        }
    
    success_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    return {
        'total_score': round(total_score, 2),
        'correct_count': correct_count,
        'total_questions': total_questions,
        'success_rate': round(success_rate, 2),
        'subject_scores': subject_scores,
        'detailed_answers': detailed_answers
    }

@app.route('/results/<int:answer_key_id>', methods=['GET'])
def get_results(answer_key_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    try:
        results = db.get_student_results(answer_key_id)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/all-results', methods=['GET'])
def get_all_results():
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    try:
        results = db.get_all_results(user_id)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/student-result/<int:result_id>', methods=['GET'])
def get_student_result_detail(result_id):
    import base64
    
    # Auth kontrol
    user_id = get_current_user()
    if not user_id:
        print(f" Auth başarısız, user_id: {user_id}")
        
    
    try:
        result = db.get_student_result_detail(result_id)
        if result:
            
            image_path = result.get('image_path')
            print(f" Result ID: {result_id}, Image path: {image_path}")
            
            if image_path:
                if not os.path.isabs(image_path):
                    image_path = os.path.join(os.path.dirname(__file__), image_path)
                
                print(f" Checking image at: {image_path}")
                print(f" File exists: {os.path.exists(image_path)}")
                
                if os.path.exists(image_path):
                    try:
                        img = cv2.imread(image_path)
                        if img is not None:
                            max_size = 600
                            h, w = img.shape[:2]
                            print(f" Original size: {w}x{h}")
                            
                            if max(h, w) > max_size:
                                scale = max_size / max(h, w)
                                new_w = int(w * scale)
                                new_h = int(h * scale)
                                img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                                print(f" Resized to: {new_w}x{new_h}")
                            
                            # JPEG olarak encode et - daha düşük kalite (50%)
                            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 50])
                            img_base64 = base64.b64encode(buffer).decode('utf-8')
                            result['image_base64'] = img_base64
                            print(f" Görsel base64 oluşturuldu: {len(img_base64) / 1024:.1f} KB")
                        else:
                            print(f" cv2.imread başarısız: {image_path}")
                    except Exception as e:
                        print(f" Görsel base64 hatası: {e}")
                        traceback.print_exc()
                else:
                    print(f" Dosya bulunamadı: {image_path}")
            else:
                print(f" Image path None")
            
            return jsonify({'success': True, 'result': result})
        else:
            return jsonify({'error': 'Sonuç bulunamadı'}), 404
    except Exception as e:
        print(f"API hatası: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/student-image/<int:result_id>', methods=['GET'])
def get_student_image(result_id):
    from flask import send_file
    from io import BytesIO
    
    try:
        # Sonuç bilgisini al
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT image_path FROM student_results WHERE id = ?', (result_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row['image_path']:
            image_path = row['image_path']
            # Tam yol oluştur
            if not os.path.isabs(image_path):
                image_path = os.path.join(os.path.dirname(__file__), image_path)
            
            if os.path.exists(image_path):
                # Görseli küçült ve sıkıştır
                img = cv2.imread(image_path)
                if img is not None:
                    # Maksimum boyut 1200px
                    max_size = 1200
                    h, w = img.shape[:2]
                    if max(h, w) > max_size:
                        scale = max_size / max(h, w)
                        new_w = int(w * scale)
                        new_h = int(h * scale)
                        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    
                    # JPEG olarak sıkıştır (kalite %80)
                    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    img_io = BytesIO(buffer.tobytes())
                    img_io.seek(0)
                    return send_file(img_io, mimetype='image/jpeg')
                else:
                    return send_file(image_path, mimetype='image/jpeg')
        
        return jsonify({'error': 'Görsel bulunamadı'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Optik Form API çalışıyor'})

@app.route('/db', methods=['GET'])
def db_viewer_home():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cursor.fetchall()]
    
    table_info = []
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        table_info.append({'name': t, 'count': count})
    
    conn.close()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Optik Form DB Viewer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1 { color: #333; }
            .table-list { display: flex; flex-wrap: wrap; gap: 15px; }
            .table-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 200px; }
            .table-card h3 { margin: 0 0 10px 0; color: #2196F3; }
            .table-card p { margin: 0; color: #666; }
            .table-card a { display: inline-block; margin-top: 10px; color: #2196F3; text-decoration: none; }
            .table-card a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1> Optik Form Veritabanı</h1>
        <div class="table-list">
    """
    
    for t in table_info:
        html += f"""
            <div class="table-card">
                <h3>{t['name']}</h3>
                <p>{t['count']} kayıt</p>
                <a href="/db/{t['name']}">Görüntüle →</a>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    return html

@app.route('/db/<table_name>', methods=['GET'])
def db_viewer_table(table_name):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Tablo var mı kontrol
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        conn.close()
        return "Tablo bulunamadı", 404
    
    # Kolon bilgileri
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Sayfa numarası
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Toplam kayıt
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    
    # Verileri al
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset))
    rows = cursor.fetchall()
    
    conn.close()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{table_name} - DB Viewer</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            h1 {{ color: #333; }}
            a.back {{ color: #2196F3; text-decoration: none; }}
            table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 20px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #2196F3; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            td {{ max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            .pagination {{ margin-top: 20px; }}
            .pagination a {{ padding: 8px 16px; margin: 0 4px; background: #2196F3; color: white; text-decoration: none; border-radius: 4px; }}
            .pagination a.disabled {{ background: #ccc; }}
            .pagination span {{ padding: 8px 16px; }}
        </style>
    </head>
    <body>
        <a class="back" href="/db">← Geri</a>
        <h1>📋 {table_name} ({total} kayıt)</h1>
        <table>
            <tr>
    """
    
    for col in columns:
        html += f"<th>{col}</th>"
    html += "</tr>"
    
    for row in rows:
        html += "<tr>"
        for val in row:
            display = str(val)[:100] + "..." if len(str(val)) > 100 else str(val)
            html += f"<td title='{str(val)[:500]}'>{display}</td>"
        html += "</tr>"
    
    html += f"""
        </table>
        <div class="pagination">
            <span>Sayfa {page}/{total_pages}</span>
    """
    
    if page > 1:
        html += f'<a href="/db/{table_name}?page={page-1}">← Önceki</a>'
    if page < total_pages:
        html += f'<a href="/db/{table_name}?page={page+1}">Sonraki →</a>'
    
    html += """
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🚀 OPTİK FORM OKUYUCU BACKEND")
    print("="*60)
    print("\n📊 Veritabanı başlatılıyor...")
    
    # Veritabanını initialize et
    try:
        db_test = Database()
        print("✅ Veritabanı hazır (optic_forms.db)")
        
        # Tablo sayılarını göster
        conn = db_test.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   👥 Kullanıcılar: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM answer_keys")
        key_count = cursor.fetchone()[0]
        print(f"   📝 Cevap Anahtarları: {key_count}")
        
        cursor.execute("SELECT COUNT(*) FROM student_results")
        result_count = cursor.fetchone()[0]
        print(f"   📊 Sonuçlar: {result_count}")
        conn.close()
        
        if user_count == 0:
            print("\n💡 İpucu: Test kullanıcısı oluşturmak için 'python db_manager.py' çalıştırın")
        
    except Exception as e:
        print(f"⚠️  Veritabanı hatası: {e}")
    
    print("\n📡 API: http://127.0.0.1:5000")
    print("🔧 OpenCV ve Flask hazır")
    print("📋 Veritabanı yönetimi: python db_manager.py")
    print("🌐 DB Viewer: http://127.0.0.1:5000/db")
    print("\n⏹️  Durdurmak için Ctrl+C\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
