
    // We use the leaflet library
    var map = L.map('map').setView([41.1572675, -8.644179999999999], 13); 
    var coordinate_meta;

    // Open street map tile
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    var s2cell = [
     {'type': 'Feature', 'properties': {'status': 'retrieved'}, 'geometry': {'type': 'LineString', 'coordinates': [[-8.639847, 41.159826], [-8.640351, 41.159871], [-8.642196, 41.160114], [-8.644455, 41.160492], [-8.646921, 41.160951], [-8.649999, 41.161491], [-8.653167, 41.162031], [-8.656434, 41.16258], [-8.660178, 41.163192], [-8.663112, 41.163687], [-8.666235, 41.1642], [-8.669169, 41.164704], [-8.670852, 41.165136], [-8.670942, 41.166576], [-8.66961, 41.167962], [-8.668098, 41.168988], [-8.66664, 41.170005], [-8.665767, 41.170635], [-8.66574, 41.170671]]}},
     {'type': 'Feature', 'properties': {'status': 'retrieved'}, 'geometry': {'type': 'LineString', 'coordinates': [[-8.640108, 41.146803], [-8.640828, 41.149728], [-8.64333, 41.152329], [-8.645517, 41.155704], [-8.647893, 41.159241], [-8.649072, 41.162904], [-8.645193, 41.165469], [-8.641143, 41.167854], [-8.637408, 41.170455], [-8.6328, 41.171787], [-8.628561, 41.172687], [-8.62434, 41.173191], [-8.619561, 41.17365], [-8.614899, 41.174226], [-8.610354, 41.174235], [-8.606448, 41.17221], [-8.601921, 41.171256], [-8.59734, 41.171589], [-8.593254, 41.170806], [-8.58978, 41.168556], [-8.586216, 41.166675], [-8.582832, 41.16546], [-8.581689, 41.163498], [-8.582121, 41.164434], [-8.583957, 41.163237]]}},
     {'type': 'Feature', 'properties': {'status': 'retrieved'}, 'geometry': {'type': 'LineString', 'coordinates': [[-8.630568, 41.154795], [-8.63064, 41.154813], [-8.631495, 41.1543], [-8.632521, 41.152905], [-8.632539, 41.152815], [-8.633241, 41.152599], [-8.63586, 41.152428], [-8.637237, 41.152761], [-8.637264, 41.152788], [-8.638929, 41.153166], [-8.641692, 41.15385], [-8.644383, 41.154489], [-8.646048, 41.153985], [-8.645634, 41.153301], [-8.645418, 41.153148], [-8.645391, 41.15223], [-8.645454, 41.152122], [-8.645436, 41.152131], [-8.645355, 41.152284], [-8.645652, 41.153346], [-8.646075, 41.15412], [-8.64711, 41.154264], [-8.648082, 41.154615], [-8.64855, 41.156397], [-8.649513, 41.158791], [-8.648766, 41.15934], [-8.650287, 41.1606], [-8.650242, 41.161311], [-8.649027, 41.161185], [-8.646804, 41.160861], [-8.646786, 41.160861], [-8.646399, 41.161203], [-8.645247, 41.161464], [-8.643897, 41.161257], [-8.643753, 41.161995], [-8.64306, 41.164038], [-8.642763, 41.164947], [-8.642709, 41.164956], [-8.641737, 41.164983]]}},
     {'type': 'Feature', 'properties': {'status': 'retrieved'}, 'geometry': {'type': 'LineString', 'coordinates': [[-8.630649, 41.154984], [-8.631837, 41.15403], [-8.632539, 41.152806], [-8.634141, 41.152545], [-8.6373, 41.152797], [-8.640846, 41.153643], [-8.644005, 41.154552], [-8.647488, 41.154282], [-8.6481, 41.155083], [-8.648163, 41.156622], [-8.648082, 41.156658], [-8.648082, 41.156676], [-8.648073, 41.156703], [-8.648082, 41.156694]]}},
     {'type': 'Feature', 'properties': {'status': 'retrieved'}, 'geometry': {'type': 'LineString', 'coordinates': [[-8.639838, 41.159799], [-8.639901, 41.159772], [-8.640315, 41.159808], [-8.640342, 41.159826], [-8.640729, 41.159403], [-8.641314, 41.15754], [-8.641926, 41.155533], [-8.642358, 41.154255], [-8.642385, 41.154138], [-8.640243, 41.153436], [-8.636724, 41.152617], [-8.634429, 41.152194], [-8.634942, 41.151123], [-8.63784, 41.150259], [-8.641854, 41.149314], [-8.64468, 41.15124], [-8.642016, 41.151231], [-8.640486, 41.147937], [-8.639496, 41.14377], [-8.637399, 41.13945], [-8.635347, 41.134932], [-8.635662, 41.129748], [-8.635941, 41.124267], [-8.634456, 41.119209], [-8.629263, 41.116014], [-8.623062, 41.114358], [-8.61678, 41.112963], [-8.610669, 41.111604], [-8.605764, 41.109102], [-8.603145, 41.105151], [-8.599149, 41.101578], [-8.594433, 41.098419], [-8.590338, 41.09508], [-8.588313, 41.092353], [-8.589483, 41.09301], [-8.588241, 41.094081], [-8.584623, 41.093874], [-8.58483, 41.093253], [-8.584479, 41.095134], [-8.586198, 41.096286], [-8.587044, 41.096412]]}},
     {'type': 'Feature', 'properties': {'status': 'querying'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[-8.638086, 41.15255], [-8.650274, 41.15255], [-8.650274, 41.161985], [-8.638086, 41.161985], [-8.638086, 41.15255]]]}}

];

    L.geoJSON(s2cell, {
        style: function(feature) {
            switch (feature.properties.status) {
                case 'querying': return {color: "#ff0000"};  // Entire querying space
                case 'retrieved': return {color: "#0000ff"}; // retrived space
            }
        }
    }).addTo(map);
    