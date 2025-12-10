from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import traceback

from database import Database
from image_processor import OpticalFormReader, AdvancedFormReader
from advanced_form_reader import AdvancedOpticalFormReader
from form_templates import list_templates, get_template

app = Flask(__name__)
CORS(app)

# Konfigürasyon
app.config['SECRET_KEY'] = 'optic-form-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Klasörleri oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('processed', exist_ok=True)

# Database ve image processor
db = Database()
form_reader = AdvancedFormReader()  # Basit formlar için
lgs_reader = AdvancedOpticalFormReader('lgs_20_20')  # LGS formları için

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_token(user_id):
    """JWT token oluştur"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

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

# ============== AUTH ENDPOINTS ==============

@app.route('/register', methods=['POST'])
def register():
    """Kullanıcı kayıt"""
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
    """Kullanıcı girişi"""
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

# ============== ANSWER KEY ENDPOINTS ==============

@app.route('/answer-keys', methods=['POST'])
def create_answer_key():
    """Cevap anahtarı oluştur veya güncelle (form adına göre)"""
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
    """Mevcut form şablonlarını listele"""
    try:
        templates = list_templates()
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/answer-keys', methods=['GET'])
def get_answer_keys():
    """Kullanıcının cevap anahtarlarını listele"""
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
    """Cevap anahtarı detayları"""
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
    """Form adına göre cevap anahtarı bul"""
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

# ============== FORM READING ENDPOINT ==============

@app.route('/read-optic-form', methods=['POST'])
def read_optic_form():
    """
    Optik formu oku ve analiz et
    """
    print("\n📥 Form okuma isteği alındı...")
    
    user_id = get_current_user()
    if not user_id:
        print("❌ Yetkisiz erişim")
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    print(f"✅ Kullanıcı ID: {user_id}")
    
    # Dosya kontrolü
    if 'file' not in request.files:
        print("❌ Dosya bulunamadı")
        return jsonify({'error': 'Dosya bulunamadı'}), 400
    
    file = request.files['file']
    if file.filename == '':
        print("❌ Dosya seçilmedi")
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    if not allowed_file(file.filename):
        print(f"❌ Geçersiz dosya formatı: {file.filename}")
        return jsonify({'error': 'Geçersiz dosya formatı (Sadece jpg, jpeg, png)'}), 400
    
    print(f"📄 Dosya adı: {file.filename}")
    
    # Cevap anahtarı ID'si
    answer_key_id = request.form.get('answer_key_id')
    if not answer_key_id:
        print("❌ Cevap anahtarı ID eksik")
        return jsonify({'error': 'Cevap anahtarı ID gerekli'}), 400
    
    print(f"🔑 Cevap anahtarı ID: {answer_key_id}")
    
    try:
        # Dosyayı kaydet
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"💾 Dosya kaydediliyor: {filepath}")
        file.save(filepath)
        print("✅ Dosya kaydedildi")
        
        # Cevap anahtarını al
        print(f"🔍 Cevap anahtarı getiriliyor...")
        answer_key = db.get_answer_key_details(int(answer_key_id))
        
        if not answer_key:
            print("❌ Cevap anahtarı bulunamadı")
            return jsonify({'error': 'Cevap anahtarı bulunamadı'}), 404
        
        print(f"✅ Cevap anahtarı bulundu: {answer_key.get('exam_name')}")
        print(f"📊 Toplam soru sayısı: {answer_key['total_questions']}")
        
        # Form şablonuna göre doğru reader'ı seç
        form_template = answer_key.get('form_template', 'simple')
        print(f"📋 Form şablonu: {form_template}")
        
        # Görüntü işleme ile cevapları oku
        total_questions = answer_key['total_questions']
        print(f"🔬 Görüntü işleme başlıyor...")
        
        if form_template == 'lgs_20_20':
            # LGS formları için gelişmiş okuyucu
            print("📚 LGS form okuyucu kullanılıyor...")
            detection_result = lgs_reader.read_form(filepath)
            
            if 'error' in detection_result:
                print(f"❌ LGS form okuma hatası: {detection_result['error']}")
                return jsonify(detection_result), 400
            
            # Öğrenci bilgilerini al
            student_info = detection_result.get('student_info', {})
            print(f"👤 Öğrenci No: {student_info.get('student_number', 'Yok')}")
            print(f"🆔 TC Kimlik: {student_info.get('tc_kimlik', 'Yok')}")
            
            # Bölüm bazlı cevapları düzleştir
            section_answers = detection_result.get('answers', {})
            all_answers = {}
            question_num = 1
            
            for section_code, answers in section_answers.items():
                print(f"   {section_code}: {len(answers)} soru")
                for q, ans in answers.items():
                    all_answers[question_num] = ans
                    question_num += 1
            
            detection_result = {'answers': all_answers, 'student_info': student_info}
            
        else:
            # Basit formlar için eski okuyucu
            print("📄 Basit form okuyucu kullanılıyor...")
            detection_result = form_reader.detect_answers(filepath, total_questions)
            
            if 'error' in detection_result:
                print(f"❌ Görüntü işleme hatası: {detection_result['error']}")
                return jsonify(detection_result), 400
        
        print(f"✅ Görüntü işleme tamamlandı")
        print(f"📝 Tespit edilen cevaplar: {len(detection_result.get('answers', {}))}")
        
        student_answers = detection_result['answers']
        
        # Cevapları karşılaştır ve puanla
        print(f"⚖️  Cevaplar karşılaştırılıyor...")
        result = compare_answers(answer_key, student_answers)
        print(f"✅ Karşılaştırma tamamlandı")
        print(f"📊 Puan: {result['total_score']} - Başarı: %{result['success_rate']}")
        
        # Sonuçları veritabanına kaydet
        student_data = {
            'name': result.get('student_name', 'Bilinmiyor'),
            'number': result.get('student_number', 'Bilinmiyor'),
            'total_score': result['total_score'],
            'success_rate': result['success_rate']
        }
        
        print(f"💾 Sonuçlar veritabanına kaydediliyor...")
        result_id = db.save_student_result(
            int(answer_key_id),
            student_data,
            result['detailed_answers'],
            filepath
        )
        print(f"✅ Sonuçlar kaydedildi (ID: {result_id})")
        
        response = {
            'success': True,
            'result_id': result_id,
            'student_name': student_data['name'],
            'student_number': student_data['number'],
            'total_score': result['total_score'],
            'success_rate': result['success_rate'],
            'subject_scores': result['subject_scores'],
            'details': f"{result['correct_count']}/{total_questions} doğru"
        }
        
        print(f"✅ İşlem başarılı!\n")
        return jsonify(response)
        
    except Exception as e:
        print(f"\n❌ HATA OLUŞTU!")
        print(f"Hata mesajı: {e}")
        print("Detaylı hata:")
        traceback.print_exc()
        print()
        
        error_message = str(e)
        if 'NoneType' in error_message:
            error_message = 'Cevap anahtarı veya form bilgisi eksik'
        elif 'list index' in error_message:
            error_message = 'Form yapısı beklenenle uyuşmuyor'
        
        return jsonify({'error': f'İşlem hatası: {error_message}'}), 500

def compare_answers(answer_key, student_answers):
    """
    Öğrenci cevaplarını cevap anahtarı ile karşılaştır
    """
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

# ============== RESULTS ENDPOINTS ==============

@app.route('/results/<int:answer_key_id>', methods=['GET'])
def get_results(answer_key_id):
    """Belirli bir cevap anahtarına ait sonuçları listele"""
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
    """Tüm sonuçları listele"""
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Yetkisiz erişim'}), 401
    
    try:
        results = db.get_all_results(user_id)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== HEALTH CHECK ==============

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Optik Form API çalışıyor'})

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
    print("🌐 Web tarayıcı: python db_viewer.py")
    print("\n⏹️  Durdurmak için Ctrl+C\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
