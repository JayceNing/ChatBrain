package config

import "github.com/dgrijalva/jwt-go"

type UserClaim struct {
	Identity string
	Name     string
	jwt.StandardClaims
}

var JwtKey = "brainbase-team-key"
var MailPassword = "Nxy99113"

// 验证码长度
var CodeLength = 6

// 验证码的过期时间 (s)
var CodeExpire = 900

// token 过期的时间
var TokenExpire = 3000

var RefreshTokenExpire = 30000
