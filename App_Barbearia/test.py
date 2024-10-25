from App_Barbearia import app, database
from App_Barbearia.models import Usuario, UserMixin, Post
from datetime import date

'''with app.app_context():
    database.create_all()'''


'''with app.app_context():
    agendar = Post(username='teste', cell='12345678901', datar=date.today(), hora='10:00', id_usuario=1)
    database.session.add(agendar)
    database.session.commit()

with app.app_context():
    dados = Post.query.all()
    p_dados = dados[0]
    print(dados)
    print(p_dados.data)'''