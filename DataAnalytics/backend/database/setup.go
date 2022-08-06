// models/setup.go

package database

import (
  //_ "github.com/lib/pq"
  //_ "github.com/jinzhu/gorm/dialects/sqlite"
  "fmt"
  "log"
  //"os"
  "github.com/joho/godotenv"
  "gorm.io/driver/postgres"
  "gorm.io/gorm"
)

const (
  host     = "localhost"
  port     = 5432
  user     = "admin"
  password = "admin"
  dbname   = "V1"
)

var DB *gorm.DB

var err error

func ConnectDatabase() {

  err := godotenv.Load(".env")

  if err != nil {
    log.Fatalf("Failed to load .env file")
  }

  psqlconn := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable", host, port, user, password, dbname)

  //db, err := gorm.Open("postgres", psqlconn)

  db, err := gorm.Open(postgres.Open(psqlconn), &gorm.Config{})

  if err != nil {
    panic("Failed to connect to database.")
  }

  //db.AutoMigrate(&BillHead{})

  //db.AutoMigrate(&ShipYardPartType{})

  DB = db

  fmt.Println("ConnectDatabase()")
}

func GetDB() *gorm.DB {
  return DB
}
