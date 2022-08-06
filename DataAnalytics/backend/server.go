// main.go

package main

import (
	"fmt"
	"net/http"
	"github.com/gin-gonic/gin"
	"server/models"
	"server/routes"
	"server/database"
	"github.com/gin-contrib/cors"
	"time"
)

func main() {

	fmt.Println("main()")

	router := gin.Default()

	router.Use(cors.New(cors.Config{
	    AllowOrigins:     []string{"http://localhost:3002"},
	    AllowMethods:     []string{"GET"},
	    AllowHeaders:     []string{"Origin"},
	    ExposeHeaders:    []string{"Content-Length"},
	    AllowCredentials: true,
	    AllowOriginFunc: func(origin string) bool {
	      return origin == "https://github.com"
	    },
    	MaxAge: 12 * time.Hour
  	}))

	router.GET("/api", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"data": "/api"})	
	})

	routes.UserRoutes(router)

	routes.SqlRoutes(router)

	database.ConnectDatabase()

	router.Run(":8001")
}

//$ curl -v GET --url http://localhost:8001/api/sql/bill_head