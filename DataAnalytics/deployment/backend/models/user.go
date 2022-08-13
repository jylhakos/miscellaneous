// models/user.go

package models

import (
  //"gorm.io/gorm"
  "time"
)

type User struct {
	//gorm.Model
	ID uint `json:"id" gorm:"primary_key"`
  Username string  `json:"username" validate:"required"`
	Password string `json:"password" validate:"required"`
  Cookie string `json:"cookie"`
  //AccessToken string `json:"access_token"`
  //RefreshToken string `json:"refresh_token"`
  CreatedAt time.Time `json:"created_at"`
  UpdatedAt time.Time `json:"updated_at"`
}