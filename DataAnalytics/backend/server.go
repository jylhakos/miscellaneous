// server.go

package main

import (
	"fmt"
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/gin-contrib/cors"
	"time"
	//"server/models"
	"server/routes"
	"server/database"
	"server/middleware"
	//"server/controllers"
)

func main() {

	fmt.Println("main()")

	router := gin.Default()

	router.Use(cors.New(cors.Config {
	    AllowOrigins:     []string{"http://localhost:3002"},
	    AllowMethods:     []string{"GET","POST","OPTIONS"},
	    AllowHeaders:     []string{"Content-Type","Content-Length","Authorization"},
	    //ExposeHeaders:    []string{"Content-Length"},
	    AllowCredentials: true,
	    //AllowOriginFunc: func(origin string) bool {
	    //  return origin == "https://localhost"
	    //},
    	MaxAge: 12 * time.Hour,
  	}))

  	//router.Use(cors.Default())

  	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "success"})	
	})

  	routes.UserRoutes(router)

	router.Use(middleware.Authorization())

	routes.SqlRoutes(router)

	database.ConnectDatabase()

	router.Run(":8001")
}