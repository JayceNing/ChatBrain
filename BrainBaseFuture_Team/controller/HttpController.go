package controller

import (
	"bupt.nxy/brainbaseteam/config"
	"bupt.nxy/brainbaseteam/models"
	"bupt.nxy/brainbaseteam/response"
	"bupt.nxy/brainbaseteam/utils"
	"errors"
	"fmt"
	"github.com/gin-gonic/gin"
	"time"
)

func SendEmail(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("user")
	Email := ctx.PostForm("email")
	// 该邮箱未被注册
	fmt.Println("email")
	fmt.Println(Email)

	var user models.UserBasic
	DB.Where("email = ?", Email).Find(&user)

	if (user != models.UserBasic{}) {
		response.Fail(ctx, "该邮箱已注册", nil)
		return
	}

	// 获取验证码
	code := utils.RandCode()
	fmt.Println(code)
	// 存储验证码
	models.InitRedis().Set(ctx, Email, code, time.Second*time.Duration(config.CodeExpire))
	fmt.Println("code save")
	// 发送验证码
	err := utils.MailSendCode(Email, code)

	if err != nil {
		fmt.Println("mail send code error")
		return
	}
	response.Success(ctx, nil, "验证码已发送")
	return
}

func UserRegister(ctx *gin.Context) {
	DB := models.GetDB("user")

	Email := ctx.PostForm("email")
	UserCode := ctx.PostForm("code")
	Password := ctx.PostForm("password")
	// 判断code是否一致
	code, err := models.InitRedis().Get(ctx, Email).Result()
	if err != nil {
		response.Fail(ctx, "请重新获取验证码", nil)
		return
	}
	if code != UserCode {
		err = errors.New("验证码错误")
		response.Fail(ctx, "验证码错误", nil)
		return
	}

	// 数据入库
	user := &models.UserBasic{
		Id:       utils.UUID(),
		Name:     "BrainBase",
		Password: utils.Md5(Password),
		Email:    Email,

		
	}
	result := DB.Create(&user)

	if result.Error != nil {
		response.Success(ctx, nil, "注册失败")
	} else {
		response.Success(ctx, nil, "注册成功")
	}


	return
}

func UserLogin(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("user")

	Email := ctx.PostForm("email")
	Password := ctx.PostForm("password")
	// 1、从数据库中查询当前用户
	var user models.UserBasic
	DB.Where("email = ? AND password = ?", Email, utils.Md5(Password)).Find(&user)
	fmt.Println(user)
	fmt.Println(Email)
	fmt.Println(utils.Md5(Password))

	if (user == models.UserBasic{}) {
		response.Fail(ctx, "用户名或密码错误", nil)
		return
	}
	// 2、 生成 token
	token, err := utils.GenerateToken(user.Id, user.Name, config.TokenExpire)
	if err != nil {
		response.Fail(ctx, "token生成错误", nil)
		return
	}
	// 生成用于刷新token的token
	refreshToken, err := utils.GenerateToken(user.Id, user.Name, config.RefreshTokenExpire)
	if err != nil {
		response.Fail(ctx, "token生成错误", nil)
		return
	}

	response.Success(ctx, gin.H{"userbasic": user, "token": token, "refreshToken": refreshToken}, "登录成功")

	return
}

func ListBase(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("promptBase")

	var promptBase []models.PromptBase
	DB.Find(&promptBase)
	fmt.Println(promptBase)

	response.Success(ctx, gin.H{"promptBase": promptBase}, "查询成功")
}

func AddBase(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("promptBase")

	BaseName := ctx.PostForm("name")
	fmt.Println(BaseName)

	promptBase := models.PromptBase{
		Name: BaseName,
	}
	DB.Create(&promptBase)

	response.Success(ctx, nil, "创建成功")
}

func DeleteBase(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("promptBase")

	BaseName := ctx.PostForm("name")

	DB.Unscoped().Where("name = ?", BaseName).Delete(&models.PromptBase{})

	response.Success(ctx, nil, "删除成功")
}

func ListPrompt(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("promptDetail")
	BaseName := ctx.PostForm("name")

	var promptDetail []models.PromptDetail
	DB.Where("basename = ?", BaseName).Find(&promptDetail)
	fmt.Println(promptDetail)

	response.Success(ctx, gin.H{"promptDetail": promptDetail}, "查询成功")
}

func AddPrompt(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("promptDetail")
	baseName := ctx.PostForm("basename")
	name := ctx.PostForm("name")
	prompt := ctx.PostForm("prompt")

	promptDetail := models.PromptDetail{
		Basename: baseName,
		Name:     name,
		Prompt:   prompt,
	}
	DB.Create(&promptDetail)

	response.Success(ctx, nil, "创建成功")
}

func DeletePrompt(ctx *gin.Context) {
	// todo: add your logic here and delete this line
	DB := models.GetDB("promptDetail")

	name := ctx.PostForm("name")
	baseName := ctx.PostForm("basename")

	DB.Unscoped().Where("name = ? AND basename = ?", name, baseName).Delete(&models.PromptDetail{})

	response.Success(ctx, nil, "删除成功")
}
