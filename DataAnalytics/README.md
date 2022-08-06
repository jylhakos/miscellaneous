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

The Cookie HTTP request header contains stored HTTP cookies associated with the back-end.

The back-end sends the HTTP cookie to a user's web browser.

The HTTP cookie with the Secure attribute is only sent to the back-end with an encrypted request over the HTTPS protocol.

The HTTP cookie with the HttpOnly attribute is inaccessible using JavaScript on the web browser.

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

CORS is an HTTP header based mechanism that allows a back-end to indicate any origins (domain) other than its own from which a web browser should permit loading resources.

In order to enable CORS the back-end should add Access-Control-Allow-Origin header to the response.

### Preflight

The web browser sends a preflight request and the back-end responds with Access-Control-Allow-Origin in the header.

A web browser will check for Access-Control-Allow-Origin parameters on the received preflight response for the following request.

### References

Go programming language https://go.dev/doc/

How to use Gin? https://gin-gonic.com/docs/

GORM https://gorm.io/docs/

CORS https://github.com/gin-contrib/cors

JWT https://datatracker.ietf.org/doc/html/rfc7519

Cookie https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cookie

React components for Chart.js https://react-chartjs-2.js.org/
