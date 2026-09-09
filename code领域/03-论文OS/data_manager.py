"""
Paper-OS 数据库模型定义
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import os


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.init_database()

    def init_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arxiv_id TEXT UNIQUE,
                filename TEXT,
                title TEXT NOT NULL,
                authors TEXT,
                year INTEGER,
                venue TEXT,
                keywords TEXT,
                citation_count INTEGER DEFAULT 0,
                importance TEXT,
                application_areas TEXT,
                difficulty_level TEXT,
                size_mb REAL,
                category TEXT,
                has_analysis BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS learning_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                level TEXT NOT NULL,
                duration_weeks INTEGER,
                description TEXT,
                order_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS path_papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path_id INTEGER,
                paper_id INTEGER,
                order_index INTEGER,
                learning_focus TEXT,
                FOREIGN KEY (path_id) REFERENCES learning_paths(id),
                FOREIGN KEY (paper_id) REFERENCES papers(id),
                UNIQUE(path_id, paper_id)
            );

            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT,
                description TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS path_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path_id INTEGER,
                application_id INTEGER,
                FOREIGN KEY (path_id) REFERENCES learning_paths(id),
                FOREIGN KEY (application_id) REFERENCES applications(id)
            );

            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                paper_id INTEGER,
                path_id INTEGER,
                status TEXT DEFAULT 'not_started',
                reading_progress REAL DEFAULT 0,
                notes TEXT,
                rating INTEGER,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (paper_id) REFERENCES papers(id),
                FOREIGN KEY (path_id) REFERENCES learning_paths(id),
                UNIQUE(user_id, paper_id)
            );

            CREATE TABLE IF NOT EXISTS practice_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                difficulty TEXT,
                code_template TEXT,
                solution TEXT,
                status TEXT DEFAULT 'not_started',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            );

            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER,
                question TEXT NOT NULL,
                options TEXT,
                correct_answer INTEGER,
                explanation TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            );

            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                quiz_id INTEGER,
                user_answer INTEGER,
                is_correct BOOLEAN,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            );

            CREATE TABLE IF NOT EXISTS code_implementation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER,
                repo_name TEXT,
                repo_url TEXT,
                language TEXT,
                description TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            );

            CREATE TABLE IF NOT EXISTS knowledge_graph (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_paper_id INTEGER,
                target_paper_id INTEGER,
                relationship_type TEXT,
                description TEXT,
                strength REAL DEFAULT 1.0,
                FOREIGN KEY (source_paper_id) REFERENCES papers(id),
                FOREIGN KEY (target_paper_id) REFERENCES papers(id),
                UNIQUE(source_paper_id, target_paper_id, relationship_type)
            );

            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                title TEXT NOT NULL,
                description TEXT,
                achieved BOOLEAN DEFAULT 0,
                achieved_at TIMESTAMP,
                certificate_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ai_qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT,
                paper_ids TEXT,
                similarity_score REAL,
                user_rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_papers_arxiv ON papers(arxiv_id);
            CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category);
            CREATE INDEX IF NOT EXISTS idx_user_progress_paper ON user_progress(paper_id);
            CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id);
            CREATE INDEX IF NOT EXISTS idx_quizzes_paper ON quizzes(paper_id);
        """)
        self.conn.commit()

    def insert_paper(self, paper_data: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO papers 
                (arxiv_id, filename, title, authors, year, venue, keywords, 
                 citation_count, importance, application_areas, difficulty_level, 
                 size_mb, category, has_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_data.get('arxiv_id'),
                paper_data.get('filename'),
                paper_data.get('title'),
                paper_data.get('authors'),
                paper_data.get('year'),
                paper_data.get('venue'),
                json.dumps(paper_data.get('keywords', [])),
                paper_data.get('citation_count', 0),
                paper_data.get('importance'),
                json.dumps(paper_data.get('application_areas', [])),
                paper_data.get('difficulty_level'),
                paper_data.get('size_mb'),
                paper_data.get('category'),
                paper_data.get('has_analysis', False)
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting paper: {e}")
            self.conn.rollback()
            return -1

    def get_paper_by_id(self, paper_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_papers_by_category(self, category: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE category = ?", (category,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_user_progress(self, paper_id: int, progress_data: Dict[str, Any]) -> bool:
        cursor = self.conn.cursor()
        try:
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO user_progress 
                (user_id, paper_id, status, reading_progress, notes, rating, 
                 started_at, completed_at)
                VALUES (1, ?, ?, ?, ?, ?, 
                        COALESCE((SELECT started_at FROM user_progress WHERE paper_id = ?), ?),
                        CASE WHEN ? = 'completed' THEN ? ELSE 
                             COALESCE((SELECT completed_at FROM user_progress WHERE paper_id = ?), NULL) END)
            """, (
                paper_id,
                progress_data.get('status', 'not_started'),
                progress_data.get('reading_progress', 0),
                progress_data.get('notes'),
                progress_data.get('rating'),
                paper_id, now,
                progress_data.get('status', 'not_started'), now,
                paper_id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating progress: {e}")
            self.conn.rollback()
            return False

    def get_user_progress(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, up.status, up.reading_progress, up.notes, up.rating
            FROM user_progress up
            JOIN papers p ON up.paper_id = p.id
            WHERE up.user_id = 1
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM papers")
        stats['total_papers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM papers WHERE has_analysis = 1")
        stats['papers_with_analysis'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(citation_count) FROM papers")
        stats['total_citations'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM user_progress WHERE status = 'completed'")
        stats['completed_papers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(reading_progress) FROM user_progress")
        stats['avg_progress'] = round(cursor.fetchone()[0] or 0, 2)
        
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM papers 
            GROUP BY category
        """)
        stats['by_category'] = dict(cursor.fetchall())
        
        return stats

    def close(self):
        if self.conn:
            self.conn.close()
