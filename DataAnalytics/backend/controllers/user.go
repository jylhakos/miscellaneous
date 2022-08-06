// controllers/user.go

package controllers

import (
	"fmt"
	"os"
	//"context"
	"log"
	"net/http"
	//"strconv"
	"time"
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"golang.org/x/crypto/bcrypt"
	"github.com/golang-jwt/jwt"
	"server/models"
	"server/database"
	"server/middleware"
)

var validate = validator.New()

var SECRET_KEY = os.Getenv("SECRET_KEY")

type SignedClaims struct {
	Username string
	jwt.StandardClaims
}

func HashPassword(password string) string {

	pass, err := bcrypt.GenerateFromPassword([]byte(password),14)

	if err != nil{
		fmt.Errorf("HashPassword", err)
		log.Panic(err.Error())
	}

	return string(pass)
}

func VerifyPassword(userPassword string, providedPassword string)(bool, string) {

	err := bcrypt.CompareHashAndPassword([]byte(providedPassword), []byte(userPassword))
	
	check := true
	
	msg := ""

	if err !=nil{
		check = false
		msg = "Verify Password Not Successful."
		fmt.Errorf("VerifyPassword", err)
	}

	return check, msg
}

func Register(ctx *gin.Context) {
//func Register() gin.HandlerFunc {

	//return func(ctx *gin.Context) {

		//var dctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

		var user models.User

		if err := ctx.BindJSON(&user); err != nil{
			fmt.Errorf("BindJSON", err)
			ctx.Abort()
			ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		validationErr := validate.Struct(user)

		if validationErr != nil{
			fmt.Errorf("Validation", validationErr)
			ctx.Abort()
			ctx.JSON(http.StatusBadRequest, gin.H{"error":validationErr.Error()})
			return
		}

		fmt.Println("Password",user.Password)

		user.Password = HashPassword(user.Password)

		//access_token, refresh_token, _ := middleware.GenerateTokens(user.Username)
		
		//token, _ := middleware.GenerateTokens(user.Username)

		//fmt.Println("AccessToken",access_token,"RefreshToken",refresh_token)

		//user.AccessToken = access_token

		//user.RefreshToken = refresh_token

		db := database.GetDB()

		err := db.Create(&user).Error

		if err != nil{
			fmt.Errorf("Error", err)
			ctx.Abort()
			ctx.JSON(http.StatusConflict, gin.H{"error":err})
			return
		}

		ctx.JSON(http.StatusOK, gin.H{"status": "success"})
		ctx.Next()
	//}
}

func Login(ctx *gin.Context) {
//func Login() gin.HandlerFunc {
	
	//return func(ctx *gin.Context) {
		
		//var dctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

		var user models.User

		var foundUser models.User
		
		if err := ctx.BindJSON(&user); err !=nil {
			ctx.Abort()
			ctx.JSON(http.StatusBadRequest, gin.H{"Error": err.Error()})
			return
		}

		fmt.Println("Login", user.Username, user.Password)

		db := database.GetDB()

		err := db.Where("username = ?", user.Username).First(&foundUser).Error

		if err != nil {
			fmt.Errorf("StatusUnauthorized", err)
			ctx.Abort()
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error":err.Error()})
			return
		}

		passwordIsValid, msg := VerifyPassword(user.Password, foundUser.Password)
		
		if !passwordIsValid {
			fmt.Errorf("StatusUnauthorized", user.Password)
			ctx.Abort()
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error":msg})
			return
		}

		if len(foundUser.Username) == 0 {
			fmt.Errorf("Username not found", user.Username)
			ctx.Abort()
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error":msg})
			return
		}

		//access_token, refresh_token, _ := middleware.GenerateTokens(foundUser.Username)

		token, _ := middleware.GenerateToken(foundUser.Username)

		fmt.Println("token", token)

		//foundUser.RefreshToken = refresh_token

		timeout := 60*30

		//ctx.SetCookie("access_token", access_token, timeout, "/", "localhost", false, true)
	
		//ctx.SetCookie("refresh_token", refresh_token, timeout, "/", "localhost", false, true)

		ctx.SetCookie("token", token, timeout, "/", "localhost", false, true)
		ctx.JSON(http.StatusOK, gin.H{"status": "success"})
		ctx.Next()
	//}
}

func Refresh(ctx *gin.Context) {

	fmt.Println("Refresh", ctx)

	cookie, _ := ctx.Request.Cookie("token")

	fmt.Println("Cookie", cookie, cookie.Name, cookie.Value)

	cookieStr := cookie.Value

	fmt.Println("cookieStr", cookieStr)

	claimsValid, msg := middleware.ValidateToken(cookieStr)

	if msg != "" {
		fmt.Errorf("Error", msg)
		ctx.Abort()
		ctx.JSON(http.StatusNotAcceptable, gin.H{"Error":msg})
		return
	}

	fmt.Println("claimsValid.ExpiresAt", claimsValid.ExpiresAt)

	//if time.Unix(claimsValid.ExpiresAt, 0).Sub(time.Now()) > 30*time.Second {
	if time.Unix(claimsValid.ExpiresAt, 0).Sub(time.Now().Local()) > 10*time.Minute {
		ctx.Abort()
		ctx.JSON(http.StatusTooEarly, gin.H{"status": "Too Early"})
		return
	}

	claims := &SignedClaims {
		StandardClaims: jwt.StandardClaims {
			ExpiresAt: time.Now().Local().Add(time.Minute * time.Duration(30)).Unix(),
		},
	}

	token, err := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(SECRET_KEY))

	if err != nil {
		ctx.Abort()
		ctx.JSON(http.StatusInternalServerError, gin.H{"Error":"StatusInternalServerError"})
		return
	}

	fmt.Println("refresh_token", token)

	timeout := 60*30

	ctx.SetCookie("token", token, timeout, "/", "localhost", false, true)
	ctx.JSON(http.StatusOK, gin.H{"status": "success"})
	ctx.Next()
}