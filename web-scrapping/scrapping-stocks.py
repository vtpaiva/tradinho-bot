import pandas as pd
from fredapi import Fred
import yfinance as yf
from datetime import datetime, timedelta

# Usar a chave API do FRED
fred = Fred(api_key='your_api_key')

# Função para coletar dados com tratamento de erros
def collect_fred_series(series_id, series_name):
    try:
        data = fred.get_series(series_id, start='2009-12-30', end='2024-10-30')
        print(f"{series_name} coletado com sucesso!")
        return data
    except Exception as e:
        print(f"Erro ao coletar {series_name}: {e}")
        return None

# Coletar os dados do FRED
interest_rate = collect_fred_series('DFF', 'Taxa de Juros')
gdp = collect_fred_series('GDP', 'PIB')
unemployment_rate = collect_fred_series('UNRATE', 'Taxa de Desemprego')
cpi = collect_fred_series('CPIAUCSL', 'Inflação (CPI)')
inflation_expectations = collect_fred_series('T5YIE', 'Expectativa de Inflação')
yield_spread = collect_fred_series('T10Y2Y', 'Spread de Rendimento 10y-2y')
vix = collect_fred_series('VIXCLS', 'Índice VIX')
industrial_production = collect_fred_series('INDPRO', 'Produção Industrial')
consumer_confidence = collect_fred_series('UMCSENT', 'Índice de Confiança do Consumidor')
hourly_earnings = collect_fred_series('CES0500000003', 'Variação na Massa Salarial')
nfc_index = collect_fred_series('NFCI', 'Índice NFCI')
savings_rate = collect_fred_series('PSAVERT', 'Taxa de Poupança Pessoal')
pce = collect_fred_series('PCE', 'Despesas Pessoais')
money_supply = collect_fred_series('M2SL', 'Oferta de Dinheiro (M2)')
ppi = collect_fred_series('PPIACO', 'Índice de Preços ao Produtor')

# Coletar os preços do S&P500 pelo Yahoo Finance
sp500 = yf.download('^GSPC', start='2009-12-30', end='2024-10-23')

# Convertendo o índice de datas do S&P 500 para o formato sem UTC
sp500.index = sp500.index.tz_localize(None)

# Consolidar todos os dados em um único DataFrame usando as datas do S&P500 como referência
df_final = pd.DataFrame(index=sp500.index)

# Adicionar os dados do FRED ao DataFrame, reindexando para garantir o alinhamento de datas
df_final['S&P500'] = sp500['Adj Close']
df_final['Interest Rate'] = interest_rate.reindex(df_final.index, method='ffill')  # Preencher valores ausentes com o último valor disponível
df_final['GDP'] = gdp.reindex(df_final.index, method='ffill')
df_final['Unemployment Rate'] = unemployment_rate.reindex(df_final.index, method='ffill')
df_final['CPI'] = cpi.reindex(df_final.index, method='ffill')
df_final['Inflation Expectations'] = inflation_expectations.reindex(df_final.index, method='ffill')
df_final['Yield Spread'] = yield_spread.reindex(df_final.index, method='ffill')
df_final['VIX'] = vix.reindex(df_final.index, method='ffill')
df_final['Industrial Production'] = industrial_production.reindex(df_final.index, method='ffill')
df_final['Consumer Confidence'] = consumer_confidence.reindex(df_final.index, method='ffill')
df_final['Hourly Earnings'] = hourly_earnings.reindex(df_final.index, method='ffill')
df_final['NFCI'] = nfc_index.reindex(df_final.index, method='ffill')
df_final['Savings Rate'] = savings_rate.reindex(df_final.index, method='ffill')
df_final['PCE'] = pce.reindex(df_final.index, method='ffill')
df_final['Money Supply'] = money_supply.reindex(df_final.index, method='ffill')
df_final['PPI'] = ppi.reindex(df_final.index, method='ffill')

# Ajustando as casas decimais da base de dados
df_final['S&P500'] = df_final['S&P500'].round(2)
df_final['GDP'] = df_final['GDP'].round(2)
df_final['CPI'] = df_final['CPI'].round(2)
df_final['Industrial Production'] = df_final['Industrial Production'].round(2)
df_final['NFCI'] = df_final['NFCI'].round(3)

# Adicionar a coluna 'fortnight' (quinzena), calculando o número de quinzenas desde a data inicial
start_date = pd.to_datetime("2009-12-30")
df_final['fortnight'] = ((df_final.index - start_date) // timedelta(days=14)).astype(int)

# Salvando o DataFrame consolidado em um arquivo CSV
df_final.to_csv('tradinho-stocks.csv')