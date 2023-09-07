geojsonLayer.on('click', function (event) {
      lastClickedMarker = event.layer.feature.properties.marker;
      console.log(feature.properties);
      lastClickedMarker.setStyle({
        fillColor: "#f3d355"
      })
      
    })