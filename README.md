# Optik Form Okuyucu Projesi

## 📱 Görüntü İşleme Projesi - Optik Form Okuyucu

Bu proje, OpenCV kullanarak optik formları okuyabilen, Flutter mobil uygulaması ve Python Flask backend'den oluşan tam kapsamlı bir sistemdir.

## 🎯 Proje Özellikleri

### ✅ Tamamlanan Özellikler

1. **Kullanıcı Yönetimi**
   - Login/Register sistemi
   - JWT token tabanlı authentication
   - Kullanıcı profili yönetimi

2. **Cevap Anahtarı Sistemi**
   - Sınav için cevap anahtarı oluşturma
   - Ders bazlı soru ve puan tanımlama
   - Cevap anahtarları listeleme

3. **Form Okuma ve Analiz**
   - Kamera ile fotoğraf çekme
   - Galeriden görsel seçme
   - OpenCV ile otomatik form tespiti
   - Kutucuk işaretlerini algılama
   - Cevapları karşılaştırma ve puanlama

4. **Sonuç Yönetimi**
   - Öğrenci sonuçlarını kaydetme
   - Sonuçları listeleme
   - Detaylı sonuç görüntüleme
   - İstatistikler ve raporlar

## 🛠 Teknolojiler

### Frontend (Flutter)
- Flutter 3.x
- Material Design 3
- HTTP paket ile REST API iletişimi
- Image Picker (kamera/galeri)
- JWT authentication

### Backend (Python)
- Flask web framework
- OpenCV (görüntü işleme)
- SQLite veritabanı
- JWT authentication
- CORS desteği

## 📦 Kurulum

### Flutter Uygulaması

1. Bağımlılıkları yükleyin:
```bash
flutter pub get
```

2. Uygulamayı çalıştırın:
```bash
flutter run
```

### Python Backend

1. Backend klasörüne gidin:
```bash
cd backend
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Backend'i başlatın:
```bash
python app.py
```

Backend http://127.0.0.1:5000 adresinde çalışacaktır.

## 🚀 Kullanım

1. **Kayıt Olun**: İlk açılışta kayıt ekranından hesap oluşturun
2. **Giriş Yapın**: Kullanıcı adı ve şifrenizle giriş yapın
3. **Cevap Anahtarı Oluşturun**: "Formlarım" sekmesinden yeni sınav cevap anahtarı oluşturun
4. **Form Okuyun**: "Analiz" sekmesinden:
   - Cevap anahtarı seçin
   - Fotoğraf çekin veya galeriden seçin
   - "Formu Analiz Et" butonuna tıklayın
5. **Sonuçları Görün**: "Geçmiş" sekmesinden tüm sonuçları inceleyin

## 🔬 Görüntü İşleme Algoritması

Proje OpenCV kullanarak şu adımları gerçekleştirir:

1. **Ön İşleme**
   - Gri tonlamaya çevirme
   - Gaussian blur ile gürültü azaltma
   - Adaptive threshold uygulama

2. **Form Tespiti**
   - Kontur tespiti
   - En büyük dörtgen bulma (form)
   - Perspektif düzeltme

3. **Kutucuk Algılama**
   - Morfolojik işlemler
   - Kontur filtreleme (alan ve şekil kontrolü)
   - Satırlara göre gruplama

4. **İşaret Tespiti**
   - Kutucuk içi piksel yoğunluğu hesaplama
   - Threshold ile dolu/boş kontrolü
   - Cevap belirleme (A, B, C, D, E)

5. **Sonuç Üretimi**
   - Cevap anahtarı ile karşılaştırma
   - Ders bazlı puanlama
   - Toplam skor ve başarı oranı hesaplama

## 📊 Veritabanı Yapısı

- **users**: Kullanıcı bilgileri
- **answer_keys**: Sınav cevap anahtarları
- **subjects**: Ders bilgileri
- **questions**: Soru detayları
- **student_results**: Öğrenci sonuçları
- **student_answers**: Öğrenci cevapları

## 🔐 Güvenlik

- JWT token tabanlı authentication
- Şifre hashleme (SHA-256)
- CORS yapılandırması
- Dosya upload validasyonu
- Token süresi sınırlama (7 gün)

## 📝 Geliştirme Notları

- Backend ve Frontend ayrı çalıştırılmalıdır
- Backend varsayılan olarak `127.0.0.1:5000` portunda çalışır
- Kamera özelliği için fiziksel cihaz veya emülatör gereklidir
- Windows'ta Developer Mode aktif olmalıdır (symlink desteği için)

---

**Not**: İlk çalıştırmada backend'de veritabanı otomatik oluşturulacaktır. Test için örnek kullanıcı oluşturup sistemi deneyebilirsiniz.
