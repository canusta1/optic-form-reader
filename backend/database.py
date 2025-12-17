import sqlite3
from datetime import datetime
import hashlib
import secrets

class Database:
    def __init__(self, db_name='optic_forms.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cevap anahtarları tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answer_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exam_name TEXT NOT NULL,
                school_type TEXT,
                form_template TEXT DEFAULT 'simple',
                total_questions INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Ders bazında sorular ve cevaplar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer_key_id INTEGER NOT NULL,
                subject_name TEXT NOT NULL,
                question_count INTEGER NOT NULL,
                points_per_question REAL NOT NULL,
                FOREIGN KEY (answer_key_id) REFERENCES answer_keys (id)
            )
        ''')
        
        # Her sorunun doğru cevabı
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                question_number INTEGER NOT NULL,
                correct_answer TEXT NOT NULL,
                points REAL NOT NULL,
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        # Öğrenci sonuçları
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer_key_id INTEGER NOT NULL,
                student_name TEXT,
                student_number TEXT,
                exam_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_score REAL,
                success_rate REAL,
                image_path TEXT,
                FOREIGN KEY (answer_key_id) REFERENCES answer_keys (id)
            )
        ''')
        
        # Öğrenci cevapları
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                question_number INTEGER NOT NULL,
                student_answer TEXT,
                correct_answer TEXT,
                is_correct BOOLEAN,
                points_earned REAL,
                FOREIGN KEY (result_id) REFERENCES student_results (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Kullanıcı işlemleri
    def create_user(self, username, email, password, full_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, full_name))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def verify_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT id, username, email, full_name
            FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    # Cevap anahtarı işlemleri
    def create_answer_key(self, user_id, exam_name, school_type, subjects_data, form_template='simple'):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Toplam soru sayısını hesapla
            total_questions = sum(s['question_count'] for s in subjects_data)
            
            # Cevap anahtarını oluştur
            cursor.execute('''
                INSERT INTO answer_keys (user_id, exam_name, school_type, form_template, total_questions)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, exam_name, school_type, form_template, total_questions))
            
            answer_key_id = cursor.lastrowid
            
            # Her ders için bilgileri kaydet
            for subject in subjects_data:
                cursor.execute('''
                    INSERT INTO subjects (answer_key_id, subject_name, question_count, points_per_question)
                    VALUES (?, ?, ?, ?)
                ''', (answer_key_id, subject['name'], subject['question_count'], subject['points_per_question']))
                
                subject_id = cursor.lastrowid
                
                # Her sorunun cevabını kaydet
                for i, answer in enumerate(subject['answers'], 1):
                    cursor.execute('''
                        INSERT INTO questions (subject_id, question_number, correct_answer, points)
                        VALUES (?, ?, ?, ?)
                    ''', (subject_id, i, answer, subject['points'][i-1] if 'points' in subject else subject['points_per_question']))
            
            conn.commit()
            return answer_key_id
        except Exception as e:
            conn.rollback()
            print(f"Error creating answer key: {e}")
            return None
        finally:
            conn.close()
    
    def get_answer_keys(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                ak.*, 
                COUNT(DISTINCT sr.id) as student_count,
                (SELECT COUNT(*) FROM subjects s WHERE s.answer_key_id = ak.id) as subject_count,
                (SELECT SUM(q.points) 
                 FROM questions q 
                 JOIN subjects s ON q.subject_id = s.id 
                 WHERE s.answer_key_id = ak.id) as total_points
            FROM answer_keys ak
            LEFT JOIN student_results sr ON ak.id = sr.answer_key_id
            WHERE ak.user_id = ?
            GROUP BY ak.id
            ORDER BY ak.created_at DESC
        ''', (user_id,))
        
        keys = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return keys
    
    def get_answer_key_by_name(self, user_id, exam_name):
        """Form adına göre cevap anahtarı bul"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM answer_keys
            WHERE user_id = ? AND exam_name = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id, exam_name))
        
        key = cursor.fetchone()
        conn.close()
        
        return dict(key) if key else None
    
    def update_answer_key(self, answer_key_id, user_id, school_type, subjects_data, form_template):
        """Mevcut cevap anahtarını güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Toplam soru sayısını hesapla
            total_questions = sum(s['question_count'] for s in subjects_data)
            
            # Cevap anahtarını güncelle
            cursor.execute('''
                UPDATE answer_keys
                SET school_type = ?, form_template = ?, total_questions = ?
                WHERE id = ? AND user_id = ?
            ''', (school_type, form_template, total_questions, answer_key_id, user_id))
            
            # Eski dersleri ve soruları sil
            cursor.execute('''
                DELETE FROM questions
                WHERE subject_id IN (SELECT id FROM subjects WHERE answer_key_id = ?)
            ''', (answer_key_id,))
            
            cursor.execute('''
                DELETE FROM subjects WHERE answer_key_id = ?
            ''', (answer_key_id,))
            
            # Yeni dersleri ekle
            for subject in subjects_data:
                cursor.execute('''
                    INSERT INTO subjects (answer_key_id, subject_name, question_count, points_per_question)
                    VALUES (?, ?, ?, ?)
                ''', (answer_key_id, subject['name'], subject['question_count'], subject['points_per_question']))
                
                subject_id = cursor.lastrowid
                
                # Her sorunun cevabını kaydet
                for i, answer in enumerate(subject['answers'], 1):
                    cursor.execute('''
                        INSERT INTO questions (subject_id, question_number, correct_answer, points)
                        VALUES (?, ?, ?, ?)
                    ''', (subject_id, i, answer, subject['points'][i-1] if 'points' in subject else subject['points_per_question']))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating answer key: {e}")
            return False
        finally:
            conn.close()
    
    def get_answer_key_details(self, answer_key_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cevap anahtarı bilgilerini al
        cursor.execute('SELECT * FROM answer_keys WHERE id = ?', (answer_key_id,))
        answer_key = dict(cursor.fetchone())
        
        # Dersleri al
        cursor.execute('''
            SELECT id, subject_name, question_count, points_per_question
            FROM subjects
            WHERE answer_key_id = ?
            ORDER BY id ASC
        ''', (answer_key_id,))
        
        subjects = []
        for subject_row in cursor.fetchall():
            subject = dict(subject_row)
            subject_id = subject['id']
            
            # Bu dersin sorularını sıra numarasına göre al
            cursor.execute('''
                SELECT question_number, correct_answer, points
                FROM questions
                WHERE subject_id = ?
                ORDER BY question_number ASC
            ''', (subject_id,))
            
            questions = cursor.fetchall()
            subject['answers'] = [dict(q)['correct_answer'] for q in questions]
            subject['points'] = [dict(q)['points'] for q in questions]
            subjects.append(subject)
        
        answer_key['subjects'] = subjects
        conn.close()
        
        return answer_key
    
    # Öğrenci sonuçları
    def save_student_result(self, answer_key_id, student_data, answers_data, image_path=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Öğrenci sonucunu kaydet
            cursor.execute('''
                INSERT INTO student_results 
                (answer_key_id, student_name, student_number, total_score, success_rate, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (answer_key_id, student_data.get('name'), student_data.get('number'),
                  student_data.get('total_score'), student_data.get('success_rate'), image_path))
            
            result_id = cursor.lastrowid
            
            # Her cevabı kaydet
            for answer in answers_data:
                cursor.execute('''
                    INSERT INTO student_answers 
                    (result_id, subject_id, question_number, student_answer, correct_answer, is_correct, points_earned)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (result_id, answer['subject_id'], answer['question_number'],
                      answer['student_answer'], answer['correct_answer'],
                      answer['is_correct'], answer['points_earned']))
            
            conn.commit()
            return result_id
        except Exception as e:
            conn.rollback()
            print(f"Error saving student result: {e}")
            return None
        finally:
            conn.close()
    
    def get_student_results(self, answer_key_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM student_results
            WHERE answer_key_id = ?
            ORDER BY exam_date DESC
        ''', (answer_key_id,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_all_results(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sr.*, ak.exam_name
            FROM student_results sr
            JOIN answer_keys ak ON sr.answer_key_id = ak.id
            WHERE ak.user_id = ?
            ORDER BY sr.exam_date DESC
        ''', (user_id,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
