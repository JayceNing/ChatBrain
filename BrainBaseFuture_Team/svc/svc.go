package svc

import (
	"bupt.nxy/brainbaseteam/middleware"
	"bupt.nxy/brainbaseteam/models"
	"github.com/go-redis/redis/v8"
	"github.com/zeromicro/go-zero/rest"
)

type ServiceContext struct {
	RDB  *redis.Client
	Auth rest.Middleware
}

func NewServiceContext() *ServiceContext {
	return &ServiceContext{
		RDB:  models.InitRedis(),
		Auth: middleware.NewAuthMiddleware().Handle,
	}
}
