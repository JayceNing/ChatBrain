<template>
  <div class="font-set">
    <div class="title">
      <h1 style="font-size: 32px;color: black;">任务列表<img src="../assets/notification.png" style="width:auto;height: 50px;"></h1>
      <h1 style="font-size: 20px;color: black;">完成这些任务，赚取你的成就！</h1>
    </div>

    <div class="box-card">

      <el-card class="single-card" style="background-color: lightcyan;border-radius: 20px">
        <template #header>
          <div class="card-header">
            <h1 style="font-size: 20px;" class="gradient-text">创造者任务</h1>
            <el-button class="button" style="background-color: black;" text><h1 style="font-size: 20px;color: white;">接受任务</h1></el-button>
          </div>
        </template>

        <el-row justify="center">
          <el-col :span="8">
            <img class="mascot" src="../assets/mascot2.png">
            <div style="margin-top: 8px">
              <el-tag class="mx-1" effect="dark" type="success" style="margin: 2px">创造者任务</el-tag>
              <el-tag class="mx-1" effect="dark" type="warning" style="margin: 2px">一般</el-tag>
            </div>
          </el-col>
          <el-col :span="2">
          </el-col>
          <el-col :span="12" style="text-align: left">
            <h1 style="font-size: 20px;color: black;text-align: center">商业计划书修改</h1>
            <h1 style="font-size: 16px;color: black; font-weight: 20">1. 文字格式调整</h1>
            <h1 style="font-size: 16px;color: black; font-weight: 20">2. 内容梳理</h1>
            <h1 style="font-size: 16px;color: black; font-weight: 20">3. 图片修改，风格一致化</h1>
            <h1 style="font-size: 20px;color: black;text-align: right;" class="gradient-text">贡献值：20</h1>
          </el-col>
        </el-row>

      </el-card>

      <el-card class="single-card" style="background-color: lightyellow;border-radius: 20px">
        <template #header>
          <div class="card-header">
            <h1 style="font-size: 20px;" class="gradient-text">开发者任务</h1>
            <el-button class="button" style="background-color: black;" text><h1 style="font-size: 20px;color: white;">接受任务</h1></el-button>
          </div>
        </template>

        <el-row justify="center">
          <el-col :span="8">
            <img class="mascot" src="../assets/mascot1.png">
            <div style="margin-top: 8px">
              <el-tag class="mx-1" effect="dark" type="success" style="margin: 2px">开发者任务</el-tag>
              <el-tag class="mx-1" effect="dark" type="danger" style="margin: 2px">困难</el-tag>
            </div>
          </el-col>
          <el-col :span="2">
          </el-col>
          <el-col :span="12" style="text-align: left">
            <h1 style="font-size: 20px;color: black;text-align: center">开发基于脑电的作曲引擎 Beethoven</h1>
            <h1 style="font-size: 16px;color: black; font-weight: 20">1. 支持输入不同情绪EEG信号生成相应曲目</h1>
            <h1 style="font-size: 16px;color: black; font-weight: 20">2. 前端页面可在 Davinci 基础上进行开发</h1>
            <h1 style="font-size: 16px;color: black; font-weight: 20">3. 后端情感分类可基于 Davinci 结果，接入作曲模型</h1>
            <h1 style="font-size: 20px;color: black;text-align: right;" class="gradient-text">贡献值：40</h1>
          </el-col>
        </el-row>

      </el-card>
    </div>

    <div class="title">
      <h2 style="font-size: 20px;color: black;font-weight: 20">Do you know what the success rate for senior Academy inventors is?</h2>
      <h2 style="font-size: 20px;color: black;font-weight: 20">Three percent.</h2>
      <h2 style="font-size: 20px;color: black;font-weight: 20">We’re no strangers to failure.</h2>
      <h2 style="font-size: 20px;color: black;font-weight: 20">What makes this the City of Progress is that we keep trying until we get it right.</h2>
    </div>
  </div>
</template>

<script>
export default {
  name: "task.vue"
}
</script>

<style scoped>

.font-set {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 0;
  text-transform: uppercase;
}

.title {
  margin-top: 80px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}

.box-card {
  margin-top: 40px;
  width: 50%;
  margin-left: 25%;

}

.single-card {
  margin-top: 20px;

}

.el-row {
  margin: 0px;
  padding: 0px;
}

.el-col {
  margin: 0px;
  padding: 0px;
}

.mascot {

  width: 60%;
  opacity: 1;
  border-radius: 20px;
}


</style>