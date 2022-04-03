# Enterprise Resource Planning (ERP)

The document explores Odoo software integration and implementation of Odoo modules for video conferencing services and locations on the map.

## Odoo

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/1.png?raw=true)

The client and server extensions are packaged as modules in Odoo. 

An addon module for Odoo contains source code files and other assets such as XML files and images.

XML files contain the templates and are processed by the server, translated and sent to the web browser whenever Odoo has loaded the files.

Assets bundles contain JavaScript and CSS files, which are converted into JavaScript and CSS files.

Odoo uses a template engine called QWeb.

Odoo uses the client and server architecture in which clients are web browsers accessing the Odoo instance via RPC (Remote Procedure Call).

Odoo uses PostgreSQL server to run on the host where Odoo instance is installed.

### Debian/Ubuntu

Setup and configure your Linux firewall rules.

The default firewall configuration tool for Ubuntu is Uncomplicated Firewall (ufw).

Configure firewall to open external ports on the host required by Odoo and Jitsi Meet instances.

```

$ ufw allow 8069

$ ufw allow 443

$ ufw allow 80

$ ufw allow 4443/tcp

$ ufw allow 8443/tcp

$ ufw allow 10000:20000/udp

$ ufw allow 5280/tcp

```

### nginx

Install nginx reverse proxy on Linux.

```

$ sudo apt install nginx

```

Configure reverse proxy settings in a file for Odoo and Jitsi Meet located in /etc/nginx/sites-available/ folder and create symbolic link to enable settings on the nginx folder.

```

$ ln -s /etc/nginx/sites-available/<FILE>.conf /etc/nginx/sites-enabled/

```

Jitsi Meet uses HTTP connections only for a reverse proxy to forward HTTPS connections, because direct access to Jitsi Meet by HTTP instead HTTPS leads to errors.

Type the following Linux command to restart the nginx service.

```

$ systemctl reload nginx.service

```

Configure Odoo settings file to set reverse proxy mode in odoo.conf file.

```

proxy_mode = True

```

The configuration odoo.conf file is located in Docker container /etc/odoo directory.

```

[options]

addons_path = /mnt/extra-addons, /odoo/addons

data_dir = /var/lib/odoo

proxy_mode = True

```

PostgreSQL

PostgreSQL manages the database files and accepts connections to the database from Odoo, and performs database actions on behalf of the Odoo.

Install PostgreSQL image from Docker repository.

```

$ docker pull postgres:13

```

Docker PostgreSQL image with 13 tag provides a better data management with optimizations for daily administration and security enhancements.

Create a volume to persistent data storage on the host computer’s directory.

```

$ docker volume create --name <DIRECTORY>

```

Configure the following PostgreSQL variables in .env FILE

```

POSTGRES_DB=postgres

POSTGRES_PASSWORD=<PASSWORD>

POSTGRES_USER=<USER>

PGDATA=/var/lib/postgresql/data/pgdata

HOST=postgres

USER=<USER>

PASSWORD=<PASSWORD>

```
Create postgres Docker container where --env-file flag to pass environment variables and --name flag to define the name of a database.

```

$ docker run -d -v <DIRECTORY>:/var/lib/postgresql/data --env-file .env --name db postgres:13

```

### Docker

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/8.png?raw=true)

Use the docker container run command to start Odoo, PostgreSQL and Jitsi Meet containers fetched from the Docker repository.

Configure Let’s Encrypt environment variables in Odoo .env file.

```

ENABLE_LETSENCRYPT=1

LETSENCRYPT_DOMAIN=<DOMAIN>

HTTPS_PORT=443

PUBLIC_URL=<DOMAIN>

```

Install Odoo image from Docker repository.

```

$ docker pull odoo:14

```

Create Docker container to run Odoo instance with volumes, ports and link options to custom configuration, extra addons, published ports, link to the database and time zone.

```

$ docker run -v <DIRECTORY>/extra-addons:/mnt/extra-addons -v <DIRECTORY>/odoo.conf:/etc/odoo -p 8069:8069 --name odoo --link db:db -e TZ=Asia/Hong_Kong ubuntu:latest date -t odoo:14 -i base

```

Time Zone

```

$ docker exec -u 0 -it <CONTAINER> /bin/bash

# dpkg-reconfigure tzdata

```

### Apps

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/2.png?raw=true)

The addons modules contain location, map and video conferencing logic in Odoo instance on Docker.

### Contacts

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/3.png?raw=true)

Install the modules Geolocation and OpenStreetMap from Apps to assign the location on Contacts.

To view the location of the contact you can click on Location.

### OpenStreetMap

The logic is performed on the Odoo instance, but supporting client features (Leaflet.js interactive maps) are added to the web browsers.

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/4.png?raw=true)

After clicking Geolocalize button in Settings page then Latitude and Longitude are assigned to website page.

Contacts module uses Leaflet.js library and OpenStreetMap to display a marker icon for a location of a contact on world map.

### Contact Us

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/5.png?raw=true)

In Contact Us page we can see our location on the map.

The Geolocation module integrates OpenStreetMap to Odoo Website.

Copy and paste Geolocation module files into your Odoo addons path.

Using maps helps us to add location based services in Odoo.

Add Google Map or Openstreetmap in Odoo Forms to know the exact location of the contacts.

The map marker shows the location.

### Calendar

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/6.png?raw=true)

Jitsi Meet API enables to embed video conferencing functionality in Calendar to provide video meetings for attendees.

The scheduled meetings can be viewed from the calendar view.

The calendar module allows the users to schedule video conferencing with the attendees.

The user can allocate a meeting by video conferencing to date by clicking on the date column. 

### Join Meeting

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/7.png?raw=true)

The Meetings page helps the user to manage meetings with video conferencing and allows user to join video conferencing on a certain date.

Meetings are listed in a Kanban view to show contacts with Join Meeting button.

### Jitsi Meet

Jitsi Meet API library scripts provides video conferencing services integrated into Odoo modules.

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/9.png?raw=true)

Embedding Jitsi Meet API to your Odoo module enables you to host video conferencing meetings.

Download and extract the latest Jitsi Meet release.

```

$ wget https://github.com/jitsi/docker-jitsi-meet/archive/refs/tags/stable-7001.zip

```

Create .env file by copying env.example file.

```

$ cp  env.example .env

```

Jitsi Meet configuration is done modifying environment variables contained in a .env file.

Create passwords for security variables in .env file by running the following bash script.

```

$ ./gen-passwords.sh

```

Create directories for configurations

```

$ mkdir -p ~/.jitsi-meet-cfg/{web/letsencrypt,transcripts,prosody,jicofo,jvb}

```

Copy config.js file to custom-config.js and interface_config.js file to custom-interface_config.js to create your own config files.

Jitsi Meet uses XMPP for signaling and the Prosody setup is provided by Docker container.

By default Jitsi uses the STUN server by Google to set up a connection.

#### Security and Privacy

The meeting rooms only exist while the meeting is actually taking place.

The meeting rooms are created when the first participant joins and they are destroyed when the last one leaves.

If someone joins the same room again, a brand new meeting is created with the same name and there is no connection to any previous meeting that might have been held with the same name.

The random generator offers names for rooms that are easy to remember and read out on a phone call.
 
If you do set a password, then it is your responsibility to communicate it to your peers.

The password will be reset once the last person leaves the room.

Authentication to access a room can be controlled by setting ENABLE_AUTH variable true in .env file.

```

ENABLE_AUTH=1

```

Internal users should be created with prosodyctl utility in the prosody Docker container.

```

$ docker-compose exec prosody /bin/bash

# prosodyctl --config /config/prosody.cfg.lua register <USER> <DOMAIN> <PASSWORD>

```

Restart the services by systemctl command.

```

$ systemctl restart {prosody,jicofo,jitsi-videobridge2,nginx}

```

### Geolocation

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/10.png?raw=true)

The Geolocation module contains elements such as views, XML files, controllers, static data.

Geolocation is the process of finding and providing the exact location of an object. 

Geolocation OpenStreetMap uses Openlayers.

Leaflet is used with OpenStreetMap to provide the map.

Click on the Configuration tab and enable Geo Localization.

Select the OpenStreetMap or Google Map.

Geolocation lets you drag the map marker according to your location in OpenStreetMap.

You can select the Location and Latitude of the address you want to show on Contacts.

HTML (Hypertext Markup Language), CSS (Cascading Style Sheet) and JavaScript are required to add map to our web page. 

The script defines a container element where to load the map.

L.map represents a map object given the DOM (Document Object Model) element. 

The map is divided into tiles using OpenStreetMap to display the map tiles.

The zoom level determines the details of focus. 

A marker is used to highlight a location on a map.

L.marker represents a marker object with determined coordinates (longitude and latitude).

### jitsi_meet

![alt text](https://github.com/jylhakos/miscellaneous/ERP/pictures/11.png?raw=true)

The jitsi_meet module contains models implemented in the Python files, views for the user interface files, data for declaring the model metadata, controllers for the website controllers, static directory for all web assets, security defining access control lists, and i18n where Odoo will look for the translation.

### References

https://www.odoo.com/documentation

https://www.postgresql.org/

https://jitsi.org/

https://www.openstreetmap.org/

https://ubuntu.com/server/docs/security-firewall

https://nginx.org/en/docs/

https://docs.docker.com/engine/install/ubuntu/
