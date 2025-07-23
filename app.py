from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__,
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')

app.secret_key = 'gizli_anahtar'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.wqotjnholvkvymsllvvf:Sophira.61=61@aws-0-eu-north-1.pooler.supabase.com:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        if form['password'] != form['confirm_password']:
            return render_template('register.html', message="Şifreler uyuşmuyor!", success=False)

        if User.query.filter((User.username == form['username']) | (User.email == form['email'])).first():
            return render_template('register.html', message="Kullanıcı adı veya e-posta zaten kayıtlı.", success=False)

        hashed_password = generate_password_hash(form['password'])
        new_user = User(
            first_name=form['first_name'],
            last_name=form['last_name'],
            username=form['username'],
            email=form['email'],
            phone=form['phone'],
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return render_template('register.html', message="Kayıt başarılı!", success=True,
                               redirect_delay=4, redirect_url=url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            return redirect(url_for('home'))

        return render_template('login.html', message="Kullanıcı adı veya şifre hatalı!")

    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
