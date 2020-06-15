<template>
  <div class="leo-login">
    <div class="leo-login-main">
      <el-form class="login-form" :model="form" ref="form" :rules="formRules">
        <el-row type="flex" justify="center" :gutter="10">
          <el-col>
            <el-form-item>
              <div class="title">修改密码</div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row type="flex" justify="center" :gutter="10">
          <el-col>
            <el-form-item label="用户邮箱:" label-width="83px" prop="email">
              <el-input ref="email" v-model="form.email" name="email" tabindex="0" disabled/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row type="flex" justify="center" :gutter="10">
          <el-col>
            <el-form-item label="旧密码:" prop="oldPassword" label-width="83px">
              <el-input :key="passwordType" ref="oldPassword" v-model="form.oldPassword" :type="passwordType"
                        placeholder="当前密码" name="oldPassword" tabindex="1">
                <i slot="suffix" @click="showPwd"
                   :class="passwordType === 'password' ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="10">
          <el-col>
            <el-form-item label="新密码:" prop="password" label-width="83px">
              <el-input :key="passwordType" ref="password" v-model="form.password" :type="passwordType"
                        placeholder="新密码" name="password" tabindex="2">
                <i slot="suffix" @click="showPwd"
                   :class="passwordType === 'password' ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col>
            <el-form-item label="确认密码:" prop="password2" label-width="83px">
              <el-input :key="passwordType" ref="password" v-model="form.password2" :type="passwordType"
                        placeholder="确认密码" name="password2" tabindex="3">
                <i slot="suffix" @click="showPwd"
                   :class="passwordType === 'password' ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-button id="login-checkout" class="login-btn" :loading="changePwdLoading" type="primary" @click="submit">提交
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script>
    import {changePassword} from "../../api/user";

    export default {
        name: 'Register',
        data() {
            const validatePass = (rule, value, callback) => {
                if (!value) {
                    callback(new Error('请输入新密码'));
                } else if (value.toString().length < 6 || value.toString().length > 18) {
                    callback(new Error('密码长度为6 - 18个字符'))
                } else {
                    callback();
                }
            };
            const validatePass2 = (rule, value, callback) => {
                if (!value) {
                    callback(new Error('请再次输入密码'));
                } else if (value !== this.form.password) {
                    callback(new Error('两次输入密码不一致!'));
                } else {
                    callback();
                }
            };
            return {
                changePwdLoading: false,
                passwordType: 'password',
                form: {
                    email: this.$store.getters.email,
                    oldPassword: '',
                    password: '',
                    password2: '',
                },
                formRules: {
                    oldPassword: [
                        {required: true, trigger: 'blur'}
                    ],
                    password: [
                        {required: true, validator: validatePass, trigger: 'blur'}
                    ],
                    password2: [
                        {required: true, validator: validatePass2, trigger: 'blur'}
                    ],
                }

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
            async submit() {
                this.$refs.form.validate(valid => {
                    if (valid) {
                        let header = {};
                        let params = {
                            email: this.form.email,
                            oldPassword: this.form.oldPassword,
                            password: this.form.password
                        }
                        this.changePwdLoading = true;
                        changePassword(params, header).then((res) => {
                            this.changePwdLoading = false;
                            if (res.status === 'ok') {
                                this.$message({
                                    message: res.data,
                                    center: true,
                                })
                                this.$store.dispatch('user/logout')
                                    .then((res) => {
                                        this.$router.push({name: 'login'})
                                    }).catch(() => {
                                })
                            } else {
                                this.$message.error({
                                    message: res.data,
                                    center: true,
                                })
                            }
                        });
                    } else {
                        this.$message.error({
                            message: "表单验证失败",
                            center: true,
                        })
                    }
                })
            },
        }
    }
</script>

<style scoped lang="scss">
  .title {
    font-size: 24px;
    color: $--color-primary;
  }

  .leo-login {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    background-size: 100% 100%;
    -moz-background-size: 100% 100%;
    -webkit-background-size: 100% 100%;
    background-repeat: no-repeat;
  }

  .leo-login-main {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 500px;
    padding: 20px;
    border-radius: 2px;
    background-color: #fff;
  }

  .login-btn {
    width: 440px;
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

    .login-btn {
      width: 100%;
    }
  }

  .login-form {
    text-align: center;
    position: relative;
  }

  .login-input {
    background: transparent;
    width: 300px;
    height: 40px;
    margin-bottom: 10px;
    border: 0;
    outline: 0;
    border-bottom: thin solid #ccc;
    box-shadow: 0 0 0px 1000px transparent inset;
  }

  .login-icon {
    margin-right: 10px;
    display: inline-block;
    width: 20px;
    height: 20px;
  }
</style>
