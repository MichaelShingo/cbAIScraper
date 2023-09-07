L.geoJSON(dataCustom, {
            pointToLayer: function (feature, latlng){
                return L.circleMarker(latlng, markerOptions)
            }
        }).addTo(map);






        pointToLayer: function (feature, latlng){
            return markers.addLayer(L.circleMarker(latlng, markerOptions))
        },