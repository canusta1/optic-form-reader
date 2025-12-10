# 🎓 LGS Optik Form Okuma Sistemi - Kullanım Kılavuzu

## 📋 Özellikler

### ✨ Yeni: Gelişmiş LGS Form Desteği

Artık sistem **LGS 20-20 standart formları** otomatik olarak okuyabiliyor:

- ✅ **Öğrenci Bilgileri**: Öğrenci no ve TC kimlik otomatik okunur
- ✅ **QR Kod Desteği**: Varsa QR kod bilgileri alınır
- ✅ **Bölüm Bazlı Okuma**: Türkçe, Sosyal, Din, İngilizce, Matematik, Fen ayrı ayrı
- ✅ **Form Hizalama**: Eğik veya perspektif bozuk fotoğrafları düzeltir
- ✅ **Yüksek Hassasiyet**: Gelişmiş bubble algılama algoritması

## 🚀 Kurulum

### 1. Backend Kurulumu

```bash
cd backend
pip install -r requirements.txt
```

**Yeni Kütüphane**: `pyzbar` QR kod okuma için eklendi.

**Windows için ek adım** (QR kod okumak istiyorsanız):
```bash
# ZBar DLL'i indirin ve PATH'e ekleyin
# https://sourceforge.net/projects/zbar/files/zbar/0.10/
```

### 2. Backend Başlatma

```bash
python app.py
```

Backend `http://127.0.0.1:5000` adresinde çalışacak.

### 3. Flutter Başlatma

```bash
flutter pub get
flutter run -d chrome
```

## 📝 Adım Adım Kullanım

### 1. Giriş Yapın

- Kayıt olun veya mevcut hesabınızla giriş yapın

### 2. Cevap Anahtarı Oluşturun

**a) "Formlar" sekmesine gidin**

**b) "Yeni Form Oluştur" butonuna tıklayın**

**c) Form Bilgilerini Doldurun:**
- **Form Adı**: Örn: "8. Sınıf Deneme Sınavı"
- **Form Şablonu**: 🆕 **"LGS 20-20 - İlkokul ve Ortaokul Cevap Kağıdı"** seçin
- **Okul Türü**: Ortaokul/Lise

**d) LGS Form Şablonu Seçtiyseniz:**

Sistem otomatik olarak şu bölümleri ekler:
- **TÜRKÇE**: 20 soru
- **SOSYAL BİLGİLER**: 20 soru
- **DİN KÜLTÜRÜ VE AHLAK BİLGİSİ**: 10 soru
- **İNGİLİZCE**: 10 soru
- **MATEMATİK**: 20 soru
- **FEN BİLİMLERİ**: 20 soru

Her bölüm için doğru cevapları işaretleyin!

**e) KAYDET** butonuna basın

### 3. Optik Form Okutun

**a) "Okut" sekmesine gidin**

**b) Oluşturduğunuz formu seçin**

**c) Fotoğraf Çekin veya Yükleyin:**
- 📷 Kamera ile çek
- 🖼️ Galeriden seç

**Fotoğraf İpuçları:**
- ✅ İyi ışıklandırma
- ✅ Formun tamamı görünsün
- ✅ Mümkün olduğunca düz açı
- ⚠️ Bulanık veya çok eğik fotoğraflardan kaçının

**d) "ANALİZ ET" butonuna basın**

**e) Sonuçları İnceleyin:**

LGS formları için özel sonuç ekranı:
```
👤 Öğrenci No: 1234567
🆔 TC Kimlik: 12345678901

📚 BÖLÜM SONUÇLARI:

TÜRKÇE:        18/20  ✅ 90%
SOSYAL:        16/20  ✅ 80%
DİN KÜLTÜRÜ:    9/10  ✅ 90%
İNGİLİZCE:      7/10  ⚠️ 70%
MATEMATİK:     15/20  ⚠️ 75%
FEN BİLİMLERİ: 17/20  ✅ 85%

TOPLAM: 82/90  ✅ 91.1%
```

### 4. Geçmiş Kayıtlara Bakın

**"Geçmiş" sekmesinden** tüm okutma sonuçlarını görebilirsiniz.

## 🎯 Form Şablonu Türleri

### 1. Basit Optik Form (Genel Amaçlı)
- Manuel soru ve ders tanımlama
- Esnek yapı
- Her türlü sınav için uygun

### 2. LGS 20-20 Form 🆕
- Standart LGS formu yapısı
- Otomatik bölüm tanıma
- Öğrenci bilgisi okuma
- QR kod desteği
- Daha hızlı ve hassas

## 🔧 Gelişmiş Özellikler

### QR Kod Kullanımı

LGS formlarında QR kod varsa:
- Öğrenci bilgileri otomatik çıkar
- Form tipi otomatik tanınır
- Manuel giriş gereksiz olur

### Form Hizalama

Eğik veya perspektif bozuk fotoğraflar:
- Otomatik düzeltilir
- Köşe noktaları bulunur
- Perspektif düzeltme uygulanır

### Bölüm Bazlı Analiz

Her ders için ayrı:
- Doğru/yanlış sayısı
- Başarı yüzdesi
- Puan hesaplama
- Detaylı soru analizi

## 🐛 Sorun Giderme

### "Form yapısı beklenenle uyuşmuyor"

**Çözüm:**
1. Fotoğrafı daha düz ve net çekin
2. Tüm formun görünür olduğundan emin olun
3. İyi ışıklandırma sağlayın
4. Form şablonunun doğru seçildiğini kontrol edin

### "Öğrenci numarası okunamadı"

**Çözüm:**
1. Bubble'lar tam doldurulmuş olmalı
2. Silikler temiz silinmeli
3. Fotoğraf kalitesi yüksek olmalı

### "QR kod okunamıyor"

**Çözüm:**
1. Windows için ZBar DLL'ini yükleyin
2. QR kod net görünür olmalı
3. Backend loglarında "QR kod" satırını kontrol edin

### Koordinatlar Yanlış

Eğer cevaplar yanlış okunuyorsa:
1. `backend/form_templates.py` dosyasını açın
2. `LGS_20_20_TEMPLATE` içindeki koordinatları ayarlayın
3. `layout` altındaki piksel değerlerini değiştirin
4. Test et → Ayarla → Tekrar test et

## 📊 Veritabanı Yönetimi

### CLI Aracı
```bash
cd backend
python db_manager.py
```

### Web Arayüzü
```bash
cd backend
python db_viewer.py
```
Tarayıcıda: `http://127.0.0.1:5001`

## 🎨 Form Şablonu Özelleştirme

Kendi form şablonunuzu oluşturmak için:

1. `backend/form_templates.py` dosyasını açın

2. Yeni şablon ekleyin:
```python
MY_CUSTOM_TEMPLATE = {
    'name': 'Benim Formum',
    'description': 'Özel sınav formu',
    'total_questions': 50,
    'sections': [
        {
            'name': 'BÖLÜM 1',
            'code': 'B1',
            'start_question': 1,
            'end_question': 25,
            'position': 'left',
            'choices': ['A', 'B', 'C', 'D']
        },
        # ...
    ],
    'layout': {
        # Koordinatlar...
    }
}
```

3. `FORM_TEMPLATES` dictionary'sine ekleyin:
```python
FORM_TEMPLATES = {
    'my_custom': MY_CUSTOM_TEMPLATE,
    # ...
}
```

4. Backend'i yeniden başlatın

5. Flutter uygulamada yeni şablon görünecek!

## 📈 İstatistikler

Geçmiş sekmesinde:
- Toplam okutma sayısı
- Ortalama başarı oranı
- Ders bazlı performans
- Zaman içinde gelişim

## 💡 İpuçları

1. **Toplu Okuma**: Birden fazla formu arka arkaya okutabilirsiniz
2. **Cevap Anahtarı Yeniden Kullanım**: Aynı cevap anahtarını farklı öğrenciler için kullanın
3. **Yedekleme**: Veritabanı dosyasını (`optical_forms.db`) düzenli yedekleyin
4. **Test Modu**: Önce boş form ile test edin, sonra gerçek formları okutun
5. **Kalibrasyon**: İlk kullanımda birkaç test formu ile koordinatları ayarlayın

## 🔄 Güncelleme Notları

### v2.0 - LGS Desteği
- ✅ LGS 20-20 form şablonu
- ✅ QR kod okuma
- ✅ Öğrenci bilgisi tanıma
- ✅ Bölüm bazlı analiz
- ✅ Form hizalama
- ✅ Perspektif düzeltme

### v1.0 - İlk Sürüm
- ✅ Temel optik form okuma
- ✅ Kullanıcı sistemi
- ✅ Cevap anahtarı yönetimi

## 📞 Destek

Sorun yaşarsanız:
1. Backend loglarını kontrol edin
2. Flutter debug console'a bakın
3. `TEST_BACKEND.md` dosyasını okuyun
4. GitHub Issues'da sorun bildirin

## 🎉 Başarılar!

Artık LGS formlarını profesyonel bir şekilde okutabilirsiniz!
