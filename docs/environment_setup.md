# Environment setup
The frontend pages are built using VUE3, the account management system is constructed with the Go language, and the literature review system utilizes Python.

So at least the following packages are required:
* Node.js v16.17.0
* go 1.21.0 +
* python 3.8 +

## Node.js
Install Node.js v16.17.0 on ubuntu.
```sh
wget https://registry.npmmirror.com/-/binary/node/v16.17.0/node-v16.17.0-linux-x64.tar.xz
tar xf node-v16.17.0-linux-x64.tar.xz  -C /usr/local/ && cd /usr/local
rm -rf /usr/local/node
ln -sfv /usr/local/node-v16.17.0-linux-x64 /usr/local/node
echo 'export NODE_HOME=/usr/local/node
export PATH=$NODE_HOME/bin:$PATH' >>/etc/profile
source /etc/profile
```
Verify installation.
```sh
node -v
npm -v
```
Project setup.
```sh
cd ./BrainBaseFuture_Team/vue
npm install
```

### Frontend Pages
#### IP Address Modify
Modify the IP address in the configuration file ```./BrainBaseFuture_Team/vue/package.json```
```json
  "scripts": {
    "dev": "vite --host {Your IP address}",
    "build": "vite build",
    "preview": "vite preview"
  },
```
Change ip address for *vue* web to connect Go system (Account Management System). Modify file ```./BrainBaseFuture_Team/vue/.env```
```
VITE_APP_BASE_URL=http://XX.XX.XX.XX:1016/  # Your IP Address
```
To connect Python System (Literature Review System).

Modify ```./vue/src/components/chatbrain.vue``` line 500.
```vue
// 此处是文献综述系统后端地址，即 chat_server/main.py 中对应服务。应为服务器地址加对应端口号 'http://XX.XX.XX.XX:8008'
const content_generate_url = ''
```
```./vue/src/components/chatbrain.vue``` line 937.
```vue
const socket = new WebSocket("ws://XX.XX.XX.XX:8008/ws");
```
```./vue/src/components/chatbrain.vue``` line 1028.
```vue
const socket = new WebSocket("ws://XX.XX.XX.XX:8008/ws/literature?useremail=" + globalVariables.userBasic.Email +"&query=" + this.selectedQuery + "&keyword=None&selectmethod=" + this.selectedselectmethod);
```
Modify ```./vue/src/App.vue``` line 101.
```vue
// 此处是文献综述系统后端地址，即 chat_server/main.py 中对应服务。应为服务器地址加对应端口号 'http://XX.XX.XX.XX:8008'
const content_generate_url = ''
```


#### Initial the service
```sh
npm run dev
```

## Go
Install go 1.21.0.
```sh
wget https://golang.google.cn/dl/go1.21.0.linux-amd64.tar.gz
tar -zxvf go1.21.0.linux-amd64.tar.gz
sudo mv go /usr/local

echo 'export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go' >>/etc/profile
source /etc/profile
```
Verify installation.
```sh
go version
```
Set proxy.
```sh
go env -w GOPROXY=https://mirrors.aliyun.com/goproxy/
```
Verify proxy.
```sh
go env GOPROXY
```
### Account Management System

#### MySQL Database
Install MySQL.
```sh
sudo apt update
sudo apt install mysql-server
```
Verify installation.
```sh
sudo systemctl status mysql
```
Modify password.
```sh
sudo mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
```
Import example database.
```sh
sudo mysql -u root -p
CREATE DATABASE bbft;
EXIT;

mysql -u root -p bbft < ./chat_server/bbft.sql
```
#### Redis Database
Install Redis.
```sh
sudo apt install redis-server
```
Verify Installation.
```sh
sudo systemctl status redis-server
redis-cli
```

#### Initial the service
```sh
cd ./BrainBaseFuture_Team
go run main.go route.go
```

*Note*: Make sure that your server has port 1016 open, or you might meet CORS error.

## Python
Package installation. 

Before installation, make sure Python 3.8 + is available on your system.
```sh
cd ./chat_server
pip install -r requirements.txt
```
### Literature Review System
Modify the IP address in Python file ```./chat_server/main.py``` line 33.
```python
SERVER_ADDRESS = ''  # Replace with your IP address
```

#### LLM API (Spark)
This example program uses the iFlytek Spark model. Detail can be found at https://www.xfyun.cn/doc/spark/Web.html#%E5%BF%AB%E9%80%9F%E8%B0%83%E7%94%A8%E9%9B%86%E6%88%90%E6%98%9F%E7%81%AB%E8%AE%A4%E7%9F%A5%E5%A4%A7%E6%A8%A1%E5%9E%8B%EF%BC%88python%E7%A4%BA%E4%BE%8B%EF%BC%89

Modifies lines 10-19 in the file ```./chat_server/SparkWS.py```
```python
#以下密钥信息从控制台获取
appid = ""     #填写控制台中获取的 APPID 信息
api_secret = ""   #填写控制台中获取的 APISecret 信息
api_key =""    #填写控制台中获取的 APIKey 信息

#用于配置大模型版本，默认“general/generalv2”
domain = "general"   # v1.5版本
# domain = "generalv2"    # v2.0版本
#云端环境的服务地址
Spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # v1.5环境的地址
```
#### Initial Literature Review System
```sh
cd ./chat_server
python main.py
```

*Note*: Make sure that your server has port 8008 open, or you might meet CORS error.