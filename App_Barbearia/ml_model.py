import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Importações relativas, pois este arquivo está dentro do pacote App_Barbearia
from . import create_app, database
from .models import Post, Usuario


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
    
    # Cria as features (entradas para o modelo) e o target (o que o modelo deve prever)
    features = []
    targets = []
    
    for user_id, group in df.groupby('id_usuario'):
        # A média de dias entre visitas é uma feature importante para o modelo
        # É a base do "padrão" de agendamento de cada usuário
        avg_days = group['dias_entre_visitas'].mean()
        
        # Iteramos sobre o histórico de cada usuário para treinar o modelo
        # A primeira visita de cada usuário não tem um intervalo anterior
        for i in range(1, len(group)):
            dias_desde_ultima = (group['data_agendamento'].iloc[i] - group['data_agendamento'].iloc[i-1]).days
            targets.append(dias_desde_ultima)
            
            # As features serão a média de dias e o dia da semana da visita anterior
            features.append([avg_days, group['data_agendamento'].iloc[i-1].weekday()])
            
    if not features:
        print("Dados insuficientes para criar features de treinamento.")
        return None, None
        
    X = pd.DataFrame(features, columns=['media_dias_entre_visitas', 'dia_da_semana'])
    y = pd.Series(targets, name='dias_para_proxima_visita')
    
    return X, y

def treinar_modelo_ml(X, y):
    """Treina o modelo de regressão e retorna o modelo treinado."""
    
    # Divide os dados em conjuntos de treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Utiliza um modelo de Floresta Aleatória para a regressão
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Avalia o modelo e imprime o erro para ver o quão preciso ele é
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Erro Quadrático Médio do modelo: {mse:.2f}")
    
    return model

def prever_proxima_visita(model, id_usuario):
    """
    Prevê a próxima data de agendamento para um usuário específico.
    
    Args:
        model: O modelo de ML treinado.
        id_usuario (int): O ID do usuário para o qual a previsão será feita.
        
    Returns:
        str: A data prevista em formato 'dd/mm/aaaa' ou None se não houver dados.
    """
    
    # Encontra o último agendamento do usuário
    ultimo_agendamento = Post.query.filter_by(id_usuario=id_usuario).order_by(Post.data.desc()).first()
    if not ultimo_agendamento:
        return None
        
    # Calcula a média de dias entre as visitas do usuário
    historico_usuario = Post.query.filter_by(id_usuario=id_usuario).order_by(Post.data).all()
    if len(historico_usuario) < 2:
        # Se o usuário tem apenas uma visita, a média de dias não pode ser calculada.
        # Nesses casos, a previsão não será tão precisa.
        media_dias = None
        
    else:
        datas = pd.Series([ag.data for ag in historico_usuario])
        media_dias = datas.diff().dt.days.mean()
    
    # Calcula a feature "dia da semana" com base na última visita
    dia_da_semana_ultima_visita = ultimo_agendamento.data.weekday()

    # Prepara a entrada para o modelo com as features calculadas
    # Se media_dias for None, o modelo pode ter um comportamento imprevisível.
    # Em um projeto real, você usaria uma média global ou outro valor.
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
    # Este bloco permite que você teste o arquivo ml_model.py diretamente
    # sem rodar o servidor Flask.
    app = create_app()
    with app.app_context():
        X, y = preparar_dados_para_ml()
        if X is not None and y is not None:
            modelo_treinado = treinar_modelo_ml(X, y)
            
            # Exemplo de como usar a previsão para um usuário com ID 1
            id_cliente_teste = 1
            data_sugerida = prever_proxima_visita(modelo_treinado, id_cliente_teste)
            
            if data_sugerida:
                print(f"A próxima visita do usuário {id_cliente_teste} está prevista para: {data_sugerida}")
            else:
                print(f"Não foi possível prever a data para o usuário {id_cliente_teste} (dados insuficientes).")

