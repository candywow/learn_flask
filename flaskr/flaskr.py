import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

app.config.update(dict(
	DATABASE = os.path.join(app.root_path, 'flaskr.db'),
	DEBUG = True,
	SECRET_KEY = 'development key',
	USERNAME = 'admin',
	PASSWORD = 'loveyou'
	))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from article order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('username'):
		abort(401)
	db = get_db()
	cur = db.execute('select * from user where name=?', [session['username']])
	user = cur.fetchone()
	print user
	db.execute('insert into article (title, text, author_id) values (?, ?, ?)',
		[request.form['title'], request.form['text'], user[0]])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		db = get_db()
		cur = db.execute('select * from user where name=?', [request.form['username']])
		user = cur.fetchone()
		if not user: 
			db.execute('insert into user (name, password) values(?, ?)', 
				[request.form['username'], request.form['password']])
			db.commit()
			flash('Registered')
			session['username'] = request.form['username']
			return redirect(url_for('show_entries'))
		else:
			flash('The username has already registered!')
	return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		db = get_db()
		cur = db.execute('select * from user where name=?', [request.form['username']])
		user = cur.fetchone()
		if not user:
			error = 'Invalid username'
		elif user[2] != request.form['password']:
			error = 'Invalid password'
		else:
			session['username'] = request.form['username']
			flash('You are logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
	app.run()