# 🚀 HIZLI BAŞLANGIÇ REHBERİ

## 1️⃣ Backend'i Başlat (İlk Çalıştırma)

```bash
# Windows PowerShell'de:
.\start_backend.bat
```

**İlk çalıştırmada:**
- ✅ Sanal ortam otomatik oluşturulur
- ✅ Python paketleri yüklenir
- ✅ `optic_forms.db` veritabanı otomatik oluşturulur
- ✅ 6 tablo otomatik hazırlanır (users, answer_keys, vs.)
- ✅ Backend http://127.0.0.1:5000 adresinde çalışır

---

## 2️⃣ Test Kullanıcısı Oluştur

Backend çalışırken **YENİ BİR TERMINAL** açın:

```bash
# PowerShell'de:
.\veritabani_yonetimi.bat
```

Menüden **[5] Test Kullanıcısı Oluştur** seçin.

**Oluşturulan kullanıcılar:**
- 👤 **Kullanıcı:** `ogretmen` | 🔑 **Şifre:** `123456`
- 👤 **Kullanıcı:** `admin` | 🔑 **Şifre:** `admin123`

---

## 3️⃣ Flutter Uygulamasını Başlat

**YENİ BİR TERMINAL** açın:

```bash
# PowerShell'de:
.\start_flutter.bat
```

Veya manuel:
```bash
flutter pub get
flutter run
```

---

## 4️⃣ Uygulamayı Test Et

1. **Giriş Yap:**
   - Kullanıcı: `ogretmen`
   - Şifre: `123456`

2. **Cevap Anahtarı Oluştur:**
   - "Formlarım" sekmesine git
   - "+" butonuna tıkla
   - Sınav adı ver (örn: "Matematik Sınavı")
   - Dersleri ve cevapları ayarla
   - Kaydet

3. **Form Oku:**
   - "Analiz" sekmesine git
   - Cevap anahtarını seç
   - Fotoğraf çek veya galeriden seç
   - "Formu Analiz Et" butonuna tıkla

4. **Sonuçları Gör:**
   - "Geçmiş" sekmesinde tüm sonuçları görüntüle

---

## 🗄️ Veritabanını Kontrol Et

### Seçenek 1: Komut Satırı (Önerilen)
```bash
.\veritabani_yonetimi.bat
```

**Menü seçenekleri:**
- [1] Veritabanı bilgileri (kayıt sayıları)
- [2] Kullanıcıları listele
- [3] Cevap anahtarlarını göster
- [4] Sonuçları görüntüle
- [5] Test kullanıcısı oluştur
- [6] Veritabanını temizle
- [7] Tablo yapılarını göster

### Seçenek 2: Web Arayüzü (Görsel)
```bash
.\veritabani_tarayici.bat
```
Tarayıcıda aç: http://127.0.0.1:5001

---

## 📂 Proje Yapısı

```
optic-form-reader-2/
│
├── lib/                          # Flutter uygulaması
│   ├── main.dart                 # Ana uygulama
│   ├── login_screen.dart         # Giriş ekranı
│   ├── auth_service.dart         # Login servisi
│   ├── create_form_screen.dart   # Cevap anahtarı oluştur
│   ├── forms_screen.dart         # Form listesi
│   ├── upload_screen.dart        # Form okuma
│   ├── history_screen.dart       # Sonuçlar
│   └── form_service.dart         # API servisi
│
├── backend/                      # Python backend
│   ├── app.py                    # Flask API server
│   ├── database.py               # SQLite yönetimi
│   ├── image_processor.py        # OpenCV görüntü işleme
│   ├── db_manager.py             # Veritabanı yönetim aracı
│   ├── db_viewer.py              # Web tarayıcı
│   ├── optic_forms.db            # SQLite veritabanı (otomatik oluşur)
│   └── requirements.txt          # Python bağımlılıkları
│
├── start_backend.bat             # Backend başlatma scripti
├── start_flutter.bat             # Flutter başlatma scripti
├── veritabani_yonetimi.bat       # DB yönetim aracı
└── veritabani_tarayici.bat       # DB web arayüzü
```

---

## 🔧 Yaygın Sorunlar ve Çözümler

### Backend başlamıyor
```bash
# Bağımlılıkları manuel yükle:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Flutter çalışmıyor
```bash
# Bağımlılıkları yenile:
flutter clean
flutter pub get
flutter run
```

### Veritabanı hatası
```bash
# Veritabanını sıfırla:
del backend\optic_forms.db
# Backend'i yeniden başlat (otomatik oluşturulur)
```

### "Connection refused" hatası
- Backend'in çalıştığından emin olun (http://127.0.0.1:5000)
- Firewall ayarlarını kontrol edin

---

## 📊 Veritabanı Tabloları

Backend ilk çalıştığında otomatik oluşturulur:

1. **users** - Kullanıcı bilgileri
2. **answer_keys** - Sınav cevap anahtarları
3. **subjects** - Ders bilgileri
4. **questions** - Soru ve doğru cevaplar
5. **student_results** - Öğrenci sınav sonuçları
6. **student_answers** - Her sorunun detaylı cevabı

Tüm tablolar **otomatik** oluşturulur, manuel bir işlem gerekmez!

---

## 💡 Önemli Notlar

1. **Backend önce başlatılmalı** - Flutter uygulaması backend'e bağlanır
2. **Veritabanı otomatik** - İlk çalıştırmada oluşturulur
3. **Test kullanıcısı** - Hızlı test için hazır kullanıcılar
4. **Port 5000** - Backend bu portta çalışır
5. **Port 5001** - Veritabanı web tarayıcısı bu portta

---

## 🎯 Sonraki Adımlar

1. ✅ Backend'i başlat
2. ✅ Test kullanıcısı oluştur
3. ✅ Flutter uygulamasını çalıştır
4. ✅ Giriş yap
5. ✅ Cevap anahtarı oluştur
6. ✅ Test et!

---

## 📚 Daha Fazla Bilgi

- **Detaylı README:** `README.md`
- **Backend Dökümantasyonu:** `backend/README.md`
- **Veritabanı Rehberi:** `backend/VERITABANI.md`

---

## 🆘 Yardım

Sorun yaşıyorsanız:

1. **Backend loglarını kontrol edin**
2. **Veritabanını kontrol edin:** `.\veritabani_yonetimi.bat`
3. **Backend'i yeniden başlatın**
4. **Flutter'ı yeniden çalıştırın**

---

**Hazırsınız! 🎉**
