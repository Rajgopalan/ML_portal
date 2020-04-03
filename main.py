
from flask import Flask, render_template, request, redirect, url_for, session,send_file
from flask_mysqldb import MySQL
from werkzeug import secure_filename
import MySQLdb.cursors
import os
import re
import shutil
import glob

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'pythonlogin'

path ='/home/ubuntu/flaskapp/cc_project1/userprofiles/'
access_rights = 0o755

# Intialize MySQL
mysql = MySQL(app)



@app.route('/')
def hello():
    return "Hello from the other side"

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
#@app.route('/login/', methods=['GET', 'POST'])
#def login():
#    return render_template('index.html', msg='')

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            #return 'Logged in successfully!'
	    cursor.execute('SELECT count FROM accounts WHERE id = %s', [session['id']])
            count = cursor.fetchone()
	    cursor.execute('SELECT filename FROM accounts WHERE id = %s', [session['id']])
            filename = cursor.fetchone()

            return render_template('home.html', username=session['username'],count=count['count'],file=filename['filename'])
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
	Firstname = request.form['Firstname']
	Lastname = request.form['Lastname']
	count=0
	filename='None'
	filepath='None'

         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
	    os.mkdir(path+username, access_rights)
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s,%s,%s,%s,%s,%s)', (username, password, email,Firstname,Lastname,count,filename,filepath))
            mysql.connection.commit()
            msg = 'You have successfully registered!'


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT count FROM accounts WHERE id = %s', [session['id']])
        count = cursor.fetchone()
	cursor.execute('SELECT filename FROM accounts WHERE id = %s', [session['id']])
        filename = cursor.fetchone()

        return render_template('home.html', username=session['username'],count=count['count'],file=filename['filename'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/pythonlogin/home/', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      #f.save(secure_filename(f.filename))
      print f
      if f.filename=="":
          msg='Please select a valid file'
	  cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute('SELECT count FROM accounts WHERE id = %s', [session['id']])
          count = cursor.fetchone()
	  cursor.execute('SELECT filename FROM accounts WHERE id = %s', [session['id']])
          filename = cursor.fetchone()

          return render_template('home.html', username=session['username'],count=count['count'],file=filename['filename'])

      path_delete='/home/ubuntu/flaskapp/cc_project1/userprofiles/'+session['username']
      shutil.rmtree(path_delete)
      os.mkdir(path_delete, access_rights)
      f.save(os.path.join('/home/ubuntu/flaskapp/cc_project1/userprofiles/'+session['username'], secure_filename(f.filename)))
      path_file='/home/ubuntu/flaskapp/cc_project1/userprofiles/' + session['username'] +'/' + secure_filename(f.filename)
      name_of_file=secure_filename(f.filename)
      file = open(path_file, "rt")
      data = file.read()
      words = data.split()
      print('Number of words in text file :', len(words))
      c=len(words)
      username_session=session['username']

      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      #cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
      cursor.execute('UPDATE accounts SET count = %s WHERE username = %s', [c,username_session])
      cursor.execute('UPDATE accounts SET filename = %s WHERE username = %s', [name_of_file,username_session])
      #UPDATE accounts SET count = c WHERE username = username_session;
      #return 'File uploaded successfully!'
      cursor.execute('UPDATE accounts SET filepath = %s WHERE username = %s;', [path_file,username_session])
      mysql.connection.commit()
      #UPDATE accounts SET filepath = path_file WHERE username = username_session;
      return render_template('home.html', username=session['username'],count=len(words),file=name_of_file)

	
     
@app.route('/return-files/')
def return_files_tut():
	path_file='/home/ubuntu/flaskapp/cc_project1/userprofiles/' + session['username'] + '/*'
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

	list_of_files = glob.glob(path_file)
	latest_file = max(list_of_files, key=os.path.getctime)
	print latest_file
	#download_path='/home/ubuntu/flaskapp/cc_project1/userprofiles/' + session['username'] +'/' + str(latest_file)
	try:
		return send_file(latest_file, as_attachment=True,cache_timeout=-1)
	except Exception as e:
		return str(e)

   
if __name__ == '__main__':
  app.run(host='0.0.0.0',debug=True)
