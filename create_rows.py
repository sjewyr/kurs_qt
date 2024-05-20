from connection import ConnectionManager
import datetime
from random import choice
import time

conn = ConnectionManager("students", "teacher", "teacher", "localhost", 5432)


def bloat_attendance(conn: ConnectionManager):
    start_date = datetime.date(2024, 5, 1)
    end_date = datetime.date(2024, 6, 30)
    subj = ["Русский язык", "Математика", "Биология"]
    current_date = start_date
    with conn as connection:
        with connection.cursor() as cursor:
            cursor.execute("select groupid from groups")
            groups = cursor.fetchall()
            while current_date <= end_date:
                for grid in groups:
                    grid = grid[0]
                    for num in range(1, 5):
                        # Преобразуем объект даты в строку в формате 'YYYY-MM-DD'
                        date_str = current_date.strftime("%Y-%m-%d")
                        subject = choice(subj)
                        # Вставляем дату в базу данных
                        try:

                            cursor.execute(
                                "SELECT * FROM planlesson (%s, %s, %s, %s)",
                                (grid, subject, date_str, num),
                            )
                            cursor.connection.commit()

                        except Exception as e:
                            cursor.connection.rollback()
                            print(
                                f"Error inserting {date_str} into groupattendance, {e}"
                            )
                        else:
                            print(f"{date_str} successfully")
                        # Переходим к следующей дате
                current_date += datetime.timedelta(days=1)


def bloat_students(conn: ConnectionManager):
    fnames = [
        "Мария",
        "Степан",
        "Вениамин",
        "Рафаэль",
        "Зигмунд",
        "Рустам",
        "Джамал",
        "Григорий",
        "Андрей",
        "Павел",
    ]
    snames = [
        "Иванов",
        "Петров",
        "Романов",
        "Булков",
        "Плюшкин",
        "Хлебобулочкин",
        "Анекдотов",
        "Сусликов",
    ]
    pats = [
        "Иванович",
        "Артемович",
        "Русланович",
        "Исламович",
        "Григорьевич",
        "Романович",
        "Андреевич",
        "Степанович",
    ]
    with conn as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT groupid FROM groups")
            groups = cursor.fetchall()
            for grid in groups:
                grid = grid[0]
                cursor.execute(
                    "select count(*) from students where groupid = %s", (grid,)
                )
                count = cursor.fetchone()[0]
                print(count)
                if count >= 10:
                    print(f"Группа {grid} переполнена")
                    continue
                for i in range(30):
                    try:
                        cursor.execute(
                            "SELECT * FROM add_student(%s, %s, %s, %s)",
                            (choice(fnames), choice(snames), choice(pats), grid),
                        )
                        cursor.connection.commit()
                    except:
                        cursor.connection.rollback()


def append_zeros(data):
    if len(str(data)) == 1:
        return "0" + (str(data)[0])
    else:
        return str(data)


def bloat_groups(conn: ConnectionManager):
    patterns = [
        "БСБО-{}-{}",
        "БФБО-{}-{}",
        "БББО-{}-{}",
        "БПБО-{}-{}",
        "БДБО-{}-{}",
        "БРБО-{}-{}",
        "БКБО-{}-{}",
        "ИББО-{}-{}",
        "ИМБО-{}-{}",
        "ИЗБО-{}-{}",
        "БСБС-{}-{}",
        "БМБО-{}-{}",
    ]
    patterns = patterns[0:3]
    with conn as connection:
        with connection.cursor() as cursor:
            for z in range(len(patterns)):
                for i in range(1, 5):
                    for j in range(19, 24):
                        try:
                            cursor.execute(
                                "SELECT * FROM create_group (%s)",
                                (patterns[z].format(append_zeros(i), str(j)),),
                            )
                            cursor.connection.commit()
                        except Exception as e:
                            cursor.connection.rollback()
                            print(
                                f"Error inserting {patterns[z].format(append_zeros(i), j)} into groups, {e}"
                            )
                        else:
                            print(
                                f"{patterns[z].format(append_zeros(i), j)} successfully"
                            )


def fix_card_id(conn: ConnectionManager):
    with conn as connection:
        with connection.cursor() as cursor:
            cursor.execute("select studentid, cardid from students")
            students = cursor.fetchall()
            for student in students:
                studentid = student[0]
                cardid = student[1]
                if len(cardid) == 7:
                    raise Exception("ТЫ ЧЕ БЛЯТЬ ДЕЛАЕШЬ УРОД ЩАС ВСЕ ПО ПИЗДЕ ПОЙДЕТ")
                try:
                    card = [cardid[0:2], cardid[2:]]
                    card[1] = "0" + card[1]
                    print(card[0] + card[1])
                    cursor.execute(
                        "UPDATE students SET cardid = %s WHERE studentid = %s",
                        (card[0] + card[1], studentid),
                    )
                    cursor.connection.commit()
                except Exception as e:
                    cursor.connection.rollback()
                    print(f"Error inserting {studentid+1} into students, {e}")
                else:
                    print(f"{studentid+1} successfully")


bloat_groups(conn)

bloat_students(conn)

bloat_attendance(conn)
