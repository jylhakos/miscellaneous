package middleware

import (
	//"context"
	"fmt"
	"log"
	"os"
	"time"
	//"strings"
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt"
)

var SECRET_KEY = os.Getenv("SECRET_KEY")

type SignedClaims struct {
	Username string
	jwt.StandardClaims
}

func GenerateToken(username string) (signedToken string, err error){
//func GenerateTokens(username string) (signedToken string, signedRefreshToken string, err error) {

	claims := &SignedClaims {
		Username: username,
		StandardClaims: jwt.StandardClaims {
			//ExpiresAt: time.Now().Local().Add(time.Hour * time.Duration(24)).Unix(),
			ExpiresAt: time.Now().Local().Add(time.Minute * time.Duration(30)).Unix(),
			//ExpiresAt: time.Now().Local().Add(time.Second * time.Duration(120)).Unix(),
		},
	}

	/*
	refreshClaims := &SignedClaims {
		StandardClaims: jwt.StandardClaims {
			ExpiresAt: time.Now().Local().Add(time.Hour * time.Duration(186)).Unix(),
		},
	}
	*/

	signedToken, err = jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(SECRET_KEY))
	
	if err != nil {
		log.Panic(err.Error())
		fmt.Errorf("Error: ", err)
		return
	}

	//signedRefreshToken, err = jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims).SignedString([]byte(SECRET_KEY))
	
	//if err != nil {
	//	log.Panic(err.Error())
	//	return
	//}

	return
}	

func ValidateToken(signedToken string) (claims *SignedClaims, msg string) {

	fmt.Println("ValidateToken", signedToken)

	token, err := jwt.ParseWithClaims(
		signedToken,
		&SignedClaims{},
		func(token *jwt.Token) (interface{}, error) {
			return []byte(SECRET_KEY), nil
		},
	)

	fmt.Println("token", token, err)

	if err != nil {
		fmt.Println("Error: ", err)
		msg = err.Error()
		fmt.Errorf("Error: ", msg)
		return
	}

	claims, ok := token.Claims.(*SignedClaims)

	if !ok {
		msg = "Token is invalid"
		msg = err.Error()
		fmt.Errorf("Error: ", msg)
		return
	}

	fmt.Println("claims.ExpiresAt", claims.ExpiresAt, "time.Now().Local().Unix()", int64(time.Now().Local().Unix()))

	if claims.ExpiresAt < int64(time.Now().Local().Unix()) {
		msg = "Token is expired"
		msg = err.Error()
		fmt.Errorf("Error: ", msg)
		return
	}

	return
}

func Authorization() gin.HandlerFunc {

	return func(ctx *gin.Context) {

		//bearerToken := ctx.Request.Header.Get("Authorization")

		//cookie, _ := ctx.Request.Cookie("access_token")

		//fmt.Println("Authorization", bearerToken, "Cookie", accessToken)

		cookie, err := ctx.Request.Cookie("cookie")

		if err != nil {
			fmt.Errorf("Cookie", err)
			ctx.Abort()
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error":"StatusUnauthorized"})
			return
		}

		cookieStr := cookie.Value

		fmt.Println("cookieStr", cookieStr)

		/*
		bearerStr := "Bearer"

		tokenString := bearerToken

		if strings.Contains(bearerToken, bearerStr) == true {
				tokenString = strings.Split(bearerToken," ")[1]
			}
		}
		*/
		
		if len(cookieStr) == 0 {
		//if cookieStr == "" {
			fmt.Errorf("Cookie", err)
			ctx.Abort()
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error":"StatusUnauthorized"})
			return
		}

		claims, msg := ValidateToken(cookieStr)

		if msg != "" {
			fmt.Errorf("ValidateToken",msg)
			ctx.Abort()
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error":msg})
			return
		}

		ctx.Set("Username", claims.Username)
		
		ctx.Next()	
	}
}