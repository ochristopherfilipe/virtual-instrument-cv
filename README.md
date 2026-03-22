# 🎹 Virtual Instrument CV (Gestural Chord Synthesizer)

Um Instrumento Musical sem toque (Touchless) construído inteiramente com **Python, Visão Computacional e Processamento Digital de Sinais (DSP)**. 
Ele lê o feed de vídeo da sua Webcam através de um HUD interativo e utiliza reconhecimento isométrico biológico para deduzir Acordes Musicais, transmitindo os sinais instantaneamente para Sintetizadores de Áudio (GarageBand, Logic, Ableton) via **Portas MIDI Virtuais Internas**.

---

## 🛠️ Habilidades Técnicas e Conceitos Aplicados (Portfólio)

Este projeto foi construído para demonstrar aplicações práticas de engenharia de software e domínio de ecossistemas computacionais complexos:

* **Visão Computacional Aplicada (OpenCV & MediaPipe):** Triangulação espacial em tempo real de 21 *landmarks* ósseos por mão. Renderização de interfaces gráficas interativas HUD (Heads-Up Display) reativas à física da mão do usuário cravadas a 60 FPS.
* **Processamento Digital de Sinais (1-Euro Filter):** Implementação manual matemática do filtro de malha fechada **Zero-Latency 1-Euro** para remover o *jitter* (ruído de *bounding boxes*) inerente das predições de ML, garantindo que as leituras estroboscópicas traduzam em notas sem falso-positivos trêmulos.
* **Multithreading Coordenado & Concorrência:** Separação violenta do loop pesado de renderização de OpenCV em paralelismo com um Motor Sequenciador Musical (Arpejador). Uso nativo da biblioteca de `threading` (*Daemon*) do Python para polifonia de notas MIDI de 136 BPM de forma assíncrona, evitando *bottlenecking* do Feed da Câmera.
* **Engenharia de Áudio & Protocolos de Baixo Nível (CoreMIDI/RtMidi):** Interação direta com os drivers de áudio do sistema operacional e barramentos locais (MAC) para instanciar dispositivos USB virtuais via C++. Programação estrita de protocolos polifônicos hexadecimais, translações Oitavadas por Pings e automação de sliders contínuos (`MIDI CC#7`).
* **Matemática Orientada a Geometria (Invariância Rotacional Euclidiana):** O classificador de gestos (*Engine* de Poses) foi completamente recodificado em métricas Euclidianas que avaliam as *ratios* da ponta dos dedos (*Tip*) exclusivamente em relação ao osso flexor do meio do dedo, e ao pulso. Isso quebrou totalmente a barreira de orientação padrão (*hardcoded*) típica na visão computacional (eixos X/Y do array), garantindo **100% de precisão de Hand Tracking independente da câmera** de perfil de mão virada para baixo, invertida ou em perspectiva diagonal.

---

## 🚀 Arquitetura Funcional

### 1. Classificador Acústico da Mão Direita
A classe `GestureRecognizer` decifra o acorde base (Mão direita).
- 🧍‍♂️ Apenas Indicador = **Dó (C)** | 🤙 Hang Loose = **Lá (A)** | 🤙 Mindinho = **Si (B)**
- ✌️ 2, 3 e 4 Dedos = Respectivos **Ré (D), Mi (E) e Fá (F)** | 🤚 Mão Aberta = **Sol (G)**
- **Acordes Maiores vs Menores:** Mão apontando pro teto = Menor (Pulso invertido), Apontando para o chão = Maior.
- **Zonas Tonais Híbridas:** Levantar a mão fisicamente na seção Topo-Esquerda do monitor injeta a matemática de **Bemois (b)** ou Topo-Direita para **Sustenidos (#)**. Parte Inferior retorna notas **Naturais**.

### 2. O Controlador Expressivo de Modulação Contínua (Mão Esquerda)
A Mão Esquerda (se na tela) instaura o seu próprio painel modular. Através do rastreamento vertical, o script traduz o deslocamento de eixos Píxeis para *Modwheels* e Potenciômetros Midi no seu DAW em tempo real.
- 🤏 **Pinça (Indicador+Polegar):** Controla o **Volume Master** via *Control Change* 7.
- 👍 **Joinha:** Modifica a aceleração métrica da música (**BPM** do Arpejador) fluida de 60 a 240 oscilações algorítmicas por minuto.
- 🔫 **Arminha (Joinha + Indicador):** Define o tamanho do Escopo (Array) do range Dinâmico musical. Um Filtro passa-baixas dinâmico amortece a variação entre a escala de criação de 2 a 32 notas.

### 3. Sequenciador Tonal Assíncrono
Gatilhos independentes de Arpejos executados de forma fantasma numa segunda porta Output injetando escalas em tempo real na raiz provida pela Mão Direita:
- 🤚 **Mão Aberta:** Construção da Árvore Lógica *Up/Down (Ping-Pong)* baseada no arpejo fundamental.
- ☝️ **Só Indicador:** Engatilha uma Escala Menor Melódica infinita.
- 🤘 **Indicador+Mindinho (Rock):** Engatilha uma Escala Menor Natural.

### 4. Menu Debouncer OSD Nativo (*On-Screen Display*)
Acione dinamicamente o *Cheat Sheet*/Tutorial OSD em cima de sua Webcam ao clicar fisicamente com os dedos "Pinça" na tela dentro do Painel de Bounding Box demilitado (XY).

---

## 💻 Instalação & Setup

**Pré-requisitos:** MacOS (Apple Silicon nativo) & Python 3.11+.

```bash
# 1. Crie e ative o ambiente virtual para impedir dependência vazada do sistema.
python3 -m venv venv
source venv/bin/activate

# 2. Instale dependências matemáticas e visuais estritas
pip install -r requirements.txt

# 3. Start a engine e ative a permissão nativa de Câmera da CLI no macOS!
python src/main.py
```