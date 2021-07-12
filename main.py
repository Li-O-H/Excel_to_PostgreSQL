import postgres_writer
import read_excel
import getpass
import sys

if __name__ == '__main__':

    filename = input("Введите имя xlsx файла (или путь к нему): ")
    tables = read_excel.get_tables(filename)
    host = input("Введите адрес хоста базы данных (локальный хост - localhost): ")
    port = int(input("Введите порт, к которому подключена база данных (обычно - 5432): "))
    database = input("Введите название базы данных: ")
    user = input("Введите имя пользователя базы данных: ")
    if sys.stdin.isatty():
        password = getpass.getpass("Введите пароль пользователя базы данных: ")
    else:
        password = input("Введите пароль пользователя базы данных: ")
    connection = postgres_writer.connect_to_db(host, port, database, user, password)
    queries = postgres_writer.create_queries(tables)
    postgres_writer.write_queries_to_db(connection, queries)
    connection.close()
