import mysql.connector
from mysql.connector import Error

class DatabaseHandler:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="damyanti26",
                database="ResumeBuilder"
            )
            self.cursor = self.connection.cursor()
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def fetch_prompt(self, prompt_id):
        """Fetch a specific prompt by its ID"""
        try:
            query = "SELECT prompts FROM Prompts WHERE prompt_id = %s"
            self.cursor.execute(query, (prompt_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching prompt: {e}")
            return None
        
    def close(self):
        """Close database connection"""
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()


