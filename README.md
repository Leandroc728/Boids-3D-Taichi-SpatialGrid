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

Para superar o gargalo de complexidade O(N²) e aproveitar o processamento massivo da GPU, o projeto utiliza duas estratégias fundamentais:

### 1. Uniform Spatial Grid (USG)
O espaço 3D é subdividido em uma grade de células de tamanho fixo. Em vez de cada Boid comparar sua posição com todos os outros N elementos da simulação, ele consulta apenas a sua própria célula e as 26 células vizinhas.
* **Garantia de O(N):** Para assegurar a performance mesmo em cenários de alta densidade, implementei um limite rígido de busca por célula (`max_boids_per_cell`). Isso transforma a busca de vizinhos em uma operação de tempo constante O(1) por boid, resultando em uma complexidade global linear O(N).

### 2. Data-Oriented Programming (DOP)
Diferente da Programação Orientada a Objetos tradicional, onde os dados ficam dispersos na memória, foi utilizado a abordagem **DOP** através dos campos (`ti.field`) do Taichi.
* **Layout de Memória:** Os dados de posição e velocidade são armazenados de forma contígua. Isso maximiza a localidade de dados e permite que a GPU realize acessos globais de memória muito mais eficientes, reduzindo drasticamente a latência de processamento.

---

### O Resultado Técnico
* **Complexidade:** Redução de O(N²) para O(N).
* **Escalabilidade:** Capacidade de processar **50.000 agentes** simultaneamente.
* **Eficiência:** Execução fluida (40+ FPS) mesmo em hardware de entrada/integrado (Intel Iris Xe).
O algoritmo se tornou então de complexidade assintótica O(N), além de ser otimizado para o acesso de dados pela GPU.

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
