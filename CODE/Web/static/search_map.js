let db_ = document.querySelector("#db_name").innerText;
console.log(db_)

// map initialization - leaflet library used
if (db_.includes("Porto")) {
    var map = L.map('map').setView([41.156521, -8.619722], 12); // Porto
} else if (db_.includes("Chicago")) {
    var map = L.map('map').setView([41.980166, -87.660084], 12); // chicago
} else if (db_.includes("NYC")) {
    var map = L.map('map').setView([40.723681, -74.000516], 12); // nyc
} else if (db_.includes("T-drive")) {
    var map = L.map('map').setView([39.9, 116.3], 12); // T-drive
} else {
    var map = L.map('map').setView([39.9, 116.3], 12); 
}



var coordinate_meta;

// Open street map is set
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);


// leaflet draw
// put db feature here
var drawnFeatures = new L.FeatureGroup();
map.addLayer(drawnFeatures);

// put this for drawing tool which would be displayed on the left
var drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnFeatures,
        remove: true
    },

    // format
    draw: {
        polygon: {
            shapeOptions: {
                color: 'purple'
            },
        },

        polyline: {
            shapeOptions: {
                color: 'red'
            },
        },

        rectangle: {
            shapeOptions: {
                color: 'green'
            },
        },

        circle: {
            shapeOptions: {
                color: 'steelblue'
            },
        },
    },
});

map.addControl(drawControl);

// after drawing
map.on("draw:created", function(e){
    var type = e.layerType;
    var layer = e.layer;

    coordinate_meta = layer.toGeoJSON(); // last coordinate data save

    layer.bindPopup(`<p>${JSON.stringify(layer.toGeoJSON())}</p>`)
    drawnFeatures.addLayer(layer);
});

// after editing the pictures
map.on("draw:edited", function(e){
    var type = e.layerType;
    var layers = e.layers;

    layers.eachLayer(function(layer){
        console.log(layer)
    })
})

// get coordinates
function getCoordinates() {
    var coordinates = coordinate_meta.geometry.coordinates;
    var left_below = coordinates[0][0];
    var right_upper = coordinates[0][2];
    var points = "(" + left_below[1] + ", " + left_below[0] + "), (" + right_upper[1] + ", " + right_upper[0] + ")";
    return points;
  }

function getPoints() {
    var points = getCoordinates();
    document.getElementById('points').value = points;
}