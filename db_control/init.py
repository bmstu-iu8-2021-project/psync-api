import psycopg2
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def connect():
    connection = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
    connection.autocommit = True
    return connection


def create():
    connection = connect()

    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons
            (
                id       serial      NOT NULL PRIMARY KEY,
                login    varchar(20) NOT NULL UNIQUE,
                email    varchar(50) NOT NULL UNIQUE,
                password varchar(60) NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS hosts
            (
                id  serial      NOT NULL PRIMARY KEY,
                mac varchar(30) NOT NULL UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS agent
            (
                id        serial NOT NULL PRIMARY KEY,
                person_id int    NOT NULL,
                host_id   int    NOT NULL,
                FOREIGN KEY (person_id) REFERENCES persons (id) ON DELETE CASCADE,
                FOREIGN KEY (host_id) REFERENCES hosts (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS resources
            (
                id       serial       NOT NULL PRIMARY KEY,
                agent_id int          NOT NULL,
                path     varchar(300) NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agent (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS replica_set
            (
                id                  serial NOT NULL PRIMARY KEY,
                current_resource_id int    NOT NULL,
                other_resource_id   int    NOT NULL,
                FOREIGN KEY (current_resource_id) REFERENCES resources (id) ON DELETE CASCADE,
                FOREIGN KEY (other_resource_id) REFERENCES resources (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS versions
            (
                id          serial       NOT NULL PRIMARY KEY,
                resource_id int          NOT NULL,
                version     varchar(20)  NOT NULL,
                created_at  timestamp    NOT NULL,
                is_actual   bool         NOT NULL,
                path        varchar(300) NOT NULL,
                FOREIGN KEY (resource_id) REFERENCES resources (id) ON DELETE CASCADE
            );
        ''')
    connection.close()


def close(connection):
    connection.close()
