<template>
  <div class="homepage">



    <div class="container" :style="{height:containerHeight + 'px'}">

      <div style="z-index: 0">
        <TransitionGroup name="image-transition" @leave="randomizeImagePosition">
          <img v-for="image in images" :key="image.id" :src="getAssetsFile(image.src)" :style=image.style class="image" />

        </TransitionGroup>
      </div>

      <div :style="{marginTop:containerHeight*0.4 + 'px'}">
        <h1 class="element" ref="typedElement" style="font-size: 50px;color: white"></h1>
      </div>

      <el-icon size="60" color="#fff">
        <ArrowDownBold />
      </el-icon>


    </div>

    <div class="middlemenu" >
      <el-menu
          class="el-menu-demo"
          mode="horizontal"
          :ellipsis="false"
          @select="handleMidSelect"
          style="background-color: black;"
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#81f54b"
      >
        <el-menu-item style="width: 30%;margin-left: 20%" index="0">团队成员</el-menu-item>
        <el-menu-item style="width: 30%;" index="1">发展历程</el-menu-item>
      </el-menu>
    </div>

    <div class="resume" >
      <el-row :gutter="0" justify="center">
        <el-col :span="7">
          <div>
            <img class="resume-avatar" src="../assets/Jayce.jpg">
          </div>
        </el-col>
        <el-col :span="10">
          <div>
            <h1 style="font-size: 48px;color: black">创始人 Jayce Ning</h1>

            <a href="https://github.com//BUPT-NingXinyu" target="_blank" class="no-link-color">
              <font-awesome-icon style="margin: 5px;" class="fa-2x" :icon="['fab', 'github']" />
            </a>
            <a href="https://www.zhihu.com/people/XinyuNing" target="_blank" class="no-link-color">
              <font-awesome-icon style="margin: 5px;" class="fa-2x" :icon="['fab', 'zhihu']" />
            </a>

            <font-awesome-icon style="margin: 5px;" class="fa-2x" :icon="['fab', 'tiktok']" />

            <a href="https://space.bilibili.com/351554857" target="_blank" class="no-link-color">
              <font-awesome-icon style="margin: 5px;" class="fa-2x" :icon="['fab', 'bilibili']" />
            </a>
            <a href="https://www.researchgate.net/profile/Xinyu-Ning" target="_blank" class="no-link-color">
              <font-awesome-icon style="margin: 5px;" class="fa-2x" :icon="['fab', 'researchgate']" />
            </a>
            <a href="https://www.kaggle.com/xinyuning" target="_blank" class="no-link-color">
              <font-awesome-icon style="margin: 5px;" class="fa-2x" :icon="['fab', 'kaggle']" />
            </a>

            <div>
              <h1 style="font-size: 32px;color: black;">构建脑机接口技术与 AI 大模型之间的桥梁</h1>
            </div>
            <div >
              <h1 class="element" ref="Jayce" style="font-size: 40px;color: black"></h1>
            </div >
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="timelinebox">
      <div class="timeline">
        <el-timeline>
            <el-timeline-item timestamp="" placement="top" style="text-align: left">
                <h1 class="gradient-text" style="font-size: 36px">2022.11.17</h1>
                <h1 style="font-size: 32px;color: white;">AI平台立项</h1>
            </el-timeline-item>
            <el-timeline-item timestamp="" placement="top" style="text-align: left">
                <h1 class="gradient-text" style="font-size: 36px">2023.3.12</h1>
                <h1 style="font-size: 32px;color: white;">发布 AI 训练 平台 V1.0.0 alpha</h1>
            </el-timeline-item>
          <el-timeline-item timestamp="" placement="top" style="text-align: left">
            <h1 class="gradient-text" style="font-size: 36px">2023.5.23</h1>
            <h1 style="font-size: 32px;color: white;">脑基未来 BrainBase Future 团队组建</h1>
          </el-timeline-item>
          <el-timeline-item timestamp="" placement="top" style="text-align: left">
            <h1 class="gradient-text" style="font-size: 36px">2023.6.1</h1>
            <h1 style="font-size: 32px;color: white;">发布脑机接口论坛  V0.1.0 alpha</h1>
          </el-timeline-item>
          <el-timeline-item timestamp="" placement="top" style="text-align: left">
            <h1 class="gradient-text" style="font-size: 36px">2023.6.11</h1>
            <h1 style="font-size: 32px;color: white;">发布 齐物 V1.0.0 基于 Stable Diffusion 的脑电作画引擎</h1>
          </el-timeline-item>
          <el-timeline-item timestamp="" placement="top" style="text-align: left">
            <h1 class="gradient-text" style="font-size: 36px">2023.6.19</h1>
            <h1 style="font-size: 32px;color: white;">发布团队管理平台 BrainBase Future Team V0.1.0 alpha</h1>
          </el-timeline-item>
            <el-timeline-item timestamp="" placement="top" style="text-align: left">
                <h1 class="gradient-text" style="font-size: 36px">2023.7.8</h1>
                <h1 style="font-size: 32px;color: white;">ChatBrain 立项</h1>
            </el-timeline-item>
            <el-timeline-item timestamp="" placement="top" style="text-align: left">
                <h1 class="gradient-text" style="font-size: 36px">2023.7.14</h1>
                <h1 style="font-size: 32px;color: white;">发布 ChatBrain V0.1.0 alpha</h1>
            </el-timeline-item>
            <el-timeline-item timestamp="" placement="top" style="text-align: left">
                <h1 class="gradient-text" style="font-size: 36px">2023.8.9</h1>
                <h1 style="font-size: 32px;color: white;">本项目获第九届中国国际“互联网+”大学生创新创业大赛北京赛区金奖</h1>
            </el-timeline-item>
        </el-timeline>
      </div>
    </div>

  </div>
</template>

<script>
import { ref } from 'vue'
import { Transition } from 'vue';
import { TransitionGroup } from 'vue';

export default {
  name: 'home.vue',
  data() {
    return {
      containerWidth: '',
      containerHeight: '',
      images: [

        { id: 1, src: "/JayceA.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 2, src: "/cjh.jpg", style:"animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 3, src: "/gjj.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 4, src: "/ht.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 5, src: "/hyh.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 6, src: "/lj.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 7, src: "/lxz.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 8, src: "/sc.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 9, src: "/szx.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 10, src: "/thm.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 11, src: "/zd.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 12, src: "/zgl.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 13, src: "/zj.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 14, src: "/zsl.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},
        { id: 15, src: "/zyt.jpg", style: "animation: slide 5s linear infinite, fadeInOut 10s infinite"},



      ],
    }
  },
  created() {
    setInterval(() => {
      this.randomizeImagePosition(this.images);
    },10000)
  },
  mounted() {
    this.containerWidth = (window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth);
    this.containerHeight = (window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight)-75;
    this.randomizeImagePosition(this.images);
    const options = {
      strings: ['这就是脑基未来团队 BrainBase Future Team.'],
      typeSpeed: 100,
      startDelay: 1000,
      backSpeed: 50,
      backDelay: 10000,
      loop: true,
      smartBackspace: true,
      showCursor: true,
      cursorChar: '',
      cursorSpeed: 1000,
      cursorBlinking: 'blink',
    };
    const jayceword = {
      strings: ['"Its our turn to decide the future of Hextech."'],
      typeSpeed: 100,
      startDelay: 1000,
      backSpeed: 50,
      backDelay: 10000,
      loop: true,
      showCursor: false,
    };
    new this.$typed(this.$refs.typedElement, options);
    new this.$typed(this.$refs.Jayce, jayceword);

  },
  methods: {

    getAssetsFile(url) {
      return new URL(`${url}`, import.meta.url).href
    },

    randomizeImagePosition(e) {
      e.forEach((image) => {
        const maxLeft = this.containerWidth
        const maxTop = this.containerHeight

        const randomLeft = Math.floor(Math.random() * maxLeft);
        const randomTop = Math.floor(Math.random() * maxTop);

        image.style = "left:" + randomLeft + 'px;' + "top:" + randomTop + 'px;animation: slide 10s linear infinite, fadeInOut 10s infinite';

      });

    },
    handleSelect(e) {
      console.log(e)
    },
    handleMidSelect(e) {
      console.log(e)
    }

  }
};

</script>

<style>
.font-set {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 0;
}

.homepage {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 0;
}

.gradient-text {
  background: linear-gradient(45deg,#d3ff33, #81f54b, #33d3ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.container {
  /*margin: 20px;*/
  /*border-radius: 20px;*/
  position: relative;
  /*width: 100%; !* 区域容器的宽度 *!*/
  /*height: 800px;*/
  overflow: hidden; /* 隐藏溢出部分 */
  /*background: black;*/

  background: url(../assets/background.png) center;

}

/*打印字配置*/
.element {
  position: relative;
}

.element::after {
  content: '';
  position: absolute;
  margin-left: 4px;
  height: 100%;
  width: 4px;
  background-color: white; /* 光标的颜色 */
  animation: blink 1s infinite; /* 光标的闪烁动画 */
}

@keyframes blink {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

.image {
  position: absolute;
  border-radius: 50%;
  top: 0;
  left: 0px;
  width: 80px;
  height: 80px;
  /*opacity: 0.6;*/
}

.image:hover {
  margin-left: -10px;
  margin-top: -10px;
  width: 100px;
  height: 100px;
  box-shadow:
      -20px 0 20px 5px rgba(213, 255, 145, 0.5),
      0px -20px 20px 5px rgba(145, 255, 191, 0.5),
      20px 0 20px 5px rgba(82, 255, 220, 0.5),
      0 20px 20px 5px rgba(239, 255, 91, 0.5);
}

@keyframes slide {
  0% {
    transform: translateY(500px);
  }
  100% {
    transform: translateY(-500px);
  }
}

@keyframes fadeInOut {
  0% {
    opacity: 0;
  }
  25% {
    opacity: 0.8;
  }
  75% {
    opacity: 0.8;
  }
  100% {
    opacity: 0;
  }
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

/*小菜单*/
.middlemenu {
  position: relative;
  width: 100%;
  height: 100px;
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  background-color: black;
}

/*团队成员*/
.resume {
  position: relative;
  width: 100%;
  background-color: #ffffff;
}

.resume-avatar{
  border-radius: 0%;
  width:100%;
  height: auto;
  box-shadow:
      -20px 0 20px 5px rgba(213, 255, 145, 0.5),
      0px -20px 20px 5px rgba(145, 255, 191, 0.5),
      20px 0 20px 5px rgba(82, 255, 220, 0.5),
      0 20px 20px 5px rgba(239, 255, 91, 0.5);

}

.el-row {
  margin-bottom: 20px;
}
.el-row:first-child {
  margin-top: 100px;
}
.el-row:last-child {
  margin-bottom: 0;
}
.el-col {
  border-radius: 4px;
  margin: 40px;
}

.grid-content {
  border-radius: 4px;
  min-height: 36px;
}

/*图标*/
.no-link-color {
  color: inherit;
  text-decoration: none;
}
.fa-2x:hover {
  box-shadow:
      -10px 0 10px 5px rgba(213, 255, 145, 0.5),
      0px -10px 10px 5px rgba(145, 255, 191, 0.5),
      10px 0 10px 5px rgba(82, 255, 220, 0.5),
      0 10px 10px 5px rgba(239, 255, 91, 0.5);
}
/*发展历程*/
.timelinebox {
  margin-top: 120px;
  position: relative;
  width: 100%;
  background-color: black;
}

.timeline {
  padding: 120px;

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