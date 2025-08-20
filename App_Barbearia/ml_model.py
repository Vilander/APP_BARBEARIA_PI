import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

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


def segmentar_clientes_kmeans():
    """
    Realiza a segmentação de clientes usando o modelo K-means (Recência, Frequência, Valor Monetário).
    """
    # 🔹 1. Coleta e Prepara os Dados de RFM (Recência, Frequência, Valor Monetário)
    
    # Mapeamento de preços para os serviços
    service_prices = {
        'Corte de Cabelo': 40.0,
        'Corte de Barba': 30.0,
        'Serviço Completo': 60.0,
    }

    # Busca todos os agendamentos e os usuários
    agendamentos = Post.query.all()
    usuarios = Usuario.query.all()

    # Estrutura para calcular as métricas RFM
    df = pd.DataFrame(columns=['user_id', 'recency', 'frequency', 'monetary'])

    for user in usuarios:
        user_agendamentos = [ag for ag in agendamentos if ag.id_usuario == user.id]

        if not user_agendamentos:
            # Clientes sem agendamentos são considerados com Recência alta, Frequência e Valor 0
            recency = (datetime.now().date() - user.data_criacao.date()).days if user.data_criacao else 0
            frequency = 0
            monetary = 0
        else:
            # Calcula a Recência (dias desde o último agendamento)
            last_appointment = max(ag.data for ag in user_agendamentos)
            recency = (datetime.now().date() - last_appointment).days

            # Calcula a Frequência (número total de agendamentos)
            frequency = len(user_agendamentos)

            # Calcula o Valor Monetário (soma dos preços dos serviços)
            monetary = sum(service_prices.get(ag.servico, 0) for ag in user_agendamentos)

        # Adiciona a linha ao DataFrame
        new_row = pd.DataFrame([{'user_id': user.id, 'recency': recency, 'frequency': frequency, 'monetary': monetary}])
        df = pd.concat([df, new_row], ignore_index=True)
    
    if df.empty:
        return pd.DataFrame() # Retorna um DataFrame vazio se não houver dados

    # 🔹 2. Pré-processamento e Treinamento do Modelo K-means
    
    # Usa apenas as colunas numéricas para o clustering
    X = df[['recency', 'frequency', 'monetary']]

    # Padroniza os dados para que o K-means funcione melhor
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Aplica o modelo K-means com 3 clusters (pode ser ajustado)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['segment'] = kmeans.fit_predict(X_scaled)

    # Mapeia os clusters para nomes mais descritivos
    segment_map = {0: 'Alto Valor', 1: 'Intermediário', 2: 'Novo Cliente'}
    df['segment_name'] = df['segment'].map(segment_map)
    
    # Adiciona o username para facilitar a visualização
    user_names = {user.id: user.username for user in usuarios}
    df['username'] = df['user_id'].map(user_names)

    return df


if __name__ == '__main__':
    # Este bloco permite que você teste o arquivo ml_model.py diretamente.
    # A maneira correta de executá-lo é a partir da pasta raiz do projeto:
    # python -m App_Barbearia.ml_model
    # Isso garante que as importações relativas funcionem.
    from . import create_app
    app = create_app()
    with app.app_context():
        # Teste de segmentação de clientes
        df_segmentos = segmentar_clientes_kmeans()
        if not df_segmentos.empty:
            print("Segmentação de clientes concluída com sucesso!")
            print(df_segmentos[['username', 'recency', 'frequency', 'monetary', 'segment_name']])
        else:
            print("Não há dados suficientes para segmentar os clientes.")
