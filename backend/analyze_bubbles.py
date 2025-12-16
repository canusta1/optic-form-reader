"""
Baloncuk algılama analizi - sorunları tespit etmek için
"""
import cv2
import numpy as np

def analyze_region(img_path, region_name):
    """Bir bölgeyi analiz et"""
    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ {region_name}: Görüntü yüklenemedi")
        return
    
    h, w = img.shape[:2]
    print(f"\n{'='*50}")
    print(f"📊 {region_name.upper()} ANALİZİ")
    print(f"{'='*50}")
    print(f"Boyut: {w}x{h}")
    
    # Gri tonlama
    gri = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Parlaklık analizi
    avg_brightness = np.mean(gri)
    print(f"Ortalama Parlaklık: {avg_brightness:.1f}")
    
    # Farklı threshold yöntemleri dene
    blurred = cv2.GaussianBlur(gri, (5, 5), 0)
    
    # Yöntem 1: Adaptive Threshold
    thresh1 = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 2)
    cnts1, _ = cv2.findContours(thresh1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Yöntem 2: Otsu
    _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cnts2, _ = cv2.findContours(thresh2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Yöntem 3: Sabit eşik
    _, thresh3 = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
    cnts3, _ = cv2.findContours(thresh3.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"\nKontur Sayıları:")
    print(f"  Adaptive: {len(cnts1)}")
    print(f"  Otsu: {len(cnts2)}")
    print(f"  Sabit(200): {len(cnts3)}")
    
    # Boyut analizi
    min_w = w / 50
    max_w = w / 3
    
    for name, cnts in [("Adaptive", cnts1), ("Otsu", cnts2), ("Sabit", cnts3)]:
        kare_ish = []
        for c in cnts:
            (x, y, wb, hb) = cv2.boundingRect(c)
            ar = wb / float(hb) if hb > 0 else 0
            if 0.5 <= ar <= 1.5 and wb >= min_w and hb >= min_w and wb <= max_w:
                kare_ish.append((wb, hb))
        
        if kare_ish:
            widths = [b[0] for b in kare_ish]
            print(f"\n  {name} Kare-ish: {len(kare_ish)}")
            print(f"    Min genişlik: {min(widths):.1f}")
            print(f"    Max genişlik: {max(widths):.1f}")
            print(f"    Ortalama: {sum(widths)/len(widths):.1f}")
        else:
            print(f"\n  {name} Kare-ish: 0")
    
    print(f"\nEşik değerleri: min_w={min_w:.1f}, max_w={max_w:.1f}")
    
    # HoughCircles ile daire tespiti dene
    circles = cv2.HoughCircles(
        blurred, 
        cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=int(w/20),
        param1=50,
        param2=30,
        minRadius=int(w/60),
        maxRadius=int(w/8)
    )
    
    if circles is not None:
        print(f"\nHoughCircles: {len(circles[0])} daire bulundu")
    else:
        print(f"\nHoughCircles: Daire bulunamadı")
    
    # Debug görüntüleri kaydet
    cv2.imwrite(f"debug_images/analyze_{region_name}_thresh_adaptive.jpg", thresh1)
    cv2.imwrite(f"debug_images/analyze_{region_name}_thresh_otsu.jpg", thresh2)
    cv2.imwrite(f"debug_images/analyze_{region_name}_thresh_fixed.jpg", thresh3)
    
    # Konturları çiz
    debug_img = img.copy()
    for c in cnts1:
        (x, y, wb, hb) = cv2.boundingRect(c)
        ar = wb / float(hb) if hb > 0 else 0
        if 0.5 <= ar <= 1.5 and wb >= min_w and hb >= min_w and wb <= max_w:
            cv2.rectangle(debug_img, (x, y), (x+wb, y+hb), (0, 255, 0), 2)
    cv2.imwrite(f"debug_images/analyze_{region_name}_contours.jpg", debug_img)

if __name__ == "__main__":
    regions = [
        ("debug_images/bolge_turkce.jpg", "turkce"),
        ("debug_images/bolge_matematik.jpg", "matematik"),
        ("debug_images/bolge_fen.jpg", "fen"),
        ("debug_images/bolge_sosyal.jpg", "sosyal")
    ]
    
    for path, name in regions:
        analyze_region(path, name)
    
    print("\n\n✅ Analiz tamamlandı! Debug görüntüleri 'debug_images' klasörüne kaydedildi.")
