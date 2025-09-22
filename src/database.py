import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class VocabularyDatabase:
    def __init__(self, db_path: str = "vocabulary.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vocabulary words table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                definition TEXT NOT NULL,
                example_sentence TEXT,
                pronunciation TEXT,
                difficulty_level INTEGER DEFAULT 1,
                category TEXT DEFAULT 'general',
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER UNIQUE,
                correct_answers INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                last_reviewed TEXT,
                mastery_level INTEGER DEFAULT 0,
                FOREIGN KEY (word_id) REFERENCES vocabulary (id)
            )
        ''')
        
        # Daily sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                words_learned INTEGER DEFAULT 0,
                quiz_score REAL DEFAULT 0.0,
                total_time_minutes INTEGER DEFAULT 0,
                session_completed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Quiz results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER,
                session_date TEXT,
                is_correct BOOLEAN,
                response_time_seconds REAL,
                FOREIGN KEY (word_id) REFERENCES vocabulary (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_vocabulary_word(self, word: str, definition: str, example: str = "", 
                           pronunciation: str = "", difficulty: int = 1, category: str = "general"):
        """Add a new vocabulary word to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO vocabulary (word, definition, example_sentence, pronunciation, difficulty_level, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (word, definition, example, pronunciation, difficulty, category))
            
            word_id = cursor.lastrowid
            
            # Initialize user progress entry
            cursor.execute('''
                INSERT INTO user_progress (word_id, last_reviewed)
                VALUES (?, ?)
                ON CONFLICT(word_id) DO NOTHING
            ''', (word_id, datetime.now().isoformat()))
            
            conn.commit()
            return word_id
        except sqlite3.IntegrityError:
            return None  # Word already exists
        finally:
            conn.close()
    
    def get_daily_words(self, count: int = 5) -> List[Dict]:
        """Get words for daily learning session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get words that haven't been mastered yet
        cursor.execute('''
            SELECT v.id, v.word, v.definition, v.example_sentence, v.pronunciation, 
                   up.mastery_level, up.correct_answers, up.total_attempts
            FROM vocabulary v
            LEFT JOIN user_progress up ON v.id = up.word_id
            WHERE up.mastery_level < 3 OR up.mastery_level IS NULL
            ORDER BY up.last_reviewed ASC, v.id ASC
            LIMIT ?
        ''', (count,))
        
        words = []
        for row in cursor.fetchall():
            words.append({
                'id': row[0],
                'word': row[1],
                'definition': row[2],
                'example': row[3],
                'pronunciation': row[4],
                'mastery_level': row[5] or 0,
                'correct_answers': row[6] or 0,
                'total_attempts': row[7] or 0
            })
        
        conn.close()
        return words
    
    def record_quiz_result(self, word_id: int, is_correct: bool, response_time: float = 0.0):
        """Record a quiz result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quiz_results (word_id, session_date, is_correct, response_time_seconds)
            VALUES (?, ?, ?, ?)
        ''', (word_id, datetime.now().isoformat(), is_correct, response_time))
        
        conn.commit()
        conn.close()
    
    def update_word_progress(self, word_id: int, is_correct: bool, response_time: float = 0.0):
        """Update progress for a specific word"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current progress
        cursor.execute('''
            SELECT correct_answers, total_attempts, mastery_level
            FROM user_progress WHERE word_id = ?
        ''', (word_id,))
        
        result = cursor.fetchone()
        if result:
            correct, total, mastery = result
            correct += 1 if is_correct else 0
            total += 1
            
            # Update mastery level based on performance
            accuracy = correct / total if total > 0 else 0
            if total >= 3 and accuracy >= 0.8:
                mastery = min(mastery + 1, 3)
            elif accuracy < 0.5:
                mastery = max(mastery - 1, 0)
        else:
            correct = 1 if is_correct else 0
            total = 1
            mastery = 1 if is_correct else 0
        
        # Update or insert progress
        cursor.execute('''
            INSERT INTO user_progress 
            (word_id, correct_answers, total_attempts, mastery_level, last_reviewed)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(word_id) DO UPDATE SET
                correct_answers = excluded.correct_answers,
                total_attempts = excluded.total_attempts,
                mastery_level = excluded.mastery_level,
                last_reviewed = excluded.last_reviewed
        ''', (word_id, correct, total, mastery, datetime.now().isoformat()))
        
        # Record quiz result
        self.record_quiz_result(word_id, is_correct, response_time)
        
        conn.commit()
        conn.close()
    
    def get_review_words(self, count: int = 10) -> List[Dict]:
        """Get words for review session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.id, v.word, v.definition, v.example_sentence, v.pronunciation,
                   up.mastery_level, up.last_reviewed
            FROM vocabulary v
            JOIN user_progress up ON v.id = up.word_id
            WHERE up.total_attempts > 0
            ORDER BY up.last_reviewed ASC
            LIMIT ?
        ''', (count,))
        
        words = []
        for row in cursor.fetchall():
            words.append({
                'id': row[0],
                'word': row[1],
                'definition': row[2],
                'example': row[3],
                'pronunciation': row[4],
                'mastery_level': row[5],
                'last_reviewed': row[6]
            })
        
        conn.close()
        return words
    
    def create_daily_session(self) -> int:
        """Create a new daily session record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        
        # Check if session already exists for today
        cursor.execute('SELECT id FROM daily_sessions WHERE session_date = ?', (today,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return existing[0]
        
        cursor.execute('''
            INSERT INTO daily_sessions (session_date)
            VALUES (?)
        ''', (today,))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id if session_id is not None else 0
    
    def update_session_stats(self, session_id: int, words_learned: int, quiz_score: float):
        """Update daily session statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE daily_sessions 
            SET words_learned = ?, quiz_score = ?, session_completed = TRUE
            WHERE id = ?
        ''', (words_learned, quiz_score, session_id))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self) -> Dict:
        """Get overall user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total words learned
        cursor.execute('SELECT COUNT(*) FROM user_progress WHERE total_attempts > 0')
        total_words = cursor.fetchone()[0]
        
        # Mastered words
        cursor.execute('SELECT COUNT(*) FROM user_progress WHERE mastery_level >= 3')
        mastered_words = cursor.fetchone()[0]
        
        # Average quiz score
        cursor.execute('SELECT AVG(quiz_score) FROM daily_sessions WHERE session_completed = TRUE')
        avg_score = cursor.fetchone()[0] or 0.0
        
        # Streak (consecutive days)
        cursor.execute('''
            SELECT COUNT(*) FROM daily_sessions 
            WHERE session_completed = TRUE AND session_date >= date('now', '-7 days')
        ''')
        recent_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_words': total_words,
            'mastered_words': mastered_words,
            'average_score': round(avg_score, 1),
            'recent_sessions': recent_sessions
        }