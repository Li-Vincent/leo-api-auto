<template>
  <el-row class="container">
    <header-view @collapse="collapse"></header-view>
    <el-col :span="24" class="main">
      <aside :class="collapsed?'menu-collapsed':'menu-expanded'">
        <!--导航菜单-->
        <el-menu :default-active="$route.meta.menu" class="el-menu-vertical-demo" unique-opened router v-if="!collapsed">
          <template v-for="(item,index) in $store.getters.routes" v-if="!item.hidden">
            <el-menu-item style="font-size:16px" v-for="child in item.children" :index="child.path" :key="child.path"
                          v-if="!child.hidden"><i :class="child.meta.icon"></i>{{child.meta.title}}
            </el-menu-item>
          </template>
        </el-menu>
      </aside>
      <section class="content-container">
        <div class="grid-content bg-purple-light">
          <el-col :span="24" class="breadcrumb-container">
            <el-breadcrumb separator="/" class="breadcrumb-inner">
              <el-breadcrumb-item style="font-size: 15px" v-for="item in $route.matched" :key="item.path">
                {{ item.name }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </el-col>
          <el-col :span="24" class="content-wrapper">
            <transition name="fade" mode="out-in">
              <router-view></router-view>
            </transition>
          </el-col>
        </div>
      </section>
    </el-col>
  </el-row>
</template>

<script>
    import Header from "./common/Header";

    export default {
        name: 'Home',
        components: {Header},
        data() {
            return {
                collapsed: false
            }
        },
        methods: {
            //折叠导航栏
            collapse: function (data) {
                this.collapsed = data;
            }
        },
        created() {
        }
    }

</script>

<style scoped lang="scss">
  .container {
    position: absolute;
    top: 0px;
    bottom: 0px;
    width: 100%;

    .main {
      display: flex;
      // background: #324057;
      position: absolute;
      top: 60px;
      bottom: 0px;
      overflow: hidden;
      margin-left: 0px;

      aside {
        flex: 0 0 240px;
        width: 240px;
        // position: absolute;
        // top: 0px;
        // bottom: 0px;
        .el-menu {
          height: 100%;
        }

        .collapsed {
          width: 60px;

          .item {
            position: relative;
          }

          .submenu {
            position: absolute;
            top: 0px;
            left: 60px;
            z-index: 99999;
            height: auto;
            display: none;
          }

        }
      }

      .menu-collapsed {
        flex: 0 0 60px;
        width: 60px;
      }

      .menu-expanded {
        flex: 0 0 240px;
        width: 240px;
      }

      .content-container {
        flex: 1;
        overflow-y: scroll;
        padding: 20px;

        .breadcrumb-container {
          .title {
            width: 200px;
            float: left;
            color: #475669;
          }

          .breadcrumb-inner {
            float: right;
          }
        }

        .content-wrapper {
          background-color: #fff;
          box-sizing: border-box;
        }
      }
    }
  }
</style>
