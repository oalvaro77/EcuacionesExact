"""
Resolución numérica de la ecuación diferencial:
    (cos(x)-sin(x)+sin(y))*dx + (cos(x)+sin(y)+cos(y))*dy = 0

1. Despeje para obtener la EDO explícita:
    (cos(x)+sin(y)+cos(y)) dy/dx = -(cos(x)-sin(x)+sin(y))
    dy/dx = - (cos(x)-sin(x)+sin(y)) / (cos(x)+sin(y)+cos(y))

2. Resolución numérica usando scipy.integrate.solve_ivp

3. Gráfica de la solución
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Definir la función f(x, y)
def f(x, y):
    return - (np.cos(x) - np.sin(x) + np.sin(y)) / (np.cos(x) + np.sin(y) + np.cos(y))

# Condición inicial (puedes cambiar y0)
x0 = 0
y0 = 0

# Intervalo de integración (ajusta según el dominio de interés)
x_span = (x0, 2*np.pi)
x_eval = np.linspace(x0, 2*np.pi, 200)

# Resolver la EDO
try:
    sol = solve_ivp(f, x_span, [y0], t_eval=x_eval, method='RK45')
    # Graficar la solución
    plt.plot(sol.t, sol.y[0], label='Solución numérica')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Solución numérica de la EDO trigonométrica')
    plt.legend()
    plt.grid()
    plt.show()
except Exception as e:
    print(f"Ocurrió un error durante la integración: {e}")

print("\nNotas:")
print("- Cambia y0 para probar diferentes condiciones iniciales.")
print("- Puedes adaptar este código para otras ecuaciones cambiando la función f(x, y).") 