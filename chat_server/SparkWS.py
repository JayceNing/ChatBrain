import SparkApi
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import websockets
import json

app = FastAPI()

#以下密钥信息从控制台获取
appid = ""     #填写控制台中获取的 APPID 信息
api_secret = ""   #填写控制台中获取的 APISecret 信息
api_key =""    #填写控制台中获取的 APIKey 信息

#用于配置大模型版本，默认“general/generalv2”
domain = "general"   # v1.5版本
# domain = "generalv2"    # v2.0版本
#云端环境的服务地址
Spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # v1.5环境的地址
# Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址


#text =[]

# length = 0

def getText(role,content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text =[]
    text.append(jsoncon)
    return text

def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text
    
#@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # 将WebSocket连接添加到集合中
    # SparkApi.websocket_clients.add(websocket)
    SparkApi.websocket_clients = [websocket]
    
    try:
        while True:
            # 这里可以添加与前端交互的逻辑
            question = await websocket.receive_text()
            data = json.loads(question)

            # 使用列表推导式过滤不符合条件的项
            question = [item for item in data if item.get("isUser") == True]
            real_question = []
            for i in question:
                real_question.append({'role': 'user', 'content': i["content"]})
            print("==============================")
            print(question)
            question = checklen(real_question)
            print(question)
            # 处理从前端接收到的数据
            SparkApi.answer =""
            await SparkApi.main(appid,api_key,api_secret,Spark_url,domain,question)
            #print(str(SparkApi.answer))
            await websocket.close()

    except WebSocketDisconnect:
        print("WebSocketDisconnect")
        # 当WebSocket连接关闭时
        # SparkApi.websocket_clients = []
        # await websocket.close()

if __name__ == '__main__':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源访问，实际中根据需要配置
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 使用uvicorn运行FastAPI应用程序，监听在指定的主机和端口上
    uvicorn.run(app, host="0.0.0.0", port=8012)



