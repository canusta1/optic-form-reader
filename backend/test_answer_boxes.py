"""
Doğru 4 Cevap Kutusunu Bul
"""
import cv2
import numpy as np

img = cv2.imread("debug_images/1_duzeltilmis.jpg")
if img is None:
    print("Görüntü bulunamadı!")
    exit()

h, w = img.shape[:2]
print(f"Görüntü boyutu: {w}x{h}")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (3, 3), 0)

thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 15, 5)

contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Cevap kutusu kriterleri:
# 1. Sağ tarafta (x > w * 0.25)
# 2. Dikey (aspect < 0.25)
# 3. Yükseklik > %50
# 4. Benzer boyutlarda 4 tane

answer_boxes = []

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 5000:
        continue
    
    x, y, bw, bh = cv2.boundingRect(cnt)
    aspect = bw / bh
    
    # Filtreler
    if x < w * 0.25:  # Sol tarafı atla (Ad/Soyad)
        continue
    if aspect > 0.2:  # Çok geniş
        continue
    if bh < h * 0.5:  # Çok kısa
        continue
    if bw < 80 or bw > 150:  # Çok dar veya çok geniş
        continue
    
    answer_boxes.append({
        'x': x, 'y': y, 'w': bw, 'h': bh, 'area': area
    })

# Duplicate'ları kaldır (benzer koordinatlı olanları)
unique_boxes = []
for box in answer_boxes:
    is_duplicate = False
    for existing in unique_boxes:
        if abs(box['x'] - existing['x']) < 20 and abs(box['y'] - existing['y']) < 20:
            is_duplicate = True
            break
    if not is_duplicate:
        unique_boxes.append(box)

# X'e göre sırala
unique_boxes.sort(key=lambda b: b['x'])

print(f"\nBulunan cevap kutuları: {len(unique_boxes)}")
for i, box in enumerate(unique_boxes):
    print(f"  {i+1}. x={box['x']}, y={box['y']}, w={box['w']}, h={box['h']}")

# Görselleştir
output = img.copy()
ders_isimleri = ['Türkçe', 'Matematik', 'Fen', 'Sosyal']
colors = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)]

for i, box in enumerate(unique_boxes[:4]):
    color = colors[i % 4]
    cv2.rectangle(output, (box['x'], box['y']), 
                  (box['x']+box['w'], box['y']+box['h']), color, 3)
    ders = ders_isimleri[i] if i < len(ders_isimleri) else f"Box {i+1}"
    cv2.putText(output, ders, (box['x'], box['y']-5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

cv2.imwrite("debug_images/answer_boxes.jpg", output)
print(f"\n✅ debug_images/answer_boxes.jpg")

# Her kutuyu ayrı kaydet
for i, box in enumerate(unique_boxes[:4]):
    ders = ders_isimleri[i].lower().replace('ü', 'u').replace('ı', 'i')
    roi = img[box['y']:box['y']+box['h'], box['x']:box['x']+box['w']]
    cv2.imwrite(f"debug_images/box_{ders}.jpg", roi)
    print(f"  💾 debug_images/box_{ders}.jpg ({roi.shape[1]}x{roi.shape[0]})")
