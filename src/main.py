import cv2
import time
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.vision.hand_tracker import HandTracker
from src.vision.gesture_recognizer import GestureRecognizer
from src.audio.midi_engine import MidiEngine

def main():
    print("Iniciando a captura da WebCam Sintetizador de Acordes...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a WebCam (Index 0).")
        return

    tracker = HandTracker(max_hands=2)
    gestures = GestureRecognizer()
    midi_synth = MidiEngine()
    
    p_time = 0

    while True:
        # Estado musical nativo se nenhuma mão válida sobrepor
        current_frame_chord = "SILÊNCIO"
        
        success, img = cap.read()
        if not success:
            break
            
        img = cv2.flip(img, 1)
        # Resolução Câmera (Para usar na HUD)
        h_img, w_img, _ = img.shape
            
        # Extrai os esqueletos MediaPipe puro
        img_temp = tracker.find_hands(img, draw=False)  
        hands = tracker.find_position(img_temp, draw=False)
        
        # -----------------------------
        # UI NEON: Escurecer o feed da câmera e desenhar layout
        # -----------------------------
        overlay = np.zeros_like(img)
        # O Blend de escurecimento (0.3 significa câmera 30% brilhante. Sombra/Cinza escuro domina)
        img = cv2.addWeighted(img, 0.4, overlay, 0.6, 0.0)
        
        # Zonas localizadas APENAS na Metade Direita da tela
        top_h = int(h_img * 0.3)
        half_w = int(w_img / 2)
        q3_w = int(w_img * 0.75) # 75% da tela (Meio da área direita)
        
        # Linha vertical central separando as mãos (Esquerda Livre / Direita Acordes)
        cv2.line(img, (half_w, 0), (half_w, h_img), (255, 255, 255), 2)
        
        # Linhas de Acordes (Apenas na Direita)
        cv2.line(img, (half_w, top_h), (w_img, top_h), (100, 50, 50), 3) # Linha horizontal
        cv2.line(img, (q3_w, 0), (q3_w, top_h), (100, 50, 50), 3) # Linha vertical do topo direito
        
        # Nomes das Zonas Direitas (Acordes)
        cv2.putText(img, "LIVRE (FUTURO)", (20, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (100, 100, 100), 2)
        cv2.putText(img, "BEMOL", (half_w + 10, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 200, 255), 2)
        cv2.putText(img, "SUSTENIDO", (q3_w + 10, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 200, 255), 2)
        cv2.putText(img, "NATURAL (ACORDES)", (half_w + 20, top_h + 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 200, 255), 2)

        if len(hands) > 0:
            for i, hand in enumerate(hands):
                lm_list = hand["lm_list"]
                
                # Desenhamos só o wireframe Neon brilhante por cima
                for lm in lm_list:
                    cv2.circle(img, (lm[1], lm[2]), 4, (255, 0, 150), cv2.FILLED)
                
                # Reconexão Óssea simplificada
                # Você poderia redesenhar a mão se achasse chique, mas só os nós já dão o tom misterioso
                
                # Avalia a coordenada X principal da mão
                indicador_x = lm_list[8][1]
                
                # Se a mão estiver na Mão Esquerda (Livre), ignorar os disparos de notas
                if indicador_x < half_w:
                    cv2.putText(img, "Mao Esquerda - Preparando Mapeamento", (lm_list[0][1] - 50, lm_list[0][2] - 50), cv2.FONT_HERSHEY_PLAIN, 1.2, (100, 100, 100), 2)
                    continue

                # Usar a biblioteca Gestual para entender O QUE ESSA MÃO TÁ FAZENDO
                base_note, chord_type, f_up = gestures.analyze_hand_gesture(lm_list)
                
                # Encontra o "pontinho" (landmark) mais alto de toda a mão (Menor Y na tela)
                highest_lm = min(lm_list, key=lambda lm: lm[2])
                highest_x = highest_lm[1]
                highest_y = highest_lm[2]
                
                # Avalia Zona baseada em qualquer parte da mão que tocou o topo primeiro
                modifier = gestures.get_zone_modifier(highest_y, highest_x, h_img, w_img)
                
                texto_acorde = ""
                cor_acorde = (0, 255, 0)
                
                if base_note:
                    # Acorde formatado: [Nota][Sustenido/Bemol][Menor/Maior_Omitido]
                    # Ex: C#m / Eb / F
                    tipo_sufixo = "m" if chord_type == "Minor" else ""
                    texto_acorde = f"{base_note}{modifier}{tipo_sufixo}"
                    cor_acorde = (0, 255, 255) if chord_type == "Major" else (255, 120, 0)
                else:
                    texto_acorde = "SILÊNCIO"
                    cor_acorde = (50, 50, 50)
                
                # Título flutuante gigante no topo da detecção
                bbox = hand["bbox"]
                cx = bbox[0]
                cy = bbox[1] - 40
                if cy < 50: cy = bbox[3] + 50
                
                cv2.putText(img, texto_acorde, (cx, cy), cv2.FONT_HERSHEY_DUPLEX, 2.5, cor_acorde, 3)
                
                # Mostramos os dedos identificados esticados (Mini debug em volta da mão)
                dedo_status = "".join(["1" if x else "0" for x in f_up])
                cv2.putText(img, f"Code: {dedo_status}", (cx, cy + 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (200, 200, 200), 2)
                
                # Registra o acorde oficial da tela para enviar pro Áudio
                current_frame_chord = texto_acorde

        # Envia tudo ao Controlador C++ MIDI para tocar o som/mudar acorde no GarageBand
        midi_synth.update(current_frame_chord)

        # FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        cv2.putText(img, f'FPS: {int(fps)}', (10, 40), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 0, 255), 2)
                    
        cv2.imshow("Instrumento Inteligente - Sintetizador de Acordes VISUAL", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    midi_synth.close()

if __name__ == "__main__":
    main()
