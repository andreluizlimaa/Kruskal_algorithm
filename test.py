import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

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
      

# ============================================
# 1. Obter o grafo da cidade de Natal
# ============================================
place = "Natal, Rio Grande do Norte, Brazil"
G = ox.graph_from_place(place, network_type='drive')

# Converte para não-direcionado mantendo o tipo MultiGraph
G_undirected = to_undirected_multigraph(G)
      

# ============================================
# 2. Obter POIs de interesse (hospitais como exemplo) E PREPARAR INFORMAÇÕES DETALHADAS
# ============================================
initial_tags = {'amenity': 'hospital'}
pois = ox.features.features_from_place(place, tags=initial_tags)

# Se não encontrar hospitais, tentar escolas
if pois.empty: # Use .empty para verificar se o GeoDataFrame está vazio
    print("Nenhum hospital encontrado. Tentando escolas...")
    initial_tags = {'amenity': 'school'} # Atualiza a tag
    pois = ox.features.features_from_place(place, tags=initial_tags)

if pois.empty:
    raise ValueError("Nenhum POI encontrado para as categorias tentadas.")

# Listas para armazenar as coordenadas e os detalhes (nome, tipo, lat, lon) de CADA POI original
poi_coords_original_order = [] # Armazena (y, x)
poi_details_original_order = [] # Armazena {'name': ..., 'amenity': ..., 'lat': ..., 'lon': ...}

for idx, row in pois.iterrows():
    # Extrair ponto representativo (centroide se for polígono)
    if row.geometry.geom_type == 'Point':
        y, x = row.geometry.y, row.geometry.x
    else:
        y, x = row.geometry.centroid.y, row.geometry.centroid.x

    poi_coords_original_order.append((y, x))
    
    # Armazena os detalhes relevantes, incluindo latitude e longitude.
    # Usa 'POI (tipo)' como nome se o nome real não existir.
    name = row.get('name', f"POI ({row['amenity']})") 
    poi_details_original_order.append({
        'name': name, 
        'amenity': row['amenity'],
        'lat': y,  # Adiciona latitude
        'lon': x   # Adiciona longitude
    })

      
# ============================================
# 3. Encontrar nós mais próximos dos POIs E MAPEAR DETALHES PARA OS NÓS
# ============================================
latitudes = [p[0] for p in poi_coords_original_order]
longitudes = [p[1] for p in poi_coords_original_order]

# Obtém os nós mais próximos. Esta lista 'nearest_nodes_for_all_pois' manterá a ordem dos POIs de entrada.
nearest_nodes_for_all_pois = ox.distance.nearest_nodes(G_undirected, X=longitudes, Y=latitudes)

# Dicionário para armazenar informações detalhadas para CADA NÓ DE POI ÚNICO.
# Se múltiplos POIs originais mapearem para o mesmo nó, o primeiro encontrado será o que terá seus detalhes armazenados.
selected_poi_nodes_info = {} 
hospital_nodes = [] # Esta lista conterá os IDs de nós únicos que representam os POIs selecionados

for i, node_id in enumerate(nearest_nodes_for_all_pois):
    if node_id not in selected_poi_nodes_info: # Adiciona apenas se este nó ainda não foi processado
        selected_poi_nodes_info[node_id] = poi_details_original_order[i]
        hospital_nodes.append(node_id) # Adiciona à lista de nós únicos para o MST

if len(hospital_nodes) < 2:
    raise ValueError("POIs insuficientes para criar um MST (menos de 2 pontos).")
      
# ============================================
# IMPRESSÃO DOS DETALHES DOS POIs SELECIONADOS
# ============================================
print("\n============================================")
print("POIs selecionados para o cálculo do MST:")
print("============================================")
for node_id in hospital_nodes:
    info = selected_poi_nodes_info[node_id]
    # Formata a localização para 4 casas decimais para melhor legibilidade
    print(f"- Nó {node_id}: Nome='{info['name']}', Tipo='{info['amenity']}', Localização=({info['lat']:.4f}, {info['lon']:.4f})")
print("============================================\n")


# ============================================
# 4. Construir um grafo completo com menor rota entre POIs
# ============================================
G_interest = nx.Graph()
for i in range(len(hospital_nodes)):
    for j in range(i+1, len(hospital_nodes)):
        route = nx.shortest_path(G_undirected, hospital_nodes[i], hospital_nodes[j], weight='length')
        route_length = 0
        for k in range(len(route)-1):
            route_length += G_undirected[route[k]][route[k+1]][0]['length']  # Como é MultiGraph, usar [0]
        G_interest.add_edge(hospital_nodes[i], hospital_nodes[j], weight=route_length)
      

# ============================================
# 5. Calcular o MST
# ============================================
mst_edges = list(nx.minimum_spanning_edges(G_interest, data=True))
total_mst_length = sum([d['weight'] for (u, v, d) in mst_edges])
print("Comprimento total do MST entre os POIs selecionados:", total_mst_length, "metros")
      
# ============================================

mst_routes = []
for (u, v, d) in mst_edges:
    route = nx.shortest_path(G_undirected, u, v, weight='length')
    mst_routes.append(route)

# Plotar o grafo base
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

# Plotar também os POIs (hospitais) em azul
poi_x = [G_undirected.nodes[n]['x'] for n in hospital_nodes]
poi_y = [G_undirected.nodes[n]['y'] for n in hospital_nodes]
ax.scatter(poi_x, poi_y, c='blue', s=80, zorder=5, edgecolor='black')

# ============================================
# Legenda e Título
# ============================================
# Criar legendas personalizadas
red_line_legend = mlines.Line2D([], [], color='red', linewidth=2, linestyle='-', label='Trajeto (MST)')
blue_circle_legend = ax.scatter([], [], c='blue', s=80, edgecolor='black', label='POI Hospital') # O label pode ser 'POI Hospital/Escola' dependendo do caso

# Adicionar a legenda ao lado direito, mais alta
plt.legend(handles=[red_line_legend, blue_circle_legend], loc='center left', bbox_to_anchor=(1.02, 0.9), fontsize=10)

# Aumentar o título para ficar um pouco mais alto
plt.title("MST entre POIs (hospitais) em Natal", fontsize=14, y=1.02)
plt.show()