# 🎹 Virtual Instrument CV (Sintetizador de Acordes Gestual)

Um Instrumento Musical sem toque (Touchless) construído inteiramente com **Python, Visão Computacional e Processamento Digital de Sinais**. 
Ele lê o feed de vídeo da sua Webcam através de um HUD Cyberpunk e utiliza reconhecimento isométrico dos seus dedos para deduzir **Acordes Musicais**, transmitindo os sinais instantaneamente para qualquer Sintetizador de Áudio (GarageBand, Logic, Ableton) via **Portas MIDI Virtuais**.

## 🚀 Arquitetura e Engenharia

### 1. Tracking Ósseo & OpenCV (Fase 1)
No núcleo da captura usamos `mediapipe-silicon` (para compatibilidade nativa de Machine Learning com hardware Apple M1/M2/M3). O vídeo é escurecido e sobreposto com wireframes de neon (`src/main.py`) para desenhar a HUD das notas lidas e o monitoramento FPS.

### 2. Motor Gestual e Invariância Rotacional (Fase 2)
A classe avançada `GestureRecognizer` decifra todo o vocabulário da mão usando matemática Euclidiana pura. Em vez de testar `Y > X` (o que quebraria a câmera se a mão estivesse de ponta cabeça), calculamos as distâncias radiais do Pulso até os Nós, o que torna o nosso leitor **100% Invariante à Rotação**. O dedão se baseia no alongamento da palma para determinar tensão.

**🎵 O Alfabeto de Acordes:**
- 🧍‍♂️ Apenas Indicador = **Dó (C)**
- ✌️ Indicador + Médio = **Ré (D)**
- 🤟 3 Dedos = **Mi (E)**
- 🖐️ 4 Dedos = **Fá (F)**
- 🤚 Mão Toda Aberta = **Sol (G)**
- 🤙 Hang Loose = **Lá (A)**
- 🤙 Só o Mindinho = **Si (B)**

**🎹 Maiores vs Menores:**
Se sua mão apontar pro Céu (Pulso abaixo dos dedos), é Maior! Se você girar sua mão apontando pro chão, a classe injeta o modo Menor automaticamente (Ex: `Am`).

### 3. Zonas Espaciais Híbridas (Fase 3)
Em vez de teclados fixos, a posição física no ar determina as propriedades sonoras:
- O painel base domina apenas a **Metade Direita da Câmera**.
- Ao levantar o seu dedo até os 30% superiores para a direita, engata o Acorde **Sustenido (#)**.
- Ao levantar para a esquerda, engata o **Bemol (b)**.
- A imensa maioria gravitacional (70% pra baixo) age como área de descanso para acordes **Naturais**. 

### 4. Processamento DSP e Instrumento Virtual (Fase 4)
Nossas leituras faciais tremulas da câmera são absorvidas por um autêntico **Zero-Latency 1-Euro Filter** (`src/dsp/filters.py`) que derrete todo o tremor vibracional provido da luz ambiente, servindo um Sinal Digital 100% estável e cravado.

Em seguida, o motor Musical (`src/audio/midi_engine.py`) decodifica cifras musicais `C#m` em matrizes poli-tonais de `Mido` em C++ (RtMIDI), construindo no kernel do macOS a conexão transparente "Virtual Instrument CV". Abra o seu DAW favorito, escolha o patch de um *Vintage Pad*, coloque as mãos no ar e a música acontece milissegundos depois!

## 💻 Instalação & Setup

**Pré-requisitos:** MacOS (Apple Silicon) & Python 3.11+.

```bash
# 1. Crie e ative o ambiente virtual para segurança
python3 -m venv venv
source venv/bin/activate

# 2. Instale todas as dependências nativas
pip install -r requirements.txt

# 3. Aperte o "Play" (Não esqueça de conceder permissão de Câmera pro Terminal!)
python src/main.py
```