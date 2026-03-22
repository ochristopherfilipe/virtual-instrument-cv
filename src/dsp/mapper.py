import time
from collections import deque

def map_to_midi_note(y_norm, min_midi=48, max_midi=72):
    """
    Transforma a altura da mão em uma nota musical discreta.
    Mão no alto = Nota alta (Aguda)
    Mão embaixo = Nota baixa (Grave)
    """
    # 1. Definimos a "Área de Toque" útil (y costuma ir de 0 na testa até 1.0 na barriga)
    # Clamp da altura útil
    y_clamped = max(0.0, min(1.0, y_norm))
    
    # 2. Inverter para que o alto da tela (0.0) produza notas mais altas (ex: C5)
    inverted_y = 1.0 - y_clamped
    
    # 3. Discretizar os semitons logarítmicos
    total_notes = max_midi - min_midi
    note = min_midi + int(inverted_y * total_notes)
    
    # Evitar out-of-bounds exato do 1.0
    note = min(max_midi, max(min_midi, note))
    
    # 4. Encontrar a Nota de cordal natural
    notas_escala = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    nome = notas_escala[note % 12]
    oitava = (note // 12) - 1
    
    return note, f"{nome}{oitava}"


class HitDetector:
    """
    Implementação de Sliding Window que analisa os últimos frames
    para encontrar aceleração brusca seguida de parada (Movimento de Tocar/Ataque).
    """
    def __init__(self, window_size=5, debounce_time=0.4, trigger_vel=1.5):
        self.history = deque(maxlen=window_size)
        self.debounce_time = debounce_time
        
        # trigger_vel: velocidade Y mínima que consideramos um "Ataque rápido de Bateria/Piano"
        self.trigger_vel = trigger_vel 
        self.last_trigger_time = 0
        
    def check_hit(self, y_val, c_time):
        """
        Calcula a velocidade (Delta Y / Delta T) usando dados na Janela.
        Mão indo pra baixo com força = Y aumenta de forma espantosa positiva.
        """
        self.history.append((c_time, y_val))
        
        if len(self.history) < 2:
            return False
            
        old_time, old_val = self.history[0]
        dt = c_time - old_time
        
        if dt <= 0:
            return False
            
        # Velocidade ao longo da duração da janela
        velocity = (y_val - old_val) / dt
        
        # Teste de Gatilho e Debounce
        if velocity > self.trigger_vel:
            if c_time - self.last_trigger_time > self.debounce_time:
                self.last_trigger_time = c_time
                return True
                
        return False
