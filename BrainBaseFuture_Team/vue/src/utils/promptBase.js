import axios from 'axios'

const client = axios.create({
    baseURL: 'http://10.112.224.75:8000'
});
client.interceptors.request.use(config => {
    config.headers['Content-Type'] = 'application/json;charset=utf-8';
    config.headers['Access-Control-Allow-Origin'] = '*';

    // config.headers['token'] = user.token;  // 设置请求头
    return config
}, error => {
    return Promise.reject(error)
});

function ListBase() {
    client.post("http://10.112.224.75:1016/api/prompt/listbase", null).then(res => {
        if (res) {
            console.log(res)
            return res.data.data

        } else {
            console.log("接口调用失败")
            return null
        }
    })
}

function AddBase(basename) {
    let data = new FormData()
    data.append("name", basename)

    client.post("http://10.112.224.75:1016/api/prompt/addbase", data).then(res => {
        if (res) {
            console.log(res)

        } else {
            console.log("接口调用失败")
        }
    })

}

function DeleteBase(basename) {
    let data = new FormData()
    data.append("name", basename)

    client.post("http://10.112.224.75:1016/api/prompt/deletebase", data).then(res => {
        if (res) {
            console.log(res)

        } else {
            console.log("接口调用失败")
        }
    })

}

function ListPrompt(basename) {
    let data = new FormData()
    data.append("name", basename)

    client.post("http://10.112.224.75:1016/api/prompt/listprompt", data).then(res => {
        if (res) {
            console.log(res)

        } else {
            console.log("接口调用失败")
        }
    })
}

function AddPrompt(basename, name, prompt) {

    let data = new FormData()
    data.append("basename", basename)
    data.append("name", name)
    data.append("prompt", prompt)

    client.post("http://10.112.224.75:1016/api/prompt/addprompt", data).then(res => {
        if (res) {
            console.log(res)

        } else {
            console.log("接口调用失败")
        }
    })

}

function DeletePrompt(basename, name) {

    let data = new FormData()
    data.append("basename", basename)
    data.append("name", name)

    client.post("http://10.112.224.75:1016/api/prompt/deleteprompt", data).then(res => {
        if (res) {
            console.log(res)

        } else {
            console.log("接口调用失败")
        }
    })

}

export {ListBase,AddBase,DeleteBase,ListPrompt,AddPrompt,DeletePrompt};