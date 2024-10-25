from App_Barbearia import database, login_manager
from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy import Time

# localiza id e faz login do usuario
@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

# Use mixin -  parameto que indica a tabela para o login

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    foto_perfil = database.Column(database.String, default='default.jpg')
    posts = database.relationship('Post', backref='autor', lazy=True)


    def contar_posts(self):
        return len(self.posts)


class Post(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    cell = database.Column(database.String, nullable=False)
    servico = database.Column(database.String, nullable=False)
    hora = database.Column(database.String, nullable=False)
    data = database.Column(database.Date, nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)


