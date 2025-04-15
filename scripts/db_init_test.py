import pyodbc
import os

# Hämta värden från miljövariabler (använder standardvärden om variablerna inte är satta)
rds_host = os.environ.get('RDS_HOST', 'database-2.ch0eo28sely1.eu-central-1.rds.amazonaws.com')
rds_user = os.environ.get('RDS_USER', 'admin')
rds_password = os.environ.get('RDS_PASSWORD', 'grupp1ai')
rds_db_name = os.environ.get('RDS_DB_NAME', 'SmartFarming')
rds_port = os.environ.get('RDS_PORT', '1433')

# Sätt ihop anslutningssträngen
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={rds_host},{rds_port};'
    f'DATABASE={rds_db_name};'
    f'UID={rds_user};'
    f'PWD={rds_password};'
)

# Försök att upprätta en anslutning
try:
    connection = pyodbc.connect(conn_str, timeout=5)
    print("Connection successful!")
except pyodbc.Error as e:
    print("Failed to connect to the database.")
    print(f"Error: {e}")
    connection = None

# Om anslutning lyckades, skapa en cursor och säkerställ att tabellerna finns
if connection is not None:
    cursor = connection.cursor()

    # Skapa tabellen IrrigationLogs om den inte redan finns
    def ensure_irrigation_table_exists(cursor):
        cursor.execute("USE SmartFarming")
        create_query = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'IrrigationLogs')
        BEGIN
            CREATE TABLE IrrigationLogs (
                timestamp BIGINT,
                temperature FLOAT,
                soil_moisture FLOAT,
                humidity FLOAT,
                light FLOAT,
                decision NVARCHAR(100)
            )
        END
        """
        cursor.execute(create_query)

    # Skapa tabellen LeafAnalysisResults om den inte redan finns
    def ensure_leaf_table_exists(cursor):
        cursor.execute("USE SmartFarming")
        create_query = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'LeafAnalysisResults')
        BEGIN
            CREATE TABLE LeafAnalysisResults (
                image NVARCHAR(255),
                timestamp BIGINT,
                labels NVARCHAR(MAX),
                disease_detected BIT
            )
        END
        """
        cursor.execute(create_query)

    # Skapa tabellen Väderdata om den inte redan finns
    def ensure_weather_table_exists(cursor):
        cursor.execute("USE SmartFarming")
        create_query = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Väderdata')
        BEGIN
            CREATE TABLE Väderdata (
                timestamp BIGINT,
                temperatur FLOAT,
                luftfuktighet FLOAT,
                nederbord FLOAT,
                ljusintensitet FLOAT
            )
        END
        """
        cursor.execute(create_query)

    # Anropa funktionerna för att säkerställa att tabellerna finns
    try:
        ensure_irrigation_table_exists(cursor)
        ensure_leaf_table_exists(cursor)
        ensure_weather_table_exists(cursor)
        connection.commit()  # Spara ändringar i databasen
        print("Tables ensured successfully.")
    except pyodbc.Error as e:
        print("Error ensuring tables:", e)
    finally:
        cursor.close()
        connection.close()
