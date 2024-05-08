from PyQt5.QtWidgets import (
    QMainWindow,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QWidget,
)

from connection import ConnectionManager


class AddGradeWindow(QMainWindow):
    def __init__(
        self,
        connection: ConnectionManager,
        student_id,
        subject=None,
        gradeid=None,
        previous=None,
    ):
        super().__init__()
        self.connection: ConnectionManager = connection
        self.subject = subject
        self.student_id = student_id
        self.gradeid = gradeid
        self.previous = previous
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить оценку")
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()
        subjectlabel = QLabel("Введите предмет", self)
        self.subject_combo = QComboBox(self)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT subject FROM subject")
                subjects = cursor.fetchall()
                for subject in subjects:
                    self.subject_combo.addItem(subject[0])
        self.subject_combo.setEditable(True)
        self.subject_combo.setInsertPolicy(QComboBox.NoInsert)
        self.subject_combo.lineEdit().setClearButtonEnabled(True)
        if self.subject:
            self.subject_combo.setCurrentText(self.subject)
            self.subject_combo.setEnabled(False)

        gradelabel = QLabel("Введите оценку", self)
        self.grade_combo = QComboBox(self)
        self.grade_combo.addItems(str(i) for i in range(2, 6))
        commentlabel = QLabel("Введите комментарий", self)
        self.comment_edit = QTextEdit(self)
        if self.gradeid:
            self.button = QPushButton("Обновить", self)
            with self.connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT grade, comment FROM grades WHERE gradeid = %s",
                        (self.gradeid,),
                    )
                    data = cursor.fetchone()
                    print(data)
                    self.grade = data[0]
                    self.comment = data[1]
                    print(self.comment)
            self.grade_combo.setCurrentText(str(self.grade))
            self.comment_edit.setText(self.comment)
            self.button.clicked.connect(self.update_grade)
        else:
            self.button = QPushButton("Добавить", self)
            self.button.clicked.connect(self.add_grade)

        self.layout.addWidget(subjectlabel)
        self.layout.addWidget(self.subject_combo)
        self.layout.addWidget(gradelabel)
        self.layout.addWidget(self.grade_combo)
        self.layout.addWidget(commentlabel)
        self.layout.addWidget(self.comment_edit)
        self.layout.addWidget(self.button)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)

    def add_grade(self):
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO grades (subject, grade, studentid, comment) VALUES (%s, %s, %s, %s)",
                    (
                        self.subject_combo.currentText(),
                        int(self.grade_combo.currentText()),
                        self.student_id,
                        self.comment_edit.toPlainText(),
                    ),
                )
                cursor.connection.commit()
        if self.previous:
            self.previous.show_grades()

    def update_grade(self):
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE grades SET grade = %s, comment = %s WHERE gradeid = %s",
                    (
                        int(self.grade_combo.currentText()),
                        self.comment_edit.toPlainText(),
                        self.gradeid,
                    ),
                )
                cursor.connection.commit()
        if self.previous:
            self.previous.show_grades()
