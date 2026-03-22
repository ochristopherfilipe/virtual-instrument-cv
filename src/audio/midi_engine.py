import mido
import time
import threading

def get_midi_base(note_str):
    """ Mapeia o caractere da nota para a nota base numérico do MIDI na oitava 4 """
    note_to_midi = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}
    base = note_to_midi.get(note_str[0], 60)
    
    if '#' in note_str:
        base += 1
    elif 'b' in note_str:
        base -= 1
        
    return base

def get_chord_notes(chord_str):
    """
    Traduz 'C#m', 'F', 'Eb' para uma array de 3 inteiros MIDI compondo o Acorde.
    Retorna [] se for silêncio.
    """
    if chord_str == "SILÊNCIO" or not chord_str:
        return []
        
    base_midi = get_midi_base(chord_str)
    
    if 'm' in chord_str:
        # Acorde Menor: Tônica, Terça Menor (+3), Quinta Justa (+7)
        return [base_midi, base_midi + 3, base_midi + 7]
    else:
        # Acorde Maior: Tônica, Terça Maior (+4), Quinta Justa (+7)
        return [base_midi, base_midi + 4, base_midi + 7]


class MidiEngine:
    def __init__(self, port_name="Virtual Instrument CV"):
        self.port_name = port_name
        self.current_notes = []
        self.last_volume = -1
        self.outport = None
        
        try:
            # Requer o backend rtmidi para abrir portas virtuais nativas
            self.outport = mido.open_output(self.port_name, virtual=True)
            print(f">>> Porta MIDI conectada com sucesso: '{self.port_name}'")
            print(">>> Abra o GarageBand e comece a tocar!")
        except Exception as e:
            print(f">>> ERRO CRÍTICO no MIDI: Não foi possível abrir porta virtual.\nMotivo: {e}")

    def set_volume(self, value):
        """
        value: Inteiro de 0 a 127
        Control Change (CC) de ID 7 é o Master Volume / Expression do MIDI.
        """
        if not self.outport:
            return
            
        val = max(0, min(127, int(value)))
        
        # Evitando congestionamento de driver limitando spam do slider
        if val != self.last_volume:
            self.outport.send(mido.Message('control_change', channel=0, control=7, value=val))
            self.last_volume = val

    def update(self, chord_str):
        """
        Faz transições perfeitas estilo Pad/Sustain.
        Desliga o que deve ser desligado e liga as vozes novas, sem repetir notas gastando CPU.
        """
        if not self.outport:
            return
            
        target_notes = get_chord_notes(chord_str)
        
        # Se o acorde desejado for perfeitamente igual ao que já ressoa, apenas ignora
        if set(target_notes) == set(self.current_notes):
            return
            
        # 1. Envia 'Note Off' nas notas físicas que não existem mais nesse novo formato/acorde
        for n in self.current_notes:
            if n not in target_notes:
                self.outport.send(mido.Message('note_off', note=n, velocity=0))
                print(f"🎵 [MIDI OFF] Parando nota {n}")
                
        # 2. Envia 'Note On' apendas nas vozes/teclas novas que devem soar agora
        if target_notes and set(target_notes) != set(self.current_notes):
            print(f"🎶 [MIDI ON] -> Disparando Acorde {chord_str} (Notas: {target_notes})")
            
        for n in target_notes:
            if n not in self.current_notes:
                self.outport.send(mido.Message('note_on', note=n, velocity=85))
                
        self.current_notes = target_notes

    def close(self):
        """ Limpa as vozes presas (Panic) e fecha o bus MIDI com o GarageBand """
        if self.outport:
            for n in self.current_notes:
                self.outport.send(mido.Message('note_off', note=n, velocity=0))
            self.outport.close()

class Arpeggiator:
    def __init__(self, port_name="Virtual Instrument Arp", bpm=130):
        self.port_name = port_name
        self.bpm = bpm
        self.outport = None
        
        try:
            self.outport = mido.open_output(self.port_name, virtual=True)
            print(f">>> Porta MIDI de Arpejos conectada: '{self.port_name}'")
        except Exception as e:
            print(f">>> ERRO Arp MIDI: {e}")
            
        self.base_note = 60 # C4 por padrão se não receber acorde
        self.mode = "OFF"
        self.chord_type = ""
        self.arp_length = 8
        
        # Sequência atual sendo tocada
        self.pattern = []
        self.step = 0
        
        # Controle da Thread
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def set_chord_context(self, chord_str):
        """ Sincroniza a Tônica da esquerda baseada na Mão Direita (Acorde) """
        if chord_str == "SILÊNCIO" or not chord_str:
            self.base_note = None
            return
            
        self.base_note = get_midi_base(chord_str)
        self.chord_type = "m" if "m" in chord_str else ""
        self._rebuild_pattern()

    def set_bpm(self, bpm):
        self.bpm = max(30, min(300, int(bpm)))

    def set_arp_length(self, length):
        new_length = max(2, min(32, int(length)))
        if self.arp_length != new_length:
            self.arp_length = new_length
            self._rebuild_pattern()

    def set_mode(self, mode):
        """ Atualiza o array musical para a escala desejada """
        if self.mode != mode:
            self.mode = mode
            self.step = 0
            self._rebuild_pattern()

    def _rebuild_pattern(self):
        if not self.base_note or self.mode == "OFF":
            self.pattern = []
            return
            
        # Oitava superior para destacar do Pad Grave (+12 semitons = Oitava 5)
        base = self.base_note + 12
        intervals = []
        
        if self.mode == "arpeggio":
            # Arpejo Sequencial Misto Baseado na Fundamental
            intervals = [0, 3, 7] if self.chord_type == "m" else [0, 4, 7]
        elif self.mode == "melodic_minor":
            # Escala Menor Melódica Ascendente
            intervals = [0, 2, 3, 5, 7, 9, 11]
        elif self.mode == "natural_minor":
            # Escala Menor Natural
            intervals = [0, 2, 3, 5, 7, 8, 10]
        else:
            return
            
        # 1. Cria a cascata "Indo" empilhando as oitavas conforme a qtd de notas dinâmicas
        notes_up = []
        for i in range(self.arp_length):
            interval = intervals[i % len(intervals)]
            octave = (i // len(intervals)) * 12
            note_val = base + octave + interval
            if note_val > 127: break # MIDI Crash protection (Limites do Teclado Real)
            notes_up.append(note_val)
            
        # 2. Cria a cascata "Voltando" (Ping-Pong)
        if len(notes_up) > 2:
            notes_down = notes_up[-2:0:-1]
            self.pattern = notes_up + notes_down
        elif len(notes_up) == 2:
            self.pattern = notes_up + notes_up[::-1]
        else:
            self.pattern = notes_up

    def _loop(self):
        """ O cérebro do sequenciador Rítmico (Metrônomo) rodando nos Bastidores """
        while self.running:
            if not self.pattern or not self.outport:
                time.sleep(0.01)
                continue
                
            # Calcula o delay de uma Semicolcheia (1/16 note)
            delay = 60.0 / self.bpm / 4.0
            note_to_play = self.pattern[self.step % len(self.pattern)]
            
            # Toca a nota
            self.outport.send(mido.Message('note_on', note=note_to_play, velocity=100))
            
            # Segura quase até a próxima para staccato leve
            time.sleep(delay * 0.8)
            
            # Solta
            self.outport.send(mido.Message('note_off', note=note_to_play, velocity=0))
            
            # Microssegundo de silêncio para limpar
            time.sleep(delay * 0.2)
            
            self.step += 1

    def close(self):
        self.running = False
        if self.outport:
            self.outport.close()
