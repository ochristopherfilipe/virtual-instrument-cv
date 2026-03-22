import cv2
import time
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.vision.hand_tracker import HandTracker
from src.vision.gesture_recognizer import GestureRecognizer
from src.audio.midi_engine import MidiEngine, Arpeggiator

def main():
    print("Iniciando a captura da WebCam Sintetizador de Acordes...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a WebCam (Index 0).")
        return

    tracker = HandTracker(max_hands=2)
    gestures = GestureRecognizer()
    midi_synth = MidiEngine()
    arpeggiator = Arpeggiator(bpm=136) # BPM Estiloso para Eletrônica
    
    p_time = 0
    smooth_pinch_y = -1
    show_help = False
    help_cooldown = 0

    while True:
        if help_cooldown > 0: help_cooldown -= 1
        # Estado musical nativo se nenhuma mão válida sobrepor
        current_frame_chord = "SILÊNCIO"
        current_frame_arp = "OFF"
        
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
        
        # Nomes das Zonas Direitas (Acordes) e Esquerda (Volume/Controles)
        cv2.putText(img, "VOLUME(Pinca) BPM(Like) LEN(Arma)", (10, 40), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
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
                
                # Area da Esquerda (Controles de Volume/CC)
                if indicador_x < half_w:
                    _, _, f_up_left = gestures.analyze_hand_gesture(lm_list)
                    soma_dedos = sum(f_up_left)

                    # --- SLIDER 1: PINÇA (Volume Master) ---
                    if gestures.is_pinching(lm_list):
                        x_pos = lm_list[8][1]
                        y_pos = lm_list[8][2]
                        
                        # Verifica Clique no botão de Ajuda
                        if 10 < x_pos < 180 and 60 < y_pos < 100:
                            if help_cooldown == 0:
                                show_help = not show_help
                                help_cooldown = 15 # debounce
                            cv2.putText(img, "CLIQUE!", (200, 85), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)
                            continue
                        # Invertido: Topo da tela (0) = Máximo (127), Base (h_img) = Mudo (0)
                        y_norm = max(0.0, min(1.0, y_pos / h_img))
                        vol_val = int((1.0 - y_norm) * 127)
                        midi_synth.set_volume(vol_val)
                        
                        # UI Fader Volume
                        pct = int(y_norm * h_img)
                        vol_pct = int((vol_val / 127.0) * 100)
                        cv2.rectangle(img, (20, pct), (50, h_img), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, f"VOLUME {vol_pct}%", (70, pct + 5), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 0), 2)
                        
                    # --- SLIDER 2: LIKE/JOINHA (BPM / Velocidade Arpejo) ---
                    elif f_up_left == [True, False, False, False, False]:
                        y_pos = lm_list[4][2] # Pegamos o polegar
                        y_norm = max(0.0, min(1.0, y_pos / h_img))
                        bpm_val = int((1.0 - y_norm) * 180) + 60 # 60 a 240 BPM
                        arpeggiator.set_bpm(bpm_val)
                        
                        # UI Fader BPM
                        pct = int(y_norm * h_img)
                        cv2.rectangle(img, (20, pct), (50, h_img), (255, 255, 0), cv2.FILLED)
                        cv2.putText(img, f"BPM: {bpm_val}", (70, pct + 5), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 0), 2)

                    # --- SLIDER 3: ARMINHA / L-SHAPE (Range/Comprimento Arpejo) ---
                    elif f_up_left == [True, True, False, False, False]:
                        y_pos = lm_list[8][2]
                        if smooth_pinch_y == -1: smooth_pinch_y = y_pos
                        smooth_pinch_y = 0.9 * smooth_pinch_y + 0.1 * y_pos # Filtro Inercial
                        
                        y_norm = max(0.0, min(1.0, smooth_pinch_y / h_img))
                        arp_len = int((1.0 - y_norm) * 30) + 2 # Range: 2 a 32 notas
                        arpeggiator.set_arp_length(arp_len)
                        
                        # UI Fader Range
                        pct = int(y_norm * h_img)
                        cv2.rectangle(img, (20, pct), (50, h_img), (255, 0, 255), cv2.FILLED)
                        cv2.putText(img, f"NOTAS: {arp_len}", (70, pct + 5), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 255), 2)

                    else:
                        smooth_pinch_y = -1 # Reseta a inércia suave
                        
                        # --- MODOS DE ARPEJO (Comando Sequencial) ---
                        if soma_dedos == 5:
                            current_frame_arp = "arpeggio"
                            cv2.putText(img, "Arpejo: Pad Sequencial", (20, h_img - 80), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 255), 2)
                        elif f_up_left == [False, True, False, False, False]:
                            current_frame_arp = "melodic_minor"
                            cv2.putText(img, "Arpejo: M. Melodica", (20, h_img - 80), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 255), 2)
                        elif f_up_left == [False, True, False, False, True]:
                            current_frame_arp = "natural_minor"
                            cv2.putText(img, "Arpejo: M. Natural", (20, h_img - 80), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 255), 2)
                        else:
                            cv2.putText(img, "Arp: Desligado", (20, h_img - 80), cv2.FONT_HERSHEY_DUPLEX, 1.0, (100, 100, 100), 2)
                    continue

                # ----- Mão Direita (Acordes) -----
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
        
        # Alimenta os metadados do Sequenciador da Esquerda
        arpeggiator.set_chord_context(current_frame_chord)
        arpeggiator.set_mode(current_frame_arp)

        # FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        # Botão de Ajuda UI
        btn_color = (0, 0, 255) if show_help else (100, 100, 100)
        cv2.rectangle(img, (10, 60), (180, 100), btn_color, cv2.FILLED)
        cv2.putText(img, "AJUDA (PINCA)", (20, 85), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 2)
        
        # Painel de Tutoriais
        if show_help:
            overlay_help = img.copy()
            cv2.rectangle(overlay_help, (80, 100), (w_img-80, h_img-50), (0, 0, 0), cv2.FILLED)
            cv2.addWeighted(overlay_help, 0.85, img, 0.15, 0, img)
            
            lines = [
                "----- TUTORIAL DE GESTOS -----",
                "",
                "[ MAO DIREITA - Acordes ]",
                " - Dedo Indicador: DO | Hang Loose: LA | So Mindinho: SI",
                " - 2, 3, 4 Dedos respectivos: RE, MI, FA",
                " - Mao Aberta: SOL",
                " - Pulso p/ Baixo = Cifra Maior | Pulso p/ Cima = Cifra Menor",
                " - Zonas: Topo Dir (#), Topo Esq (b), Base Inteira (Natural)",
                "",
                "[ MAO ESQUERDA - Arpejo e Modwheel ]",
                " - Pinca (Indicador+Polegar) Posicao Y: Volume (Master)",
                " - Like / Joinha Posicao Y: BPM / Velocidade Arpejo",
                " - Arminha (Like+Indicador) Posicao Y: Qtd Notas Arpejo",
                " - Mao Aberta (Sozinha): Liga Arpejo Sequencial",
                " - So Indicador (Sozinho): Liga Escala Menor Melodica",
                " - Indicador+Mindinho (Rock): Liga Escala Menor Natural"
            ]
            y_offset = 140
            for line in lines:
                cv2.putText(img, line, (100, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
                y_offset += 25

        cv2.putText(img, f'FPS: {int(fps)}', (10, 40), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 0, 255), 2)
                    
        cv2.imshow("Instrumento Inteligente - Sintetizador de Acordes VISUAL", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    midi_synth.close()
    arpeggiator.close()

if __name__ == "__main__":
    main()
