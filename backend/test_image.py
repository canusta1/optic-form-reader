#!/usr/bin/env python3
"""Test görüntü işleme"""

from image_processor import AdvancedFormReader
import cv2
import sys

# En son yüklenen görüntüyü test et
image_path = 'uploads/20251207_141438_scaled_test1.jpg'

print(f"\n{'='*60}")
print(f"TEST: {image_path}")
print(f"{'='*60}\n")

# Görüntü dosyasının var olup olmadığını kontrol et
import os
if not os.path.exists(image_path):
    print(f"❌ HATA: Görüntü bulunamadı: {image_path}")
    sys.exit(1)

print(f"[OK] Goruntu dosyasi bulundu: {image_path}")

# Image processor oluştur
processor = AdvancedFormReader()

# Bubble detection test et
print(f"\n{'='*60}")
print("BUBBLE DETECTION TEST")
print(f"{'='*60}\n")

try:
    result = processor.detect_answers(image_path, expected_questions=90)
    print(f"\n✅ İşlem tamamlandı!")
    print(f"📊 Sonuç: {result}")
    
    if isinstance(result, dict) and 'answers' in result:
        answers = result['answers']
        print(f"📊 Bulunan cevap sayısı: {len(answers)}")
        
        if len(answers) > 0:
            print("\nİlk 5 cevap:")
            for i, answer in enumerate(answers[:5]):
                print(f"  {i+1}. {answer}")
    else:
        print("\n⚠️  Hiç cevap bulunamadı!")
        print("\n🔍 Debug görüntülerini kontrol edin:")
        print("   - debug_edges.jpg")
        print("   - debug_contours.jpg")
        print("   - debug_warped.jpg")
        print("   - debug_preprocessed.jpg")
        print("   - debug_morphed.jpg")
        print("   - debug_binary_input_fixed.jpg")
        print("   - debug_bubbles.jpg")
        print("   - debug_rows.jpg")
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*60}\n")
