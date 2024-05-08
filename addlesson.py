from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QComboBox,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
from connection import ConnectionManager
import psycopg2


class AddLesson(QMainWindow):
    def __init__(
        self, connection: ConnectionManager, group_id, date, seq, lesson_window
    ):
        super().__init__()
        self.connection = connection
        self.init_ui()
        self.group_id = group_id
        self.date = date
        self.seq = seq
        self.lesson_window = lesson_window

    def init_ui(self):
        self.setWindowTitle("Добавить занятие")
        self.setGeometry(100, 100, 300, 150)
        self.layout = QVBoxLayout()
        self.resultlabel = QLabel(self)
        label = QLabel("Введите название предмета", self)
        self.subject_combo = QComboBox(self)
        self.button = QPushButton("Добавить", self)
        with self.connection as conn:
            with conn.cursor() as cursor:

                cursor.execute("SELECT subject FROM subject")
                subjects = cursor.fetchall()
                for subject in subjects:
                    self.subject_combo.addItem(subject[0])
        self.subject_combo.setEditable(True)
        self.subject_combo.setInsertPolicy(QComboBox.NoInsert)
        self.subject_combo.lineEdit().setClearButtonEnabled(True)
        self.centralWidget = QWidget(self)
        self.layout.addWidget(label)
        self.layout.addWidget(self.subject_combo)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.resultlabel)
        self.centralWidget.setLayout(self.layout)
        self.button.clicked.connect(self.add_lesson)
        self.setCentralWidget(self.centralWidget)

    def add_lesson(self):
        try:
            with self.connection as connection:
                with connection.cursor(
                    cursor_factory=psycopg2.extras.DictCursor
                ) as cursor:
                    exists = cursor.execute(
                        "SELECT * FROM CheckLesson(%s,%s,%s)",
                        (self.group_id, self.date, self.seq),
                    )
                    exists = cursor.fetchone()[0]
                    print(exists)
                    if not exists:
                        subject = self.subject_combo.currentText()
                        cursor.execute(
                            "Select * from PlanLesson(%s, %s, %s, %s)",
                            (self.group_id, subject, self.date, self.seq),
                        )
                    else:
                        subject = self.subject_combo.currentText()
                        cursor.execute(
                            "Select * from UpdateLesson(%s, %s, %s, %s)",
                            (self.group_id, subject, self.date, self.seq),
                        )
                    cursor.connection.commit()
        except Exception as e:
            self.resultlabel.setText("Ошибка при планировании занятия")
            print(e)
        else:
            self.resultlabel.setText(f"Планирование занятия {subject} прошло успешно")
            self.lesson_window.view_lessons()
