import mido
import time

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
        self.outport = None
        
        try:
            # Requer o backend rtmidi para abrir portas virtuais nativas
            self.outport = mido.open_output(self.port_name, virtual=True)
            print(f">>> Porta MIDI conectada com sucesso: '{self.port_name}'")
            print(">>> Abra o GarageBand e comece a tocar!")
        except Exception as e:
            print(f">>> ERRO CRÍTICO no MIDI: Não foi possível abrir porta virtual.\nMotivo: {e}")

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
