import sympy as sp
from sympy import symbols, diff, Eq, solve, simplify, exp, integrate, log, cos, sin
import re

def analizar_ecuacion_exacta(ecuacion_str):
    """
    Analiza si una ecuación diferencial es exacta y encuentra factor integrante si no lo es.
    Formato esperado: M(x,y)*dx + N(x,y)*dy = 0
    """
    x, y = symbols('x y')
    
    # Preprocesar: quitar espacios y '=0'
    ecuacion_str = ecuacion_str.replace(' ', '').replace('=0', '')
    ecuacion_str = ecuacion_str.replace('sen(', 'sin(').replace('cos(', 'cos(')  # Normalizar funciones
    
    # Patrones mejorados para capturar diferentes formatos
    patrones = [
        r'^(.+?)\*dx([+-].+?)\*dy$',     # M*dx+N*dy o M*dx-N*dy
        r'^(.+?)\*dy([+-].+?)\*dx$',     # N*dy+M*dx o N*dy-M*dx
        r'^([+-]?)dx([+-].+?)\*dy$',     # ±dx+N*dy o ±dx-N*dy
        r'^([+-]?)dy([+-].+?)\*dx$',     # ±dy+M*dx o ±dy-M*dx
        r'^(.+?)\*dx([+-]?)dy$',         # M*dx±dy
        r'^(.+?)\*dy([+-]?)dx$',         # N*dy±dx
        r'^([+-]?)dx([+-]?)dy$',         # ±dx±dy
        r'^([+-]?)dy([+-]?)dx$',         # ±dy±dx
        r'^\((.+?)\)dx\((.+?)\)dy$',     # (M)*dx(N)*dy
        r'^\((.+?)\)dy\((.+?)\)dx$',     # (N)*dy(M)*dx
    ]
    
    match = None
    patron_usado = None
    
    for i, patron in enumerate(patrones):
        match = re.match(patron, ecuacion_str)
        if match:
            patron_usado = i
            break
    
    if not match:
        raise ValueError(f"Formato incorrecto: '{ecuacion_str}'\nUse formato: M(x,y)*dx + N(x,y)*dy = 0")
    
    # Extraer M y N según el patrón
    try:
        if patron_usado == 0:  # M*dx+N*dy
            M_str = match.group(1)
            N_str = match.group(2)
        elif patron_usado == 1:  # N*dy+M*dx
            N_str = match.group(1)
            M_str = match.group(2)
        elif patron_usado == 2:  # ±dx+N*dy
            signo = match.group(1) if match.group(1) else '+'
            M_str = '1' if signo == '+' else '-1'
            N_str = match.group(2)
        elif patron_usado == 3:  # ±dy+M*dx
            signo = match.group(1) if match.group(1) else '+'
            N_str = '1' if signo == '+' else '-1'
            M_str = match.group(2)
        elif patron_usado == 4:  # M*dx±dy
            M_str = match.group(1)
            signo = match.group(2) if match.group(2) else '+'
            N_str = '1' if signo == '+' else '-1'
        elif patron_usado == 5:  # N*dy±dx
            N_str = match.group(1)
            signo = match.group(2) if match.group(2) else '+'
            M_str = '1' if signo == '+' else '-1'
        elif patron_usado == 6:  # ±dx±dy
            signo1 = match.group(1) if match.group(1) else '+'
            signo2 = match.group(2) if match.group(2) else '+'
            M_str = '1' if signo1 == '+' else '-1'
            N_str = '1' if signo2 == '+' else '-1'
        elif patron_usado == 7:  # ±dy±dx
            signo1 = match.group(1) if match.group(1) else '+'
            signo2 = match.group(2) if match.group(2) else '+'
            N_str = '1' if signo1 == '+' else '-1'
            M_str = '1' if signo2 == '+' else '-1'
        elif patron_usado == 8:  # (M)*dx(N)*dy
            M_str = match.group(1)
            N_str = match.group(2)
        elif patron_usado == 9:  # (N)*dy(M)*dx
            N_str = match.group(1)
            M_str = match.group(2)
        
        # Limpiar strings y convertir a expresiones sympy
        M = sp.sympify(M_str.replace('*', '*').strip())
        N = sp.sympify(N_str.replace('*', '*').strip())
        
    except Exception as e:
        raise ValueError(f"Error al procesar M='{M_str}' o N='{N_str}': {e}")
    
    # Calcular derivadas parciales
    try:
        dM_dy = diff(M, y)
        dN_dx = diff(N, x)
    except Exception as e:
        raise ValueError(f"Error al calcular derivadas: {e}")
    
    # Verificar exactitud
    diferencia = simplify(dM_dy - dN_dx)
    es_exacta = diferencia == 0
    
    resultado = {
        'ecuacion_original': ecuacion_str,
        'M': M,
        'N': N,
        'dM_dy': dM_dy,
        'dN_dx': dN_dx,
        'diferencia': diferencia,
        'es_exacta': es_exacta
    }
    
    # Si no es exacta, buscar factor integrante
    if not es_exacta:
        factor = None
        caso_factor = None
        
        try:
            # CASO 1: Factor μ(x) - solo depende de x
            if N != 0:  # Evitar división por cero
                cociente_x = simplify((dM_dy - dN_dx) / N)
                print(f"Cociente para μ(x): (∂M/∂y - ∂N/∂x)/N = {cociente_x}")
                # Verificar si depende solo de x
                if cociente_x.free_symbols <= {x} and cociente_x != 0:
                    try:
                        integral_x = integrate(cociente_x, x)
                        factor = exp(integral_x)
                        caso_factor = 'μ(x)'
                        print(f"Factor μ(x) encontrado: {factor}")
                    except Exception:
                        pass
            
            # CASO 2: Factor μ(y) - solo depende de y
            if factor is None and M != 0:  # Evitar división por cero
                cociente_y = simplify((dN_dx - dM_dy) / M)
                print(f"Cociente para μ(y): (∂N/∂x - ∂M/∂y)/M = {cociente_y}")
                # Verificar si depende solo de y
                if cociente_y.free_symbols <= {y} and cociente_y != 0:
                    try:
                        integral_y = integrate(cociente_y, y)
                        factor = exp(integral_y)
                        caso_factor = 'μ(y)'
                        print(f"Factor μ(y) encontrado: {factor}")
                    except Exception:
                        pass
             # CASO 2B: Factor μ(y) mejorado - casos especiales
            if factor is None and M != 0:
                try:
                    # Analizar estructura específica para ecuaciones polinomiales
                    cociente_y = simplify((dN_dx - dM_dy) / M)
                    print(f"Cociente mejorado para μ(y): (∂N/∂x - ∂M/∂y)/M = {cociente_y}")
                    
                    # Casos especiales donde el cociente puede simplificarse
                    if cociente_y == -1/y:  # μ = 1/y
                        factor = 1/y
                        caso_factor = 'μ(y) = 1/y'
                        print(f"Factor μ(y) = 1/y encontrado")
                    elif cociente_y == -2/y:  # μ = 1/y²
                        factor = 1/(y**2)
                        caso_factor = 'μ(y) = 1/y²'
                        print(f"Factor μ(y) = 1/y² encontrado")
                    elif cociente_y == 1/y:  # μ = y
                        factor = y
                        caso_factor = 'μ(y) = y'
                        print(f"Factor μ(y) = y encontrado")
                except Exception as e:
                    print(f"Error en análisis mejorado μ(y): {e}")
            
            # CASO ESPECIAL: Factor μ(xy) - depende del producto xy
            if factor is None:
                # Para ecuaciones de la forma f(x,y)dx + g(x,y)dy = 0
                # donde el factor puede ser función de xy
                z = symbols('z')  # z = xy
                try:
                    # Sustituir xy por z y ver si se simplifica
                    M_z = M.subs(x*y, z)
                    N_z = N.subs(x*y, z)
                    
                    # Verificar si podemos expresar como función de z = xy
                    cociente_xy = simplify((dM_dy - dN_dx) / N)
                    print(f"Analizando factor μ(xy): cociente = {cociente_xy}")
                    
                    # Casos especiales conocidos
                    factores_especiales_xy = [
                         # Factores básicos
                    (x, 'μ = x'),
                    (y, 'μ = y'),
                    (x*y, 'μ = xy'),
                    (x**2, 'μ = x²'),
                    (y**2, 'μ = y²'),
                    (x**2 * y, 'μ = x²y'),
                    (x * y**2, 'μ = xy²'),
                    (x**2 * y**2, 'μ = x²y²'),
                    
                    # Factores racionales básicos
                    (1/x, 'μ = 1/x'),
                    (1/y, 'μ = 1/y'),
                    (1/(x*y), 'μ = 1/(xy)'),
                    (1/(x**2), 'μ = 1/x²'),
                    (1/(y**2), 'μ = 1/y²'),
                    (1/(x**2 * y), 'μ = 1/(x²y)'),
                    (1/(x * y**2), 'μ = 1/(xy²)'),
                    (1/(x**2 * y**2), 'μ = 1/(x²y²)'),
                    
                    # Factores para ecuaciones polinomiales específicas
                    (1/(y**3), 'μ = 1/y³'),
                    (1/(x**3), 'μ = 1/x³'),
                    (1/(x * y**3), 'μ = 1/(xy³)'),
                    (1/(x**3 * y), 'μ = 1/(x³y)'),
                    
                    # Combinaciones lineales
                    ((x + y), 'μ = x + y'),
                    ((x - y), 'μ = x - y'),
                    (1/(x + y), 'μ = 1/(x + y)'),
                    (1/(x - y), 'μ = 1/(x - y)'),
                    
                    # Factores exponenciales
                    (exp(x), 'μ = eˣ'),
                    (exp(y), 'μ = eʸ'),
                    (exp(x + y), 'μ = e^(x+y)'),
                    (exp(x - y), 'μ = e^(x-y)'),
                    ]
                    
                    for mu_test, nombre in factores_especiales_xy:
                        try:
                            M_test = simplify(M * mu_test)
                            N_test = simplify(N * mu_test)
                            dM_test_dy = diff(M_test, y)
                            dN_test_dx = diff(N_test, x)
                            
                            if simplify(dM_test_dy - dN_test_dx) == 0:
                                factor = mu_test
                                caso_factor = nombre
                                print(f"Factor especial encontrado: {nombre}")
                                break
                        except Exception:
                            continue
                            
                except Exception as e:
                    print(f"Error analizando μ(xy): {e}")
            
            # CASO ESPECIAL PARA ECUACIONES RACIONALES
            if factor is None:
                try:
                    # Para ecuaciones de la forma P(x,y)/Q(x,y) dx + R(x,y)/S(x,y) dy = 0
                    # El factor integrante puede ser una función racional
                    
                    # Analizar la estructura de M y N
                    print(f"Estructura de M: {M}, tipo: {type(M)}")
                    print(f"Estructura de N: {N}, tipo: {type(N)}")
                    
                    # Para el caso específico (1/x)dx - (1+xy²)dy = 0
                    # Probar factores racionales comunes
                    factores_racionales = [
                        (x, 'μ = x'),
                        (x**2, 'μ = x²'),
                        (1/(1 + x*y**2), 'μ = 1/(1+xy²)'),
                        (x/(1 + x*y**2), 'μ = x/(1+xy²)'),
                        ((1 + x*y**2)/x, 'μ = (1+xy²)/x'),
                    ]
                    
                    for mu_test, nombre in factores_racionales:
                        try:
                            M_test = simplify(M * mu_test)
                            N_test = simplify(N * mu_test)
                            dM_test_dy = diff(M_test, y)
                            dN_test_dx = diff(N_test, x)
                            
                            diferencia_test = simplify(dM_test_dy - dN_test_dx)
                            print(f"Probando {nombre}: diferencia = {diferencia_test}")
                            
                            if diferencia_test == 0:
                                factor = mu_test
                                caso_factor = nombre
                                print(f"Factor racional encontrado: {nombre}")
                                break
                        except Exception as e:
                            print(f"Error probando {nombre}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error buscando factores racionales: {e}")
            
            # CASO 3: Factores especiales comunes (ampliado)
            if factor is None:
                factores_especiales = [
                    (x, 'μ = x'),
                    (y, 'μ = y'),
                    (x*y, 'μ = xy'),
                    (x**2, 'μ = x²'),
                    (y**2, 'μ = y²'),
                    (x**2 * y, 'μ = x²y'),
                    (x * y**2, 'μ = xy²'),
                    (x**2 * y**2, 'μ = x²y²'),
                    (1/x, 'μ = 1/x'),
                    (1/y, 'μ = 1/y'),
                    (1/(x*y), 'μ = 1/(xy)'),
                    (1/(x**2), 'μ = 1/x²'),
                    (1/(y**2), 'μ = 1/y²'),
                    (1/(x**2 * y), 'μ = 1/(x²y)'),
                    (1/(x * y**2), 'μ = 1/(xy²)'),
                    ((x + y), 'μ = x + y'),
                    ((x - y), 'μ = x - y'),
                    (1/(x + y), 'μ = 1/(x + y)'),
                    (1/(x - y), 'μ = 1/(x - y)'),
                    (exp(x), 'μ = eˣ'),
                    (exp(y), 'μ = eʸ'),
                    (exp(x + y), 'μ = e^(x+y)'),
                    (exp(x - y), 'μ = e^(x-y)'),
                ]
                
                for mu_test, nombre in factores_especiales:
                    try:
                        M_test = simplify(M * mu_test)
                        N_test = simplify(N * mu_test)
                        dM_test_dy = diff(M_test, y)
                        dN_test_dx = diff(N_test, x)
                        
                        if simplify(dM_test_dy - dN_test_dx) == 0:
                            factor = mu_test
                            caso_factor = nombre
                            break
                    except Exception:
                        continue
            
            # CASO 4: Factor integrante de la forma μ = x^m * y^n (método sistemático mejorado)
            if factor is None:
                try:
                    # Intentar diferentes combinaciones de exponentes
                    for m_test in range(-3, 4):  # m de -3 a 3
                        for n_test in range(-3, 4):  # n de -3 a 3
                            if m_test == 0 and n_test == 0:
                                continue
                            
                            # Crear factor de prueba con manejo de casos especiales
                            if m_test < 0 or n_test < 0:
                                # Para factores con exponentes negativos, usar 1/(x^|m| * y^|n|)
                                if m_test < 0 and n_test < 0:
                                    mu_test = 1/((x**abs(m_test)) * (y**abs(n_test)))
                                elif m_test < 0:
                                    mu_test = (y**n_test)/((x**abs(m_test)))
                                else:  # n_test < 0
                                    mu_test = (x**m_test)/((y**abs(n_test)))
                            else:
                                mu_test = (x**m_test) * (y**n_test)
                            
                            try:
                                M_test = simplify(M * mu_test)
                                N_test = simplify(N * mu_test)
                                dM_test_dy = diff(M_test, y)
                                dN_test_dx = diff(N_test, x)
                                
                                if simplify(dM_test_dy - dN_test_dx) == 0:
                                    factor = mu_test
                                    caso_factor = f'μ = {mu_test}'
                                    print(f"Factor sistemático encontrado: {mu_test}")
                                    break
                            except Exception:
                                continue
                        
                        if factor is not None:
                            break
                            
                except Exception as e:
                    print(f"Error en búsqueda sistemática mejorada: {e}")
            
            # CASO 5: Verificar factores de la forma f(ax + by)
            if factor is None:
                try:
                    # Probar algunos factores especiales basados en combinaciones lineales
                    combinaciones = [
                        (x + y, 'μ = (x + y)'),
                        (x - y, 'μ = (x - y)'),
                        (x + 2*y, 'μ = (x + 2y)'),
                        (2*x + y, 'μ = (2x + y)'),
                        (x**2 + y**2, 'μ = (x² + y²)'),
                        (x**2 - y**2, 'μ = (x² - y²)'),
                    ]
                    
                    for combinacion, nombre in combinaciones:
                        try:
                            M_test = simplify(M * combinacion)
                            N_test = simplify(N * combinacion)
                            dM_test_dy = diff(M_test, y)
                            dN_test_dx = diff(N_test, x)
                            
                            if simplify(dM_test_dy - dN_test_dx) == 0:
                                factor = combinacion
                                caso_factor = nombre
                                break
                        except Exception:
                            continue
                            
                except Exception as e:
                    print(f"Error buscando factores de combinación lineal: {e}")
            
            # CASO 6: Análisis especial para ecuaciones racionales
            if factor is None:
                try:
                    factor_especial, caso_especial = analizar_caso_especial_racional(M, N, x, y)
                    if factor_especial is not None:
                        factor = factor_especial
                        caso_factor = caso_especial
                except Exception as e:
                    print(f"Error en análisis especial: {e}")
            
            # CASO 7: Usar método avanzado para factores complejos
            if factor is None:
                try:
                    factor_avanzado, caso_avanzado = buscar_factor_integrante_avanzado(M, N, x, y)
                    if factor_avanzado is not None:
                        factor = factor_avanzado
                        caso_factor = f"Avanzado: μ = {caso_avanzado}"
                except Exception as e:
                    print(f"Error en método avanzado: {e}")
            # CASO 8: Análisis específico para ecuaciones trigonométricas
            if factor is None:
                try:
                    # Detectar si hay funciones trigonométricas
                    if any(func in str(M) + str(N) for func in ['sin', 'cos', 'tan']):
                        factor_trig, caso_trig = analizar_ecuacion_trigonometrica(M, N, x, y)
                        if factor_trig is not None:
                            factor = factor_trig
                            caso_factor = f"Trigonométrico: {caso_trig}"
                except Exception as e:
                    print(f"Error en análisis trigonométrico: {e}")
            # CASO 9: Análisis específico para ecuaciones polinomiales
            if factor is None:
                try:
                    # Detectar si tenemos ecuaciones polinomiales complejas
                    factor_poli, caso_poli = analizar_ecuacion_polinomial(M, N, x, y)
                    if factor_poli is not None:
                        factor = factor_poli
                        caso_factor = f"Polinomial: {caso_poli}"
                except Exception as e:
                    print(f"Error en análisis polinomial: {e}")
        
        except Exception as e:
            print(f"Error buscando factor integrante: {e}")
        
        # Verificar ecuación transformada
        if factor is not None:
            try:
                M_nuevo = simplify(M * factor)
                N_nuevo = simplify(N * factor)
                dM_nuevo_dy = diff(M_nuevo, y)
                dN_nuevo_dx = diff(N_nuevo, x)
                es_exacta_nueva = simplify(dM_nuevo_dy - dN_nuevo_dx) == 0
                
                resultado.update({
                    'factor_integrante': factor,
                    'caso_factor': caso_factor,
                    'M_nuevo': M_nuevo,
                    'N_nuevo': N_nuevo,
                    'dM_nuevo_dy': dM_nuevo_dy,
                    'dN_nuevo_dx': dN_nuevo_dx,
                    'diferencia_nueva': simplify(dM_nuevo_dy - dN_nuevo_dx),
                    'es_exacta_nueva': es_exacta_nueva
                })
            except Exception as e:
                print(f"Error verificando ecuación transformada: {e}")
        else:
            resultado.update({
                'factor_integrante': None,
                'caso_factor': 'No encontrado con métodos básicos'
            })
    
    return resultado

def obtener_edo_explicita(ecuacion_str):
    """
    Convierte M*dx + N*dy = 0 a dy/dx = -M/N
    """
    try:
        resultado = analizar_ecuacion_exacta(ecuacion_str)
        M = resultado['M']
        N = resultado['N']
        
        if N == 0:
            return "dy/dx = ∞ (ecuación no puede expresarse en forma explícita)"
        
        return f"dy/dx = -({M})/({N})"
    
    except Exception as e:
        return f"Error: {e}"

def analizar_caso_especial_racional(M, N, x, y):
    """
    Analiza casos especiales para ecuaciones con términos racionales
    como (1/x)dx - (1+xy²)dy = 0
    """
    dM_dy = diff(M, y)
    dN_dx = diff(N, x)
    
    print(f"\n=== ANÁLISIS ESPECIAL PARA ECUACIÓN RACIONAL ===")
    print(f"M = {M}")
    print(f"N = {N}")
    print(f"∂M/∂y - ∂N/∂x = {simplify(dM_dy - dN_dx)}")
    
    # Caso específico: (1/x)dx - (1+xy²)dy = 0
    if str(M) == '1/x' and str(N) == '-(1 + x*y**2)':
        print("Detectado caso específico: (1/x)dx - (1+xy²)dy = 0")
        
        # Para esta ecuación, el factor integrante es μ = x
        factor_test = x
        M_test = simplify(M * factor_test)  # (1/x) * x = 1
        N_test = simplify(N * factor_test)  # -(1+xy²) * x = -x(1+xy²)
        
        print(f"Probando μ = x:")
        print(f"M₁ = M·μ = {M_test}")
        print(f"N₁ = N·μ = {N_test}")
        
        dM_test_dy = diff(M_test, y)
        dN_test_dx = diff(N_test, x)
        
        print(f"∂M₁/∂y = {dM_test_dy}")
        print(f"∂N₁/∂x = {dN_test_dx}")
        print(f"∂M₁/∂y - ∂N₁/∂x = {simplify(dM_test_dy - dN_test_dx)}")
        
        if simplify(dM_test_dy - dN_test_dx) == 0:
            return factor_test, "μ = x (caso racional específico)"
    
    # Método general para ecuaciones racionales
    # Probar factores que eliminen singularidades
    
    # Si M tiene términos 1/x, probar μ = x^n
    if '1/x' in str(M):
        for n in range(1, 4):
            factor_test = x**n
            try:
                M_test = simplify(M * factor_test)
                N_test = simplify(N * factor_test)
                dM_test_dy = diff(M_test, y)
                dN_test_dx = diff(N_test, x)
                
                if simplify(dM_test_dy - dN_test_dx) == 0:
                    return factor_test, f"μ = x^{n} (eliminando singularidad)"
            except Exception:
                continue
    
    # Si N tiene términos 1/y, probar μ = y^n
    if '1/y' in str(N):
        for n in range(1, 4):
            factor_test = y**n
            try:
                M_test = simplify(M * factor_test)
                N_test = simplify(N * factor_test)
                dM_test_dy = diff(M_test, y)
                dN_test_dx = diff(N_test, x)
                
                if simplify(dM_test_dy - dN_test_dx) == 0:
                    return factor_test, f"μ = y^{n} (eliminando singularidad)"
            except Exception:
                continue
    
    return None, None

def buscar_factor_integrante_avanzado(M, N, x, y):
    """
    Busca factores integrantes más complejos usando métodos especializados
    """
    dM_dy = diff(M, y)
    dN_dx = diff(N, x)
    
    # Método 1: Factor de la forma μ = x^a * y^b
    try:
        diferencia = dM_dy - dN_dx
        
        # Para μ = x^a * y^b, la condición es:
        # ∂M/∂y - ∂N/∂x = a*N/x - b*M/y
        
        # Intentar resolver para diferentes valores de a y b
        for a in range(-2, 3):
            for b in range(-2, 3):
                if a == 0 and b == 0:
                    continue
                
                try:
                    # Verificar si la ecuación se satisface
                    lado_derecho = a*N/x - b*M/y if x != 0 and y != 0 else 0
                    
                    if simplify(diferencia - lado_derecho) == 0:
                        mu = x**a * y**b
                        return mu, f"x^{a} * y^{b}"
                        
                except (ZeroDivisionError, Exception):
                    continue
    
    except Exception:
        pass
    
    # Método 2: Factor que hace la ecuación homogénea
    try:
        # Si M y N son homogéneas del mismo grado, buscar factor
        grado_M = obtener_grado_homogeneo(M, x, y)
        grado_N = obtener_grado_homogeneo(N, x, y)
        
        if grado_M is not None and grado_N is not None:
            if grado_M == grado_N:
                # Probar μ = 1/(x^n * y^m) para hacer exacta
                for n in range(0, grado_M + 2):
                    for m in range(0, grado_M + 2):
                        try:
                            mu = 1/(x**n * y**m) if n > 0 or m > 0 else 1
                            M_test = simplify(M * mu)
                            N_test = simplify(N * mu)
                            
                            dM_test_dy = diff(M_test, y)
                            dN_test_dx = diff(N_test, x)
                            
                            if simplify(dM_test_dy - dN_test_dx) == 0:
                                return mu, f"1/(x^{n} * y^{m})"
                                
                        except Exception:
                            continue
    
    except Exception:
        pass
    
    # Método 3: Factores trigonométricos
    try:
        # Probar factores que involucran funciones trigonométricas
        factores_trig = [
            (exp(sin(x)), 'μ = e^(sin(x))'),
            (exp(cos(x)), 'μ = e^(cos(x))'),
            (exp(sin(y)), 'μ = e^(sin(y))'),
            (exp(cos(y)), 'μ = e^(cos(y))'),
            (exp(sin(x) + cos(y)), 'μ = e^(sin(x) + cos(y))'),
            (exp(cos(x) + sin(y)), 'μ = e^(cos(x) + sin(y))'),
            # Factores específicos para ecuaciones trigonométricas
            (exp(sin(x) + sin(y)), 'μ = e^(sin(x) + sin(y))'),
            (exp(cos(x) + cos(y)), 'μ = e^(cos(x) + cos(y))'),
            (exp(sin(x) - cos(x)), 'μ = e^(sin(x) - cos(x))'),
            (exp(cos(x) - sin(x)), 'μ = e^(cos(x) - sin(x))'),
        ]
        
        for mu_test, nombre in factores_trig:
            try:
                M_test = simplify(M * mu_test)
                N_test = simplify(N * mu_test)
                dM_test_dy = diff(M_test, y)
                dN_test_dx = diff(N_test, x)
                
                if simplify(dM_test_dy - dN_test_dx) == 0:
                    return mu_test, nombre
            except Exception:
                continue
    
    except Exception:
        pass
    
    return None, None
def analizar_ecuacion_trigonometrica(M, N, x, y):
    """
    Método especializado para ecuaciones con funciones trigonométricas
    """
    try:
        # Para ecuaciones de la forma con sen y cos, a menudo el factor es exponencial
        # Probar factores de la forma e^(combinación trigonométrica)
        
        # Analizar la estructura de M y N
        print(f"Analizando ecuación trigonométrica:")
        print(f"M = {M}")
        print(f"N = {N}")
        
        # Factores comunes para ecuaciones con sen/cos
        factores_especiales = [
            exp(sin(x)), exp(cos(x)), exp(sin(y)), exp(cos(y)),
            exp(sin(x) + sin(y)), exp(cos(x) + cos(y)),
            exp(sin(x) + cos(y)), exp(cos(x) + sin(y)),
            exp(sin(x) - cos(x)), exp(cos(x) - sin(x)),
            exp(sin(y) - cos(y)), exp(cos(y) - sin(y)),
            # Factores racionales
            1/(cos(x)), 1/(sin(x)), 1/(cos(y)), 1/(sin(y)),
        ]
        
        for factor_test in factores_especiales:
            try:
                M_test = simplify(M * factor_test)
                N_test = simplify(N * factor_test)
                dM_test_dy = diff(M_test, y)
                dN_test_dx = diff(N_test, x)
                
                if simplify(dM_test_dy - dN_test_dx) == 0:
                    return factor_test, f"μ = {factor_test}"
            except Exception:
                continue
                
        return None, None
        
    except Exception as e:
        print(f"Error en análisis trigonométrico: {e}")
        return None, None
    
def analizar_ecuacion_polinomial(M, N, x, y):
    """
    Método especializado para ecuaciones polinomiales complejas
    """
    try:
        print(f"\n=== ANÁLISIS POLINOMIAL ESPECIALIZADO ===")
        print(f"M = {M}")
        print(f"N = {N}")
        
        dM_dy = diff(M, y)
        dN_dx = diff(N, x)
        diferencia = simplify(dM_dy - dN_dx)
        
        print(f"∂M/∂y = {dM_dy}")
        print(f"∂N/∂x = {dN_dx}")
        print(f"∂M/∂y - ∂N/∂x = {diferencia}")
        
        # Método 1: Analizar grados de los polinomios
        try:
            # Para M = x*y² + x²*y² + 3, N = x*y³
            # El cociente (∂N/∂x - ∂M/∂y)/M nos da información del factor
            
            if M != 0:
                cociente = simplify((dN_dx - dM_dy) / M)
                print(f"Cociente (∂N/∂x - ∂M/∂y)/M = {cociente}")
                
                # Buscar patrones específicos
                if cociente == -1/y:
                    return 1/y, "μ = 1/y (polinomial)"
                elif cociente == -2/y:
                    return 1/(y**2), "μ = 1/y² (polinomial)"
                elif cociente == -3/y:
                    return 1/(y**3), "μ = 1/y³ (polinomial)"
                    
            if N != 0:
                cociente = simplify((dM_dy - dN_dx) / N)
                print(f"Cociente (∂M/∂y - ∂N/∂x)/N = {cociente}")
                
                # Buscar patrones específicos
                if cociente == 1/x:
                    return x, "μ = x (polinomial)"
                elif cociente == 2/x:
                    return x**2, "μ = x² (polinomial)"
                elif cociente == -1/x:
                    return 1/x, "μ = 1/x (polinomial)"
                    
        except Exception as e:
            print(f"Error en análisis de cocientes: {e}")
        
        # Método 2: Factores específicos para ecuaciones de la forma ax^m*y^n + bx^p*y^q + c
        factores_polinomial = [
            (1/y, 'μ = 1/y'),
            (1/(y**2), 'μ = 1/y²'),
            (1/(y**3), 'μ = 1/y³'),
            (1/x, 'μ = 1/x'),
            (1/(x**2), 'μ = 1/x²'),
            (1/(x*y), 'μ = 1/(xy)'),
            (1/(x*y**2), 'μ = 1/(xy²)'),
            (1/(x**2*y), 'μ = 1/(x²y)'),
            (x/y, 'μ = x/y'),
            (y/x, 'μ = y/x'),
            (x/(y**2), 'μ = x/y²'),
            (y/(x**2), 'μ = y/x²'),
        ]
        
        for factor_test, nombre in factores_polinomial:
            try:
                M_test = simplify(M * factor_test)
                N_test = simplify(N * factor_test)
                dM_test_dy = diff(M_test, y)
                dN_test_dx = diff(N_test, x)
                
                diferencia_test = simplify(dM_test_dy - dN_test_dx)
                print(f"Probando {nombre}: diferencia = {diferencia_test}")
                
                if diferencia_test == 0:
                    return factor_test, f"{nombre} (método polinomial)"
            except Exception as e:
                print(f"Error probando {nombre}: {e}")
                continue
        
        return None, None
        
    except Exception as e:
        print(f"Error en análisis polinomial: {e}")
        return None, None

def obtener_grado_homogeneo(expr, x, y):
    """
    Obtiene el grado de homogeneidad de una expresión
    """
    try:
        # Sustituir x -> t*x, y -> t*y y ver si sale t^n * expr
        t = symbols('t')
        expr_escalada = expr.subs([(x, t*x), (y, t*y)])
        
        for grado in range(0, 5):
            if simplify(expr_escalada - t**grado * expr) == 0:
                return grado
        
        return None
    except Exception:
        return None

def mostrar_resultado(ecuacion_str):
    """
    Función auxiliar para mostrar resultados de forma ordenada
    """
    try:
        resultado = analizar_ecuacion_exacta(ecuacion_str)
        
        print(f"\n=== ANÁLISIS DE: {ecuacion_str} ===")
        print(f"M(x,y) = {resultado['M']}")
        print(f"N(x,y) = {resultado['N']}")
        print(f"∂M/∂y = {resultado['dM_dy']}")
        print(f"∂N/∂x = {resultado['dN_dx']}")
        print(f"∂M/∂y - ∂N/∂x = {resultado['diferencia']}")
        
        if resultado['es_exacta']:
            print("✅ LA ECUACIÓN ES EXACTA")
        else:
            print("❌ LA ECUACIÓN NO ES EXACTA")
            
            if 'factor_integrante' in resultado and resultado['factor_integrante'] is not None:
                print(f"\n🔧 FACTOR INTEGRANTE ENCONTRADO:")
                print(f"Tipo: {resultado['caso_factor']}")
                print(f"μ = {resultado['factor_integrante']}")
                print(f"\nECUACIÓN TRANSFORMADA:")
                print(f"M₁(x,y) = {resultado['M_nuevo']}")
                print(f"N₁(x,y) = {resultado['N_nuevo']}")
                print(f"Es exacta: {'✅ SÍ' if resultado['es_exacta_nueva'] else '❌ NO'}")
            else:
                print(f"⚠️  Factor integrante: {resultado['caso_factor']}")
        
        print(f"\nForma explícita: {obtener_edo_explicita(ecuacion_str)}")
        
    except Exception as e:
        print(f"Error: {e}")

# Ejemplos de uso y pruebas
if __name__ == "__main__":
    # Casos de prueba actualizados
    casos_prueba = [
        "(x-y+1)*dx-dy",
        "(1/x)*dx-(1+x*y^2)*dy", 
        "(2*x*y+3)*dx+x^2*dy",
        "(4*x*y^2 + 3*y)*dx + (3*x^2*y + 2*x)*dy",  # Nuevo caso
        "y*dx-x*dy",
        "(x^2 + y^2)*dx + 2*x*y*dy",  # Otro caso interesante
        "dx+dy",
        "(cos(x)-sen(x)+sen(y))*dx+(cos(x)+sen(y)+cos(y))*dy",
         "(x*y^2+x^2*y^2+3)*dx + (x*y^3)*dy",
    ]
    
    for caso in casos_prueba:
        mostrar_resultado(caso)
        print("-" * 50)