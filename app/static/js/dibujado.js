/** Permite cambiar niveles de corte en el dendograma (sólo para algunos algoritmos) **/
function changeLevel(id) {
    if (communityList !== undefined) {
        networkData = communityList[id];
        networkData["lista"].forEach(function (e, id) {
            if (Object.keys(nodes._data)[0] == 1) {
                id += 1;
            }
            nodes.update([{id: id, group: parseInt(e)}]);
        });
        nodeContent.innerHTML = "Seleccione un nodo";
        setCommunityData(networkData.tiempo, networkData.mod);
        allNodes = nodes.get({returnType: "Object"});
    }
}

/** Petición para calcular comunidades **/
function updateIndex(value) {

    if (value >= 0){
        $.ajax({
            type : 'POST',
            url : $SCRIPT_ROOT + '/apply_alg/'+value,
            success : function(data) {
                var networkData = JSON.parse(data);

                valuesa = Object.keys(networkData).map(function(key){
                    return networkData[key];
                });
                if (valuesa.length < 3) {
                    document.getElementById('parametrosDiv').style.display = "block";
                    $('label[for=r1]').html("&nbsp;Nivel 2");
                    $('label[for=r2]').html("&nbsp;Nivel 1");
                    communityList = valuesa;
                    if (document.getElementById('r1').checked) {
                        networkData = valuesa[0];

                    }else{
                        networkData = valuesa[1];
                    }
                } else {
                    document.getElementById('parametrosDiv').style.display = "none";
                }

                networkData["lista"].forEach(function (e,id) {
                    if(Object.keys(nodes._data)[0] == 1){
                        id +=1;
                    }
                    nodes.update([{id:id, group:parseInt(e)}]);
                });
                nodeContent.innerHTML = "Seleccione un nodo";
                setCommunityData(networkData.tiempo,networkData.mod);
                allNodes = nodes.get({returnType:"Object"});
            }
        });
        network.on("click",neighbourhoodHighlight);

    }
}

/** Pintar el grafo **/
function redrawAll() {
    var container = document.getElementById('mynetwork');
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        autoResize: true,
        width: '100%',
        height: '99%',
        nodes: {
            borderWidth: 1,
            shape: 'dot',
            scaling: {
                min:3,
                max: 40,
                label: {
                    enabled: true,
                    min: 10,
                    max: 25,
                    drawThreshold: 5,
                    maxVisible: 20
                }
            },
            font: {
                face: 'Tahoma'
            }
        },
        edges: {
            width: 0.15,
            color: {inherit: 'from'},
            smooth: {
                type: 'continuous'
            }
        },
        groups:{
            useDefaultGroups: true
        },
        interaction: {
            hideEdgesOnDrag: true,
            multiselect: true
        },
        physics: {
            barnesHut: {
                gravitationalConstant: -4000,
                springConstant: 0.01,
                springLength: 200
            },
            forceAtlas2Based: {
                gravitationalConstant: -26,
                centralGravity: 0.005,
                springLength: 230,
                springConstant: 0.18
            },
            maxVelocity: 100,
            solver: 'barnesHut',
            timestep: 0.35,
            stabilization: {
                enabled:true,
                iterations:4000,
                updateInterval:25
            }
        }
    };
    network = new vis.Network(container, data, options);

    // Obtener copia de los nodos para marcar vecinos
    allNodes = nodes.get({returnType:"Object"});


    network.on("stabilizationProgress", function(params) {
        var maxWidth = 496;
        var minWidth = 20;
        var widthFactor = params.iterations/params.total;
        var width = Math.max(minWidth,maxWidth * widthFactor);

        document.getElementById('bar').style.width = width + 'px';
        document.getElementById('text').innerHTML = Math.round(widthFactor*100) + '%';
    });
    network.once("stabilizationIterationsDone", function() {
            document.getElementById('text').innerHTML = '100%';
            document.getElementById('bar').style.width = '496px';
            document.getElementById('loadingBar').style.opacity = 0;
            // really clean the dom element
            setTimeout(function () {document.getElementById('loadingBar').style.display = 'none';}, 500);
    });
}

function neighbourhoodHighlight(params) {
    // if something is selected:
    if (params.nodes.length > 0) {
        var selectedNode = params.nodes[0];
        var data = nodes.get(selectedNode); // get the data from selected node
        nodeContent.innerHTML = JSON.stringify(data, undefined, 3); // show the data in the div
            highlightActive = true;
            var i,j;
            var degrees = 1;

            // mark all nodes as hard to read.
            for (var nodeId in allNodes) {
            allNodes[nodeId].color = 'rgba(200,200,200,0.5)';
            if (allNodes[nodeId].hiddenLabel === undefined) {
                allNodes[nodeId].hiddenLabel = allNodes[nodeId].label;
                allNodes[nodeId].label = undefined;
            }
            }
            var connectedNodes = network.getConnectedNodes(selectedNode);
            var allConnectedNodes = [];

            // get the second degree nodes
            for (i = 1; i < degrees; i++) {
            for (j = 0; j < connectedNodes.length; j++) {
                allConnectedNodes = allConnectedNodes.concat(network.getConnectedNodes(connectedNodes[j]));
            }
            }

            // all second degree nodes get a different color and their label back
            for (i = 0; i < allConnectedNodes.length; i++) {
            allNodes[allConnectedNodes[i]].color = 'rgba(150,150,150,0.75)';
            if (allNodes[allConnectedNodes[i]].hiddenLabel !== undefined) {
                allNodes[allConnectedNodes[i]].label = allNodes[allConnectedNodes[i]].hiddenLabel;
                allNodes[allConnectedNodes[i]].hiddenLabel = undefined;
            }
            }

            // all first degree nodes get their own color and their label back
            for (i = 0; i < connectedNodes.length; i++) {
            allNodes[connectedNodes[i]].color = undefined;
            if (allNodes[connectedNodes[i]].hiddenLabel !== undefined) {
                allNodes[connectedNodes[i]].label = allNodes[connectedNodes[i]].hiddenLabel;
                allNodes[connectedNodes[i]].hiddenLabel = undefined;
            }
            }

            // the main node gets its own color and its label back.
            allNodes[selectedNode].color = undefined;
            if (allNodes[selectedNode].hiddenLabel !== undefined) {
            allNodes[selectedNode].label = allNodes[selectedNode].hiddenLabel;
            allNodes[selectedNode].hiddenLabel = undefined;
            }
        }
    else if (highlightActive === true) {
        // reset all nodes
        for (var nodeId in allNodes) {
            allNodes[nodeId].color = undefined;
            if (allNodes[nodeId].hiddenLabel !== undefined) {
                allNodes[nodeId].label = allNodes[nodeId].hiddenLabel;
                allNodes[nodeId].hiddenLabel = undefined;
            }
        }
        highlightActive = false;
        $('.myCheckbox').prop('checked', true);

        Object.keys(getCommunityColor()).forEach(function(element) {
            if (communityChecked.indexOf(parseInt(element)) < 0 ){
                communityChecked.push(parseInt(element));
            }
        });
    }

    // transform the object into an array
    var updateArray = [];
    for (nodeId in allNodes) {
        if (allNodes.hasOwnProperty(nodeId)) {
        updateArray.push(allNodes[nodeId]);
        }
    }
    nodes.update(updateArray);
    }

function communityHighlight() {
    // if something is selected:
    if (communityChecked.length > -1) {
        var i,j;

        // mark all nodes as hard to read.
        for (var nodeId in allNodes) {
            if (communityChecked.indexOf(allNodes[nodeId].group) < 0){
                allNodes[nodeId].color = 'rgba(200,200,200,0.5)';
                if (allNodes[nodeId].hiddenLabel === undefined) {
                    allNodes[nodeId].hiddenLabel = allNodes[nodeId].label;
                    allNodes[nodeId].label = undefined;
                }

            }else {
                allNodes[nodeId].color = undefined;
                if (allNodes[nodeId].hiddenLabel !== undefined) {
                    allNodes[nodeId].label = allNodes[nodeId].hiddenLabel;
                    allNodes[nodeId].hiddenLabel = undefined;
                }
            }
        }
    }

    // transform the object into an array
    var updateArray = [];
    for (nodeId in allNodes) {
        if (allNodes.hasOwnProperty(nodeId)) {
        updateArray.push(allNodes[nodeId]);
        }
    }
    nodes.update(updateArray);
    }


function getCommunityColor(){
    return network["groups"]["groups"];
}

function enlacesInOut(nodo) {
    var connectedNodes = network.getConnectedNodes(nodo.id);
    var entrada = 0;
    var salida = 0;

    connectedNodes.forEach(function (e) {
        if (nodo.group === (nodes.get(e)).group) {
            entrada++;
        }else {
            salida++;
        }
    });
    nodes.update([{id:nodo.id, grados:{in:entrada, out:salida}}]);
    return {com: nodo.group,
            grados: {
            in: entrada,
            out: salida}
    };
}


function setCommunityData(tiempo, modularidad) {
    var valoresCom = {};
    var colores = getCommunityColor();
    var numberOfCom = [];

    nodes.forEach(function (element) {
        if(numberOfCom.indexOf(element.group) < 0){
            numberOfCom.push(element.group);
        }
        var aux = enlacesInOut(element);
        if (!valoresCom[aux.com]) {
            valoresCom[aux.com] = aux.grados;
        }else{
            valoresCom[aux.com].in += aux.grados.in;
            valoresCom[aux.com].out += aux.grados.out;
        }
    });

    communityChecked = numberOfCom;

    var html = "";
    Object.keys(colores).slice(0,numberOfCom.length).forEach(function(key, index) {
        var total = valoresCom[key].in + valoresCom[key].out;
        var dentro = (valoresCom[key].in/total)*100;
        var fuera = (valoresCom[key].out/total)*100;

        html += '<input class="myCheckbox" onchange="updateCheckedList('+index+')" type="checkbox" value="'+index+'" checked> <a style="cursor:pointer;" onclick="selectNodesFromColor('+index+')"><span style="background:' + this[key].color.background + '">&nbsp;&nbsp;</span> Comunidad '
            + (index+1) + '</a><a href="#com' + index + '" data-toggle="collapse"><i class="material-icons">arrow_drop_down</i></a><div class="collapse" id="com' + index + '">' +
            '#N: ' + (nodes.get()).filter(function (el) {return el.group === index;}).length +  ', #E: ' + valoresCom[key].in + '<br>G<sub>in</sub>: ' + dentro.toPrecision(2) + '%, G<sub>out</sub>: ' + fuera.toPrecision(2) + '%' +
            '</div><br>';
    }, colores);

    communitiesContent.innerHTML =  html +
                                    "<br>Tiempo: " + tiempo + " ms<br>" +
                                    "Modularidad: " + modularidad;
}

function updateCheckedList(param) {
    var ind = communityChecked.indexOf(param);
    if (ind < 0){
        communityChecked.push(param);
    }else{
        communityChecked.splice(ind,1);
    }
    communityChecked.sort();
    communityHighlight();
}

function selectNodesFromColor(ind) {
    var newNodes = (nodes.get()).filter(function (el) {
            return el.group === (ind);
    }).map(function(el) {
        return el.id;
    }).sort();

    var options = {
        scale: 0.35,
        locked: true,
        animation: {
            duration: 1000,
            easingFunction: 'easeInQuad'
        }
    };
    network.focus(newNodes[Math.floor(Math.random()*newNodes.length)],options);
}
