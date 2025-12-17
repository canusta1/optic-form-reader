"""
Optik Form Okuyucu - Görüntü İşleme Modülü
==========================================
YGS Cevap Formu için özelleştirilmiş optik form okuyucu.

Özellikler:
- Perspektif düzeltme
- Gürültü temizleme
- Ad/Soyad okuma
- 4 ders bölümü okuma (Türkçe, Matematik, Fen, Sosyal)
- Her derste 40 soru, 5 seçenek (A-E)
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

class OptikFormOkuyucu:
    """
    YGS Optik Form Okuyucu
    
    Form yapısı:
    - Sol üst: Ad (12 sütun x 26 satır A-Z)
    - Sol alt: Soyad (12 sütun x 26 satır A-Z)
    - Sağ taraf: 4 ders bölümü (her biri 40 soru x 5 seçenek)
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.debug_dir = "debug_images"
        
        if self.debug_mode:
            os.makedirs(self.debug_dir, exist_ok=True)
        
        # Seçenek harfleri
        self.secenekler = ['A', 'B', 'C', 'D', 'E']
        
        # Türk alfabesi (Ad/Soyad için)
        self.alfabe = list("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")
        
        # Form bölge oranları (normalize edilmiş koordinatlar)
        # YGS formu yapısına göre kalibre edilmiş
        # Form yapısı: Sol tarafta Ad/Soyad, sağ tarafta 4 ders bölümü
        self.bolge_oranlari = {
            # Ad bölgesi - sol üst köşe (genişletildi)
            'ad': {
                'x1': 0.080, 'y1': 0.092,
                'x2': 0.3, 'y2': 0.500
            },
            # Soyad bölgesi - Ad'ın altında (genişletildi)
            'soyad': {
                'x1': 0.080, 'y1': 0.530,
                'x2': 0.3, 'y2': 0.94
            },
            # Türkçe - ilk ders sütunu (soldan daraltıldı, üstten 6 bubble küçültüldü)
            'turkce': {
                'x1': 0.315, 'y1': 0.385,
                'x2': 0.42, 'y2': 0.94
            },
            # T.Matematik - ikinci ders sütunu (sağa doğru genişletildi)
            'matematik': {
                'x1': 0.45, 'y1': 0.385,
                'x2': 0.585, 'y2': 0.94
            },
            # Sosyal Bil. - üçüncü ders sütunu (fen ile yer değiştirildi)
            'sosyal': {
                'x1': 0.595, 'y1': 0.385,
                'x2': 0.745, 'y2': 0.94 
            },
            # Fen Bilimleri - dördüncü ders sütunu (sosyal ile yer değiştirildi)
            'fen': {
                'x1': 0.74, 'y1': 0.385,
                'x2': 0.89, 'y2': 0.94
            }
        }
    
    def form_oku(self, goruntu_yolu: str) -> Dict:
        """
        Ana fonksiyon - Optik formu oku ve sonuçları döndür
        
        Args:
            goruntu_yolu: Form görüntüsünün dosya yolu
            
        Returns:
            Dict: {
                'success': bool,
                'student_info': {'name': str, 'surname': str},
                'answers': {1: 'A', 2: 'B', ...},
                'sections': {
                    'turkce': {1: 'A', ...},
                    'matematik': {1: 'B', ...},
                    ...
                }
            }
        """
        try:
            # 1. Görüntüyü yükle
            print(f"📷 Görüntü yükleniyor: {goruntu_yolu}")
            orijinal = cv2.imread(goruntu_yolu)
            
            if orijinal is None:
                return {'success': False, 'error': 'Görüntü yüklenemedi'}
            
            print(f"   Boyut: {orijinal.shape[1]}x{orijinal.shape[0]}")
            
            # 2. Perspektif düzeltme
            print("🔧 Perspektif düzeltme yapılıyor...")
            duzeltilmis = self.perspektif_duzelt(orijinal)
            
            if duzeltilmis is None:
                return {'success': False, 'error': 'Perspektif düzeltme başarısız'}
            
            # 2.5 Yöneliş kontrolü (orientation check) - Kağıt doğru yöneliş'te mi?
            print("📐 Yöneliş kontrolü yapılıyor...")
            duzeltilmis = self.yonelisini_kontrol_et(duzeltilmis)
            
            # 3. Bölgeleri çıkar (sadece renkli görüntüden)
            print("📐 Form bölgeleri çıkarılıyor...")
            bolgeler = self.bolgeleri_cikar_renkli(duzeltilmis)
            
            # 4. Ad/Soyad oku
            print("👤 Ad/Soyad okunuyor...")
            ad = self.isim_oku_renkli(bolgeler.get('ad'), 12, 'ad')
            soyad = self.isim_oku_renkli(bolgeler.get('soyad'), 12, 'soyisim')
            
            print(f"   Ad: {ad}")
            print(f"   Soyad: {soyad}")
            
            # 5. Ders cevaplarını oku - HER BÖLGE İÇİN AYRI İŞLEM
            print("📝 Cevaplar okunuyor...")
            
            tum_cevaplar = {}
            bolum_cevaplari = {}
            soru_sayaci = 1
            
            ders_isimleri = ['turkce', 'matematik', 'fen', 'sosyal']
            ders_etiketleri = ['Türkçe', 'Matematik', 'Fen', 'Sosyal']
            
            for ders, etiket in zip(ders_isimleri, ders_etiketleri):
                if ders in bolgeler and bolgeler[ders] is not None:
                    # Renkli bölge üzerinden cevapları oku
                    ders_cevaplari = self.cevaplari_oku_renkli(bolgeler[ders], 40, ders)
                    bolum_cevaplari[ders] = ders_cevaplari
                    
                    # Genel cevap listesine ekle
                    for q, ans in ders_cevaplari.items():
                        tum_cevaplar[soru_sayaci] = ans
                        soru_sayaci += 1
                    
                    bos_sayisi = sum(1 for v in ders_cevaplari.values() if v == 'BOŞ')
                    print(f"   {etiket}: {40 - bos_sayisi}/40 işaretli")
                else:
                    print(f"   ⚠️  {etiket} bölgesi bulunamadı")
            
            print(f"✅ Toplam {len(tum_cevaplar)} soru okundu")
            
            # ✨ Terminale cevapları yazdır
            print("\n" + "="*60)
            print("📋 OKUNAN CEVAPLAR")
            print("="*60)
            print(f"👤 Öğrenci: {ad} {soyad}\n")
            
            for ders, etiket in zip(ders_isimleri, ders_etiketleri):
                if ders in bolum_cevaplari:
                    print(f"\n📚 {etiket.upper()} (40 Soru)")
                    print("-" * 60)
                    cevaplar_listesi = []
                    for soru_no in range(1, 41):
                        cevap = bolum_cevaplari[ders].get(soru_no, 'BOŞ')
                        cevaplar_listesi.append(f"{soru_no:2d}:{cevap:3s}")
                        # Her 10 soruda bir satır sonu
                        if soru_no % 10 == 0:
                            print("  " + "  ".join(cevaplar_listesi))
                            cevaplar_listesi = []
                    # Kalan cevaplar varsa yazdır
                    if cevaplar_listesi:
                        print("  " + "  ".join(cevaplar_listesi))
                    
                    # İstatistik
                    isaretli = sum(1 for v in bolum_cevaplari[ders].values() if v != 'BOŞ')
                    print(f"  ✓ İşaretli: {isaretli}/40, Boş: {40-isaretli}/40")
            
            print("\n" + "="*60 + "\n")
            
            return {
                'success': True,
                'student_info': {
                    'name': ad,
                    'surname': soyad,
                    'student_number': ''
                },
                'answers': tum_cevaplar,
                'sections': bolum_cevaplari
            }
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def yonelisini_kontrol_et(self, goruntu: np.ndarray) -> np.ndarray:
        """
        Perspektif düzeltme sonrası kağıdın yöneliş'ini kontrol et.
        Eğer kağıt 90° veya 270° döndürülmüşse, düzelt.
        
        YGS formu: 1600x2264 (genişlik x yükseklik, A4 oranı)
        Eğer ters tutulmuşsa: 2264x1600 olacak → 90° döndür
        """
        h, w = goruntu.shape[:2]
        
        # Beklenen oran: yükseklik > genişlik (portrait mode)
        # Eğer genişlik > yükseklik ise (landscape mode), 90° döndür
        if w > h:
            print(f"⚠️  Kağıt yan çevrilmiş! ({w}x{h}) → Düzeltiliyor...")
            # 90 derece saat yönünde döndür (veya -90 saat yönü tersine)
            goruntu = cv2.rotate(goruntu, cv2.ROTATE_90_COUNTERCLOCKWISE)
            h, w = goruntu.shape[:2]
            print(f"✅ Düzeltildi: {w}x{h}")
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1e_yonelisli.jpg", goruntu)
        
        return goruntu
    
    def perspektif_duzelt(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        """
        A4 kağıdı tespit edip perspektif düzeltme yap
        
        Algoritma:
        1. Beyaz A4 kağıdını tespit et (en büyük beyaz dikdörtgen)
        2. 4 köşesini bul
        3. Perspektif dönüşümü uygula
        """
        h, w = goruntu.shape[:2]
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/0_orijinal.jpg", goruntu)
        
        print("   📍 Beyaz A4 kağıdı aranıyor...")
        
        # Yöntem 1: Beyaz kağıt tespiti
        koseler = self.beyaz_kagit_bul(goruntu)
        
        if koseler is not None:
            print("   ✅ A4 kağıt bulundu!")
            return self.perspektif_donustur(goruntu, koseler)
        
        # Yöntem 2: Kenar tespiti ile en büyük dörtgen
        print("   📍 Kenar tespiti deneniyor...")
        koseler = self.kenar_ile_dikdortgen_bul(goruntu)
        
        if koseler is not None:
            print("   ✅ Dikdörtgen bulundu!")
            return self.perspektif_donustur(goruntu, koseler)
        
        # Hiçbiri başarısız olursa
        print("   ⚠️ A4 bulunamadı, orijinal boyutlandırılıyor...")
        return self.yeniden_boyutlandir(goruntu)
    
    def beyaz_kagit_bul(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        """
        Beyaz A4 kağıdını tespit et
        """
        try:
            h, w = goruntu.shape[:2]
            
            # Gri tonlamaya çevir
            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
            
            # Gaussian blur uygula
            blur = cv2.GaussianBlur(gri, (5, 5), 0)
            
            # Beyaz alanları tespit et - yüksek parlaklık
            # Threshold değerini düşük tutarak beyaz kağıdı yakala
            _, beyaz_maske = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
            
            # Alternatif: Adaptif threshold
            adaptif = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
            
            # İki maskeyi birleştir
            kombine = cv2.bitwise_and(beyaz_maske, adaptif)
            
            # Morfolojik işlemler - boşlukları doldur
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
            kombine = cv2.morphologyEx(kombine, cv2.MORPH_CLOSE, kernel, iterations=3)
            kombine = cv2.morphologyEx(kombine, cv2.MORPH_OPEN, kernel, iterations=2)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1a_beyaz_maske.jpg", kombine)
            
            # Konturları bul
            konturlar, _ = cv2.findContours(kombine, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not konturlar:
                return None
            
            # En büyük konturu bul
            en_buyuk = max(konturlar, key=cv2.contourArea)
            alan = cv2.contourArea(en_buyuk)
            
            # Minimum alan kontrolü - görüntünün en az %20'si
            min_alan = h * w * 0.20
            if alan < min_alan:
                print(f"   Alan çok küçük: {alan} < {min_alan}")
                return None
            
            # Konveks hull ile düzelt
            hull = cv2.convexHull(en_buyuk)
            
            # Poligon yaklaşımı - 4 köşe bul
            epsilon = 0.02 * cv2.arcLength(hull, True)
            yaklasik = cv2.approxPolyDP(hull, epsilon, True)
            
            if self.debug_mode:
                debug_img = goruntu.copy()
                cv2.drawContours(debug_img, [yaklasik], -1, (0, 255, 0), 3)
                cv2.imwrite(f"{self.debug_dir}/1b_kontur_beyaz.jpg", debug_img)
            
            if len(yaklasik) == 4:
                return self.koseler_sirala(yaklasik.reshape(4, 2))
            
            # 4 köşe bulunamadıysa minAreaRect kullan
            rect = cv2.minAreaRect(hull)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            
            if self.debug_mode:
                debug_img = goruntu.copy()
                cv2.drawContours(debug_img, [box], -1, (255, 0, 0), 3)
                cv2.imwrite(f"{self.debug_dir}/1c_minrect.jpg", debug_img)
            
            return self.koseler_sirala(box.astype(np.float32))
            
        except Exception as e:
            print(f"   Beyaz kağıt hatası: {e}")
            return None
    
    def kenar_ile_dikdortgen_bul(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        """
        Canny kenar tespiti ile en büyük dikdörtgeni bul
        """
        try:
            h, w = goruntu.shape[:2]
            
            # Gri tonlama
            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gri, (5, 5), 0)
            
            # Canny kenar tespiti - farklı parametrelerle dene
            for low, high in [(20, 60), (30, 100), (50, 150)]:
                kenarlar = cv2.Canny(blur, low, high)
                
                # Kenarları kalınlaştır
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                kenarlar = cv2.dilate(kenarlar, kernel, iterations=2)
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/1d_kenar_{low}_{high}.jpg", kenarlar)
                
                # Konturları bul
                konturlar, _ = cv2.findContours(kenarlar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if not konturlar:
                    continue
                
                # En büyük konturları sırala
                konturlar = sorted(konturlar, key=cv2.contourArea, reverse=True)
                
                for kontur in konturlar[:5]:
                    alan = cv2.contourArea(kontur)
                    
                    # Minimum alan kontrolü
                    if alan < h * w * 0.15:
                        continue
                    
                    # Konveks hull
                    hull = cv2.convexHull(kontur)
                    
                    # Poligon yaklaşımı
                    epsilon = 0.02 * cv2.arcLength(hull, True)
                    yaklasik = cv2.approxPolyDP(hull, epsilon, True)
                    
                    # 4 köşe kontrolü
                    if len(yaklasik) >= 4:
                        # En yakın 4 köşeyi bul
                        if len(yaklasik) == 4:
                            koseler = yaklasik.reshape(4, 2)
                        else:
                            # minAreaRect kullan
                            rect = cv2.minAreaRect(hull)
                            box = cv2.boxPoints(rect)
                            koseler = box
                        
                        # Dikdörtgen oranı kontrolü (A4: ~1.414)
                        sirali = self.koseler_sirala(koseler.astype(np.float32))
                        genislik = np.linalg.norm(sirali[1] - sirali[0])
                        yukseklik = np.linalg.norm(sirali[3] - sirali[0])
                        
                        if yukseklik > 0:
                            oran = max(genislik, yukseklik) / min(genislik, yukseklik)
                            # A4 oranı 1.414, tolerans: 1.2 - 1.8
                            if 1.2 < oran < 1.8:
                                if self.debug_mode:
                                    debug_img = goruntu.copy()
                                    cv2.drawContours(debug_img, [np.int32(sirali)], -1, (0, 255, 0), 3)
                                    cv2.imwrite(f"{self.debug_dir}/1e_dikdortgen.jpg", debug_img)
                                
                                return sirali
            
            return None
            
        except Exception as e:
            print(f"   Kenar tespiti hatası: {e}")
            return None
    
    def perspektif_donustur(self, goruntu: np.ndarray, koseler: np.ndarray) -> np.ndarray:
        """
        Bulunan köşelere göre perspektif dönüşümü yap
        """
        # Hedef boyutlar (A4 oranı yaklaşık) - Daha yüksek çözünürlük
        genislik = 1600  # 800'den artırıldı
        yukseklik = 2264  # 1132'den artırıldı (A4 oranı korundu)
        
        hedef = np.array([
            [0, 0],
            [genislik - 1, 0],
            [genislik - 1, yukseklik - 1],
            [0, yukseklik - 1]
        ], dtype=np.float32)
        
        # Perspektif dönüşüm matrisi
        matris = cv2.getPerspectiveTransform(koseler.astype(np.float32), hedef)
        
        # Dönüşümü uygula - INTER_CUBIC kullanarak daha kaliteli interpolasyon
        duzeltilmis = cv2.warpPerspective(goruntu, matris, (genislik, yukseklik), 
                                          flags=cv2.INTER_CUBIC)
        
        if self.debug_mode:
            # Debug için köşeleri çiz
            debug_img = goruntu.copy()
            for i, kose in enumerate(koseler):
                cv2.circle(debug_img, (int(kose[0]), int(kose[1])), 10, (0, 255, 0), -1)
                cv2.putText(debug_img, str(i), (int(kose[0])+15, int(kose[1])), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imwrite(f"{self.debug_dir}/1c_koseler.jpg", debug_img)
            cv2.imwrite(f"{self.debug_dir}/1d_perspektif_ham.jpg", duzeltilmis)
        
        # ✨ Perspektif düzeltme sonrası hafif iyileştirme uygula
        duzeltilmis = self.perspektif_sonrasi_iyilestir_hafif(duzeltilmis)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1d_perspektif.jpg", duzeltilmis)
        
        return duzeltilmis
    
    def perspektif_sonrasi_iyilestir(self, goruntu: np.ndarray) -> np.ndarray:
        """
        Perspektif düzeltme sonrası görüntü kalitesini artır
        
        Uygulanan iyileştirmeler:
        1. Gürültü azaltma (Non-local Means Denoising)
        2. Keskinleştirme (Unsharp Masking)
        3. Kontrast artırma (CLAHE - Contrast Limited Adaptive Histogram Equalization)
        4. Binarization için optimize edilmiş eşikleme
        """
        # Gri tonlamaya çevir
        if len(goruntu.shape) == 3:
            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
        else:
            gri = goruntu.copy()
        
        # 1. Gürültü azaltma - fastNlMeansDenoising
        # h: filtre gücü (7-10 arası optimal, yüksek değer daha fazla gürültü azaltır)
        denoised = cv2.fastNlMeansDenoising(gri, None, h=7, templateWindowSize=7, searchWindowSize=21)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1e1_denoised.jpg", denoised)
        
        # 2. Keskinleştirme - Unsharp Masking
        # Gaussian blur ile yumuşatılmış versiyonu çıkar
        gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
        # Orijinalden blur çıkararak keskin kenarları vurgula
        sharpened = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1e2_sharpened.jpg", sharpened)
        
        # 3. Kontrast artırma - CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # clipLimit: kontrast limitlemesi (2.0-4.0 arası)
        # tileGridSize: yerel bölge boyutu
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        contrasted = clahe.apply(sharpened)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1e3_contrasted.jpg", contrasted)
        
        # 4. Adaptive Thresholding - Her bölge için optimize edilmiş eşikleme
        # Bu, farklı aydınlatma koşullarında daha iyi sonuç verir
        binary = cv2.adaptiveThreshold(
            contrasted, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            blockSize=11,  # Komşuluk boyutu
            C=2  # Ortalamadan çıkarılacak sabit
        )
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1e4_binary.jpg", binary)
        
        # Morphological işlemler - Küçük gürültüleri temizle
        kernel = np.ones((2, 2), np.uint8)
        # Açma işlemi: önce erozyon sonra genişleme (küçük noktaları temizler)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        # Kapama işlemi: önce genişleme sonra erozyon (küçük delikleri doldurur)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1e5_cleaned.jpg", cleaned)
        
        # Renkli görüntüye geri çevir (diğer fonksiyonlar BGR bekliyor)
        result = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def perspektif_sonrasi_iyilestir_hafif(self, goruntu: np.ndarray) -> np.ndarray:
        """
        Perspektif düzeltme sonrası hafif iyileştirme
        RENKLİ görüntüyü koruyarak iyileştirme yapar (renk tespiti için kritik)
        """
        # ✨ RENKLİ görüntüyü koru - her kanalı ayrı işle
        if len(goruntu.shape) == 3:
            # Her renk kanalını ayrı işle
            canals = cv2.split(goruntu)
            processed_canals = []
            
            for canal in canals:
                # 1. Gürültü azaltma
                denoised = cv2.fastNlMeansDenoising(canal, None, h=7, templateWindowSize=7, searchWindowSize=21)
                
                # 2. Hafif keskinleştirme
                gaussian = cv2.GaussianBlur(denoised, (0, 0), 1.5)
                sharpened = cv2.addWeighted(denoised, 1.3, gaussian, -0.3, 0)
                
                processed_canals.append(sharpened)
            
            # Kanalları birleştir
            result = cv2.merge(processed_canals)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1e_renkli_iyilestirilmis.jpg", result)
        else:
            # Gri tonlama için eski yöntem
            denoised = cv2.fastNlMeansDenoising(goruntu, None, h=7, templateWindowSize=7, searchWindowSize=21)
            gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
            sharpened = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)
            result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def yeniden_boyutlandir(self, goruntu: np.ndarray) -> np.ndarray:
        """
        Perspektif bulunamazsa sadece yeniden boyutlandır
        """
        genislik = 1600  # 800'den artırıldı
        yukseklik = 2264  # 1132'den artırıldı
        resized = cv2.resize(goruntu, (genislik, yukseklik), interpolation=cv2.INTER_CUBIC)
        # Hafif iyileştirme uygula
        return self.perspektif_sonrasi_iyilestir_hafif(resized)
    
    def koseler_sirala(self, noktalar: np.ndarray) -> np.ndarray:
        """
        4 köşe noktasını sırala: sol-üst, sağ-üst, sağ-alt, sol-alt
        
        ÖNEMLİ: Kağıt her zaman dikey (portrait) modda olmalı!
        Yani yükseklik > genişlik olmalı.
        
        Basit ve güvenilir algoritma:
        1. Y koordinatına göre üst 2 ve alt 2 noktayı ayır
        2. X koordinatına göre sol ve sağ noktaları belirle
        3. Portrait/Landscape kontrolü yap
        """
        noktalar = noktalar.astype(np.float32)
        
        # Y koordinatına göre sırala (küçükten büyüğe = üstten alta)
        y_sirali = noktalar[np.argsort(noktalar[:, 1])]
        
        # Üst 2 nokta (Y değeri küçük olanlar)
        ust_noktalar = y_sirali[:2]
        # Alt 2 nokta (Y değeri büyük olanlar)
        alt_noktalar = y_sirali[2:]
        
        # Üst noktaları X'e göre sırala (sol, sağ)
        ust_noktalar = ust_noktalar[np.argsort(ust_noktalar[:, 0])]
        # Alt noktaları X'e göre sırala (sol, sağ)
        alt_noktalar = alt_noktalar[np.argsort(alt_noktalar[:, 0])]
        
        # Sıralama: sol-üst, sağ-üst, sağ-alt, sol-alt
        sol_ust = ust_noktalar[0]
        sag_ust = ust_noktalar[1]
        sol_alt = alt_noktalar[0]
        sag_alt = alt_noktalar[1]
        
        # Genişlik ve yükseklik hesapla
        genislik = np.linalg.norm(sag_ust - sol_ust)
        yukseklik = np.linalg.norm(sol_alt - sol_ust)
        
        sirali = np.zeros((4, 2), dtype=np.float32)
        
        # A4 kağıt dikey (portrait) olmalı: yükseklik > genişlik
        if genislik > yukseklik:
            # Kağıt yatay (landscape) - 90 derece döndürülmeli
            # Köşeleri saat yönünde 90 derece döndür
            # Eski sağ-üst -> yeni sol-üst
            # Eski sağ-alt -> yeni sağ-üst
            # Eski sol-alt -> yeni sağ-alt
            # Eski sol-üst -> yeni sol-alt
            sirali[0] = sag_ust   # Yeni sol-üst
            sirali[1] = sag_alt   # Yeni sağ-üst
            sirali[2] = sol_alt   # Yeni sağ-alt
            sirali[3] = sol_ust   # Yeni sol-alt
        else:
            # Kağıt zaten dikey (portrait) - doğru sırada
            sirali[0] = sol_ust
            sirali[1] = sag_ust
            sirali[2] = sag_alt
            sirali[3] = sol_alt
        
        return sirali
    
    def on_isleme(self, goruntu: np.ndarray) -> np.ndarray:
        """
        Canny edge detection bazlı ön işleme
        Sadece kenarlar ve koyu alanlar görünür
        """
        # Gri tonlama
        gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/2a_gri.jpg", gri)
        
        # Hafif blur
        blur = cv2.GaussianBlur(gri, (3, 3), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blur, 50, 150)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/2b_canny.jpg", edges)
        
        # Kenarları biraz kalınlaştır
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Koyu alanları da ekle (işaretli baloncuklar)
        _, dark = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY_INV)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/2c_dark.jpg", dark)
        
        # Birleştir
        binary = cv2.bitwise_or(edges, dark)
        
        # Küçük gürültüleri temizle
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/2d_binary_final.jpg", binary)
        
        return binary
    
    def ad_soyad_kutularini_bul(self, img: np.ndarray) -> List[Dict]:
        """
        Form üzerindeki ad ve soyad kutularını otomatik tespit et
        Sol tarafta, üstte AD altta SOYAD olmak üzere 2 eş boyutlu kutu bulur
        
        Returns:
            2 kutu: [Ad, Soyad] sırasıyla (Y'ye göre üstten alta)
        """
        h, w = img.shape[:2]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 15, 5)
        
        # Kontur bul
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Ad/Soyad kutusu kriterleri:
        # 1. Sol tarafta (x < w * 0.35)
        # 2. Dikey dikdörtgen (aspect < 0.60)
        # 3. Yükseklik > %35
        # 4. Genişlik %10-25 arası
        
        min_box_width = w * 0.10
        max_box_width = w * 0.25
        min_box_height = h * 0.35
        
        candidates = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 3000:
                continue
            
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = bw / bh if bh > 0 else 999
            
            # Filtreler
            if x > w * 0.35:  # Sağ tarafı atla (Cevap kutuları)
                continue
            if aspect > 0.60:  # Çok geniş
                continue
            if bh < min_box_height:  # Çok kısa
                continue
            if bw < min_box_width or bw > max_box_width:
                continue
            
            candidates.append({
                'x': x, 'y': y, 'w': bw, 'h': bh, 'area': area
            })
        
        print(f"      Ad/Soyad kutu adayı sayısı: {len(candidates)}")
        
        # Duplicate'ları kaldır (benzer koordinatlı)
        unique_boxes = []
        for box in candidates:
            is_duplicate = False
            for existing in unique_boxes:
                # Y koordinatı çok yakınsa duplicate
                y_overlap = (box['y'] < existing['y'] + existing['h'] and 
                            box['y'] + box['h'] > existing['y'])
                
                if y_overlap and abs(box['x'] - existing['x']) < 30:
                    # Daha büyük olanı tut
                    if box['area'] > existing['area']:
                        unique_boxes.remove(existing)
                        unique_boxes.append(box)
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_boxes.append(box)
        
        print(f"      Eşsiz Ad/Soyad kutu sayısı: {len(unique_boxes)}")
        
        # ✨ YENİ: Boyut ve X koordinatı benzerliğine göre çiftleri bul
        # Ad ve Soyad kutuları benzer genişlik/yüksekliğe sahip olmalı ve X koordinatları yakın olmalı
        filtered_boxes = []
        
        for i, box1 in enumerate(unique_boxes):
            for box2 in unique_boxes[i+1:]:
                # X koordinatları benzer mi? (±30px)
                x_farki = abs(box1['x'] - box2['x'])
                if x_farki > 30:
                    continue
                
                # Boyutlar benzer mi? (genişlik ±%20, yükseklik ±%20)
                w_oran = min(box1['w'], box2['w']) / max(box1['w'], box2['w'])
                h_oran = min(box1['h'], box2['h']) / max(box1['h'], box2['h'])
                
                if w_oran < 0.80 or h_oran < 0.80:
                    continue
                
                # Y farkı yeterli mi? (alt alta olmalı, en az %10 form yüksekliği)
                y_farki = abs(box1['y'] - box2['y'])
                if y_farki < h * 0.10:
                    continue
                
                # Üsttekini Ad, alttakini Soyad olarak al
                if box1['y'] < box2['y']:
                    filtered_boxes = [box1, box2]
                else:
                    filtered_boxes = [box2, box1]
                
                print(f"      ✅ Ad/Soyad çifti bulundu: X farkı={x_farki}px, Y farkı={y_farki}px, W oranı={w_oran:.2f}, H oranı={h_oran:.2f}")
                break
            
            if filtered_boxes:
                break
        
        print(f"      Filtrelenmiş Ad/Soyad kutu sayısı: {len(filtered_boxes)}")
        for i, box in enumerate(filtered_boxes[:2]):
            print(f"        Kutu {i+1} ({'Ad' if i==0 else 'Soyad'}): x={box['x']}, y={box['y']}, w={box['w']}, h={box['h']}")
        
        if self.debug_mode and len(filtered_boxes) >= 2:
            debug_img = img.copy()
            labels = ['AD', 'SOYAD']
            colors = [(0,255,0), (255,0,0)]
            for i, box in enumerate(filtered_boxes[:2]):
                cv2.rectangle(debug_img, (box['x'], box['y']), 
                             (box['x']+box['w'], box['y']+box['h']), colors[i], 2)
                cv2.putText(debug_img, labels[i], (box['x'], box['y']-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors[i], 2)
            cv2.imwrite(f"{self.debug_dir}/auto_ad_soyad_boxes.jpg", debug_img)
        
        return filtered_boxes[:2] if len(filtered_boxes) >= 2 else []
    
    def cevap_kutularini_bul(self, img: np.ndarray) -> List[Dict]:
        """
        Form üzerindeki 4 cevap kutusunu otomatik tespit et
        Sabit koordinat yerine görüntü işleme ile bulur
        
        Returns:
            4 kutu: [Türkçe, Matematik, Fen, Sosyal] sırasıyla (X'e göre)
        """
        h, w = img.shape[:2]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 15, 5)
        
        # Kontur bul
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Cevap kutusu kriterleri:
        # 1. Sağ tarafta (x > w * 0.25) - Ad/Soyad solda
        # 2. Dikey dikdörtgen (aspect < 0.30)
        # 3. Yükseklik > %40
        # 4. Genişlik esnek (minimum %6, maksimum %22)
        
        min_box_width = w * 0.06  # Daha dar kutuları da kabul et
        max_box_width = w * 0.22  # Daha geniş kutuları da kabul et
        min_box_height = h * 0.40  # Biraz daha kısa kutuları da kabul et
        
        candidates = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 3000:
                continue
            
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = bw / bh if bh > 0 else 999
            
            # Filtreler
            if x < w * 0.25:  # Sol tarafı atla (Ad/Soyad)
                continue
            if aspect > 0.30:  # Çok geniş, cevap kutusu değil
                continue
            if bh < min_box_height:  # Çok kısa
                continue
            if bw < min_box_width or bw > max_box_width:
                continue
            
            candidates.append({
                'x': x, 'y': y, 'w': bw, 'h': bh, 'area': area
            })
        
        print(f"      Kutu adayı sayısı: {len(candidates)}")
        for i, box in enumerate(candidates):
            print(f"        Aday {i+1}: x={box['x']}, y={box['y']}, w={box['w']}, h={box['h']}")
        
        # Duplicate'ları kaldır (benzer koordinatlı - X ekseninde çakışma kontrolü)
        unique_boxes = []
        for box in candidates:
            is_duplicate = False
            for existing in unique_boxes:
                # X koordinatı çok yakınsa duplicate (kutular yan yana değil)
                x_overlap = (box['x'] < existing['x'] + existing['w'] and 
                            box['x'] + box['w'] > existing['x'])
                
                if x_overlap and abs(box['y'] - existing['y']) < 30:
                    # Daha büyük olanı tut
                    if box['area'] > existing['area']:
                        unique_boxes.remove(existing)
                        unique_boxes.append(box)
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_boxes.append(box)
        
        print(f"      Eşsiz kutu sayısı: {len(unique_boxes)}")
        
        # X'e göre sırala (soldan sağa: Türkçe, Matematik, Sosyal, Fen)
        unique_boxes.sort(key=lambda b: b['x'])
        
        # ✨ YENİ: Kutular arasında minimum mesafe kontrolü (birbirine çok yakın kutuları ele)
        min_distance = w * 0.12  # Minimum %12 mesafe (yaklaşık 192px @ 1600px)
        filtered_boxes = []
        
        for box in unique_boxes:
            # Bu kutu, zaten seçilmiş kutulardan çok uzakta mı?
            too_close = False
            for selected in filtered_boxes:
                distance = abs(box['x'] - selected['x'])
                if distance < min_distance:
                    too_close = True
                    print(f"        ⚠️ x={box['x']} kutusu atlandı (x={selected['x']}'e çok yakın, mesafe={distance:.0f})")
                    break
            
            if not too_close:
                filtered_boxes.append(box)
        
        print(f"      Filtrelenmiş kutu sayısı: {len(filtered_boxes)}")
        for i, box in enumerate(filtered_boxes[:4]):
            print(f"        Kutu {i+1}: x={box['x']}, w={box['w']}")
        
        if self.debug_mode and len(filtered_boxes) >= 4:
            debug_img = img.copy()
            # Sıralama: Türkçe, Matematik, Sosyal, Fen (fen ve sosyal yer değişti)
            ders_isimleri = ['Turkce', 'Mat', 'Sosyal', 'Fen']
            colors = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)]
            for i, box in enumerate(filtered_boxes[:4]):
                cv2.rectangle(debug_img, (box['x'], box['y']), 
                             (box['x']+box['w'], box['y']+box['h']), colors[i], 2)
                cv2.putText(debug_img, ders_isimleri[i], (box['x'], box['y']-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 2)
            cv2.imwrite(f"{self.debug_dir}/auto_boxes.jpg", debug_img)
        
        return filtered_boxes[:4] if len(filtered_boxes) >= 4 else []
    
    def bolgeleri_cikar_renkli(self, renkli: np.ndarray) -> Dict:
        """
        Form bölgelerini otomatik tespit ile çıkar
        Önce ad/soyad ve cevap kutularını bul, bulamazsa sabit koordinat kullan
        """
        h, w = renkli.shape[:2]
        bolgeler = {}
        
        # Ad/Soyad kutularını tespit et
        ad_soyad_kutular = self.ad_soyad_kutularini_bul(renkli)
        
        if len(ad_soyad_kutular) == 2:
            print("   ✅ Ad/Soyad kutuları otomatik tespit edildi")
            ad_soyad_isimleri = ['ad', 'soyad']
            
            for i, kutu in enumerate(ad_soyad_kutular):
                bolge_adi = ad_soyad_isimleri[i]
                x, y, bw, bh = kutu['x'], kutu['y'], kutu['w'], kutu['h']
                
                # ✨ Ad/Soyad için de üstten %3 kırp (başlık ve hizalama düzeltmesi)
                kirpma = int(bh * 0.065)
                y += kirpma
                bh -= kirpma
                
                bolgeler[bolge_adi] = renkli[y:y+bh, x:x+bw].copy()
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/bolge_{bolge_adi}.jpg", bolgeler[bolge_adi])
        else:
            print(f"   ⚠️ Ad/Soyad otomatik tespit başarısız ({len(ad_soyad_kutular)} kutu), sabit koordinat kullanılıyor")
            # Ad/Soyad için sabit koordinat kullan
            ad_soyad_oranlari = {
                'ad': {'x1': 0.080, 'y1': 0.092, 'x2': 0.28, 'y2': 0.500},
                'soyad': {'x1': 0.080, 'y1': 0.530, 'x2': 0.28, 'y2': 0.94}
            }
            
            for bolge_adi, oranlar in ad_soyad_oranlari.items():
                x1 = int(w * oranlar['x1'])
                y1 = int(h * oranlar['y1'])
                x2 = int(w * oranlar['x2'])
                y2 = int(h * oranlar['y2'])
                
                # ✨ Sabit koordinatlarda da üstten %3 kırp
                bh = y2 - y1
                kirpma = int(bh * 0.05)
                y1 += kirpma
                y2 = y1 + (bh - kirpma)
                
                bolgeler[bolge_adi] = renkli[y1:y2, x1:x2].copy()
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/bolge_{bolge_adi}.jpg", bolgeler[bolge_adi])
        
        # Cevap kutularını tespit et
        kutular = self.cevap_kutularini_bul(renkli)
        
        if len(kutular) == 4:
            print("   ✅ 4 cevap kutusu otomatik tespit edildi")
            # Sıralama: Türkçe, Matematik, Sosyal, Fen (fen ve sosyal yer değişti)
            ders_isimleri = ['turkce', 'matematik', 'fen', 'sosyal']
            
            for i, kutu in enumerate(kutular):
                ders = ders_isimleri[i]
                x, y, bw, bh = kutu['x'], kutu['y'], kutu['w'], kutu['h']
                
                # ✨ Tüm dersler için üstten %2 kırp (başlık harflerini kaldır)
                kirpma = int(bh * 0.02)
                y += kirpma
                bh -= kirpma
                
                bolgeler[ders] = renkli[y:y+bh, x:x+bw].copy()
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/bolge_{ders}.jpg", bolgeler[ders])
        
        else:
            # Otomatik tespit başarısız, sabit koordinat kullan
            print(f"   ⚠️ Otomatik tespit başarısız ({len(kutular)} kutu), sabit koordinat kullanılıyor")
            
            if self.debug_mode:
                debug_all = renkli.copy()
            
            for bolge_adi, oranlar in self.bolge_oranlari.items():
                x1 = int(w * oranlar['x1'])
                y1 = int(h * oranlar['y1'])
                x2 = int(w * oranlar['x2'])
                y2 = int(h * oranlar['y2'])
                
                bolge_renkli = renkli[y1:y2, x1:x2].copy()
                bolgeler[bolge_adi] = bolge_renkli
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/bolge_{bolge_adi}.jpg", bolge_renkli)
                    renk = (0, 255, 0)
                    cv2.rectangle(debug_all, (x1, y1), (x2, y2), renk, 2)
                    cv2.putText(debug_all, bolge_adi.upper(), (x1 + 5, y1 + 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, renk, 1)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/3_tum_bolgeler.jpg", debug_all)
        
        return bolgeler
    
    def cevaplari_oku_renkli(self, bolge_renkli: np.ndarray, soru_sayisi: int = 40, ders_adi: str = "") -> Dict[int, str]:
        """
        Yuvarlak tespiti ile cevap okuma:
        1. HoughCircles ile tüm daireleri tespit et
        2. Her dairenin içindeki ortalama parlaklığı hesapla
        3. Daireleri satırlara grupla (Y koordinatına göre)
        4. Her satırda X koordinatına göre sırala (A, B, C, D, E)
        5. En koyu daire = işaretli cevap
        """
        cevaplar = {}
        
        if bolge_renkli is None or bolge_renkli.size == 0:
            return {i: 'BOŞ' for i in range(1, soru_sayisi + 1)}
        
        h, w = bolge_renkli.shape[:2]
        
        # Gri tonlama
        gri = cv2.cvtColor(bolge_renkli, cv2.COLOR_BGR2GRAY)
        
        # Debug görüntüsü
        if self.debug_mode:
            debug_img = bolge_renkli.copy()
        
        # Blur
        blurred = cv2.GaussianBlur(gri, (5, 5), 0)
        
        # Satır ve daire boyutu
        satir_yuksekligi = h / soru_sayisi
        beklenen_yaricap = int(satir_yuksekligi / 2.5)
        
        # HoughCircles - sıkı yarıçap kontrolü ile (küçük harflerin iç dairelerini engelle)
        min_r = max(8, int(beklenen_yaricap * 0.7))  # En az 8px veya %70 (3'ten artırıldı)
        max_r = int(beklenen_yaricap * 1.3)  # En fazla %130
        
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=int(beklenen_yaricap * 0.8),
            param1=50,
            param2=20,
            minRadius=min_r,
            maxRadius=max_r
        )
        
        if circles is None:
            print(f"      {ders_adi}: HoughCircles bulamadı!")
            return {i: 'BOŞ' for i in range(1, soru_sayisi + 1)}
        
        detected = circles[0]
        print(f"      {ders_adi}: {len(detected)} daire tespit edildi (r:{min_r}-{max_r}px)")
        
        # Her daire için parlaklık hesapla ve satıra ata
        daire_bilgileri = []
        yaricap_listesi = []
        
        for circle in detected:
            cx, cy, r = float(circle[0]), float(circle[1]), float(circle[2])
            
            # ✨ YENİ: Çok küçük daireleri hemen ele (ç, ö, ü gibi harflerin iç kısımları)
            if r < min_r:
                continue
            
            yaricap_listesi.append(r)
            
            # ROI
            x1, y1 = max(0, int(cx - r)), max(0, int(cy - r))
            x2, y2 = min(w, int(cx + r)), min(h, int(cy + r))
            roi = gri[y1:y2, x1:x2]
            
            if roi.size == 0:
                continue
            
            # Dairesel maske ile ortalama parlaklık
            mask = np.zeros(roi.shape, dtype=np.uint8)
            mcx, mcy = roi.shape[1] // 2, roi.shape[0] // 2
            mr = min(mcx, mcy)
            if mr < 2:
                continue
            cv2.circle(mask, (mcx, mcy), mr, 255, -1)
            
            pixels = roi[mask == 255]
            if len(pixels) == 0:
                continue
            
            avg = float(np.mean(pixels))
            
            # Satır numarası
            satir_no = int(cy / satir_yuksekligi) + 1
            satir_no = max(1, min(soru_sayisi, satir_no))
            
            daire_bilgileri.append({
                'cx': cx, 'cy': cy, 'r': r,
                'avg': avg, 'satir': satir_no
            })
        
        # ✨ YENİ: Anormal büyük daireleri filtrele (outlier detection)
        if len(yaricap_listesi) > 10:
            yaricap_median = float(np.median(yaricap_listesi))
            yaricap_std = float(np.std(yaricap_listesi))
            # 2 standart sapmadan fazla büyük olanları ele
            max_kabul_edilebilir = yaricap_median + (2 * yaricap_std)
            
            onceki_sayi = len(daire_bilgileri)
            daire_bilgileri = [d for d in daire_bilgileri if d['r'] <= max_kabul_edilebilir]
            
            if len(daire_bilgileri) < onceki_sayi:
                print(f"      {ders_adi}: {onceki_sayi - len(daire_bilgileri)} büyük daire filtrelendi (r>{max_kabul_edilebilir:.1f})")
        
        # Debug çizimi
        if self.debug_mode:
            for d in daire_bilgileri:
                renk = (0, 255, 0) if d['avg'] < 150 else (0, 0, 255)
                cv2.circle(debug_img, (int(d['cx']), int(d['cy'])), int(d['r']), renk, 1)
        
        # Satırlara grupla
        satirlar = {}
        for d in daire_bilgileri:
            s = d['satir']
            if s not in satirlar:
                satirlar[s] = []
            satirlar[s].append(d)
        
        # Her satırı işle
        for satir_no in range(1, soru_sayisi + 1):
            if satir_no not in satirlar or len(satirlar[satir_no]) == 0:
                cevaplar[satir_no] = 'BOŞ'
                continue
            
            daireler = satirlar[satir_no]
            
            # X'e göre sırala (A, B, C, D, E)
            daireler.sort(key=lambda d: d['cx'])
            
            # İlk 5 seçeneği al
            secenekler = daireler[:5]
            
            if len(secenekler) == 0:
                cevaplar[satir_no] = 'BOŞ'
                continue
            
            # En koyu olanı bul
            en_koyu = min(secenekler, key=lambda d: d['avg'])
            en_koyu_idx = secenekler.index(en_koyu)
            
            # Diğerlerinin ortalaması
            diger_avg = [d['avg'] for d in secenekler if d != en_koyu]
            diger_ortalama = sum(diger_avg) / len(diger_avg) if diger_avg else 255
            
            # ✨ YENİ: Daha esnek doluluk kontrolü (%70 doluluk = avg ~150)
            # Karar: En koyu < 150 VE diğerlerinden 20 daha koyu
            if en_koyu['avg'] < 150 and (diger_ortalama - en_koyu['avg']) > 20:
                cevaplar[satir_no] = self.secenekler[en_koyu_idx]
                if self.debug_mode:
                    cv2.circle(debug_img, (int(en_koyu['cx']), int(en_koyu['cy'])), 
                              int(en_koyu['r']) + 2, (0, 255, 0), 3)
            else:
                cevaplar[satir_no] = 'BOŞ'
        
        # Debug kaydet
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/circles_{ders_adi}.jpg", debug_img)
            ilk_10 = {k: v for k, v in list(cevaplar.items())[:10]}
            print(f"      {ders_adi} ilk 10: {ilk_10}")
        
        isaretli = sum(1 for v in cevaplar.values() if v != 'BOŞ')
        print(f"      {ders_adi}: {isaretli}/{soru_sayisi} işaretli")
        
        return cevaplar
    
    def daire_doluluk_hesapla(self, roi: np.ndarray, yaricap: int) -> float:
        """
        Daire içindeki doluluk oranını hesapla
        Basit ve etkili: ortalama parlaklık kontrolü
        """
        if roi.size == 0:
            return 0.0
        
        h, w = roi.shape[:2]
        
        # Daire maskesi oluştur
        maske = np.zeros((h, w), dtype=np.uint8)
        merkez_x = w // 2
        merkez_y = h // 2
        r = min(yaricap, min(w, h) // 2 - 1)
        r = max(r, 2)
        
        cv2.circle(maske, (merkez_x, merkez_y), r, 255, -1)
        
        # Daire içindeki pikselleri al
        daire_pikseller = roi[maske == 255]
        
        if daire_pikseller.size == 0:
            return 0.0
        
        # Ortalama parlaklık
        ortalama = np.mean(daire_pikseller)
        
        # Dolu baloncuk: avg < 120 (çok koyu)
        # Boş baloncuk: avg > 150 (açık)
        # 
        # Doluluk skoru: düşük ortalama = yüksek doluluk
        # 0 (avg=200) -> 1.0 (avg=50)
        
        if ortalama < 80:
            doluluk = 1.0
        elif ortalama > 170:
            doluluk = 0.0
        else:
            # 80-170 arasında lineer interpolasyon
            doluluk = (170 - ortalama) / 90.0
        
        return doluluk
    
    def hucre_doluluk_hesapla(self, hucre_gri: np.ndarray, yuvarlak: bool = True) -> float:
        """
        Tek bir hücre için doluluk oranı hesapla
        Yuvarlak maske kullanarak baloncuk içini kontrol et
        
        Dolu baloncuk: avg 60-100 (koyu)
        Boş baloncuk: avg 170-185 (açık)
        """
        if hucre_gri.size == 0:
            return 0.0
        
        h, w = hucre_gri.shape[:2]
        
        if yuvarlak and h > 5 and w > 5:
            # Yuvarlak maske oluştur - baloncuk şeklinde
            maske = np.zeros((h, w), dtype=np.uint8)
            merkez_x = w // 2
            merkez_y = h // 2
            yaricap = min(w, h) // 2 - 1  # Biraz küçük tut
            yaricap = max(yaricap, 2)  # Minimum 2 piksel
            
            cv2.circle(maske, (merkez_x, merkez_y), yaricap, 255, -1)
            
            # Sadece daire içindeki pikselleri al
            daire_pikseller = hucre_gri[maske == 255]
            
            if daire_pikseller.size == 0:
                return 0.0
            
            # Ortalama parlaklık
            ortalama = np.mean(daire_pikseller)
        else:
            # Küçük hücreler için dikdörtgen kullan
            ortalama = np.mean(hucre_gri)
        
        # Sabit eşiklerle doluluk hesapla
        # Analiz sonuçları: dolu avg=60-100, boş avg=170-185
        if ortalama < 100:
            # Çok koyu - tam dolu
            doluluk = 1.0
        elif ortalama > 160:
            # Çok açık - boş
            doluluk = 0.0
        else:
            # Arası - oranla (160'dan 100'e doğru doluluk artar)
            doluluk = (160 - ortalama) / 60.0
        
        return doluluk
    
    def isim_oku_renkli(self, bolge_renkli: np.ndarray, max_karakter: int = 12, bolge_adi: str = "isim") -> str:
        """
        Renkli bölgeden isim oku - HoughCircles yöntemi ile (derslerdeki gibi)
        Yan yana sütunlar, her sütun bir harf pozisyonu
        Her sütunda yukarıdan aşağıya alfabetik harfler
        """
        if bolge_renkli is None or bolge_renkli.size == 0:
            return ""
        
        h, w = bolge_renkli.shape[:2]
        
        # Gri tonlama
        gri = cv2.cvtColor(bolge_renkli, cv2.COLOR_BGR2GRAY)
        
        # Debug görüntüsü
        if self.debug_mode:
            debug_img = bolge_renkli.copy()
        
        # Blur
        blurred = cv2.GaussianBlur(gri, (5, 5), 0)
        
        # Her sütun bir karakter, her satır bir harf
        sutun_genisligi = w / max_karakter
        satir_sayisi = len(self.alfabe)  # 29 harf (Türk alfabesi)
        satir_yuksekligi = h / satir_sayisi
        beklenen_yaricap = int(min(satir_yuksekligi, sutun_genisligi) / 2.5)
        
        # HoughCircles
        min_r = max(5, int(beklenen_yaricap * 0.6))
        max_r = int(beklenen_yaricap * 1.4)
        
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=int(beklenen_yaricap * 0.8),
            param1=50,
            param2=20,
            minRadius=min_r,
            maxRadius=max_r
        )
        
        if circles is None:
            print(f"      İsim: HoughCircles bulamadı!")
            return ""
        
        detected = circles[0]
        print(f"      İsim: {len(detected)} daire tespit edildi (r:{min_r}-{max_r}px)")
        
        # Her daire için parlaklık hesapla ve sütuna ata
        daire_bilgileri = []
        
        for circle in detected:
            cx, cy, r = float(circle[0]), float(circle[1]), float(circle[2])
            
            if r < min_r:
                continue
            
            # ROI
            x1, y1 = max(0, int(cx - r)), max(0, int(cy - r))
            x2, y2 = min(w, int(cx + r)), min(h, int(cy + r))
            roi = gri[y1:y2, x1:x2]
            
            if roi.size == 0:
                continue
            
            # Dairesel maske ile ortalama parlaklık
            mask = np.zeros(roi.shape, dtype=np.uint8)
            mcx, mcy = roi.shape[1] // 2, roi.shape[0] // 2
            mr = min(mcx, mcy)
            if mr < 2:
                continue
            cv2.circle(mask, (mcx, mcy), mr, 255, -1)
            
            pixels = roi[mask == 255]
            if len(pixels) == 0:
                continue
            
            avg = float(np.mean(pixels))
            
            # Sütun ve satır numarası
            sutun_no = int(cx / sutun_genisligi)
            satir_no = int(cy / satir_yuksekligi)
            
            # Sınır kontrolü
            if sutun_no < 0 or sutun_no >= max_karakter:
                continue
            if satir_no < 0 or satir_no >= satir_sayisi:
                continue
            
            daire_bilgileri.append({
                'cx': cx, 'cy': cy, 'r': r,
                'avg': avg, 'sutun': sutun_no, 'satir': satir_no
            })
        
        # Debug çizimi
        # ✨ GÜNCELLEME: Yeni katı eşikle tutarlı (120 yerine 150)
        if self.debug_mode:
            for d in daire_bilgileri:
                renk = (0, 255, 0) if d['avg'] < 120 else (0, 0, 255)
                cv2.circle(debug_img, (int(d['cx']), int(d['cy'])), int(d['r']), renk, 1)
        
        # Sütunlara grupla
        sutunlar = {}
        for d in daire_bilgileri:
            s = d['sutun']
            if s not in sutunlar:
                sutunlar[s] = []
            sutunlar[s].append(d)
        
        # Her sütunu işle
        isim = []
        for sutun_no in range(max_karakter):
            if sutun_no not in sutunlar or len(sutunlar[sutun_no]) == 0:
                continue
            
            daireler = sutunlar[sutun_no]
            
            # En koyu olanı bul
            en_koyu = min(daireler, key=lambda d: d['avg'])
            
            # Diğerlerinin ortalaması
            diger = [d['avg'] for d in daireler if d != en_koyu]
            diger_ortalama = sum(diger) / len(diger) if diger else 255
            
            # ✨ DAHA KATI: En koyu < 120 (çok daha koyu olmalı) VE diğerlerinden 35+ daha koyu
            # Ad/Soyad için daha kesin doluluk kontrolü gerekli
            if en_koyu['avg'] < 120 and (diger_ortalama - en_koyu['avg']) > 35:
                harf_idx = en_koyu['satir']
                if 0 <= harf_idx < len(self.alfabe):
                    isim.append((sutun_no, self.alfabe[harf_idx]))
                    
                    if self.debug_mode:
                        cv2.circle(debug_img, (int(en_koyu['cx']), int(en_koyu['cy'])), 
                                  int(en_koyu['r']) + 2, (0, 255, 0), 3)
        
        # Sütun sırasına göre sırala
        isim.sort(key=lambda x: x[0])
        isim_str = ''.join([h for _, h in isim])
        
        # Debug kaydet
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/{bolge_adi}_circles.jpg", debug_img)
            print(f"      {bolge_adi.capitalize()} tespit: {isim_str}")
        
        return isim_str
    
    def bolgeleri_cikar(self, renkli: np.ndarray, binary: np.ndarray) -> Dict:
        """
        Form bölgelerini çıkar
        """
        h, w = renkli.shape[:2]
        bolgeler = {}
        
        # Debug için tüm bölgeleri tek bir görüntüde göster
        if self.debug_mode:
            debug_all = renkli.copy()
        
        for bolge_adi, oranlar in self.bolge_oranlari.items():
            x1 = int(w * oranlar['x1'])
            y1 = int(h * oranlar['y1'])
            x2 = int(w * oranlar['x2'])
            y2 = int(h * oranlar['y2'])
            
            # Renkli bölge
            bolge_renkli = renkli[y1:y2, x1:x2].copy()
            bolgeler[bolge_adi] = bolge_renkli
            
            # Her bölge için ayrı binary işleme (daha iyi sonuç)
            bolge_binary = self.bolge_binary_isle(bolge_renkli)
            bolgeler[f'{bolge_adi}_binary'] = bolge_binary
            
            if self.debug_mode:
                # Her bölgeyi ayrı kaydet
                cv2.imwrite(f"{self.debug_dir}/bolge_{bolge_adi}.jpg", bolge_renkli)
                cv2.imwrite(f"{self.debug_dir}/bolge_{bolge_adi}_binary.jpg", bolge_binary)
                
                # Tüm bölgeleri tek görüntüde çiz
                renk = (0, 255, 0)  # Yeşil
                cv2.rectangle(debug_all, (x1, y1), (x2, y2), renk, 2)
                cv2.putText(debug_all, bolge_adi.upper(), (x1 + 5, y1 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, renk, 1)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/3_tum_bolgeler.jpg", debug_all)
        
        return bolgeler
    
    def bolge_binary_isle(self, bolge_renkli: np.ndarray) -> np.ndarray:
        """
        Küçük bölge için optimize edilmiş binary dönüşüm
        Boyuta göre parametreler ayarlanır
        """
        h, w = bolge_renkli.shape[:2]
        
        # Gri tonlama
        gri = cv2.cvtColor(bolge_renkli, cv2.COLOR_BGR2GRAY)
        
        # Küçük bölgeler için blur YAPMA veya çok az yap
        # Büyük görüntüde 3x3 iyi ama küçük bölgede detayları kaybettirir
        if min(h, w) > 200:
            blur = cv2.GaussianBlur(gri, (3, 3), 0)
        else:
            blur = gri  # Blur yapma
        
        # Küçük bölgeler için Canny eşiklerini düşür
        # Büyük görüntüde 50-150 iyi ama küçük bölgede daha hassas olmalı
        if min(h, w) > 200:
            canny_low, canny_high = 50, 150
        else:
            canny_low, canny_high = 30, 100
        
        # Canny edge detection
        edges = cv2.Canny(blur, canny_low, canny_high)
        
        # Küçük bölgelerde dilate YAPMA - detayları bozar
        if min(h, w) > 200:
            kernel_dilate = np.ones((2, 2), np.uint8)
            edges = cv2.dilate(edges, kernel_dilate, iterations=1)
        
        # Koyu alanları bul - eşiği bölge parlaklığına göre ayarla
        ortalama = np.mean(gri)
        esik = int(ortalama - 30)  # Ortalamadan 30 birim daha koyu
        esik = max(80, min(200, esik))  # 80-200 arası sınırla
        
        _, dark_areas = cv2.threshold(blur, esik, 255, cv2.THRESH_BINARY_INV)
        
        # Birleştir
        combined = cv2.bitwise_or(edges, dark_areas)
        
        # Küçük gürültüleri temizle - küçük bölgelerde daha az agresif
        if min(h, w) > 200:
            kernel_clean = np.ones((2, 2), np.uint8)
            combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel_clean, iterations=1)
        
        return combined
    
    def cevaplari_oku(self, binary_bolge: np.ndarray, soru_sayisi: int = 40, ders_adi: str = "") -> Dict[int, str]:
        """
        Bir ders bölgesinden cevapları oku - Gelişmiş algoritma
        
        Args:
            binary_bolge: İşlenmiş binary görüntü
            soru_sayisi: Toplam soru sayısı (varsayılan 40)
            ders_adi: Debug için ders adı
            
        Returns:
            {soru_no: 'A/B/C/D/E/BOŞ', ...}
        """
        cevaplar = {}
        
        if binary_bolge is None or binary_bolge.size == 0:
            return {i: 'BOŞ' for i in range(1, soru_sayisi + 1)}
        
        h, w = binary_bolge.shape[:2]
        
        # Debug görüntüsü
        if self.debug_mode:
            debug_img = cv2.cvtColor(binary_bolge, cv2.COLOR_GRAY2BGR)
        
        # Kontur bazlı baloncuk tespiti
        konturlar, _ = cv2.findContours(binary_bolge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Baloncuk adaylarını filtrele
        baloncuklar = []
        min_alan = (h / soru_sayisi) * (w / 8) * 0.1  # Minimum baloncuk alanı
        max_alan = (h / soru_sayisi) * (w / 5) * 1.5  # Maksimum baloncuk alanı
        
        for kontur in konturlar:
            alan = cv2.contourArea(kontur)
            if min_alan < alan < max_alan:
                x, y, kw, kh = cv2.boundingRect(kontur)
                # Yaklaşık kare/daire şeklinde olmalı (en-boy oranı)
                oran = kw / kh if kh > 0 else 0
                if 0.5 < oran < 2.0:
                    # Merkez noktası
                    cx = x + kw // 2
                    cy = y + kh // 2
                    # Doluluk oranı (kontur içindeki beyaz piksel)
                    mask = np.zeros(binary_bolge.shape, dtype=np.uint8)
                    cv2.drawContours(mask, [kontur], -1, 255, -1)
                    doluluk = cv2.countNonZero(cv2.bitwise_and(binary_bolge, mask)) / alan
                    baloncuklar.append({
                        'x': cx, 'y': cy, 
                        'alan': alan, 
                        'doluluk': doluluk,
                        'bbox': (x, y, kw, kh)
                    })
        
        if self.debug_mode:
            print(f"      {ders_adi}: {len(baloncuklar)} baloncuk adayı bulundu")
        
        # Satır ve sütun bazlı gruplama
        satir_yuksekligi = h / soru_sayisi
        secenek_genislik = w / 6  # Soru no + 5 seçenek
        
        for soru in range(1, soru_sayisi + 1):
            # Bu satırdaki baloncukları bul
            y_min = (soru - 1) * satir_yuksekligi
            y_max = soru * satir_yuksekligi
            
            satir_baloncuklari = [b for b in baloncuklar if y_min <= b['y'] < y_max]
            
            if not satir_baloncuklari:
                cevaplar[soru] = 'BOŞ'
                continue
            
            # X koordinatına göre sırala
            satir_baloncuklari.sort(key=lambda b: b['x'])
            
            # En dolu baloncuğu bul
            en_dolu = max(satir_baloncuklari, key=lambda b: b['doluluk'])
            
            # Hangi seçenek olduğunu belirle (X pozisyonuna göre)
            # İlk %16 soru numarası, kalan %84 seçenekler
            secenek_baslangic = w * 0.16
            secenek_alan = (w - secenek_baslangic) / 5
            
            if en_dolu['x'] < secenek_baslangic:
                # Soru numarası alanında - geçersiz
                cevaplar[soru] = 'BOŞ'
            else:
                secenek_idx = int((en_dolu['x'] - secenek_baslangic) / secenek_alan)
                secenek_idx = max(0, min(4, secenek_idx))  # 0-4 arası sınırla
                
                # Doluluk kontrolü
                if en_dolu['doluluk'] > 0.3:  # %30'dan fazla dolu
                    cevaplar[soru] = self.secenekler[secenek_idx]
                    
                    if self.debug_mode:
                        x, y, kw, kh = en_dolu['bbox']
                        cv2.rectangle(debug_img, (x, y), (x+kw, y+kh), (0, 255, 0), 2)
                else:
                    cevaplar[soru] = 'BOŞ'
        
        # Grid bazlı fallback - kontur bulunamazsa
        bos_sayisi = sum(1 for v in cevaplar.values() if v == 'BOŞ')
        if bos_sayisi > soru_sayisi * 0.7:  # %70'den fazla boşsa grid bazlı dene
            if self.debug_mode:
                print(f"      {ders_adi}: Kontur bazlı başarısız, grid bazlı deneniyor...")
            cevaplar = self.grid_bazli_oku(binary_bolge, soru_sayisi, ders_adi)
        
        if self.debug_mode:
            # İşaretli cevapları görüntüye yaz
            for soru, cevap in list(cevaplar.items())[:10]:
                y = int((soru - 0.5) * satir_yuksekligi)
                cv2.putText(debug_img, f"{soru}:{cevap}", (5, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
            cv2.imwrite(f"{self.debug_dir}/grid_{ders_adi}.jpg", debug_img)
        
        return cevaplar
    
    def grid_bazli_oku(self, binary_bolge: np.ndarray, soru_sayisi: int, ders_adi: str) -> Dict[int, str]:
        """
        Grid bazlı cevap okuma (fallback)
        """
        cevaplar = {}
        h, w = binary_bolge.shape[:2]
        
        satir_yuksekligi = h / soru_sayisi
        secenek_sayisi = 5
        
        # Sol tarafta soru numaraları (%16), sağda seçenekler (%84)
        secenek_baslangic = int(w * 0.16)
        secenek_genislik = (w - secenek_baslangic) / secenek_sayisi
        
        for soru in range(1, soru_sayisi + 1):
            y1 = int((soru - 1) * satir_yuksekligi)
            y2 = int(soru * satir_yuksekligi)
            
            # Satır padding
            py = int(satir_yuksekligi * 0.15)
            y1 += py
            y2 -= py
            
            doluluk_oranlari = []
            
            for secenek_idx in range(secenek_sayisi):
                x1 = secenek_baslangic + int(secenek_idx * secenek_genislik)
                x2 = secenek_baslangic + int((secenek_idx + 1) * secenek_genislik)
                
                # Hücre padding
                px = int(secenek_genislik * 0.15)
                x1 += px
                x2 -= px
                
                hucre = binary_bolge[y1:y2, x1:x2]
                
                if hucre.size > 0:
                    doluluk = np.sum(hucre > 0) / hucre.size
                    doluluk_oranlari.append((self.secenekler[secenek_idx], doluluk))
            
            if doluluk_oranlari:
                doluluk_oranlari.sort(key=lambda x: x[1], reverse=True)
                en_yuksek = doluluk_oranlari[0]
                ikinci = doluluk_oranlari[1] if len(doluluk_oranlari) > 1 else ('', 0)
                
                # Daha düşük eşik değerleri
                if en_yuksek[1] > 0.12 and (en_yuksek[1] - ikinci[1]) > 0.05:
                    cevaplar[soru] = en_yuksek[0]
                else:
                    cevaplar[soru] = 'BOŞ'
            else:
                cevaplar[soru] = 'BOŞ'
        
        return cevaplar
    
    def isim_oku(self, binary_bolge: np.ndarray, max_karakter: int = 12) -> str:
        """
        Ad veya soyad bölgesinden isim oku
        
        Form yapısı: Her sütun bir karakter, her satır bir harf (A-Z)
        """
        if binary_bolge is None or binary_bolge.size == 0:
            return ""
        
        h, w = binary_bolge.shape[:2]
        
        # Her sütun bir karakter
        sutun_genislik = w / max_karakter
        
        # Her satır bir harf (26 harf varsayalım)
        satir_sayisi = 26
        satir_yukseklik = h / satir_sayisi
        
        isim = []
        
        for sutun in range(max_karakter):
            x1 = int(sutun * sutun_genislik)
            x2 = int((sutun + 1) * sutun_genislik)
            
            en_yuksek_doluluk = 0
            secilen_harf = ''
            
            for satir in range(satir_sayisi):
                y1 = int(satir * satir_yukseklik)
                y2 = int((satir + 1) * satir_yukseklik)
                
                hucre = binary_bolge[y1:y2, x1:x2]
                
                if hucre.size > 0:
                    doluluk = np.sum(hucre > 0) / hucre.size
                    
                    if doluluk > en_yuksek_doluluk and doluluk > 0.15:
                        en_yuksek_doluluk = doluluk
                        if satir < len(self.alfabe):
                            secilen_harf = self.alfabe[satir]
            
            if secilen_harf:
                isim.append(secilen_harf)
        
        return ''.join(isim)
    
    def sonuclari_karsilastir(self, ogrenci_cevaplari: Dict[int, str], 
                               dogru_cevaplar: Dict[int, str]) -> Dict:
        """
        Öğrenci cevaplarını doğru cevaplarla karşılaştır
        
        Args:
            ogrenci_cevaplari: {soru_no: 'A/B/C/D/E/BOŞ', ...}
            dogru_cevaplar: {soru_no: 'A/B/C/D/E', ...}
            
        Returns:
            {
                'dogru_sayisi': int,
                'yanlis_sayisi': int,
                'bos_sayisi': int,
                'toplam_soru': int,
                'basari_yuzdesi': float,
                'detaylar': [{soru, ogrenci, dogru, sonuc}, ...]
            }
        """
        dogru = 0
        yanlis = 0
        bos = 0
        detaylar = []
        
        for soru_no, dogru_cevap in dogru_cevaplar.items():
            ogrenci_cevap = ogrenci_cevaplari.get(soru_no, 'BOŞ')
            
            if ogrenci_cevap == 'BOŞ':
                bos += 1
                sonuc = 'boş'
            elif ogrenci_cevap == dogru_cevap:
                dogru += 1
                sonuc = 'doğru'
            else:
                yanlis += 1
                sonuc = 'yanlış'
            
            detaylar.append({
                'soru': soru_no,
                'ogrenci': ogrenci_cevap,
                'dogru': dogru_cevap,
                'sonuc': sonuc
            })
        
        toplam = len(dogru_cevaplar)
        basari = (dogru / toplam * 100) if toplam > 0 else 0
        
        return {
            'dogru_sayisi': dogru,
            'yanlis_sayisi': yanlis,
            'bos_sayisi': bos,
            'toplam_soru': toplam,
            'basari_yuzdesi': round(basari, 2),
            'net': round(dogru - (yanlis / 4), 2),  # 4 yanlış 1 doğruyu götürür
            'detaylar': detaylar
        }


# Test fonksiyonu
def test_form_okuyucu():
    """Modülü test et"""
    okuyucu = OptikFormOkuyucu(debug_mode=True)
    
    # Test görüntüsü varsa oku
    test_dosyalari = ['test_form.jpg', 'uploads/test.jpg', 'form.jpg']
    
    for dosya in test_dosyalari:
        if os.path.exists(dosya):
            print(f"\n{'='*50}")
            print(f"Test: {dosya}")
            print('='*50)
            
            sonuc = okuyucu.form_oku(dosya)
            
            if sonuc['success']:
                print(f"\n✅ Form başarıyla okundu!")
                print(f"Ad: {sonuc['student_info']['name']}")
                print(f"Soyad: {sonuc['student_info']['surname']}")
                print(f"Toplam cevap: {len(sonuc['answers'])}")
            else:
                print(f"❌ Hata: {sonuc.get('error')}")
            
            return sonuc
    
    print("Test dosyası bulunamadı!")
    return None


if __name__ == "__main__":
    test_form_okuyucu()
