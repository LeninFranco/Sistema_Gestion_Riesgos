from flask import Flask
from src.utils.db import db
from src.utils.crypto import bcrypt
from src.routes.login import login
from src.routes.proyectos import proyectos
from src.routes.home import home
from src.routes.responsables import responsables
from src.routes.activos import activos
from src.routes.riesgos import riesgos
from src.routes.participantes import participantes
from src.routes.proyectosP import proyectosP
from src.routes.planes import planes
import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'src', 'database', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = secrets.token_hex(16)

app.register_blueprint(login)
app.register_blueprint(proyectos)
app.register_blueprint(home)
app.register_blueprint(responsables)
app.register_blueprint(activos)
app.register_blueprint(riesgos)
app.register_blueprint(participantes)
app.register_blueprint(proyectosP)
app.register_blueprint(planes)


db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)