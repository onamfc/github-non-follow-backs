import sqlite3
import logging
from datetime import datetime
from config import DATABASE_FILE

class DatabaseManager:
    def __init__(self):
        self.db_file = DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Users I'm following
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS following (
                    username TEXT PRIMARY KEY,
                    user_id INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Users following me
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS followers (
                    username TEXT PRIMARY KEY,
                    user_id INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Users I've unfollowed
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unfollowed (
                    username TEXT PRIMARY KEY,
                    user_id INTEGER,
                    unfollowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT DEFAULT 'not_following_back'
                )
            ''')
            
            # Processing status tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_type TEXT,
                    last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    details TEXT
                )
            ''')
            
            conn.commit()
            logging.info("Database initialized successfully")
    
    def update_following_list(self, following_users):
        """Update the list of users I'm following"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM following')
            
            # Insert new data
            for user in following_users:
                cursor.execute('''
                    INSERT INTO following (username, user_id) 
                    VALUES (?, ?)
                ''', (user['login'], user['id']))
            
            conn.commit()
            logging.info(f"Updated following list with {len(following_users)} users")
    
    def update_followers_list(self, followers_users):
        """Update the list of users following me"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM followers')
            
            # Insert new data
            for user in followers_users:
                cursor.execute('''
                    INSERT INTO followers (username, user_id) 
                    VALUES (?, ?)
                ''', (user['login'], user['id']))
            
            conn.commit()
            logging.info(f"Updated followers list with {len(followers_users)} users")
    
    def get_users_to_unfollow(self, limit=None):
        """Get users I'm following who are not following me back"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT f.username, f.user_id 
                FROM following f 
                LEFT JOIN followers fo ON f.username = fo.username 
                LEFT JOIN unfollowed u ON f.username = u.username
                WHERE fo.username IS NULL 
                AND u.username IS NULL
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [{'login': row[0], 'id': row[1]} for row in results]
    
    def mark_as_unfollowed(self, username, user_id):
        """Mark a user as unfollowed"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO unfollowed (username, user_id) 
                VALUES (?, ?)
            ''', (username, user_id))
            
            conn.commit()
            logging.info(f"Marked {username} as unfollowed")
    
    def update_processing_status(self, process_type, status, details=None):
        """Update processing status"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO processing_status (process_type, status, details) 
                VALUES (?, ?, ?)
            ''', (process_type, status, details))
            
            conn.commit()
    
    def get_stats(self):
        """Get current statistics"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Count following
            cursor.execute('SELECT COUNT(*) FROM following')
            following_count = cursor.fetchone()[0]
            
            # Count followers
            cursor.execute('SELECT COUNT(*) FROM followers')
            followers_count = cursor.fetchone()[0]
            
            # Count unfollowed
            cursor.execute('SELECT COUNT(*) FROM unfollowed')
            unfollowed_count = cursor.fetchone()[0]
            
            # Count users to unfollow
            cursor.execute('''
                SELECT COUNT(*) 
                FROM following f 
                LEFT JOIN followers fo ON f.username = fo.username 
                LEFT JOIN unfollowed u ON f.username = u.username
                WHERE fo.username IS NULL 
                AND u.username IS NULL
            ''')
            to_unfollow_count = cursor.fetchone()[0]
            
            return {
                'following': following_count,
                'followers': followers_count,
                'unfollowed': unfollowed_count,
                'to_unfollow': to_unfollow_count
            }