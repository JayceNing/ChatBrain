<template>

  <div v-if="login==0" class="font-set">

    <el-row class="row-bg" justify="center">
      <el-col :span="6">
        <div class="title">

          <div >
            <h1 class="quotes" ref="word" style="font-size: 40px;color: black"></h1>
          </div >

        </div>
      </el-col>
      <el-col :span="2">

      </el-col>
      <el-col :span="8">
        <div class="box-card">
          <el-card>
            <!-- <div class="card-header" >
              <img src="../assets/logo3.png" style="width:auto;height: 50px;margin-right: 5px">
            </div> -->


            <div v-if="registering==0" class="inputs" style="margin-bottom: 80px">
              <h1 style="font-size: 28px;color: black;">登录</h1>
              <div class="input">
                <el-input v-model="username" placeholder="电子邮箱" />
              </div>
              <div class="input">
                <el-input v-model="password" placeholder="密码" />
              </div>
              <el-button class="button" style="background-color: white;border: 2px solid black;" text><h1 style="font-size: 20px;color: black;" @click="tapRegister">注册</h1></el-button>
              <el-button class="button" style="background-color: black;" text><h1 style="font-size: 20px;color: white;" @click="tapLogin">登录</h1></el-button>
            </div>

            <div v-if="registering==1 & nextStage==0" class="inputs" style="margin-bottom: 20px">
              <h1 style="font-size: 28px;color: black;">注册</h1>
              <div class="input" style="margin-bottom: 80px">
                <h2 style="font-size: 20px;color: black;font-weight: 20">本平台 正处于内测阶段，请填写正确的邀请码进行注册</h2>
                <div class="input">
                  <el-input v-model="code" placeholder="邀请码" />
                </div>
                <div class="input">
                  <el-button class="button" style="background-color: black;" text><h1 style="font-size: 20px;color: white;" @click="tapNext">下一步</h1></el-button>
                </div>
              </div>

              <el-button class="button" style="background-color: white;border: 2px solid black;" text><h1 style="font-size: 20px;color: black;" @click="tapLogin">返回登录页面</h1></el-button>
            </div>

            <div v-if="registering==1 & nextStage==1" class="inputs" style="margin-bottom: 20px">
              <h1 style="font-size: 28px;color: black;">注册</h1>

              <div class="input" style="margin-bottom: 80px">
                <div class="input" style="display: flex">
<!--                  <el-input v-model="email" placeholder="邮箱" />-->

                  <el-form ref="email" :model="formData">
                  <el-form-item
                      label=""
                      prop="email"
                      :rules="[
                      { required: true, message: '请输入邮箱地址', trigger: 'blur' },
                      { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
                      ]"
                  >
                    <el-input
                        v-model="formData.email"
                        placeholder="邮箱"
                    />
                  </el-form-item>
                  </el-form>


                  <el-button :disabled="isButtonDisabled" class="button" style="background-color: white;border: 2px solid black;margin-left: 20px" text><h1 style="font-size: 20px;color: black;" @click="sendValid">{{ buttonText }}</h1></el-button>
                </div>

                <el-form ref="pass" :model="formData">
                <div class="input">
                  <el-input v-model="valid" placeholder="验证码" />
                </div>
                <div class="input">

                  <el-form-item label="" prop="pass" :rules="[{ validator: validatePass, trigger: 'blur' }]">
                    <el-input v-model="formData.pass" type="password" autocomplete="off" placeholder="请输入密码"/>
                  </el-form-item>
                  <el-form-item label="" prop="checkPass" :rules="[{ validator: validatePass2, trigger: 'blur' }]">
                    <el-input
                        v-model="formData.checkPass"
                        type="password"
                        autocomplete="off"
                        placeholder="请再次输入密码"
                    />
                  </el-form-item>
                </div>
                </el-form>


                <div class="input">
                  <el-button class="button" style="background-color: black;" text><h1 style="font-size: 20px;color: white;" @click="tapNext">下一步</h1></el-button>
                </div>
              </div>


              <el-button class="button" style="background-color: white;border: 2px solid black;" text><h1 style="font-size: 20px;color: black;" @click="tapLogin">返回登录页面</h1></el-button>
            </div>



          </el-card>

        </div>
      </el-col>
    </el-row>

  </div>


  <div v-if="login==1">
    <div class="title">
      <div class="font-set">
        <!-- <img src="../assets/logo3.png" style="width:auto;height: 50px;margin-right: 5px"> -->
        <h1 style="font-size: 32px;color: black;">个人资料</h1>
      </div>


      <div class="resume" >
        <el-row :gutter="0" justify="center">
          <el-col :span="4">
            <div>

              <img v-if="globalVariables.userBasic.ImagePath != ''" class="resume-avatar" :src=globalVariables.userBasic.ImagePath>
              <img v-if="globalVariables.userBasic.ImagePath == ''" class="resume-avatar" src="../assets/JayceA.jpg" style="border-radius:50%">
            </div>
          </el-col>
          <el-col :span="10">
            <!-- <div>
              <h1 style="font-size: 48px;color: black">用户名： {{ globalVariables.userBasic.Name }}</h1>
              <p style="text-transform: none">电子邮箱：{{ globalVariables.userBasic.Email }}</p>

            </div> -->
            <el-descriptions title="账号信息">
              <el-descriptions-item label="用户名"> {{globalVariables.userBasic.Name}}</el-descriptions-item>
              <el-descriptions-item label="电子邮箱">{{ globalVariables.userBasic.Email }}</el-descriptions-item>
            </el-descriptions>

            <el-descriptions title="账号余额" style="margin-top: 20px">
              <el-descriptions-item label="余额"> {{globalVariables.userBasic.Money}} 元</el-descriptions-item>
            </el-descriptions>

            <el-button class="button" style="background-color: black;margin-top:20px" text><h1 style="font-size: 20px;color: white;" @click="recharge">账号充值</h1></el-button>


          </el-col>
        </el-row>

      </div>

    </div>
  </div>

  <div v-if="popup>0" class="popup font-set">
    <div class="popup-content">
      <h2 class="gradient-text" style="margin-bottom: 80px">提示</h2>
      <h2 v-if="popup==1" style="font-size: 20px;color: black;margin-bottom: 80px">请输入正确的邀请码！</h2>
      <h2 v-if="popup==2" style="font-size: 20px;color: black;margin-bottom: 80px">验证码已发送！</h2>
      <h2 v-if="popup==3" style="font-size: 20px;color: black;margin-bottom: 80px">请检查该邮箱是否可用</h2>
      <h2 v-if="popup==4" style="font-size: 20px;color: black;margin-bottom: 80px">注册成功！</h2>
      <h2 v-if="popup==5" style="font-size: 20px;color: black;margin-bottom: 80px">请检查密码是否正确</h2>
      <h2 v-if="popup==6" style="font-size: 20px;color: black;margin-bottom: 80px">{{ popMsg }}</h2>
      <el-button class="button" style="background-color: black;" text><h1 style="font-size: 20px;color: white;" @click="closepop">关闭</h1></el-button>
    </div>
  </div>

</template>

<script>
import request from "../utils/request";
import { globalVariables } from '../utils/globalVariables.js';

export default {
  name: "profile.vue",
  computed: {
    globalVariables() {
      return globalVariables
    }
  },

  data() {
    return {
      login: 0,
      username: '',
      password: '',
      registering: 0,
      nextStage: 0,
      code: '',
      popup: 0,
      valid:'',
      popMsg: '',
      //验证码按钮
      isButtonDisabled: false, // 按钮是否禁用
      countdownSeconds: 60, // 倒计时秒数
      buttonText: '发送验证码', // 按钮文本
      formData: {
        email: '',
        pass: '',
        checkPass: ''
      },
      userBasic: '',

    }

  },
  mounted() {
    if (globalVariables.login == 0) {
      const word = {
        strings: ['“Humans don’t live for centuries. We can’t wait for progress. We need leadership focused on the future, not the past.”- Jayce Trails.'],
        typeSpeed: 100,
        startDelay: 1000,
        backSpeed: 50,
        backDelay: 10000,
        loop: true,
        showCursor: false,
      };
      new this.$typed(this.$refs.word, word);
    }
  },
  created() {
    this.login = globalVariables.login
  },

  methods: {
    closepop(){
      this.popup=0
    },

    tapRegister() {
      if (this.registering == 0){
        this.registering = 1
      }

    },
    tapLogin() {
      console.log(this.registering)
      console.log(this.username)
      console.log(this.password)
      if (this.registering == 1) {
        this.registering = 0
      } else {
        let data = new FormData()
        data.append("email", this.username)
        data.append("password", this.password)

        request.post("/api/k8s/userlogin", data).then(res => {
          if (res) {
            console.log(res)
            if (res.code == 400){
              this.popup = 6
              this.popMsg = res.msg
            } else {
              this.popMsg = res.msg
              this.token = res.data.token
              this.refreshtoken = res.data.refreshtoken
              this.userBasic = res.data.userbasic
              this.login = 1
              globalVariables.login = 1
              globalVariables.token = res.data.token
              globalVariables.refreshToken = res.data.refreshtoken
              globalVariables.userBasic = res.data.userbasic

            }
          } else {
            console.log("登录失败")
          }
        })
      }

    },
    tapNext() {
      console.log(this.nextStage)
      if (this.nextStage == 0) {
        if (this.code!=="Nothingfeelsimpossible"){
          this.popup = 1
        }
        else {
          this.nextStage = 1
        }
      } else if (this.nextStage == 1) {
        console.log("开始注册")
        this.userRegister()
      }
    },
    userRegister() {
      let data = new FormData()
      data.append("email", this.formData.email)
      data.append("code", this.valid)
      data.append("password", this.formData.pass)

      this.$refs.email.validate(valid => {
        if (valid) {
          // 表单验证通过，可以进行注册操作
          console.log('注册表单验证成功');
          if(this.formData.pass == this.formData.checkPass) {
            request.post("/api/k8s/userregister", data).then(res => {
              if (res) {
                console.log(res)
                this.popup = 6
                if (res.code == 400){
                  this.popMsg = res.msg
                } else {
                  this.popMsg = res.msg
                  this.tapLogin()
                }
              } else {
                console.log("注册失败")
              }
            })
          }else {
            console.log('表单验证失败');
            this.popup=5
          }

        } else {
          console.log('表单验证失败');
          this.popup=3
        }
      });

    },
    validatePass(rule, value, callback) {
      if (value === '') {
        callback(new Error('请输入密码'))
      }
    },
    validatePass2(rule, value, callback) {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.formData.pass) {
        callback(new Error("两次密码不一致"))
      } else {
        callback()
      }
    },
    sendValid() {
      let data = new FormData()
      data.append("email", this.formData.email)
        console.log(this.formData.email)
        console.log(data)
      this.$refs.email.validate(valid => {
        if (valid) {
          // 表单验证通过，可以进行提交操作
          // 在这里可以执行你的逻辑，比如发送验证码等
          console.log('邮箱验证通过');
          this.startCountdown()
          request.post("/api/k8s/sendemail", data).then(res => {
            if (res) {
              console.log("验证码发送成功")
              console.log(res)
                if(res.code==400){
                    this.popup = 6
                    this.popMsg = res.msg
                }else{
                    this.popup = 2
                }

            } else {
              console.log("请检查该邮箱是否可用")
            }
          })
        } else {
          console.log('表单验证失败');
          this.popup=3
        }
      });
    },
    startCountdown() {
      this.isButtonDisabled = true; // 禁用按钮
      this.countdownSeconds = 60; // 重置倒计时秒数
      this.buttonText = `${this.countdownSeconds}s`; // 更新按钮文本

      const timer = setInterval(() => {
        this.countdownSeconds--; // 秒数减少
        this.buttonText = `${this.countdownSeconds}s`; // 更新按钮文本

        if (this.countdownSeconds === 0) {
          clearInterval(timer); // 清除计时器
          this.isButtonDisabled = false; // 启用按钮
          this.buttonText = '发送验证码'; // 恢复按钮文本
        }
      }, 1000);

    },
    
    recharge() {
      this.popup = 6
      this.popMsg = "充值功能正在构建中，敬请期待。。。"

    }

  }

}
</script>

<style scoped>

.font-set {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 0;
  text-transform:  uppercase;
}

.title {
  margin-top: 80px;
}

.box-card{
  width: 100%;
}

/*打印字配置*/
.quotes {
  position: relative;
  height: 500px;
}

.quotes::after {
  content: '';
  position: absolute;
  margin-left: 4px;
  height: 100%;
  width: 4px;
  background-color: white; /* 光标的颜色 */
  animation: blink 1s infinite; /* 光标的闪烁动画 */
}

.inputs {
  width: 70%;
  margin-left: 15%;
}

.input {
  margin: 20px
}

/* 弹窗 */
.popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9999;
}

.popup-content {
  background-color: #fff;
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

</style>