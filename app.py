# from App_Barbearia import app

# if __name__ == "__main__":
#     app.run()

# app.py na raiz do projeto

from App_Barbearia import create_app, iniciar_servico_lembretes

# Cria a instância da aplicação que o Flask e o Flask-Migrate irão usar
app = create_app()

if __name__ == '__main__':
    iniciar_servico_lembretes(app)
    app.run(debug=True)
