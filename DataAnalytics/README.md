# Data Analytics

The project contains the front-end (client) and the back-end (server) applications deployed on Docker.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/DataAnalytics/CHARTJS.png?raw=true)

Figure: Visualization of collected data by Chart.js library

## JWT

JSON web token (JWT) allows a back-end (server) to authenticate the users, without storing any information about them on the back-end itself.

The signature is the key part of the JWT.

Download the Golang JWT package using the Linux command.

```

$ go get github.com/golang-jwt/jwt

$ go get .

$ go run main.go

```

The JWT must be added to HTTP Header if the web browser accesses protected resources on the back-end.

### Cookie

The Cookie HTTP request header contains stored [HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) associated with the back-end.

The back-end sends the HTTP cookie to a user's web browser.

The HTTP cookie with the HttpOnly attribute is inaccessible using JavaScript on the web browser.

Cookies with [SameSite=None](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite) must set the Secure attribute or the cookie will be blocked.

The HTTP cookie with the Secure attribute is only sent to the back-end with an encrypted request over the HTTPS protocol.

```

http.SetCookie(c.Writer, &http.Cookie{
    Name:     name,
    Value:    url.QueryEscape(value),
    MaxAge:   maxAge,
    Path:     path,
    Domain:   domain,
    SameSite: c.sameSite,
    Secure:   secure,
    HttpOnly: httpOnly,
  })

```

### How to send HttpOnly cookies?

Use the httpOnly flag to prevent JavaScript from reading it on the web browser.

```

Access-Control-Allow-Credentials: true

```

### How to add HttpOnly cookies in Axios?

The withCredentials options assigns httpOnly cookies in the HTTP requests.

```

axios.get(<URL>, { withCredentials: true });

```
If the web browser receives an 401 Unauthorized response from the back-end, then the React app can handle this by requesting to refresh the httpOnly cookie.

Whenever httpOnly cookie expires, then the React app uses axios interceptors to refresh the token.

## Cross-Origin Resource Sharing (CORS)

The browsers restrict cross-origin HTTP requests initiated from scripts to follow the same origin policy.

An origin is defined as a combination of URL, host name, and port number. 

CORS is an HTTP header based mechanism that allows a back-end to indicate any origins (domain) other than its own from which a web browser should permit loading resources.

Download and install package for [Gin](https://github.com/gin-gonic/gin/blob/master/context.go) middleware and handler to enable CORS support.

```

$ go get github.com/gin-contrib/cors

```

In order to enable CORS, the back-end adds Access-Control-Allow-Origin header to the response.

```

package main

import (
  "time"
  "github.com/gin-contrib/cors"
  "github.com/gin-gonic/gin"
)

func main() {

  router := gin.Default()

  router.Use(cors.New(cors.Config{
    AllowOrigins:     []string{"https://foo.com", "https://bar.com", "http://localhost"},
    AllowMethods:     []string{"GET", "POST"},
    AllowHeaders:     []string{"Origin"},
    ExposeHeaders:    []string{"Content-Length"},
    AllowCredentials: true,
    AllowOriginFunc: func(origin string) bool {
      return origin == "https://github.com"
    },
    MaxAge: 12 * time.Hour,
  }))

  router.Run()
}

```

### Preflight

A preflight request is a CORS request using three HTTP request headers: Access-Control-Request-Method, Access-Control-Request-Headers, and the Origin header.

The web browser sends a preflight request and the back-end responds with Access-Control-Allow-Origin in the header.

A preflight request is automatically issued by a web browser and the web browser will check for Access-Control-Allow-Origin parameters on the received preflight response for the following request.

## Deployment

Deploying React (front-end) and Golang (back-end) applications as the Docker containers and securing the connections for containerized applications with Nginx reverse proxy.

### References

Go programming language https://go.dev/doc/

How to use Gin? https://gin-gonic.com/docs/

GORM https://gorm.io/docs/

CORS https://github.com/gin-contrib/cors

Preflight https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request

JWT https://datatracker.ietf.org/doc/html/rfc7519

Cookie https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cookie

React components for Chart.js https://react-chartjs-2.js.org/
