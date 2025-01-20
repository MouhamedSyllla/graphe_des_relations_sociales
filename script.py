


import pandas as pd
import geopandas as gpd
import contextily as ctx
from itertools import combinations

# 1. Chargement des données
data = pd.read_csv("foursquare_data.csv")  # Remplacez avec le chemin réel du fichier
data['timestamp'] = pd.to_datetime(data['timestamp'])

# 2. Préparation des données
data = data.sort_values(by=['VenueID', 'timestamp'])  # Trier par lieu et temps

# 3. Identification des interactions
user_pairs = []

for venue, group in data.groupby('VenueID'):
    group = group.sort_values(by='timestamp')
    for i, user1 in enumerate(group['UserID']):
        for j, user2 in enumerate(group['UserID']):
            if i >= j:
                continue
            time_diff = abs((group.iloc[i]['timestamp'] - group.iloc[j]['timestamp']).total_seconds())
            if time_diff <= 3600:  # 1 heure
                user_pairs.append((user1, user2))

# Compter les interactions
from collections import Counter
pair_counts = Counter(user_pairs)

# Filtrer pour garder seulement les paires avec >= 10 interactions
filtered_pairs = [pair for pair, count in pair_counts.items() if count >= 10]

# 4. Préparer les données pour la visualisation
top_5_pairs = filtered_pairs[:5]
top_5_locations = data[data['UserID'].isin([user for pair in top_5_pairs for user in pair])]

# 5. Visualisation des interactions sur la carte
gdf = gpd.GeoDataFrame(
    top_5_locations,
    geometry=gpd.points_from_xy(top_5_locations.longitude, top_5_locations.latitude),
    crs="EPSG:4326"
)

# Reprojection et ajout de fond de carte
gdf = gdf.to_crs(epsg=3857)
ax = gdf.plot(figsize=(12, 8), alpha=0.6, edgecolor='k')
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

# Ajouter des annotations pour les 5 paires
for pair in top_5_pairs:
    pair_data = gdf[gdf['UserID'].isin(pair)]
    for _, row in pair_data.iterrows():
        ax.annotate(f"User {row['UserID']}", (row.geometry.x, row.geometry.y), fontsize=8)

# Afficher la carte
import matplotlib.pyplot as plt
plt.show()
