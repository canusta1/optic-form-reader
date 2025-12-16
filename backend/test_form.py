"""
Optik Form Okuyucu Test Script
Perspektif düzeltme ve cevap okuma testleri
"""
import os
import sys
import cv2

# Modülü import et
from image_processor import OptikFormOkuyucu

def test_goruntu(goruntu_yolu: str):
    """Tek bir görüntüyü test et"""
    
    if not os.path.exists(goruntu_yolu):
        print(f"❌ Dosya bulunamadı: {goruntu_yolu}")
        return
    
    print("\n" + "="*60)
    print(f"TEST: {goruntu_yolu}")
    print("="*60)
    
    # Debug modunda okuyucu oluştur
    okuyucu = OptikFormOkuyucu(debug_mode=True)
    
    # Formu oku
    sonuc = okuyucu.form_oku(goruntu_yolu)
    
    if sonuc['success']:
        print("\n✅ Form başarıyla okundu!")
        print(f"\n👤 Öğrenci Bilgileri:")
        print(f"   Ad: {sonuc['student_info']['name']}")
        print(f"   Soyad: {sonuc['student_info']['surname']}")
        
        print(f"\n📝 Cevaplar ({len(sonuc['answers'])} soru):")
        
        # Ders bazlı özet
        if 'sections' in sonuc:
            for ders, cevaplar in sonuc['sections'].items():
                bos = sum(1 for v in cevaplar.values() if v == 'BOŞ')
                dolu = len(cevaplar) - bos
                print(f"   {ders.upper()}: {dolu}/{len(cevaplar)} işaretli")
                
                # İlk 10 cevabı göster
                ilk_10 = {k: v for k, v in list(cevaplar.items())[:10]}
                print(f"      İlk 10: {ilk_10}")
        
        print("\n📁 Debug görüntüleri: backend/debug_images/")
        
    else:
        print(f"\n❌ Hata: {sonuc.get('error')}")
    
    return sonuc


def main():
    # uploads klasöründeki görüntüleri tara
    uploads_dir = "uploads"
    
    if not os.path.exists(uploads_dir):
        print("uploads klasörü bulunamadı!")
        return
    
    # Tüm jpg/png dosyalarını bul
    dosyalar = [f for f in os.listdir(uploads_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not dosyalar:
        print("uploads klasöründe görüntü bulunamadı!")
        print("Lütfen test etmek için bir form görüntüsü yükleyin.")
        return
    
    # En son yüklenen dosyayı test et
    dosyalar.sort(key=lambda x: os.path.getmtime(os.path.join(uploads_dir, x)), reverse=True)
    
    en_son = dosyalar[0]
    test_goruntu(os.path.join(uploads_dir, en_son))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Parametre olarak dosya yolu verilmişse
        test_goruntu(sys.argv[1])
    else:
        main()
