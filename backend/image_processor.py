import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional

class OpticalFormReader:
    """
    OpenCV kullanarak optik form okuma sınıfı
    """
    
    def __init__(self):
        # OMR BUBBLE PARAMETRELERİ - LGS FORMU İÇİN OPTİMİZE EDİLDİ
        # LGS formundaki YUVARLAK kutucuklar - SADECE GERÇEKTEKİ OMR BUBBLES!
        # GERÇEK LGS formunda bubbles uniform boyutta
        self.min_bubble_area = 40         # Minimum alan - biraz daha düşük
        self.max_bubble_area = 300        # Maximum alan - biraz daha geniş
        self.threshold_value = 180        # Sabit threshold (uygun)
        self.filled_threshold = 0.65      # DEPRECATED - adaptive fill kullanılıyor
        
        # Yeni parametreler - SADECE YUVARLAK OMR BUBBLES için OPTİMİZE
        self.min_circularity = 0.70       # Dairesellik eşiği - YÜKSEK ama gerçekçi
        self.aspect_ratio_range = (0.7, 1.4)  # En-boy oranı - DAR ama esnek
        self.grid_tolerance = 20          # Satır/sütun gruplama toleransı
        self.min_fill_ratio = 0.35        # İçi dolu kabul etme eşiği (35% beyaz piksel)
    
    def preprocess_image(self, image):
        """
        OMR için optimize edilmiş görüntü ön işleme
        
        CRITICAL FIX: Uses ADAPTIVE THRESHOLD with BINARY_INV
        - Black background (paper) → 0
        - White foreground (bubbles/marks) → 255
        
        Değişiklikler:
        1. Contrast artırma (CLAHE) - Zayıf ışıkta bile bubble'ları görür
        2. Daha büyük GaussianBlur (7,7) - Gürültüyü daha iyi temizler
        3. Bilateral filter - Kenarları koruyarak gürültü temizler
        4. Adaptive threshold with BINARY_INV - Varyasyonlu ışıklandırmada çalışır
        5. Daha büyük morfolojik kernel - Küçük kesikleri kapatır
        """
        print("\n🔧 PREPROCESSING IMAGE:")
        
        # 1. Gri tonlamaya çevir
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print(f"   Step 1: Converted to grayscale - shape: {gray.shape}")
        
        # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # Kontrastı artırarak zayıf ışıkta bile bubble'ları belirginleştirir
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        print(f"   Step 2: CLAHE applied - intensity range: [{gray.min()}, {gray.max()}]")
        
        # 3. Bilateral filter - LGS KÜÇÜK KUTUCUKLAR İÇİN HAFİFLETİLDİ
        # Daha küçük kernel: Küçük detayları korur
        denoised = cv2.bilateralFilter(gray, 5, 50, 50)  # Was 9, 75, 75
        print(f"   Step 3: Bilateral filter applied (gentle, preserves small details)")
        
        # 4. GaussianBlur - LGS İÇİN HAFİF
        # (5,5) kernel: Küçük kutucukları bulanıklaştırmamak için (was 7,7)
        blurred = cv2.GaussianBlur(denoised, (5, 5), 0)
        print(f"   Step 4: Gaussian blur applied (5x5, preserves tiny bubbles)")
        
        # 5. CRITICAL: Adaptive threshold with BINARY_INV - LGS FORMU İÇİN
        # blockSize=11: Küçük kutucuklar için daha küçük pencere (was 21)
        # C=8: Daha hassas threshold (was 10)
        # THRESH_BINARY_INV: Inverts result so WHITE paper → BLACK background
        #                     and DARK marks/bubbles → WHITE foreground
        print(f"   Step 5: Applying adaptive threshold (LGS optimized)...")
        print(f"           - blockSize: 11 (smaller windows for tiny bubbles)")
        print(f"           - C: 8 (sensitive threshold for small marks)")
        print(f"           - Mode: THRESH_BINARY_INV (white paper → black bg)")
        
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 8
        )
        
        # Check result
        white_pixels = cv2.countNonZero(thresh)
        total_pixels = thresh.size
        white_ratio = white_pixels / total_pixels
        print(f"   Result: {white_pixels}/{total_pixels} white pixels ({white_ratio:.1%})")
        
        if white_ratio > 0.5:
            print(f"   ⚠️  WARNING: >50% white pixels! Image might NOT be inverted properly")
            print(f"   Expected: Black background (paper) with white bubbles (marks)")
        else:
            print(f"   ✓ Good: <50% white pixels (bubbles/marks on black background)")
        
        # 6-7. MORFOLOJİK İŞLEMLER KALDIRILDI!
        # SEBEP: LGS formundaki küçük ve yoğun bubble'lar birbirine çok yakın
        #        CLOSE işlemi bubble'ları birleştiriyor → tek dev kontür oluşuyor
        #        OPEN işlemi küçük bubble'ları tamamen siliyor
        # ÇÖZÜM: Morfolojik işlem YAPMA, doğrudan threshold çıktısını kullan
        print(f"   Step 6-7: Morphological operations SKIPPED (preserves tiny, dense bubbles)")
        
        print(f"✅ Preprocessing complete\n")
        return thresh
    
    def find_form_contours(self, image):
        """
        OMR bubble kontürlerini bul
        
        Değişiklikler:
        1. Daha büyük kernel (5,5) - Bubble içindeki boşlukları kapat
        2. RETR_TREE yerine RETR_EXTERNAL - Sadece dış kontürler (daha hızlı)
        3. CHAIN_APPROX_SIMPLE - Bellek tasarrufu
        
        CONTOUR DETECTION STRATEGY:
        - RETR_EXTERNAL: We only need outer contours of bubbles. Using RETR_TREE
          or RETR_CCOMP would give us nested hierarchies (e.g., filled bubbles with
          inner contours), which is unnecessary and slower.
        - CHAIN_APPROX_SIMPLE: Compresses contour points (e.g., straight lines stored
          as 2 endpoints instead of all pixels). Reduces memory without losing accuracy.
        """
        # Morfolojik closing: LGS KÜÇÜK KUTUCUKLAR İÇİN OPTİMİZE
        # (3,3) ELLIPSE kernel: Küçük kutucukları birleştirmemek için (was 5,5)
        # iterations=1: Daha hafif işlem (was 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        morphed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # DEBUG: Save morphological result
        cv2.imwrite('debug_morphed.jpg', morphed)
        print("💾 Saved: debug_morphed.jpg (LGS: 3x3 kernel, 1 iteration)")
        
        # Kontürleri bul
        # RETR_EXTERNAL: Sadece en dış kontürler (hız optimizasyonu)
        # CHAIN_APPROX_SIMPLE: Kontür noktalarını sıkıştır (bellek optimizasyonu)
        contours, _ = cv2.findContours(
            morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        return contours
    
    def filter_bubble_contours(self, contours, image_shape):
        """
        OMR bubble'larını filtrele (gelişmiş) - WITH DEBUG OUTPUT
        
        İyileştirmeler:
        1. Dairesellik kontrolü eklendi - Kalem lekeleri elemek için
        2. Solidity kontrolü - İçi boş şekilleri yoksay
        3. Konvexity - Düzensiz şekilleri eleme
        4. Minimum piksel yoğunluğu - Çok küçük nesneleri atla
        
        DEBUG MODE: Prints details of every contour examined
        """
        bubbles = []
        
        # LGS FORMU İÇİN OPTİMİZE EDİLMİŞ PARAMETRELERİ KULLAN
        min_area_debug = self.min_bubble_area  # 20 pixels
        max_area_debug = self.max_bubble_area  # 800 pixels
        
        print(f"\n🔍 FILTERING {len(contours)} CONTOURS (STRICT OMR BUBBLE DETECTION):")
        print(f"   SADECE OMR BUBBLES ARANIR - diğer tüm şekiller reddedilir!")
        print(f"   Area range: {min_area_debug}-{max_area_debug} pixels (UNIFORM bubble size)")
        print(f"   Aspect ratio: {self.aspect_ratio_range} (SQUARE-like)")
        print(f"   Min circularity: {self.min_circularity} (HIGH - circular shapes only!)")
        print(f"   Min solidity: 0.80 (HIGH - solid filled shapes only!)")
        print(f"   Fill detection threshold: {self.min_fill_ratio} (for marked/unmarked)")
        print("=" * 80)
        
        for idx, contour in enumerate(contours, 1):
            # Kontur alanı
            area = cv2.contourArea(contour)
            
            # Konturun etrafına dikdörtgen çiz
            x, y, w, h = cv2.boundingRect(contour)
            
            # En-boy oranı kontrolü (kare/dikdörtgen olmalı)
            aspect_ratio = w / float(h) if h > 0 else 0
            
            # Dairesellik (Circularity) kontrolü
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            # Solidity: Kontur alanı / Konveks gövde alanı
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            # DEBUG: Print details for EVERY contour
            status = "✓ ACCEPTED"
            rejection_reason = ""
            
            # Alan kontrolü (RELAXED)
            if not (min_area_debug < area < max_area_debug):
                status = "✗ REJECTED"
                if area <= min_area_debug:
                    rejection_reason = f"Area too small ({area:.0f} ≤ {min_area_debug})"
                else:
                    rejection_reason = f"Area too large ({area:.0f} ≥ {max_area_debug})"
            # En-boy oranı kontrolü
            elif not (self.aspect_ratio_range[0] < aspect_ratio < self.aspect_ratio_range[1]):
                status = "✗ REJECTED"
                rejection_reason = f"Aspect ratio out of range ({aspect_ratio:.2f})"
            # Dairesellik kontrolü - SADECE YUVARLAKLAR (0.70+ = yuvarlak şekiller)
            elif circularity < self.min_circularity:
                status = "✗ REJECTED"
                rejection_reason = f"Circularity too low ({circularity:.2f} < {self.min_circularity})"
            # Solidity kontrolü - Dolu yuvarlak kutular için SIKI
            elif solidity < 0.80:  # 0.80+ = içi dolu, düzgün şekil
                status = "✗ REJECTED"
                rejection_reason = f"Solidity too low ({solidity:.2f} < 0.80)"
            elif perimeter == 0 or hull_area == 0:
                status = "✗ REJECTED"
                rejection_reason = "Invalid contour (perimeter or hull_area = 0)"
            
            # Print contour details
            print(f"Contour #{idx:3d}: Area={area:6.0f}, Ratio={aspect_ratio:.2f}, "
                  f"Circ={circularity:.2f}, Sol={solidity:.2f} -> {status}")
            if rejection_reason:
                print(f"              {rejection_reason}")
            
            # Add to bubbles if passed all checks
            if status == "✓ ACCEPTED":
                bubbles.append({
                    'contour': contour,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h,
                    'area': area,
                    'center': (x + w // 2, y + h // 2),
                    'circularity': circularity,
                    'solidity': solidity,
                    'aspect_ratio': aspect_ratio,
                    'is_filled': False  # Daha sonra hesaplanacak
                })
        
        print("=" * 80)
        print(f"✅ FINAL RESULT: {len(bubbles)} bubbles accepted out of {len(contours)} contours\n")
        
        return bubbles
    
    def get_bubble_fill_ratio(self, image, bubble):
        """
        Kutucuğun doluluk oranını hesapla (0.0 - 1.0)
        
        KRITIK: Preprocessed image'da BEYAZ = işaretlenmiş alan (BINARY_INV)
                Siyah arka plan + beyaz işaretler
        
        İyileştirmeler:
        1. ROI padding - Kenar etkisini azaltır
        2. ROI ortası kontrolü - Kenar gölgeleri yanlış pozitif vermez
        3. Normalized fill ratio - Karşılaştırma için kullanılabilir
        
        Returns:
            float: Doluluk oranı (0.0 = boş, 1.0 = tamamen dolu)
        """
        x, y, w, h = bubble['x'], bubble['y'], bubble['w'], bubble['h']
        
        # ROI padding: Kenarlardan %15 içeri gir (kenar gölgelerini yoksay)
        padding_x = int(w * 0.15)
        padding_y = int(h * 0.15)
        
        x_start = max(0, x + padding_x)
        y_start = max(0, y + padding_y)
        x_end = min(image.shape[1], x + w - padding_x)
        y_end = min(image.shape[0], y + h - padding_y)
        
        # Kutucuğun ORTASINI al (kenar etkisiz)
        roi = image[y_start:y_end, x_start:x_end]
        
        if roi.size == 0:
            return 0.0
        
        # ROI içindeki BEYAZ piksel sayısı (preprocessed BINARY_INV: white = filled)
        total_pixels = roi.size
        white_pixels = cv2.countNonZero(roi)
        
        # Doldurulma oranı: Beyaz piksel oranı
        fill_ratio = white_pixels / total_pixels
        
        return fill_ratio
    
    def check_if_filled_adaptive(self, image, row_bubbles: List[Dict], bubble_idx: int) -> bool:
        """
        ADAPTIVE fill detection: Kutucuğun işaretli olup olmadığını satır ortalamasına göre belirle
        
        ALGORITHM:
        1. Calculate fill ratio for all bubbles in the row
        2. Compute mean and standard deviation
        3. A bubble is "filled" if its fill ratio is significantly above the mean
        
        This adapts to:
        - Different lighting conditions
        - Different scanning qualities
        - Different marking instruments (pen vs pencil)
        
        Args:
            image: Preprocessed image
            row_bubbles: All bubbles in the current row
            bubble_idx: Index of the bubble to check
        
        Returns:
            bool: True if bubble is marked, False otherwise
        """
        # Calculate fill ratios for all bubbles in the row
        fill_ratios = [self.get_bubble_fill_ratio(image, b) for b in row_bubbles]
        
        if not fill_ratios:
            return False
        
        current_fill = fill_ratios[bubble_idx]
        
        # Calculate statistics
        mean_fill = np.mean(fill_ratios)
        std_fill = np.std(fill_ratios)
        
        # ADAPTIVE THRESHOLD: A bubble is filled if it's significantly above average
        # Use mean + 1.0 * std_dev as threshold (was 1.5 - too strict)
        # This means the bubble must be at least 1.0 standard deviations above the mean
        threshold = mean_fill + (1.0 * std_fill)
        
        # Also require minimum absolute fill ratio (0.35) to avoid false positives
        # This is the CRITICAL parameter - işaretli kutular en az %35 beyaz piksel içermeli
        min_absolute_fill = self.min_fill_ratio  # 0.3 from __init__
        
        is_filled = (current_fill > threshold) and (current_fill > min_absolute_fill)
        
        # Debug output for the row (only once per row)
        if bubble_idx == 0:
            print(f"      Fill stats - Mean: {mean_fill:.3f}, Std: {std_fill:.3f}, Threshold: {threshold:.3f}")
            print(f"      Ratios: {[f'{r:.3f}' for r in fill_ratios]}")
        
        return is_filled
    
    def check_if_filled(self, image, bubble):
        """
        DEPRECATED: Legacy method using hardcoded threshold
        Use check_if_filled_adaptive() instead for better results
        
        Kept for backwards compatibility with older code
        """
        fill_ratio = self.get_bubble_fill_ratio(image, bubble)
        
        # Hardcoded threshold: %65 doluluk = işaretli
        # ⚠️ WARNING: This fails under different lighting conditions!
        return fill_ratio > self.filled_threshold
    
    def group_bubbles_by_row(self, bubbles, tolerance=20):
        """
        Kutucukları satırlara göre grupla - STRICT row-then-column ordering
        
        ALGORITHM:
        1. Sort all bubbles by Y coordinate (top to bottom)
        2. Group bubbles with similar Y values into rows (tolerance-based)
        3. Sort each row by X coordinate (left to right)
        
        Args:
            bubbles: Kutucuk listesi
            tolerance: Y koordinatı toleransı (piksel)
        
        Returns:
            Satırlara göre gruplandırılmış kutucuklar (strict ordering)
        """
        if not bubbles:
            return []
        
        # Phase 1: Sort by Y coordinate (top to bottom) - PRIMARY SORT
        sorted_bubbles = sorted(bubbles, key=lambda b: b['y'])
        
        rows = []
        current_row = [sorted_bubbles[0]]
        current_row_y_avg = sorted_bubbles[0]['y']
        
        for bubble in sorted_bubbles[1:]:
            # Calculate average Y of current row for more stable grouping
            current_row_y_avg = sum(b['y'] for b in current_row) / len(current_row)
            
            # If Y coordinate is within tolerance of current row average, add to row
            if abs(bubble['y'] - current_row_y_avg) <= tolerance:
                current_row.append(bubble)
            else:
                # Phase 2: Sort current row by X coordinate (left to right) - SECONDARY SORT
                current_row.sort(key=lambda b: b['x'])
                rows.append(current_row)
                
                # Start new row
                current_row = [bubble]
                current_row_y_avg = bubble['y']
        
        # Don't forget last row
        if current_row:
            current_row.sort(key=lambda b: b['x'])
            rows.append(current_row)
        
        # Debug output for verification
        print(f"📊 Bubble Grouping Summary:")
        print(f"   Total bubbles: {len(bubbles)}")
        print(f"   Rows detected: {len(rows)}")
        for i, row in enumerate(rows, 1):
            print(f"   Row {i}: {len(row)} bubbles (Y avg: {sum(b['y'] for b in row) / len(row):.1f})")
        
        return rows
    
    def detect_answers(self, image_path: str, expected_questions: int = 20, 
                      options_per_question: int = 5) -> Dict:
        """
        OMR formu oku ve cevapları tespit et
        
        ÖNEMLİ: Perspektif düzeltme otomatik uygulanır!
        
        Args:
            image_path: Görüntü dosya yolu
            expected_questions: Beklenen soru sayısı
            options_per_question: Her soru için seçenek sayısı (A,B,C,D,E = 5)
        
        Returns:
            Dict: Tespit edilen cevaplar ve meta bilgiler
        """
        try:
            # Görüntüyü oku
            image = cv2.imread(image_path)
            if image is None:
                return {'error': 'Görüntü okunamadı'}
            
            original_shape = image.shape
            
            # ÖNEMLİ: İlk önce form köşelerini bul ve perspektif düzelt
            # Timing mark bazlı yöntem öncelikli!
            if isinstance(self, AdvancedFormReader):
                # Önce timing mark bazlı metodu dene
                corners = self.detect_form_corners_with_timing_marks(image)
                
                if corners is not None:
                    print("📐 Form köşeleri bulundu (timing mark bazlı), perspektif düzeltiliyor...")
                    image = self.apply_perspective_transform(image, corners)
                else:
                    print("⚠️ Form köşeleri bulunamadı, orijinal görüntü kullanılıyor")
            
            # Ön işleme (optimize edilmiş OMR preprocessing)
            processed = self.preprocess_image(image)
            
            # DEBUG: Save the INVERTED binary image
            cv2.imwrite('debug_binary_input_fixed.jpg', processed)
            print("💾 Saved: debug_binary_input_fixed.jpg (INVERTED: black bg, white bubbles)")
            print(f"   Image shape: {processed.shape}")
            print(f"   Unique pixel values: {np.unique(processed)}")
            
            # Verify inversion
            white_pixel_count = cv2.countNonZero(processed)
            total_pixels = processed.size
            print(f"   White pixels: {white_pixel_count}/{total_pixels} ({white_pixel_count/total_pixels:.1%})")
            if white_pixel_count / total_pixels > 0.5:
                print("   ⚠️  WARNING: Most pixels are WHITE - inversion may have failed!")
                print("   Expected: Black background (paper) with white foreground (bubbles)")
            else:
                print("   ✓ Looks good: Black background with white objects")
            
            # Kontürleri bul - TÜM kontürleri al (RETR_LIST kullan)
            # RETR_EXTERNAL sadece en dış kontürü buluyor → tüm form 1 kontür
            # RETR_LIST tüm kontürleri buluyor → her bubble ayrı kontür
            contours, _ = cv2.findContours(processed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            print(f"\n🔍 RAW CONTOURS: {len(contours)} contours found (RETR_LIST mode)")
            
            # Kutucukları filtrele
            bubbles = self.filter_bubble_contours(contours, image.shape)
            
            # DEBUG: Draw detected bubbles on original
            debug_bubbles = image.copy()
            for bubble in bubbles:
                x, y, w, h = bubble['x'], bubble['y'], bubble['w'], bubble['h']
                cv2.rectangle(debug_bubbles, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imwrite('debug_bubbles.jpg', debug_bubbles)
            print(f"💾 Saved: debug_bubbles.jpg ({len(bubbles)} bubbles detected)")
            
            if len(bubbles) == 0:
                return {'error': 'Kutucuk bulunamadı. Lütfen daha net bir fotoğraf çekin.'}
            
            # VALIDATE: Check expected bubble count
            expected_bubble_count = expected_questions * options_per_question
            print(f"\n🔍 Bubble Count Validation:")
            print(f"   Expected: {expected_bubble_count} bubbles ({expected_questions} questions × {options_per_question} options)")
            print(f"   Detected: {len(bubbles)} bubbles")
            
            if len(bubbles) < expected_bubble_count:
                print(f"   ⚠️  WARNING: Detected fewer bubbles than expected!")
                print(f"   Missing: {expected_bubble_count - len(bubbles)} bubbles")
                print(f"   Possible causes: Poor image quality, incorrect filtering, occlusion")
            elif len(bubbles) > expected_bubble_count:
                print(f"   ⚠️  WARNING: Detected more bubbles than expected!")
                print(f"   Extra: {len(bubbles) - expected_bubble_count} bubbles")
                print(f"   Possible causes: Dust, text detected as bubbles, loose filtering")
            else:
                print(f"   ✅ Perfect match!")
            
            # Satırlara göre grupla
            rows = self.group_bubbles_by_row(bubbles)
            
            # DEBUG: Visualize row grouping
            debug_rows = image.copy()
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
            for row_idx, row in enumerate(rows):
                color = colors[row_idx % len(colors)]
                for bubble in row:
                    x, y, w, h = bubble['x'], bubble['y'], bubble['w'], bubble['h']
                    cv2.rectangle(debug_rows, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(debug_rows, f"R{row_idx+1}", (x, y-5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            cv2.imwrite('debug_rows.jpg', debug_rows)
            print(f"💾 Saved: debug_rows.jpg (rows color-coded)")
            
            # VALIDATE: Check row count
            if len(rows) != expected_questions:
                print(f"\n⚠️  Row Count Mismatch:")
                print(f"   Expected rows: {expected_questions}")
                print(f"   Detected rows: {len(rows)}")
                print(f"   This may indicate Y-coordinate grouping issues")
            
            # Cevapları tespit et
            answers = {}
            option_letters = ['A', 'B', 'C', 'D', 'E', 'F']
            
            for question_num, row in enumerate(rows, 1):
                if question_num > expected_questions:
                    break
                
                # VALIDATE: Check bubbles per row
                if len(row) != options_per_question:
                    print(f"⚠️  Question {question_num}: Expected {options_per_question} options, found {len(row)}")
                
                # ADAPTIVE FILL DETECTION: Compare each bubble against row average
                # This adapts to different lighting conditions automatically
                print(f"   Q{question_num}:", end="")
                filled_indices = []
                for option_idx, bubble in enumerate(row[:options_per_question]):
                    if self.check_if_filled_adaptive(processed, row[:options_per_question], option_idx):
                        filled_indices.append(option_idx)
                
                # Cevabı belirle
                if len(filled_indices) == 0:
                    answers[question_num] = 'BOŞ'
                    print(f" → BOŞ")
                elif len(filled_indices) == 1:
                    answers[question_num] = option_letters[filled_indices[0]]
                    print(f" → {option_letters[filled_indices[0]]}")
                else:
                    # Birden fazla işaretleme - hata
                    multiple_answers = [option_letters[i] for i in filled_indices]
                    print(f" → HATALI (Multiple: {', '.join(multiple_answers)})")
                    answers[question_num] = 'HATALI'
            
            return {
                'success': True,
                'answers': answers,
                'total_bubbles_found': len(bubbles),
                'rows_found': len(rows),
                'questions_detected': len(answers)
            }
            
        except Exception as e:
            return {'error': f'Görüntü işleme hatası: {str(e)}'}
    
    def detect_student_info(self, image_path: str) -> Dict:
        """
        Öğrenci bilgilerini (ad, numara) optik formdan oku
        Bu basitleştirilmiş bir versiyondur - gerçek uygulamada OCR kullanılabilir
        """
        # Bu kısım için gelişmiş OCR (pytesseract) kullanılabilir
        # Şimdilik basit bir implementasyon
        return {
            'student_name': 'Ad OCR ile okunacak',
            'student_number': 'Numara OCR ile okunacak'
        }
    
    def draw_results(self, image_path: str, answers: Dict, output_path: str):
        """
        Sonuçları görüntü üzerine çiz
        """
        image = cv2.imread(image_path)
        
        # Sonuçları yazdır
        y_offset = 30
        for question, answer in answers.items():
            text = f"S{question}: {answer}"
            cv2.putText(image, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 30
        
        cv2.imwrite(output_path, image)
        return output_path


class AdvancedFormReader(OpticalFormReader):
    """
    Daha gelişmiş form okuma - perspektif düzeltme, form tespiti
    Timing mark bazlı hizalama desteği
    """
    
    def detect_timing_marks(self, image):
        """
        LGS formundaki soldaki dikey timing mark'ları tespit et
        
        Bu timing mark'lar:
        - Formun sol kenarında dikey sırada
        - Siyah dikdörtgen şekiller
        - Form hizalaması için referans noktaları
        
        Returns:
            List[Tuple]: Timing mark merkezlerinin koordinatları [(x,y), ...]
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Threshold: Siyah timing mark'ları beyaz arka plandan ayır
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morfolojik işlem: Küçük gürültüleri temizle
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Kontürleri bul
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        timing_marks = []
        image_height, image_width = image.shape[:2]
        
        # Sol %15'lik bölgede timing mark'ları ara
        left_boundary = int(image_width * 0.15)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Timing mark boyutu kontrolü (100-1000 piksel arası)
            if 100 < area < 1000:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Sol bölgede mi?
                if x < left_boundary:
                    # En/boy oranı kontrolü (dikey dikdörtgen)
                    aspect_ratio = h / float(w) if w > 0 else 0
                    
                    # Dikey dikdörtgen: yükseklik > genişlik (oran > 1.5)
                    if aspect_ratio > 1.5:
                        center_x = x + w // 2
                        center_y = y + h // 2
                        timing_marks.append({
                            'center': (center_x, center_y),
                            'bbox': (x, y, w, h),
                            'area': area
                        })
        
        # Y koordinatına göre sırala (yukarıdan aşağıya)
        timing_marks.sort(key=lambda m: m['center'][1])
        
        print(f"🎯 {len(timing_marks)} timing mark bulundu")
        return timing_marks
    
    def detect_form_corners_with_timing_marks(self, image, debug=False):
        """
        Timing mark'ları kullanarak form köşelerini tespit et
        
        Yöntem:
        1. Soldaki timing mark'ları bul
        2. Timing mark kalitesini kontrol et
        3. Timing mark'ların dikey hizalamasından eğimi hesapla
        4. Form kenarlarını timing mark'lara göre belirle
        5. 4 köşe noktası döndür
        
        Args:
            image: Giriş görüntüsü
            debug: Debug görselleştirme aktif mi?
        
        Returns:
            corners: 4 köşe noktası veya None
        """
        timing_marks = self.detect_timing_marks(image)
        
        if len(timing_marks) < 3:
            print("⚠️ Yeterli timing mark bulunamadı, alternatif metod kullanılıyor")
            return self.detect_form_corners(image)  # Fallback
        
        # Timing mark kalitesini kontrol et
        is_valid, message = self.validate_timing_marks(timing_marks)
        if not is_valid:
            print(f"⚠️ Timing mark kalitesi düşük: {message}")
            print("   Alternatif metod kullanılıyor...")
            return self.detect_form_corners(image)  # Fallback
        
        print(f"✅ Timing mark kalitesi: {message}")
        
        # DEBUG: Always save timing marks visualization
        self.visualize_timing_marks(image, timing_marks, 'debug_timing_marks.jpg')
        print("💾 Saved: debug_timing_marks.jpg")
        
        # Timing mark merkezlerini al
        points = np.array([m['center'] for m in timing_marks])
        
        # En az kareler yöntemi ile doğru fit et (sol kenar)
        # x = m*y + c formülü (y bağımsız değişken çünkü dikey çizgi)
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        
        # Polinom fit (1. derece = doğru)
        coeffs = np.polyfit(y_coords, x_coords, 1)
        m_left, c_left = coeffs  # Eğim ve kesişim
        
        # Eğim açısı (derece cinsinden)
        angle_deg = np.degrees(np.arctan(m_left))
        print(f"📐 Sol kenar eğimi: {angle_deg:.2f}°")
        
        # Çok eğikse uyarı ver
        if abs(angle_deg) > 15:
            print(f"⚠️ Form çok eğik ({angle_deg:.1f}°), düzeltme zor olabilir")
        
        # Form boyutlarını tahmin et
        height, width = image.shape[:2]
        
        # İlk ve son timing mark'tan form sınırlarını belirle
        # Padding: Timing mark'lar formun tam kenarında değil, biraz içerde
        top_padding = 100  # Üst kenara kadar mesafe
        bottom_padding = 100  # Alt kenara kadar mesafe
        
        top_y = max(0, timing_marks[0]['center'][1] - top_padding)
        bottom_y = min(height, timing_marks[-1]['center'][1] + bottom_padding)
        
        # Sol kenardaki x koordinatları (doğru denklemi kullan)
        top_left_x = int(m_left * top_y + c_left)
        bottom_left_x = int(m_left * bottom_y + c_left)
        
        # Form genişliğini tahmin et
        # LGS formu standart A4: en/boy ≈ 1:1.41
        form_height = bottom_y - top_y
        form_width = int(form_height / 1.41)
        
        # Sağ kenar da eğimli olabilir (paralel)
        # Sol kenarla aynı eğimi kullan
        top_right_x = top_left_x + form_width
        bottom_right_x = bottom_left_x + form_width
        
        # 4 köşe noktası
        corners = np.array([
            [top_left_x, top_y],              # Sol-üst
            [top_right_x, top_y],              # Sağ-üst
            [bottom_right_x, bottom_y],        # Sağ-alt
            [bottom_left_x, bottom_y]          # Sol-alt
        ], dtype=np.float32)
        
        print(f"✅ Timing mark bazlı köşeler belirlendi: {form_width}x{form_height}")
        return corners
    
    def detect_form_corners(self, image):
        """
        Kağıt doküman köşelerini tespit et (OMR form sınırları)
        
        ÖNEMLİ DEĞİŞİKLİKLER:
        1. Canny parametreleri (50,150) → (75,200)
           - Neden: Kağıt kenarları düşük kontrastlı, yüksek threshold gerekir
        2. Daha büyük GaussianBlur (5,5) → (7,7)
           - Neden: Kağıt dokusu gürültü yaratır, daha fazla bulanıklık gerekir
        3. Dilation eklendi
           - Neden: Kesik kenarları birleştirir, köşe tespitini iyileştirir
        4. Minimum alan kontrolü
           - Neden: Küçük nesneleri (lekeler, gölgeler) yoksayar
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Daha güçlü blur: Kağıt dokusunu ve gürültüyü temizle
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # Canny edge detection - KAĞIT DOKÜMANI İÇİN OPTİMİZE
        # Threshold1=75 (düşük): Zayıf kenarları yakala
        # Threshold2=200 (yüksek): Güçlü kenarları garantile
        # Oran 1:2.67 - kağıt kenarları için ideal
        edged = cv2.Canny(blurred, 75, 200, apertureSize=3)
        
        # DEBUG: Save edges
        cv2.imwrite('debug_edges.jpg', edged)
        print("💾 Saved: debug_edges.jpg")
        
        # Dilation: Kesik kenarları birleştir
        # Kağıt köşeleri bazen kesik görünür, bu onları kapatır
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edged = cv2.dilate(edged, kernel, iterations=1)
        
        # Kontürleri bul
        contours, _ = cv2.findContours(
            edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # DEBUG: Draw contours on original
        debug_contours = image.copy()
        cv2.drawContours(debug_contours, contours, -1, (0, 255, 0), 2)
        cv2.imwrite('debug_contours.jpg', debug_contours)
        print("💾 Saved: debug_contours.jpg")
        
        if not contours:
            return None
        
        # Konturları alana göre sırala (en büyük = form)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Minimum alan kontrolü: Görüntü alanının en az %10'u olmalı
        image_area = image.shape[0] * image.shape[1]
        min_area = image_area * 0.1
        
        # En büyük konturları kontrol et
        for contour in contours[:5]:  # İlk 5 konturu dene
            area = cv2.contourArea(contour)
            
            # Alan yeterince büyük mü?
            if area < min_area:
                continue
            
            # Kontürü yaklaşık dörtgene dönüştür
            peri = cv2.arcLength(contour, True)
            # epsilon=0.02: Daha esnek (eğik/bozuk formlar için)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # 4 köşeli bir şekil bulduk mu?
            if len(approx) == 4:
                return approx.reshape(4, 2)
        
        return None
    
    def apply_perspective_transform(self, image, corners):
        """
        Perspektif dönüşümü uygula - formu düzelt
        
        Gelişmiş özellikler:
        1. Timing mark bazlı hizalama koruma
        2. Aspect ratio koruması (A4: 1:1.41)
        3. Otomatik padding (kenarlar kesikse)
        """
        # Köşeleri sırala: sol-üst, sağ-üst, sağ-alt, sol-alt
        rect = self.order_points(corners)
        (tl, tr, br, bl) = rect
        
        # Genişlik ve yükseklik hesapla
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))
        
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))
        
        # A4 en/boy oranını koru (opsiyonel düzeltme)
        expected_ratio = 1.41  # A4 oranı
        current_ratio = max_height / max_width if max_width > 0 else 1
        
        # Oran sapması %20'den fazlaysa düzelt
        if abs(current_ratio - expected_ratio) / expected_ratio > 0.2:
            print(f"⚙️ Aspect ratio düzeltiliyor: {current_ratio:.2f} → {expected_ratio:.2f}")
            if current_ratio > expected_ratio:
                # Çok uzun, genişliği artır
                max_width = int(max_height / expected_ratio)
            else:
                # Çok geniş, yüksekliği artır
                max_height = int(max_width * expected_ratio)
        
        # Hedef noktalar (düz dikdörtgen)
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype=np.float32)
        
        # Perspektif dönüşüm matrisi
        M = cv2.getPerspectiveTransform(rect, dst)
        
        # Warp uygula
        warped = cv2.warpPerspective(
            image, M, (max_width, max_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)  # Beyaz padding
        )
        
        # DEBUG: Save warped result
        cv2.imwrite('debug_warped.jpg', warped)
        print("💾 Saved: debug_warped.jpg")
        
        print(f"✅ Perspektif düzeltildi: {warped.shape[1]}x{warped.shape[0]}")
        return warped
    
    def visualize_timing_marks(self, image, timing_marks, output_path='debug_timing_marks.jpg'):
        """
        Debug: Timing mark'ları görselleştir
        """
        debug_img = image.copy()
        
        for i, mark in enumerate(timing_marks):
            cx, cy = mark['center']
            x, y, w, h = mark['bbox']
            
            # Timing mark'ı çerçevele
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Merkezi işaretle
            cv2.circle(debug_img, (cx, cy), 5, (0, 0, 255), -1)
            
            # Numara yaz
            cv2.putText(debug_img, str(i+1), (x-20, cy), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Doğru fit et (varsa)
        if len(timing_marks) >= 2:
            points = np.array([m['center'] for m in timing_marks])
            y_coords = points[:, 1]
            x_coords = points[:, 0]
            
            coeffs = np.polyfit(y_coords, x_coords, 1)
            m, c = coeffs
            
            # Doğruyu çiz
            y1, y2 = int(y_coords.min()), int(y_coords.max())
            x1 = int(m * y1 + c)
            x2 = int(m * y2 + c)
            cv2.line(debug_img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        
        cv2.imwrite(output_path, debug_img)
        print(f"🎨 Debug görsel kaydedildi: {output_path}")
        
        return debug_img
    
    def validate_timing_marks(self, timing_marks):
        """
        Timing mark'ların kalitesini kontrol et
        
        Returns:
            bool: Timing mark'lar geçerli mi?
            str: Hata mesajı (varsa)
        """
        if len(timing_marks) < 3:
            return False, f"Yetersiz timing mark: {len(timing_marks)}<3"
        
        # Y koordinatlarının düzenli aralıklı olup olmadığını kontrol et
        y_coords = [m['center'][1] for m in timing_marks]
        
        if len(y_coords) >= 2:
            # Ardışık timing mark'lar arası mesafeler
            distances = [y_coords[i+1] - y_coords[i] for i in range(len(y_coords)-1)]
            avg_distance = np.mean(distances)
            std_distance = np.std(distances)
            
            # Standart sapma ortalamadan %30'dan fazla farklıysa sorunlu
            if std_distance > avg_distance * 0.3:
                return False, f"Düzensiz aralık: std={std_distance:.1f}, avg={avg_distance:.1f}"
        
        # X koordinatlarının yaklaşık aynı hizada olup olmadığını kontrol et
        x_coords = [m['center'][0] for m in timing_marks]
        x_std = np.std(x_coords)
        
        # X sapması 20 pikselden fazlaysa çok eğik
        if x_std > 20:
            return False, f"Çok eğik: x_std={x_std:.1f}>20"
        
        return True, "OK"
    
    def order_points(self, pts):
        """
        Noktaları sırala: sol-üst, sağ-üst, sağ-alt, sol-alt
        """
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # Toplamları ve farklarını hesapla
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        
        rect[0] = pts[np.argmin(s)]      # Sol-üst
        rect[2] = pts[np.argmax(s)]      # Sağ-alt
        rect[1] = pts[np.argmin(diff)]   # Sağ-üst
        rect[3] = pts[np.argmax(diff)]   # Sol-alt
        
        return rect
