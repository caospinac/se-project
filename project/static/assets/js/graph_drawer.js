function draw() {
    var nodes = {{nodes}};
    var edges = {{edges}};
    var network = null;

    var container = document.getElementById('mynetwork');

    var data = {
        nodes: nodes,
        edges: edges
    };

    var options = {
        nodes: {
            shape: 'dot',
            font: {
                face: 'Tahoma',
                color: 'white'
            }
        },
        edges: {
            width: 0.15,
            smooth: {
                type: 'continuous'
            }
        },
        interaction: {
            tooltipDelay: 200,
            hideEdgesOnDrag: true
        },
        physics: {
            stabilization: false,
            barnesHut: {
                gravitationalConstant: -10000,
                springConstant: 0.002,
                springLength: 150
            }
        }
    };
    network = new vis.Network(container, data, options);
    network.on('doubleClick', function(params) {
        document.getElementById('selection').innerHTML = 'Selection: ' + nodes[params.nodes].toSource();
    });
}