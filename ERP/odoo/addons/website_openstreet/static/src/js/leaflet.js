odoo.define('website_openstreet.leaflet', function (require) {
"use strict";

  require('web.dom_ready');

  var lat = 22.542883,
      lng = 114.062996,
      enable = true,
      size = 400;

  $.get( "/map/config", function(data) {

      var data_json = JSON.parse(data);

      lat = data_json['lat'];

      lng = data_json['lng'];

      enable = data_json['enable'];

      size = data_json['size'];

      if (enable && $('#mapid').length){

          var point = new L.LatLng(lat, lng);

          var map = L.map('mapid').setView(point, 15);

          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '© <a href="http://openstreetmap.org">OpenStreetMap</a>'
          }).addTo(map);

          var redIcon = new L.Icon({
                              iconUrl: 'website_openstreet/static/src/images/red.png',
                              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                              iconSize: [25, 41],
                              iconAnchor: [12, 41],
                              popupAnchor: [1, -34],
                              shadowSize: [41, 41]
              });

          var marker = L.marker([lat, lng], {icon: redIcon});

          marker.addTo(map);

          $('#mapid').css('width',size);

          $('#mapid').css('height',size);

          // Disable Google Symbol Icon
          $('.img-fluid').hide();
      }
  });

 });

