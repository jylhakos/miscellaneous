package routes

import (
	"github.com/gin-gonic/gin"
	"server/controllers"
	//"server/middleware"
)

func UserRoutes(router *gin.Engine) {
	router.POST("/api/user/register",controllers.Register)
	router.POST("/api/user/login",controllers.Login)
	router.POST("/api/user/refresh",controllers.Refresh)
}

func SqlRoutes(router *gin.Engine) {
	router.GET("/api/sql/bill_head",controllers.GetBillHead) 
	router.GET("/api/sql/shipyard_parttype",controllers.GetShipYardPartType) 
	router.GET("/api/sql/ship_structure",controllers.GetShipStructure)
	router.GET("/api/sql/ship_shipyard",controllers.GetShipYard)
	router.GET("/api/sql/ship_partitem",controllers.GetShipPartItem)
}

//$ curl -v GET --url http://localhost:8001/api/sql/bill_head

//$ curl -v -H "Authorization: Bearer <JWT>" -X GET --url http://localhost:8001/api/sql/bill_head

//$ curl -v -H "Cookie: cookie=<JWT>" -X GET --url http://localhost:8001/api/sql/bill_head

//$ curl -v -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://localhost:8001/api/user/register

//$ curl -v -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://localhost:8001/api/user/login

//$ curl -v -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://172.2.0.3:8001/api/user/register

//$ curl -v -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://172.2.0.3:8001/api/user/login

//$ curl -v GET --url 172.2.0.2:3002/login