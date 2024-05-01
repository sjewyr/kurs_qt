import psycopg2


class ConnectionManager:
    def __init__(self, dbname, user, password, host, port):
        self.__dbname = dbname
        self.user = user
        self.__password = password
        self.__host = host
        self.__port = port

    def __enter__(self):
        self.connection = psycopg2.connect(
            dbname=self.__dbname,
            user=self.user,
            password=self.__password,
            host=self.__host,
            port=self.__port,
            client_encoding="utf8",
        )
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()
