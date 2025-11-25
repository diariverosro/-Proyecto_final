# Importar librerías
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Cargar datos
data_sleep = pd.read_csv("Sleep_health_and_lifestyle_dataset.csv")
#print(data_sleep.head())

# Transformación de "Sleep Disorder"
data_sleep['Sleep Disorder'].fillna('No Sleep Disorder', inplace=True)

# Transformación de "Blood Pressure"
data_sleep[['Systolic Pressure', 'Diastolic Pressure']] = data_sleep['Blood Pressure'].str.split('/', expand=True)
data_sleep['Systolic Pressure'] = pd.to_numeric(data_sleep['Systolic Pressure'])
data_sleep['Diastolic Pressure'] = pd.to_numeric(data_sleep['Diastolic Pressure'])

# Transformar columnas categoricas
# Variables categóricas
categorical_cols = ['Gender', 'Occupation', 'BMI Category', 'Sleep Disorder']
# Aplicar One-Hot Encoding
data_sleep_encoded = pd.get_dummies(data_sleep, columns=categorical_cols, drop_first=True)

# Seleccionar variable objetivo y variables predictoras
#y = data_sleep_encoded['Quality of Sleep']
le = LabelEncoder()
y = le.fit_transform(data_sleep_encoded['Quality of Sleep'])
X = data_sleep_encoded.drop(columns=['Quality of Sleep', 'Person ID', 'Blood Pressure'])

print("Shape of X:", X.shape)
print("Shape of y:", y.shape)

# Dividar el conjunto de pruebas y entrenamiento
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Shape of X_train:", X_train.shape)
print("Shape of X_test:", X_test.shape)
print("Shape of y_train:", y_train.shape)
print("Shape of y_test:", y_test.shape)

# Implementar XGBoost Clasificador
model = XGBClassifier(
    objective="multi:softmax",
    num_class=len(np.unique(y)),
    eval_metric="mlogloss",
    learning_rate=0.1,
    max_depth=6,
    n_estimators=150,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_train, y_train)

# Predicciones
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))

# Reporte de clasificación
print("\nReporte de Clasificación:")
print(classification_report(y_test, y_pred))

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Matriz de Confusión - XGBoost")
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.show()

# Importancia de variables
plt.figure(figsize=(10, 6))
sns.barplot(
    x=model.feature_importances_,
    y=X.columns
)
plt.title("Importancia de Variables - XGBoost")
plt.show()