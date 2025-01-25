import pandas as pd, tensorflow as tf, numpy as np, spacy
from tensorflow import keras
from sklearn.model_selection import GridSearchCV
from scikeras.wrappers import KerasRegressor, KerasClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from keras import metrics
import json
import os

# Load the dataset
headlines_df = pd.read_csv('data/new_headlines.csv')

# Load spaCy model
nlp = spacy.load('en_core_web_md')

# Transform titles into vectors using spaCy embeddings
vectors = headlines_df['title'].apply(lambda x: nlp(x).vector)
vectors_df = pd.DataFrame(vectors.tolist())

# Shift 'diff' column by -1 to align targets with the next fortnight
headlines_df['diff'] = headlines_df['diff'].shift(-1)

# Remove rows with NaN values after the shift
headlines_df = headlines_df.dropna()

# Combine vectorized titles and other data
headlines = pd.concat([headlines_df.drop(columns=['title']), vectors_df], axis=1)

# Create binary target for classification (1 if diff >= 0, else 0)
headlines['up'] = headlines['diff'].apply(lambda x: 1 if x >= 0 else 0)

# Ensure diff is the last column
headlines = headlines[[col for col in headlines.columns if col != 'diff'] + ['diff']]

# Split the dataset into train, validation, and test sets based on fortnight
train = headlines[(headlines['fortnight'] >= 4) & (headlines['fortnight'] <= 205)]
val = headlines[(headlines['fortnight'] >= 206) & (headlines['fortnight'] <= 255)]
test = headlines[(headlines['fortnight'] >= 256) & (headlines['fortnight'] <= 385)]

# Separate features and targets for classification and regression
X_train, y_train_class, y_train_reg = train.iloc[:, :-2], train['up'], train['diff']
X_val, y_val_class, y_val_reg = val.iloc[:, :-2], val['up'], val['diff']
X_test, y_test_class, y_test_reg = test.iloc[:, :-2], test['up'], test['diff']

X_train.columns = X_train.columns.astype(str)
X_val.columns = X_val.columns.astype(str)
X_test.columns = X_test.columns.astype(str)

# Normalize numeric columns
colunas_numericas = X_train.select_dtypes(include='number').columns
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), colunas_numericas),
    ]
)

pipeline = Pipeline(steps=[('preprocessor', preprocessor)])

X_train = pipeline.fit_transform(X_train)
X_val = pipeline.transform(X_val)
X_test = pipeline.transform(X_test)

X_train

def create_model():
    model = keras.models.Sequential([
        keras.layers.Input(shape=[X_train.shape[1]]),
        keras.layers.Dense(100, activation='relu', kernel_regularizer=l2(0.1)),
        keras.layers.Dense(100, activation='relu', kernel_regularizer=l2(0.1)),
        keras.layers.Dense(100, activation='relu', kernel_regularizer=l2(0.1)),
        keras.layers.Dense(100, activation=keras.activations.swish),
        keras.layers.Dense(1, activation='sigmoid')  # Output for binary classification
    ])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

# Early stopping for classification
early_stopping = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)

keras_model = KerasClassifier(model=create_model, callbacks=[early_stopping])

param_grid = {
    'optimizer': ['sgd', 'rmsprop', 'adam'],
    'epochs': [50, 100],
}

grid = GridSearchCV(estimator=keras_model, param_grid=param_grid, scoring='balanced_accuracy', n_jobs=3, verbose=1)
grid_result = grid.fit(X_train, y_train_class, validation_data=(X_val, y_val_class))

best_params_classification = grid_result.best_params_

# Define the best classification model
best_classification = grid_result.best_estimator_

print(classification_report(y_test_class, best_classification.predict(X_test)))

model = keras.models.Sequential([
    keras.layers.Input(shape=[X_train.shape[1]]),
    keras.layers.Dense(250, activation='relu'),
    keras.layers.Dense(250, activation='relu'),
    keras.layers.Dense(250, activation='relu'),
    keras.layers.Dense(1, activation='linear')  # Output for regression
])

model.compile(optimizer='adam', 
              loss='mean_squared_error', 
              metrics=[
                  metrics.MeanAbsoluteError(),
                  metrics.RootMeanSquaredError()
              ])

# Creating the KerasRegressor
keras_model = KerasRegressor(model=model)

param_grid = {
    'optimizer': ['rmsprop', 'sgd'],
    'epochs': [10, 50, 100],
}

grid = GridSearchCV(estimator=keras_model, param_grid=param_grid, scoring='neg_mean_squared_error', n_jobs=1)
grid_result = grid.fit(X_train, y_train_reg, validation_data=(X_val, y_val_reg))

# Best parameters for regression
best_params_regression = grid_result.best_params_

# Extract the best regression model
best_regression_model = grid_result.best_estimator_.model_

# Combine and save best parameters
best_hyperparameters = {
    "classification": {
        **best_params_classification,
        "architecture": [
            {"type": "Dense", "units": 100, "activation": "relu", "kernel_regularizer": "l2(0.1)"},
            {"type": "Dense", "units": 100, "activation": "relu", "kernel_regularizer": "l2(0.1)"},
            {"type": "Dense", "units": 100, "activation": "relu", "kernel_regularizer": "l2(0.1)"},
            {"type": "Dense", "units": 1, "activation": "sigmoid"}
        ],
        "loss": "binary_crossentropy",
        "metrics": ["accuracy"]
    },
    "regression": {
        **best_params_regression,
        "architecture": [
            {"type": "Dense", "units": 250, "activation": "relu"},
            {"type": "Dense", "units": 250, "activation": "relu"},
            {"type": "Dense", "units": 250, "activation": "relu"},
            {"type": "Dense", "units": 1, "activation": "linear"}
        ],
        "loss": "mean_squared_error",
        "metrics": ["mean_absolute_error", "root_mean_squared_error"]
    }
}

# Save JSON and models
os.makedirs("models", exist_ok=True)

with open("models/best_NLP_params.json", "w") as f:
    json.dump(best_hyperparameters, f, indent=4)

best_classification.model_.save("models/best_classification_model.keras")
best_regression_model.save("models/best_regression_model.keras")

print("Hiperparâmetros detalhados e modelos salvos em /models")
