#!/usr/bin/env python3
"""Fen debug görüntüsündeki daireleri analiz et"""

import cv2
import numpy as np

# Fen debug görüntüsünü yükle
img = cv2.imread('debug_images/circles_fen.jpg')
if img is None:
    print("circles_fen.jpg bulunamadı!")
    exit(1)

h, w = img.shape[:2]
print(f"Görüntü boyutu: {w}x{h}")

# Yeşil daireleri bul (işaretli cevaplar)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# Yeşil renk aralığı
lower_green = np.array([40, 50, 50])
upper_green = np.array([80, 255, 255])
green_mask = cv2.inRange(hsv, lower_green, upper_green)

# Konturları bul
contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"\n✅ {len(contours)} yeşil işaretli daire bulundu\n")

# Satır yüksekliği (40 soru)
satir_yuksekligi = h / 40

# Her konturu analiz et
green_circles = []
for cnt in contours:
    M = cv2.moments(cnt)
    if M['m00'] == 0:
        continue
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    
    # Satır numarası hesapla
    satir_no = int(cy / satir_yuksekligi) + 1
    satir_no = max(1, min(40, satir_no))
    
    green_circles.append({'cx': cx, 'cy': cy, 'satir': satir_no})

# Satıra göre sırala
green_circles.sort(key=lambda c: c['satir'])

print("Satır | Y Pozisyon | X Pozisyon | Şık")
print("-" * 50)

for i, circle in enumerate(green_circles[:10], 1):
    # X pozisyonuna göre şık belirle (kabaca)
    # Form genişliğini 5 şıkka böl
    siklar = ['A', 'B', 'C', 'D', 'E']
    sik_genislik = w / 5
    sik_idx = int(circle['cx'] / sik_genislik)
    sik_idx = max(0, min(4, sik_idx))
    sik = siklar[sik_idx]
    
    print(f"  {circle['satir']:2d}  |   {circle['cy']:4d}     |   {circle['cx']:4d}    |  {sik}")

print(f"\n📊 İlk satır Y pozisyonu: {green_circles[0]['cy']}")
print(f"📊 Satır yüksekliği: {satir_yuksekligi:.1f}px")
print(f"📊 İlk satır teorik Y: 0-{satir_yuksekligi:.1f}px")
