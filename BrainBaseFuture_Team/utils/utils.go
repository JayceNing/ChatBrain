package utils

import (
	"bupt.nxy/brainbaseteam/config"
	"crypto/md5"
	"crypto/tls"
	"errors"
	"fmt"
	"github.com/dgrijalva/jwt-go"
	"github.com/jordan-wright/email"
	uuid "github.com/satori/go.uuid"
	"math/rand"
	"net/smtp"
	"time"
)

func GenerateToken(identity string, name string, second int) (string, error) {
	// id
	// identity
	// name
	uc := config.UserClaim{
		Identity: identity,
		Name:     name,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Add(time.Second * time.Duration(second)).Unix(),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, uc)
	tokenString, err := token.SignedString([]byte(config.JwtKey))
	if err != nil {
		return "", err
	}
	return tokenString, nil
}

// Token 解析
func AnalyzeToken(token string) (*config.UserClaim, error) {
	uc := new(config.UserClaim)
	claims, err := jwt.ParseWithClaims(token, uc, func(token *jwt.Token) (interface{}, error) {
		return []byte(config.JwtKey), nil
	})
	if err != nil {
		return nil, err
	}
	if !claims.Valid {
		return uc, errors.New("token is invalid")
	}
	return uc, err
}

// 邮箱验证码发送
func MailSendCode(mail string, code string) error {
	e := email.NewEmail()
	e.From = "脑基未来 Jayce Ning <" + config.MailAddress + ">"
	e.To = []string{mail}
	e.Subject = "电子邮箱验证码"
	e.HTML = []byte("<h1>脑基未来 BrainBase Future</h1><p>尊敬的用户！</p><p>感谢您注册我们的服务。您的验证码是：</p><h1>" + code + "</h1><p>验证码有效期为15分钟。</p><p>请将该验证码输入到注册页面以完成注册过程。</p>")
	err := e.SendWithTLS("smtp.exmail.qq.com:465", smtp.PlainAuth("", config.MailAddress, config.MailPassword, "smtp.exmail.qq.com"),
		&tls.Config{InsecureSkipVerify: true, ServerName: "smtp.exmail.qq.com"})
	if err != nil {
		return err
	}
	return nil
}

func RandCode() string {
	s := "1234567890"
	code := ""
	rand.Seed(time.Now().UnixNano())
	for i := 0; i < config.CodeLength; i++ {
		code += string(s[rand.Intn(len(s))])
	}
	return code
}

func UUID() string {
	return uuid.NewV4().String()
}

func Md5(s string) string {
	return fmt.Sprintf("%x", md5.Sum([]byte(s)))
}
