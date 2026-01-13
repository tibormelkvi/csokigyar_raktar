import os
import socket
import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'titkos-kulcs-csokigyár-2024'

# --- KÖRNYEZET KEZELÉS ---
if 'TibiAtya' in socket.gethostname():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/TibiAtya/raktar.db'
    DEBUG_MODE = False
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'raktar.db')
    DEBUG_MODE = True

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- ADATBÁZIS MODELLEK ---
class Kategoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nev = db.Column(db.String(100), unique=True, nullable=False)
    termekek = db.relationship('Termek', backref='kategoria', lazy=True)

class Termek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nev = db.Column(db.String(100), nullable=False)
    mennyiseg = db.Column(db.Float, nullable=False)
    min_szint = db.Column(db.Float, default=1.0)
    kategoria_id = db.Column(db.Integer, db.ForeignKey('kategoria.id'), nullable=True)

class Naplo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idopont = db.Column(db.DateTime, default=datetime.now)
    felhasznalo = db.Column(db.String(50))
    esemeny = db.Column(db.String(255))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='vendeg')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# --- ADATBÁZIS INICIALIZÁLÁS ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('123'), role='admin'))
        db.session.commit()

# --- ÚTVONALAK ---
@app.route('/')
@login_required
def index():
    kategoriak = Kategoria.query.order_by(Kategoria.nev).all()
    egyeb_termekek = Termek.query.filter_by(kategoria_id=None).order_by(Termek.nev).all()
    naplo_bejegyzesek = Naplo.query.order_by(Naplo.idopont.desc()).limit(10).all()
    osszes_kg = db.session.query(db.func.sum(Termek.mennyiseg)).scalar() or 0
    keves_keszlet_db = Termek.query.filter(Termek.mennyiseg <= Termek.min_szint).count()
    return render_template('index.html', kategoriak=kategoriak, egyeb_termekek=egyeb_termekek, 
                           naplo=naplo_bejegyzesek, osszes_kg=osszes_kg, keves_keszlet=keves_keszlet_db)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Hibás felhasználónév vagy jelszó!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/export')
@login_required
def export_csv():
    termekek = Termek.query.all()
    si = StringIO()
    si.write('\ufeff')  # BOM az ékezetekhez
    cw = csv.writer(si, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    cw.writerow(['Termék', 'Készlet (kg)', 'Csoport', 'Állapot'])
    for t in termekek:
        allapot = "KEVÉS" if t.mennyiseg <= t.min_szint else "OK"
        kat = t.kategoria.nev if t.kategoria else "Egyéb"
        suly_formazott = str(t.mennyiseg).replace('.', ',')
        cw.writerow([t.nev, suly_formazott, kat, allapot])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=raktar_kimutatas.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

@app.route('/kategoria_hozzaadas', methods=['POST'])
@login_required
def kategoria_hozzaadas():
    if current_user.role != 'admin': return "Nincs jogod!", 403
    nev = request.form.get('kategoria_nev')
    if nev and not Kategoria.query.filter_by(nev=nev).first():
        db.session.add(Kategoria(nev=nev))
        db.session.add(Naplo(felhasznalo=current_user.username, esemeny=f"Új csoport: {nev}"))
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/hozzaadas', methods=['POST'])
@login_required
def hozzaadas():
    if current_user.role != 'admin': return "Nincs jogod!", 403
    nev, mennyiseg = request.form.get('nev'), float(request.form.get('mennyiseg'))
    min_s = float(request.form.get('min_szint') or 1.0)
    kat_id = request.form.get('kategoria_id')
    k_id = int(kat_id) if kat_id else None
    db.session.add(Termek(nev=nev, mennyiseg=mennyiseg, kategoria_id=k_id, min_szint=min_s))
    db.session.add(Naplo(felhasznalo=current_user.username, esemeny=f"Hozzáadva: {nev}"))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/szerkesztes/<int:id>', methods=['GET', 'POST'])
@login_required
def szerkesztes(id):
    if current_user.role != 'admin': return "Nincs jogod!", 403
    termek = Termek.query.get_or_404(id)
    if request.method == 'POST':
        termek.nev, termek.mennyiseg = request.form['nev'], float(request.form['mennyiseg'])
        termek.min_szint = float(request.form['min_szint'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('szerkesztes.html', termek=termek)

@app.route('/torles/<int:id>')
@login_required
def torles(id):
    if current_user.role != 'admin': return "Nincs jogod!", 403
    termek = Termek.query.get_or_404(id)
    db.session.delete(termek)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/felhasznalok', methods=['GET', 'POST'])
@login_required
def felhasznalok():
    if current_user.role != 'admin': return "Nincs jogod!", 403
    if request.method == 'POST':
        uj_nev, uj_role = request.form.get('username'), request.form.get('role')
        uj_pw = generate_password_hash(request.form.get('password'))
        if not User.query.filter_by(username=uj_nev).first():
            db.session.add(User(username=uj_nev, password=uj_pw, role=uj_role))
            db.session.commit()
    return render_template('felhasznalok.html', userek=User.query.all())

@app.route('/jelszo_modositas/<int:id>', methods=['POST'])
@login_required
def jelszo_modositas(id):
    if current_user.role != 'admin': return "Nincs jogod!", 403
    user = User.query.get_or_404(id)
    uj_jelszo = request.form.get('uj_jelszo')
    if uj_jelszo:
        user.password = generate_password_hash(uj_jelszo)
        db.session.commit()
        flash(f'{user.username} jelszava frissítve!')
    return redirect(url_for('felhasznalok'))

@app.route('/felhasznalo_torles/<int:id>')
@login_required
def felhasznalo_torles(id):
    if current_user.role != 'admin': return "Nincs jogod!", 403
    user = User.query.get_or_404(id)
    if user.username != 'admin':
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('felhasznalok'))

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)