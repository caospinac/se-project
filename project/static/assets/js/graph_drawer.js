function openInNewTab(url) {
  var win = window.open(url, '_blank');
  win.focus();
}

function draw(nodes, edges) {
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
        if (nodes[params.nodes].DI != null){
            openInNewTab("http://dx.doi.org/" + nodes[params.nodes].DI);
        } else {
            // window.alert("It cant by open this article, beacause this article has not a doi");
            openInNewTab("https://www.youtube.com/watch?v=9UZbGgXvCCA");
        }
    });
}