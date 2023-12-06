from tkinter import *
from tkinter import font as tkfont
from tkinter import messagebox

import sqlite3
import random
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Database:
    def __init__(self, db):
        self.otp = 'Invalid'
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS USER (EMAIL TEXT PRIMARY KEY, OTP TEXT)")
        self.conn.commit()
        
    def insert(self, email):
        try:
            self.cur.execute("INSERT INTO USER VALUES (?, ?)", (email,self.otp))
            self.conn.commit()
            messagebox.showinfo("Register", "Your Email Id is register Successfully.")
        except:
            messagebox.showerror('Error', 'Your Email Id already exists.')
            
    def update(self, otp, recv):
        try:
            self.cur.execute("UPDATE USER SET OTP = ? WHERE EMAIL = ?", (otp, recv))
            self.conn.commit()
        except:
            messagebox.showerror('Field Change', 'Please do not change the Email Id.')

    def fetchEmail(self, email):
        self.cur.execute("SELECT COUNT(*) FROM USER WHERE EMAIL = ?", (email, ))
        ct = self.cur.fetchone()[0]

        if ct == 0:
            return False
        else:
            return True
        
    def getOTP(self, recv):
        try:
            self.cur.execute("SELECT OTP FROM USER WHERE EMAIL = ?", (recv, ))
            return self.cur.fetchone()[0]
        except:
            messagebox.showerror('Field Change', 'Please do not change the Email Id.')

    def __del__(self):
        self.conn.close()


# Validation
def validate_email_input(P):
    if P == "" or P.islower():
        return True
    else:
        return False
    
def validate_otp_input(P):
    if P == "" or P.isdigit():
        return True
    else:
        return False

# Clear Field
def clear_text():
    field1.delete(0, END)
    
# Registration
def register_email():
    if f1.get() == '' or f1.get().endswith('@gmail.com') == False:
        messagebox.showerror('Required Fields', 'Please Fill the Valid Email Id.')
        return
    
    db.insert(f1.get())
    clear_text()

# validation on email
def check_email():
    if f2.get() == '' or f2.get().endswith('@gmail.com') == False:
        messagebox.showerror('Required Fields', 'Please Fill the Valid Email Id.')
        return False
    return True

# Timer
def timer(time_remain):
    global timerId
    if time_remain > 0:
        time_remain -= 1
        l5.config(text=f"Time left: {time_remain} sec")
        timerId = root.after(1000, lambda: timer(time_remain))
    else:
        l5.config(text="OTP is expire now!")
        b4.config(state="disabled")
    
# Generate OTP
def getOTP(btnName):
    global changeOTPId
    if(btnName == 'Resend OTP'):
        root.after_cancel(changeOTPId)
        root.after_cancel(timerId)
        
    emailValidate = check_email()
    
    if emailValidate:
        z = db.fetchEmail(f2.get())
        if z:
            response = messagebox.askyesno('Confirm', f'Are you confirmed to send OTP on {f2.get()} ?')
            if response:
                global otp, recipient_email
                otp = random.randint(1000, 9999)
                sender_email = '***********************@gmail.com'   #sender email Id
                recipient_email = f2.get()
                subject = 'OTP VERIFICATION'
                if(btnName == 'Resend OTP'):
                    message = f"Your Resend OTP for Python project is {otp}. This OTP is valid only for another 60 seconds. Don't Share it with anyone. \n\nThank You."
                else:
                    message = f"Your OTP for Python project is {otp}. This OTP is valid only for 60 seconds. Don't Share it with anyone. \n\nThank You."
                
                print("Email in Processing...")
                try:
                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587) 
                    smtp_server.starttls()
                    smtp_server.login(sender_email, "*******************************")    #sender email password

                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message, 'plain'))

                    smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
                    smtp_server.quit()
                    
                    print("Email is sent...")
                    db.update(otp, recipient_email)
                    field2.config(state="disabled")
                    b2.config(state="disabled")
                    b4.config(state="normal")
                    timer(60)
                    
                    def changeOTP():
                        db.update('Invalid', recipient_email)
                        field2.config(state="normal")
                        b2.config(state="normal")
                        
                    changeOTPId = root.after(60000, changeOTP)
                    
                except Exception:
                    messagebox.showerror("Fatal Error", f"An error occurred due to: {str(Exception)}")
        else:
            messagebox.showerror('Not Found', 'Email Id is not Found.')

# Verify OTP
def verifyOTP():
    user_otp = db.getOTP(recipient_email)
    if(user_otp == f3.get()):
        db.update('Invalid', recipient_email)
        messagebox.showinfo('Great', 'Congratulations! You are ready to go ahead.')
        field3.delete(0, END)
        field2.config(state="normal")
        b2.config(state="normal")
        b4.config(state='disabled') 
        root.after_cancel(changeOTPId)
        root.after_cancel(timerId)
        l5.config(text='')
    else:
        messagebox.showerror('Wrong', 'Sorry! Your OTP is not verified.')

# Make verify button enabled and disabled
def changeVerifyMode():
    if f2.get() == '':
        b3.config(state="disabled")
    else:
        b3.config(state="normal")
        
def setVerifyMode(event):
    field2.after(10, changeVerifyMode)


# create database
db = Database('USER')
root = Tk()
root.geometry("900x350")
root.title("OTP GENERATOR")

custom_font = tkfont.Font(family="Helvetica", size=14)


# Add registration section
frame1 = Frame(root)
frame1.grid(row=0, column=0)
l1 = Label(frame1, text='Register Email Id: ', width=25, font=custom_font, pady=20)
l1.grid(row=0, column=0, sticky=W)
f1 = StringVar()
field1 = Entry(frame1, textvariable=f1, width=35)
field1.grid(row=0, column=1)
e1 = Label(frame1, text=' ', width=12, font=custom_font, pady=20)
e1.grid(row=0, column=2, sticky=W)

b1 = Button(frame1, text='Register', font=custom_font, width=12, command=register_email)
b1.grid(row=0, column=3)

validation = root.register(validate_email_input)
field1.config(validate="key", validatecommand=(validation, "%P"))


# Add Label
frame2 = Frame(root)
frame2.grid(row=1, column=0)
l2 = Label(frame2, text='=== GENERATE OTP ===', width=50, font=custom_font, pady=20)
l2.grid(row=1, column=0, sticky=W)


# Add OTP Section
frame3 = Frame(root)
frame3.grid(row=2, column=0)
l3 = Label(frame3, text='Enter Email Id: ', width=25, font=custom_font, pady=20)
l3.grid(row=2, column=0, sticky=W)
f2 = StringVar()
field2 = Entry(frame3, textvariable=f2, width=35)
field2.grid(row=2, column=1)
e2 = Label(frame3, text=' ', width=12, font=custom_font, pady=20)
e2.grid(row=2, column=2, sticky=W)

b2 = Button(frame3, text='Get OTP', font=custom_font, width=12, command=lambda: getOTP('Get OTP'))
b2.grid(row=2, column=3)

field2.config(validate="key", validatecommand=(validation, "%P"))
field2.bind("<Key>", setVerifyMode)

l4 = Label(frame3, text='Enter OTP: ', width=25, font=custom_font, pady=20)
l4.grid(row=3, column=0, sticky=W)
f3 = StringVar()
field3 = Entry(frame3, textvariable=f3, width=35)
field3.grid(row=3, column=1)

time_font = tkfont.Font(family="Helvetica", size=11)
l5 = Label(frame3, text='', width=15, font=time_font, foreground="red", pady=20)
l5.grid(row=3, column=2, sticky=W)

validate_otp = root.register(validate_otp_input)
field3.config(validate="key", validatecommand=(validate_otp, "%P"))

b3 = Button(frame3, text='Verify', font=custom_font, width=12, command=verifyOTP)
b3.grid(row=4, column=1)

if f2.get() == '':
    b3.config(state="disabled")

b4 = Button(frame3, text='Resend OTP', font=custom_font, width=12, state="disabled", command=lambda: getOTP('Resend OTP'))
b4.grid(row=4, column=2)

root.mainloop()