import os

# Con MySQL se usa PyMySQL (no necesita compilar nada). Se presenta a Django como "MySQLdb".
if os.environ.get("DB_ENGINE", "mysql") == "mysql":
    try:
        import pymysql

        pymysql.version_info = (2, 2, 1, "final", 0)
        pymysql.install_as_MySQLdb()
    except ImportError:  # PyMySQL no está instalado (por ejemplo, al usar SQLite)
        pass
