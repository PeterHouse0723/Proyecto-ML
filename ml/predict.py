"""
Modulo de Prediccion de Nivel de Procrastinacion
Utiliza el modelo Random Forest entrenado para predecir el nivel de adiccion
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

class ProcrastinationPredictor:
    """Clase para realizar predicciones de procrastinacion"""

    def __init__(self):
        self.model = None
        self.label_encoders = None
        self.feature_names = None
        self.cargar_modelo()

    def cargar_modelo(self):
        """Carga el modelo y componentes necesarios"""
        try:
            modelo_path = Path("ml/models/random_forest_model.pkl")
            encoders_path = Path("ml/models/label_encoders.pkl")
            features_path = Path("ml/models/feature_names.pkl")

            self.model = joblib.load(modelo_path)
            self.label_encoders = joblib.load(encoders_path)
            self.feature_names = joblib.load(features_path)

            return True
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
            return False

    def mapear_genero(self, genero_str):
        """Mapea el genero del formulario al formato del dataset"""
        mapeo = {
            'M': 'Male',
            'F': 'Female',
            'O': 'Other',
            'masculino': 'Male',
            'femenino': 'Female',
            'otro': 'Other'
        }
        return mapeo.get(genero_str, 'Other')

    def mapear_grado_escolar(self, grado_str):
        """Mapea el grado escolar al formato del dataset"""
        # El dataset usa: 7th, 8th, 9th, 10th, 11th, 12th
        # Si recibimos texto como "Universidad", mapeamos a grado alto
        mapeo = {
            'Primaria': '7th',
            'Secundaria': '9th',
            'Preparatoria': '11th',
            'Universidad': '12th',
            'Posgrado': '12th',
            'Doctorado': '12th'
        }

        # Si ya viene en formato correcto
        if grado_str in ['7th', '8th', '9th', '10th', '11th', '12th']:
            return grado_str

        return mapeo.get(grado_str, '10th')

    def mapear_proposito(self, proposito_str):
        """Mapea el proposito de uso del celular"""
        # Dataset usa: Education, Social Media, Gaming, Browsing, Other
        mapeo = {
            'educacion': 'Education',
            'redes': 'Social Media',
            'entretenimiento': 'Browsing',
            'comunicacion': 'Other',
            'juegos': 'Gaming',
            'otro': 'Other'
        }
        return mapeo.get(proposito_str, 'Other')

    def preparar_datos_formulario(self, datos_formulario, datos_cuenta=None):
        """
        Prepara los datos del formulario para la prediccion

        Args:
            datos_formulario: dict con datos del formulario
            datos_cuenta: dict con datos de la cuenta del usuario (opcional)

        Returns:
            DataFrame con las features preparadas
        """
        # Crear diccionario con todas las features necesarias
        features = {}

        # 1. Age - de cuenta o formulario
        if datos_cuenta and 'edad' in datos_cuenta:
            features['Age'] = int(datos_cuenta['edad'])
        else:
            features['Age'] = int(datos_formulario.get('age', 16))

        # 2. Gender - de cuenta o formulario
        if datos_cuenta and 'genero' in datos_cuenta:
            genero = self.mapear_genero(datos_cuenta['genero'])
        else:
            genero = self.mapear_genero(datos_formulario.get('gender', 'O'))

        # Codificar genero
        features['Gender'] = self.label_encoders['Gender'].transform([genero])[0]

        # 3. School_Grade - de cuenta o formulario
        if datos_cuenta and 'grado_escolaridad' in datos_cuenta and datos_cuenta['grado_escolaridad']:
            grado = self.mapear_grado_escolar(datos_cuenta['grado_escolaridad'])
        else:
            grado = self.mapear_grado_escolar(datos_formulario.get('schoolgrade', 'Universidad'))

        # Codificar grado escolar
        features['School_Grade'] = self.label_encoders['School_Grade'].transform([grado])[0]

        # 4. Daily_Usage_Hours - del formulario
        features['Daily_Usage_Hours'] = float(datos_formulario.get('daily_usage', 5.0))

        # 5. Sleep_Hours - del formulario
        features['Sleep_Hours'] = float(datos_formulario.get('sleephours', 7.0))

        # 6. Academic_Performance - del formulario (convertir escala 0-5 a 0-100)
        academic = datos_formulario.get('academic_perf', '4.0')
        try:
            # Convertir de escala 0-5 a 0-100
            academic_5_scale = float(academic)
            features['Academic_Performance'] = int((academic_5_scale / 5.0) * 100)
        except:
            features['Academic_Performance'] = 80  # Default: 4.0/5.0 = 80/100

        # 7. Social_Interactions - valor por defecto (ya no se pregunta en formulario)
        features['Social_Interactions'] = 5

        # 8. Exercise_Hours - del formulario
        features['Exercise_Hours'] = float(datos_formulario.get('exercise', 1.0))

        # 9-11. Variables psicologicas - valores por defecto (medios)
        # Estos datos normalmente se obtendrian de un cuestionario psicologico
        features['Anxiety_Level'] = 5
        features['Depression_Level'] = 5
        features['Self_Esteem'] = 5

        # 12. Parental_Control - valor por defecto
        features['Parental_Control'] = 0

        # 13. Screen_Time_Before_Bed - del formulario (ya viene en horas)
        screen_before_bed = float(datos_formulario.get('screen_before_bed', 1.0))
        features['Screen_Time_Before_Bed'] = screen_before_bed  # Ya esta en horas

        # 14. Phone_Checks_Per_Day - del formulario
        features['Phone_Checks_Per_Day'] = int(datos_formulario.get('checks_per_day', 50))

        # 15. Apps_Used_Daily - del formulario
        apps = datos_formulario.get('apps_daily', [])
        if isinstance(apps, list):
            features['Apps_Used_Daily'] = len(apps)
        else:
            features['Apps_Used_Daily'] = 10

        # 16. Time_on_Social_Media - del formulario (ya viene en horas)
        social_media = float(datos_formulario.get('time_social_media', 2.0))
        features['Time_on_Social_Media'] = social_media  # Ya esta en horas

        # 17. Time_on_Gaming - del formulario (ya viene en horas)
        gaming = float(datos_formulario.get('time_gaming', 1.0))
        features['Time_on_Gaming'] = gaming  # Ya esta en horas

        # 18. Time_on_Education - del formulario (ya viene en horas)
        education = float(datos_formulario.get('time_education', 0.5))
        features['Time_on_Education'] = education  # Ya esta en horas

        # 19. Phone_Usage_Purpose - del formulario
        proposito = self.mapear_proposito(datos_formulario.get('purpose', 'otro'))
        features['Phone_Usage_Purpose'] = self.label_encoders['Phone_Usage_Purpose'].transform([proposito])[0]

        # 20. Family_Communication - valor por defecto
        features['Family_Communication'] = 5

        # 21. Weekend_Usage_Hours - del formulario
        features['Weekend_Usage_Hours'] = float(datos_formulario.get('weekend_usage', 6.0))

        # Crear DataFrame con el orden correcto de features
        df = pd.DataFrame([features])
        df = df[self.feature_names]  # Asegurar el orden correcto

        return df

    def predecir(self, datos_formulario, datos_cuenta=None):
        """
        Predice el nivel de procrastinacion

        Args:
            datos_formulario: dict con datos del formulario
            datos_cuenta: dict con datos de la cuenta (opcional)

        Returns:
            dict con prediccion y analisis
        """
        # Preparar datos
        X = self.preparar_datos_formulario(datos_formulario, datos_cuenta)

        # Realizar prediccion
        prediccion = self.model.predict(X)[0]

        # Limitar entre 1 y 10
        prediccion = max(1.0, min(10.0, prediccion))

        # Clasificar nivel
        if prediccion < 3:
            nivel = "Bajo"
            color = "green"
            descripcion = "Tienes un nivel bajo de procrastinacion. Mantienes un buen equilibrio con el uso del celular."
        elif prediccion < 5:
            nivel = "Moderado-Bajo"
            color = "lightgreen"
            descripcion = "Tu nivel de procrastinacion es moderado-bajo. Estas en el camino correcto, pero puedes mejorar."
        elif prediccion < 7:
            nivel = "Moderado"
            color = "orange"
            descripcion = "Tienes un nivel moderado de procrastinacion. Es momento de implementar cambios en tus habitos."
        elif prediccion < 9:
            nivel = "Alto"
            color = "orangered"
            descripcion = "Tu nivel de procrastinacion es alto. El uso del celular esta afectando tu productividad significativamente."
        else:
            nivel = "Muy Alto"
            color = "red"
            descripcion = "Nivel de procrastinacion muy alto. Es urgente tomar medidas para reducir el tiempo en el celular."

        # Generar recomendaciones basadas en los datos
        recomendaciones = self.generar_recomendaciones(datos_formulario, prediccion)

        # Calcular factores de riesgo
        factores_riesgo = self.identificar_factores_riesgo(datos_formulario)

        return {
            'prediccion': round(prediccion, 2),
            'nivel': nivel,
            'color': color,
            'descripcion': descripcion,
            'recomendaciones': recomendaciones,
            'factores_riesgo': factores_riesgo,
            'datos_analizados': {
                'horas_diarias': datos_formulario.get('daily_usage', 0),
                'apps_usadas': datos_formulario.get('apps_daily', []),
                'tiempo_redes': datos_formulario.get('time_social_media', 0),
                'horas_sueno': datos_formulario.get('sleephours', 0)
            }
        }

    def generar_recomendaciones(self, datos, prediccion):
        """Genera recomendaciones personalizadas"""
        recomendaciones = []

        # Analizar horas diarias de uso
        horas_uso = float(datos.get('daily_usage', 0))
        if horas_uso > 6:
            recomendaciones.append({
                'tipo': 'critico',
                'titulo': 'Reduce el tiempo de uso del celular',
                'mensaje': f'Usas {horas_uso} horas diarias. Intenta reducir a 4-5 horas estableciendo limites en las apps.'
            })
        elif horas_uso > 4:
            recomendaciones.append({
                'tipo': 'advertencia',
                'titulo': 'Controla tu tiempo en el celular',
                'mensaje': f'Usas {horas_uso} horas diarias. Considera establecer tiempos especificos para usar el celular.'
            })

        # Analizar redes sociales (ahora en horas)
        tiempo_redes = float(datos.get('time_social_media', 0))
        if tiempo_redes > 3:  # Mas de 3 horas
            recomendaciones.append({
                'tipo': 'critico',
                'titulo': 'Limita el tiempo en redes sociales',
                'mensaje': f'Pasas {tiempo_redes:.1f} horas en redes sociales. Usa temporizadores de apps para limitarlo a 1-1.5 horas.'
            })
        elif tiempo_redes > 2:  # Mas de 2 horas
            recomendaciones.append({
                'tipo': 'advertencia',
                'titulo': 'Reduce tiempo en redes sociales',
                'mensaje': f'Pasas {tiempo_redes:.1f} horas en redes sociales. Considera reducirlo gradualmente.'
            })

        # Analizar sueno
        horas_sueno = float(datos.get('sleephours', 7))
        if horas_sueno < 7:
            recomendaciones.append({
                'tipo': 'advertencia',
                'titulo': 'Mejora tus habitos de sueno',
                'mensaje': f'Duermes {horas_sueno} horas. Intenta dormir 7-9 horas y evita el celular 1 hora antes de dormir.'
            })

        # Analizar pantalla antes de dormir (ahora en horas)
        pantalla_dormir = float(datos.get('screen_before_bed', 0))
        if pantalla_dormir > 1:  # Mas de 1 hora
            recomendaciones.append({
                'tipo': 'advertencia',
                'titulo': 'Evita pantallas antes de dormir',
                'mensaje': f'Usas el celular {pantalla_dormir:.1f} horas antes de dormir. Intenta reducirlo a menos de 0.5 horas (30 minutos).'
            })
        elif pantalla_dormir > 0.5:  # Mas de 30 minutos
            recomendaciones.append({
                'tipo': 'consejo',
                'titulo': 'Reduce pantallas antes de dormir',
                'mensaje': 'Intenta usar el celular menos de 30 minutos antes de acostarte para mejorar la calidad del sueno.'
            })

        # Analizar ejercicio
        ejercicio = float(datos.get('exercise', 0))
        if ejercicio < 2:
            recomendaciones.append({
                'tipo': 'consejo',
                'titulo': 'Aumenta la actividad fisica',
                'mensaje': 'Haz al menos 3-4 horas de ejercicio a la semana para reducir el estres y mejorar el enfoque.'
            })

        # Recomendaciones generales segun nivel
        if prediccion >= 8:
            recomendaciones.append({
                'tipo': 'critico',
                'titulo': 'Busca apoyo profesional',
                'mensaje': 'Considera hablar con un orientador o psicologo sobre tus habitos digitales.'
            })

        # Siempre agregar al menos una recomendacion positiva
        recomendaciones.append({
            'tipo': 'consejo',
            'titulo': 'Implementa la tecnica Pomodoro',
            'mensaje': 'Estudia 25 minutos sin distracciones, descansa 5 minutos. Repite 4 veces y toma un descanso largo.'
        })

        return recomendaciones[:5]  # Maximo 5 recomendaciones

    def identificar_factores_riesgo(self, datos):
        """Identifica los principales factores de riesgo"""
        factores = []

        horas_uso = float(datos.get('daily_usage', 0))
        tiempo_redes = float(datos.get('time_social_media', 0))  # Ya esta en horas
        tiempo_juegos = float(datos.get('time_gaming', 0))  # Ya esta en horas
        revisiones = int(datos.get('checks_per_day', 0))

        if horas_uso > 6:
            factores.append({
                'factor': 'Uso excesivo del celular',
                'valor': f'{horas_uso} horas/dia',
                'impacto': 'Alto'
            })

        if tiempo_redes > 3:
            factores.append({
                'factor': 'Tiempo elevado en redes sociales',
                'valor': f'{tiempo_redes:.1f} horas/dia',
                'impacto': 'Alto'
            })

        if revisiones > 100:
            factores.append({
                'factor': 'Revisar celular frecuentemente',
                'valor': f'{revisiones} veces/dia',
                'impacto': 'Medio'
            })

        if tiempo_juegos > 2:
            factores.append({
                'factor': 'Tiempo en videojuegos',
                'valor': f'{tiempo_juegos:.1f} horas/dia',
                'impacto': 'Medio'
            })

        return factores

# Instancia global del predictor
predictor = ProcrastinationPredictor()
