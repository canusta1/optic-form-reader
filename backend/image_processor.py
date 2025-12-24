import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import glob

class OptikFormOkuyucu:
   

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.debug_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_images')
        self.debug_dir = os.path.abspath(self.debug_dir)
        
        if self.debug_mode:
            os.makedirs(self.debug_dir, exist_ok=True)
        
        self.secenekler = ['A', 'B', 'C', 'D', 'E']
        
        self.alfabe = list("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")
        
        self.bolge_oranlari = {
            'ad': {'x1': 0.080, 'y1': 0.092, 'x2': 0.3, 'y2': 0.500},
            'soyad': {'x1': 0.080, 'y1': 0.530, 'x2': 0.3, 'y2': 0.94},
            'turkce': {'x1': 0.315, 'y1': 0.385, 'x2': 0.42, 'y2': 0.94},
            'matematik': {'x1': 0.45, 'y1': 0.385, 'x2': 0.585, 'y2': 0.94},
            'sosyal': {'x1': 0.595, 'y1': 0.385, 'x2': 0.745, 'y2': 0.94},
            'fen': {'x1': 0.74, 'y1': 0.385, 'x2': 0.89, 'y2': 0.94}
        }
    
    def debug_klasoru_temizle(self):
        """Yeni analiz için debug klasörünü temizle"""
        if not self.debug_mode:
            return
        
        try:
            # Tüm görüntü dosyalarını sil
            patterns = ['*.jpg', '*.jpeg', '*.png', '*.gif']
            silinen = 0
            
            for pattern in patterns:
                for dosya in glob.glob(os.path.join(self.debug_dir, pattern)):
                    try:
                        os.remove(dosya)
                        silinen += 1
                    except Exception as e:
                        print(f"Dosya silinemedi: {dosya} - {e}")
            
            if silinen > 0:
                print(f"🧹 Debug klasörü temizlendi: {silinen} dosya silindi")
        except Exception as e:
            print(f"Debug temizleme hatası: {e}")

    def form_oku(self, goruntu_yolu: str) -> Dict:
    
        try:
            # Yeni analiz başlamadan önce eski debug görüntülerini temizle
            self.debug_klasoru_temizle()
            
            print(f"Görüntü yükleniyor: {goruntu_yolu}")
            orijinal = cv2.imread(goruntu_yolu)
            
            if orijinal is None:
                return {'success': False, 'error': 'Görüntü yüklenemedi'}
            
            print("Perspektif düzeltme yapılıyor...")
            duzeltilmis = self.perspektif_duzelt(orijinal)
            
            if duzeltilmis is None:
                return {'success': False, 'error': 'Perspektif düzeltme başarısız'}
            
            print("Yöneliş kontrolü yapılıyor...")
            duzeltilmis = self.yonelisini_kontrol_et(duzeltilmis)
            
            print("Form bölgeleri çıkarılıyor...")
            bolgeler = self.bolgeleri_cikar_renkli(duzeltilmis)
            
            print("Ad/Soyad okunuyor...")
            ad = self.isim_oku_renkli(bolgeler.get('ad'), 12, 'ad')
            soyad = self.isim_oku_renkli(bolgeler.get('soyad'), 12, 'soyisim')
            
            print(f"Ad Soyad: {ad} {soyad}")
        
            
            print("Cevaplar okunuyor...")
            
            tum_cevaplar = {}
            bolum_cevaplari = {}
            soru_sayaci = 1
            
            ders_isimleri = ['turkce', 'matematik', 'fen', 'sosyal']
            ders_etiketleri = ['Türkçe', 'Matematik', 'Fen', 'Sosyal']
            
            for ders, etiket in zip(ders_isimleri, ders_etiketleri):
                if ders in bolgeler and bolgeler[ders] is not None:
                    ders_cevaplari = self.cevaplari_oku_renkli(bolgeler[ders], 40, ders)
                    bolum_cevaplari[ders] = ders_cevaplari
                    
                    # bölge bölge aldığım ders cevaplarını tüm cevaplar listesine ekliyorum.
                    for q, ans in ders_cevaplari.items():
                        tum_cevaplar[soru_sayaci] = ans
                        soru_sayaci += 1
                    
                    bos_sayisi = sum(1 for v in ders_cevaplari.values() if v == 'BOŞ')
                    print(f"   {etiket}: {40 - bos_sayisi}/40 işaretli")
                else:
                    print(f"{etiket} bölgesi bulunamadı")
            
            print(f"Toplam {len(tum_cevaplar)} soru okundu")
            

            # terminale cevaplar yazdırılır.
            print("\n" + "="*60)
            print(" OKUNAN CEVAPLAR")
            print("="*60)
            print(f" Öğrenci: {ad} {soyad}\n")
            
            for ders, etiket in zip(ders_isimleri, ders_etiketleri):
                if ders in bolum_cevaplari:
                    print(f"\n📚 {etiket.upper()} (40 Soru)")
                    print("-" * 60)
                    cevaplar_listesi = []
                    for soru_no in range(1, 41):
                        cevap = bolum_cevaplari[ders].get(soru_no, 'BOŞ')
                        cevaplar_listesi.append(f"{soru_no:2d}:{cevap:3s}")
                        if soru_no % 10 == 0:
                            print("  " + "  ".join(cevaplar_listesi))
                            cevaplar_listesi = []
                    if cevaplar_listesi:
                        print("  " + "  ".join(cevaplar_listesi))
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
    
    # kağıdın yönelişini kontrol eder eğer kağıt yan çevrilmişse düzeltir.
    def yonelisini_kontrol_et(self, goruntu: np.ndarray) -> np.ndarray:
       
        h, w = goruntu.shape[:2]

        if w > h:
            print(f"Kağıt yan çevrilmiş! ({w}x{h}) → Düzeltiliyor...")
            goruntu = cv2.rotate(goruntu, cv2.ROTATE_90_COUNTERCLOCKWISE)
            h, w = goruntu.shape[:2]
            print(f"Düzeltildi: {w}x{h}")
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1e_yonelisli.jpg", goruntu)
        
        return goruntu
    
    # Çoklu strateji ile A4 kağıdını tespit eder ve perspektif düzeltme yapar.
    # ÖNEMLİ: Orijinal görüntü kalitesi korunur, tespit işlemleri kopya üzerinde yapılır.
    def perspektif_duzelt(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
      
        h, w = goruntu.shape[:2]
        
        # ÖNEMLİ: Orijinal görüntüyü koru - tespit için kopya kullan
        orijinal = goruntu.copy()
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/0_orijinal.jpg", orijinal)
        
        print("A4 kağıdı aranıyor (çoklu strateji)...")
        
        # Strateji 1: LAB renk uzayı tabanlı tespit (aydınlatmadan bağımsız)
        print("  [1/6] LAB renk uzayı tespiti...")
        koseler = self.lab_kagit_tespit(goruntu)
        if koseler is not None:
            print("  ✓ LAB tespiti başarılı!")
            return self.perspektif_donustur(orijinal, koseler)
        
        # Strateji 2: Gelişmiş beyaz kağıt tespiti 
        print("  [2/6] Gelişmiş beyaz kağıt tespiti...")
        koseler = self.beyaz_kagit_bul(goruntu)
        if koseler is not None:
            print("  ✓ Beyaz kağıt tespiti başarılı!")
            return self.perspektif_donustur(orijinal, koseler)
        
        # Strateji 3: Saturation analizi
        print("  [3/6] Saturation analizi...")
        koseler = self.saturation_kagit_tespit(goruntu)
        if koseler is not None:
            print("  ✓ Saturation tespiti başarılı!")
            return self.perspektif_donustur(orijinal, koseler)
        
        # Strateji 4: Gelişmiş kenar tespiti (CLAHE + Bilateral)
        print("  [4/6] Gelişmiş kenar tespiti...")
        koseler = self.kenar_ile_dikdortgen_bul(goruntu)
        if koseler is not None:
            print("  ✓ Kenar tespiti başarılı!")
            return self.perspektif_donustur(orijinal, koseler)
        
        # Strateji 5: Gradient magnitude tabanlı tespit (açık arka planlar için)
        print("  [5/6] Gradient magnitude tespiti...")
        koseler = self.gradient_kenar_tespit(goruntu)
        if koseler is not None:
            print("  ✓ Gradient tespiti başarılı!")
            return self.perspektif_donustur(orijinal, koseler)
        
        # Strateji 6: Hough Lines dikdörtgen tespiti
        print("  [6/6] Hough Lines tespiti...")
        koseler = self.hough_lines_dikdortgen_bul(goruntu)
        if koseler is not None:
            print("  ✓ Hough Lines tespiti başarılı!")
            return self.perspektif_donustur(orijinal, koseler)
        
        print("  ✗ Tüm yöntemler başarısız, orijinal boyutlandırılıyor...")
        return self.yeniden_boyutlandir(orijinal)
    
    # LAB renk uzayı tabanlı kağıt tespiti - aydınlatmadan bağımsız
    def lab_kagit_tespit(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        try:
            h, w = goruntu.shape[:2]
            
            # LAB renk uzayına dönüştür
            lab = cv2.cvtColor(goruntu, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            
            # L kanalını normalize et
            l_norm = cv2.normalize(l_channel, None, 0, 255, cv2.NORM_MINMAX)
            
            # Dinamik threshold hesapla - görüntünün parlaklık dağılımına göre
            l_mean = np.mean(l_norm)
            l_std = np.std(l_norm)
            
            # Kağıt genellikle ortalamanın üzerinde parlaklığa sahip
            l_threshold = max(150, min(220, l_mean + l_std * 0.5))
            
            # L kanalı maskesi - yüksek parlaklık
            l_mask = l_norm > l_threshold
            
            # A ve B kanalları için nötrallik kontrolü (kağıt renksizdir)
            # LAB'da 128 nötr noktadır
            a_neutral = np.abs(a_channel.astype(np.float32) - 128) < 25
            b_neutral = np.abs(b_channel.astype(np.float32) - 128) < 35
            
            # Maskeleri birleştir
            combined_mask = l_mask & a_neutral & b_neutral
            combined_mask = combined_mask.astype(np.uint8) * 255
            
            # Morfolojik işlemler - gürültüyü temizle
            kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
            
            # Küçük gürültüleri temizle
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel_small, iterations=2)
            # Boşlukları doldur
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_large, iterations=3)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1a_lab_mask.jpg", combined_mask)
            
            # Konturları bul
            konturlar, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not konturlar:
                return None
            
            # En büyük konturu bul
            en_buyuk = max(konturlar, key=cv2.contourArea)
            alan = cv2.contourArea(en_buyuk)
            
            # Minimum alan kontrolü (%15)
            min_alan = h * w * 0.15
            if alan < min_alan:
                return None
            
            # Convex hull ve 4 köşe bulma
            hull = cv2.convexHull(en_buyuk)
            epsilon = 0.02 * cv2.arcLength(hull, True)
            yaklasik = cv2.approxPolyDP(hull, epsilon, True)
            
            if self.debug_mode:
                debug_img = goruntu.copy()
                cv2.drawContours(debug_img, [yaklasik], -1, (0, 255, 0), 3)
                cv2.imwrite(f"{self.debug_dir}/1b_lab_kontur.jpg", debug_img)
            
            if len(yaklasik) == 4:
                return self.koseler_sirala(yaklasik.reshape(4, 2))
            
            # 4 köşe bulunamazsa minAreaRect kullan
            rect = cv2.minAreaRect(hull)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            
            # A4 oranı kontrolü (yaklaşık 1.41)
            rect_w, rect_h = rect[1]
            if rect_w > 0 and rect_h > 0:
                oran = max(rect_w, rect_h) / min(rect_w, rect_h)
                if oran < 1.2 or oran > 1.8:
                    return None
            
            return self.koseler_sirala(box.astype(np.float32))
            
        except Exception as e:
            print(f"   LAB tespit hatası: {e}")
            return None
    
    # Saturation (doygunluk) tabanlı kağıt tespiti
    def saturation_kagit_tespit(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        try:
            h, w = goruntu.shape[:2]
            
            # HSV renk uzayına dönüştür
            hsv = cv2.cvtColor(goruntu, cv2.COLOR_BGR2HSV)
            h_channel, s_channel, v_channel = cv2.split(hsv)
            
            # Dinamik threshold - görüntüye göre ayarla
            s_mean = np.mean(s_channel)
            v_mean = np.mean(v_channel)
            
            # Düşük saturation threshold (kağıt renksizdir)
            s_threshold = max(30, min(60, s_mean * 0.4))
            # Yüksek value threshold (kağıt parlaktır)
            v_threshold = max(160, min(200, v_mean + 30))
            
            # Maskeler
            low_saturation = s_channel < s_threshold
            high_value = v_channel > v_threshold
            
            # Birleştir
            kagit_mask = (low_saturation & high_value).astype(np.uint8) * 255
            
            # Morfolojik işlemler
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
            kagit_mask = cv2.morphologyEx(kagit_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
            kagit_mask = cv2.morphologyEx(kagit_mask, cv2.MORPH_OPEN, kernel, iterations=2)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1a_saturation_mask.jpg", kagit_mask)
            
            # Konturları bul
            konturlar, _ = cv2.findContours(kagit_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not konturlar:
                return None
            
            # En büyük konturu bul
            en_buyuk = max(konturlar, key=cv2.contourArea)
            alan = cv2.contourArea(en_buyuk)
            
            min_alan = h * w * 0.15
            if alan < min_alan:
                return None
            
            hull = cv2.convexHull(en_buyuk)
            epsilon = 0.02 * cv2.arcLength(hull, True)
            yaklasik = cv2.approxPolyDP(hull, epsilon, True)
            
            if len(yaklasik) == 4:
                return self.koseler_sirala(yaklasik.reshape(4, 2))
            
            rect = cv2.minAreaRect(hull)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            
            # A4 oranı kontrolü
            rect_w, rect_h = rect[1]
            if rect_w > 0 and rect_h > 0:
                oran = max(rect_w, rect_h) / min(rect_w, rect_h)
                if oran < 1.2 or oran > 1.8:
                    return None
            
            return self.koseler_sirala(box.astype(np.float32))
            
        except Exception as e:
            print(f"   Saturation tespit hatası: {e}")
            return None
    
    # Hough Lines ile dikdörtgen tespiti
    def hough_lines_dikdortgen_bul(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        try:
            h, w = goruntu.shape[:2]
            
            # Gri tonlama
            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
            
            # Bilateral filter - kenarları koruyarak gürültüyü azalt
            blur = cv2.bilateralFilter(gri, 11, 75, 75)
            
            # Otsu ile dinamik threshold
            otsu_thresh, _ = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Canny kenar tespiti - Otsu tabanlı dinamik threshold
            low = int(otsu_thresh * 0.3)
            high = int(otsu_thresh * 0.7)
            edges = cv2.Canny(blur, low, high)
            
            # Kenarları kalınlaştır
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.dilate(edges, kernel, iterations=2)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1a_hough_edges.jpg", edges)
            
            # Hough Lines ile çizgi tespiti
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                                    minLineLength=min(h, w) * 0.15, 
                                    maxLineGap=20)
            
            if lines is None or len(lines) < 4:
                return None
            
            # Yatay ve dikey çizgileri ayır
            yatay_cizgiler = []
            dikey_cizgiler = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                aci = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                
                if aci < 15 or aci > 165:  # Yatay
                    yatay_cizgiler.append(line[0])
                elif 75 < aci < 105:  # Dikey
                    dikey_cizgiler.append(line[0])
            
            if len(yatay_cizgiler) < 2 or len(dikey_cizgiler) < 2:
                return None
            
            # En üst, en alt, en sol, en sağ çizgileri bul
            yatay_cizgiler.sort(key=lambda l: (l[1] + l[3]) / 2)
            dikey_cizgiler.sort(key=lambda l: (l[0] + l[2]) / 2)
            
            ust_cizgi = yatay_cizgiler[0]
            alt_cizgi = yatay_cizgiler[-1]
            sol_cizgi = dikey_cizgiler[0]
            sag_cizgi = dikey_cizgiler[-1]
            
            # Çizgi kesişimlerinden köşeleri hesapla
            def cizgi_kesisimi(line1, line2):
                x1, y1, x2, y2 = line1
                x3, y3, x4, y4 = line2
                
                denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if abs(denom) < 1e-10:
                    return None
                
                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
                
                px = x1 + t * (x2 - x1)
                py = y1 + t * (y2 - y1)
                
                return [px, py]
            
            # 4 köşeyi hesapla
            sol_ust = cizgi_kesisimi(ust_cizgi, sol_cizgi)
            sag_ust = cizgi_kesisimi(ust_cizgi, sag_cizgi)
            sol_alt = cizgi_kesisimi(alt_cizgi, sol_cizgi)
            sag_alt = cizgi_kesisimi(alt_cizgi, sag_cizgi)
            
            if None in [sol_ust, sag_ust, sol_alt, sag_alt]:
                return None
            
            koseler = np.array([sol_ust, sag_ust, sag_alt, sol_alt], dtype=np.float32)
            
            # Sınır kontrolü
            for kose in koseler:
                if kose[0] < 0 or kose[0] > w or kose[1] < 0 or kose[1] > h:
                    return None
            
            # Alan kontrolü
            alan = cv2.contourArea(koseler)
            if alan < h * w * 0.15:
                return None
            
            # A4 oranı kontrolü
            genislik = np.linalg.norm(koseler[1] - koseler[0])
            yukseklik = np.linalg.norm(koseler[3] - koseler[0])
            if yukseklik > 0 and genislik > 0:
                oran = max(genislik, yukseklik) / min(genislik, yukseklik)
                if oran < 1.2 or oran > 1.8:
                    return None
            
            if self.debug_mode:
                debug_img = goruntu.copy()
                cv2.polylines(debug_img, [koseler.astype(np.int32)], True, (0, 255, 0), 3)
                cv2.imwrite(f"{self.debug_dir}/1b_hough_rect.jpg", debug_img)
            
            return self.koseler_sirala(koseler)
            
        except Exception as e:
            print(f"   Hough Lines hatası: {e}")
            return None
    
    # Gradient magnitude tabanlı kenar tespiti - açık arka planlarda etkili
    def gradient_kenar_tespit(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        try:
            h, w = goruntu.shape[:2]
            
            # Gri tonlama
            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
            
            # Gürültü azaltma
            blur = cv2.GaussianBlur(gri, (5, 5), 0)
            
            # Sobel gradient hesapla
            sobelx = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=3)
            
            # Gradient magnitude
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Dinamik threshold
            mag_mean = np.mean(magnitude)
            mag_std = np.std(magnitude)
            threshold = max(30, min(80, mag_mean + mag_std))
            
            # Binary mask
            _, edges = cv2.threshold(magnitude, int(threshold), 255, cv2.THRESH_BINARY)
            
            # Morfolojik işlemler
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.dilate(edges, kernel, iterations=2)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=3)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1a_gradient_edges.jpg", edges)
            
            # Konturları bul
            konturlar, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not konturlar:
                return None
            
            # En büyük konturları sırala
            konturlar = sorted(konturlar, key=cv2.contourArea, reverse=True)
            
            for kontur in konturlar[:5]:
                alan = cv2.contourArea(kontur)
                
                if alan < h * w * 0.15:
                    continue
                
                hull = cv2.convexHull(kontur)
                hull_alan = cv2.contourArea(hull)
                konvekslik = alan / hull_alan if hull_alan > 0 else 0
                
                if konvekslik < 0.6:
                    continue
                
                rect = cv2.minAreaRect(hull)
                box = cv2.boxPoints(rect)
                box = np.int32(box)
                
                rect_w, rect_h = rect[1]
                if rect_w > 0 and rect_h > 0:
                    oran = max(rect_w, rect_h) / min(rect_w, rect_h)
                    if 1.2 < oran < 1.8:
                        koseler = self.koseler_sirala(box.astype(np.float32))
                        
                        if self.debug_mode:
                            debug_img = goruntu.copy()
                            cv2.drawContours(debug_img, [np.int32(koseler)], -1, (0, 255, 0), 3)
                            cv2.imwrite(f"{self.debug_dir}/1b_gradient_rect.jpg", debug_img)
                        
                        return koseler
            
            return None
            
        except Exception as e:
            print(f"   Gradient tespit hatası: {e}")
            return None
    
    # Geliştirilmiş beyaz kağıt tespiti - dinamik threshold ve çoklu strateji
    def beyaz_kagit_bul(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
       
        try:
            h, w = goruntu.shape[:2]
            
            # Gri tonlamaya çevir
            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
            
            # Bilateral filter - kenarları koruyarak gürültüyü azalt
            blur = cv2.bilateralFilter(gri, 9, 75, 75)
            
            # Dinamik threshold hesapla - görüntüye göre ayarla
            gri_mean = np.mean(blur)
            gri_std = np.std(blur)
            
            # Otsu threshold
            otsu_thresh, _ = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Çoklu threshold denemesi
            thresholds_to_try = [
                max(140, min(200, gri_mean + gri_std)),  # Dinamik
                otsu_thresh,  # Otsu
                170,  # Varsayılan yüksek
                150,  # Orta
            ]
            
            best_result = None
            best_score = 0
            
            for thresh_val in thresholds_to_try:
                # Binary threshold
                _, beyaz_maske = cv2.threshold(blur, int(thresh_val), 255, cv2.THRESH_BINARY)
                
                # Adaptif threshold
                adaptif = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 15, 3)
                
                # Maskeleri birleştir
                kombine = cv2.bitwise_and(beyaz_maske, adaptif)
                
                # Morfolojik işlemler - daha agresif
                kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
                kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
                
                # Önce küçük gürültüleri temizle
                kombine = cv2.morphologyEx(kombine, cv2.MORPH_OPEN, kernel_small, iterations=2)
                # Sonra boşlukları doldur
                kombine = cv2.morphologyEx(kombine, cv2.MORPH_CLOSE, kernel_large, iterations=4)
                
                # Konturları bul
                konturlar, _ = cv2.findContours(kombine, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if not konturlar:
                    continue
                
                # En büyük konturu bul
                en_buyuk = max(konturlar, key=cv2.contourArea)
                alan = cv2.contourArea(en_buyuk)
                
                # Minimum alan kontrolü (%15)
                min_alan = h * w * 0.15
                if alan < min_alan:
                    continue
                
                # Konvekslik skoru hesapla
                hull = cv2.convexHull(en_buyuk)
                hull_alan = cv2.contourArea(hull)
                konvekslik = alan / hull_alan if hull_alan > 0 else 0
                
                # A4 oranı kontrolü
                rect = cv2.minAreaRect(en_buyuk)
                rect_w, rect_h = rect[1]
                if rect_w > 0 and rect_h > 0:
                    oran = max(rect_w, rect_h) / min(rect_w, rect_h)
                    if oran < 1.2 or oran > 1.8:
                        continue
                else:
                    continue
                
                # Skor hesapla (alan + konvekslik + oran uyumu)
                oran_uyumu = 1 - abs(oran - 1.41) / 0.41  # A4 oranına yakınlık
                score = (alan / (h * w)) * konvekslik * oran_uyumu
                
                if score > best_score:
                    best_score = score
                    best_result = (en_buyuk, hull, kombine)
            
            if best_result is None:
                return None
            
            en_buyuk, hull, kombine = best_result
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1a_beyaz_maske.jpg", kombine)
            
            # Poligon yaklaşımı ile 4 köşe bul
            epsilon = 0.02 * cv2.arcLength(hull, True)
            yaklasik = cv2.approxPolyDP(hull, epsilon, True)
            
            if self.debug_mode:
                debug_img = goruntu.copy()
                cv2.drawContours(debug_img, [yaklasik], -1, (0, 255, 0), 3)
                cv2.imwrite(f"{self.debug_dir}/1b_kontur_beyaz.jpg", debug_img)
            
            if len(yaklasik) == 4:
                koseler = self.koseler_sirala(yaklasik.reshape(4, 2))
                # A4 oranı son kontrolü
                genislik = np.linalg.norm(koseler[1] - koseler[0])
                yukseklik = np.linalg.norm(koseler[3] - koseler[0])
                if yukseklik > 0 and genislik > 0:
                    oran = max(genislik, yukseklik) / min(genislik, yukseklik)
                    if 1.2 < oran < 1.8:
                        return koseler
            
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
    
    # Geliştirilmiş Canny kenar tespiti ile dikdörtgen bulur
    def kenar_ile_dikdortgen_bul(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
        try:
            h, w = goruntu.shape[:2]

            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
            
            # CLAHE ile kontrastı artır (histogram eşitleme)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gri = clahe.apply(gri)
            
            # Bilateral filter - kenarları koruyarak gürültüyü azalt
            blur = cv2.bilateralFilter(gri, 11, 75, 75)
            
            # Otsu ile dinamik threshold
            otsu_thresh, _ = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Dinamik ve sabit threshold kombinasyonları
            threshold_pairs = [
                (int(otsu_thresh * 0.3), int(otsu_thresh * 0.7)),  # Otsu tabanlı
                (int(otsu_thresh * 0.2), int(otsu_thresh * 0.5)),  # Düşük Otsu
                (20, 60),   # Düşük sabit
                (30, 100),  # Orta sabit
                (50, 150),  # Yüksek sabit
            ]
            
            best_result = None
            best_score = 0

            for low, high in threshold_pairs:
                # Canny kenar tespiti
                kenarlar = cv2.Canny(blur, low, high)
                
                # Kenarları kalınlaştır
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                kenarlar = cv2.dilate(kenarlar, kernel, iterations=2)
                
                # Kenarları birleştir
                kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                kenarlar = cv2.morphologyEx(kenarlar, cv2.MORPH_CLOSE, kernel_close, iterations=2)
                
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
                    
                    # Minimum alan kontrolü (%15)
                    if alan < h * w * 0.15:
                        continue
                    
                    # Konveks hull
                    hull = cv2.convexHull(kontur)
                    hull_alan = cv2.contourArea(hull)
                    
                    # Konvekslik kontrolü
                    konvekslik = alan / hull_alan if hull_alan > 0 else 0
                    if konvekslik < 0.7:  # Çok düzensiz şekilleri atla
                        continue
                    
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
                        
                        sirali = self.koseler_sirala(koseler.astype(np.float32))
                        genislik = np.linalg.norm(sirali[1] - sirali[0])
                        yukseklik = np.linalg.norm(sirali[3] - sirali[0])
                        
                        if yukseklik > 0 and genislik > 0:
                            oran = max(genislik, yukseklik) / min(genislik, yukseklik)
                            if 1.2 < oran < 1.8:
                                # Skor hesapla
                                oran_uyumu = 1 - abs(oran - 1.41) / 0.41
                                score = (alan / (h * w)) * konvekslik * oran_uyumu
                                
                                if score > best_score:
                                    best_score = score
                                    best_result = sirali
            
            if best_result is not None:
                if self.debug_mode:
                    debug_img = goruntu.copy()
                    cv2.drawContours(debug_img, [np.int32(best_result)], -1, (0, 255, 0), 3)
                    cv2.imwrite(f"{self.debug_dir}/1e_dikdortgen.jpg", debug_img)
                
                return best_result
            
            return None
            
        except Exception as e:
            print(f"   Kenar tespiti hatası: {e}")
            return None
    
    def perspektif_donustur(self, goruntu: np.ndarray, koseler: np.ndarray) -> np.ndarray:
       
        genislik = 1600
        yukseklik = 2264
        
        hedef = np.array([
            [0, 0],
            [genislik - 1, 0],
            [genislik - 1, yukseklik - 1],
            [0, yukseklik - 1]
        ], dtype=np.float32)
        
        matris = cv2.getPerspectiveTransform(koseler.astype(np.float32), hedef)
        
        duzeltilmis = cv2.warpPerspective(goruntu, matris, (genislik, yukseklik), 
                                          flags=cv2.INTER_CUBIC)
        
        if self.debug_mode:
            debug_img = goruntu.copy()
            for i, kose in enumerate(koseler):
                cv2.circle(debug_img, (int(kose[0]), int(kose[1])), 10, (0, 255, 0), -1)
                cv2.putText(debug_img, str(i), (int(kose[0])+15, int(kose[1])), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imwrite(f"{self.debug_dir}/1c_koseler.jpg", debug_img)
            cv2.imwrite(f"{self.debug_dir}/1d_perspektif_ham.jpg", duzeltilmis)
        
        duzeltilmis = self.perspektif_sonrasi_iyilestir_hafif(duzeltilmis)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1d_perspektif.jpg", duzeltilmis)
        
        return duzeltilmis
    
    
    # Perspektif düzeltme sonrası hafif iyileştirme
    # NOT: Daire okumayı bozmamak için çok agresif işlemler yapılmaz
    def perspektif_sonrasi_iyilestir_hafif(self, goruntu: np.ndarray) -> np.ndarray:
        
        if len(goruntu.shape) == 3:
            canals = cv2.split(goruntu)
            processed_canals = []
            
            for canal in canals:
                # Hafif gürültü azaltma - daire şekillerini korumak için düşük h değeri
                denoised = cv2.fastNlMeansDenoising(canal, None, h=5, templateWindowSize=7, searchWindowSize=21)
                
                # Çok hafif keskinleştirme - daireleri bozmamak için
                gaussian = cv2.GaussianBlur(denoised, (0, 0), 1.0)
                # Düşük keskinleştirme oranı (1.15 vs 1.3)
                sharpened = cv2.addWeighted(denoised, 1.15, gaussian, -0.15, 0)
                
                processed_canals.append(sharpened)
            
            # Kanalları birleştir
            result = cv2.merge(processed_canals)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1e_renkli_iyilestirilmis.jpg", result)
        else:
            # Gri tonlama için
            denoised = cv2.fastNlMeansDenoising(goruntu, None, h=5, templateWindowSize=7, searchWindowSize=21)
            gaussian = cv2.GaussianBlur(denoised, (0, 0), 1.0)
            sharpened = cv2.addWeighted(denoised, 1.2, gaussian, -0.2, 0)
            result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        
        return result
    
    # perspektif bulunamazsa sadece yeniden boyutlandır.
    def yeniden_boyutlandir(self, goruntu: np.ndarray) -> np.ndarray:
        genislik = 1600
        yukseklik = 2264
        resized = cv2.resize(goruntu, (genislik, yukseklik), interpolation=cv2.INTER_CUBIC)
        return self.perspektif_sonrasi_iyilestir_hafif(resized)
    
    def koseler_sirala(self, noktalar: np.ndarray) -> np.ndarray:
        
        noktalar = noktalar.astype(np.float32)
        
        y_sirali = noktalar[np.argsort(noktalar[:, 1])]
        ust_noktalar = y_sirali[:2]
        alt_noktalar = y_sirali[2:]
        
        ust_noktalar = ust_noktalar[np.argsort(ust_noktalar[:, 0])]
        alt_noktalar = alt_noktalar[np.argsort(alt_noktalar[:, 0])]
        
        sol_ust = ust_noktalar[0]
        sag_ust = ust_noktalar[1]
        sol_alt = alt_noktalar[0]
        sag_alt = alt_noktalar[1]
        
        genislik = np.linalg.norm(sag_ust - sol_ust)
        yukseklik = np.linalg.norm(sol_alt - sol_ust)
        
        sirali = np.zeros((4, 2), dtype=np.float32)
        
      
        if genislik > yukseklik:
           
            sirali[0] = sag_ust   
            sirali[1] = sag_alt   
            sirali[2] = sol_alt   
            sirali[3] = sol_ust   
        else:
            sirali[0] = sol_ust
            sirali[1] = sag_ust
            sirali[2] = sag_alt
            sirali[3] = sol_alt
        
        return sirali
    
    
    def ad_soyad_kutularini_bul(self, img: np.ndarray) -> List[Dict]:
       
        h, w = img.shape[:2]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 15, 5)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
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
            
            if x > w * 0.35:  
                continue
            if aspect > 0.60:  
                continue
            if bh < min_box_height: 
                continue
            if bw < min_box_width or bw > max_box_width:
                continue
            
            candidates.append({
                'x': x, 'y': y, 'w': bw, 'h': bh, 'area': area
            })
        
        print(f"Ad/Soyad kutu adayı sayısı: {len(candidates)}")
        
        unique_boxes = []
        for box in candidates:
            is_duplicate = False
            for existing in unique_boxes:
                
                y_overlap = (box['y'] < existing['y'] + existing['h'] and 
                            box['y'] + box['h'] > existing['y'])
                
                if y_overlap and abs(box['x'] - existing['x']) < 30:
                    if box['area'] > existing['area']:
                        unique_boxes.remove(existing)
                        unique_boxes.append(box)
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_boxes.append(box)
        
        print(f"Eşsiz Ad/Soyad kutu sayısı: {len(unique_boxes)}")
        
        filtered_boxes = []
        
        for i, box1 in enumerate(unique_boxes):
            for box2 in unique_boxes[i+1:]:
                x_farki = abs(box1['x'] - box2['x'])
                if x_farki > 30:
                    continue
                
                w_oran = min(box1['w'], box2['w']) / max(box1['w'], box2['w'])
                h_oran = min(box1['h'], box2['h']) / max(box1['h'], box2['h'])
                
                if w_oran < 0.80 or h_oran < 0.80:
                    continue
                
                y_farki = abs(box1['y'] - box2['y'])
                if y_farki < h * 0.10:
                    continue
                
                if box1['y'] < box2['y']:
                    filtered_boxes = [box1, box2]
                else:
                    filtered_boxes = [box2, box1]
                
                print(f"Ad/Soyad çifti bulundu")
                break
            
            if filtered_boxes:
                break
        
        print(f"Filtrelenmiş Ad/Soyad kutu sayısı: {len(filtered_boxes)}")
        for i, box in enumerate(filtered_boxes[:2]):
            print(f" Kutu {i+1} ({'Ad' if i==0 else 'Soyad'}): x={box['x']}, y={box['y']}, w={box['w']}, h={box['h']}")
        
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

        h, w = img.shape[:2]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 15, 5)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        min_box_width = w * 0.06
        max_box_width = w * 0.22
        min_box_height = h * 0.40
        
        candidates = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 3000:
                continue
            
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = bw / bh if bh > 0 else 999
            
            if x < w * 0.25:  
                continue
            if aspect > 0.30:  
                continue
            if bh < min_box_height: 
                continue
            if bw < min_box_width or bw > max_box_width:
                continue
            
            candidates.append({
                'x': x, 'y': y, 'w': bw, 'h': bh, 'area': area
            })
        
        print(f"Kutu adayı sayısı: {len(candidates)}")
        for i, box in enumerate(candidates):
            print(f"Aday {i+1}: x={box['x']}, y={box['y']}, w={box['w']}, h={box['h']}")
        
        unique_boxes = []
        for box in candidates:
            is_duplicate = False
            for existing in unique_boxes:
               
                x_overlap = (box['x'] < existing['x'] + existing['w'] and 
                            box['x'] + box['w'] > existing['x'])
                
                if x_overlap and abs(box['y'] - existing['y']) < 30:
                    if box['area'] > existing['area']:
                        unique_boxes.remove(existing)
                        unique_boxes.append(box)
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_boxes.append(box)
        
        print(f"Eşsiz kutu sayısı: {len(unique_boxes)}")
        
        # x'e göre sırala soldan sağa türkçe, matematik, fen, sosyal
        unique_boxes.sort(key=lambda b: b['x'])
        
        # kutular arasında minimum mesafe kontrolü
        min_distance = w * 0.12
        filtered_boxes = []
        
        for box in unique_boxes:
            too_close = False
            for selected in filtered_boxes:
                distance = abs(box['x'] - selected['x'])
                if distance < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                filtered_boxes.append(box)
        
        print(f"Filtrelenmiş kutu sayısı: {len(filtered_boxes)}")
        for i, box in enumerate(filtered_boxes[:4]):
            print(f"Kutu {i+1}: x={box['x']}, w={box['w']}")
        
        if self.debug_mode and len(filtered_boxes) >= 4:
            debug_img = img.copy()
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
        h, w = renkli.shape[:2]
        bolgeler = {}
        
        ad_soyad_kutular = self.ad_soyad_kutularini_bul(renkli)
        
        if len(ad_soyad_kutular) == 2:
            print(" Ad/Soyad kutuları otomatik tespit edildi")
            ad_soyad_isimleri = ['ad', 'soyad']
            
            for i, kutu in enumerate(ad_soyad_kutular):
                bolge_adi = ad_soyad_isimleri[i]
                x, y, bw, bh = kutu['x'], kutu['y'], kutu['w'], kutu['h']
                
                kirpma = int(bh * 0.065)
                y += kirpma
                bh -= kirpma
                
                bolgeler[bolge_adi] = renkli[y:y+bh, x:x+bw].copy()
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/bolge_{bolge_adi}.jpg", bolgeler[bolge_adi])
        else:
            print(f"Ad/Soyad otomatik tespit başarısız, sabit koordinat kullanılıyor")
            # sabit koordinat kullan
            ad_soyad_oranlari = {
                'ad': {'x1': 0.080, 'y1': 0.092, 'x2': 0.28, 'y2': 0.500},
                'soyad': {'x1': 0.080, 'y1': 0.530, 'x2': 0.28, 'y2': 0.94}
            }
            
            for bolge_adi, oranlar in ad_soyad_oranlari.items():
                x1 = int(w * oranlar['x1'])
                y1 = int(h * oranlar['y1'])
                x2 = int(w * oranlar['x2'])
                y2 = int(h * oranlar['y2'])
                
                # üstten kırpma yap
                bh = y2 - y1
                kirpma = int(bh * 0.05)
                y1 += kirpma
                y2 = y1 + (bh - kirpma)
                
                bolgeler[bolge_adi] = renkli[y1:y2, x1:x2].copy()
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/bolge_{bolge_adi}.jpg", bolgeler[bolge_adi])
        
        # cevap kutularını tespit et
        kutular = self.cevap_kutularini_bul(renkli)
        
        if len(kutular) == 4:
            print("4 cevap kutusu otomatik tespit edildi")
            ders_isimleri = ['turkce', 'matematik', 'fen', 'sosyal']
            
            for i, kutu in enumerate(kutular):
                ders = ders_isimleri[i]
                x, y, bw, bh = kutu['x'], kutu['y'], kutu['w'], kutu['h']
                
                kirpma = int(bh * 0.02)
                y += kirpma
                bh -= kirpma
                
                bolgeler[ders] = renkli[y:y+bh, x:x+bw].copy()
                
                if self.debug_mode:
                    cv2.imwrite(f"{self.debug_dir}/bolge_{ders}.jpg", bolgeler[ders])
        
        else:
            print(f"Otomatik tespit başarısız, sabit koordinat kullanılıyor")
            
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
        
        return bolgeler
    
    def cevaplari_oku_renkli(self, bolge_renkli: np.ndarray, soru_sayisi: int = 40, ders_adi: str = "") -> Dict[int, str]:
        cevaplar = {}
        
        if bolge_renkli is None or bolge_renkli.size == 0:
            return {i: 'BOŞ' for i in range(1, soru_sayisi + 1)}
        
        h, w = bolge_renkli.shape[:2]
        
        # Gri tonlama
        gri = cv2.cvtColor(bolge_renkli, cv2.COLOR_BGR2GRAY)
        
        # Debug görüntüsü
        if self.debug_mode:
            debug_img = bolge_renkli.copy()
        
        # Hafif blur - daireleri korumak için
        blurred = cv2.GaussianBlur(gri, (5, 5), 0)
        
        # Satır ve daire boyutu
        satir_yuksekligi = h / soru_sayisi
        beklenen_yaricap = int(satir_yuksekligi / 2.5)
        
        # HoughCircles parametreleri - biraz daha katı
        min_r = max(8, int(beklenen_yaricap * 0.7))
        max_r = int(beklenen_yaricap * 1.3)
        
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=int(beklenen_yaricap * 0.8),
            param1=50,
            param2=22,  # Biraz daha katı (20 -> 22)
            minRadius=min_r,
            maxRadius=max_r
        )
        
        if circles is None:
            print(f"{ders_adi}: HoughCircles bulamadı!")
            return {i: 'BOŞ' for i in range(1, soru_sayisi + 1)}
        
        detected = circles[0]
        print(f"{ders_adi}: {len(detected)} daire tespit edildi (r:{min_r}-{max_r}px)")
        
        daire_bilgileri = []
        yaricap_listesi = []
        tum_avg_degerleri = []  # Tüm parlaklık değerleri
        
        for circle in detected:
            cx, cy, r = float(circle[0]), float(circle[1]), float(circle[2])
            
            if r < min_r:
                continue
            
            yaricap_listesi.append(r)
            
            # ROI bölge etrafında ufak bir kare oluşturur
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
            std = float(np.std(pixels))  # Standart sapma da hesapla
            min_val = float(np.min(pixels))  # Minimum değer
            
            tum_avg_degerleri.append(avg)
            
            satir_no = int(cy / satir_yuksekligi) + 1
            satir_no = max(1, min(soru_sayisi, satir_no))
            
            daire_bilgileri.append({
                'cx': cx, 'cy': cy, 'r': r,
                'avg': avg, 'std': std, 'min': min_val, 'satir': satir_no
            })
        
        # Anormal büyük daireleri filtrele
        if len(yaricap_listesi) > 10:
            yaricap_median = float(np.median(yaricap_listesi))
            yaricap_std = float(np.std(yaricap_listesi))
            max_kabul_edilebilir = yaricap_median + (2 * yaricap_std)
            
            onceki_sayi = len(daire_bilgileri)
            daire_bilgileri = [d for d in daire_bilgileri if d['r'] <= max_kabul_edilebilir]
            
            if len(daire_bilgileri) < onceki_sayi:
                print(f"{ders_adi}: {onceki_sayi - len(daire_bilgileri)} büyük daire filtrelendi (r>{max_kabul_edilebilir:.1f})")
        
        # Dinamik eşikler hesapla - tüm dairelerin ortalamasına göre
        if len(tum_avg_degerleri) > 5:
            global_ortalama = float(np.mean(tum_avg_degerleri))
            global_std = float(np.std(tum_avg_degerleri))
            # İşaretli kabul edilecek maksimum parlaklık (daha katı)
            dinamik_esik = min(140, global_ortalama - global_std * 0.5)
        else:
            dinamik_esik = 130  # Varsayılan daha katı
            global_ortalama = 180
        
        if self.debug_mode:
            print(f"      {ders_adi} - Dinamik eşik: {dinamik_esik:.0f}, Global ort: {global_ortalama:.0f}")
            for d in daire_bilgileri:
                renk = (0, 255, 0) if d['avg'] < dinamik_esik else (0, 0, 255)
                cv2.circle(debug_img, (int(d['cx']), int(d['cy'])), int(d['r']), renk, 1)
        
        # Satırlara grupla
        satirlar = {}
        for d in daire_bilgileri:
            s = d['satir']
            if s not in satirlar:
                satirlar[s] = []
            satirlar[s].append(d)
        
        # Her satır işlenir
        for satir_no in range(1, soru_sayisi + 1):
            if satir_no not in satirlar or len(satirlar[satir_no]) == 0:
                cevaplar[satir_no] = 'BOŞ'
                continue
            
            daireler = satirlar[satir_no]
            
            # X'e göre sırala (A, B, C, D, E)
            daireler.sort(key=lambda d: d['cx'])
            
            secenekler = daireler[:5]
            
            if len(secenekler) == 0:
                cevaplar[satir_no] = 'BOŞ'
                continue
            
            # En koyu olanı bul
            en_koyu = min(secenekler, key=lambda d: d['avg'])
            en_koyu_idx = secenekler.index(en_koyu)
            
            diger_avg = [d['avg'] for d in secenekler if d != en_koyu]
            diger_ortalama = sum(diger_avg) / len(diger_avg) if diger_avg else 255
            
            # ===== DAHA KATI KRİTERLER =====
            
            # Kriter 1: Mutlak karanlık eşiği (dinamik veya sabit)
            mutlak_esik = min(dinamik_esik, 135)
            kriter1_gecti = en_koyu['avg'] < mutlak_esik
            
            # Kriter 2: Diğerlerinden yeterince koyu olmalı (fark kontrolü)
            min_fark = 25  # 20 -> 25 daha katı
            kriter2_gecti = (diger_ortalama - en_koyu['avg']) > min_fark
            
            # Kriter 3: Oran kontrolü - en koyu, diğerlerinin ortalamasının %85'inden az olmalı
            oran_esik = 0.85
            if diger_ortalama > 0:
                kriter3_gecti = (en_koyu['avg'] / diger_ortalama) < oran_esik
            else:
                kriter3_gecti = False
            
            # Kriter 4: Standart sapma kontrolü - işaretli dairelerin içi homojen olmalı
            # (çok yüksek std değeri gölge veya kirlilik olabilir)
            kriter4_gecti = en_koyu['std'] < 50  # İç homojenlik
            
            # Kriter 5: Minimum piksel değeri - en az birkaç piksel çok koyu olmalı
            kriter5_gecti = en_koyu['min'] < 100
            
            # Tüm kriterleri değerlendir (en az 4 tanesi geçmeli)
            gecen_kriter_sayisi = sum([kriter1_gecti, kriter2_gecti, kriter3_gecti, kriter4_gecti, kriter5_gecti])
            
            # Kesin işaretli: Kriter 1, 2 ve 3 mutlaka geçmeli + en az 1 tane daha
            kesin_isaretli = kriter1_gecti and kriter2_gecti and kriter3_gecti and gecen_kriter_sayisi >= 4
            
            if kesin_isaretli:
                cevaplar[satir_no] = self.secenekler[en_koyu_idx]
                if self.debug_mode:
                    cv2.circle(debug_img, (int(en_koyu['cx']), int(en_koyu['cy'])), 
                              int(en_koyu['r']) + 2, (0, 255, 0), 3)
            else:
                cevaplar[satir_no] = 'BOŞ'
             
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/circles_{ders_adi}.jpg", debug_img)
            ilk_10 = {k: v for k, v in list(cevaplar.items())[:10]}
            print(f"      {ders_adi} ilk 10: {ilk_10}")
        
        isaretli = sum(1 for v in cevaplar.values() if v != 'BOŞ')
        print(f"      {ders_adi}: {isaretli}/{soru_sayisi} işaretli")
        
        return cevaplar
    
    
    def isim_oku_renkli(self, bolge_renkli: np.ndarray, max_karakter: int = 12, bolge_adi: str = "isim") -> str:
        if bolge_renkli is None or bolge_renkli.size == 0:
            return ""
        
        h, w = bolge_renkli.shape[:2]
        
        gri = cv2.cvtColor(bolge_renkli, cv2.COLOR_BGR2GRAY)
        
        if self.debug_mode:
            debug_img = bolge_renkli.copy()
        
        blurred = cv2.GaussianBlur(gri, (5, 5), 0)
        
        sutun_genisligi = w / max_karakter
        satir_sayisi = len(self.alfabe)  
        satir_yuksekligi = h / satir_sayisi
        beklenen_yaricap = int(min(satir_yuksekligi, sutun_genisligi) / 2.5)
        
        
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
            print(f"{bolge_adi}: HoughCircles bulamadı!")
            return ""
        
        detected = circles[0]
        print(f"{bolge_adi}: {len(detected)} daire tespit edildi (r:{min_r}-{max_r}px)")
        
        daire_bilgileri = []
        tum_avg_degerleri = []  # Tüm parlaklık değerleri
        
        for circle in detected:
            cx, cy, r = float(circle[0]), float(circle[1]), float(circle[2])
            
            if r < min_r:
                continue
            
            x1, y1 = max(0, int(cx - r)), max(0, int(cy - r))
            x2, y2 = min(w, int(cx + r)), min(h, int(cy + r))
            roi = gri[y1:y2, x1:x2]
            
            if roi.size == 0:
                continue
            
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
            std = float(np.std(pixels))
            min_val = float(np.min(pixels))
            
            tum_avg_degerleri.append(avg)
            
            sutun_no = int(cx / sutun_genisligi)
            satir_no = int(cy / satir_yuksekligi)
            
            if sutun_no < 0 or sutun_no >= max_karakter:
                continue
            if satir_no < 0 or satir_no >= satir_sayisi:
                continue
            
            daire_bilgileri.append({
                'cx': cx, 'cy': cy, 'r': r,
                'avg': avg, 'std': std, 'min': min_val, 'sutun': sutun_no, 'satir': satir_no
            })
        
        # Dinamik eşik hesapla
        if len(tum_avg_degerleri) > 5:
            global_ortalama = float(np.mean(tum_avg_degerleri))
            dinamik_esik = min(130, global_ortalama - 30)
        else:
            dinamik_esik = 120
      
        if self.debug_mode:
            for d in daire_bilgileri:
                renk = (0, 255, 0) if d['avg'] < dinamik_esik else (0, 0, 255)
                cv2.circle(debug_img, (int(d['cx']), int(d['cy'])), int(d['r']), renk, 1)
        
        sutunlar = {}
        for d in daire_bilgileri:
            s = d['sutun']
            if s not in sutunlar:
                sutunlar[s] = []
            sutunlar[s].append(d)
        
        isim = []
        for sutun_no in range(max_karakter):
            if sutun_no not in sutunlar or len(sutunlar[sutun_no]) == 0:
                continue
            
            daireler = sutunlar[sutun_no]
            
            en_koyu = min(daireler, key=lambda d: d['avg'])
            
            diger = [d['avg'] for d in daireler if d != en_koyu]
            diger_ortalama = sum(diger) / len(diger) if diger else 255
            
            # Daha katı kriterler
            mutlak_esik = min(dinamik_esik, 130)
            min_fark = 25
            oran_esik = 0.85
            
            kriter1 = en_koyu['avg'] < mutlak_esik
            kriter2 = (diger_ortalama - en_koyu['avg']) > min_fark
            kriter3 = (en_koyu['avg'] / diger_ortalama) < oran_esik if diger_ortalama > 0 else False
            kriter4 = en_koyu['std'] < 50
            kriter5 = en_koyu['min'] < 100
            
            gecen_kriter = sum([kriter1, kriter2, kriter3, kriter4, kriter5])
            kesin_isaretli = kriter1 and kriter2 and kriter3 and gecen_kriter >= 4
            
            if kesin_isaretli:
                harf_idx = en_koyu['satir']
                if 0 <= harf_idx < len(self.alfabe):
                    isim.append((sutun_no, self.alfabe[harf_idx]))
                    
                    if self.debug_mode:
                        cv2.circle(debug_img, (int(en_koyu['cx']), int(en_koyu['cy'])), 
                                  int(en_koyu['r']) + 2, (0, 255, 0), 3)
        
        isim.sort(key=lambda x: x[0])
        isim_str = ''.join([h for _, h in isim])
        
       
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/{bolge_adi}_circles.jpg", debug_img)
            print(f"{bolge_adi.capitalize()} tespit: {isim_str}")
        
        return isim_str
    
    
    def sonuclari_karsilastir(self, ogrenci_cevaplari: Dict[int, str], 
                               dogru_cevaplar: Dict[int, str]) -> Dict:
      
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
            'net': round(dogru - (yanlis / 4), 2),  
            'detaylar': detaylar
        }


