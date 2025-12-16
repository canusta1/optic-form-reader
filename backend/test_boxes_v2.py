"""
Perspektif Düzeltilmiş Görüntüde Kutu Tespiti
"""
import cv2
import numpy as np

# Perspektif düzeltilmiş görüntüyü yükle
img = cv2.imread("debug_images/1_duzeltilmis.jpg")
if img is None:
    print("Perspektif düzeltilmiş görüntü bulunamadı!")
    exit()

h, w = img.shape[:2]
print(f"Görüntü boyutu: {w}x{h}")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (3, 3), 0)

# Adaptive threshold - çizgileri bulmak için
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 15, 5)
cv2.imwrite("debug_images/thresh.jpg", thresh)

# Canny
edges = cv2.Canny(blurred, 50, 150)
cv2.imwrite("debug_images/edges2.jpg", edges)

# Kontur bul
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print(f"Toplam kontur: {len(contours)}")

# Dikdörtgen filtrele
output = img.copy()
rectangles = []

for i, cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area < 1000:  # Çok küçük
        continue
    
    # Dikdörtgen yaklaşımı
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    
    x, y, bw, bh = cv2.boundingRect(cnt)
    
    # Boyut filtreleri
    if bw < 30 or bh < 100:  # Çok küçük
        continue
    
    aspect = bw / bh
    
    rectangles.append({
        'x': x, 'y': y, 'w': bw, 'h': bh,
        'area': area, 'aspect': aspect,
        'corners': len(approx)
    })

# Alan'a göre sırala
rectangles.sort(key=lambda r: r['area'], reverse=True)

print(f"\nEn büyük 15 dikdörtgen:")
for i, r in enumerate(rectangles[:15]):
    print(f"  {i+1}. x={r['x']:3d}, y={r['y']:3d}, w={r['w']:3d}, h={r['h']:3d}, "
          f"aspect={r['aspect']:.2f}, corners={r['corners']}")
    
    if i < 10:
        color = (0, 255, 0) if r['aspect'] < 0.4 else (0, 0, 255)
        cv2.rectangle(output, (r['x'], r['y']), (r['x']+r['w'], r['y']+r['h']), color, 2)
        cv2.putText(output, f"{i+1}", (r['x']+2, r['y']+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

cv2.imwrite("debug_images/rects_found.jpg", output)
print("\n✅ debug_images/rects_found.jpg")

# Dikey dikdörtgenleri filtrele (cevap kutuları)
print("\n--- Dikey Dikdörtgenler (aspect < 0.35, h > %30) ---")
vertical = [r for r in rectangles if r['aspect'] < 0.35 and r['h'] > h * 0.3]

for i, r in enumerate(vertical):
    print(f"  {i+1}. x={r['x']}, y={r['y']}, w={r['w']}, h={r['h']}")

# Yan yana 4 kutu bul
if len(vertical) >= 4:
    # Y pozisyonu benzer olanları grupla
    vertical.sort(key=lambda r: r['x'])  # X'e göre sırala
    
    # İlk 4'ü al
    boxes = vertical[:4]
    
    output2 = img.copy()
    ders_isimleri = ['Turkce', 'Mat', 'Fen', 'Sosyal']
    colors = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)]
    
    for i, box in enumerate(boxes):
        color = colors[i % 4]
        cv2.rectangle(output2, (box['x'], box['y']), 
                      (box['x']+box['w'], box['y']+box['h']), color, 3)
        cv2.putText(output2, ders_isimleri[i], (box['x'], box['y']-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    cv2.imwrite("debug_images/4_boxes.jpg", output2)
    print(f"\n✅ 4 kutu bulundu: debug_images/4_boxes.jpg")
else:
    print(f"\n⚠️ Sadece {len(vertical)} dikey dikdörtgen bulundu")
