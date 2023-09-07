 if (feature.properties.isSaved) {
          console.log('its saved!');
          return L.circleMarker(latlng, markerOptionsSaved)
        } else { return L.circleMarker(latlng, markerOptions) }