from csv import writer
import csv
from flask import Flask, Response, abort, render_template, request , redirect, send_file, url_for
import psycopg2 #pip install psycopg2 
import psycopg2.extras
import io
import xlwt

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_mail import Mail, Message
import pandas as pd
import datetime

app = Flask(__name__)
mail = Mail(app) 

flag=0

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '' #mail username
app.config['MAIL_PASSWORD'] = '' #mail password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

DB_HOST = "" #database hostname
DB_NAME = "" #database name
DB_USER = "" #database username
DB_PASS = "" #database password
DB_PORT = 5433 #port no

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)


def send_mail():
    df = pd.read_excel (r'') #excel file path
    today = datetime.date.today()
    print("Today = ",today)
    #Get the current Year
    year = today.year
    #Loop through the birthday list
    for i in range(0,len(df)):
  #Get the month
        month = df['Birth_Month'][i]
        print(month)
  #Get the day
        day = df['Birth_Day'][i]
        print(day)
  #Get the email
        email = df['Email'][i]
        print(email)
  #Get the name
        name = df['Name'][i]
  #Get the birthdate
        birthdate = datetime.date(year, month, day)
        print(birthdate)
  #Check if today birthday
        if birthdate == today:
            msg = Message(
            'Hello',
            sender ='idateshreya@gmail.com',
            recipients = [email]
            )
            print("DONE")
            #msg.body = 'Hello Flask message sent from Flask-Mail'
            #mail.body = 
            #msg.html = render_template("Automail.html")
            msg.html = render_template("Automail.html")
            mail.send(msg)

@app.route('/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/')
def hello():
    global flag
    flag=0
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    global flag
    flag = 0
    send_mail()
    email = request.form.get("email")
    password = request.form.get("password")
    error = None
    if request.method == 'POST':
        if request.form['email'] != 'admin@gmail.com' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            flag=1
            return redirect(url_for('admin'))
    return render_template('login.html', error=error)

@app.route("/AdminDashboard")
def admin():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    engine = create_engine("") #database connectivity path
    db = scoped_session(sessionmaker(bind=engine))
    registeredMembers=db.execute("SELECT * FROM Registered order by prn;")
    return render_template("AdminDashboard3.html", registeredMembers=registeredMembers)

@app.route("/mail")
def displayMail():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    return render_template("showAutomail.html")

@app.route("/registered/add")
def memberInsert():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    return render_template("Add3.html")


@app.route("/memberAdd", methods=['GET', 'POST'])
def memberAdd():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    prn=request.form.get("prn")
    name=request.form.get("name")
    birth_day=request.form.get("birth_day")
    birth_month=request.form.get("birth_month")
    birth_year=request.form.get("birth_year")
    email=request.form.get("email")
    #print(prn)
    error = None
    
    #create string update query with the values from form
    strSQL =("insert into registered(prn,name,birth_day,birth_month,birth_year,email) values ("+prn+",'"+name+"',"+birth_day+","+birth_month+","+birth_year+",'"+email+"')")
    cur.execute(strSQL) 
    
    #commit to database
    conn.commit() 
    try:
        correctDate=datetime.datetime(year=int(birth_year),month=int(birth_month),day=int(birth_day))
    except ValueError:
        strSQL="delete from Registered where prn='{}'".format((prn))
        #execute delete query
        cur.execute(strSQL) 
        #commit to database
        conn.commit() 
        error="Invalid Date. Please enter again."
        return render_template("Add3.html",error=error)
    return redirect(url_for('display'))
    

@app.route("/registered/modify/<int:prn>")
def memberModify(prn):
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Registered where prn=prn",{"prn":prn})
    cur.fetchall()
    return render_template("update3.html")  

@app.route("/memberUpdate", methods=["POST"])
def memberUpdate():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    #store values recieved from HTML form in local variables
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    prn=request.form.get("prn")
    name=request.form.get("name")
    birth_day=request.form.get("birth_day")
    birth_month=request.form.get("birth_month")
    birth_year=request.form.get("birth_year")
    email=request.form.get("email")
    #create string update query with the values from form
    strSQl= "update Registered set prn='"+str(prn)+"', name='"+name+"', birth_day='"+birth_day+"',birth_month='"+birth_month+"', birth_year='" +birth_year+"', email='" +email+ "' where prn= '"+str(prn)+"'"
    #Execute update query
    cur.execute(strSQl) 
    #commit to database
    conn.commit() 
    return redirect(url_for('display'))

@app.route("/memDelete/<int:prn>")
def memberDelete(prn):
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #create delete query as string
    strSQL="delete from Registered where prn='{}'".format((prn))
    #execute delete query
    cur.execute(strSQL) 
    #commit to database
    conn.commit() 
    return redirect(url_for('display'))

@app.route("/display")
def display():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    engine = create_engine("postgresql://postgres:Percy394/*@localhost:5433/Registered")
    db = scoped_session(sessionmaker(bind=engine))
    registeredMembers=db.execute("SELECT * FROM Registered order by prn;")
    return render_template("AdminDashboard3.html", registeredMembers=registeredMembers)   

@app.route("/DownloadExcel")
def download():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Registered")
    result = cur.fetchall()
    output = io.BytesIO()
    workbook = xlwt.Workbook()
    #add a sheet
    sh = workbook.add_sheet('Registered Member')
 
    #add headers
    sh.write(0, 0, 'PRN')
    sh.write(0, 1, 'Name')
    sh.write(0, 2, 'Birth Day')
    sh.write(0, 3, 'Birth Month')
    sh.write(0, 4, 'Birth Year')
    sh.write(0, 5, 'Email')
 
    prnx = 0
    for row in result:
        sh.write(prnx+1, 0, str(row['prn']))
        sh.write(prnx+1, 1, row['name'])
        sh.write(prnx+1, 2, str(row['birth_day']))
        sh.write(prnx+1, 3, str(row['birth_month']))
        sh.write(prnx+1, 4, str(row['birth_year']))
        sh.write(prnx+1, 5, row['email'])
        prnx += 1
 
    workbook.save(output)
    output.seek(0)
 
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=registered_members.xls"})


@app.route("/donations")
def donations():
    global flag
    if flag==0:
        return redirect(url_for('hello'))
    return render_template('donations2.html')

if __name__ == '__main__':
    app.run(debug=True)