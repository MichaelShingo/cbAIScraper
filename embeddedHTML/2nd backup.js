<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
  crossorigin=""
/>

<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css"
/>
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css"
/>

<!-- Make sure you put this AFTER Leaflet's CSS -->
<script
  src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
  crossorigin=""
></script>

<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Londrina+Outline&family=Nunito+Sans:ital,opsz,wght@0,6..12,200;0,6..12,400;0,6..12,700;1,6..12,200&display=swap');
  #map {
    height: 100%;
  }
  
  .marker-cluster {
    width: 30px;
    height: 30px;
    border-radius: 100%;
    text-align: center;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.9;
    color: white;
    border: 6px solid rgba(0, 0, 0, 0.4);
  }

  .leaflet-popup-tip, .leaflet-popup-content-wrapper, .leaflet-popup-tip-container, .leaflet-popup-content  {
    background-color: rgba(0,0,0,0);
  }

  .leaflet-popup {
    border-radius: 10px;
    background-color: rgba(0,0,0, 0.85);
    transform: translate(5px, -10px);
  }
  .leaflet-popup-tip-container {
    width: 0;
    height: 0;
    border-left: 9px solid rgba(0,0,0,0);
    border-right: 9px solid rgba(0,0,0,0);
    border-top: 12px solid rgba(0,0,0, 0.85); /* Adjust color and height as needed */
    left: 53.2% !important;
  }

  .leaflet-popup-content-wrapper {
    opacity: 0.75;
    transition: 0.5s;
  }


  .leaflet-popup-content-wrapper p {
    font-family: Nunito Sans;
    font-weight: bold;
    color: white;
  }
  .leaflet-popup-content-wrapper h3 {
    font-family: Nunito Sans;
    color: #ffde59;
  }

  .leaflet-popup-close-button{
    color: #ffde59;
  }

 

</style>

<div id="map"></div>

<script>
  // map styles
  const markerOptions = {
    radius: 8,
    fillColor: "#eeeee4",
    stroke: "#000000 !important",
    color: "#000000",
    weight: 2,
    opacity: 1,
    fillOpacity: 0.7,
    transition: 0.5
  };
  const markerOptionsSaved = {
    radius: 8,
    fillColor: "#f3d355",
    stroke: "#000000 !important",
    color: "#000000",
    weight: 2,
    opacity: 1,
    fillOpacity: 0.7,
    transition: 0.5
  };

  let lastClickedMarker = null;

  

  var clusterOptions = {
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: true,
    zoomToBoundsOnClick: true,
    maxClusterRadius: 40,  // Customize the clustering radius

    // Customize the styles of the cluster circles
    iconCreateFunction: function(cluster) {
      var childCount = cluster.getChildCount();
      var fillColor = '#000000'; // Set your desired fill color here

      return L.divIcon({
        html: '<div style="background-color: ' + fillColor + ';" class="marker-cluster">' + childCount + '</div>',
        className: 'custom-cluster-icon',
        iconSize: L.point(40, 40)
      });
    }
};

   
  //initialize map
  var map = L.map("map").setView([37.239998, -38.734288], 2);
  // set tile layer -   //mapbox://styles/michaelshingo/cllkp5o5r01cn01qsdj880w3v
  //https://api.mapbox.com/styles/v1/michaelshingo/cllkp5o5r01cn01qsdj880w3v/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoibWljaGFlbHNoaW5nbyIsImEiOiJjbGxrcGU0N3kybzlnM21tZ2J2azg5NHcxIn0.QImSA8Uo5Syzct9j5bHazA
  const openStreetMapURL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const mapBoxURL = 'https://api.mapbox.com/styles/v1/michaelshingo/cllkp5o5r01cn01qsdj880w3v/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoibWljaGFlbHNoaW5nbyIsImEiOiJjbGxrcGU0N3kybzlnM21tZ2J2azg5NHcxIn0.QImSA8Uo5Syzct9j5bHazA';
  L.tileLayer(openStreetMapURL, {
    maxZoom: 19,
    minZoom: 2,
    attribution: "© <a href='https://www.mapbox.com/about/maps/'>Mapbox</a> © <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a> <strong><a href='https://www.mapbox.com/map-feedback/' target='_blank'>Improve this map</a></strong>",
  }).addTo(map);
  // Set max bounds 
  var maxBounds = L.latLngBounds(
    L.latLng(-99.516692, -175.277409), // South West
    L.latLng(99.650667, 172.671202)  // North East
  );
  map.setMaxBounds(maxBounds);


  // FUNCTIONS
  function onMarkerClick(e) {
    let zoomLevel = map.getZoom();
    if (zoomLevel < 4) {
      map.flyTo(e.latlng, zoomLevel + 2);
    }
} 
  
// DATA RECEPTION FROM WIX
  window.onmessage = (event) => {

    // need to differentiate between initial location send vs. delete/update event 
    if (event.data) {
      console.log(event.data.messageType);
      locations = event.data.markers;
      

    }

    // create list of geoJSON data
    let lst = [];
    for (let i = 0; i < locations.length; i++) {
      let curObj = {
        type: "Feature",
        properties: {
          oppID: "emptyStr",
          title: '',
          location: '',
          isSaved: false
        },
        geometry: {
          coordinates: [],
          type: "Point",
        },
      };
      curObj.geometry.coordinates = [
        parseFloat(locations[i].position.lng),
        parseFloat(locations[i].position.lat),
      ];
      curObj.properties.oppID = locations[i].id.toString();
      curObj.properties.title = locations[i].title;
      curObj.properties.location = locations[i].location;
      curObj.properties.isSaved = locations[i].isSaved;
      lst.push(curObj);
      // window.parent.postMessage(curObj, "https://www.forthelostcreative.com");
    }

    // add list of objects to geoJSON data obj
    const dataCustom = {
      type: "FeatureCollection",
      features: lst,
    };

    // Create marker cluster group
    const markers = L.markerClusterGroup(clusterOptions);


    let clickedFeature = undefined;
    var geojsonLayer = L.geoJSON(dataCustom, {
      onEachFeature: function (feature, layer) {
        var id = feature.properties.oppID;
        
        const popupContent = `<div class="popup-container"><h3 class="popup-title">${feature.properties.title}</h3> <p class="popup-text">${feature.properties.location}</p></div>`;
        layer.bindPopup(popupContent);
        layer.on("click", function (event) {
          clickedFeature = event.target;
          // clickedFeature.setStyle({fillColor: '#000000'});
          window.parent.postMessage({ 'lat': event.latlng.lat, 'lng': event.latlng.lng, 'oppID': id}, 'https://www.forthelostcreative.com');
        });
        markers.addLayer(layer); // Add the individual layer to the marker cluster group
      },
      pointToLayer: function (feature, latlng){
        // IF FEATURE.ID IS IN USER_OPPS ARRAY, PASS DIFFERENT MARKER OPTIONS
        if (feature.properties.isSaved) {
          console.log('its saved!');
          return L.circleMarker(latlng, markerOptionsSaved)
        } else { return L.circleMarker(latlng, markerOptions) }
      },
    });
    
    // geojsonLayer.on('click', function (event) {
    //   let leafletID = event.target._leaflet_id;
      
    //   console.log(`Leaflet id = ${leafletID}`);
    //   console.log(`event.target._layers = ${JSON.stringify(event.target._layers)}`);
    //   console.log(`is this the thing itself, the marker with style? ${event.target._layers[leafletID]}`);
      
    //   lastClickedMarker = event.target._layers[_leaflet_id]
    //   lastClickedMarker.options.fillColor = "#f3d355";
    //   console.log(event.layer.feature.properties);
    // });

    map.addLayer(markers);

    markers.eachLayer(function(marker) {
      marker.on('click', function(e) {
        let zoomLevel = map.getZoom();
        if (zoomLevel < 4) {
          map.flyTo(e.latlng, zoomLevel + 2);
        }
        lastClickedMarker = this;
        // console.log('last clicked marker:', typeof lastClickedMarker)
        // console.log(lastClickedMarker);

        lastClickedMarker.iconCreateFunction = () => {
            return L.divIcon({
          html: '<div style="background-color: ' + '#000000' + ';" class="marker-cluster"></div>',
          className: 'custom-cluster-icon',
          iconSize: L.point(40, 40)
      });
        }
        
      });
    })

    geojsonLayer.addTo(markers);
  };
</script>
