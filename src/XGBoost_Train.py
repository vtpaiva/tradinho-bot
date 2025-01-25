import pandas as pd
import xgboost as xgb
import optuna
from sklearn.metrics import mean_squared_error
import numpy as np
import json

# Carregar os dados já processados
data = pd.read_csv('/home/Herb_R00t/Tradinho/data/fortnight_time_series.csv')

# Ordenar por fortnight para garantir ordem cronológica
data = data.sort_values(by='fortnight')

# Criar a coluna de target da próxima quinzena (shift para frente)
data['diff_Target_next'] = data['diff_Target'].shift(-1)

# Remover a última linha porque não temos o target da próxima quinzena
data = data[:-1]

# Separar as features e o target
features = data.drop(columns=['fortnight', 'diff_Target', 'diff_Target_next', 'S&P500_Open_Price', 'S&P500_Close_Price'])
target = data['diff_Target_next']

# Separar os conjuntos de treino, validação e teste com base em fortnight
train_data = data[(data['fortnight'] >= 4) & (data['fortnight'] <= 205)]
val_data = data[(data['fortnight'] >= 206) & (data['fortnight'] <= 255)]
test_data = data[(data['fortnight'] >= 256) & (data['fortnight'] <= 385)]

X_train = train_data[features.columns]
y_train = train_data['diff_Target_next']

X_val = val_data[features.columns]
y_val = val_data['diff_Target_next']

X_test = test_data[features.columns]
y_test = test_data['diff_Target_next']

# Função de otimização com Optuna
def objective(trial):
    param = {
        "objective": "reg:squarederror",
        "tree_method": "hist",
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "min_child_weight": trial.suggest_float("min_child_weight", 1, 10),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "lambda": trial.suggest_float("lambda", 1e-3, 10.0, log=True),
        "alpha": trial.suggest_float("alpha", 1e-3, 10.0, log=True),
    }

    # Treinar o modelo com os parâmetros sugeridos
    model = xgb.XGBRegressor(**param, n_estimators=100)
    model.fit(X_train, y_train)

    # Previsão no conjunto de validação
    preds_val = model.predict(X_val)
    rmse_val = mean_squared_error(y_val, preds_val, squared=False)
    return rmse_val

# Otimização com Optuna
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=80)  # Ajustado para 80 trials

# Melhor modelo
best_params = study.best_params
print("Melhores Parâmetros:", best_params)

# Salvar os melhores parâmetros em um arquivo JSON
params_output_path = '/home/Herb_R00t/Tradinho/models/best_xgboost_params.json'
with open(params_output_path, 'w') as f:
    json.dump(best_params, f)

print(f"Melhores parâmetros salvos em {params_output_path}")

# Treinar o modelo final com os melhores parâmetros
final_model = xgb.XGBRegressor(**best_params, n_estimators=100)
final_model.fit(pd.concat([X_train, X_val]), pd.concat([y_train, y_val]))  # Treinar no conjunto combinado de treino e validação

# Salvar o modelo final treinado
model_output_path = '/home/Herb_R00t/Tradinho/models/final_xgboost_model.bin'
final_model.save_model(model_output_path)
print(f"Modelo XGBoost salvo em {model_output_path}")

# Previsão no conjunto de teste
final_preds = final_model.predict(X_test)

# Avaliação final
final_rmse = mean_squared_error(y_test, final_preds, squared=False)
print("RMSE Final no Teste:", final_rmse)