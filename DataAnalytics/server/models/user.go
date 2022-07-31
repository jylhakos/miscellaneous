// models/user.go

package models

import (
  "gorm.io/gorm"
  //"time"
)

type User struct {
	//gorm.Model
	ID uint `json:"id" gorm:"primary_key"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type Token struct {
	TokenString string `json:"token"`
}