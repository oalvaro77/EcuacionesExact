from ecuacion_exacta import analizar_ecuacion_exacta

# Lista de ecuaciones de prueba en diferentes formatos y órdenes
ecuaciones = [
    "(x-y+1)*dx-dy=0",
    "2*x*y*dx + x**2*dy = 0",
    "y**2*dx+2*x*y*dy=0",
    "(x**2+y)*dx + x*dy = 0",
    "x*dy + y*dx = 0",
    "-dy + (x-y+1)*dx = 0",
    "x*dy-y*dx=0"
]

for eq in ecuaciones:
    print(f"Probando: {eq}")
    try:
        resultado = analizar_ecuacion_exacta(eq)
        for k, v in resultado.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40) 