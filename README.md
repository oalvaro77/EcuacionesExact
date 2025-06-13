# Analizador de Ecuaciones Diferenciales Exactas

Este programa permite analizar ecuaciones diferenciales exactas, determinar si son exactas o no, y en caso de no serlo, calcular el factor integrante para transformarlas en exactas.

## Requisitos

- Python 3.7 o superior
- sympy

## Instalación

1. Clona este repositorio o descarga los archivos
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecuta el programa:
```bash
python interfaz.py
```

2. En la interfaz gráfica, ingresa la ecuación diferencial en el formato:
   - Para ecuaciones de la forma M(x,y)dx + N(x,y)dy = 0
   - Ejemplo: (x-y+1)dx-dy=0

3. Haz clic en "Analizar" para ver los resultados

## Características

- Determina si una ecuación diferencial es exacta
- Muestra las derivadas parciales
- Calcula el factor integrante si la ecuación no es exacta
- Muestra la nueva ecuación después de aplicar el factor integrante
- Verifica si la nueva ecuación es exacta 