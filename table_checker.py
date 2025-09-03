from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker


def list_tables_and_data(engine):
    # Загрузка метаданных из базы данных
    metadata = MetaData()
    metadata.reflect(engine)  # reflect method loads the table structure

    # Получение списка таблиц в базе данных MySQL
    table_names = metadata.tables.keys()

    print("Список таблиц в базе данных MySQL:")
    print("=" * 40)
    for table_name in table_names:
        print(f"- {table_name}")
    print("=" * 40)

    # Проверка данных в каждой таблице
    for table_name in table_names:
        print(f"\nДанные в таблице: {table_name}")
        print("=" * 40)
        table_mysql = Table(table_name, metadata, autoload_with=engine)
        query = session.query(table_mysql).limit(5)
        results = query.all()

        if results:
            for row in results:
                print(row)
        else:
            print("Нет данных")
        print("=" * 40)


if __name__ == "__main__":
    # Подключение к облачной базе данных MySQL
    DATABASE_URI_MYSQL = 'mysql+pymysql://user1:Ps123456@147.45.138.165:3306/psadmin_db?charset=utf8mb4'
    engine_mysql = create_engine(DATABASE_URI_MYSQL)
    SessionMySQL = sessionmaker(bind=engine_mysql)
    session = SessionMySQL()

    # Вызов функции для вывода списка таблиц и их данных
    list_tables_and_data(engine_mysql)

    # Закрытие соединения
    session.close()
