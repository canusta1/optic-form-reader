# Test için basit optik form görseli oluşturma scripti
import cv2
import numpy as np

def create_test_form():
    """Test için basit bir optik form görseli oluştur"""
    # Beyaz arka plan
    form = np.ones((800, 600, 3), dtype=np.uint8) * 255
    
    # Başlık
    cv2.putText(form, "TEST OPTIK FORMU", (150, 50), 
                cv2.FONT_HERSHEY_BOLD, 1, (0, 0, 0), 2)
    
    # Öğrenci bilgileri
    cv2.putText(form, "Adi Soyadi:", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.rectangle(form, (200, 80), (500, 110), (0, 0, 0), 1)
    
    cv2.putText(form, "No:", (50, 140), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.rectangle(form, (200, 120), (350, 150), (0, 0, 0), 1)
    
    # Sorular (5 seçenekli)
    start_y = 200
    options = ['A', 'B', 'C', 'D', 'E']
    
    for q in range(1, 11):  # 10 soru
        # Soru numarası
        cv2.putText(form, f"S{q}:", (50, start_y + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Seçenekler
        for i, opt in enumerate(options):
            x = 120 + i * 60
            y = start_y
            
            # Kutucuk
            cv2.rectangle(form, (x, y), (x + 30, y + 30), (0, 0, 0), 2)
            
            # Harf
            cv2.putText(form, opt, (x + 8, y + 22), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Örnek işaretleme (rastgele)
            if q % 3 == i % 3:  # Bazı kutucukları işaretle
                cv2.circle(form, (x + 15, y + 15), 10, (0, 0, 0), -1)
        
        start_y += 50
    
    return form

if __name__ == "__main__":
    print("Test optik formu oluşturuluyor...")
    form = create_test_form()
    
    # Kaydet
    cv2.imwrite("test_optic_form.jpg", form)
    print("✅ Test formu oluşturuldu: test_optic_form.jpg")
    
    # Göster
    cv2.imshow("Test Optik Form", form)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
