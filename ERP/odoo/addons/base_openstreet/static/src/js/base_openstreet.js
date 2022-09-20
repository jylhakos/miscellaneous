odoo.define("base_openstreet.base_openstreet", function (require) {
  "use strict";

  var fieldRegistry = require("web.field_registry");
  var abstractField = require("web.AbstractField");

  var base_openstreet = abstractField.extend({
    template: "base_openstreet_template",
    start: function () {
      var self = this;
      this._super();
      self._initMap();
    },
    _initMap: function () {
      var self = this
      $(document).ready(function () {
        setTimeout(() => {
          //var lat = self.recordData.lat;
          //var lng = self.recordData.lng;

          var lat = self.recordData.lat;
          var lng = self.recordData.lng;

          console.log('lat', lat, 'lng', lng)
          
          if (!lat && !lng) {
            lat = 0.000000000000;
            lng = 0.000000000000;
          }

          var redIcon = new L.Icon({
                              iconUrl: '/base_openstreet/static/src/images/red.png',
                              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                              iconSize: [25, 41],
                              iconAnchor: [12, 41],
                              popupAnchor: [1, -34],
                              shadowSize: [41, 41]
              });

          var map = L.map('mapid').setView([lat, lng], 15);
          
          L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
          }).addTo(map);

          var edit = self.mode == "edit" ? true : false;

          //var marker = L.marker([lat, lng], { draggable: edit }).addTo(map);

          var marker = L.marker([lat, lng], {icon: redIcon, draggable: edit }).addTo(map);
          
          marker.on("dragend", function (e) {
            var latlng = e.target._latlng;

            console.log('e.target._latlng', e.target._latlng)

            self.trigger_up("field_changed", {
              dataPointID: self.dataPointID,
              changes: {
                lat: latlng.lat,
                lng: latlng.lng,
              },
              viewType: self.viewType,
            });
          });
          
          if (edit) {
            var geocode = L.Control.geocoder({
              defaultMarkGeocode: false,
            }).addTo(map);
            
            geocode.on("markgeocode", function (e) {
              var lat = e.geocode.center.lat;
              var lng = e.geocode.center.lng;
              
              map.flyTo([lat, lng]);
              marker.setLatLng(new L.LatLng(lat, lng));
              self.trigger_up("field_changed", {
                dataPointID: self.dataPointID,
                changes: {
                  lat: lat,
                  lng: lng,
                },
                viewType: self.viewType,
              });
            });
          }

          var interval = setInterval(() => {
            if (map && map._size.x > 0){
              clearInterval(interval);
            } else if (!document.getElementById("mapid")) {
              clearInterval(interval);
            }
            window.dispatchEvent(new Event("resize"));
          }, 500);
        }, 100);

      });
    },
    isSet: function () {
      return true;
    },
  });
  
  fieldRegistry.add("base_openstreet", base_openstreet);
});
