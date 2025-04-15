# db_init.py – innehåller funktioner för att skapa tabeller automatiskt om de inte finns


def ensure_irrigation_table_exists(cursor):
    cursor.execute("USE RDSadmin")
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


def ensure_leaf_table_exists(cursor):
    cursor.execute("USE RDSadmin")
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

def ensure_weather_table_exists(cursor):
    cursor.execute("USE RDSadmin")
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



