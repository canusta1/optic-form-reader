"""
Akıllı Kutu Tespiti - 4 Ders Kutusunu Otomatik Bul
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple

def find_answer_boxes(img: np.ndarray) -> List[Dict]:
    """
    Form üzerindeki 4 cevap kutusunu otomatik tespit et
    Türkçe, Matematik, Fen, Sosyal sırasıyla
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Blur ve threshold
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Otsu threshold
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morfolojik işlem - küçük gürültüleri temizle
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Kontur bul
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Büyük dikdörtgenleri filtrele
    # Ders kutuları: yaklaşık görüntünün %5-15 arası alan kaplar
    min_area = (h * w) * 0.02
    max_area = (h * w) * 0.15
    
    # Beklenen boyut: Yükseklik görüntünün %40-60'ı, genişlik %5-15'i
    min_height = h * 0.35
    max_height = h * 0.65
    min_width = w * 0.04
    max_width = w * 0.18
    
    candidates = []
    
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < min_area or area > max_area:
            continue
        
        x, y, bw, bh = cv2.boundingRect(cnt)
        
        # Boyut kontrolü
        if not (min_height < bh < max_height and min_width < bw < max_width):
            continue
        
        # Aspect ratio: dikey dikdörtgen (0.1 - 0.4)
        aspect = bw / bh
        if not (0.1 < aspect < 0.45):
            continue
        
        # Form'un sağ yarısında olmalı (cevap kutuları sağda)
        if x < w * 0.25:
            continue
        
        candidates.append({
            'x': x, 'y': y, 'w': bw, 'h': bh,
            'cx': x + bw/2, 'cy': y + bh/2,
            'area': area
        })
    
    print(f"  Aday kutu sayısı: {len(candidates)}")
    
    if len(candidates) < 4:
        print("  ⚠️ Yeterli kutu bulunamadı!")
        return []
    
    # Benzer Y pozisyonundaki kutuları grupla (aynı satırda olanlar)
    # Y merkezi benzer olanları bul
    candidates.sort(key=lambda c: c['cy'])
    
    # En büyük Y grubunu bul
    y_tolerance = h * 0.1
    groups = []
    used = set()
    
    for i, c1 in enumerate(candidates):
        if i in used:
            continue
        group = [c1]
        used.add(i)
        
        for j, c2 in enumerate(candidates):
            if j in used:
                continue
            if abs(c1['cy'] - c2['cy']) < y_tolerance:
                group.append(c2)
                used.add(j)
        
        if len(group) >= 3:  # En az 3 kutu yan yana
            groups.append(group)
    
    if not groups:
        print("  ⚠️ Yan yana kutu grubu bulunamadı!")
        return []
    
    # En çok kutu içeren grubu al
    best_group = max(groups, key=len)
    print(f"  En iyi grup: {len(best_group)} kutu")
    
    # X'e göre sırala (soldan sağa: Türkçe, Matematik, Fen, Sosyal)
    best_group.sort(key=lambda c: c['x'])
    
    # İlk 4'ü al
    answer_boxes = best_group[:4]
    
    return answer_boxes


# Test
img = cv2.imread("debug_images/0_orijinal.jpg")
if img is None:
    print("Görüntü bulunamadı!")
    exit()

print(f"Görüntü boyutu: {img.shape[1]}x{img.shape[0]}")

boxes = find_answer_boxes(img)

# Görselleştir
output = img.copy()
ders_isimleri = ['Türkçe', 'Matematik', 'Fen', 'Sosyal']
colors = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)]

for i, box in enumerate(boxes):
    color = colors[i % 4]
    cv2.rectangle(output, (box['x'], box['y']), 
                  (box['x']+box['w'], box['y']+box['h']), color, 4)
    
    ders = ders_isimleri[i] if i < len(ders_isimleri) else f"Kutu {i+1}"
    cv2.putText(output, ders, (box['x'], box['y']-15),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
    
    print(f"  {ders}: x={box['x']}, y={box['y']}, w={box['w']}, h={box['h']}")

cv2.imwrite("debug_images/auto_boxes.jpg", output)
print(f"\n✅ {len(boxes)} kutu bulundu")
print("✅ Sonuç: debug_images/auto_boxes.jpg")

# Her kutunun içini ayrı kaydet
for i, box in enumerate(boxes):
    ders = ders_isimleri[i] if i < len(ders_isimleri) else f"kutu_{i}"
    roi = img[box['y']:box['y']+box['h'], box['x']:box['x']+box['w']]
    cv2.imwrite(f"debug_images/auto_{ders.lower()}.jpg", roi)
    print(f"  💾 debug_images/auto_{ders.lower()}.jpg")
