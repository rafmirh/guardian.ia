import pandas as pd
import numpy as np

ALCALDIAS = ["Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán", "Cuajimalpa", 
             "Cuauhtémoc", "Gustavo A. Madero", "Iztacalco", "Iztapalapa", "La Magdalena Contreras",
             "Miguel Hidalgo", "Milpa Alta", "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco"]

def leer_datos_csv(archivo='usurpacion_etl.csv'):
    """Lee y retorna el DataFrame del CSV"""
    return pd.read_csv(archivo)

def calcular_probabilidad_riesgo(sexo, edad, indice_alcaldia, df):
    """Calcula la probabilidad de riesgo basándose en frecuencias estadísticas"""
    # Filtrar datos similares
    similares = df[(df['sexo'] == sexo) & (abs(df['edad'] - edad) <= 5) & (df['indice_alcaldia'] == indice_alcaldia)]
    
    if len(similares) == 0:
        # Si no hay datos exactos, usar datos más generales
        similares = df[(df['sexo'] == sexo) & (abs(df['edad'] - edad) <= 10)]
    
    if len(similares) == 0:
        # Fallback: usar promedios generales
        return 15.0  # Probabilidad base
    
    # Calcular riesgo basado en frecuencia relativa
    total_casos = len(df)
    casos_similares = len(similares)
    
    # Factores de riesgo
    factor_edad = 1.0
    if 18 <= edad <= 35: factor_edad = 1.3  # Mayor riesgo en adultos jóvenes
    elif edad > 65: factor_edad = 1.2  # Mayor riesgo en adultos mayores
    
    factor_sexo = 1.1 if sexo == 0 else 1.0  # Ligeramente mayor riesgo para mujeres
    
    # Cálculo final de probabilidad
    probabilidad_base = (casos_similares / total_casos) * 100
    probabilidad_ajustada = min(probabilidad_base * factor_edad * factor_sexo * 5, 95.0)
    
    return max(probabilidad_ajustada, 5.0)  # Mínimo 5%, máximo 95%

def validar_inputs(sexo, edad, alcaldia_idx):
    """Valida los inputs del usuario"""
    if sexo not in [0, 1] or not isinstance(edad, int) or edad < 0 or edad > 120:
        return False
    if alcaldia_idx < 0 or alcaldia_idx >= len(ALCALDIAS):
        return False
    return True

def obtener_alcaldias():
    """Retorna la lista de alcaldías ordenadas"""
    return ALCALDIAS