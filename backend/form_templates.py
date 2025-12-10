"""
Optik form şablonları - Farklı sınav tiplerinin yapısını tanımlar
"""

# LGS Form Yapısı (20-20 Format)
LGS_20_20_TEMPLATE = {
    'name': 'LGS 20-20',
    'description': 'İlkokul ve Ortaokul Cevap Kağıdı',
    'total_questions': 90,
    
    # Öğrenci bilgileri koordinatları (formdaki konumlar)
    'student_info': {
        'group_no': {
            'type': 'bubbles',
            'position': 'left_top',
            'bubble_count': 10,
            'digits': 1
        },
        'student_no': {
            'type': 'bubbles',
            'position': 'left_center',
            'bubble_count': 10,
            'digits': 7
        },
        'tc_kimlik': {
            'type': 'bubbles',
            'position': 'center_bottom',
            'bubble_count': 10,
            'digits': 11
        },
        'name': {
            'type': 'text',
            'position': 'left_info',
            'fields': ['Soyadı - Adı']
        }
    },
    
    # Sözel Bölüm
    'sections': [
        {
            'name': 'TÜRKÇE',
            'code': 'TR',
            'start_question': 1,
            'end_question': 20,
            'position': 'bottom_left_column1',
            'choices': ['A', 'B', 'C', 'D', 'E']
        },
        {
            'name': 'SOSYAL / HAYAT BİL. - İNKILAP TARİHİ ve ATATÜRKÇÜLÜK',
            'code': 'SOSYAL',
            'start_question': 1,
            'end_question': 20,
            'position': 'bottom_left_column2',
            'choices': ['A', 'B', 'C', 'D', 'E']
        },
        {
            'name': 'DİN KÜLTÜRÜ VE AHLAK BİLGİSİ',
            'code': 'DIN',
            'start_question': 1,
            'end_question': 10,
            'position': 'bottom_left_column3',
            'choices': ['A', 'B', 'C', 'D', 'E']
        },
        {
            'name': 'İNGİLİZCE',
            'code': 'ING',
            'start_question': 1,
            'end_question': 10,
            'position': 'bottom_left_column4',
            'choices': ['A', 'B', 'C', 'D', 'E']
        },
        {
            'name': 'MATEMATİK',
            'code': 'MAT',
            'start_question': 1,
            'end_question': 20,
            'position': 'bottom_right_column1',
            'choices': ['A', 'B', 'C', 'D', 'E']
        },
        {
            'name': 'FEN BİLİMLERİ',
            'code': 'FEN',
            'start_question': 1,
            'end_question': 20,
            'position': 'bottom_right_column2',
            'choices': ['A', 'B', 'C', 'D', 'E']
        }
    ],
    
    # Form yapısı koordinatları (piksel bazlı, normalize edilecek)
    'layout': {
        'width': 2480,  # A4 @ 300 DPI
        'height': 3508,
        
        # Sözel bölüm (altta sol)
        'sozel_section': {
            'x': 48,
            'y': 2200,
            'width': 484,
            'height': 1280,
            'columns': [
                {'name': 'TÜRKÇE', 'x_offset': 0, 'width': 121},
                {'name': 'SOSYAL', 'x_offset': 121, 'width': 121},
                {'name': 'DİN', 'x_offset': 242, 'width': 121},
                {'name': 'İNGİLİZCE', 'x_offset': 363, 'width': 121}
            ],
            'question_height': 64,
            'bubble_spacing': 24
        },
        
        # Sayısal bölüm (altta sağ)
        'sayisal_section': {
            'x': 532,
            'y': 2200,
            'width': 242,
            'height': 1280,
            'columns': [
                {'name': 'MATEMATİK', 'x_offset': 0, 'width': 121},
                {'name': 'FEN BİLİMLERİ', 'x_offset': 121, 'width': 121}
            ],
            'question_height': 64,
            'bubble_spacing': 24
        },
        
        # Üstteki büyük cevap alanı (opsiyonel kullanım)
        'main_answer_area': {
            'x': 376,
            'y': 54,
            'width': 734,
            'height': 590,
            'grid_rows': 11,
            'grid_cols': 10
        },
        
        # Öğrenci no (sol)
        'student_no_area': {
            'x': 48,
            'y': 172,
            'width': 148,
            'height': 268,
            'bubble_rows': 7,
            'bubble_cols': 10
        },
        
        # TC Kimlik (ortada alt)
        'tc_kimlik_area': {
            'x': 196,
            'y': 1380,
            'width': 373,
            'height': 180,
            'bubble_rows': 11,
            'bubble_cols': 10
        }
    }
}

# Basit Optik Form Şablonu (Eski sistem)
SIMPLE_TEMPLATE = {
    'name': 'Basit Optik Form',
    'description': 'Genel amaçlı optik form',
    'total_questions': 'variable',
    'sections': [
        {
            'name': 'Genel',
            'code': 'GEN',
            'start_question': 1,
            'end_question': 'variable',
            'position': 'auto',
            'choices': ['A', 'B', 'C', 'D', 'E']
        }
    ]
}

# Tüm şablonlar
FORM_TEMPLATES = {
    'lgs_20_20': LGS_20_20_TEMPLATE,
    'simple': SIMPLE_TEMPLATE
}

def get_template(template_name='simple'):
    """Şablon adına göre form şablonu döndür"""
    return FORM_TEMPLATES.get(template_name, SIMPLE_TEMPLATE)

def list_templates():
    """Mevcut tüm şablonları listele"""
    return [
        {
            'id': key,
            'name': value['name'],
            'description': value['description']
        }
        for key, value in FORM_TEMPLATES.items()
    ]
