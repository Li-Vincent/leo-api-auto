<template>
  <el-row class="container">
    <header-view :projectName="projectName"></header-view>
    <!-- project 导航栏-->
    <el-col :span="24">
      <template :index='project_id'>
        <el-menu default-active="autoTest" class="el-menu-demo" mode="horizontal" @select="handleSelect" unique-opened>
          <template v-for="menu in projectNavMenu" v-if="menu.projectMenu">
            <template v-for="(items,index) in menu.children" v-if="!items.hidden">
              <el-menu-item :class="$route.nav===items.nav?'is-active':''"
                            :index="items.child?items.children[0].nav:items.nav" v-if="items.leaf"
                            :key="items.path">
                <template v-if="!items.child">
                  <router-link :to="{ name: items.name, params: {id: project_id}}"
                               style='text-decoration: none;color: #000000;'>
                    <div>
                      {{items.meta.title }}
                    </div>
                  </router-link>
                </template>
                <template v-if="items.child">
                  <router-link :to="{ name: items.children[0].name, params: {id: project_id}}"
                               style='text-decoration: none;color: #000000;'>
                    <div>
                      {{items.meta.title }}
                    </div>
                  </router-link>
                </template>
              </el-menu-item>
              <el-submenu :index="index+''" v-if="!items.leaf">
                <template slot="title">{{items.meta.title}}</template>
                <el-menu-item v-for="child in items.children" :key="child.path" :index="child.path"
                              v-if="!child.hidden">
                  <router-link :to="{ name: child.name, params: {id: project_id}}"
                               style='text-decoration: none;color: #000000;'>
                    {{child.meta.title}}
                  </router-link>
                </el-menu-item>
              </el-submenu>
            </template>
          </template>
        </el-menu>
      </template>
    </el-col>
    <el-col :span="24">
      <transition name="fade" mode="out-in">
        <router-view></router-view>
      </transition>
    </el-col>
  </el-row>
</template>

<script>
    import Header from "../common/Header";
    import {getProjectInfo} from "../../api/project";

    export default {
        name: 'Project',
        components: {Header},
        data() {
            return {
                project_id: this.$route.params.project_id,
                projectName: '',
                projectNavMenu: this.$store.getters.routes
            }
        },
        methods: {
            handleSelect: function (a, b) {
            },
        },
        mounted() {
            getProjectInfo(this.$route.params.project_id).then((res) => {
                if (res.status === 'ok') {
                    this.projectName = res.data.name;
                }
            })
        }
    }

</script>

<style scoped lang="scss">

  .container {
    position: absolute;
    top: 0px;
    bottom: 0px;
    width: 100%;
  }
</style>
