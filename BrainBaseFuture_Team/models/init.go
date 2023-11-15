package models

import (
	"fmt"
	"github.com/go-redis/redis/v8"
	"github.com/spf13/viper"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

var DB *gorm.DB
var PromptBaseDB *gorm.DB
var PromptDetailDB *gorm.DB

func InitDB() {
	//driverName := "mysql"
	host := viper.GetString("datasource.host")
	port := viper.GetString("datasource.port")
	database := viper.GetString("datasource.database")
	username := viper.GetString("datasource.username")
	password := viper.GetString("datasource.password")
	charset := viper.GetString("datasource.charset")
	println(username)

	args := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=%s&parseTime=True&loc=Local",
		username,
		password,
		host,
		port,
		database,
		charset)

	//db, err := gorm.Open(driverName, args)
	//dsn := "root:root@tcp(127.0.0.1:3306)/ginessential?charset=utf8mb4&parseTime=True&loc=Local"
	dsn := args
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})

	if err != nil {
		panic("failed to connect database, err: " + err.Error())
	}
	db.AutoMigrate(&UserBasic{})
	DB = db

	db.Set("gorm:table_options", "ENGINE=InnoDB DEFAULT CHARSET=utf8").AutoMigrate(&PromptBase{})
	PromptBaseDB = db

	db.Set("gorm:table_options", "ENGINE=InnoDB DEFAULT CHARSET=utf8").AutoMigrate(&PromptDetail{})
	PromptDetailDB = db

}

func GetDB(table string) *gorm.DB {
	if table == "user" {
		return DB
	}
	if table == "promptBase" {
		return PromptBaseDB
	}
	if table == "promptDetail" {
		return PromptDetailDB
	}
	return nil
}

func InitRedis() *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr:     viper.GetString("Redis.Addr"),
		Password: "", // no password set
		DB:       0,  // use default DB
	})
}
