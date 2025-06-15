✨ Otimização de Redes Urbanas: Farmácias e Hospitais em Natal com o Algoritmo de Kruskal 🏥💊

Este repositório contém um poderoso notebook Python que desvenda a lógica por trás da distribuição de serviços essenciais nas cidades! Usamos o Algoritmo de Kruskal para otimizar a conectividade entre pontos de interesse (POIs) em um cenário urbano real. Nossa missão? Explorar a distribuição de farmácias e hospitais em Natal, Rio Grande do Norte, e identificar a rede de conexões mais eficiente para esses locais vitais.

🗺️ O Desafio que Resolvemos
Nosso objetivo principal foi analisar como a localização estratégica das farmácias em Natal se relaciona com a facilidade de acesso e a proximidade de serviços cruciais como hospitais, UPAs e clínicas. Através da construção de um grafo urbano e da aplicação da Árvore Geradora Mínima (MST), conseguimos identificar o arranjo de conexões que minimiza a distância total para interligar esses estabelecimentos, revelando padrões de otimização no planejamento urbano.

🧠 Desvendando os Conceitos por Trás da Solução
Para entender a mágica por trás dessa otimização, precisamos explorar alguns conceitos fundamentais:

Grafos Urbanos: Imagine sua cidade como um mapa de conexões! 📍 

Grafos são estruturas matemáticas que representam a rede de ruas e pontos de interesse (nós/vértices) de uma cidade, com as conexões (arestas) tendo "pesos" como distância ou tempo.
Árvore Geradora Mínima (MST - Minimum Spanning Tree): Pense na forma mais econômica de conectar todos os pontos de uma rede sem criar nenhum caminho redundante (ciclo). A MST é exatamente isso: uma subestrutura de um grafo que conecta todos os seus vértices com o menor custo total possível. 🌳

Algoritmo de Kruskal: Nosso herói da otimização! 💪 Este algoritmo "guloso" encontra a MST selecionando, passo a passo, as arestas de menor peso que não formam ciclos, construindo a árvore de forma eficiente.

💻 Como Rodar o Código Localmente
Quer replicar essa análise e explorar os dados de Natal? Siga estes passos simples para rodar o notebook em sua máquina!

Clone o Repositório: Primeiro, você precisa baixar o código para o seu computador. Abra seu terminal ou prompt de comando e execute:
Bash

git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio # Navegue até a pasta do projeto
Crie e Ative o Ambiente Virtual: É uma boa prática criar um ambiente virtual para isolar as dependências do projeto.

python -m venv venv
No Windows:

.\venv\Scripts\activate
No Linux/macOS:

source venv/bin/activate

Instale as Dependências: Com o ambiente ativado, instale todas as bibliotecas necessárias.

pip install -r requirements.txt

Execute o Notebook: Agora, você pode abrir e rodar o notebook.

📊 Nosso Grafo Gerado em Natal
Após rodar o notebook, você terá uma visualização impactante do grafo das farmácias e hospitais em Natal. Veja como as conexões mínimas se formam e onde os pontos de interesse se localizam!

![Image](https://github.com/user-attachments/assets/b66225c1-3b37-41f8-8942-538e901c869a)

🔍 Análise e Resultados Encontrados
A execução do Algoritmo de Kruskal no nosso grafo de farmácias, em conjunto com a localização dos hospitais, nos trouxe insights cruciais sobre a dinâmica urbana de Natal:

O traçado em vermelho, que representa a Árvore Geradora Mínima (MST) entre as farmácias selecionadas, demonstra visualmente a rede de conexões mais eficiente e de menor custo (em termos de distância) para interligar esses estabelecimentos. O comprimento total calculado da MST (mencionado na legenda do gráfico) quantifica essa otimização, mostrando o mínimo de infraestrutura de conexão necessária.

Ao observarmos a distribuição dos pontos azuis (farmácias) e dos pontos vermelhos (hospitais) no mapa, emerge uma clara correlação entre suas localizações:

Concentração em Áreas Chave: É perceptível que a maior parte das farmácias, e consequentemente os trechos da MST, tendem a se concentrar em regiões com alta densidade urbana e, notavelmente, próximas a grandes hospitais ou centros de saúde. Esta proximidade não é mera coincidência; ela reflete uma estratégia de mercado e uma necessidade prática.
Facilidade de Acesso: A localização estratégica das farmácias em avenidas principais e em pontos de fácil acesso (visíveis no grafo de ruas subjacente) é um fator chave para garantir que pacientes e acompanhantes dos hospitais possam se dirigir rapidamente a uma farmácia caso o hospital não forneça um medicamento específico ou para conveniência pós-consulta.
Otimização para o Cliente e para o Negócio: Essa proximidade e conectividade otimizada pelas vias urbanas facilita não apenas a vida do consumidor (pacientes, visitantes), que encontra o que precisa com menos deslocamento, mas também otimiza a logística e o potencial de lucro para as farmácias. Estar "no caminho" ou "ao lado" de um hospital garante um fluxo constante de clientes com necessidades imediatas por produtos farmacêuticos.
Em síntese, a análise do nosso grafo revela que a alta quantidade e a distribuição das farmácias em Natal estão intrinsecamente ligadas à localização estratégica dos hospitais, formando uma rede de apoio essencial para a saúde pública e privada na cidade, otimizada pela acessibilidade e conveniência.

🚀 Aplicações no Mundo Real
A análise de redes urbanas com algoritmos como o Kruskal vai muito além das farmácias! Essa metodologia tem aplicações poderosas em diversos setores:

Mobilidade Urbana: Otimizar rotas para serviços de entrega, transporte público ou veículos de emergência. 🚚🚑
Redes de Infraestrutura: Planejar a instalação de cabos de fibra óptica, redes de saneamento ou linhas de energia elétrica com o menor custo. 💡💧

Planejamento de Negócios: Analisar a melhor localização para novos estabelecimentos comerciais, considerando a proximidade a outros pontos de interesse e a acessibilidade. 📈

Serviços de Saúde: Otimizar a distribuição de unidades de saúde e farmácias para melhor atendimento à população. ❤️

✍️ Leia o Artigo Completo no Medium
Quer entender cada detalhe desse projeto, desde os fundamentos teóricos até as implementações práticas? Publicamos um artigo super completo no Medium!

Acesse o artigo completo aqui: https://medium.com/@andreluizlimaa/desvendando-a-rede-de-farmácias-de-natal-uma-análise-com-grafos-e-o-algoritmo-de-kruskal-92cd2bc04b92

🎧 Mergulhe Fundo com Nosso Podcast no NotebookLM
Para complementar a leitura e ter uma experiência mais dinâmica, gravamos um podcast exclusivo no NotebookLM, totalmente baseado no conteúdo do nosso artigo no Medium! Nele, você encontrará uma entrevista em formato de perguntas e respostas, abordando:

O Problema: Discutimos em detalhes o problema de otimização da conectividade em redes urbanas que o notebook resolveu.
Conceitos Chave: Explicamos de forma ainda mais acessível a Árvore Geradora Mínima (MST), o Algoritmo de Kruskal e como os grafos urbanos são ferramentas poderosas.
Aplicações Práticas: Exploramos diversas aplicações, desde a mobilidade urbana até o planejamento de redes de infraestrutura.
Impacto e Aprendizados: Refletimos sobre a importância dessas análises para o planejamento de cidades inteligentes e os principais conhecimentos adquiridos.
Ouça o podcast e aprofunde seu conhecimento: https://drive.google.com/file/d/1qUFj6ZEiOTmsEYtqaziFXYgBb88tJfYu/view?usp=sharing

