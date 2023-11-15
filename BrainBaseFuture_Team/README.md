# BrainBaseFuture_Team

这里是脑基未来团队管理系统的前后端代码，本系统已合并至 [ChatBrain](https://github.com/JayceNing/ChatBrain)

## 注意事项
### 大语言模型（星火）Key配置

修改 ./vue/.env 文件

```
VITE_APP_SPARK_API_KEY=12bd2d6d5e3324c491af8b0002c2a397
VITE_APP_SPARK_API_SECRET=Y2UwZDg5ZGVmY2U5Y2Y0OTE0OGNhOGU1
VITE_APP_SPARK_API_APPID=cd72ab24
```

### 前端服务器配置

修改 ./vue/src/components/chatbrain.vue 代码第 500 行

将地址修改为文献综述系统 IP 地址端口号
```
// 此处是文献综述系统后端地址，即 chat_server/main.py 中对应服务。应为服务器地址加对应端口号 'http://XX.XX.XX.XX:8008'
const content_generate_url = ''
```

修改 ./vue/src/App.vue 代码第 101 行，修改同上
```
// 此处是文献综述系统后端地址，即 chat_server/main.py 中对应服务。应为服务器地址加对应端口号 'http://XX.XX.XX.XX:8008'
const content_generate_url = ''
```

### 验证码服务器配置

对于验证码发送功能，需要修改发送验证码的邮箱地址

修改 ./config/config.go 配置文件
```
# 此处配置用于发送验证码的邮箱地址
var MailAddress = ""  # 修改为邮箱地址（QQ邮箱）
var MailPassword = ""  # 修改为邮箱密码（QQ邮箱）
```


## 贡献者

<a href="https://github.com/JayceNing/ChatBrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=JayceNing/ChatBrain" />
</a>

Jayce Ning

个人主页：https://jaycening.github.io/zh-cn/

Github：https://github.com/JayceNing

知乎：https://www.zhihu.com/people/XinyuNing