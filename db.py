import mysql.connector
from mysql.connector import Error
import config

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Establish a connection to the database."""
        try:
            # First connect to MySQL server to check/create DB
            temp_conn = mysql.connector.connect(
                host=config.DB_HOST,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            if temp_conn.is_connected():
                cursor = temp_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME}")
                temp_conn.close()

            # Now connect to the specific database
            self.connection = mysql.connector.connect(
                host=config.DB_HOST,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME
            )
            print("Successfully connected to the database.")

        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None

    def create_tables(self):
        """Execute the schema.sql file to create tables."""
        if self.connection and self.connection.is_connected():
            try:
                cursor = self.connection.cursor()
                # Read schema.sql
                schema_path = "data/schema.sql"
                with open(schema_path, 'r') as f:
                    statements = f.read().split(';')
                    for statement in statements:
                        if statement.strip():
                            cursor.execute(statement)
                self.connection.commit()
                print("Tables checked/created successfully.")
            except Error as e:
                print(f"Error creating tables: {e}")
    
    def log_detection(self, faces_detected, mode, fps, latency):
        """Log a single detection event."""
        if self.connection and self.connection.is_connected():
            try:
                cursor = self.connection.cursor()
                query = "INSERT INTO detections (faces_detected, mode, fps, latency_ms) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (faces_detected, mode, fps, latency))
                self.connection.commit()
            except Error as e:
                print(f"Error logging detection: {e}")

    def log_benchmark(self, cpu_fps, gpu_fps, cpu_latency, gpu_latency):
        """Log benchmark results."""
        if self.connection and self.connection.is_connected():
            try:
                cursor = self.connection.cursor()
                query = "INSERT INTO benchmarks (cpu_fps, gpu_fps, cpu_latency_ms, gpu_latency_ms) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (cpu_fps, gpu_fps, cpu_latency, gpu_latency))
                self.connection.commit()
            except Error as e:
                print(f"Error logging benchmark: {e}")

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")
