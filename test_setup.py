import os
import sqlite3
import unittest

class TestSetup(unittest.TestCase):
    def test_database_exists(self):
        db_path = os.path.join('data', 'discovery.db')
        self.assertTrue(os.path.exists(db_path), f"Database not found at {db_path}")

    def test_database_schema(self):
        db_path = os.path.join('data', 'discovery.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check expected tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['documents', 'analysis', 'themes', 'theme_docs', 'insights']
        for table in expected_tables:
            self.assertIn(table, tables, f"Expected table '{table}' is missing from database schema.")
        
        conn.close()

    def test_imports(self):
        try:
            import google_play_scraper
            import praw
            import sentence_transformers
            from sklearn.cluster import DBSCAN
            import sklearn
            import groq
            import fastapi
            import uvicorn
        except ImportError as e:
            self.fail(f"Dependency import failed: {e}")

    def test_groq_client_import(self):
        try:
            from analysis.groq_client import client, GroqClientWrapper
            self.assertIsNotNone(client)
        except Exception as e:
            self.fail(f"Failed to import/initialize GroqClientWrapper: {e}")

if __name__ == '__main__':
    unittest.main()
