try:
    from App_Barbearia import create_app
    app = create_app()
    print('App created successfully')
except Exception as e:
    print(f'Error: {e}')