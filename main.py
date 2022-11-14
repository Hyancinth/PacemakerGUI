from pickletools import uint1
import sys
from tkinter import E
from PyQt5.uic import loadUi
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget
import sqlite3
import os
import serial


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
   
        loadUi("UI Files/welcomeScreen.ui", self) #load welcome screen ui file
        
        self.loginButton.clicked.connect(self.goToLogin) #when login button is pressed
        self.signupButton.clicked.connect(self.goToSignup) #when signup button is pressed
    
    '''
    Moves to login screen
    '''
    def goToLogin(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    '''
    Moves to signup screen
    '''
    def goToSignup(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        
        loadUi("UI Files/login.ui", self) #load login screen ui file
        
        self.passwordLine.setEchoMode(QtWidgets.QLineEdit.Password) #hides password input with dots
        
        self.loginBtn.clicked.connect(self.loginFunction) #when login button is pressed
        self.signupBtn.clicked.connect(self.goSignup) #when signup button is pressed
        

    '''
    Manages login. 
    Verifies if entered username and password 
    '''
    def loginFunction(self):
        userName = self.usernameLine.text() #get entered username
        password = self.passwordLine.text() #get entered password
        
        #Check if username or password is empty
        if len(userName) == 0 or len(password) == 0:
            self.errorLabel.setText("Please input all fields ")
        
        #Check in the database if username matches password
        else:
            
            #Create cursor and query to the database
            conn = sqlite3.connect("userDatabase.db")
            cur = conn.cursor()
            query = 'SELECT password FROM loginInfo WHERE username = \''+ userName +"\'"
            
            try:
                #execute query
                cur.execute(query)
                resultPass = cur.fetchone()[0]
            except:
                self.errorLabel.setText("Invalid username or password")
            
            if resultPass == password:
                print("Successfully logged in.")
                self.errorLabel.setText("")
                
                self.logCurUser()
              
                widget.setCurrentIndex(widget.currentIndex() + 2)
                
            else:
                self.errorLabel.setText("Invalid username or password")
    
    '''
    Move to signup screen
    '''
    def goSignup(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    '''
    Attempts to open a text file and write the username of the current user. 
    This is used to keep track of the current user so the correct text file is loaded for parameters
    '''
    def logCurUser(self):
        try:
            with open('curUser.txt', 'a+') as txt:
                txt.write("name")
                txt.truncate(0)
                
                user = self.usernameLine.text()
       
                txt.write(user)
                
                txt.close()
         
        except Exception as e:
            print(e)
            
class SignupScreen(QDialog):
    def __init__(self):
        super(SignupScreen, self).__init__()
        
        loadUi("UI Files/signup.ui", self) #load signup screen ui file
        
        #hide password and password confirmation
        self.password_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_line.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.signup_button.clicked.connect(self.signupFunction) #when signup button is pressed
        self.login_button.clicked.connect(self.goToLogin) #when login button is pressed
        
    '''
    Creates a new entry into the database with a username and password
    No more than 10 users can be logged into the database
    '''
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
            
            #Check for duplicate ysers
            users = [username[0] for username in cur.execute("SELECT username FROM loginInfo")] #get list of users in the database
          
            for u in users:
                if userName.lower() == u.lower():
                    self.errorLabel.setText("User already exists")
                    conn.commit()
                    conn.close()
            
            #check for password containing only alpha-numeric character
            if not password.isalnum():
                self.errorLabel.setText("Use only alpha-numeric characters for password")
            
            #Check if there are 10 entries in the database 
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
            
                self.createText()
        
                widget.setCurrentIndex(widget.currentIndex() - 1) #go to login screen if successful signup
    
    '''
    Attempt to create a text file anmed after the user with initial values for each of the programmable parameters.
    THe parameters are initially set to their minimum values
    '''
    def createText(self):
        uName = self.username_line.text() #get username
        try:
            with open('%s.txt' % uName, 'w') as txt:
                '''
                    Format of data array 
                    [0] = Lower Rate Limit
                    [1] = Upper Rate Limit 
                    [2] = Atrial Amplitude
                    [3] = Atrial pulse width
                    [4] = Ventricular Amplitude
                    [5] = Ventricular Pulse Width 
                    [6] = VRP
                    [7] = ARP
                    [8] = Serial Number, perhaps this value is obtained from the system view and saved to txt file as the screen loads in
                '''
                data = [30, 50, 0.0, 0.1, 0.0, 0.1, 150, 150, 12345]
                for val in data:
                    txt.write(str(val) + '\n')
                txt.close()
        except Exception as e:
            print(e)
    
    '''
    Move to login screen
    '''
    def goToLogin(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

class SystemViewScreen(QDialog):
    def __init__(self):
        super(SystemViewScreen, self).__init__()
        
        loadUi("UI Files/systemView.ui", self) #load systemView screen ui file
        
        self.userData = [] #initialize empty user data array
        
        #open current user text file and get the logged user
        with open('curUser.txt', 'r') as txt:
            loggedUser = txt.readline()
            txt.close()
        
        #open the logged user's .txt file and append values to userData[]
        with open('%s.txt' % loggedUser, 'r') as txt:
            for line in txt: 
                self.userData.append(line.strip())
            txt.close()
        
        self.displayParameter()
        
        self.saveProfileBtn.clicked.connect(self.updateValues) #When Save Profile Button is clicked
        
        #Button Modes 
        self.aooBtn.clicked.connect(self.aoo)
        self.vooBtn.clicked.connect(self.voo)
        self.aaiBtn.clicked.connect(self.aai)
        self.vviBtn.clicked.connect(self.vvi)
    
    '''
    Updates labels with parameter values
    '''
    def displayParameter(self):
        self.lrlValue.setText(self.userData[0])
        self.urlValue.setText(self.userData[1])
        self.aaValue.setText(self.userData[2])
        self.apwValue.setText(self.userData[3])
        self.vaValue.setText(self.userData[4])
        self.vpwValue.setText(self.userData[5])
        self.vrpValue.setText(self.userData[6])
        self.arpValue.setText(self.userData[7])
    
    '''
    Update parameter values based on inputs 
    Conditions for accepting inputs are based off table and intervals were decided by our group
    '''
    def updateValues(self):

        if(len(self.lrlLine.text()) != 0 and int(self.lrlLine.text()) >= 30 and int(self.lrlLine.text()) <= 175):
            self.userData[0] = self.lrlLine.text()
        elif(len(self.lrlLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
     
     
        if(len(self.urlLine.text()) != 0 and int(self.urlLine.text()) >= 50 and int(self.urlLine.text()) <= 175):
            self.userData[1] = self.urlLine.text()
        elif(len(self.urlLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
          

        if(len(self.aaLine.text()) != 0 and len(self.aaLine.text()) == 3 and float(self.aaLine.text()) >= 0.0 and float(self.aaLine.text()) <= 5.0):
            self.userData[2] = self.aaLine.text()
        elif(len(self.aaLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
        
   
        if(len(self.apwLine.text()) != 0 and len(self.apwLine.text()) == 3 and float(self.apwLine.text()) >= 0.1 and float(self.apwLine.text()) <= 1.9):
            self.userData[3] = self.apwLine.text()
        elif(len(self.apwLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
        
        
        if(len(self.vaLine.text()) != 0 and len(self.vaLine.text()) == 3 and float(self.vaLine.text()) >= 0.0 and float(self.vaLine.text()) <= 5.0):
            self.userData[4] = self.vaLine.text()
        elif(len(self.vaLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
       
        
        if(len(self.vpwLine.text()) != 0 and len(self.vpwLine.text()) == 3 and float(self.vpwLine.text()) >= 0.1 and float(self.vpwLine.text()) <= 1.9):
            self.userData[5] = self.vpwLine.text()
        elif(len(self.vpwLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
        
        
        if(len(self.vrpLine.text()) != 0 and int(self.vrpLine.text())%10 == 0 and int(self.vrpLine.text()) >= 150 and int(self.vrpLine.text()) <= 500):
            self.userData[6] = self.vrpLine.text()
        elif(len(self.vrpLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
        
        
        if(len(self.arpLine.text()) != 0 and int(self.arpLine.text())%10 == 0 and int(self.arpLine.text()) >= 150 and int(self.arpLine.text()) <= 500):
            self.userData[7] = self.arpLine.text()
        elif(len(self.arpLine.text()) == 0):
            print("")
        else:
            self.error_label.setText("Please enter a valid value")
        
        self.displayParameter()
        
        with open('curUser.txt', 'r') as txt:
            loggedUser = txt.readline()
            txt.close()
        
        with open('%s.txt' % loggedUser, 'w') as txt:
            txt.truncate(0)
            for val in self.userData:
                txt.write(val + '\n')
            txt.close()

    def aoo(self):
        self.pacingMode.setText("aoo")
        
        #Disable Line edits that shouldn't be used in this mode
        self.vaLine.setDisabled(True)
        self.vpwLine.setDisabled(True)
        self.vrpLine.setDisabled(True)
        self.arpLine.setDisabled(True)
        
        self.va.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
    
        self.vpw.setStyleSheet('''
                font: italic 16pt "Calibri";
                color:red;
                border-radius:10px;
                background-color: rgba(255, 255, 255, 0);
                ''')

        self.vrp.setStyleSheet('''
                font: italic 16pt "Calibri";
                color:red;
                border-radius:10px;
                background-color: rgba(255, 255, 255, 0);
                ''')
        self.arp.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

    def voo(self):
        self.pacingMode.setText("voo")
        
        #Disable Line edits that shouldn't be used in this mode
        self.aaLine.setDisabled(True)
        self.apwLine.setDisabled(True)
        self.vrpLine.setDisabled(True)
        self.arpLine.setDisabled(True)
        
        self.aa.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
        self.apw.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.vrp.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.arp.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
        #white
        self.va.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.vpw.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
    def aai(self):
        self.pacingMode.setText("aai")
        
        #Disable Line edits that shouldn't be used in this mode
        self.vaLine.setDisabled(True)
        self.vpwLine.setDisabled(True)
        self.vrpLine.setDisabled(True)
        
        self.va.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.vpw.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.vrp.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
    
        #white
        self.aa.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
        self.apw.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.arp.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
    
    def vvi(self):
        self.pacingMode.setText("vvi")
        
        #Disable Line edits that shouldn't be used in this modes
        self.aaLine.setDisabled(True)
        self.apwLine.setDisabled(True)
        self.arpLine.setDisabled(True)
        
        self.aa.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
        
        self.apw.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
        
        self.arp.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:red;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')
        
        #white
        self.va.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.vpw.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

        self.vrp.setStyleSheet('''
                        font: italic 16pt "Calibri";
                        color:white;
                        border-radius:10px;
                        background-color: rgba(255, 255, 255, 0);
                        ''')

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