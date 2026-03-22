# 🎹 Roadmap: Instrumento Musical Inteligente (CV & ML Focus)

Este roadmap foi otimizado para um portfólio de Data Science e Computer Vision, focando em técnicas avançadas de processamento de sinais e modelagem.

## 1. Engenharia de Captura e Visão (CV) 👁️
- [ ] Extração de Features: Implementar HandTracker modular para extrair coordenadas 3D (X, Y, Z) dos 21 marcos do MediaPipe.
- [ ] Normalização Espacial: Criar algoritmo para normalizar as coordenadas em relação ao tamanho da palma da mão (tornando o sistema robusto a diferentes distâncias da câmera).
- [ ] Tratamento de Oclusão: Implementar lógica para lidar com a perda momentânea de rastreio (Data Imputation simples para evitar cliques no áudio).
- [ ] HUD de Debug: Interface com máscaras de segmentação e exibição de vetores de movimento.

## 2. Processamento de Sinais e Estatística (Data Science) 📈
- [ ] Filtro de Kalman ou One Euro Filter: Implementar filtros avançados para reduzir o "jitter" (ruído) das mãos, garantindo um sinal de áudio limpo.
- [ ] Mapeamento Logarítmico: Converter o movimento linear do eixo Y para a escala logarítmica de frequências (Hz) ou semitons MIDI.
- [ ] Janelamento (Sliding Window): Usar janelas temporais para detectar a intenção do gesto antes de disparar o gatilho sonoro.

## 3. Classificação de Gestos (Machine Learning) 🤖
- [ ] Coleta de Dataset: Criar um script para gravar as coordenadas das mãos em diferentes posições (aberta, fechada, pinça, sinal de 'V').
- [ ] Treinamento de Modelo: Treinar um classificador (SVM, Random Forest ou uma rede neural simples) usando Scikit-learn ou TensorFlow para reconhecer gestos específicos.
- [ ] Inference Pipeline: Integrar o modelo treinado para que a troca de escalas ou timbres seja feita via classificação de imagem, e não apenas por "if/else" de distância entre dedos.

## 4. Arquitetura do Instrumento e Áudio 🎵
- [ ] Motor de Síntese: Implementar AudioEngine usando portas MIDI virtuais para demonstrar integração entre sistemas.
- [ ] Quantização Probabilística: Criar um sistema que "puxa" a nota para a mais próxima da escala escolhida (Scale Snap).
- [ ] Controle Dinâmico: Mapear a velocidade do movimento (derivação da posição) para a "Velocity" (intensidade) da nota MIDI.

## 5. Análise de Performance e Analytics (DS) 📊
- [ ] Data Logging: Exportar os dados da performance (notas tocadas, estabilidade das mãos, tempo de resposta) para um arquivo .csv ou .json.
- [ ] Dashboard de Performance: Criar um pequeno notebook (ou tela no app) que mostre o "Heatmap" de onde o usuário mais tocou e a precisão do rastreio.

## 6. Documentação e Portfólio 🚀
- [ ] README Técnico: Explicar a matemática por trás da normalização e a escolha do filtro de suavização.
- [ ] Gif/Vídeo Demonstrativo: Gravar a tela com o HUD de debug ativo (mostrando os esqueletos das mãos e as predições do modelo de ML).
- [ ] Setup Instructions: Guia de como configurar o ambiente virtual e as portas MIDI virtuais.