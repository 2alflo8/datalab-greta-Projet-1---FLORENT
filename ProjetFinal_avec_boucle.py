#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 20:39:29 2019

@author: Nicolas, Florent, Maxime
"""
import folium
import requests
from pandas.io.json import json_normalize
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Url des données de l'API
stockR=requests.get(url="https://services1.arcgis.com/HzzPcgRsxxyIZdlU/arcgis/rest/services/mes_centre_val_de_loire_mensuel_poll_princ_1/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json").json()

# DataFrame...
result=json_normalize(stockR['features'])
df=pd.DataFrame(result)


    
# Notre vue sur la carte
carte = folium.Map(location = [47.5, 1.6833])
# Overlay qui représente le contour de la région centre
overlay_region = f'/home/shikshik/Téléchargements/Projet 1/CARTE_PROJET/overlay_region.json'

# Je met l'overlay sur la carte...
folium.GeoJson(
    overlay_region,  
    name='Région Centre-Val de Loire'
).add_to(carte)

# Je sais pas plus...
folium.LayerControl().add_to(carte)

# Tri par ville 
gpville = df.groupby(['attributes.nom_com', 'attributes.nom_polluant']).mean()
posVille = df.groupby(['attributes.nom_com']).mean()


#Recupéraption des noms de ville dans une liste
indexVille=posVille.index


Polluants_type_colors = {    
  'NO': 'darkblue',
  'PM10': 'darkgreen',
  'O3': 'darkviolet',
  'NO2': 'skyblue',
  'PM2.5': 'red',
  'CO': 'black',
}



# Créé la map
for i in range(len(indexVille)):  
  
    myCity = indexVille[i]
    graphSave=myCity+"_graph.jpg"#variable pour enregistrer le graph et le recup dans la popup
    dfGraph=df[(df["attributes.nom_com"] == myCity)]#création de la data
    dfGraph=dfGraph.sort_values(by = 'attributes.date_debut')
    #cré du graph
    f,ax1 = plt.subplots(figsize =(30,5))
    myGraph = sns.pointplot(
            x='attributes.date_debut',
            y='attributes.valeur',
            hue="attributes.nom_polluant",
            palette=Polluants_type_colors,
            data=dfGraph,
            alpha=0.8)
    
    myGraph.legend(title='Polluants')
    plt.title(myCity, fontsize = 15,color='darkblue')
    plt.xlabel('Dates',fontsize = 15,color='blue')
    plt.ylabel('µg/m3',fontsize = 15,color='blue')
    plt.grid()
    myGraph.figure.savefig(graphSave, dpi=60)

    html_Ville=folium.Html("<img src={}></img>".format(graphSave), script=True)
    popupVille = folium.Popup(html_Ville, max_width=100)
    
    #Ajout des marker
    folium.Marker(
      location=[posVille.iloc[i]['attributes.y_wgs84'], posVille.iloc[i]['attributes.x_wgs84']],
      icon=folium.Icon(icon='bar-chart'),
      popup=popupVille,
      tooltip="Cliquer pour plus d'infos",
   ).add_to(carte)

carte.save('Carte résumé.html')



gpPol= df.groupby(['attributes.nom_polluant']).mean()
indexPol=gpPol.index
radius=[50,3,3,0.5,3,3]

# Crée les 6 autres cartes
for i in range(len(indexPol)):
    
    polluant=df[(df["attributes.nom_polluant"] == indexPol[i])]
    polluant=polluant.groupby(['attributes.nom_com']).mean()
    polI=polluant.index
    nomCarte="carte"+indexPol[i]
    test=nomCarte+".html"
    nomCarte=folium.Map(location = [47.383333, 0.683333])

    for g in range(len(polluant)):       
        myCity = polI[g]
        graphSave=myCity+"_graph.jpg"
        html_Ville=folium.Html("<img src={}></img>".format(graphSave), script=True)
        popupVille = folium.Popup(html_Ville, max_width=100)
        
        folium.CircleMarker(
                location=[polluant.iloc[g]['attributes.y_wgs84'], polluant.iloc[g]['attributes.x_wgs84']],
                radius=polluant.iloc[g]['attributes.valeur']*radius[i],
                popup=popupVille,
                tooltip="Cliquez pour plus d'infos",
                color='darkblue',
                fill=True,
                fill_color='darkblue'
                
                ).add_to(nomCarte)
    nomCarte.save(test)    


