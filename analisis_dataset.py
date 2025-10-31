"""
Analisis Exploratorio de Datos (EDA) para Prediccion de Procrastinacion
Dataset: teen_phone_addiction_dataset.csv
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuracion de visualizacion
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def cargar_datos():
    """Carga el dataset de adiccion al celular"""
    ruta_dataset = Path("app/static/dataset/teen_phone_addiction_dataset.csv")
    df = pd.read_csv(ruta_dataset)
    print("=" * 80)
    print("DATASET CARGADO EXITOSAMENTE")
    print("=" * 80)
    print(f"\nDimensiones: {df.shape[0]} filas x {df.shape[1]} columnas\n")
    return df

def analisis_basico(df):
    """Realiza un analisis basico del dataset"""
    print("\n" + "=" * 80)
    print("1. INFORMACION GENERAL DEL DATASET")
    print("=" * 80)
    print("\nColumnas disponibles:")
    print("-" * 80)
    for i, col in enumerate(df.columns, 1):
        tipo = str(df[col].dtype)
        nulos = df[col].isnull().sum()
        print(f"{i:2d}. {col:<30} | Tipo: {tipo:<10} | Nulos: {nulos}")

    print("\n" + "=" * 80)
    print("2. ESTADISTICAS DESCRIPTIVAS")
    print("=" * 80)
    print(df.describe())

    print("\n" + "=" * 80)
    print("3. VARIABLE OBJETIVO: Addiction_Level")
    print("=" * 80)
    print(f"Min: {df['Addiction_Level'].min():.2f}")
    print(f"Max: {df['Addiction_Level'].max():.2f}")
    print(f"Media: {df['Addiction_Level'].mean():.2f}")
    print(f"Mediana: {df['Addiction_Level'].median():.2f}")
    print(f"Desv. Est: {df['Addiction_Level'].std():.2f}")

def analizar_correlaciones(df):
    """Analiza correlaciones con la variable objetivo"""
    print("\n" + "=" * 80)
    print("4. CORRELACIONES CON ADDICTION_LEVEL (NIVEL DE PROCRASTINACION)")
    print("=" * 80)

    # Seleccionar solo columnas numericas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    correlaciones = df[columnas_numericas].corr()['Addiction_Level'].sort_values(ascending=False)

    print("\nVariables mas correlacionadas (positiva y negativamente):\n")
    print(correlaciones)

    # Identificar variables importantes
    print("\n" + "-" * 80)
    print("VARIABLES MAS INFLUYENTES:")
    print("-" * 80)
    importantes = correlaciones[abs(correlaciones) > 0.3]
    for var, corr in importantes.items():
        if var != 'Addiction_Level':
            direccion = "aumenta" if corr > 0 else "disminuye"
            print(f"• {var:<30}: {corr:>6.3f} -> {direccion} la procrastinacion")

def mapear_variables_formulario(df):
    """Mapea las variables del dataset con las del formulario"""
    print("\n" + "=" * 80)
    print("5. MAPEO: DATASET <-> FORMULARIO")
    print("=" * 80)

    mapeo = {
        "Dataset": [
            "Age", "Gender", "School_Grade", "Daily_Usage_Hours",
            "Sleep_Hours", "Academic_Performance", "Social_Interactions",
            "Exercise_Hours", "Screen_Time_Before_Bed", "Phone_Checks_Per_Day",
            "Apps_Used_Daily", "Time_on_Social_Media", "Time_on_Gaming",
            "Time_on_Education", "Phone_Usage_Purpose", "Weekend_Usage_Hours"
        ],
        "Formulario": [
            "age", "gender", "schoolgrade", "daily_usage",
            "sleephours", "academic_perf", "social",
            "exercise", "screen_before_bed", "checks_per_day",
            "apps_daily", "time_social_media", "time_gaming",
            "time_education", "purpose", "weekend_usage"
        ],
        "Tipo": [
            "numerico", "categorico", "categorico", "numerico",
            "numerico", "numerico", "numerico",
            "numerico", "numerico", "numerico",
            "numerico", "numerico", "numerico",
            "numerico", "categorico", "numerico"
        ]
    }

    df_mapeo = pd.DataFrame(mapeo)
    print("\n", df_mapeo.to_string(index=False))

    print("\n" + "-" * 80)
    print("NOTA: Todas las variables del formulario tienen correspondencia con el dataset")
    print("-" * 80)

def recomendar_modelo():
    """Recomienda el mejor modelo para el problema"""
    print("\n" + "=" * 80)
    print("6. RECOMENDACION DE MODELOS DE MACHINE LEARNING")
    print("=" * 80)

    print("\nTIPO DE PROBLEMA: REGRESION")
    print("Variable objetivo: Addiction_Level (continua de 0 a 10)")
    print("\n" + "-" * 80)

    modelos = [
        {
            "nombre": "Random Forest Regressor",
            "pros": [
                "Excelente para capturar relaciones no lineales",
                "Maneja bien variables categoricas y numericas",
                "Resistente a overfitting",
                "Proporciona importancia de features",
                "No requiere normalizacion"
            ],
            "contras": [
                "Puede ser lento en datasets muy grandes",
                "Menos interpretable que modelos lineales"
            ],
            "recomendacion": "★★★★★ ALTAMENTE RECOMENDADO"
        },
        {
            "nombre": "Gradient Boosting (XGBoost/LightGBM)",
            "pros": [
                "Mejor rendimiento en muchos casos",
                "Excelente precision",
                "Maneja bien datos desbalanceados",
                "Feature importance integrado"
            ],
            "contras": [
                "Requiere tunning de hiperparametros",
                "Puede hacer overfitting si no se configura bien",
                "Mas complejo de implementar"
            ],
            "recomendacion": "★★★★☆ RECOMENDADO PARA OPTIMIZACION"
        },
        {
            "nombre": "Support Vector Regression (SVR)",
            "pros": [
                "Efectivo en espacios de alta dimension",
                "Versatil con diferentes kernels"
            ],
            "contras": [
                "Requiere normalizacion de datos",
                "Lento con datasets grandes",
                "Dificil de interpretar"
            ],
            "recomendacion": "★★★☆☆ ALTERNATIVA"
        },
        {
            "nombre": "Regresion Lineal Multiple",
            "pros": [
                "Simple e interpretable",
                "Rapido de entrenar",
                "Buena linea base"
            ],
            "contras": [
                "Asume relaciones lineales",
                "Menos flexible",
                "Menor precision esperada"
            ],
            "recomendacion": "★★☆☆☆ SOLO COMO BASELINE"
        }
    ]

    for i, modelo in enumerate(modelos, 1):
        print(f"\n{i}. {modelo['nombre']}")
        print(f"   Recomendacion: {modelo['recomendacion']}")
        print("\n   PROS:")
        for pro in modelo['pros']:
            print(f"   + {pro}")
        print("\n   CONTRAS:")
        for contra in modelo['contras']:
            print(f"   - {contra}")
        print("\n" + "-" * 80)

    print("\n" + "=" * 80)
    print("RECOMENDACION FINAL")
    print("=" * 80)
    print("""
ESTRATEGIA PROPUESTA:

1. FASE 1 - BASELINE:
   - Entrenar Regresion Lineal como punto de referencia
   - Establecer metricas base (RMSE, MAE, R²)

2. FASE 2 - MODELO PRINCIPAL:
   - Random Forest Regressor (RECOMENDADO)
   - Razones:
     * Excelente balance precision/complejidad
     * Maneja bien tus 16 variables sin normalizacion
     * Proporciona importancia de features
     * Robusto y confiable
     * Ideal para proyectos academicos

3. FASE 3 - OPTIMIZACION (OPCIONAL):
   - Probar XGBoost/LightGBM si se necesita mas precision
   - Fine-tuning de hiperparametros

METRICAS A USAR:
- R² Score (coeficiente de determinacion)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Cross-Validation Score

NOTA: Para un proyecto academico sobre procrastinacion estudiantil,
Random Forest es la mejor opcion por su balance entre rendimiento,
interpretabilidad y facilidad de implementacion.
    """)

def plan_implementacion():
    """Muestra el plan de implementacion"""
    print("\n" + "=" * 80)
    print("7. PLAN DE IMPLEMENTACION")
    print("=" * 80)
    print("""
PASOS A SEGUIR:

1. Preprocesamiento de Datos
   - Codificar variables categoricas (Gender, School_Grade, Purpose)
   - Manejar valores faltantes si existen
   - Dividir en train/test (80/20 o 70/30)

2. Entrenamiento del Modelo
   - Entrenar Random Forest Regressor
   - Realizar validacion cruzada
   - Ajustar hiperparametros (n_estimators, max_depth)

3. Evaluacion
   - Calcular metricas en conjunto de prueba
   - Analizar importancia de features
   - Visualizar predicciones vs valores reales

4. Guardado del Modelo
   - Serializar modelo con joblib/pickle
   - Guardar escaladores si se usan

5. Integracion con Flask
   - Crear endpoint /predecir
   - Recibir datos del formulario
   - Retornar nivel de procrastinacion + recomendaciones

ARCHIVOS A CREAR:
- ml/preprocessing.py      -> Preprocesamiento de datos
- ml/train_model.py        -> Entrenamiento del modelo
- ml/predict.py            -> Funciones de prediccion
- ml/models/               -> Carpeta para guardar modelos entrenados
- ml/models/random_forest_model.pkl
- ml/models/label_encoders.pkl

    """)

def main():
    """Funcion principal"""
    print("\n" + "=" * 80)
    print(" " * 20 + "ANALISIS DE DATASET - PROCRASTINACION")
    print("=" * 80)

    # Cargar datos
    df = cargar_datos()

    # Analisis basico
    analisis_basico(df)

    # Analizar correlaciones
    analizar_correlaciones(df)

    # Mapear variables
    mapear_variables_formulario(df)

    # Recomendar modelo
    recomendar_modelo()

    # Plan de implementacion
    plan_implementacion()

    print("\n" + "=" * 80)
    print("ANALISIS COMPLETADO")
    print("=" * 80)
    print("\nProximo paso: Ejecutar el script de entrenamiento del modelo")
    print("Comando: python ml/train_model.py\n")

if __name__ == "__main__":
    main()
