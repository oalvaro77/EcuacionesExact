import tkinter as tk
from tkinter import ttk, messagebox
from ecuacion_exacta import analizar_ecuacion_exacta, obtener_edo_explicita
import sympy as sp
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

class EcuacionExactaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Ecuaciones Diferenciales Exactas")
        self.root.geometry("800x600")
        
        # Crear y configurar el estilo
        style = ttk.Style()
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5)
        style.configure("TEntry", padding=5)
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Instrucciones
        instrucciones = "Ingrese la ecuación en formato: M(x,y)dx + N(x,y)dy = 0\nEjemplo: (x-y+1)*dx - dy = 0"
        ttk.Label(main_frame, text=instrucciones, wraplength=600).grid(row=0, column=0, sticky=tk.W)
        
        # Entrada de la ecuación
        ttk.Label(main_frame, text="Ecuación diferencial:").grid(row=1, column=0, sticky=tk.W)
        self.ecuacion_entry = ttk.Entry(main_frame, width=50)
        self.ecuacion_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Frame para botones de ejemplo
        ejemplos_frame = ttk.LabelFrame(main_frame, text="Ejemplos", padding="5")
        ejemplos_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Botones de ejemplo
        ejemplos = [
            ("(x-y+1)*dx-dy=0", "Ejercicio 1"),
            ("(x*y^3+1)*dx+x^2*y^2*dy=0", "Ejercicio 2"),
            ("-y*dx+(x+y^2-1)*dy=0", "Ejercicio 3"),
            ("y*dx+(x-x^2*y)*dy=0", "Ejercicio 4"),
            ("x^2*y^2*dx+(x^3*y+y+3)*dy=0", "Ejercicio 5"),
            ("x^2*dx-(x^3*y^2+3*y^2)*dy=0", "Ejercicio 6"),
            ("(x^2+y^2)*dx+2*x*y*dy=0", "Ejercicio 7"),
            ("(3*x^2*y^2+2*x*y)*dx+(2*x^3*y+x^2)*dy=0", "Ejercicio 8"),
            ("(x^2+2*x+y)*dx+(1-x^2-y)*dy=0", "Ejercicio 9"),
            ("(cos(x)-sen(x)+sen(y))*dx+(cos(x)+sen(y)+cos(y))*dy=0", "Ejercicio 10")
        ]
        
        for i, (ecuacion, descripcion) in enumerate(ejemplos):
            ttk.Button(ejemplos_frame, 
                      text=descripcion,
                      command=lambda e=ecuacion: self.cargar_ejemplo(e)).grid(
                          row=i//2, column=i%2, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        # Botón de análisis
        ttk.Button(main_frame, text="Analizar", command=self.analizar_ecuacion).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Frame para resultados
        self.resultados_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        self.resultados_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Área de texto para resultados
        self.resultados_text = tk.Text(self.resultados_frame, height=20, width=70, wrap=tk.WORD)
        self.resultados_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para el área de texto
        scrollbar = ttk.Scrollbar(self.resultados_frame, orient=tk.VERTICAL, command=self.resultados_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.resultados_text['yscrollcommand'] = scrollbar.set
        
    def cargar_ejemplo(self, ecuacion):
        self.ecuacion_entry.delete(0, tk.END)
        self.ecuacion_entry.insert(0, ecuacion)
        self.analizar_ecuacion()
        
    def analizar_ecuacion(self):
        ecuacion_str = self.ecuacion_entry.get()
        try:
            # Permitir ^ como potencia
            ecuacion_str = ecuacion_str.replace('^', '**')
            resultado = analizar_ecuacion_exacta(ecuacion_str)
            self.mostrar_resultados(resultado)
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar la ecuación: {str(e)}\n\nAsegúrese de usar el formato correcto:\nM(x,y)*dx + N(x,y)*dy = 0")
    
    def mostrar_resultados(self, resultado):
        self.resultados_text.delete(1.0, tk.END)
        
        def formatear(expr):
            return str(expr).replace('**', '^')
        
        # Mostrar si es exacta
        self.resultados_text.insert(tk.END, f"¿Es exacta?: {'Sí' if resultado['es_exacta'] else 'No'}\n\n")
        
        # Mostrar M y N
        self.resultados_text.insert(tk.END, f"M = {formatear(resultado['M'])}\n")
        self.resultados_text.insert(tk.END, f"N = {formatear(resultado['N'])}\n\n")
        
        # Mostrar derivadas parciales
        self.resultados_text.insert(tk.END, f"∂M/∂y = {formatear(resultado['dM_dy'])}\n")
        self.resultados_text.insert(tk.END, f"∂N/∂x = {formatear(resultado['dN_dx'])}\n\n")
        
        if not resultado['es_exacta']:
            self.resultados_text.insert(tk.END, "La ecuación no es exacta. Calculando factor integrante...\n\n")
            if resultado.get('factor_integrante') is not None:
                caso = resultado.get('caso_factor')
                if caso == 'x':
                    self.resultados_text.insert(tk.END, "Caso 1: Factor integrante función de x\n")
                elif caso == 'y':
                    self.resultados_text.insert(tk.END, "Caso 2: Factor integrante función de y\n")
                elif caso == 'xy':
                    m = resultado.get('m')
                    n = resultado.get('n')
                    self.resultados_text.insert(tk.END, f"Caso 3: Factor integrante de la forma x^m y^n con m = {m}, n = {n}\n")
                self.resultados_text.insert(tk.END, f"Factor integrante: {formatear(resultado['factor_integrante'])}\n\n")
            else:
                self.resultados_text.insert(tk.END, "No se encontró un factor integrante elemental de los casos 1, 2 o 3.\n\n")
                self.resultados_text.insert(tk.END, "Sugerencias:\n")
                self.resultados_text.insert(tk.END, "- Intente una sustitución de variables para simplificar la ecuación.\n")
                self.resultados_text.insert(tk.END, "- Consulte literatura especializada para factores integrantes más generales.\n")
                self.resultados_text.insert(tk.END, "- Considere resolver la ecuación numéricamente si solo necesita una solución aproximada.\n\n")
                # Agregar botón para resolución numérica
                btn_num = tk.Button(self.resultados_frame, text="Resolver numéricamente", command=self.resolver_numericamente)
                btn_num.grid(row=1, column=0, pady=5, sticky=tk.W)
            
            self.resultados_text.insert(tk.END, "Nueva ecuación después de multiplicar por el factor integrante:\n")
            self.resultados_text.insert(tk.END, f"M' = {formatear(resultado['M_nuevo'])}\n")
            self.resultados_text.insert(tk.END, f"N' = {formatear(resultado['N_nuevo'])}\n\n")
            
            self.resultados_text.insert(tk.END, "Nuevas derivadas parciales:\n")
            self.resultados_text.insert(tk.END, f"∂M'/∂y = {formatear(resultado['dM_nuevo_dy'])}\n")
            self.resultados_text.insert(tk.END, f"∂N'/∂x = {formatear(resultado['dN_nuevo_dx'])}\n\n")
            
            self.resultados_text.insert(tk.END, f"¿La nueva ecuación es exacta?: {'Sí' if resultado['es_exacta_nueva'] else 'No'}\n")

    def resolver_numericamente(self):
        # Pedir condición inicial y dominio
        top = tk.Toplevel(self.root)
        top.title("Resolución numérica")
        tk.Label(top, text="Condición inicial x0:").grid(row=0, column=0)
        x0_entry = tk.Entry(top)
        x0_entry.grid(row=0, column=1)
        tk.Label(top, text="Condición inicial y0:").grid(row=1, column=0)
        y0_entry = tk.Entry(top)
        y0_entry.grid(row=1, column=1)
        tk.Label(top, text="x final:").grid(row=2, column=0)
        xf_entry = tk.Entry(top)
        xf_entry.grid(row=2, column=1)
        def ejecutar():
            try:
                x0 = float(x0_entry.get())
                y0 = float(y0_entry.get())
                xf = float(xf_entry.get())
                ecuacion_str = self.ecuacion_entry.get().replace('^', '**')
                edo_str = obtener_edo_explicita(ecuacion_str)
                # Crear función f(x, y) usando eval de forma segura
                def f(x, y):
                    return eval(edo_str, {"x": x, "y": y, "sin": np.sin, "cos": np.cos, "exp": np.exp, "log": np.log, "sqrt": np.sqrt})
                x_span = (x0, xf)
                x_eval = np.linspace(x0, xf, 200)
                sol = solve_ivp(f, x_span, [y0], t_eval=x_eval, method='RK45')
                plt.plot(sol.t, sol.y[0], label='Solución numérica')
                plt.xlabel('x')
                plt.ylabel('y')
                plt.title('Solución numérica de la EDO')
                plt.legend()
                plt.grid()
                plt.show()
            except Exception as e:
                messagebox.showerror("Error", f"Error en la resolución numérica: {e}")
        tk.Button(top, text="Graficar", command=ejecutar).grid(row=3, column=0, columnspan=2, pady=10)

def main():
    root = tk.Tk()
    app = EcuacionExactaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 