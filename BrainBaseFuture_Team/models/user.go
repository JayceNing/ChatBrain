package models

import "gorm.io/gorm"

type UserBasic struct {
	gorm.Model
	Id        string `gorm:"type:varchar(256);not null;not null;unique"`
	ImagePath string `gorm:"varchar(1024);"`
<<<<<<< HEAD
	Name      string `gorm:"type:varchar(1024);""`
	Password  string `gorm:"type:varchar(1024);""`
	Email     string `gorm:"type:varchar(1024);""`
=======
	Name      string `gorm:"type:varchar(1024);"`
	Password  string `gorm:"type:varchar(1024);"`
	Email     string `gorm:"type:varchar(1024);"`
	Money     int `gorm:"type:int;"`
>>>>>>> 20230902
}
