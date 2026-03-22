# 🎹 Instrumento Musical Inteligente (CV & DSP)

Bem-vindo ao repositório do **Instrumento Musical Inteligente**, um projeto focado em fundir Visão Computacional (CV) com Processamento Digital de Sinais (DSP) e futuramente Machine Learning para criar uma experiência musical touchless (sem toque) via Webcam.

## 🚀 Status do Projeto

Neste momento, a arquitetura base do sistema foi estabelecida:

### Fase 1: Visão Computacional Robusta (Concluída ✅)
Implementamos um núcleo de rastreamento de mãos em tempo real usando **MediaPipe (versão Apple Silicon)**.
- **Detecção Múltipla:** Capaz de rastrear e segmentar múltiplas mãos simultaneamente com suporte a bounding boxes.
- **Normalização Espacial Matemática:** Para garantir que a distância da câmera não influencie a "escala" musical, todas as coordenadas são divididas dinamicamente pela distância Euclidiana do Pulso ao Dedo Médio. Dessa forma, as coordenadas passam a ser relativas ao tamanho da mão, e não da tela.

### Fase 2: Digital Signal Processing (Andamento 🔄)
A captura crua do MediaPipe sofre com o natural *Jitter* (vibrações micro-milimétricas calculadas pela IA preditiva). Como para o áudio precisamos de estabilidade 100%, desenvolvemos:
- **Zero-Latency One Euro Filter:** Construído puramente em Python, este filtro passa-baixa adaptativo analisa a "velocidade" (derivada do movimento) da mão. Quando a mão se move rápido, a frequência de corte se ajusta para `beta` para evitar lag (atraso de rastreio). Quando a mão para, a frequência despenca e o sinal congela na tela, entregando precisão cirúrgica sem qualquer oscilação.

## 📁 Estrutura do Código
```text
src/
 ├── dsp/
 │    └── filters.py       # Algoritmos Matemáticos Puros (One-Euro Filter)
 ├── vision/
 │    └── hand_tracker.py  # Wrapper Orientado à Objetos para MediaPipe (Normalização)
 └── main.py               # Application Loop e HUD Interativo (OpenCV)
```

## 💻 Instalação & Execução

Para rodar os testes desenvolvidos no MacOS (Apple Silicon):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

*Nota: Garanta que o terminal que está rodando o Script possui as devidas permissões do macOS para acessar sua Câmera.*