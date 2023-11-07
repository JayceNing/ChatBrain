package models

import "gorm.io/gorm"

type PromptBase struct {
	gorm.Model
	Name string `gorm:"type:varchar(1024);not null;not null;unique"`
}

type PromptDetail struct {
	gorm.Model
	Basename string `gorm:"type:varchar(1024);"`
	Name     string `gorm:"type:varchar(1024);"`
	Prompt   string `gorm:"type:text;charset=utf8mb4"`
}
