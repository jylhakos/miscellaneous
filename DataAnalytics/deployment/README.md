# Deployment

The deployment of applications is done using Docker containers and utilizing container management and orchestration by Kubernetes provided on Google Cloud Platform (GCP).

## Docker

```

$ cd frontend

$ docker build -t frontend .

```

Docker-compose lets you create and run multi-container Docker apps. 

Docker provides a host network which lets containers share your host’s networking stack.

Containers are launched with the host network by adding the --network=host flag

```

$ docker run -p 192.168.9.97:3002:3002 --network=host --env HTTPS=true

```
If you’re using Docker Compose, modify your container’s service definition to include the network_mode field.

The docker-compose.yaml file is a YAML file defining services, networks, and volumes for Docker applications.

The context defines a path to a directory containing a Dockerfile.

From your project directory, type [docker compose command](https://docs.docker.com/engine/reference/commandline/docker/) to build the images for applications from the Dockerfiles.

```

$ docker-compose build

```

## Using HTTPS

You can run npm command to start the React app in development mode and set the HTTPS environment variable to true to serve pages over HTTPS, then start the development server.

```

$ HTTPS=true npm start

```

To set SSL certificate, set the SSL_CRT_FILE and SSL_KEY_FILE environment variables to the path of the certificate and the key file.

## NGINX

The sites-available folder is for storing all of the vhost configurations.

The sites-enabled folder contains symlinks to files in the sites-available folder.

To configure Nginx for HTTPS, the ssl parameter must be enabled on listening sockets in the server block, and the locations of the server certificate and private key files need to be specified.

Secure HTTP traffic between [Nginx](https://www.nginx.com/resources/wiki/start/topics/examples/full/) and upstream servers, using SSL/TLS encryption.

```

server {
    listen              443 ssl;
    server_name         backend;

    ssl_certificate_key /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/certs/server.key;

    location /api {
        proxy_pass http://<URL>;
        #...
    }
}

```

Set HttpOnly, SameSite, and secure flags on cookies in Set-Cookie upstream response headers.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/DataAnalytics/deployment/PREFLIGHT.png?raw=true)

Figure: Preflight

### References

Docker https://docs.docker.com/

Nginx https://nginx.org/en/docs/

Axios https://axios-http.com/docs/intro

GCP https://cloud.google.com/