from App_Barbearia import create_app, database
from App_Barbearia.models import Usuario

app = create_app()

user_email = input("Digite o email do usuário para torná-lo admin: ")

with app.app_context():
    user = Usuario.query.filter_by(email=user_email).first()

    if user:
        user.role = 'admin'
        database.session.commit()
        print(f"O usuário {user.username} agora é um administrador!")
    else:
        print(f"Usuário com email {user_email} não encontrado.")
