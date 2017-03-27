from flask import Flask, render_template, redirect, url_for, session, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

socketio = SocketIO(app)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

# TODO: HERE IS WHERE ILL ADD THE CONNECTIONS TO DB WHEN SOMEONE JOINS A room
# TODO: INSTEAD OF STATE, DO ROOM
# class State(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     connections = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # instantiating a form, passing it into the template with form=form
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                session['user'] = current_user.username
                session['room'] = 'first'
                return redirect(url_for('.dashboard'))
        return '<h1>Invalid username or password</h1>'
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/algoview')
@login_required
def algoview():
    room = session.get('room')
    return render_template('algoview.html', room=room)

# Socket stuff
@socketio.on('message', namespace='/algoview')
def message(msg):
    print(msg)

@socketio.on('editor', namespace='/algoview')
def editor(json):
    room = session.get('room')
    user = session.get('user')
    emit('editor', str(json), broadcast=True, include_self=False, room=room)

@socketio.on('submission', namespace='/algoview')
def submission(json):
    # TODO: HERE IS WHERE I WOULD MAKE A VARIABLE FOR FUNCTION NAME WITH SOME TEXT PARSING
    # TODO: HERE IS WHERE I WILL LOAD ASSOCIATED TEST/ALGO
    room = session.get('room')

    # TESTING SYNTAX ERRORS
    try:
        # THIS EXECUTES USERS PYTHON CODE AND ADDS FUNCTION TO GLOBAL SCOPE
        exec(json['data'], globals())
    except (SyntaxError, NameError) as e:
        emit('incorrect', {'user': current_user.username, 'error': str(e), 'message':'wow lol '+ current_user.username + ' is rly bad at this'}, broadcast=True, room=room)
    else:
        # TESTING CORRECT FUNCTION NAME
        try:
            multiply
        except NameError as e:
            emit('incorrect', {'user': current_user.username, 'error': str(e), 'message':'wow lol '+ current_user.username + ' is rly bad at this'}, broadcast=True, room=room)
        else:
            # TESTING CORRECT FUNCTION PARAMETERS
            try:
                multiply(1,9)
            except TypeError as e:
                emit('incorrect', {'user': current_user.username, 'error': str(e), 'message':'wow lol '+ current_user.username + ' is rly bad at this'}, broadcast=True, room=room)
            else:
                # TESTING FOR CORRECT RESULT
                if multiply(1,9) == 9 and multiply(15123, 424) == 6412152:
                    emit('worked', {'user': current_user.username, 'message':'omg '+ current_user.username +' dun did it!'}, broadcast=True, room=room)
                else:
                    emit('incorrect', {'user': current_user.username, 'error':current_user.username+"'s function did not return the correct value", 'message':'wow lol '+ user + ' is rly bad at this'}, broadcast=True, room=room)


@socketio.on('join', namespace='/algoview')
def join(data):
    room = session.get('room')
    user = session.get('user')
    join_room(room)
    send('somebody has entered the room.', room=room)

@socketio.on('left', namespace='/algoview')
def on_leave(data):
    room = session.get('room')
    leave_room(room)
    send('someone has left the room.', room=room)

if __name__ == '__main__':
    socketio.run(app, 'localhost', debug=True)
