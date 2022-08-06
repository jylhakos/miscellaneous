// database/setup.go

package database

import (
  "fmt"
  "log"
  "os"
  "github.com/joho/godotenv"
  "gorm.io/driver/postgres"
  //_ "github.com/lib/pq"
  "gorm.io/gorm"
)

var DB *gorm.DB

var err error

func ConnectDatabase() {

  err := godotenv.Load(".env")

  if err != nil {
    fmt.Println("Failed to load .env file",err)
    log.Fatalf("Failed to load .env file")
    return
  }

  host := os.Getenv("PG_HOST")
  port := os.Getenv("PG_PORT")
  dbname := os.Getenv("PG_DBNM")
  user := os.Getenv("PG_USER")
  password := os.Getenv("PG_PASS")

  psqlconn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable", host, port, user, password, dbname)

  //db, err := gorm.Open("postgres", psqlconn)

  db, err := gorm.Open(postgres.Open(psqlconn), &gorm.Config{})

  if err != nil {
    fmt.Println("Failed to connect to database ",err)
    log.Fatalf("Failed to connect to database ")
    return
  }

  //db.AutoMigrate(&BillHead{})

  //db.AutoMigrate(&ShipYardPartType{})

  DB = db

  fmt.Println("Connected to database ", dbname)
}

func GetDB() *gorm.DB {
  return DB
}