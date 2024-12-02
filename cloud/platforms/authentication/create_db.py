import sys

import environ
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

env = environ.Env()
# Retrieve environment variables from .env file
environ.Env.read_env(".env")

environment = env.str("ENVIRONMENT")
db_name = env.str("DB_NAME")
db_user = env.str("DB_USERNAME")
db_password = env.str("DB_PASSWORD")
db_host = env.str("DB_HOST")
db_port = env.str("DB_PORT")


def get_db_name() -> str:
    if environment == "local":
        db_name = "test_authentication"
    else:
        db_name = "authentication"
    return db_name


def create_db() -> None:
    print(f"Attempting creation DB: {db_name}")
    connection = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        dbname="postgres",
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {get_db_name()}")
            print(f"Created DB: {get_db_name()}")
    except psycopg2.errors.DuplicateDatabase:  # pylint: disable=E1101
        print(f"Database {get_db_name()} already exists, skipping")
    finally:
        if connection:
            connection.close()
    print("Done creating DB")


if __name__ == "__main__":
    create_db()
    sys.exit(0)
