"""
Dolu vs Boş baloncuk analizi
"""
import cv2
import numpy as np

# Turkce bölgesini incele
bolge = cv2.imread('debug_images/bolge_turkce.jpg')
gri = cv2.cvtColor(bolge, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gri, (5, 5), 0)

h, w = bolge.shape[:2]

circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=max(int(w / 10), 5),
    param1=50,
    param2=25,
    minRadius=max(int(w / 15), 3),
    maxRadius=max(int(w / 5), 8)
)

print('Daire analizi - dolu vs boş farkını bul:')
print('='*70)

if circles is not None:
    daireler = []
    for circle in circles[0]:
        cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2])
        
        x1 = max(0, cx - r)
        y1 = max(0, cy - r)
        x2 = min(w, cx + r)
        y2 = min(h, cy + r)
        
        roi = gri[y1:y2, x1:x2]
        
        if roi.size > 0:
            # Daire maskesi ile sadece daire içini al
            maske = np.zeros(roi.shape, dtype=np.uint8)
            cv2.circle(maske, (roi.shape[1]//2, roi.shape[0]//2), r-1, 255, -1)
            daire_pix = roi[maske == 255]
            
            if daire_pix.size > 0:
                daire_avg = np.mean(daire_pix)
                daire_std = np.std(daire_pix)
                daire_min = np.min(daire_pix)
                
                # Koyu piksel oranı (farklı eşiklerle)
                koyu_100 = np.sum(daire_pix < 100) / daire_pix.size
                koyu_120 = np.sum(daire_pix < 120) / daire_pix.size
                koyu_140 = np.sum(daire_pix < 140) / daire_pix.size
                
                daireler.append({
                    'cx': cx, 'cy': cy, 'r': r,
                    'avg': daire_avg, 'std': daire_std, 'min': daire_min,
                    'koyu_100': koyu_100, 'koyu_120': koyu_120, 'koyu_140': koyu_140
                })
    
    # Koyu piksel oranına göre sırala
    daireler.sort(key=lambda x: x['koyu_120'], reverse=True)
    
    print(f'Toplam {len(daireler)} daire bulundu\n')
    
    print('En yüksek koyu_120 (muhtemelen dolu):')
    for d in daireler[:10]:
        print(f"  cx={d['cx']:3d}, cy={d['cy']:3d}, avg={d['avg']:.0f}, std={d['std']:.1f}, min={d['min']:3d}, k100={d['koyu_100']:.2f}, k120={d['koyu_120']:.2f}, k140={d['koyu_140']:.2f}")
    
    print()
    print('En düşük koyu_120 (muhtemelen boş):')
    for d in daireler[-10:]:
        print(f"  cx={d['cx']:3d}, cy={d['cy']:3d}, avg={d['avg']:.0f}, std={d['std']:.1f}, min={d['min']:3d}, k100={d['koyu_100']:.2f}, k120={d['koyu_120']:.2f}, k140={d['koyu_140']:.2f}")
    
    # Histogram
    print('\n\nKoyu_120 dağılımı:')
    k120_values = [d['koyu_120'] for d in daireler]
    bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for i in range(len(bins)-1):
        count = sum(1 for v in k120_values if bins[i] <= v < bins[i+1])
        bar = '#' * count
        print(f"  {bins[i]:.1f}-{bins[i+1]:.1f}: {count:3d} {bar}")
