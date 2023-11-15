<template>

  <div class="font-set">
  <el-menu
      class="el-menu-demo"
      mode="horizontal"
      :ellipsis="false"
      @select="handleSelect"
      style="background-color: black;"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#81f54b"
  >

    <nav style="margin-left: 10px;margin-top: 10px" @click="toHome">
      <img src="./assets/logo1.png" style="width:50px;height: 50px;margin-right: 5px">
      <h1 class="gradient-text">基于大语言模型的文献综述自动生成平台</h1><h2> </h2>
    </nav>


<!--    <el-menu-item index="0">任务列表</el-menu-item>-->
<!--    <el-menu-item index="1">成就榜</el-menu-item>-->

      <el-menu-item index="3" style="width:auto">AI学术</el-menu-item>

    <el-sub-menu index="2">
      <template #title><text style="font-family: Arial, sans-serif;font-size: 20px;font-weight: bold;">个人资料</text></template>
      <div v-if="login==0">
        <el-menu-item index="2-0" style="width: 100%;">登录</el-menu-item>
      </div>
      <div v-if="login==1">
        <el-menu-item index="2-1" style="width: 100%;">个人信息</el-menu-item>
        <el-menu-item index="2-2" style="width: 100%;">退出登录</el-menu-item>
      </div>

    </el-sub-menu>
  </el-menu>
    </div>

  <index v-if="currentPage==0"></index>
  <task v-if="currentPage==1"></task>
  <rank v-if="currentPage==2"></rank>
  <profile v-if="currentPage==3"></profile>
    <chatbrain @update-data="handleUpdateData" v-if="currentPage==4"></chatbrain>


  <footer>
    <!-- <p>&copy; 2023 BrainBase Future Tech Company. All rights reserved.</p> -->
  </footer>
</template>

<script>
import index from './components/home.vue'
import rank from './components/rank.vue'
import task from './components/task.vue'
import profile from './components/profile.vue'
import chatbrain from './components/chatbrain.vue'
import { globalVariables } from './utils/globalVariables.js';

import axios from 'axios'


export default {
  name: 'Home',
  data() {
    return {
      currentPage: 0,
      login: 0,
    }
  },
  components: {
    index,
    rank,
    task,
    profile,
      chatbrain
  },
  created() {


  },

  updated() {
    this.login = globalVariables.login
    if (this.login){
      this.queryMoney()
    }

  },
  methods: {
      handleUpdateData(newData) {
          this.currentPage = newData;
      },
    toHome() {
      this.currentPage = 0
    },


    queryMoney(){
      // 此处是文献综述系统后端地址，即 chat_server/main.py 中对应服务。应为服务器地址加对应端口号 'http://XX.XX.XX.XX:8008'
      const content_generate_url = ''
      let data = {
          "useremail": globalVariables.userBasic.Email,
          "x": ""
      }

      axios.post(content_generate_url + '/v1/querymoney', data,
          {
              headers: {
                  'Content-Type': 'application/json'
              },
          })
          .then(response => {
              console.log("queryMoney")
              console.log(response)
              globalVariables.userBasic.Money = response.data.res


          })
          .catch(error => {
              console.error(error);
          });
    },


    handleSelect(e) {
      console.log(e)
      if (e==0) {
        this.currentPage = 1
      }
      if (e==1) {
        this.currentPage = 2
      }
      if (e== "2-1" | e== "2-0") {
        this.currentPage = 3
      }
      if (e== "2-2") {
        this.currentPage = 0
        this.login = 0
        globalVariables.login = 0
        globalVariables.token = ''
        globalVariables.refreshToken = ''
        globalVariables.userBasic = ''
      }
      if (e == "3") {
          this.currentPage = 4
      }
    },

  }
};

</script>

<style>
.font-set {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 0;
}


.gradient-text {
  background: linear-gradient(45deg,#d3ff33, #81f54b, #33d3ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}


nav {
  display: flex;
  margin: 0 auto;
  left: 0px;
}

nav h1 {
  margin-top: 4px;
  font-size: 28px;
  margin-right: 10px;
  color: #ffffff;
}

nav h2 {
  font-size: 20px;
  color: #ffffff;
  text-transform: uppercase;
}

/*菜单字体*/
/* 修改菜单项的字体 */
.el-menu {
  border: 0px;
}
.el-menu-item {
  font-family: Arial, sans-serif;
  font-size: 20px;
  font-weight: bold;
  width: 160px;
  height:72px;
  line-height: 72px;

}

.el-sub-menu {
  font-family: Arial, sans-serif;
  font-size: 18px;
  font-weight: bold;
}

/*页脚*/
footer {
  background-color: white;
  position: relative;
  text-align: center;
  width: 100%;
  bottom: 0px;
  color: #fff;
}
footer p {
  font-size: 16px;
  color: black;
}
</style>