<template>
  <div class="leo-login">
    <div class="leo-login-main">
      <div style="text-align:center;margin-bottom:20px;">
        <img src="../../assets/logo.png" style="margin-bottom: 8px" width="100px" height="90px">
        <div style="font-size: 24px;color: #e6a721">{{sysName}}</div>
      </div>
      <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" autocomplete="on"
               label-position="left">
        <el-form-item prop="email">
          <el-input ref="email" v-model="loginForm.email" placeholder="请输入邮箱" name="email"
                    tabindex="1" autocomplete="on"/>
        </el-form-item>
        <el-form-item prop="password">
          <el-input :key="passwordType" ref="password" v-model="loginForm.password" :type="passwordType"
                    placeholder="Password" name="password" tabindex="2" autocomplete="on"
                    @keyup.enter.native="handleLogin">
            <i slot="suffix" @click="showPwd"
               :class="passwordType === 'password' ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
          </el-input>
        </el-form-item>
        <el-button id="login-checkout" class="login-btn" :loading="loginLoading" type="primary" @click="handleLogin">
          登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script>
    import {removeToken} from "../../utils/auth";

    export default {
        data() {
            const validatePassword = (rule, value, callback) => {
                if (!value) {
                    callback(new Error('请输入密码'));
                } else if (value.toString().length < 6 || value.toString().length > 18) {
                    // callback(new Error('密码长度为6 - 18个字符'))
                    callback()
                } else {
                    callback()
                }
            }
            return {
                sysName: 'Leo API AutoTest',
                loginForm: {
                    email: '',
                    password: ''
                },
                loginRules: {
                    username: [{required: true, trigger: 'blur'}],
                    password: [{required: true, trigger: 'blur', validator: validatePassword}]
                },
                passwordType: 'password',
                loginLoading: false,
                redirect: undefined,
                otherQuery: {}
            }
        },
        watch: {
            $route: {
                handler: function (route) {
                    const query = route.query
                    if (query) {
                        this.redirect = query.redirect
                        this.otherQuery = this.getOtherQuery(query)
                    }
                },
                immediate: true
            }
        },
        methods: {
            showPwd() {
                if (this.passwordType === 'password') {
                    this.passwordType = ''
                } else {
                    this.passwordType = 'password'
                }
                this.$nextTick(() => {
                    this.$refs.password.focus()
                })
            },
            handleLogin() {
                this.$refs.loginForm.validate(valid => {
                    if (valid) {
                        this.$store.dispatch('user/login', this.loginForm)
                            .then(() => {
                                this.loginLoading = false
                                this.$router.push({path: this.redirect || '/', query: this.otherQuery})
                            })
                            .catch(() => {
                                this.loginLoading = false
                            })
                    } else {
                        console.log('error login input!!')
                        return false
                    }
                })
            },
            getOtherQuery(query) {
                return Object.keys(query).reduce((acc, cur) => {
                    if (cur !== 'redirect') {
                        acc[cur] = query[cur]
                    }
                    return acc
                }, {})
            }
        }
    }
</script>

<style scoped>
  .leo-login {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    background-size: 100% 100%;
    -moz-background-size: 100% 100%;
    -webkit-background-size: 100% 100%;
    background: url(../../assets/imgs/login-bg.jpeg) no-repeat;
    background-size: cover;
  }

  .leo-login-main {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 440px;
    padding: 30px 20px;
    border-radius: 4px;
    background-color: #fff;
  }

  .login-btn {
    width: 100%;
  }

  .login-form {
    text-align: center;
    position: relative;
    width: 300px;
  }

  @media screen and (max-width: 500px) {
    .leo-login {
      background: #fff;
    }

    .leo-login-main {
      width: 90%;
      box-sizing: border-box;
      border: none;
      box-shadow: none;
      background-color: transparent;
    }
  }
</style>
