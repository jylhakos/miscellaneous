package controllers

import (
	"context"
	"log"
	"net/http"
	"strconv"
	"time"
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"golang.org/x/crypto/bcrypt"
	"server/database"
	"server/middleware"
	"server/models"
)

var validate = validator.New()

func HashPassword(password string) string{

	pass, err := bcrypt.GenerateFromPassword([]byte(password),14)

	if err!=nil{

		log.Panic(err.Error())
	}

	return string(pass)
}

func VerifyPassword(userPassword string, providedPassword string)(bool, string){

	err := bcrypt.CompareHashAndPassword([]byte(providedPassword), []byte(userPassword))
	
	check := true
	
	msg := ""

	if err!=nil{

		msg = "Name or password is wrong."

		check = false
	}

	return check, msg
}

func Register() gin.HandlerFunc{

	return func(ctx *gin.Context) {

		var dctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)
		
		var user models.User
		
		if err := ctx.BindJSON(&user); err!=nil{
			defer cancel()
			ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		validationErr := validate.Struct(user)
		
		if validationErr!=nil{
			defer cancel()
			ctx.JSON(http.StatusBadRequest, gin.H{"error":validationErr.Error()})
			return
		}

		count, err := userCollection.CountDocuments(dctx, bson.M{"email":user.Email})
		
		defer cancel()
		
		if err!=nil{
			log.Panic(err)
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":"error occured while checking for email"})
			return
		}
		
		password := HashPassword(*user.Password)
		
		user.Password = &password

		defer cancel()
		
		if err!=nil{
			log.Panic(err)
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":"error occured while checking for phone number"})
			return
		}

		if count>0 || phoneCount>0{
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":"this email or phone number already exits"})
			return
		}

		user.ID = primitive.NewObjectID()

		user.User_id = user.ID.Hex()

		token, refreshToken, _ := middleware.GenerateToken(*Name, user.User_id)

		user.Token = &token

		user.Refresh_token = &refreshToken

		//resultInsertionNumber, insertError :=userCollection.InsertOne(dctx, user)

		if insertError!=nil{
			msg := "user item was not created"
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":msg})
			return
		}

		defer cancel()

		ctx.JSON(http.StatusOK, gin.H{
			"status":"success",
			"insertion number": resultInsertionNumber,
		})
	}
}

func Login() gin.HandlerFunc{
	
	return func(ctx *gin.Context) {
		
		var dctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)
		
		var user models.User
		
		var foundUser models.User
		
		if err := ctx.BindJSON(&user); err!=nil{
			defer cancel()
			ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		err := userCollection.FindOne(dctx, bson.M{"email":user.Email}).Decode(&foundUser)
		
		defer cancel()
		
		if err!=nil{
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":"email or password is incorrect"})
			return
		}

		passwordIsValid, msg := VerifyPassword(*user.Password, *foundUser.Password)
		
		if !passwordIsValid {
			ctx.JSON(http.StatusInternalServerError,gin.H{"error":msg})
			return
		}

		if foundUser.Email == nil{
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":"user not found"})
		}

		token, refreshToken, _ := GenerateToken(*foundUser.Email,*foundUser.First_name,*foundUser.Last_name,*foundUser.User_type,foundUser.User_id)
		
		//err = userCollection.FindOne(dctx, bson.M{"user_id": foundUser.User_id}).Decode(&foundUser)
		/*if err!=nil{
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":err.Error()})
			return
		}*/

		ctx.JSON(http.StatusOK, foundUser)
	}
}

func GetUser() gin.HandlerFunc{

	return func(ctx *gin.Context) {

		user_id := ctx.Param("user_id")

		var dctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)
		
		var user models.User
		
		//err := userCollection.FindOne(dctx, bson.M{"user_id":user_id}).Decode(&user)
		
		defer cancel()
		
		if err!=nil{
			ctx.JSON(http.StatusInternalServerError, gin.H{"error":err.Error()})
		}
		
		ctx.JSON(http.StatusOK,user)
	}
}