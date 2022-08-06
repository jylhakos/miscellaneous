// models/sql.go

package models

import (
  //"gorm.io/gorm"
  "time"
)

type BillHead struct {
  //gorm.Model
  ID uint `json:"id" gorm:"primary_key"`
  BillNo string `json:"bill_no"`
  CompanyId string `json:"company_id"`
  ShipId string `json:"ship_id"`
  SpNo string `json:"sp_no"`
  TotalAmount string `json: "total_amount"`
  BillDate string `json: "bill_date"`
  //bill_date time.Time `json: "bill_date"`
}

type ShipYardPartType struct {
  ID uint `json:"id" gorm:"primary_key"`
  ShipYardId uint `json:"shipyard_id"`
  Code string `json:"code"`
  Name string `json:"name"`
  Sequence uint `json:"sequence"`  
  ParentId uint `json:"parent_id"` 
  CreateUid uint `json:"create_uid"`  
  CreateDate time.Time `json:"create_date"` 
  WriteUid uint `json:"write_uid"` 
  WriteDate time.Time `json:"write_date"`
}

type ShipStructure struct {
  ID uint `json:"id" gorm:"primary_key"`
  Code string `json:"code"`
  Name string `json:"name"`
  Sequence uint `json:"sequence"`
}

type ShipYard struct {
  ID uint `json:"id" gorm:"primary_key"`
  Code string `json:"code"`
  Name string `json:"name"`
  Sequence uint `json:"sequence"`  
  Contact string `json:"contact"`
  Phone uint `json:"phone"`
  CompanyId uint `json:"company_id"`
  City string `json:"city"`
  StateId uint `json:"state_id"`
  CountryId uint `json:"country_id"`
  Lat string `json:"lat"`
  Lng string `json:"lng"`
}

type ShipPartItem struct {
  ID uint `json:"id" gorm:"primary_key"` 
  ShipPartTypeId  uint `json:"ship_parttype_id"`
  ShipParTypeCode  string `json:"ship_parttype_code "` 
  Code string `json:"code"`
  Name string `json:"name"`  
  Unit string `json:"unit"`
}