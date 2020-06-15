<template>
  <el-col :span="24" class="header">
    <el-col :span="8" class="logo" :class="collapsed?'logo-collapse-width':'logo-width'">
      <router-link to="/" style='text-decoration: none;color: #FFFFFF;'>
        <img id="logo" src="../../assets/logo.png"/>{{collapsed?'':sysName}}
      </router-link>
    </el-col>
    <el-col :span="1">
      <div class="tools" @click.prevent="collapse">
        <i class="fa fa-align-justify"></i>
      </div>
    </el-col>
    <el-col :span="11" class="project-info" v-if="projectName">
      <span class="project-info-inner">{{projectName}}</span>
    </el-col>
    <el-col :span="4" class="user-info">
      <el-dropdown trigger="hover">
					<span class="el-dropdown-link user-info-inner">
						{{sysUserName}}
						<img id="user-photo" src="../../assets/imgs/user.gif"/>
					</span>
        <el-dropdown-menu slot="dropdown">
          <router-link :to="{ name: 'ChangePassword'}" style='text-decoration: none;color: #FFFFFF;'>
            <el-dropdown-item v-if="isLogin">修改密码</el-dropdown-item>
          </router-link>
          <el-dropdown-item :loading="logoutLoading" divided @click.native="logout" v-if="isLogin">退出登录
          </el-dropdown-item>
          <el-dropdown-item @click.native="login" v-if="!isLogin">登录</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </el-col>
  </el-col>
</template>

<script>
    import {logout} from '../../api/user'
    import {removeToken, setToken, getToken} from "../../utils/auth";
    import jwt_decode from "jwt-decode"

    export default {
        name: "Header",
        props: ['projectName'],
        data() {
            return {
                sysName: 'Leo API AutoTest',
                collapsed: false,
                sysUserName: '',
                isLogin: false,
                logoutLoading: false
            }
        },
        methods: {
            //跳转登录
            login: function () {
                this.$router.push({name: 'login'})
            },
            //退出登录
            logout: function () {
                this.$confirm('确认退出吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.isLogin = false
                    this.logoutLoading = true
                    this.$store.dispatch('user/logout')
                        .then((res) => {
                            this.logoutLoading = false
                            this.$message.success({
                                message: res,
                                center: true,
                            })
                            this.$router.push({name: 'login'})
                        }).catch(() => {
                        this.loginLoading = false
                    })
                })
            },
            //折叠导航栏
            collapse: function () {
                this.collapsed = !this.collapsed;
                this.$emit('collapse', this.collapsed);
            }
        },
        mounted() {
            try {
                let email = jwt_decode(getToken()).email;
                if (email.trim().length > 0) {
                    this.isLogin = true
                }
                this.sysUserName = email
            } catch (e) {
                removeToken()
                this.$message.error({
                    message: '未获取到用户信息，请重新登录!',
                    center: true,
                })
                this.$router.push({name: 'login'})
            }

        }
    }

</script>

<style scoped lang="scss">
  .container {
    position: absolute;
    top: 0px;
    bottom: 0px;
    width: 100%;

    .header {
      height: 60px;
      line-height: 60px;
      background: $--color-primary;
      color: #fff;

      .user-info {
        text-align: right;
        padding-right: 35px;
        float: right;

        .user-info-inner {
          cursor: pointer;
          color: #fff;

          img {
            width: 40px;
            height: 40px;
            border-radius: 20px;
            margin: 10px 0px 10px 10px;
            float: right;
          }
        }
      }

      .logo {
        height: 60px;
        font-size: 22px;
        padding-left: 10px;
        padding-right: 10px;
        border-color: rgba(238, 241, 146, 0.3);
        border-right-width: 1px;
        border-right-style: solid;

        img {
          width: 40px;
          float: left;
          margin: 10px 5px 10px 0px;
        }

        .txt {
          color: #fff;
        }
      }

      .logo-width {
        width: 240px;
      }

      .logo-collapse-width {
        width: 60px
      }

      .tools {
        padding: 0px 23px;
        width: 14px;
        height: 60px;
        line-height: 60px;
        cursor: pointer;
      }

      .project-info {
        text-align: left;
        padding-right: 35px;
        float: left;
        font-size: 22px;
        line-height: 60px;

        .project-info-inner {
          cursor: pointer;
          color: #fff;
        }
      }
    }
  }
</style>
