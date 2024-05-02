import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCalendarWidget,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
)
import psycopg2
import psycopg2.extras

from connection import ConnectionManager
from addlesson import AddLesson
from attendance import AttendanceWindow
from groups import GroupWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Логин")
        self.setGeometry(100, 100, 300, 150)

        self.password_label = QLabel("Пароль:", self)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.student_button = QPushButton("Зайти как студент", self)
        self.teacher_button = QPushButton("Зайти как учитель", self)

        layout = QVBoxLayout()
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.student_button)
        layout.addWidget(self.teacher_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


class MainWindow(QMainWindow):
    def __init__(self, connection: ConnectionManager):
        super().__init__()
        self.setWindowTitle("Главное меню")
        self.setGeometry(100, 100, 400, 200)
        self.connection: ConnectionManager = connection

        self.attendance_button = QPushButton("Посмотреть расписание", self)
        self.attendance_button.clicked.connect(self.show_schedule_window)

        self.grades_button = QPushButton("Информация о группах", self)
        self.grades_button.clicked.connect(self.show_group_window)

        layout = QVBoxLayout()
        layout.addWidget(self.attendance_button)
        layout.addWidget(self.grades_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_schedule_window(self):
        self.schedule_window = ScheduleWindow(self.connection)
        self.schedule_window.show()

    def show_group_window(self):
        self.group_window = GroupWindow(self.connection)
        self.group_window.show()


class ScheduleWindow(QMainWindow):
    def __init__(self, connection: ConnectionManager):
        super().__init__()
        self.setWindowTitle("Расписание")
        self.setGeometry(100, 100, 800, 700)

        self.connection: ConnectionManager = connection
        self.calendar = QCalendarWidget(self)
        self.group_combo = QComboBox(self)
        self.seq_combo = QComboBox(self)
        self.label = QLabel(self)
        self.label.setText("Выберите дату и группу")
        self.seq_combo.addItems(str(i) for i in range(1, 11))
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM groups")
                groups = cursor.fetchall()
                for group in groups:
                    self.group_combo.addItem(group[1], group[0])
        self.view_button = QPushButton("Показать расписание", self)
        self.view_button.clicked.connect(self.view_lessons)
        self.list_widget = QListWidget()

        # Создаем компоновщик и добавляем виджеты
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.calendar)
        main_layout.addWidget(self.group_combo)
        main_layout.addWidget(self.seq_combo)
        main_layout.addWidget(self.view_button)
        main_layout.addWidget(self.label)

        main_layout.addWidget(self.list_widget)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Устанавливаем компоновщик для главного виджета
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def view_lessons(self):
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                group_id = self.group_combo.itemData(self.group_combo.currentIndex())
                data = []
                for i in range(1, 9):
                    cursor.execute(
                        (
                            "select attendanceid, subject from groupattendance where groupid = %s and date = %s and num = %s"
                        ),
                        (group_id, date, i),
                    )
                    row = cursor.fetchone()
                    if row:
                        data.append(dict(row))
                    else:
                        data.append(dict())
                self.list_widget.clear()
        for num, row in enumerate(data):
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)

            # Текстовая метка с именем

            if row:
                label = QLabel(f"{num+1}: {row['subject']}", self)
                item_layout.addWidget(label)
                check_button = QPushButton("Открыть посещаемость", self)
                check_button.clicked.connect(
                    lambda _, group_id=group_id, date=date, num=num: self.show_attendance(
                        group_id, date, num + 1
                    )
                )
                item_layout.addWidget(check_button)
                if self.connection.user == "teacher":
                    add_button = QPushButton("Изменить занятие", self)
                    add_button.clicked.connect(
                        lambda _, date=date, group_id=group_id, num=num: self.add_lesson(
                            group_id, date, num + 1
                        )
                    )
                    item_layout.addWidget(add_button)
                    delete_button = QPushButton("Удалить занятие", self)
                    delete_button.clicked.connect(
                        lambda _, date=date, group_id=group_id, num=num: self.delete_lesson(
                            group_id, date, num + 1
                        )
                    )
                    item_layout.addWidget(delete_button)
            else:
                if self.connection.user == "teacher":
                    add_button = QPushButton("Добавить занятие", self)
                    add_button.clicked.connect(
                        lambda _, date=date, group_id=group_id, num=num: self.add_lesson(
                            group_id, date, num + 1
                        )
                    )
                    item_layout.addWidget(add_button)
                else:
                    label = QLabel(f"{num+1}: Нет занятия", self)
                    item_layout.addWidget(label)

            # Устанавливаем item_widget в качестве виджета элемента
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def show_attendance(self, group_id, date, seq):
        self.AttendanceWindow = AttendanceWindow(self.connection, group_id, date, seq)
        self.AttendanceWindow.show()

    def add_lesson(self, group_id, date, seq):
        self.AddLessonWindow = AddLesson(self.connection, group_id, date, seq, self)
        self.AddLessonWindow.show()

    def delete_lesson(self, group_id, date, seq):
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from deletelesson(%s, %s, %s)", (group_id, date, seq)
                )
                cursor.connection.commit()
        self.view_lessons()

    def view_attendance(self):
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                group_id = self.group_combo.itemData(self.group_combo.currentIndex())
                seq = int(self.seq_combo.currentText())
                cursor.execute(
                    (
                        "Select a.attendanceid, s.firstname, s.surname, s.patronymic, s.cardid, a.status from studentattendance sa "
                        "join groupattendance ga on ga.groupid = %s "
                        "join attendance a on sa.attendanceid = a.attendanceid "
                        "join students s on a.studentid = s.studentid "
                        "where ga.date = %s and ga.num = %s and sa.groupattendanceid = ga.attendanceid "
                    ),
                    (group_id, date, seq),
                )
                data = cursor.fetchall()
                for row in data:
                    row = dict(row)
                    print(row)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT groupname FROM groups WHERE groupid = %s", (group_id,)
                )
                group = cursor.fetchone()
                cursor.execute(
                    "SELECT subject FROM groupattendance WHERE groupid = %s AND date = %s AND num = %s",
                    (group_id, date, seq),
                )
                subject = cursor.fetchone()
        if data:
            self.label.setText(
                f"Посещаемость группы {group[0]} на {seq} занятии {date} по предмету {subject[0]}"
            )
        else:
            self.label.setText(
                f"Занятие в группе {group[0]} на {seq} занятии {date} не запланировано"
            )
        self.list_widget.clear()
        # Создаем элементы списка
        for row in data:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)

            # Текстовая метка с именем
            label = QLabel(
                " ".join(
                    [row["firstname"], row["surname"], row["patronymic"], row["cardid"]]
                )
            )
            item_layout.addWidget(label)

            # ComboBox с текущим значением
            combo_box = QComboBox()
            combo_box.addItems(["Н", "У", "+"])
            combo_box.setCurrentText(row["status"])
            item_layout.addWidget(combo_box)
            if self.connection.user == "teacher":
                # Кнопка для отправки изменений в базу данных
                button = QPushButton("Отметить")
                button.clicked.connect(
                    lambda _, id=row[
                        "attendanceid"
                    ], combo_box=combo_box: self.update_attendance(
                        id, combo_box.currentText()
                    )
                )
                item_layout.addWidget(button)
            else:
                combo_box.setDisabled(True)

            # Устанавливаем item_widget в качестве виджета элемента
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)


class App:
    def __init__(self):
        self.login_window = LoginWindow()
        self.conn = None
        self.login_window.student_button.clicked.connect(
            lambda: self.login("student", self.login_window.password_entry.text())
        )
        self.login_window.teacher_button.clicked.connect(
            lambda: self.login("teacher", self.login_window.password_entry.text())
        )
        self.login_window.show()

    def login(self, user_type, password):
        dbname = "students"
        host = "localhost"
        port = "5432"
        connection = None
        try:
            # Подключение к базе данных
            if user_type == "teacher":
                connection = psycopg2.connect(
                    dbname=dbname,
                    user="teacher",
                    password=password,
                    host=host,
                    port=port,
                )
            elif user_type == "student":
                connection = psycopg2.connect(
                    dbname=dbname,
                    user="student",
                    password=password,
                    host=host,
                    port=port,
                )
            else:
                print("Неверная роль пользователя")
                return None
            self.login_window.close()
            self.conn = ConnectionManager(dbname, user_type, password, host, port)
            self.open_main_window()

        except (Exception, psycopg2.Error) as error:
            print("Ошибка при работе с PostgreSQL:", error)
        finally:
            if connection:
                connection.close()
            return self.conn

    def open_main_window(self):
        self.main_window = MainWindow(self.conn)
        self.main_window.show()


class PlanWindow(QMainWindow):
    def __init__(self, connection: ConnectionManager):
        super().__init__()
        self.setWindowTitle("Plan Lesson")
        self.setGeometry(100, 100, 800, 700)
        layout = QVBoxLayout()
        self.connection: ConnectionManager = connection
        self.calendar = QCalendarWidget(self)
        self.group_combo = QComboBox(self)
        self.subject_combo = QComboBox(self)
        self.seq_combo = QComboBox(self)
        self.plan_button = QPushButton("Plan Lesson", self)
        self.result = QLabel(self)
        self.result.setText("Планирование занятия")
        self.seq_combo.addItems(str(i) for i in range(1, 11))
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM groups")
                groups = cursor.fetchall()
                for group in groups:
                    self.group_combo.addItem(group[1], group[0])

                cursor.execute("SELECT subject FROM subject")
                subjects = cursor.fetchall()
                for subject in subjects:
                    self.subject_combo.addItem(subject[0])

        self.plan_button.clicked.connect(self.plan_lesson)
        widget = QWidget()
        layout.addWidget(self.calendar)
        layout.addWidget(self.group_combo)
        layout.addWidget(self.subject_combo)
        layout.addWidget(self.seq_combo)
        layout.addWidget(self.plan_button)
        layout.addWidget(self.result)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def plan_lesson(self):
        try:
            with self.connection as connection:
                with connection.cursor(
                    cursor_factory=psycopg2.extras.DictCursor
                ) as cursor:
                    date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                    group_id = self.group_combo.itemData(
                        self.group_combo.currentIndex()
                    )
                    subject = self.subject_combo.currentText()
                    seq = int(self.seq_combo.currentText())
                    cursor.execute(
                        "Select * from PlanLesson(%s, %s, %s, %s)",
                        (group_id, subject, date, seq),
                    )
                    cursor.connection.commit()
        except Exception as e:
            self.result.setText("Ошибка при планировании занятия")
            print(e)
        else:
            self.result.setText(
                f"Планирование занятия {self.gro} для группы {self.group_combo.currentText()} прошло успешно"
            )


def main():
    app = QApplication(sys.argv)
    my_app = App()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
