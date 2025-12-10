# 🗄️ Veritabanı Yönetimi

## SQLite Veritabanı Hakkında

SQLite otomatik olarak oluşturulur. Backend ilk çalıştırıldığında `optic_forms.db` dosyası oluşturulur ve tüm tablolar hazırlanır.

## 📍 Veritabanı Dosyası Konumu

```
backend/optic_forms.db
```

## 🛠️ Veritabanı Yönetim Araçları

### 1️⃣ Komut Satırı Aracı (Önerilen)

Veritabanını yönetmek için interaktif menü:

```bash
# Çalıştır:
python db_manager.py

# Veya Windows'ta:
..\veritabani_yonetimi.bat
```

**Özellikler:**
- ✅ Veritabanı bilgilerini göster
- 👥 Kullanıcıları listele
- 📝 Cevap anahtarlarını göster
- 📊 Sonuçları görüntüle
- ➕ Test kullanıcısı oluştur
- 🗑️ Veritabanını temizle
- 📋 Tablo yapılarını göster

### 2️⃣ Web Arayüzü (Görsel)

Modern web tarayıcısı ile veritabanını görüntüle:

```bash
# Çalıştır:
python db_viewer.py

# Tarayıcıda aç:
http://127.0.0.1:5001
```

**Özellikler:**
- 📊 Tüm tabloları görsel olarak göster
- 🔄 Yenile butonu
- 📈 İstatistikler
- 🎨 Modern arayüz

### 3️⃣ SQL Komutları

Direkt SQLite ile bağlan:

```bash
sqlite3 optic_forms.db
```

Yararlı komutlar:
```sql
-- Tüm tabloları göster
.tables

-- Kullanıcıları listele
SELECT * FROM users;

-- Cevap anahtarlarını göster
SELECT ak.*, u.username 
FROM answer_keys ak 
JOIN users u ON ak.user_id = u.id;

-- Sonuçları göster
SELECT sr.*, ak.exam_name 
FROM student_results sr 
JOIN answer_keys ak ON sr.answer_key_id = ak.id;

-- Çıkış
.quit
```

## 🏗️ Veritabanı Yapısı

### 1. users (Kullanıcılar)
```sql
id               INTEGER PRIMARY KEY
username         TEXT UNIQUE
email            TEXT UNIQUE
password_hash    TEXT
full_name        TEXT
created_at       TIMESTAMP
```

### 2. answer_keys (Cevap Anahtarları)
```sql
id               INTEGER PRIMARY KEY
user_id          INTEGER (FK -> users.id)
exam_name        TEXT
school_type      TEXT
total_questions  INTEGER
created_at       TIMESTAMP
```

### 3. subjects (Dersler)
```sql
id                   INTEGER PRIMARY KEY
answer_key_id        INTEGER (FK -> answer_keys.id)
subject_name         TEXT
question_count       INTEGER
points_per_question  REAL
```

### 4. questions (Sorular)
```sql
id              INTEGER PRIMARY KEY
subject_id      INTEGER (FK -> subjects.id)
question_number INTEGER
correct_answer  TEXT
points          REAL
```

### 5. student_results (Öğrenci Sonuçları)
```sql
id              INTEGER PRIMARY KEY
answer_key_id   INTEGER (FK -> answer_keys.id)
student_name    TEXT
student_number  TEXT
total_score     REAL
success_rate    REAL
image_path      TEXT
exam_date       TIMESTAMP
```

### 6. student_answers (Öğrenci Cevapları)
```sql
id              INTEGER PRIMARY KEY
result_id       INTEGER (FK -> student_results.id)
subject_id      INTEGER (FK -> subjects.id)
question_number INTEGER
student_answer  TEXT
correct_answer  TEXT
is_correct      BOOLEAN
points_earned   REAL
```

## 🚀 Hızlı Başlangıç

### Test Kullanıcısı Oluştur

```bash
python db_manager.py
# Menüden [5] Test Kullanıcısı Oluştur
```

**Hazır test kullanıcıları:**
- **Kullanıcı:** ogretmen | **Şifre:** 123456
- **Kullanıcı:** admin | **Şifre:** admin123

### Veritabanını Kontrol Et

```bash
python db_manager.py
# Menüden [1] Veritabanı Bilgileri
```

### Tabloları Göster

```bash
python db_manager.py
# Menüden [7] Tablo Yapılarını Göster
```

## 🔄 Backup ve Restore

### Yedekleme
```bash
# Windows
copy backend\optic_forms.db backup\optic_forms_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db

# Linux/Mac
cp backend/optic_forms.db backup/optic_forms_backup_$(date +%Y%m%d).db
```

### Geri Yükleme
```bash
# Windows
copy backup\optic_forms_backup_20241207.db backend\optic_forms.db

# Linux/Mac
cp backup/optic_forms_backup_20241207.db backend/optic_forms.db
```

## 🗑️ Veritabanını Sıfırla

### Tüm verileri sil
```bash
python db_manager.py
# Menüden [6] Veritabanını Temizle
```

### Veya dosyayı sil ve yeniden başlat
```bash
# Veritabanı dosyasını sil
rm backend/optic_forms.db  # Linux/Mac
del backend\optic_forms.db  # Windows

# Backend'i başlat (otomatik yeniden oluşturulur)
python app.py
```

## 📊 Örnek Sorgular

### En başarılı öğrenciler
```sql
SELECT student_name, student_number, total_score, success_rate
FROM student_results
ORDER BY success_rate DESC
LIMIT 10;
```

### Sınav bazlı istatistikler
```sql
SELECT 
    ak.exam_name,
    COUNT(sr.id) as student_count,
    AVG(sr.success_rate) as avg_success,
    MAX(sr.total_score) as max_score
FROM answer_keys ak
LEFT JOIN student_results sr ON ak.id = sr.answer_key_id
GROUP BY ak.id;
```

### Kullanıcı aktivitesi
```sql
SELECT 
    u.username,
    u.full_name,
    COUNT(DISTINCT ak.id) as exam_count,
    COUNT(DISTINCT sr.id) as result_count
FROM users u
LEFT JOIN answer_keys ak ON u.id = ak.user_id
LEFT JOIN student_results sr ON ak.id = sr.answer_key_id
GROUP BY u.id;
```

## 🔍 Troubleshooting

### "database is locked" hatası
```bash
# Tüm Python process'leri kapat
taskkill /F /IM python.exe  # Windows

# Veya veritabanı bağlantılarını kapat
```

### Veritabanı bozuldu
```bash
# Yedek yoksa:
rm optic_forms.db
python app.py  # Yeniden oluşturulur

# Yedek varsa:
cp backup/optic_forms_backup.db optic_forms.db
```

### Tablolar yok
```bash
# database.py dosyasını kontrol et
# Backend'i yeniden başlat
python app.py
```

## 📱 Mobil Uygulamadan Erişim

Flutter uygulaması otomatik olarak backend API'yi kullanır. Veritabanına direkt erişim gerekmez.

API endpoint'leri:
- `POST /register` - Yeni kullanıcı (users tablosuna ekler)
- `POST /login` - Giriş
- `POST /answer-keys` - Cevap anahtarı (answer_keys, subjects, questions)
- `POST /read-optic-form` - Form okuma (student_results, student_answers)
- `GET /all-results` - Sonuçlar

## 💡 İpuçları

1. **Düzenli yedek alın** - Özellikle production'da
2. **Test kullanıcısı kullanın** - Geliştirme aşamasında
3. **Web arayüzünü kullanın** - Kolay görselleştirme için
4. **Komut satırı aracını kullanın** - Hızlı yönetim için
5. **SQLite Browser kullanın** - Detaylı analiz için ([DB Browser for SQLite](https://sqlitebrowser.org/))

---

**Not:** Veritabanı dosyası `.gitignore` içinde olmalıdır. Yedeklerinizi güvenli bir yerde saklayın.
