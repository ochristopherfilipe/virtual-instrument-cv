import math

def smoothing_factor(t_e, cutoff):
    """Calcula o alpha (fator de suavização) a partir da frequência de corte."""
    r = 2 * math.pi * cutoff * t_e
    return r / (r + 1)

def exponential_smoothing(a, x, x_prev):
    """Aplica o filtro Exponential Smoothing básico."""
    return a * x + (1 - a) * x_prev

class OneEuroFilter:
    """
    Filtro 1 Euro: Filtro passa-baixa adaptativo.
    A frequência de corte muda dinamicamente baseada na velocidade,
    tirando o tremor a baixas velocidades e removendo lag em altas.
    """
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        # min_cutoff: Filtro base (quanto menor, mais corta tremidos quando a mão está parada)
        # beta: Coeficiente de velocidade (quanto maior, menos lag quando move rápido)
        # d_cutoff: Frequência de corte fixa para a estabilização da derivada
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        
        self.x_prev = float(x0)
        self.dx_prev = float(dx0)
        self.t_prev = float(t0)

    def __call__(self, t, x):
        """
        Retorna o valor processado e filtrado no tempo 't'.
        """
        t_e = t - self.t_prev
        
        # Caso o ciclo seja instantâneo, retornamos a memória (previne div by 0)
        if t_e <= 0.0:
            return self.x_prev
            
        # 1. Filtro da derivada (estimativa contínua da velocidade)
        a_d = smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = exponential_smoothing(a_d, dx, self.dx_prev)
        
        # 2. Adaptação do corte passa-baixa baseado em o quão rápido a mão se move
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        # 3. Aplicar Filtro de fato aos dados reais de posição
        a = smoothing_factor(t_e, cutoff)
        x_hat = exponential_smoothing(a, x, self.x_prev)
        
        # 4. Gravar memória para a próxima iteração
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        
        return x_hat
