# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, jsonify
import json
from igraph import *
import pymongo
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, APP_STATIC
import time
import networkx

current_milli_time = lambda: int(round(time.time() * 1000))

# Define the WSGI application object
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = APP_STATIC

print(os.environ)
# Create mongo object
# TODO: The problem here is that we need to set the correct database host (first argument), it's the IP of the DB container
# client = pymongo.MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017) 
client = pymongo.MongoClient('mongodb://db:27017/')
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


    return render_template("index.html", json = data, ds = datasets)


def parseIgraphToNetworkx(ig):
    G = networkx.Graph(ig.get_edgelist())  # In case you graph is undirected

    if (len(ig.es['size']) > 0):            # Añadimos los pesos de los enlaces
        index = 0
        for u, v, d in G.edges(data=True):
            d['weight'] = ig.es['size'][index]
            index += 1

    return G


@app.route('/comparative', methods=['GET', 'POST'])
def comparative():
    datasets = db.networks.find({}, {"_id": 0, "name": 1})
    dbNames = []
    for d in datasets:
        dbNames.append(d['name'])

    if request.method == 'POST':
        algInd =  [int(i) for i in request.form.getlist('algoritmos')]
        bdName = request.form['bd']
        listT, listC, listQ = listComparative(algInd, bdName)
        return render_template("comparative.html", ds = dbNames, data = listT, data1 = listC, data2 = listQ)

    return render_template("comparative.html", ds = dbNames)

@app.route('/doc')
def doc():
    return render_template("doc.html")

def listComparative(algInd, bdName):
    listT = []
    listC = []
    listQ = []

    data = db.networks.find_one({'name': bdName})["data"]

    nodes = data['nodes']
    edges = data['edges']

    # Sort nodes and edges
    nodes = sorted(nodes, key=lambda k: int(k['id']), reverse=False)
    edges = sorted(edges, key=lambda k: int(k['id']), reverse=False)

    # Create the graph
    g = Graph.DictList(nodes, edges, directed=False, vertex_name_attr="id")  # Igraph

    for i in algInd:
        # Get the communities partition
        t_ini = time.time()
        if (i == 0):
            # Igraph
            community = g.community_multilevel(weights=g.es['size'], return_levels=False)
            comList = community.membership
            q = community.q
            name = "Louvain"
        elif (i == 1):
            community = g.community_fastgreedy(weights=g.es['size']).as_clustering()
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
        elif (i == 4):
            community = g.community_walktrap(weights=g.es['size']).as_clustering()
            comList = community.membership
            q = community.q
            name = "Walktrap"

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

            comList = []
            comDict = {}
            # Get the communities partition
            t_ini = time.time()
            if (index == 0):
                for ind, val in enumerate(g.community_multilevel(weights=g.es['size'], return_levels=True)):
                    intervalo = (time.time() - t_ini)
                    comDict["louvain"+str(ind)] = {
                        "lista": val.membership,
                        "tiempo": round(intervalo * 1000, 3),
                        "mod": round(val.q, 3)
                    }

            elif (index == 1):
                community = g.community_fastgreedy(weights=g.es['size']).as_clustering()
                comList = community.membership
                q = community.q
            elif (index == 2):
                community = g.community_edge_betweenness(weights=g.es['size'], directed=False).as_clustering()
                comList = community.membership
                q = community.q
            elif (index == 3):
                community = g.community_label_propagation(weights=g.es['size'])
                comList = community.membership
                q = community.q
            elif (index == 4):
                community = g.community_walktrap(weights=g.es['size']).as_clustering()
                comList = community.membership
                q = community.q

            t_fin = time.time()
            time_op = (t_fin - t_ini) * 1000

            if (len(comDict) > 0):
                return json.dumps(comDict)

            return json.dumps({"lista": comList,
                               "tiempo": round(time_op, 3),
                                "mod": round(q, 3)
            })

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('main'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/load', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            save_file(file)

            return redirect(url_for('main'))

@app.route('/setDB/<filename>')
def setDefaultDB(filename):
    global actualDB
    if ('.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS):
        actualDB = secure_filename(filename)
    return redirect(url_for('main'))

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
