# Deployment

The deployment of applications is done using Docker containers and utilizing container management and orchestration by Kubernetes provided on Google Cloud Platform (GCP).

## Docker

## Using HTTPS

## NGINX

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