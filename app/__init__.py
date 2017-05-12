# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for
import json
from igraph import *

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

@app.route('/')
def main():
    with open('app/gameT.json', 'r') as data:
        jsonToPython = json.load(data,'ascii')
    print jsonToPython

    return render_template("index.html", json = jsonToPython)#, nodes = jsonToPython["nodes"], edges = jsonToPython["edges"])

@app.route('/alg/<int:index>')
def alg(index):
    applyAlgDectCommunity(index)
    return redirect(url_for('main'))

def applyAlgDectCommunity(index):
    with open('app/gameT.json', 'r') as data:
        jsonToPython = json.load(data)

    nodes = jsonToPython['nodes']
    edges = jsonToPython['edges']

    # Sort nodes and edges
    nodes = sorted(nodes, key=lambda k: int(k['id']), reverse=False)
    edges = sorted(edges, key=lambda k: int(k['id']), reverse=False)

    # Create the graph
    g = Graph.DictList(nodes, edges, directed=False, vertex_name_attr="id")
    # print g

    # Get the communities partition
    if (index == 0):
        community = g.community_multilevel(weights=g.es['size'])
    elif (index == 1):
        community = g.community_leading_eigenvector(weights=g.es['size'])
    elif (index == 2):
        community = g.community_edge_betweenness(weights=g.es['size']).as_clustering()
    elif (index == 3):
        community = g.community_label_propagation(weights=g.es['size'])

    # print community
    # print g.vs[0]['color']

    # Change vertex color according to community partition
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'grey', 'cyan', 'olive', 'purple']

    for ind in range(len(community.membership)):
        g.vs[ind]['color'] = colors[community.membership[ind]]
        nodes[ind]['color'] = colors[community.membership[ind]]
        nodes[ind]['size'] = float(nodes[ind]["attributes"]["Grado"])
    # print g.vs.get_attribute_values('color')

    # print edges[0]

    red = {"nodes": nodes, "edges": edges}
    # print red["nodes"]

    with open('red'+str(index)+'.json', 'wb') as data:
        json.dump(red, data, indent=4)

    return True

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# if __name__ == "__main__":
# 	app.run(port=5000, debug=True)




