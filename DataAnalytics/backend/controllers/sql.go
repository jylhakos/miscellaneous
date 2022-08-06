// controllers/sql.go

package controllers

import (
  "fmt"
  "net/http"
  "github.com/gin-gonic/gin"
  "server/models"
)

// SELECT * FROM bill_head;
func GetBillHead(c *gin.Context) {
  fmt.Println("GetBillHead")
  var bill_head []models.BillHead
  fmt.Println(&models.BillHead{})
  db := models.GetDB()
  fmt.Println("GetDB", db)
  if err := db.Table("bill_head").Select("id","bill_no","company_id","ship_id","sp_no","total_amount","bill_date").Find(&bill_head).Error; err != nil {
    fmt.Println("Error", err)
    return
  }
  fmt.Println("Find", gin.H{"data": bill_head})
  c.JSON(http.StatusOK, gin.H{"data": bill_head})
  fmt.Println("JSON", bill_head)
}

// SELECT * FROM shipyard_parttype;
func GetShipYardPartType(c *gin.Context) {
  fmt.Println("GetShipYardPartType")
  var shipyard_parttype []models.ShipYardPartType
  fmt.Println(&models.ShipYardPartType{})
  db := models.GetDB()
  fmt.Println("GetDB", db)
  if err := db.Table("shipyard_parttype").Find(&shipyard_parttype).Error; err != nil {
    fmt.Println("Error", err)
    return
  }
  c.JSON(http.StatusOK, gin.H{"data": shipyard_parttype})
  fmt.Println(http.StatusOK, "JSON", shipyard_parttype)
}

// SELECT * FROM ship_structure;
func GetShipStructure(c *gin.Context) {
  fmt.Println("GetShipStructure")
  var ship_structure []models.ShipStructure
  fmt.Println(&models.ShipStructure{})
  db := models.GetDB()
  fmt.Println("GetDB", db)
  if err := db.Table("ship_structure").Select("id","code","name","sequence").Find(&ship_structure).Error; err != nil {
    fmt.Println("Error", err)
    return
  }
  c.JSON(http.StatusOK, gin.H{"data": ship_structure})
  fmt.Println(http.StatusOK, "JSON", ship_structure)
}

// SELECT * FROM ship_shipyard;
func GetShipYard(c *gin.Context) {
  fmt.Println("GetShipYard")
  var ship_shipyard []models.ShipYard
  fmt.Println(&models.ShipYard{})
  db := models.GetDB()
  fmt.Println("GetDB", db)
  if err := db.Table("ship_shipyard").Select("id","code","name","sequence","contact","phone","company_id","city","state_id","city","state_id","country_id","lat","lng").Find(&ship_shipyard).Error; err != nil {
    fmt.Println("Error", err)
    return
  }
  c.JSON(http.StatusOK, gin.H{"data": ship_shipyard})
  fmt.Println(http.StatusOK, "JSON", ship_shipyard)
}

// SELECT * FROM ship_partitem;
func GetShipPartItem(c *gin.Context) {
  fmt.Println("GetShipPartItem")
  var ship_partitem []models.ShipPartItem
  fmt.Println(&models.ShipPartItem{})
  db := models.GetDB()
  fmt.Println("GetDB", db)
  if err := db.Table("ship_partitem").Select("id","ship_parttype_id","ship_parttype_code","code","name","unit").Find(&ship_partitem).Error; err != nil {
    fmt.Println("Error", err)
    return
  }
  c.JSON(http.StatusOK, gin.H{"data": ship_partitem})
  fmt.Println(http.StatusOK, "JSON", ship_partitem)
}