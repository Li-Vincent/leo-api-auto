<template>
  <div class="error">
    <div class="error-container">
      <p class="remind">您访问的页面地球不存在，请返回主页！</p>
      <router-link to="/">
        <p><a class="button">返回主页</a></p>
      </router-link>
    </div>
  </div>
</template>

<script>
    export default {
        name: "NotFound"
    }
</script>

<style scoped lang="scss">
  .error{
    height: 100%;
    background-color: #f8f8f8;
  }
  .error-container {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 483px;
    margin: -300px 0 0 -242px;
    padding-top: 199px;
    padding-bottom: 50px;
    font-size: 18px;
    color: #666;
    text-align: center;
    background: url(../assets/404.jpg) 0 0 no-repeat;
  }

  .error .remind {
    margin: 30px 0;
  }

  .error .button {
    display: inline-block;
    padding: 0 20px;
    line-height: 40px;
    font-size: 14px;
    color: #fff;
    background-color: $--color-primary;
    text-decoration: none;
  }

  .error .button:hover {
    opacity: .9;
  }
</style>
