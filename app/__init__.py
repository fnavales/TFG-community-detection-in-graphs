# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, jsonify
import json
from igraph import *
import pymongo
from werkzeug import secure_filename
from config import ALLOWED_EXTENSIONS, APP_STATIC

# Define the WSGI application object
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = APP_STATIC

# Create mongo object
client = pymongo.MongoClient()
db = client.TFG
actualDB = None

# Configurations
app.config.from_object('config')

@app.route('/')
def main():
    # with open('app/gameT.json', 'rb') as data:
    #     jsonToPython = json.load(data)

    if (actualDB):
        data = db.networks.find_one({'name':actualDB})["data"]
    else:
        return redirect(url_for('upload_file'))

    return render_template("index.html", json = data) #

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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/load', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
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



