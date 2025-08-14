# Importa o objeto 'app' e 'database' do seu pacote principal.
# O nome da sua instância do SQLAlchemy é 'database', não 'db'.
from App_Barbearia import app, database
# Importa a classe 'Usuario' do seu arquivo de modelos.
from App_Barbearia.models import Usuario

# Solicita o email do usuário a ser promovido.
user_email = input("Digite o email do usuário para torná-lo admin: ")

# Usa o objeto 'app' importado para criar o contexto da aplicação.
with app.app_context():
    # Busca o usuário pelo email fornecido.
    user = Usuario.query.filter_by(email=user_email).first()

    if user:
        # Se o usuário for encontrado, altera a sua 'role' para 'admin'.
        user.role = 'admin'
        # Salva a mudança no banco de dados.
        database.session.commit()
        print(f"O usuário {user.username} agora é um administrador!")
    else:
        print(f"Usuário com email {user_email} não encontrado.")
