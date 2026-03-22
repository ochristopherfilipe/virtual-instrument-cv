# 🎹 Virtual Instrument CV (Sintetizador de Acordes Gestual)

Um Instrumento Musical sem toque (Touchless) construído inteiramente com **Python, Visão Computacional e Processamento Digital de Sinais (DSP)**. 
Ele lê o feed de vídeo da sua Webcam através de um HUD Cyberpunk interativo e utiliza reconhecimento isométrico biológico para deduzir **Acordes Musicais e Modulations**, transmitindo os sinais instantaneamente para qualquer Sintetizador de Áudio (GarageBand, Logic, Ableton) via **Portas MIDI Virtuais C++**.

## 🚀 Arquitetura e Engenharia

### 1. Tracking Ósseo & OpenCV
No núcleo da captura usamos `mediapipe-silicon` (para compatibilidade nativa de Machine Learning com hardware Apple Silicon). O vídeo base da câmera recebe um blend escurecido de sobreposição de wireframes de neon (`src/main.py`) construindo a HUD gráfica das notas e os atuadores modulares.

### 2. Motor Gestual Invariante e Visão da Mão Direita
A classe avançada `GestureRecognizer` decifra o vocabulário da sua Mão Direita usando matemática Euclidiana pura. Avaliamos a distância radial do Pulso até a ponta (Tip) em contraste com o nó médio (PIP), o que nos entrega uma topologia **100% Invariante à Rotação** (perfeita para identificar dedos de ponta-cabeça na webcam).

**🎵 O Alfabeto de Acordes (Mão Direita):**
- 🧍‍♂️ Apenas Indicador = **Dó (C)** | 🤙 Hang Loose = **Lá (A)** | 🤙 Só o Mindinho = **Si (B)**
- ✌️ 2, 3 e 4 Dedos = Respectivos **Ré (D), Mi (E) e Fá (F)**
- 🤚 Mão Toda Aberta = **Sol (G)**
- **Maiores vs Menores:** Mão apontando pro teto = Cifra Maior, Apontando para o chão = Cifra Menor.

**Zonas Híbridas (Mão Direita):**
- Topo Direito: **Sustenido (#)**
- Topo Esquerdo: **Bemol (b)**
- Metade Inferior Inteira (70%): Área de descanso ergonômico para notas **Naturais**.

### 3. Arpejador Multithread e Modwheel da Mão Esquerda
A Mão Esquerda foi isolada em memória para funcionar como um maestro expressivo simultâneo.
O núcleo do sequenciador roda protegido em uma **Thread Paralela Background**, garantindo que o delay BPM entre as notas toque sem nunca "congelar" o processamento de frames da Webcam. O Python exporta o seu áudio em **Duas Portas Virtuais** independentes (`Virtual Instrument CV` e `Virtual Instrument Arp`).

**Controles Contínuos (Deslizamentos Virtuais no Eixo Y):**
- 🤏 **Pinça (Indicador+Polegar):** Fader embutido na HUD mapeado para o **Volume Master** via MIDI Control Change nativo (CC#7).
- 👍 **Mão Fechada com Polegar Aberto (Joinha):** Controla a velocidade matemática do **BPM** do metrónomo.
- 🔫 **Arminha (Joinha + Indicador):** Controla a quantidade de notas do Arpejo *Ping-Pong* (Loop subindo e descendo pelas oitavas variando de 2 até 32 notas dinâmicas com proteção *crashproof* até a clave limite 127). Possui lógica de inércia e baixa-passagem algoritmica para suavidade.

**Sequenciador e Escalas Acionadas (Esquerda Livre):**
- 🤚 **Mão Aberta:** Alimenta a Tônica e dispara um Arpejo Sequencial do Acorde base da direita.
- ☝️ **Só Indicador:** Engatilha Escala Menor Melódica.
- 🤘 **Indicador+Mindinho (Rock):** Engatilha Escala Menor Natural.

### 4. Componente OSD Nativo (On-Screen Display)
- Basta levar a "Pinça" da mão esquerda até ao módulo azul na margem superior esquerda do vídeo para ativar a UI de Tutorial. Um algoritmo debouncer detecta os píxeis e projeta em runtime uma cortina escura por todo o seu vídeo, ensinando o "Manual" de uso completo do app para o usuário final sem precisar fechar e ler arquivos de texto.

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