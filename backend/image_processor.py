import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

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
    

    def form_oku(self, goruntu_yolu: str) -> Dict:
    
        try:
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
            
            print(f"   Ad Soyad: {ad} {soyad}")
        
            
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
                    print(f"   ⚠️  {etiket} bölgesi bulunamadı")
            
            print(f"✅ Toplam {len(tum_cevaplar)} soru okundu")
            

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
    
    # önce a4 kağıdını 2 yöntemle sırayla tespit eder daha sonra perspektif düzeltme yapar.
    def perspektif_duzelt(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
      
        h, w = goruntu.shape[:2]
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/0_orijinal.jpg", goruntu)
        
        print("A4 kağıdı aranıyor...")
        
        koseler = self.beyaz_kagit_bul(goruntu)
        
        if koseler is not None:
            print("A4 kağıt bulundu!")
            return self.perspektif_donustur(goruntu, koseler)
        
        print("Kenar tespiti deneniyor...")
        koseler = self.kenar_ile_dikdortgen_bul(goruntu)
        
        if koseler is not None:
            print("Dikdörtgen bulundu!")
            return self.perspektif_donustur(goruntu, koseler)
        
        print("A4 bulunamadı, orijinal boyutlandırılıyor...")
        return self.yeniden_boyutlandir(goruntu)
    
    # beyaz kağıdı tespit eder.
    def beyaz_kagit_bul(self, goruntu: np.ndarray) -> Optional[np.ndarray]:
       
        try:
            h, w = goruntu.shape[:2]
            
            # gri tonlamaya çevirir
            gri = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
            
            # gaussian blur uygular
            blur = cv2.GaussianBlur(gri, (5, 5), 0)
            
            # beyaz alanları tespit eder 
            # threshold değerini düşük tutarak beyaz kağıdı yakalar
            _, beyaz_maske = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
            
            # alternatif: adaptif threshold komşulara bakarak işlem yapar daha hassastır
            adaptif = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
            
            # maskeleri birleştirir
            kombine = cv2.bitwise_and(beyaz_maske, adaptif)
            
           
            # kernel boyutu 15x15 lik alanda işlem yapar
            """ morp_open ve morp_close boşlukları ve dış alanları beyaz ve siyaha
              doldurur iterations ise tekrar sayısını tutar 
            """
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
            kombine = cv2.morphologyEx(kombine, cv2.MORPH_CLOSE, kernel, iterations=3)
            kombine = cv2.morphologyEx(kombine, cv2.MORPH_OPEN, kernel, iterations=2)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1a_beyaz_maske.jpg", kombine)
            
            # konturları bul
            konturlar, _ = cv2.findContours(kombine, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not konturlar:
                return None
            
            # en büyük konturu bul
            en_buyuk = max(konturlar, key=cv2.contourArea)
            alan = cv2.contourArea(en_buyuk)
            
            # minimum alan kontrolü görüntünün en az %20'sinde arayarak hata yapmanın önüne geçmeye çalışrı 
            min_alan = h * w * 0.20
            if alan < min_alan:
                return None
            
            # en büyük beyaz alanın kenarlarında düzeltme yapar
            hull = cv2.convexHull(en_buyuk)
            
            # poligon yaklaşımıile 4 köşe bulunur
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
        # hedef boyutlar A4 oranında
        genislik = 1600
        yukseklik = 2264
        
        hedef = np.array([
            [0, 0],
            [genislik - 1, 0],
            [genislik - 1, yukseklik - 1],
            [0, yukseklik - 1]
        ], dtype=np.float32)
        
        # perspektif dönüşüm matrisi
        matris = cv2.getPerspectiveTransform(koseler.astype(np.float32), hedef)
        
        # dönüşümü uygula
        duzeltilmis = cv2.warpPerspective(goruntu, matris, (genislik, yukseklik), 
                                          flags=cv2.INTER_CUBIC)
        
        if self.debug_mode:
            # debug için köşeleri çiz
            debug_img = goruntu.copy()
            for i, kose in enumerate(koseler):
                cv2.circle(debug_img, (int(kose[0]), int(kose[1])), 10, (0, 255, 0), -1)
                cv2.putText(debug_img, str(i), (int(kose[0])+15, int(kose[1])), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imwrite(f"{self.debug_dir}/1c_koseler.jpg", debug_img)
            cv2.imwrite(f"{self.debug_dir}/1d_perspektif_ham.jpg", duzeltilmis)
        
        # perspektif düzeltme sonrası hafif iyileştirme uygula
        duzeltilmis = self.perspektif_sonrasi_iyilestir_hafif(duzeltilmis)
        
        if self.debug_mode:
            cv2.imwrite(f"{self.debug_dir}/1d_perspektif.jpg", duzeltilmis)
        
        return duzeltilmis
    
    
    def perspektif_sonrasi_iyilestir_hafif(self, goruntu: np.ndarray) -> np.ndarray:
        """
        Perspektif düzeltme sonrası hafif iyileştirme
        RENKLİ görüntüyü koruyarak iyileştirme yapar (renk tespiti için kritik)
        """
        # renkli görüntüyü koru - her kanalı ayrı işle
        if len(goruntu.shape) == 3:
            canals = cv2.split(goruntu)
            processed_canals = []
            
            for canal in canals:
                # gürültü azaltma
                denoised = cv2.fastNlMeansDenoising(canal, None, h=7, templateWindowSize=7, searchWindowSize=21)
                
                # hafif keskinleştirme
                gaussian = cv2.GaussianBlur(denoised, (0, 0), 1.5)
                sharpened = cv2.addWeighted(denoised, 1.3, gaussian, -0.3, 0)
                
                processed_canals.append(sharpened)
            
            # kanalları birleştir
            result = cv2.merge(processed_canals)
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/1e_renkli_iyilestirilmis.jpg", result)
        else:
            # gri tonlama için
            denoised = cv2.fastNlMeansDenoising(goruntu, None, h=7, templateWindowSize=7, searchWindowSize=21)
            gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
            sharpened = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)
            result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def yeniden_boyutlandir(self, goruntu: np.ndarray) -> np.ndarray:
        """
        Perspektif bulunamazsa sadece yeniden boyutlandır
        """
        genislik = 1600
        yukseklik = 2264
        resized = cv2.resize(goruntu, (genislik, yukseklik), interpolation=cv2.INTER_CUBIC)
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
            
            # filtreler
            if x > w * 0.35:  # sağ tarafı atla
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
        
        # tekrar eden kutuları kaldır
        unique_boxes = []
        for box in candidates:
            is_duplicate = False
            for existing in unique_boxes:
                # y koordinatı çok yakınsa geç
                y_overlap = (box['y'] < existing['y'] + existing['h'] and 
                            box['y'] + box['h'] > existing['y'])
                
                if y_overlap and abs(box['x'] - existing['x']) < 30:
                    # daha büyük olanı tut
                    if box['area'] > existing['area']:
                        unique_boxes.remove(existing)
                        unique_boxes.append(box)
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_boxes.append(box)
        
        print(f"      Eşsiz Ad/Soyad kutu sayısı: {len(unique_boxes)}")
        
        # boyut ve x koordinatı benzerliğine göre çiftleri bul
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
        
        # cevap kutusu kriterleri
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
            
            # filtreler
            if x < w * 0.25:  # sol tarafı atla
                continue
            if aspect > 0.30:  # çok geniş, cevap kutusu değil
                continue
            if bh < min_box_height:  # çok kısa
                continue
            if bw < min_box_width or bw > max_box_width:
                continue
            
            candidates.append({
                'x': x, 'y': y, 'w': bw, 'h': bh, 'area': area
            })
        
        print(f"      Kutu adayı sayısı: {len(candidates)}")
        for i, box in enumerate(candidates):
            print(f"        Aday {i+1}: x={box['x']}, y={box['y']}, w={box['w']}, h={box['h']}")
        
        # tekrar eden kutuları kaldır
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
        
        print(f"      Eşsiz kutu sayısı: {len(unique_boxes)}")
        
        # X'e göre sırala (soldan sağa: Türkçe, Matematik, Sosyal, Fen)
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
                
                # üstten kırpma yap
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
            
            if self.debug_mode:
                cv2.imwrite(f"{self.debug_dir}/3_tum_bolgeler.jpg", debug_all)
        
        return bolgeler
    
    def cevaplari_oku_renkli(self, bolge_renkli: np.ndarray, soru_sayisi: int = 40, ders_adi: str = "") -> Dict[int, str]:
        cevaplar = {}
        
        if bolge_renkli is None or bolge_renkli.size == 0:
            return {i: 'BOŞ' for i in range(1, soru_sayisi + 1)}
        
        h, w = bolge_renkli.shape[:2]
        
        # gri tonlama
        gri = cv2.cvtColor(bolge_renkli, cv2.COLOR_BGR2GRAY)
        
        # debug görüntüsü
        if self.debug_mode:
            debug_img = bolge_renkli.copy()
        
        # blur
        blurred = cv2.GaussianBlur(gri, (5, 5), 0)
        
        # satır ve daire boyutu
        satir_yuksekligi = h / soru_sayisi
        beklenen_yaricap = int(satir_yuksekligi / 2.5)
        
        # hough circles ile daire tespiti
        min_r = max(8, int(beklenen_yaricap * 0.7))
        max_r = int(beklenen_yaricap * 1.3)
        
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
            print(f"{ders_adi}: HoughCircles bulamadı!")
            return {i: 'BOŞ' for i in range(1, soru_sayisi + 1)}
        
        detected = circles[0]
        print(f"{ders_adi}: {len(detected)} daire tespit edildi (r:{min_r}-{max_r}px)")
        
     
        daire_bilgileri = []
        yaricap_listesi = []
        
        for circle in detected:
            cx, cy, r = float(circle[0]), float(circle[1]), float(circle[2])
            
            # çok küçük daireleri atla
            if r < min_r:
                continue
            
            yaricap_listesi.append(r)
            
            # roi bölge etrafınfa ufak bir kare oluşturur
            x1, y1 = max(0, int(cx - r)), max(0, int(cy - r))
            x2, y2 = min(w, int(cx + r)), min(h, int(cy + r))
            roi = gri[y1:y2, x1:x2]
            
            if roi.size == 0:
                continue
            
            # dairesel maske ile ortalama parlaklık
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
            
            # satır numarası
            satir_no = int(cy / satir_yuksekligi) + 1
            satir_no = max(1, min(soru_sayisi, satir_no))
            
            daire_bilgileri.append({
                'cx': cx, 'cy': cy, 'r': r,
                'avg': avg, 'satir': satir_no
            })
        
        # anormal büyük daireleri filtrelenir
        if len(yaricap_listesi) > 10:
            yaricap_median = float(np.median(yaricap_listesi))
            yaricap_std = float(np.std(yaricap_listesi))
            max_kabul_edilebilir = yaricap_median + (2 * yaricap_std)
            
            onceki_sayi = len(daire_bilgileri)
            daire_bilgileri = [d for d in daire_bilgileri if d['r'] <= max_kabul_edilebilir]
            
            if len(daire_bilgileri) < onceki_sayi:
                print(f"{ders_adi}: {onceki_sayi - len(daire_bilgileri)} büyük daire filtrelendi (r>{max_kabul_edilebilir:.1f})")
        
        
        if self.debug_mode:
            for d in daire_bilgileri:
                renk = (0, 255, 0) if d['avg'] < 150 else (0, 0, 255)
                cv2.circle(debug_img, (int(d['cx']), int(d['cy'])), int(d['r']), renk, 1)
        
        # satırlara gruplanır
        satirlar = {}
        for d in daire_bilgileri:
            s = d['satir']
            if s not in satirlar:
                satirlar[s] = []
            satirlar[s].append(d)
        
        # her satır işlenir
        for satir_no in range(1, soru_sayisi + 1):
            if satir_no not in satirlar or len(satirlar[satir_no]) == 0:
                cevaplar[satir_no] = 'BOŞ'
                continue
            
            daireler = satirlar[satir_no]
            
            # x'e göre sırala (A, B, C, D, E)
            daireler.sort(key=lambda d: d['cx'])
            
            
            secenekler = daireler[:5]
            
            if len(secenekler) == 0:
                cevaplar[satir_no] = 'BOŞ'
                continue
            
            # en koyu olanı bul
            en_koyu = min(secenekler, key=lambda d: d['avg'])
            en_koyu_idx = secenekler.index(en_koyu)
            
            # diğerlerinin ortalaması
            diger_avg = [d['avg'] for d in secenekler if d != en_koyu]
            diger_ortalama = sum(diger_avg) / len(diger_avg) if diger_avg else 255
            
            # en koyu < 150 ve diğerlerinden 20 daha koyu ise işaretli say
            if en_koyu['avg'] < 150 and (diger_ortalama - en_koyu['avg']) > 20:
                cevaplar[satir_no] = self.secenekler[en_koyu_idx]
                if self.debug_mode:
                    cv2.circle(debug_img, (int(en_koyu['cx']), int(en_koyu['cy'])), 
                              int(en_koyu['r']) + 2, (0, 255, 0), 3)
            else:
                cevaplar[satir_no] = 'BOŞ'
        
        # debug kaydet      
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
        
        # gri tonlama
        gri = cv2.cvtColor(bolge_renkli, cv2.COLOR_BGR2GRAY)
        
        # debug görüntüsü
        if self.debug_mode:
            debug_img = bolge_renkli.copy()
        
        # blur
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
            
            
            sutun_no = int(cx / sutun_genisligi)
            satir_no = int(cy / satir_yuksekligi)
            
            
            if sutun_no < 0 or sutun_no >= max_karakter:
                continue
            if satir_no < 0 or satir_no >= satir_sayisi:
                continue
            
            daire_bilgileri.append({
                'cx': cx, 'cy': cy, 'r': r,
                'avg': avg, 'sutun': sutun_no, 'satir': satir_no
            })
        
        # debug çizimi
        if self.debug_mode:
            for d in daire_bilgileri:
                renk = (0, 255, 0) if d['avg'] < 120 else (0, 0, 255)
                cv2.circle(debug_img, (int(d['cx']), int(d['cy'])), int(d['r']), renk, 1)
        
        # sütunlara grupla
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
            
            # en koyu olanı bul
            en_koyu = min(daireler, key=lambda d: d['avg'])
            
            diger = [d['avg'] for d in daireler if d != en_koyu]
            diger_ortalama = sum(diger) / len(diger) if diger else 255
            
            # en koyu < 120 ve diğerlerinden 35+ daha koyu ise işaretli say
            if en_koyu['avg'] < 120 and (diger_ortalama - en_koyu['avg']) > 35:
                harf_idx = en_koyu['satir']
                if 0 <= harf_idx < len(self.alfabe):
                    isim.append((sutun_no, self.alfabe[harf_idx]))
                    
                    if self.debug_mode:
                        cv2.circle(debug_img, (int(en_koyu['cx']), int(en_koyu['cy'])), 
                                  int(en_koyu['r']) + 2, (0, 255, 0), 3)
        
        # sütun sırasına göre sırala
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


