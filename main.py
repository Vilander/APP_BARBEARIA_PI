from App_Barbearia import create_app, database, iniciar_servico_lembretes

app = create_app()

with app.app_context():
    database.create_all()

if __name__ == '__main__':
    iniciar_servico_lembretes(app)
    app.run(host="0.0.0.0", port=5000, debug=True)

