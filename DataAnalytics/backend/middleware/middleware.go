package middleware

import (
	"context"
	"log"
	"os"
	"time"
	"net/http"
	"github.com/gin-gonic/gin"
)

var SECRET_KEY = os.Getenv("SECRET_KEY")

type SignedClaims struct{
	Name string
	jwt.StandardClaims
}

func ValidateToken(signedToken string) (claims *SignedClaims, msg string){

	token, err := jwt.ParseWithClaims(
		signedToken,
		&SignedClaims{},
		func(token *jwt.Token) (interface{}, error) {
			return []byte(SECRET_KEY), nil
		},
	)

	if err!=nil{
		msg = err.Error()
		return
	}

	claims, ok := token.Claims.(*SignedClaims)

	if !ok{
		msg = "the token is invalid"
		msg = err.Error()
		return
	}

	if claims.ExpiresAt < int64(time.Now().Local().Unix()){
		msg = "token has expired"
		msg = err.Error()	
	}

	return claims,msg
}

func GenerateToken(name string) (signedToken string, signedRefreshToken string, err error){
	
	claims := &SignedClaims{
		Name: name,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Local().Add(time.Hour * time.Duration(24)).Unix(),
		},
	}

	refreshClaims := &SignedClaims{
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Local().Add(time.Hour * time.Duration(186)).Unix(),
		},
	}

	signedToken, err = jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(SECRET_KEY))
	if err!=nil{
		log.Panic(err.Error())
		return
	}

	signedRefreshToken, err = jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims).SignedString([]byte(SECRET_KEY))
	if err!=nil{
		log.Panic(err.Error())
		return
	}

	return
}	

func Authorization() gin.HandlerFunc{

	return func(ctx *gin.Context) {

		clientToken := ctx.Request.Header.Get("token")

		if clientToken==""{
			ctx.JSON(http.StatusInternalServerError, gin.H{"Error":"No authorization header"})
			ctx.Abort()
			return
		}

		claims, err := ValidateToken(clientToken)

		if err!=""{

			ctx.JSON(http.StatusInternalServerError, gin.H{"Error":err})

			ctx.Abort()

			return
		}

		ctx.Set("Name", claims.Name)

		ctx.Next()	
	}
}