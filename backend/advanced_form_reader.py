"""
Gelişmiş Optik Form Okuyucu - LGS ve diğer standart formlar için
"""

import cv2
import numpy as np
from pyzbar import pyzbar
from form_templates import get_template

class AdvancedOpticalFormReader:
    """
    Şablon bazlı gelişmiş optik form okuyucu
    QR kod tanıma, öğrenci bilgisi okuma ve bölüm bazlı cevap okuma
    """
    
    def __init__(self, template_name='simple'):
        self.template = get_template(template_name)
        self.debug_mode = True
        
    def read_form(self, image_path):
        """
        Formu oku ve tüm bilgileri çıkar
        """
        # Görüntüyü yükle
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Görüntü yüklenemedi'}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        result = {
            'template': self.template['name'],
            'student_info': {},
            'answers': {},
            'qr_data': None
        }
        
        # 1. QR Kod oku (varsa)
        qr_data = self.read_qr_code(image)
        if qr_data:
            result['qr_data'] = qr_data
            print(f"📱 QR Kod: {qr_data}")
        
        # 2. Form hizalama ve düzeltme
        aligned_image = self.align_form(gray)
        
        # 3. Öğrenci bilgilerini oku
        if 'student_info' in self.template:
            student_info = self.read_student_info(aligned_image)
            result['student_info'] = student_info
            print(f"👤 Öğrenci Bilgileri: {student_info}")
        
        # 4. Cevapları oku (bölüm bazlı)
        answers = self.read_answers_by_sections(aligned_image)
        result['answers'] = answers
        
        return result
    
    def read_qr_code(self, image):
        """QR kodu oku"""
        try:
            decoded_objects = pyzbar.decode(image)
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            print(f"QR kod okuma hatası: {e}")
        return None
    
    def detect_timing_marks_lgs(self, gray_image):
        """
        LGS formundaki soldaki timing mark'ları tespit et
        (image_processor.py'deki ile aynı mantık ama grayscale için)
        """
        # Threshold: Siyah timing mark'ları beyaz arka plandan ayır
        _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morfolojik işlem
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Kontürleri bul
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        timing_marks = []
        image_height, image_width = gray_image.shape
        left_boundary = int(image_width * 0.15)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if 100 < area < 1000:
                x, y, w, h = cv2.boundingRect(contour)
                
                if x < left_boundary:
                    aspect_ratio = h / float(w) if w > 0 else 0
                    
                    if aspect_ratio > 1.5:
                        center_x = x + w // 2
                        center_y = y + h // 2
                        timing_marks.append({
                            'center': (center_x, center_y),
                            'bbox': (x, y, w, h),
                            'area': area
                        })
        
        timing_marks.sort(key=lambda m: m['center'][1])
        print(f"🎯 LGS timing marks: {len(timing_marks)} bulundu")
        return timing_marks
    
    def align_form(self, gray_image):
        """
        Formu hizala - timing mark bazlı perspektif düzeltme
        
        Öncelik:
        1. Timing mark bazlı (LGS formları için)
        2. Fallback: Klasik 4-köşe tespit
        """
        # Önce timing mark'ları dene
        timing_marks = self.detect_timing_marks_lgs(gray_image)
        
        if len(timing_marks) >= 3:
            print("📐 Timing mark bazlı hizalama kullanılıyor...")
            
            # Timing mark'lardan köşeleri hesapla
            points = np.array([m['center'] for m in timing_marks])
            y_coords = points[:, 1]
            x_coords = points[:, 0]
            
            # Sol kenar doğrusu
            coeffs = np.polyfit(y_coords, x_coords, 1)
            m_left, c_left = coeffs
            
            height, width = gray_image.shape
            
            # Form sınırları
            top_y = max(0, timing_marks[0]['center'][1] - 100)
            bottom_y = min(height, timing_marks[-1]['center'][1] + 100)
            
            top_left_x = int(m_left * top_y + c_left)
            bottom_left_x = int(m_left * bottom_y + c_left)
            
            form_height = bottom_y - top_y
            form_width = int(form_height / 1.41)
            
            corners = np.array([
                [top_left_x, top_y],
                [top_left_x + form_width, top_y],
                [bottom_left_x + form_width, bottom_y],
                [bottom_left_x, bottom_y]
            ], dtype=np.float32)
            
            return self.four_point_transform(gray_image, corners)
        
        # Fallback: Klasik kontür bazlı
        print("⚠️ Timing mark yetersiz, klasik metod kullanılıyor")
        thresh = cv2.adaptiveThreshold(
            gray_image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            peri = cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
            
            if len(approx) == 4:
                return self.four_point_transform(gray_image, approx.reshape(4, 2))
        
        return gray_image
    
    def four_point_transform(self, image, pts):
        """4 noktalı perspektif düzeltme"""
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect
        
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    def order_points(self, pts):
        """Noktaları sırala: sol-üst, sağ-üst, sağ-alt, sol-alt"""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    def read_student_info(self, image):
        """Öğrenci bilgilerini oku (numara, TC kimlik vb.)"""
        student_info = {}
        
        height, width = image.shape
        
        # Öğrenci numarasını oku (sol taraf bubble'lar)
        if 'student_no' in self.template.get('student_info', {}):
            student_no = self.read_number_bubbles(
                image,
                x=int(width * 0.02),  # Sol %2
                y=int(height * 0.15),  # Üstten %15
                bubble_width=int(width * 0.06),
                bubble_height=int(height * 0.08),
                digit_count=7
            )
            student_info['student_number'] = student_no
        
        # TC Kimlik oku (ortada alt)
        if 'tc_kimlik' in self.template.get('student_info', {}):
            tc_kimlik = self.read_number_bubbles(
                image,
                x=int(width * 0.08),
                y=int(height * 0.39),
                bubble_width=int(width * 0.15),
                bubble_height=int(height * 0.05),
                digit_count=11
            )
            student_info['tc_kimlik'] = tc_kimlik
        
        return student_info
    
    def read_number_bubbles(self, image, x, y, bubble_width, bubble_height, digit_count):
        """
        Sayı bubble'larını oku (0-9 her basamak için)
        """
        number = ""
        
        # Her basamak için
        col_spacing = bubble_width // digit_count
        row_spacing = bubble_height // 10  # 0-9
        
        for digit in range(digit_count):
            max_filled = -1
            selected_number = 0
            
            digit_x = x + (digit * col_spacing)
            
            # 0-9 her seçenek için
            for num in range(10):
                bubble_y = y + (num * row_spacing)
                
                # Bubble bölgesini al
                bubble_region = image[
                    bubble_y:bubble_y + row_spacing,
                    digit_x:digit_x + col_spacing
                ]
                
                if bubble_region.size == 0:
                    continue
                
                # Bubble doluluk oranı
                filled_ratio = np.sum(bubble_region < 127) / bubble_region.size
                
                if filled_ratio > max_filled:
                    max_filled = filled_ratio
                    selected_number = num
            
            # Minimum %20 doluluk varsa ekle
            if max_filled > 0.2:
                number += str(selected_number)
            else:
                number += "_"
        
        return number if "_" not in number else "Okunamadı"
    
    def read_answers_by_sections(self, image):
        """Bölüm bazlı cevapları oku (Türkçe, Matematik vb.)"""
        all_answers = {}
        
        if 'sections' not in self.template:
            return self.read_simple_answers(image)
        
        height, width = image.shape
        
        # Her bölüm için
        for section in self.template['sections']:
            section_name = section['code']
            start_q = section['start_question']
            end_q = section['end_question']
            position = section['position']
            
            print(f"\n📚 {section['name']} bölümü okunuyor...")
            
            # Pozisyona göre koordinatları belirle
            x, y, col_width, row_height = self.get_section_coordinates(
                width, height, position
            )
            
            # Bu bölümdeki cevapları oku
            section_answers = self.read_section_bubbles(
                image, x, y, col_width, row_height,
                start_q, end_q, section['choices']
            )
            
            all_answers[section_name] = section_answers
        
        return all_answers
    
    def get_section_coordinates(self, width, height, position):
        """Pozisyon string'ine göre koordinatları döndür"""
        # LGS formu için koordinatlar
        coords = {
            'bottom_left_column1': (0.02, 0.63, 0.05, 0.03),  # Türkçe
            'bottom_left_column2': (0.07, 0.63, 0.05, 0.03),  # Sosyal
            'bottom_left_column3': (0.12, 0.63, 0.05, 0.03),  # Din
            'bottom_left_column4': (0.17, 0.63, 0.05, 0.03),  # İngilizce
            'bottom_right_column1': (0.22, 0.63, 0.05, 0.03), # Matematik
            'bottom_right_column2': (0.27, 0.63, 0.05, 0.03), # Fen
        }
        
        if position in coords:
            ratios = coords[position]
            return (
                int(width * ratios[0]),
                int(height * ratios[1]),
                int(width * ratios[2]),
                int(height * ratios[3])
            )
        
        # Default
        return (int(width * 0.1), int(height * 0.3), int(width * 0.8), int(height * 0.6))
    
    def read_section_bubbles(self, image, x, y, col_width, row_height, 
                            start_q, end_q, choices):
        """Bir bölümdeki tüm bubble'ları oku"""
        answers = {}
        
        choice_spacing = col_width // len(choices)
        
        for q_num in range(start_q, end_q + 1):
            q_y = y + ((q_num - start_q) * row_height)
            
            max_filled = -1
            selected_choice = None
            
            # Her şık için (A, B, C, D, E)
            for i, choice in enumerate(choices):
                choice_x = x + (i * choice_spacing)
                
                # Bubble bölgesi
                bubble = image[
                    q_y:q_y + row_height,
                    choice_x:choice_x + choice_spacing
                ]
                
                if bubble.size == 0:
                    continue
                
                # Doluluk oranı
                filled_ratio = np.sum(bubble < 127) / bubble.size
                
                if filled_ratio > max_filled:
                    max_filled = filled_ratio
                    selected_choice = choice
            
            # Minimum %25 doluluk kontrolü
            if max_filled > 0.25:
                answers[q_num] = selected_choice
            else:
                answers[q_num] = "BOŞ"
        
        return answers
    
    def read_simple_answers(self, image):
        """Basit form için cevap okuma (eski sistem)"""
        # Eski OpticalFormReader mantığı
        return {}
