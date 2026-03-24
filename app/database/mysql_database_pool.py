import mysql.connector.pooling
from mysql.connector import Error
from typing import Optional
import os
import logging
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration using environment variables
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'wan'),
    'password': os.getenv('DB_PASSWORD', 'Qqwe123123'),
    'host': os.getenv('DB_HOST', '192.168.2.118'),
    'database': os.getenv('DB_NAME', 'bilibili_NLP'),
    'pool_name': 'mypool',
    'pool_size': 10,
    'pool_reset_session': True
}

class DatabasePool:
    def __init__(self):
        self.pool_config = DB_CONFIG
        self.connection_pool = None
        self._create_pool()

    def _create_pool(self):
        """Create a connection pool"""
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.pool_config)
            logger.info("Database pool created successfully")
        except Error as e:
            logger.error(f"Error creating database pool: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            
            connection = self.connection_pool.get_connection()#type: ignore
            return connection
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            return None

    @contextmanager
    def get_db_connection(self):
        """Context manager for getting database connections"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            if not conn:
                raise Exception("Failed to get database connection from pool")
            cursor = conn.cursor(dictionary=True)
            yield conn, cursor
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

# Global database pool instance
db_pool = DatabasePool()

def get_db_connection():
    """Get a database connection from the pool"""
    return db_pool.get_connection()