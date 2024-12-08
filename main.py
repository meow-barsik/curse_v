import sqlite3
import os
import shutil
import sys
import database
from ui_main import Ui_MainWindow
from ui_form import Ui_Form
from ui_auth_reg import Ui_Dialog
from PySide6.QtWidgets import QDialog, QMainWindow, QApplication, QLabel, QFileDialog, QMessageBox
from PySide6.QtGui import QFont, QPixmap
from PIL import Image

global user_id
global form_id
global interes_id


class Auth_Reg(QDialog, Ui_Dialog):
    def __init__(self, main, parent=None):
        super(Auth_Reg, self).__init__(parent)
        self.setupUi(self)
        self.main = main
        self.exec()

    def setupUi(self, Dialog):
        super().setupUi(Dialog)
        self.auth_button.clicked.connect(self.auth)
        self.to_reg_button.clicked.connect(self.go_to_reg)
        self.registr_button.clicked.connect(self.reg)
        self.reg_window.hide()

    def auth(self):
        self.main.username = self.username_input.text()
        self.close()
        self.main.show()


    def go_to_reg(self):
        self.auth_window.hide()
        self.reg_window.show()
        print(1)

    def reg(self):
        username = self.us_input.text()
        mail = self.mail_input.text()
        phone = self.phone_input.text()
        password = self.passwd_input.text()

        connect, curs = database.db_connection()
        curs.execute("INSERT INTO Users (username_user, mail_user, phone_num_user, password_user) VALUES (?,?,?,?)",
                     (username, mail, phone, password))
        connect.commit()

        curs.execute("SELECT id_user FROM Users WHERE username_user = ?", (username,))
        user_id = curs.fetchone()[0]

        curs.execute("INSERT INTO Form (id_user_form) VALUES (?)", (user_id,))
        connect.commit()

        curs.execute("INSERT INTO Interes (id_user_interes) VALUES (?)", (user_id,))
        connect.commit()

        database.db_close(connect)
        Form(self, user_id)


class Form(QDialog, Ui_Form):
    def __init__(self, auth, us_id):
        super().__init__()
        self.auth = auth
        self.user_id = us_id
        self.setupUi(self)


    def setupUi(self, Form):
        super().setupUi(Form)
        self.button_next.clicked.connect(self.go)
        self.add_pic.clicked.connect(self.add_picture)
        self.exec()

    def go(self):
        name = self.name_input.text()
        surname = self.surname_input.text()
        age = self.age_input.text()
        city = self.city_input.text()
        check_box = [[self.theatral, "theatral"], [self.art_check, "art"], [self.music_check, "music"],
                     [self.game_check, "game"], [self.animals_check, "animal"], [self.garden_check, "garden"],
                     [self.vyazanie_check, "vyazanie"], [self.spor_check, "sport"], [self.language_check, "language"],
                     [self.books_check, "books"]]

        connect, curs = database.db_connection()
        curs.execute("UPDATE Form SET name_form=?, surname_form=?, city_form=?, age_form=?",
                     (name, surname, city, age))
        database.db_close(connect)

        connect, curs = database.db_connection()
        for check in check_box:
            if check[0].isChecked() == True:
                curs.execute(f"UPDATE Interes SET {check[1]}=1 WHERE id_user_interes={self.user_id}")
        database.db_close(connect)

        self.close()
        self.auth.auth_window.show()

    def add_picture(self):

        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if self.is_image(file_name):
            project_directory = os.path.join(os.getcwd(), "users_pic")
            os.makedirs(project_directory, exist_ok=True)
            destination = os.path.join(project_directory, os.path.basename(file_name))

            shutil.copy(file_name, destination)
            QMessageBox.information(self, "Успех", f"Аватар добавлен")
            pixmap = QPixmap(destination)
            print(destination)
            self.form_pic.setPixmap(pixmap)
            connect, curs = database.db_connection()
            curs.execute("UPDATE Form SET pic_destination=? WHERE id_user_form=?", (destination, self.user_id))
            database.db_close(connect)

        else:
            QMessageBox.warning(self, "Ошибка", "Файл не является изображением")



    def is_image(self, file_path):
        try:
            img = Image.open(file_path)
            img.verify()
            return True
        except (IOError, SyntaxError):
            return False






class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.user_city = None
        self.username = None
        self.user_id = None
        self.users_sorted = []

        self.auth_window = Auth_Reg(self)
        self.setupUi(self)

    def setupUi(self, window):
        super().setupUi(window)
        self.profile_button.clicked.connect(self.show_profile)
        self.home_button.clicked.connect(self.show_home)
        self.like_button.clicked.connect(self.like)
        self.dis_button.clicked.connect(self.dis)

        connect, curs = database.db_connection()

        curs.execute(f"SELECT id_user FROM Users WHERE username_user={self.username}")
        self.user_id = curs.fetchone()[0]

        curs.execute(f"SELECT pic_destination FROM Form WHERE id_user_form={self.user_id}")
        path_self_pic = str(curs.fetchone()[0])

        curs.execute(f"SELECT name_form, surname_form, city_form, age_form FROM Form WHERE id_user_form={self.user_id}")
        info = curs.fetchone()

        curs.execute(f"SELECT theatral, art, music, game, animal, garden, vyazanie, sport, language, books FROM Interes "
                     f"WHERE id_user_interes={self.user_id}")
        interes = curs.fetchone()
        database.db_close(connect)

        pixmap = QPixmap(path_self_pic)
        self.prof_pic.setPixmap(pixmap)
        self.label_interes = ["Театральное искусство","Художественное искусство", "Музыка", "Игры",
                         "Животные", "Садоводство", "Вязание", "Спорт", "Лингвистика","Книги"]
        self.user_interes = []
        for i in range(len(self.label_interes)):
            a = [interes[i], self.label_interes[i]]
            self.user_interes.append(a)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        for i in self.user_interes:
            print(i)
            if i[0] == 1:
                interes_label = QLabel()
                interes_label.setFont(font)
                interes_label.setText(str(i[1]))
                interes_label.setMinimumHeight(10)
                interes_label.setStyleSheet(u"background-color: rgb(255, 199, 248);\n border: 0px; \n border-radius: 5px; padding: 1px")
                self.self_interes.addWidget(interes_label)

        self.name_prof.setText(str(info[0]))
        self.surname_prof.setText(str(info[1]))
        self.city_prof.setText(str(info[2]))
        self.age_prof.setText(str(info[3]))

        self.user_city = info[2]

        connect, curs = database.db_connection()
        curs.execute(f"SELECT Users.id_user, Form.city_form FROM Users JOIN Form ON Users.id_user=Form.id_user_form ")
        users_unsorted = curs.fetchall()
        database.db_close(connect)

        self.users_cards = []
        users_city = []
        users_other_city = []
        for user in users_unsorted:
            user = [user[0], user[1], 0]
            if user[0] != self.user_id:
                connect, curs = database.db_connection()
                curs.execute(f"SELECT theatral, art, music, game, animal, garden, vyazanie, sport, language, books "
                             f"FROM Interes WHERE id_user_interes={user[0]}")
                for_check = curs.fetchone()
                database.db_close(connect)

                overlap = 0
                for i in range(len(for_check)):
                    if for_check[i]+self.user_interes[i][0] == 2:
                        overlap+=1
                user[2] = overlap

                if user[1] == self.user_city:
                    users_city.append(user)
                else:
                    users_other_city.append(user)

        users_city = sorted(users_city, key=lambda x: x[2])
        users_city.reverse()
        users_other_city = sorted(users_other_city, key=lambda y: y[2])
        users_other_city.reverse()
        self.users_cards = users_city+users_other_city
        print(self.users_cards)

        self.next_user()

    def show_home(self):
        self.main.show()
        self.messanger.hide()
        self.profile.hide()

    def show_profile(self):
        self.main.hide()
        self.messanger.hide()
        self.profile.show()

    def next_user(self):
        user = self.users_cards[0]
        print(user)
        self.users_cards.pop(0)

        connect, curs = database.db_connection()
        curs.execute(f"SELECT name_form, age_form, pic_destination FROM Form WHERE id_user_form = {user[0]}")
        info = list(curs.fetchall()[0])
        user += info

        curs.execute("SELECT theatral, art, music, game, animal, garden, vyazanie, sport, language, books "
                             f"FROM Interes WHERE id_user_interes={user[0]}")
        user_interes = list(curs.fetchone())
        print(user_interes)
        database.db_close(connect)

        self.name.setText(str(user[3]))
        self.age.setText(str(user[4]))
        self.city.setText(str(user[1]))
        pixmap = QPixmap(str(user[5]))
        self.photo.setPixmap(pixmap)

        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.labels = [self.label_0, self.label_1, self.label_2, self.label_3, self.label_4, self.label_5, self.label_6, self.label_7, self.label_8, self.label_9]
        labels = self.labels
        j = 0
        for i in range(len(self.label_interes)):
            if user_interes[i] == 1:
                labels[j].setText(self.label_interes[i])
                j+=1
            else:
                labels = labels[:-1]

                print(labels)

    def like(self):
        for i in self.labels:
            i.setText("")
        self.next_user()

    def dis(self):
        for i in self.labels:
            i.setText("")
        self.next_user()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec())
