# Boids 3D Ecosystem Simulation

![Taichi](https://img.shields.io/badge/Taichi-High_Performance-blue)
![Python](https://img.shields.io/badge/Python-3.12-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

> Uma simulação de vida artificial e comportamentos emergentes em tempo real, renderizando 50.000 partículas simultâneas através de aceleração massiva em GPU.

<div align="center">
  <img src="demonstrations/50000_boids/video.gif" alt="Demonstração do Boids 3D com 50.000 Boids" width="600">
</div>

## Sobre o Projeto

Este projeto implementa o algoritmo de **Boids** (desenvolvido por Craig Reynolds em 1986) em um ambiente 3D. Em vez de calcular as interações na CPU, a simulação foi construída utilizando a linguagem/biblioteca **Taichi**, o que permite compilar o código Python diretamente para kernels de GPU (Cuda/Vulkan). Além disso, foram implementadas outras técnicas para otimização de processamento.

## Arquitetura e Otimização

Para contornar o gargalo de complexidade O(N²) e executar o processamento em paralelo de forma eficiente, o projeto se apoia em duas técnicas essenciais:

*   **Uniform Spatial Grid:** O espaço 3D é dividido em pequenas células estruturadas em grade, reduzindo o espaço de busca para cada Boid. Assim, cada boid só procura e interage com vizinhos que estão dentro da sua própria célula ou nas células coladas nela.
*   **Data-Oriented Programming:** A estrutura do código foi implementada pensando em como a placa de vídeo prefere consumir informações. Usando os campos do Taichi, os dados de todos os boids são alinhados sequencialmente na memória. Essa organização garante que a GPU consiga acessar as informações o mais rápido possível.

## Funcionalidades

Além de implementar as regras clássicas de *flocking*, a simulação introduz comportamentos e instintos avançados:

*   **Regras Clássicas (Flocking):**
    *   *Coesão:* Boids tentam se aproximar do centro de massa dos vizinhos.
    *   *Alinhamento:* Boids alinham sua velocidade e direção com o grupo.
    *   *Separação:* Boids evitam colisões entre si.
*   **Instintos de Sobrevivência:**
    *   *Predadores (Hunting/Fleeing):* Boids vermelhos caçam o boid mais próximo. Boids azuis possuem um multiplicador de visão para fugir do perigo.
    *   *Alimentação (Foraging):* Boids são atraídos por pontos de comida (verdes) espalhados pelo ambiente.
*   **Física e Ambiente:** 
    *   Sistema de bordas invisíveis (Steer away from edges).
    *   Aceleração por gravidade e ganho de velocidade em mergulhos (*Dive Boost*).

## Como Executar na Sua Máquina

### Pré-requisitos
Certifique-se de ter o Python 3.9+ instalado e uma placa de vídeo dedicada.

### Instalação
```bash
# Clone o repositório
git clone https://github.com/Leandroc728/Boids-3D-Taichi-SpatialGrid.git

# Entre na pasta
cd Boids-3D-Taichi-SpatialGrid

# Instale as dependências
pip install -r requirements.txt

# Execute
python main.py
```
## Interface de Usuário

O projeto inclui um painel de controle interativo onde é possível ajustar as variáveis em tempo real:

* Sliders de Pesos: Altere a intensidade de coesão, separação, medo e outras variáveis.
* Raio de Percepção: Ajuste quão longe cada boid consegue "enxergar".
* Controle de Câmera: Utilize o Botão Direito do Mouse para rotacionar e as teclas para navegar no espaço 3D(W, A, S, D, Q, R).

## Ferramentas

* Python 3.12: Linguagem base.
* Taichi Lang: Compilação JIT para GPU.
