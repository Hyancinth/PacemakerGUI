from pickletools import uint1
import sys
from PyQt5.uic import loadUi
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget
import sqlite3

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
   
        loadUi("UI Files/welcomeScreen.ui", self) #load welcome screen ui file
        
        self.loginButton.clicked.connect(self.goToLogin) 
        self.signupButton.clicked.connect(self.goToSignup)
    
    def goToLogin(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def goToSignup(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("UI Files/login.ui", self)
        
        self.passwordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.loginBtn.clicked.connect(self.loginFunction)
        
        self.signupBtn.clicked.connect(self.goSignup)
        

    def loginFunction(self):
        userName = self.usernameLine.text()
        password = self.passwordLine.text()
        
        if len(userName) == 0 or len(password) == 0:
            self.errorLabel.setText("Please input all fields ")
        
        else:
            conn = sqlite3.connect("userDatabase.db")
            cur = conn.cursor()
            query = 'SELECT password FROM loginInfo WHERE username = \''+ userName +"\'"
            try:
                cur.execute(query)
                resultPass = cur.fetchone()[0]
            except:
                self.errorLabel.setText("Invalid username or password")
            
            if resultPass == password:
                print("Successfully logged in.")
                self.errorLabel.setText("")
                widget.setCurrentIndex(widget.currentIndex() + 2)
                
            else:
                self.errorLabel.setText("Invalid username or password")
    
    def goSignup(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
            
class SignupScreen(QDialog):
    def __init__(self):
        super(SignupScreen, self).__init__()
        
        loadUi("UI Files/signup.ui", self)
        
        self.password_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_line.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.signup_button.clicked.connect(self.signupFunction)
        
        self.login_button.clicked.connect(self.goToLogin)
        
    def signupFunction(self):
        userName = self.username_line.text()
        password = self.password_line.text()
        confirm = self.confirm_line.text()
        
        if len(userName) == 0 or len(password) == 0 or len(confirm) == 0:
            self.errorLabel.setText("Please input all fields ")
            
        elif password != confirm:
            self.errorLabel.setText("Please ensure passwords match")
            
        else:
            conn = sqlite3.connect("userDatabase.db")
            cur = conn.cursor()
            
            cur.execute('SELECT COUNT(*) FROM loginInfo')
            count = cur.fetchone()[0]
            
            if count + 1 > 10:
                self.errorLabel.setText("10 users already registered")
                conn.commit()
                conn.close()
        
            else:
                userInfo = [userName, password]
                cur.execute('INSERT INTO loginInfo (username, password) VALUES (?,?)', userInfo)
                conn.commit()
                conn.close()
            
            widget.setCurrentIndex(widget.currentIndex() - 1) #go to login screen if successful signup
        
    def goToLogin(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

class SystemViewScreen(QDialog):
    def __init__(self):
        super(SystemViewScreen, self).__init__()
        
        loadUi("UI Files/systemView.ui", self)

if __name__ == "__main__":    
    app = QApplication(sys.argv)
    
    welcome = WelcomeScreen()
    
    widget = QStackedWidget()
    widget.addWidget(welcome)
    
    login = LoginScreen()
    widget.addWidget(login)

    signup = SignupScreen()
    widget.addWidget(signup)
    
    systemView = SystemViewScreen()
    widget.addWidget(systemView)
    
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")