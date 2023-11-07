package main

import (
	"bupt.nxy/brainbaseteam/controller"
	"bupt.nxy/brainbaseteam/middleware"
	"github.com/gin-gonic/gin"
)

func CollectRoute(r *gin.Engine) *gin.Engine {
	r.Use(middleware.CORSMiddleware())

	// 发送验证码
	r.POST("/api/k8s/sendemail", controller.SendEmail)

	// 用户注册
	r.POST("/api/k8s/userregister", controller.UserRegister)

	// 用户登录
	r.POST("/api/k8s/userlogin", controller.UserLogin)

	// 提示词仓库功能
	r.POST("/api/prompt/listbase", controller.ListBase)
	r.POST("/api/prompt/addbase", controller.AddBase)
	r.POST("/api/prompt/deletebase", controller.DeleteBase)

	r.POST("/api/prompt/listprompt", controller.ListPrompt)
	r.POST("/api/prompt/addprompt", controller.AddPrompt)
	r.POST("/api/prompt/deleteprompt", controller.DeletePrompt)

	return r
}
