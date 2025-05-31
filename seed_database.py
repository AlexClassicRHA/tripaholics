"""Script to seed database."""

import os
import json
import time
from random import choice, randint
from datetime import datetime
from sqlalchemy import create_engine, text
from argon2 import PasswordHasher
from model import User, Trip, db, connect_to_db
import crud
import server
import model


def recreate_db():
    # Подключение к системной базе с AUTOCOMMIT
    sys_engine = create_engine(
        'postgresql://postgres:000000@localhost:5432/postgres',
        isolation_level="AUTOCOMMIT"
    )
    
    try:
        with sys_engine.connect() as conn:
            # Завершаем ВСЕ подключения к базе trips
            conn.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'trips'
            """))
            
            # Даем время на завершение процессов
            time.sleep(1)
            
            # Удаляем базу данных
            conn.execute(text("DROP DATABASE IF EXISTS trips"))
            
            # Создаем новую базу
            conn.execute(text("CREATE DATABASE trips"))
            
            print("База данных успешно пересоздана")
    except Exception as e:
        print(f"Ошибка при пересоздании базы: {e}")
    finally:
        # Закрываем соединение с системной базой
        sys_engine.dispose()


ph = PasswordHasher()

recreate_db()
time.sleep(2)

model.connect_to_db(server.app)
model.db.create_all()



#os.system("dropdb trips")
#os.system("createdb trips")

#os.system(r'"C:\Program Files\PostgreSQL\17\bin\dropdb" trips')
#os.system(r'"C:\Program Files\PostgreSQL\17\bin\dropdb" trips')


def fake_users():
    """Create fake users into database."""

    #User.query.delete()
    #model.db.session.commit()

    nick = crud.create_user(fname="Nick", lname="Whitlock", email="nick@gmail.com", password=ph.hash("123456"))
    amanda = crud.create_user(fname="Amanda", lname="Katz", email="amanda@gmail.com", password=ph.hash("1234")) 
    # raquel = crud.create_user(fname="Raquel", lname="Pfeifle", email="raquel@gmail.com", password=ph.hash("1234"))

    # model.db.session.add(nick)
    model.db.session.add_all([nick, amanda])
    model.db.session.commit()


# Load destinations data from JSON file
with open("data/destinations_imgs.json") as file:
    destinations_data = json.loads(file.read())

# Create trips, store them in a list so we 
# can use them to create fake destinations
imgs_in_db = []

for destination in destinations_data:
    city_name, place_name, description, url = (
        destination["city_name"],
        destination["place_name"],
        destination["description"],
        destination["url"],
    )

    db_images = crud.create_image(place_name, city_name, description, url)
    imgs_in_db.append(db_images)

model.db.session.add_all(imgs_in_db)
model.db.session.commit()


if __name__ == "__main__":

    fake_users()