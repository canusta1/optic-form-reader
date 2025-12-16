"""
Otomatik Kutu Tespiti Testi
Form üzerindeki 4 ders kutusunu otomatik bul
"""
import cv2
import numpy as np

# Perspektif düzeltilmiş görüntüyü yükle
img = cv2.imread("debug_images/1_duzeltilmis.jpg")
if img is None:
    img = cv2.imread("debug_images/0_orijinal.jpg")
    
if img is None:
    print("Görüntü bulunamadı!")
    exit()

print(f"Görüntü boyutu: {img.shape[1]}x{img.shape[0]}")

# Gri tonlama
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Kenar tespiti
edges = cv2.Canny(gray, 50, 150)

# Morfolojik işlem - kenarları birleştir
kernel = np.ones((3, 3), np.uint8)
edges = cv2.dilate(edges, kernel, iterations=2)
edges = cv2.erode(edges, kernel, iterations=1)

# Kontur bul
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

print(f"Toplam kontur: {len(contours)}")

# Büyük dikdörtgenleri filtrele
h, w = img.shape[:2]
min_area = (h * w) * 0.01  # Görüntünün en az %1'i
max_area = (h * w) * 0.20  # Görüntünün en fazla %20'si

rectangles = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < min_area or area > max_area:
        continue
    
    # Dikdörtgen yaklaşımı
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    
    # 4 köşeli mi?
    if len(approx) == 4:
        x, y, bw, bh = cv2.boundingRect(approx)
        aspect_ratio = bw / bh
        
        # Dikey dikdörtgen (yükseklik > genişlik)
        if 0.1 < aspect_ratio < 0.5 and bh > h * 0.3:
            rectangles.append({
                'x': x, 'y': y, 'w': bw, 'h': bh,
                'area': area, 'contour': cnt
            })
            print(f"  Kutu bulundu: x={x}, y={y}, w={bw}, h={bh}, aspect={aspect_ratio:.2f}")

print(f"\nDikey dikdörtgen sayısı: {len(rectangles)}")

# Görselleştir
output = img.copy()
for i, rect in enumerate(rectangles):
    color = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)][i % 4]
    cv2.rectangle(output, (rect['x'], rect['y']), 
                  (rect['x']+rect['w'], rect['y']+rect['h']), color, 3)
    cv2.putText(output, f"Kutu {i+1}", (rect['x'], rect['y']-10),
               cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

cv2.imwrite("debug_images/kutu_tespiti.jpg", output)
print("\n✅ Sonuç: debug_images/kutu_tespiti.jpg")

# Alternatif: Threshold ile kutu tespiti
print("\n--- Alternatif Yöntem: Adaptive Threshold ---")
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 11, 2)

# Yatay ve dikey çizgileri bul
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

# Çizgileri birleştir
grid = cv2.add(horizontal_lines, vertical_lines)
cv2.imwrite("debug_images/grid_lines.jpg", grid)
print("✅ Çizgiler: debug_images/grid_lines.jpg")
