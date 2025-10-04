from db import get_db_cursor

with get_db_cursor() as cursor:
    cursor.execute("SELECT GETDATE()")
    row = cursor.fetchone()
    print("Connexion OK, date SQL Server :", row[0])
