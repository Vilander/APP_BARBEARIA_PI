import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

try:
    # Importações relativas, pois este arquivo está dentro do pacote App_Barbearia
    from . import create_app, database
    from .models import Post, Usuario
except ImportError:
    print("Erro: Este arquivo deve ser executado como um módulo.")
    print("Por favor, execute o seguinte comando a partir da pasta raiz do seu projeto:")
    print("python -m App_Barbearia.ml_model")
    exit()


def preparar_dados_para_ml():
    """Busca os dados do banco de dados e os prepara para o treinamento do modelo de ML."""
    
    # Obtém todos os agendamentos ordenados por usuário e data
    agendamentos = Post.query.order_by(Post.id_usuario, Post.data).all()
    dados = []
    for agendamento in agendamentos:
        dados.append({
            'id_usuario': agendamento.id_usuario,
            'data_agendamento': agendamento.data
        })
    
    if not dados:
        print("Não há agendamentos suficientes para treinar o modelo.")
        return None, None
        
    df = pd.DataFrame(dados)
    
    # Converte a coluna de data para o tipo datetime para permitir cálculos
    df['data_agendamento'] = pd.to_datetime(df['data_agendamento'])
    
    # Calcula a diferença em dias entre as visitas de cada usuário
    df['dias_entre_visitas'] = df.groupby('id_usuario')['data_agendamento'].diff().dt.days.fillna(0)
    
    # Cria a coluna com o dia da semana da última visita (segunda=0, domingo=6)
    df['dia_da_semana'] = df['data_agendamento'].dt.dayofweek
    
    # Apenas para remover a primeira linha de cada usuário (onde a diferença de dias é 0)
    df = df[df['dias_entre_visitas'] > 0]
    
    if len(df) < 2:
        print("Dados insuficientes para treinar o modelo após o pré-processamento.")
        return None, None

    # Recursos (features) e Alvo (target) para o modelo
    X = df[['dias_entre_visitas', 'dia_da_semana']]
    y = df['dias_entre_visitas'] # O alvo é a próxima visita, mas usaremos a anterior como base

    return X, y

def treinar_modelo_ml(X, y):
    """Treina o modelo de Machine Learning com os dados preparados."""
    # Dividir os dados em conjuntos de treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Inicializar e treinar o modelo de Regressão Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Avaliar o modelo
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Erro Quadrático Médio do modelo: {mse:.2f}")

    return model

def prever_proxima_visita(model, id_usuario):
    """
    Prevê a data da próxima visita para um usuário específico.
    Args:
        model: O modelo de ML treinado.
        id_usuario: O ID do usuário para quem a previsão será feita.
    Returns:
        A data prevista no formato 'DD/MM/AAAA' ou None se não houver dados.
    """
    # Busca os agendamentos do usuário, ordenados pela data de forma descendente
    agendamentos_usuario = Post.query.filter_by(id_usuario=id_usuario).order_by(Post.data.desc()).all()
    
    if not agendamentos_usuario or len(agendamentos_usuario) < 2:
        print(f"Dados insuficientes para o usuário {id_usuario}.")
        return None # Retorna None se não houver agendamentos ou se houver apenas um

    # Calcula a média dos dias entre as visitas
    datas = [ag.data for ag in agendamentos_usuario]
    diferencas_dias = [(datas[i] - datas[i+1]).days for i in range(len(datas)-1)]
    media_dias = sum(diferencas_dias) / len(diferencas_dias) if diferencas_dias else None

    # Último agendamento do usuário
    ultimo_agendamento = agendamentos_usuario[0]
    dia_da_semana_ultima_visita = ultimo_agendamento.data.weekday()

    # Se a média de dias for None, significa que só há um agendamento.
    # Neste projeto real, você usaria uma média global ou outro valor.
    if media_dias is None:
        return None # Retorna None se não houver dados suficientes

    input_features = pd.DataFrame([[media_dias, dia_da_semana_ultima_visita]], 
                                  columns=['media_dias_entre_visitas', 'dia_da_semana'])

    # Faz a previsão do número de dias até a próxima visita
    dias_previstos = model.predict(input_features)[0]
    
    # Calcula a data prevista somando os dias previstos à data da última visita
    data_prevista = ultimo_agendamento.data + timedelta(days=int(dias_previstos))
    
    return data_prevista.strftime('%d/%m/%Y')


if __name__ == '__main__':
    # Este bloco permite que você teste o arquivo ml_model.py diretamente.
    # A maneira correta de executá-lo é a partir da pasta raiz do projeto:
    # python -m App_Barbearia.ml_model
    # Isso garante que as importações relativas funcionem.
    from . import create_app
    app = create_app()
    with app.app_context():
        X, y = preparar_dados_para_ml()
        if X is not None and y is not None:
            modelo_treinado = treinar_modelo_ml(X, y)
            
            # Exemplo de como usar a previsão para um usuário com ID 1
            # 💡 Altere o id_cliente_teste para o ID de um usuário existente
            id_cliente_teste = 1 
            data_sugerida = prever_proxima_visita(modelo_treinado, id_cliente_teste)
            
            if data_sugerida:
                print(f"Modelo treinado com sucesso!")
                print(f"Data sugerida para o usuário {id_cliente_teste}: {data_sugerida}")
            else:
                print("Não foi possível fazer uma previsão. Verifique se o usuário tem agendamentos suficientes.")
        else:
            print("Não foi possível treinar o modelo. Dados insuficientes.")

