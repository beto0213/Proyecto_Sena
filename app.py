from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SECRET_KEY'] = 'password'
    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app


app = create_app()
# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# tablas base de datos
class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Producto {self.titulo}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Rutas
@app.route("/")
def home():
    productos = Producto.query.all()
    return render_template('home.html', productos=productos)




@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        # check que exista usuario y credenciales
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        return 'contraseña o usuario incorrecto'
    return render_template('login.html')


# productos
@app.route('/productos', methods=['GET', 'POST'])
@login_required
def create_producto():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        producto = Producto(titulo=titulo, descripcion=descripcion, precio=precio)
        db.session.add(producto)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("/crear_producto.html")


# @app.router('/productos/<int:product_id>', methods=['PUT'])
# def update_producto(product_id):
#   producto = Producto.query.get(product_id)
#  if producto:
#     producto.titulo = request.form.get('titulo')
#    producto.descripcion = request.form.get('descripcion')
#   producto.precio = request.form.get('precio')
# db.session.commit()
# return  redirect(url_for('home'))

@app.route('/productos/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_producto(id):
    producto = Producto.query.get(id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
    return redirect(url_for('home'))


# Correr la aplicación
if __name__ == '__main__':
    app.run(debug=True)
