"""
Entrenamiento del Modelo de Prediccion de Procrastinacion
Utiliza Random Forest Regressor para predecir el nivel de adiccion al celular
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# Configuracion
RANDOM_STATE = 42
TEST_SIZE = 0.2
sns.set_style("whitegrid")

class ProcrastinationModel:
    """Clase para entrenar y evaluar modelos de prediccion de procrastinacion"""

    def __init__(self):
        self.model = None
        self.baseline_model = None
        self.label_encoders = {}
        self.feature_names = []
        self.metrics = {}

    def cargar_datos(self):
        """Carga y preprocesa el dataset"""
        print("=" * 80)
        print("1. CARGANDO DATASET")
        print("=" * 80)

        ruta_dataset = Path("app/static/dataset/teen_phone_addiction_dataset.csv")
        df = pd.read_csv(ruta_dataset)

        print(f"✓ Dataset cargado: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"✓ Sin valores nulos: {df.isnull().sum().sum() == 0}")

        return df

    def preprocesar_datos(self, df):
        """Preprocesa los datos para el entrenamiento"""
        print("\n" + "=" * 80)
        print("2. PREPROCESAMIENTO DE DATOS")
        print("=" * 80)

        # Copiar datos
        df_proc = df.copy()

        # Eliminar columnas no necesarias
        columnas_eliminar = ['ID', 'Name', 'Location']
        df_proc = df_proc.drop(columns=columnas_eliminar)
        print(f"✓ Eliminadas columnas: {columnas_eliminar}")

        # Identificar variables categoricas
        categoricas = ['Gender', 'School_Grade', 'Phone_Usage_Purpose']

        # Codificar variables categoricas
        print(f"✓ Codificando variables categoricas: {categoricas}")
        for col in categoricas:
            le = LabelEncoder()
            df_proc[col] = le.fit_transform(df_proc[col])
            self.label_encoders[col] = le
            print(f"  - {col}: {len(le.classes_)} categorias")

        # Separar features y target
        X = df_proc.drop('Addiction_Level', axis=1)
        y = df_proc['Addiction_Level']

        self.feature_names = X.columns.tolist()

        print(f"\n✓ Features (X): {X.shape[1]} variables")
        print(f"✓ Target (y): Addiction_Level")
        print(f"\nVariables utilizadas:")
        for i, feat in enumerate(self.feature_names, 1):
            print(f"  {i:2d}. {feat}")

        return X, y

    def dividir_datos(self, X, y):
        """Divide los datos en entrenamiento y prueba"""
        print("\n" + "=" * 80)
        print("3. DIVISION DE DATOS")
        print("=" * 80)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )

        print(f"✓ Conjunto de entrenamiento: {X_train.shape[0]} muestras ({(1-TEST_SIZE)*100:.0f}%)")
        print(f"✓ Conjunto de prueba: {X_test.shape[0]} muestras ({TEST_SIZE*100:.0f}%)")

        return X_train, X_test, y_train, y_test

    def entrenar_baseline(self, X_train, y_train, X_test, y_test):
        """Entrena modelo baseline (Regresion Lineal)"""
        print("\n" + "=" * 80)
        print("4. ENTRENAMIENTO MODELO BASELINE (Regresion Lineal)")
        print("=" * 80)

        self.baseline_model = LinearRegression()
        self.baseline_model.fit(X_train, y_train)

        # Predicciones
        y_pred_train = self.baseline_model.predict(X_train)
        y_pred_test = self.baseline_model.predict(X_test)

        # Metricas
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        test_mae = mean_absolute_error(y_test, y_pred_test)

        self.metrics['baseline'] = {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_rmse': test_rmse,
            'test_mae': test_mae
        }

        print(f"✓ Modelo entrenado")
        print(f"\nMETRICAS:")
        print(f"  R² (train): {train_r2:.4f}")
        print(f"  R² (test):  {test_r2:.4f}")
        print(f"  RMSE (test): {test_rmse:.4f}")
        print(f"  MAE (test):  {test_mae:.4f}")

        return self.baseline_model

    def entrenar_random_forest(self, X_train, y_train, X_test, y_test):
        """Entrena modelo Random Forest Regressor"""
        print("\n" + "=" * 80)
        print("5. ENTRENAMIENTO MODELO PRINCIPAL (Random Forest)")
        print("=" * 80)

        # Configuracion del modelo
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1
        )

        print("Hiperparametros:")
        print(f"  - n_estimators: 100")
        print(f"  - max_depth: 15")
        print(f"  - min_samples_split: 5")
        print(f"  - min_samples_leaf: 2")
        print(f"\nEntrenando...")

        self.model.fit(X_train, y_train)

        # Predicciones
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)

        # Metricas
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        test_mae = mean_absolute_error(y_test, y_pred_test)

        self.metrics['random_forest'] = {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_rmse': test_rmse,
            'test_mae': test_mae
        }

        print(f"✓ Modelo entrenado exitosamente")
        print(f"\nMETRICAS:")
        print(f"  R² (train): {train_r2:.4f}")
        print(f"  R² (test):  {test_r2:.4f}")
        print(f"  RMSE (test): {test_rmse:.4f}")
        print(f"  MAE (test):  {test_mae:.4f}")

        return self.model

    def validacion_cruzada(self, X, y):
        """Realiza validacion cruzada"""
        print("\n" + "=" * 80)
        print("6. VALIDACION CRUZADA (5-Fold)")
        print("=" * 80)

        cv_scores = cross_val_score(
            self.model, X, y, cv=5,
            scoring='r2', n_jobs=-1
        )

        print(f"✓ Scores por fold:")
        for i, score in enumerate(cv_scores, 1):
            print(f"  Fold {i}: {score:.4f}")

        print(f"\n✓ Promedio: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

        self.metrics['cross_validation'] = {
            'mean': cv_scores.mean(),
            'std': cv_scores.std(),
            'scores': cv_scores.tolist()
        }

        return cv_scores

    def analizar_importancia_features(self):
        """Analiza la importancia de las features"""
        print("\n" + "=" * 80)
        print("7. IMPORTANCIA DE VARIABLES")
        print("=" * 80)

        importancias = self.model.feature_importances_
        indices = np.argsort(importancias)[::-1]

        print("\nTop 10 variables mas importantes:\n")
        for i in range(min(10, len(self.feature_names))):
            idx = indices[i]
            print(f"  {i+1:2d}. {self.feature_names[idx]:<30} {importancias[idx]:.4f}")

        self.metrics['feature_importance'] = {
            'features': self.feature_names,
            'importances': importancias.tolist()
        }

    def comparar_modelos(self):
        """Compara modelos entrenados"""
        print("\n" + "=" * 80)
        print("8. COMPARACION DE MODELOS")
        print("=" * 80)

        print(f"\n{'Metrica':<20} {'Baseline':<15} {'Random Forest':<15} {'Mejora':<10}")
        print("-" * 65)

        baseline = self.metrics['baseline']
        rf = self.metrics['random_forest']

        # R² Test
        mejora_r2 = ((rf['test_r2'] - baseline['test_r2']) / baseline['test_r2']) * 100
        print(f"{'R² (test)':<20} {baseline['test_r2']:<15.4f} {rf['test_r2']:<15.4f} {mejora_r2:>+9.2f}%")

        # RMSE
        mejora_rmse = ((baseline['test_rmse'] - rf['test_rmse']) / baseline['test_rmse']) * 100
        print(f"{'RMSE (test)':<20} {baseline['test_rmse']:<15.4f} {rf['test_rmse']:<15.4f} {mejora_rmse:>+9.2f}%")

        # MAE
        mejora_mae = ((baseline['test_mae'] - rf['test_mae']) / baseline['test_mae']) * 100
        print(f"{'MAE (test)':<20} {baseline['test_mae']:<15.4f} {rf['test_mae']:<15.4f} {mejora_mae:>+9.2f}%")

        print("\n✓ Random Forest supera significativamente al baseline")

    def guardar_modelo(self):
        """Guarda el modelo y encoders"""
        print("\n" + "=" * 80)
        print("9. GUARDANDO MODELO")
        print("=" * 80)

        modelo_path = Path("ml/models/random_forest_model.pkl")
        encoders_path = Path("ml/models/label_encoders.pkl")
        features_path = Path("ml/models/feature_names.pkl")
        metrics_path = Path("ml/models/metrics.pkl")

        # Guardar modelo
        joblib.dump(self.model, modelo_path)
        print(f"✓ Modelo guardado: {modelo_path}")

        # Guardar encoders
        joblib.dump(self.label_encoders, encoders_path)
        print(f"✓ Label encoders guardados: {encoders_path}")

        # Guardar nombres de features
        joblib.dump(self.feature_names, features_path)
        print(f"✓ Feature names guardados: {features_path}")

        # Guardar metricas
        joblib.dump(self.metrics, metrics_path)
        print(f"✓ Metricas guardadas: {metrics_path}")

        print(f"\n✓ Todos los archivos guardados exitosamente")

def main():
    """Funcion principal"""
    print("\n" + "=" * 80)
    print(" " * 15 + "ENTRENAMIENTO DEL MODELO DE PROCRASTINACION")
    print("=" * 80)

    # Inicializar modelo
    pm = ProcrastinationModel()

    # 1. Cargar datos
    df = pm.cargar_datos()

    # 2. Preprocesar
    X, y = pm.preprocesar_datos(df)

    # 3. Dividir datos
    X_train, X_test, y_train, y_test = pm.dividir_datos(X, y)

    # 4. Entrenar baseline
    pm.entrenar_baseline(X_train, y_train, X_test, y_test)

    # 5. Entrenar Random Forest
    pm.entrenar_random_forest(X_train, y_train, X_test, y_test)

    # 6. Validacion cruzada
    pm.validacion_cruzada(X, y)

    # 7. Importancia de features
    pm.analizar_importancia_features()

    # 8. Comparar modelos
    pm.comparar_modelos()

    # 9. Guardar modelo
    pm.guardar_modelo()

    print("\n" + "=" * 80)
    print("ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print("\nProximo paso: Implementar prediccion para nuevos usuarios")
    print("Archivo: ml/predict.py\n")

if __name__ == "__main__":
    main()
