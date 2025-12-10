# Backend Test ve Hata Çözüm Kılavuzu

## 🔍 Hatayı Tespit Etme Adımları

### 1️⃣ Backend Çalışıyor mu?

```bash
# Windows'ta çalışan backend'i kontrol et
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

Veya tarayıcıda açın:
```
http://127.0.0.1:5000
```

Eğer "Cannot GET /" görürseniz backend çalışıyor demektir ✅

### 2️⃣ Backend'i Başlatın

```bash
# Proje klasöründe
cd backend_python
python app.py
```

veya başlatma betiğini kullanın:
```bash
.\start_backend.bat
```

### 3️⃣ Backend Loglarını İzleyin

Backend çalışırken terminal penceresinde şunları göreceksiniz:
- `📥 Form okuma isteği alındı...` - İstek geldi
- `✅ Kullanıcı ID: X` - Giriş yapılmış
- `📄 Dosya adı: ...` - Dosya yüklendi
- `🔑 Cevap anahtarı ID: ...` - Cevap anahtarı seçildi
- `🔬 Görüntü işleme başlıyor...` - OpenCV çalışıyor
- `✅ İşlem başarılı!` - Tamamlandı

**Hata varsa** `❌` işareti ve detaylı hata mesajı göreceksiniz!

## 🐛 Yaygın Hatalar ve Çözümleri

### Hata 1: "Backend çalışmıyor!"
**Çözüm:**
```bash
cd backend_python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Hata 2: "Cevap anahtarı bulunamadı"
**Nedeni:** Henüz cevap anahtarı oluşturmadınız.

**Çözüm:** 
1. Uygulamada "Formlar" sekmesine gidin
2. "Yeni Form Oluştur" butonuna basın
3. Sınav bilgilerini girin ve kaydedin
4. Şimdi "Okut" sekmesinden bu formu seçebilirsiniz

### Hata 3: "Görüntü işleme hatası"
**Nedeni:** OpenCV fotoğrafı işleyemiyor.

**Olası Sebepler:**
- Fotoğraf çok bulanık
- Form açık değil veya eğik
- Işık çok az veya çok fazla
- Fotoğraf formatı desteklenmiyor

**Çözüm:**
1. Fotoğrafı yeniden çekin (daha net, daha düz)
2. İyi ışıklandırma sağlayın
3. Formu düz bir yüzeye koyun
4. JPG veya PNG formatında olduğundan emin olun

### Hata 4: "NoneType object has no attribute"
**Nedeni:** Veritabanı kayıt dönmedi.

**Çözüm:**
```bash
# Veritabanını kontrol edin
cd backend_python
python db_manager.py
# Menüden 1 veya 5 seçin (kullanıcıları ve formları listeleyin)
```

## 🧪 Manuel Test

### Test 1: Backend Erişimi
```bash
curl http://127.0.0.1:5000
```
Cevap: `Cannot GET /` ✅

### Test 2: Register
```bash
curl -X POST http://127.0.0.1:5000/register `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"test\",\"password\":\"123456\"}'
```

### Test 3: Login
```bash
curl -X POST http://127.0.0.1:5000/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"test\",\"password\":\"123456\"}'
```

Token'ı kopyalayın, sonraki testlerde kullanın.

### Test 4: Cevap Anahtarları Listele
```bash
curl http://127.0.0.1:5000/answer-keys `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📋 Checklist

Görüntü yüklerken hata alıyorsanız bu adımları sırayla kontrol edin:

- [ ] Backend çalışıyor mu? (`python app.py`)
- [ ] Veritabanı var mı? (`backend_python/optical_forms.db` dosyası var mı?)
- [ ] Giriş yapıldı mı? (Token var mı?)
- [ ] En az 1 cevap anahtarı oluşturuldu mu?
- [ ] Fotoğraf doğru formatta mı? (JPG/PNG)
- [ ] Fotoğraf çok büyük değil mi? (Max 16MB)
- [ ] Backend loglarında hata var mı?
- [ ] Flutter uygulama loglarında hata var mı?

## 🎯 Tam Test Senaryosu

1. **Backend başlat:**
   ```bash
   .\start_backend.bat
   ```

2. **Flutter başlat:**
   ```bash
   .\start_flutter.bat
   ```

3. **Kullanıcı oluştur ve giriş yap**

4. **Formlar sekmesinde yeni form oluştur:**
   - Sınav adı: "Test Sınavı"
   - Ders: Matematik (yeni)
   - Toplam soru: 20
   - Her sorunun cevabını işaretle (örn: A, B, C, D, E)
   - KAYDET

5. **Okut sekmesine git:**
   - Cevap anahtarı: "Test Sınavı" seçili olmalı
   - Kameradan fotoğraf çek veya galeriden seç
   - "ANALİZ ET" butonuna bas

6. **Backend terminalinde logları izle:**
   - Her adımı görmelisin
   - Hata varsa detaylı açıklama olacak

7. **Sonuç ekranını kontrol et:**
   - Puan, başarı oranı görünmeli
   - Soru detayları görünmeli

## 🚨 Acil Durum

Hiçbir şey çalışmıyorsa:

```bash
# Yeni baştan
cd backend_python
Remove-Item venv -Recurse -Force
Remove-Item optical_forms.db -Force
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Başka terminalde:
```bash
# Flutter temizle ve yeniden başlat
flutter clean
flutter pub get
flutter run
```
