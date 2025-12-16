"""
Basit Daire Tespiti Testi
Tek bir bölge görüntüsü üzerinde HoughCircles testİ
"""
import cv2
import numpy as np

# Türkçe bölgesini yükle
img = cv2.imread("debug_images/bolge_turkce.jpg")
if img is None:
    print("Görüntü yüklenemedi!")
    exit()

print(f"Görüntü boyutu: {img.shape[1]}x{img.shape[0]}")

# Gri tonlama
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Blur
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

h, w = gray.shape

# Beklenen daire boyutu
soru_sayisi = 40
satir_yuksekligi = h / soru_sayisi
beklenen_yaricap = int(satir_yuksekligi / 2.5)

print(f"Satır yüksekliği: {satir_yuksekligi:.1f}px")
print(f"Beklenen yarıçap: {beklenen_yaricap}px")

# Farklı parametrelerle deneyelim
print("\n--- HoughCircles Testleri ---")

# Test 1: Orijinal parametreler
circles1 = cv2.HoughCircles(
    blurred, cv2.HOUGH_GRADIENT, dp=1.2,
    minDist=beklenen_yaricap * 2,
    param1=50, param2=30,
    minRadius=max(beklenen_yaricap - 5, 3),
    maxRadius=beklenen_yaricap + 10
)
print(f"Test 1 (dp=1.2, p2=30): {len(circles1[0]) if circles1 is not None else 0} daire")

# Test 2: Daha düşük param2
circles2 = cv2.HoughCircles(
    blurred, cv2.HOUGH_GRADIENT, dp=1.2,
    minDist=beklenen_yaricap * 2,
    param1=50, param2=20,
    minRadius=max(beklenen_yaricap - 5, 3),
    maxRadius=beklenen_yaricap + 10
)
print(f"Test 2 (dp=1.2, p2=20): {len(circles2[0]) if circles2 is not None else 0} daire")

# Test 3: dp=1
circles3 = cv2.HoughCircles(
    blurred, cv2.HOUGH_GRADIENT, dp=1,
    minDist=beklenen_yaricap * 2,
    param1=50, param2=25,
    minRadius=max(beklenen_yaricap - 5, 3),
    maxRadius=beklenen_yaricap + 10
)
print(f"Test 3 (dp=1, p2=25): {len(circles3[0]) if circles3 is not None else 0} daire")

# Test 4: Daha geniş yarıçap aralığı
circles4 = cv2.HoughCircles(
    blurred, cv2.HOUGH_GRADIENT, dp=1,
    minDist=beklenen_yaricap,
    param1=50, param2=20,
    minRadius=3,
    maxRadius=beklenen_yaricap + 15
)
print(f"Test 4 (geniş radius, p2=20): {len(circles4[0]) if circles4 is not None else 0} daire")

# En iyi sonucu görselleştir
best_circles = circles4 if circles4 is not None else circles2
if best_circles is not None:
    output = img.copy()
    detected = best_circles[0]
    
    print(f"\n--- Daire Analizi ({len(detected)} daire) ---")
    
    # Her daire için parlaklık hesapla
    brightness_list = []
    for circle in detected:
        cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2])
        
        # ROI
        x1, y1 = max(0, cx - r), max(0, cy - r)
        x2, y2 = min(w, cx + r), min(h, cy + r)
        roi = gray[y1:y2, x1:x2]
        
        if roi.size > 0:
            # Dairesel maske
            mask = np.zeros(roi.shape, dtype=np.uint8)
            mcx, mcy = roi.shape[1] // 2, roi.shape[0] // 2
            mr = min(mcx, mcy)
            cv2.circle(mask, (mcx, mcy), mr, 255, -1)
            
            pixels = roi[mask == 255]
            if len(pixels) > 0:
                avg = np.mean(pixels)
                brightness_list.append((cx, cy, r, avg))
                
                # Renk: koyu = yeşil (dolu), açık = kırmızı (boş)
                if avg < 120:
                    color = (0, 255, 0)  # Dolu
                else:
                    color = (0, 0, 255)  # Boş
                
                cv2.circle(output, (cx, cy), r, color, 2)
    
    # Parlaklık dağılımı
    brightness_list.sort(key=lambda x: x[3])
    print(f"En koyu 5 daire (muhtemelen dolu):")
    for i, (cx, cy, r, avg) in enumerate(brightness_list[:5]):
        satir = int(cy / satir_yuksekligi) + 1
        print(f"  {i+1}. satır={satir}, avg={avg:.0f}")
    
    print(f"\nEn açık 5 daire (muhtemelen boş):")
    for i, (cx, cy, r, avg) in enumerate(brightness_list[-5:]):
        satir = int(cy / satir_yuksekligi) + 1
        print(f"  {i+1}. satır={satir}, avg={avg:.0f}")
    
    # Dolu sayısı
    dolu_sayisi = sum(1 for _, _, _, avg in brightness_list if avg < 120)
    print(f"\nDolu daire sayısı (avg < 120): {dolu_sayisi}")
    
    cv2.imwrite("debug_images/test_circles.jpg", output)
    print("\n✅ Sonuç: debug_images/test_circles.jpg")
else:
    print("❌ Hiç daire bulunamadı!")
