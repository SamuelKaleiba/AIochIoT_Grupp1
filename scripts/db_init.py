# db_init.py – innehåller funktioner för att skapa tabeller automatiskt om de inte finns

def ensure_irrigation_table_exists(cursor):
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
