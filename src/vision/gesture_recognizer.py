import math

class GestureRecognizer:
    def __init__(self):
        pass

    def analyze_hand_gesture(self, lm_list):
        """
        Recebe a lista de landmarks [id, x, y, z] e retorna:
        (Nota Base, Tipo do Acorde, Dicionário de estado dos dedos)
        Retorna (None, None, []) se a pose não bater com nenhum acorde.
        """
        if not lm_list or len(lm_list) < 21:
            return None, None, []
            
        wrist = lm_list[0]
        middle_mcp = lm_list[9]
        
        # 1. Orientação da Mão: Maior (Cima) ou Menor (Baixo)
        # O eixo Y cresce de cima pra baixo no pixel do monitor.
        # Se Pulso(Y) > Medio(Y), significa que o pulso está embaixo e os dedos pra cima (Maior)
        if wrist[2] > middle_mcp[2]:
            chord_type = "Major"  # Pra Cima
            is_up = True
        else:
            chord_type = "Minor"  # Pra Baixo
            is_up = False
            
        # 2. Detecção de Extensão dos Dedos
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
        fingers_up = []
        
        # --- Lógica do Polegar (Thumb) ---
        # Polegar se move no eixo X, mas de forma oposta na mão Direita/Esquerda.
        # Uma heurística excelente é medir a distância temporal entre a ponta do dedão e a base do mindinho.
        # Se a mão abrir, o dedão afasta bastante.
        dist_palm = math.hypot(wrist[1] - middle_mcp[1], wrist[2] - middle_mcp[2])
        dist_thumb = math.hypot(lm_list[4][1] - lm_list[17][1], lm_list[4][2] - lm_list[17][2])
        
        # O fator 1.2 foi flexibilizado para facilitar o reconhecimento da nota G (5 dedos).
        if dist_thumb > dist_palm * 1.2:
            fingers_up.append(True)
        else:
            fingers_up.append(False)
            
        # --- Lógica dos outros 4 dedos (Invariante a Rotação 2D) ---
        for tip, pip in zip(finger_tips, finger_pips):
            # A distância da ponta do dedo pro pulso
            dist_tip = math.hypot(lm_list[tip][1] - wrist[1], lm_list[tip][2] - wrist[2])
            # A distância da base do dedo pro pulso
            dist_pip = math.hypot(lm_list[pip][1] - wrist[1], lm_list[pip][2] - wrist[2])
            
            # Se a ponta do dedo estiver mais distante do pulso do que a junta, 
            # significa que o dedo está esticado, independente da mão estar virada pra cima, pra baixo ou de lado!
            if dist_tip > dist_pip * 0.95:
                fingers_up.append(True)
            else:
                fingers_up.append(False)

        # 3. Mapeamento para Notas/Acordes
        f = fingers_up
        base_note = None
        
        if f == [False, True, False, False, False]:
            base_note = "C"   # Só indicador
        elif f == [False, True, True, False, False]:
            base_note = "D"   # Indicador e Médio
        elif f == [False, True, True, True, False]:
            base_note = "E"   # Índex, Máx, Anelar
        elif f == [False, True, True, True, True]:
            base_note = "F"   # Índex ao Mínimo
        elif f == [True, True, True, True, True]:
            base_note = "G"   # 5 Dedos (Mão Aberta)
        elif f == [True, False, False, False, True]:
            base_note = "A"   # Hang Loose
        elif f == [False, False, False, False, True]:
            base_note = "B"   # Só Mínimo
            
        return base_note, chord_type, fingers_up

    def get_zone_modifier(self, pointer_y, pointer_x, max_screen_h, max_screen_w):
        """
        Retorna:
        - "" (Natural) se estiver na metade inferior da tela
        - "#" (Sustenido) se estiver na metade superior, lado direito
        - "b" (Bemol) se estiver na metade superior, lado esquerdo
        """
        top_h = max_screen_h * 0.3
        thq_w = max_screen_w * 0.75 # Meio da parte direita da tela
        
        # Metade de baixo (agora 70% da tela) é Natural
        if pointer_y >= top_h:
            return ""
            
        # O topo da Metade Direita é dividido
        if pointer_x > thq_w:
            return "#"
        else:
            return "b"
