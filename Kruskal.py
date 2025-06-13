import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# --- FUNÇÃO PARA CONVERTER O GRAFO ---
def to_undirected_multigraph(G):
    """
    Converte um MultiDiGraph direcionado em um MultiGraph não-direcionado,
    preservando atributos dos nós e arestas.
    """
    H = nx.MultiGraph()
    # Copiar nós e seus atributos
    for n, data in G.nodes(data=True):
        H.add_node(n, **data)

    # Copiar arestas e seus atributos, sem direcionamento
    for u, v, data in G.edges(data=True):
        # Em um MultiGraph, se já existir uma aresta u-v, esta será adicionada como mais uma aresta paralela
        H.add_edge(u, v, **data)

    # Copiar atributos do grafo
    H.graph.update(G.graph)
    return H

# --- CONFIGURAÇÃO DO LIMITE DE POIs ---
# Defina o número máximo de POIs para o cálculo do MST.
# Se houver mais POIs do que esse valor, apenas os primeiros serão usados.
MAX_POIS_FOR_MST = 60 # Você pode mudar este valor para 10, 20, etc.

# --- CÓDIGO PRINCIPAL ---

# ============================================
# 1. Obter e processar o grafo da cidade de Natal
# ============================================
place = "Natal, Rio Grande do Norte, Brazil"
G = ox.graph_from_place(place, network_type='drive')

# Converte para não-direcionado mantendo o tipo MultiGraph
G_undirected = to_undirected_multigraph(G)

print("Obtendo o maior componente conectado do grafo usando NetworkX...")
# Encontra todos os componentes conectados
connected_components = list(nx.connected_components(G_undirected))
# Encontra o maior componente (o que tem mais nós)
largest_component_nodes = max(connected_components, key=len)
# Cria um subgrafo contendo apenas os nós do maior componente
G_undirected = G_undirected.subgraph(largest_component_nodes).copy()

print(f"Grafo possui {len(G_undirected.nodes)} nós e {len(G_undirected.edges)} arestas após filtragem do maior componente.")

# ============================================
# 2. Obter POIs de interesse (com fallback) e preparar informações detalhadas
# ============================================
# Tenta encontrar farmácias primeiro
initial_tags = {'amenity': 'pharmacy'}
pois = ox.features.features_from_place(place, tags=initial_tags)

if pois.empty:
    raise ValueError("Nenhum POI encontrado para a categoria tentada farmácia.")

# Listas para armazenar as coordenadas e os detalhes de CADA POI original
poi_coords_original_order = []
poi_details_original_order = []

for idx, row in pois.iterrows():
    # Extrair ponto representativo (centroide se for polígono)
    if row.geometry.geom_type == 'Point':
        y, x = row.geometry.y, row.geometry.x
    else:
        y, x = row.geometry.centroid.y, row.geometry.centroid.x

    poi_coords_original_order.append((y, x))

    # Armazena os detalhes relevantes, incluindo latitude e longitude.
    # Usa um nome genérico se o nome real não existir ou for 'nan'.
    name = row.get('name')
    if not name or (isinstance(name, str) and name.lower() == 'nan'):
        # Tenta ser mais específico com base na tag
        if row['amenity'] == 'pharmacy':
            name_for_display = "Farmácia (sem nome)"
        else:
            name_for_display = f"POI ({row['amenity']})"
    else:
        name_for_display = name

    poi_details_original_order.append({
        'name': name_for_display,
        'amenity': row['amenity'],
        'lat': y,
        'lon': x
    })

# Armazena o número total de POIs encontrados antes da filtragem
total_pois_found = len(poi_coords_original_order)

# ============================================
# 3. Encontrar nós mais próximos dos POIs e mapear detalhes para os nós
# ============================================
latitudes = [p[0] for p in poi_coords_original_order]
longitudes = [p[1] for p in poi_coords_original_order]

# Obtém os nós mais próximos.
nearest_nodes_for_all_pois = ox.distance.nearest_nodes(G_undirected, X=longitudes, Y=latitudes)

# Dicionário para armazenar informações detalhadas para CADA NÓ DE POI ÚNICO.
selected_poi_nodes_info = {}
pharmacy_nodes = [] # Esta lista conterá os IDs de nós únicos que representam os POIs selecionados

for i, node_id in enumerate(nearest_nodes_for_all_pois):
    # Verifica se o nó do POI está realmente no grafo G_undirected (após a filtragem do componente maior)
    if node_id in G_undirected.nodes:
        if node_id not in selected_poi_nodes_info: # Garante nós únicos
            selected_poi_nodes_info[node_id] = poi_details_original_order[i]
            pharmacy_nodes.append(node_id)

# Verifica se há pelo menos 2 POIs no maior componente conectado
if len(pharmacy_nodes) < 2:
    raise ValueError(f"POIs insuficientes para criar um MST (apenas {len(pharmacy_nodes)} pontos no maior componente conectado).")

# Armazena o número de POIs elegíveis após a filtragem do componente maior
pois_eligible_for_mst = len(pharmacy_nodes)

# --- APLICA O LIMITE DE POIs AQUI ---
if len(pharmacy_nodes) > MAX_POIS_FOR_MST:
    print(f"\nLimitando o cálculo do MST a {MAX_POIS_FOR_MST} POIs para fins de teste. POIs originais encontrados: {total_pois_found}, Elegíveis no componente maior: {pois_eligible_for_mst}")
    pharmacy_nodes = pharmacy_nodes[:MAX_POIS_FOR_MST] # Pega apenas os primeiros N POIs

# ============================================
# Impressão dos detalhes dos POIs selecionados
# ============================================
print("\n============================================")
print("POIs selecionados para o cálculo do MST:")
print("============================================")
for node_id in pharmacy_nodes:
    info = selected_poi_nodes_info[node_id]
    print(f"- Nó {node_id}: Nome='{info['name']}', Tipo='{info['amenity']}', Localização=({info['lat']:.4f}, {info['lon']:.4f})")
print("============================================\n")


# ============================================
# 4. Construir um grafo completo com menor rota entre POIs
# ============================================
G_interest = nx.Graph()
for i in range(len(pharmacy_nodes)):
    for j in range(i+1, len(pharmacy_nodes)):
        # Já garantimos que os nós estão no mesmo componente, então shortest_path deve funcionar
        route = nx.shortest_path(G_undirected, pharmacy_nodes[i], pharmacy_nodes[j], weight='length')
        route_length = 0
        for k in range(len(route)-1):
            route_length += G_undirected[route[k]][route[k+1]][0]['length']
        G_interest.add_edge(pharmacy_nodes[i], pharmacy_nodes[j], weight=route_length)

# ============================================
# 5. Calcular o MST
# ============================================
mst_edges = list(nx.minimum_spanning_edges(G_interest, data=True))
total_mst_length = sum([d['weight'] for (u, v, d) in mst_edges])
print("Comprimento total do MST entre os POIs selecionados:", total_mst_length, "metros")

mst_routes = []
for (u, v, d) in mst_edges:
    route = nx.shortest_path(G_undirected, u, v, weight='length')
    mst_routes.append(route)

# ============================================
# 6. Adicionar hospitais ao mapa e imprimir seus detalhes
# ============================================
# Coletar os 10 hospitais mais bem avaliados/maiores em Natal
hospitals_data = ox.features.features_from_place(place, tags={'amenity': 'hospital'})

hospital_coords = []
hospital_details = []
# Limita a 10 hospitais, se houver mais
for idx, row in hospitals_data.head(10).iterrows():
    if row.geometry.geom_type == 'Point':
        y, x = row.geometry.y, row.geometry.x
    else:
        y, x = row.geometry.centroid.y, row.geometry.centroid.x
    
    hospital_coords.append((y, x))
    
    name = row.get('name')
    if not name or (isinstance(name, str) and name.lower() == 'nan'):
        name_for_display = "Hospital (sem nome)"
    else:
        name_for_display = name

    hospital_details.append({
        'name': name_for_display,
        'amenity': 'hospital',
        'lat': y,
        'lon': x
    })

# Encontrar os nós mais próximos para os hospitais
hospital_latitudes = [p[0] for p in hospital_coords]
hospital_longitudes = [p[1] for p in hospital_coords]
nearest_nodes_for_hospitals = ox.distance.nearest_nodes(G_undirected, X=hospital_longitudes, Y=hospital_latitudes)

hospital_nodes = []
# Mapear os detalhes dos hospitais para seus nós e adicioná-los à lista de nós de hospitais
for i, node_id in enumerate(nearest_nodes_for_hospitals):
    if node_id in G_undirected.nodes:
        hospital_nodes.append(node_id)

print("\n============================================")
print("Hospitais encontrados e selecionados:")
print("============================================")
for i, node_id in enumerate(hospital_nodes):
    info = hospital_details[i] # Usa o índice para pegar os detalhes correspondentes
    print(f"- Nó {node_id}: Nome='{info['name']}', Tipo='{info['amenity']}', Localização=({info['lat']:.4f}, {info['lon']:.4f})")
print("============================================\n")


# ============================================
# 7. Plotar o grafo e o MST
# ============================================
fig, ax = ox.plot_graph(
    G_undirected,
    node_size=0,
    edge_color="gray",
    edge_linewidth=0.5,
    show=False,
    close=False,
    bgcolor='white',
    figsize=(10, 9)
)

# Destacar as rotas do MST em vermelho
for route in mst_routes:
    x = [G_undirected.nodes[n]['x'] for n in route]
    y = [G_undirected.nodes[n]['y'] for n in route]
    ax.plot(x, y, color='red', linewidth=2, zorder=4)

# Plotar também os POIs (farmácias/postos/escolas) em azul
poi_x = [G_undirected.nodes[n]['x'] for n in pharmacy_nodes]
poi_y = [G_undirected.nodes[n]['y'] for n in pharmacy_nodes]
ax.scatter(poi_x, poi_y, c='blue', s=80, zorder=5, edgecolor='black')

# Plotar os hospitais em vermelho
hospital_plot_x = [G_undirected.nodes[n]['x'] for n in hospital_nodes]
hospital_plot_y = [G_undirected.nodes[n]['y'] for n in hospital_nodes]
ax.scatter(hospital_plot_x, hospital_plot_y, c='red', s=80, marker='o', zorder=6, edgecolor='black')


# ============================================
# Legenda e Título
# ============================================
# Pega o tipo de amenidade que foi de fato usado
amenity_type_str = initial_tags['amenity'].capitalize() # Ex: 'Pharmacy'

# Traduz o tipo para o português para a legenda
if initial_tags['amenity'] == 'pharmacy':
    poi_label_base = "Farmácias"
else:
    poi_label_base = "POIs"


# Criar legendas personalizadas
red_line_legend = mlines.Line2D([], [], color='red', linewidth=2, linestyle='-', label='Trajeto (MST)')

# Ajusta a legenda para os POIs para ter múltiplas linhas
blue_circle_legend_label = (
    f'{poi_label_base}\n'  # Primeira linha: tipo de POI
    f'Total encontrados: {total_pois_found}\n' # Segunda linha: total encontrado
    f'Selecionados para MST: {len(pharmacy_nodes)}' # Terceira linha: selecionados
)
blue_circle_legend = mlines.Line2D(
    [], [],
    color='blue', # Cor do marcador
    marker='o', # Tipo de marcador (círculo)
    markersize=8, # Tamanho do marcador
    linestyle='None', # Sem linha
    markeredgecolor='black', # Borda do marcador
    label=blue_circle_legend_label
)

# Adiciona legenda para hospitais com a contagem
red_circle_legend = mlines.Line2D(
    [], [],
    color='red',
    marker='o',
    markersize=10,
    linestyle='None',
    markeredgecolor='black',
    label=f'Hospitais: {len(hospital_nodes)}'
)

# --- CORREÇÃO AQUI ---
# O seu cálculo para o comprimento do MST estava invertido para metros e km
# total_mst_length é o valor em metros
# Para KM, divida por 1000
mst_length_km = total_mst_length / 1000

mst_label_text = (
    f'Comprimento Total do MST:\n'
    f'Valor: {total_mst_length:.2f} metros\n' # Formata para 2 casas decimais
    f'Valor: {mst_length_km:.2f} Km'          # Formata para 2 casas decimais
)

# Crie um handle Line2D "fantasma" para exibir o texto do MST na legenda
# Ele não terá linha nem marcador, apenas o texto do label
mst_legend = mlines.Line2D(
    [], [],
    color='none', # Não desenha nenhuma linha
    marker='none', # Não desenha nenhum marcador
    linestyle='None', # Sem estilo de linha
    label=mst_label_text
)


# Adicionar a legenda ao lado esquerdo, ajustando a posição X
# Inclua o novo objeto `mst_legend` nos `handles`
plt.legend(handles=[red_line_legend, blue_circle_legend, red_circle_legend, mst_legend], loc='center left', bbox_to_anchor=(0.9, 0.9), fontsize=10)


# Aumentar o título para ficar um pouco mais alto
plt.title(f"MST entre {poi_label_base} em Natal", fontsize=14, y=1.02)
plt.show()