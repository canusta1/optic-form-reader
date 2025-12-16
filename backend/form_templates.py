"""
Optik form şablonları - Farklı sınav tiplerinin yapısını tanımlar

YGS Form Yapısı:
================
SOL TARAF (Kimlik):
- AD: 10 sütun × 29 satır (her sütun bir harf pozisyonu)
- SOYAD: 10 sütun × 29 satır

SAĞ TARAF (Cevaplar):
- 4 ders kutusu: TÜRKÇE, MATEMATİK, FEN BİLİMLERİ, SOSYAL BİL
- Her ders: 40 soru × 5 şık = 200 bubble
- Toplam: 160 soru × 5 = 800 bubble
"""

# Türk alfabesi (29 harf)
TURKISH_ALPHABET = [
    'A', 'B', 'C', 'Ç', 'D', 'E', 'F', 'G', 'Ğ', 'H',
    'I', 'İ', 'J', 'K', 'L', 'M', 'N', 'O', 'Ö', 'P',
    'R', 'S', 'Ş', 'T', 'U', 'Ü', 'V', 'Y', 'Z'
]

YGS_TEMPLATE = {
    'name': 'YGS',
    'description': 'Yükseköğretime Geçiş Sınavı Cevap Kağıdı (160 Soru)',
    'total_questions': 160,
    'use_coordinates': True,
    
    # Hedef boyut (perspektif düzeltme sonrası)
    'target_size': (2480, 3508),
    
    # ========== KİMLİK BİLGİLERİ (SOL TARAF) ==========
    'name_section': {
        'name': 'AD',
        'columns': 10,      # 10 harf pozisyonu
        'rows': 29,         # 29 Türk harfi
        'alphabet': TURKISH_ALPHABET,
        'x_range': (0, 826),        # X koordinat aralığı
        'y_range': (0, 1754),       # Y koordinat aralığı (yarı yükseklik)
    },
    
    'surname_section': {
        'name': 'SOYAD',
        'columns': 10,
        'rows': 29,
        'alphabet': TURKISH_ALPHABET,
        'x_range': (0, 826),
        'y_range': (1754, 3508),    # AD'nin altında
    },
    
    # ========== CEVAP ALANLARI (SAĞ TARAF) ==========
    'answer_sections': [
        {
            'name': 'TÜRKÇE',
            'code': 'TURKCE',
            'start_question': 1,
            'end_question': 40,
            'questions': 40,
            'choices': ['A', 'B', 'C', 'D', 'E'],
            'x_range': (826, 1239),
            'y_range': (0, 3507),
        },
        {
            'name': 'T.MATEMATİK',
            'code': 'T_MATEMATIK',
            'start_question': 41,
            'end_question': 80,
            'questions': 40,
            'choices': ['A', 'B', 'C', 'D', 'E'],
            'x_range': (1239, 1652),
            'y_range': (0, 3507),
        },
        {
            'name': 'FEN BİLİMLERİ',
            'code': 'FEN_BILIMLERI',
            'start_question': 81,
            'end_question': 120,
            'questions': 40,
            'choices': ['A', 'B', 'C', 'D', 'E'],
            'x_range': (1652, 2065),
            'y_range': (0, 3507),
        },
        {
            'name': 'SOSYAL BİLİMLER',
            'code': 'SOSYAL_BILIMLER',
            'start_question': 121,
            'end_question': 160,
            'questions': 40,
            'choices': ['A', 'B', 'C', 'D', 'E'],
            'x_range': (2065, 2479),
            'y_range': (0, 3507),
        }
    ],
    
    # Bubble tespit ayarları
    'bubble_detection': {
        'color_detection': True,
        'lower_red1': [0, 50, 50],
        'upper_red1': [10, 255, 255],
        'lower_red2': [160, 50, 50],
        'upper_red2': [180, 255, 255],
        'min_fill_score': 140,      # İşaretli bubble threshold
        'min_difference': 15,       # İkinciden fark threshold
    },
    
    # Perspektif düzeltme
    'perspective_correction': {
        'enabled': True,
    }
}

# Tüm şablonlar
FORM_TEMPLATES = {
    'ygs': YGS_TEMPLATE
}

def get_template(template_name='simple'):
    """Şablon adına göre form şablonu döndür"""
    return FORM_TEMPLATES.get(template_name, None)

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
