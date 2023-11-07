<template>
  <div class="font-set">
    <div class="title">
      <img src="../assets/logo3.png" style="width:auto;height: 50px;margin-right: 5px">
      <h1 style="font-size: 32px;color: black;">成就榜<img src="../assets/notification.png" style="width:auto;height: 50px;"></h1>
      <el-row class="row-bg" justify="center">
        <el-col :span="6">
          <h1 style="font-size: 32px;" class="gradient-text">开发者</h1>
          <img class="mascot" src="../assets/mascot1.png">
        </el-col>

        <el-col :span="6">
          <h1 style="font-size: 32px;" class="gradient-text">创造者</h1>
          <img class="mascot" src="../assets/mascot2.png">
        </el-col>
      </el-row>
      <h1 style="font-size: 20px;color: black;">加入光荣的进化吧！</h1>
      <h2 style="font-size: 20px;color: black;font-weight: 20">We are the City of Progress. And our future is bright.</h2>
    </div>
  </div>

</template>

<script>


export default {
  name: "rank.vue",
  data() {
    return {
      login: 0
    }

  },
  created() {

  }
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

.mascot {
  width: 60%;
  opacity: 1;
  border-radius: 20px;
}

.mascot:hover {
  box-shadow:
      -20px 0 20px 5px rgba(213, 255, 145, 0.5),
      0px -20px 20px 5px rgba(145, 255, 191, 0.5),
      20px 0 20px 5px rgba(82, 255, 220, 0.5),
      0 20px 20px 5px rgba(239, 255, 91, 0.5);
}

</style>