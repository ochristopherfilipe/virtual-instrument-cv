import cv2
import mediapipe as mp
import math

class HandTracker:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        """
        Inicializa o rastreador de mãos usando MediaPipe.
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode, 
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con, 
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def find_hands(self, img, draw=True):
        """
        Encontra as mãos na imagem e opcionalmente desenha os marcos e conexões.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img
        
    def find_position(self, img, draw=True):
        """
        Retorna uma lista de dicionários contendo os dados de cada mão detectada.
        As chaves são:
        - lm_list: Coordenadas em pixels reais [id, x, y, z]
        - norm_list: Coordenadas normalizadas em relação à base da mão
        - bbox: Bounding Box
        - scale: Escala do tamanho da mão (Pulso até base do dedo médio)
        """
        all_hands = []
        if self.results.multi_hand_landmarks:
            for my_hand in self.results.multi_hand_landmarks:
                my_lm_list = []
                x_list = []
                y_list = []
                
                h, w, c = img.shape
                # Coleta as coordenadas brutas na proporção da tela
                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    my_lm_list.append([id, cx, cy, lm.z])
                    x_list.append(cx)
                    y_list.append(cy)
                    
                    if draw:
                        # Destaca as pontas dos dedos e a base da palma
                        if id in [0, 4, 8, 12, 16, 20]:
                            cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
                
                # Extraindo o bounding box
                xmin, xmax = min(x_list), max(x_list)
                ymin, ymax = min(y_list), max(y_list)
                
                # Normalização de Escala (Independente da profundidade)
                # Medimos a distância de id 0 (pulso) a id 9 (nó do dedo médio)
                wrist = my_lm_list[0]
                mcp_mid = my_lm_list[9]
                scale = math.hypot(mcp_mid[1] - wrist[1], mcp_mid[2] - wrist[2])
                
                if scale == 0: 
                    scale = 0.001 # Evita divisão por zero
                    
                # Normalização Espacial e Invariante de Translação
                norm_list = []
                for lm in my_lm_list:
                    # Centralizamos o eixo x e y ao pulso, e dividimos pela escala
                    nx = (lm[1] - wrist[1]) / scale
                    ny = (lm[2] - wrist[2]) / scale
                    norm_list.append([lm[0], nx, ny, lm[3]])
                
                all_hands.append({
                    "lm_list": my_lm_list,
                    "norm_list": norm_list,
                    "bbox": (xmin, ymin, xmax, ymax),
                    "scale": scale
                })
                
                if draw:
                    cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)
                    
        return all_hands
