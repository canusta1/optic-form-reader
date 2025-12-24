
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
    
    # perspektif düzeltme sonrası beklenen boyut
    'target_size': (2480, 3508),
    
    # sol taraf kimlik bilgileri    
    'name_section': {
        'name': 'AD',
        'columns': 10,      
        'rows': 29,        
        'alphabet': TURKISH_ALPHABET,
        'x_range': (0, 826),      
        'y_range': (0, 1754),      
    },
    
    'surname_section': {
        'name': 'SOYAD',
        'columns': 10,
        'rows': 29,
        'alphabet': TURKISH_ALPHABET,
        'x_range': (0, 826),
        'y_range': (1754, 3508),    
    },
    
    # sağ taraf cevap alanları  
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
        'min_fill_score': 140,     
        'min_difference': 15,   
    },
    
  
    'perspective_correction': {
        'enabled': True,
    }
}

FORM_TEMPLATES = {
    'ygs': YGS_TEMPLATE
}

def get_template(template_name='ygs'):
    return FORM_TEMPLATES.get(template_name)

def list_templates():
    return [
        {
            'id': key,
            'name': value['name'],
            'description': value['description']
        }
        for key, value in FORM_TEMPLATES.items()
    ]
