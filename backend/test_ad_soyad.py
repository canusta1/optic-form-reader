#!/usr/bin/env python3
"""Ad/Soyad tespit testi"""

from image_processor import OptikFormOkuyucu
import os

processor = OptikFormOkuyucu(debug_mode=True)

# uploads klasöründeki ilk dosyayı al
uploads = [f for f in os.listdir('uploads') if f.endswith(('.jpg', '.png'))]
if uploads:
    result = processor.form_oku(os.path.join('uploads', uploads[0]))
    print(f"\n🎯 SONUÇ:")
    print(f"   Ad: '{result['student_info']['name']}'")
    print(f"   Soyad: '{result['student_info']['surname']}'")
else:
    print("Upload klasöründe dosya bulunamadı!")
