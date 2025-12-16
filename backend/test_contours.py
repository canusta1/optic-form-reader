"""
Akıllı Kutu Tespiti - Debug Versiyonu
"""
import cv2
import numpy as np

img = cv2.imread("debug_images/0_orijinal.jpg")
if img is None:
    print("Görüntü bulunamadı!")
    exit()

h, w = img.shape[:2]
print(f"Görüntü boyutu: {w}x{h}")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Canny edge detection
edges = cv2.Canny(blurred, 30, 100)
cv2.imwrite("debug_images/edges.jpg", edges)

# Dilate to connect edges
kernel = np.ones((5, 5), np.uint8)
edges_dilated = cv2.dilate(edges, kernel, iterations=2)
cv2.imwrite("debug_images/edges_dilated.jpg", edges_dilated)

# Kontur bul
contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Toplam kontur: {len(contours)}")

# Tüm büyük konturları çiz
output = img.copy()
big_contours = []

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 10000:  # Çok küçükleri atla
        continue
    
    x, y, bw, bh = cv2.boundingRect(cnt)
    
    big_contours.append({
        'x': x, 'y': y, 'w': bw, 'h': bh,
        'area': area,
        'aspect': bw/bh if bh > 0 else 0
    })

# Alan'a göre sırala
big_contours.sort(key=lambda c: c['area'], reverse=True)

print(f"\nEn büyük 20 kontur:")
for i, c in enumerate(big_contours[:20]):
    print(f"  {i+1}. area={c['area']:.0f}, x={c['x']}, y={c['y']}, w={c['w']}, h={c['h']}, aspect={c['aspect']:.2f}")
    
    # İlk 10'u çiz
    if i < 10:
        color = (0, 255, 0) if i < 4 else (0, 0, 255)
        cv2.rectangle(output, (c['x'], c['y']), (c['x']+c['w'], c['y']+c['h']), color, 3)
        cv2.putText(output, f"{i+1}", (c['x']+5, c['y']+30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

cv2.imwrite("debug_images/all_contours.jpg", output)
print("\n✅ debug_images/all_contours.jpg")

# Şimdi dikey dikdörtgenleri filtrele
print("\n--- Dikey Dikdörtgenler (aspect < 0.5) ---")
vertical_rects = [c for c in big_contours if c['aspect'] < 0.5 and c['h'] > h * 0.2]
print(f"Dikey dikdörtgen sayısı: {len(vertical_rects)}")

for i, c in enumerate(vertical_rects[:10]):
    print(f"  {i+1}. x={c['x']}, y={c['y']}, w={c['w']}, h={c['h']}, aspect={c['aspect']:.2f}")

# Dikey dikdörtgenleri çiz
output2 = img.copy()
for i, c in enumerate(vertical_rects[:10]):
    color = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)][i % 4]
    cv2.rectangle(output2, (c['x'], c['y']), (c['x']+c['w'], c['y']+c['h']), color, 4)

cv2.imwrite("debug_images/vertical_rects.jpg", output2)
print("\n✅ debug_images/vertical_rects.jpg")
