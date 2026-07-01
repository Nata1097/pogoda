import sqlite3

def init_db():
    """Database creation."""
    conn = sqlite3.connect("pogoda.db")
    cursor = conn.cursor()
    
    # Creates the weather_outfit_logs table if it does not exist.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_outfit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            apparent_temperature REAL,
            wind_speed REAL,
            clothing_top TEXT,
            clothing_bottom TEXT,
            clothing_jacket TEXT,
            clothing_accessories TEXT,
            feeling TEXT,
            activity TEXT,
            comment TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def save_weather_to_db(weather_data):
    """Takes a dictionary with weather and outfit data and saves it into the database."""
    conn = sqlite3.connect("pogoda.db")
    cursor = conn.cursor()
    
    # Insert data from dictionary to table
    cursor.execute("""
        INSERT INTO weather_outfit_logs (
            timestamp, temperature, apparent_temperature, wind_speed,
            clothing_top, clothing_bottom, clothing_jacket, clothing_accessories,
            feeling, activity, comment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        weather_data["timestamp"], 
        weather_data["temperature"], 
        weather_data["apparent_temperature"], 
        weather_data["wind_speed"],
        weather_data["clothing_top"],
        weather_data["clothing_bottom"],
        weather_data["clothing_jacket"],
        weather_data["clothing_accessories"],
        weather_data["feeling"],
        weather_data["activity"],
        weather_data["comment"]
    ))
    
    conn.commit()
    conn.close()
    print("Data successfully saved to the database.")