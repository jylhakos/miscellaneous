package routes

import (
	"github.com/gin-gonic/gin"
	"server/controllers"
	"server/middleware"
)

func UserRoutes(router *gin.Engine){
	router.POST("/api/user/register",controllers.Register)
	router.POST("/api/user/login",controllers.Login)
}

func SqlRoutes(router *gin.Engine){
	router.Use(middleware.Authorization())
	router.GET("/api/sql/bill_head",controllers.GetBillHead) 
	router.GET("/api/sql/shipyard_parttype",controllers.GetShipYardPartType) 
	router.GET("/api/sql/ship_structure",controllers.GetShipStructure)
	router.GET("/api/sql/ship_shipyard",controllers.GetShipYard)
	router.GET("/api/sql/ship_partitem",controllers.GetShipPartItem)
}
