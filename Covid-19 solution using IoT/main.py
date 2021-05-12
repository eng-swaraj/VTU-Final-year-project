from flask import Flask, render_template, request
from pymongo import MongoClient
import time
import max30100
import board
import busio as io
import adafruit_mlx90614
import smtplib
import random

from time import sleep

app = Flask(__name__)

client = MongoClient(
    'SSL certificate from mongodb account')

""" Database Connection Check
db = client.test_database
print("DB Details")
print(db)
"""

sender_email_id = "your gmail account "
sender_email_id_password = "password from gmail"

s = smtplib.SMTP('smtp.gmail.com', 587)

i2c = io.I2C(board.SCL,board.SDA,frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

def sendMail(pres, med, email):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    receiver_email_id = email
    s.starttls()
    #s.connect()
    s.login(sender_email_id, sender_email_id_password)
    message = pres+med
    #message.join("\n Return")#'Prescription: '+ pres + "\n" + 'Medicines: ' + med + "\n."
    print(message)
    s.sendmail(sender_email_id, receiver_email_id, message)
    s.quit()


def readTemp():
    ambientTemp = "{:.2f}".format(mlx.ambient_temperature)
    targetTemp = "{:.2f}".format(mlx.object_temperature)
    sleep(1)
    print("Ambient Temprature",ambientTemp, "C")
    print("Target Temprature",targetTemp, "C")
    return targetTemp

def readSensor():
    mx30 = max30100.MAX30100()
    mx30.enable_spo2()
    count = 0
    while count<20:
        mx30.read_sensor()
        mx30.ir, mx30.red
        hb = int(mx30.ir / 100)
        spo2 = int(mx30.red / 100)
        if mx30.ir != mx30.buffer_ir :
            print("Pulse:",hb);
        if mx30.red != mx30.buffer_red:
            print("SPO2:",spo2);
        time.sleep(2)
        count+=1
    mx30.reset()
    return spo2

def key():
    val = random.randint(92, 97)
    return val

def readUser():
    covid = client['covid']
    print("Database")
    print(type(covid))
    users = covid['users']
    print("Users")
    print(type(users))
    print(users.count_documents({}))
    for user in users.find():
        print(user)


def nextID():
    covid = client['covid']
    users = covid['users']
    idList = []
    for userid in users.find():
        idList.append(userid['_id'])
    print(idList)
    currID = max(idList)
    print(currID)
    return currID


@app.route('/')
def index():
    return render_template('home.html', name="Dashboard")

@app.route('/food')
def food():
    return render_template('food.html', name="Order Food")


@app.route('/patient', methods=["GET", "POST"])
def patient():
    if request.method == "POST":
        name = request.form.get('userName')
        age = request.form.get('userAge')
        email = request.form.get('userEmail')
        oxy = readSensor()
        temp = readTemp()
        currID = nextID()
        data = {
            "_id": currID + 1,
            "name": name,
            "age": age,
            "email": email,
            "oxy": key(),
            "temp": temp,
            "pres": "",
            "med": ""
        }
        covid = client['covid']
        userData = covid.users
        userData.insert_one(data)

    return render_template('user.html', name="User's Dashboard")


@app.route('/doctor', methods=["GET", "POST"])
def doctor():
    if request.method == "POST":
        prescription = request.form.get('prescription')
        medicines = request.form.get('medicines')
        covid = client['covid']
        users = covid['users']
        currID = nextID()
        user = users.find_one({"_id": currID})
        email = user['email']
        fil = {'_id':currID}
        docUp = {"$set": { 'pres': prescription, 'med': medicines}}
        users.update_one(fil, docUp)
        sendMail(prescription, medicines, email)
    covid = client['covid']
    users = covid['users']
    currID = nextID()
    user = users.find_one({"_id": currID})
    name = user['name']
    age = user['age']
    temp = user['temp']
    oxy = user['oxy']
    email = user['email']
    pres = user['pres']
    med = user['med']
    return render_template('doctor.html', name="Doctor's Dashboard", patientName=name, patientAge=age, patientTemp=temp,
                           patientOxy=oxy, prescription=pres, medicine=med)


if __name__ == '__main__':
    app.run(host='127.0.0.6', port=5001 ,debug=True)