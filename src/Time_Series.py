import pandas as pd

# Carregar o arquivo CSV original
data = pd.read_csv('/home/Herb_R00t/Tradinho/data/tradinho-stocks.csv')

# Converter a coluna 'date' para o formato datetime e ordenar por data
data['date'] = pd.to_datetime(data['date'])
data = data.sort_values(by='date')

# Calcular o valor do S&P500 no primeiro dia de cada fortnight
data['S&P500_Open_Price'] = data.groupby('fortnight')['S&P500'].transform('first')

# Calcular o valor do S&P500 no último dia de cada fortnight
first_day_sp500 = data.groupby('fortnight')['S&P500'].transform('first')
last_day_sp500 = data.groupby('fortnight')['S&P500'].transform('last')

# Calcular 'diff_Target' como a diferença entre o último e o primeiro dia de cada fortnight
data['diff_Target'] = last_day_sp500 - first_day_sp500

# Calcular as médias e desvios padrão agrupados por fortnight
cols_to_aggregate = [col for col in data.columns if col not in ['date', 'fortnight_day', 'fortnight', 'diff_Target', 'S&P500_Open_Price']]
fortnight_agg = data.groupby('fortnight')[cols_to_aggregate].mean()
fortnight_std = data.groupby('fortnight')[cols_to_aggregate].std()

# Renomear as colunas de média e desvio padrão
fortnight_agg = fortnight_agg.add_suffix('_mean')
fortnight_std = fortnight_std.add_suffix('_std')

# Combinar as médias, desvios padrão, o target 'diff_Target', e 'S&P500_Open_Price' no dataset final
fortnight_features = pd.concat([fortnight_agg, fortnight_std], axis=1).reset_index()
fortnight_features['diff_Target'] = data.groupby('fortnight')['diff_Target'].first().reset_index(drop=True)
fortnight_features['S&P500_Open_Price'] = data.groupby('fortnight')['S&P500_Open_Price'].first().reset_index(drop=True)

# Aplicar os lags nas colunas de médias agrupadas por fortnight
columns_to_lag = {
    'S&P500_mean': [1, 2, 3],
    'Interest Rate_mean': [2, 4],
    'VIX_mean': [1, 2, 3],
    'GDP_mean': [2, 4],
    'Unemployment Rate_mean': [2, 4]
}

for col, lags in columns_to_lag.items():
    for lag in lags:
        lag_col = f'{col}_lag{lag}'
        fortnight_features[lag_col] = fortnight_features[col].shift(lag)

# Remover linhas com valores ausentes causados pelos lags
fortnight_features = fortnight_features.dropna()

# Filtrar para manter apenas dados até 2024-10-15
filtered_fortnight_features = fortnight_features[fortnight_features['fortnight'] <= max(data[data['date'] <= '2024-10-15']['fortnight'])]

# Salvar o novo DataFrame processado como um CSV
output_path = '/home/Herb_R00t/Tradinho/data/fortnight_time_series.csv'
filtered_fortnight_features.to_csv(output_path, index=False)