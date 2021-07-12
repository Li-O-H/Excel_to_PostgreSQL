import sys
import psycopg2
import collections


# Класс, представляющий запрос на создание и заполнение таблицы
class TableCreateAndInsertQuery:
    def __init__(self, name, table):
        self.name = name
        self.table = table

    def set_name(self, name):
        self.name = name

    def get_query(self):
        # Если таблица пустая - ничего не делаем
        if len(self.table) == 0:
            print(f"Таблица {self.name} пустая")
            return ""

        columns = []
        # Названиями колонок считаем поля первой строки
        for i in range(len(self.table[0])):
            columns.append(str(self.table[0][i]))
        records = []

        # Если таблица содержит повторяющиеся колонки - мы не можем ее создать. Ничего не делаем
        if len([item for item, count in collections.Counter(columns).items() if count > 1]) > 0:
            print(f"Таблица {self.name} содержит повторяющиеся названия колонок и не может быть записана")
            return ""

        # None-объекты заменяем на NULL, остальные заключаем в кавычки
        for row in range(len(self.table) - 1):
            records.append([])
            for cell in self.table[row + 1]:
                if cell is None:
                    records[-1].append("NULL")
                else:
                    records[-1].append(f"\'{str(cell)}\'")

        columns_parameters = ""
        for column in columns:
            # Все колонки считаем text
            columns_parameters = f"{columns_parameters}\"{str(column)}\" text,\n"
        columns_parameters = columns_parameters[:len(columns_parameters) - 2]
        table_create_query = f"CREATE TABLE \"{self.name}\"(\n{columns_parameters});"

        insert_query = ""
        # Проверяем, есть ли записи (есть ли больше одной строки)
        if len(records) != 0:
            columns_string = ""
            for column in columns:
                columns_string = f"{columns_string}, \"{str(column)}\""
            columns_string = columns_string[2:]
            values = ""
            for record in records:
                fields = ", ".join(record)
                values = f"{values}({fields}),\n"

            values = values[:len(values) - 2]
            insert_query = f"INSERT INTO \"{self.name}\" ({columns_string})\nVALUES {values};"

        return f"{table_create_query}\n{insert_query}"


def create_queries(tables):
    tables_queries = []
    new_names = []
    for table in tables:
        # Даем пользователю возможность задать имя для создаваемой таблицы
        new_name = input(f"Введите новое имя для таблицы {table.name}: ")
        # Отсекаем повторяющиеся имена
        while new_names.__contains__(new_name):
            new_name = input(f"Имя {new_name} уже было введено. Введите другое имя для таблицы {table.name}: ")
        new_names.append(new_name)
        query = TableCreateAndInsertQuery(new_name, table.table)
        tables_queries.append(query)
    return tables_queries


def connect_to_db(host, port, database, user, password):
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password
        )
    except psycopg2.Error:
        print(f"Ошибка при попытке подключения к базе данных {database}")
        sys.exit(1)
    print(f"Подключение к базе данных {database} успешно создано")
    return connection


def write_queries_to_db(connection, queries):
    cursor = connection.cursor()
    for query in queries:
        completed = False
        while not completed:
            try:
                if query.get_query() != "":
                    cursor.execute(query.get_query())
                    connection.commit()
                completed = True
            except psycopg2.Error as e:
                connection.rollback()
                # Если таблица с таким именем уже есть, даем пользователю изменять имя, пока оно не подойдет
                if e.pgcode == "42P07":
                    query.set_name(input(f"Имя {query.name} занято. Введите новое имя для таблицы: "))
                else:
                    print(f"Во время выполнения запроса для таблицы {query.name} возникла ошибка:\n{e.pgerror}")
                    completed = True
    cursor.close()
    print("Таблицы успешно записаны в базу данных")
