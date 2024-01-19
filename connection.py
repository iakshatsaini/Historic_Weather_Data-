import psycopg2

# database credentials
db_host = 'localhost'
db_port = '5432'
db_name = 'postgres'
db_user = 'postgres'
db_password = 'mypassword'

# Establish a connection to the PostgreSQL database
def postgre_sql_connection():
    try:
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = connection.cursor()
        return connection, cursor
    except psycopg2.Error as e:
        return f"Error: {e}"
