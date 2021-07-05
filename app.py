from flask import Flask,render_template,session,redirect
import pymysql
from flask import request
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.secret_key ="Wdg@#$%89jMfh2879mT"
connection = pymysql.connect(host='localhost', user='root', password='', database='farmers')

@app.route("/")
def home():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    print("Products",rows)
    return  render_template('index.html',rows = rows)




@app.route("/index2")
def home2():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    print("Products",rows)
    return  render_template('index2.html',rows = rows)

@app.route("/login",methods = ['POST','GET'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM shopit_users WHERE email= %s AND password = %s",(email,password))
        if cursor.rowcount == 1:
             session['key'] = email
             return redirect('/index2')
        else:
            return render_template('login.html',msg = "Fallied to loggin,check your username and password")
    return render_template('login.html')


@app.route("/single/<product_id>")
def single(product_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items WHERE ProductID =%s",(product_id))
    products = cursor.fetchone()

    return render_template('single.html',products = products)


@app.route("/register",methods=['POST','GET'])
def register():
    if request.method == "POST":
        email = request.form['Email']
        phone = request.form['Phone']
        password = request.form['Password']
        cursor = connection.cursor()
        cursor.execute("INSERT INTO shopit_users(email,phone,password) VALUES(%s,%s,%s)",(email,phone,password))
        connection.commit()
        return render_template('register.html',msg = "your account was created succesfully")
    else:
        return  render_template('register.html')

@app.route('/mpesa',methods = ['POST','GET'])
def mpesa():
    if request.method == "POST":
        Phone = str(request.form['Phone'])
        qty = request.form['qty']
        amount = 1
        total_amount = str(amount*qty)
        # GENERATING THE ACCESS TOKEN
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": Phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": Phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        return response.text
    else:
        return "Invalid request"



@app.route('/loggout')
def logout():
    session.pop('key',None)
    return  redirect('/')

@app.route('/furniture')
def furniture():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM furniture")
    rows = cursor.fetchall()
    print("furniture",rows)
    return render_template('furniture.html', rows = rows )

@app.route("/pay/<product_id>")
def pay(product_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM furniture WHERE ProductID =%s",(product_id))
    furniture = cursor.fetchone()

    return render_template('pay.html',furniture=furniture)

if __name__ == "__main__":
    app.run(debug=True)