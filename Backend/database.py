import mysql.connector

from Backend.config import DB_CONFIG as config


class DatabaseAPI:
    def __init__(self):
        pass

    @staticmethod
    def is_user_registered(username):
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = f"SELECT COUNT(*) FROM users WHERE username = '{username}'"
                cursor.execute(sql)

                result = cursor.fetchone()
                count = result[0]

                if count > 0:
                    return True
                else:
                    return False

        except mysql.connector.Error as e:
            print(f"Error conectándose a la base de datos MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def register_user(username, full_name, password, public_key, cyphered_private_key):
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = f"INSERT INTO users (username, password, full_name, public_key, cyphered_private_key) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (username, password, full_name, public_key, cyphered_private_key))

                connection.commit()
        except mysql.connector.Error as e:
            print(f"Error conectándose a la base de datos MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def delete_user(username):
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = f"delete from users where username = '{username}'"
                cursor.execute(sql)

                connection.commit()
        except mysql.connector.Error as e:
            print(f"Error conectándose a la base de datos MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_user_password(username):
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = "SELECT password FROM users WHERE username = %s"
                cursor.execute(sql, (username,))

                result = cursor.fetchone()
                password = result[0]
                return password

        except mysql.connector.Error as e:
            print(f"Error conectándose a la base de datos MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_user_public_key(username):
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = "SELECT public_key FROM users WHERE username = %s"
                cursor.execute(sql, (username,))

                result = cursor.fetchone()
                cyphered_private_key = result[0]
                return cyphered_private_key

        except mysql.connector.Error as e:
            print(f"Error conectándose a la base de datos MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_user_cyphered_private_key(username):
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = "SELECT cyphered_private_key FROM users WHERE username = %s"
                cursor.execute(sql, (username,))

                result = cursor.fetchone()
                cyphered_private_key = result[0]
                return cyphered_private_key

        except mysql.connector.Error as e:
            print(f"Error conectándose a la base de datos MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_all_users():
        try:
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                cursor = connection.cursor()
                sql = "SELECT username,full_name FROM users"
                cursor.execute(sql)

                result = cursor.fetchall()
                users = []
                for fila in result:
                    users.append({"username": fila[0], "full_name": fila[1]})

                return users

        except mysql.connector.Error as e:
            print(f"Error conectándose a la base de datos MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()