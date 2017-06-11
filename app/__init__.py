# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, jsonify
import json
from igraph import *
import pymongo
from werkzeug import secure_filename
from config import ALLOWED_EXTENSIONS, APP_STATIC
import time
import networkx
import community as nxcom

current_milli_time = lambda: int(round(time.time() * 1000))

# Define the WSGI application object
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = APP_STATIC

# Create mongo object
client = pymongo.MongoClient()
db = client.TFG
actualDB = None

# Configurations
app.config.from_object('config')

@app.route('/', methods=['GET', 'POST'])
def main():
    datasets = None
    if request.method == 'POST':
        upload_file()
        return redirect(url_for('main'))
    else:
        datasets = db.networks.find({},{"_id":0,"name":1})

    if (actualDB):
        data = db.networks.find_one({'name': actualDB})["data"]
    else:
        data = None
    #     return redirect(url_for('upload_file'))


    return render_template("index.html", json = data, ds = datasets)


def parseIgraphToNetworkx(ig):
    G = networkx.Graph(ig.get_edgelist())  # In case you graph is undirected

    if (len(ig.es['size']) > 0):            # Añadimos los pesos de los enlaces
        index = 0
        for u, v, d in G.edges(data=True):
            d['weight'] = ig.es['size'][index]
            index += 1

    return G


@app.route('/comparative')
def comparative():
    listT, listC, listQ = listComparative()

    return render_template("comparative.html", data = listT, data1 = listC, data2 = listQ)

def listComparative():
    listT = []
    listC = []
    listQ = []
    data = db.networks.find_one({'name': actualDB})["data"]

    nodes = data['nodes']
    edges = data['edges']

    # Sort nodes and edges
    nodes = sorted(nodes, key=lambda k: int(k['id']), reverse=False)
    edges = sorted(edges, key=lambda k: int(k['id']), reverse=False)

    # Create the graph
    g = Graph.DictList(nodes, edges, directed=False, vertex_name_attr="id")  # Igraph
    G = parseIgraphToNetworkx(g)  # Networkx

    for i in range(4):
        # Get the communities partition
        t_ini = time.time()
        if (i == 0):
            # NetworX
            # parti = nxcom.best_partition(G,weight='weight', resolution=0.95)
            # comList = parti.values()
            # g = nxcom.modularity(parti, G, weight='weight')
            # Igraph
            community = g.community_multilevel(weights=g.es['size'], return_levels=False)
            comList = community.membership
            q = community.q
            name = "Lovaina"
            # for list in g.community_multilevel(weights=g.es['size'], return_levels=True):
            #     print list
        elif (i == 1):
            community = g.community_leading_eigenvector(weights=g.es['size'])
            comList = community.membership
            q = community.q
            name = "Greedy Newman"
        elif (i == 2):
            community = g.community_edge_betweenness(weights=g.es['size']).as_clustering()
            comList = community.membership
            q = community.q
            name = "Edge Betweenness"
        elif (i == 3):
            community = g.community_label_propagation(weights=g.es['size'])
            comList = community.membership
            q = community.q
            name = "Label Propagation"

        t_fin = time.time()
        time_op = (t_fin - t_ini) *1000
        listT.append([name,float(time_op)])
        listC.append([name,int(len(community))])
        listQ.append([name,community.q])
    return listT, listC, listQ

@app.route('/apply_alg/<int:index>', methods=['GET', 'POST'])
def applyAlgDectCommunity(index):
    if request.method == 'POST':
        if (actualDB):
            data = db.networks.find_one({'name':actualDB})["data"]

            nodes = data['nodes']
            edges = data['edges']

            # Sort nodes and edges
            nodes = sorted(nodes, key=lambda k: int(k['id']), reverse=False)
            edges = sorted(edges, key=lambda k: int(k['id']), reverse=False)

            # Create the graph
            g = Graph.DictList(nodes, edges, directed=False, vertex_name_attr="id")     # Igraph
            G = parseIgraphToNetworkx(g)                                                # Networkx

            # Get the communities partition
            t_ini = time.time()
            if (index == 0):
                # NetworX
                # parti = nxcom.best_partition(G,weight='weight', resolution=0.95)
                # comList = parti.values()
                # g = nxcom.modularity(parti, G, weight='weight')
                # Igraph
                community = g.community_multilevel(weights=g.es['size'], return_levels=False)
                # print community
                comList = community.membership
                q = community.q
                # for list in g.community_multilevel(weights=g.es['size'], return_levels=True):
                #     print list
            elif (index == 1):
                community = g.community_leading_eigenvector(weights=g.es['size'])
                comList = community.membership
                q = community.q
            elif (index == 2):
                community = g.community_edge_betweenness(weights=g.es['size']).as_clustering()
                comList = community.membership
                q = community.q
            elif (index == 3):
                community = g.community_label_propagation(weights=g.es['size'])
                comList = community.membership
                q = community.q

            t_fin = time.time()
            time_op = (t_fin - t_ini) * 1000

            # print db.networks.update_one(
            #     {'name': actualDB},
            #     {'$set': {'data': data}},
            #     upsert=True  # Create the file if not exits
            # )
            return json.dumps({"comunidades": comList,
                               "tiempo": round(time_op, 3),
                                "modularidad": round(q, 3)
            })
        else:
            return redirect(url_for('upload_file'))

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/load', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            print file
            save_file(file)

            # file.save(os.path.join(APP_STATIC, filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            return redirect(url_for('main'))
    else:
        datasets = db.networks.find({},{"_id":0,"name":1})
    return render_template("load_file.html", ds=datasets)

@app.route('/setDB/<filename>')
def setDefaultDB(filename):
    global actualDB
    if ('.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS):
        actualDB = secure_filename(filename)
        print actualDB
        return redirect(url_for('main'))
    return redirect(url_for('upload_file'))

def save_file(file):
    # Save network as a MongoDB file
    added =  db.networks.update_one(
        {'name': secure_filename(file.filename)},
        {'$set': {'data': json.load(file)}},
        upsert = True  # Create the file if not exits
    )

    global actualDB
    if (added != None):
        actualDB = secure_filename(file.filename)



