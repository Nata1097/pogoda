import sqlite3

def init_db():
    """Database creation."""
    conn = sqlite3.connect("pogoda.db")
    cursor = conn.cursor()
    
    # Creates the database and the weather_logs table if they do not exist.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            apparent_temperature REAL,
            wind_speed REAL
        )
    """)
    
    conn.commit()
    conn.close()

def save_weather_to_db(weather_data):
    """Takes a dictionary with weather data and saves it into the database."""
    conn = sqlite3.connect("pogoda.db")
    cursor = conn.cursor()
    
    # Insert data from dictionary to table
    cursor.execute("""
        INSERT INTO weather_logs (timestamp, temperature, apparent_temperature, wind_speed)
        VALUES (?, ?, ?, ?)
    """, (
        weather_data["timestamp"], 
        weather_data["temperature"], 
        weather_data["apparent_temperature"], 
        weather_data["wind_speed"]
    ))
    
    conn.commit()
    conn.close()
    print("Weather data successfully saved to the database.")