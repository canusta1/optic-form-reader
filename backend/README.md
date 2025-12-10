# Optik Form Okuyucu - Backend

Bu klasör Python Flask backend'i içerir.

## Kurulum

1. Python sanal ortamı oluşturun:
```bash
python -m venv venv
```

2. Sanal ortamı aktifleştirin:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python app.py
```

Server http://127.0.0.1:5000 adresinde çalışmaya başlayacak.

## API Endpoints

### Authentication
- `POST /register` - Yeni kullanıcı kaydı
- `POST /login` - Kullanıcı girişi

### Cevap Anahtarları
- `POST /answer-keys` - Cevap anahtarı oluştur
- `GET /answer-keys` - Kullanıcının cevap anahtarlarını listele
- `GET /answer-keys/<id>` - Cevap anahtarı detayı

### Form Okuma
- `POST /read-optic-form` - Optik formu oku ve analiz et

### Sonuçlar
- `GET /results/<answer_key_id>` - Belirli bir cevap anahtarına ait sonuçlar
- `GET /all-results` - Kullanıcının tüm sonuçları

## Özellikler

- OpenCV ile görüntü işleme
- Optik işaretleme tespiti
- Perspektif düzeltme
- Cevap karşılaştırma ve puanlama
- SQLite veritabanı
- JWT authentication
