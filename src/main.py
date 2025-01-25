import pandas as pd
import numpy as np
import xgboost as xgb
from tensorflow.keras.models import load_model
import spacy

# Carregar dados
dados_xgboost = pd.read_csv('/home/Herb_R00t/Tradinho/data/fortnight_time_series.csv')
dados_nlp = pd.read_csv('/home/Herb_R00t/Tradinho/data/new_headlines.csv')

# Filtrar os dados para o conjunto de teste (quinzenas de 256 a 385)
dados_xgboost = dados_xgboost[(dados_xgboost['fortnight'] >= 256) & (dados_xgboost['fortnight'] <= 385)].reset_index(drop=True)
dados_nlp = dados_nlp[(dados_nlp['fortnight'] >= 256) & (dados_nlp['fortnight'] <= 385)].reset_index(drop=True)

# Carregar o modelo XGBoost salvo
modelo_xgboost = xgb.XGBRegressor()
modelo_xgboost.load_model('/home/Herb_R00t/Tradinho/models/final_xgboost_model.bin')

# Carregar o modelo de regressão em Keras
modelo_nlp = load_model('/home/Herb_R00t/Tradinho/models/best_regression_model.keras')

# Pré-processar headlines para embeddings
nlp = spacy.load('en_core_web_md')
dados_nlp['vector'] = dados_nlp['title'].apply(lambda x: nlp(x).vector)
vetores_nlp = pd.DataFrame(dados_nlp['vector'].tolist())
dados_nlp = pd.concat([dados_nlp.drop(columns=['title', 'vector']), vetores_nlp], axis=1)

# Inicializar lista de resultados
resultados = []

# Backtest quinzenal
for i in range(len(dados_xgboost)):
    # Dados da quinzena atual
    linha_xgboost = dados_xgboost.iloc[i]
    linha_nlp = dados_nlp.iloc[i]

    # Previsão XGBoost com os dados da quinzena atual
    features_xgboost = linha_xgboost.drop(
        columns=['fortnight', 'diff_Target', 'S&P500_Open_Price', 'S&P500_Close_Price']
    ).values.reshape(1, -1)
    diff_xgboost = modelo_xgboost.predict(features_xgboost)[0]

    # Previsão NLP com os dados da quinzena atual
    features_nlp = linha_nlp.drop(columns=['fortnight', 'diff']).values.reshape(1, -1)
    diff_nlp = modelo_nlp.predict(features_nlp)[0][0]

    # Cálculo ponderado
    diff_final = (0.6 * diff_xgboost) + (0.4 * diff_nlp)

    # Salvar os resultados
    resultados.append({
        "fortnight": linha_xgboost['fortnight'],
        "real_diff": linha_nlp['diff'],  # DIFF real do CSV NLP
        "diff_xgboost": diff_xgboost,
        "diff_nlp": diff_nlp,
        "diff_final": diff_final,
        "open_price": linha_xgboost['S&P500_Open_Price'],
        "close_price": linha_xgboost['S&P500_Close_Price']
    })

# Converter resultados em DataFrame
resultados_df = pd.DataFrame(resultados)

# Salvar em CSV
output_path = '/home/Herb_R00t/Tradinho/data/combined_predictions.csv'
resultados_df.to_csv(output_path, index=False)
print(f"CSV gerado e salvo em {output_path}")