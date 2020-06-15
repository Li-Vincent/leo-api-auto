<template>
  <div class="leo-login">
    <div class="leo-login-main">
      <el-form class="login-form" :model="form" ref="form" :rules="formRules">
        <el-row type="flex" justify="center" :gutter="10">
          <el-col>
            <el-form-item>
              <div class="title">用户注册</div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row type="flex" justify="center" :gutter="10">
          <el-col>
            <el-form-item label="用户邮箱:" label-width="83px" prop="email">
              <el-input v-model="form.email"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row type="flex" justify="center" :gutter="10">
          <el-col>
            <el-form-item label="登录密码:" prop="password" label-width="83px">
              <el-input v-model="form.password"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col>
            <el-form-item label="用户角色:" prop="roles" label-width="83px">
              <el-checkbox-group v-for="(role,index) in rolesOption" v-model="form.roles" :key="index">
                <el-checkbox :label="role.name">{{role.description}}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-button id="login-checkout" class="login-btn" :loading="registerLoading" type="primary" @click="submit">注册
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script>
    import {register} from "../../api/user";

    export default {
        name: 'Register',
        data() {
            const validatePass = (rule, value, callback) => {
                if (!value) {
                    callback(new Error('请输入密码'));
                } else if (value.toString().length < 6 || value.toString().length > 18) {
                    callback(new Error('密码长度为6 - 18个字符'))
                } else {
                    callback();
                }
            };
            return {
                registerLoading: false,
                form: {
                    email: '',
                    password: '',
                    roles: [],
                },
                formRules: {
                    email: [{required: true, type: 'email', trigger: 'blur'}],
                    password: [{required: true, validator: validatePass, trigger: 'blur'}],
                    roles: [{required: true}]
                },
                rolesOption: [
                    {'name': 'admin', 'description': '超级管理员'},
                    {'name': 'project', 'description': '项目管理员'},
                    {'name': 'user', 'description': '普通用户'}
                ]
            }
        },
        methods: {
            async submit() {
                this.$refs.form.validate(valid => {
                    if (valid) {
                        let header = {};
                        let params = {email: this.form.email, password: this.form.password, roles: this.form.roles}
                        this.registerLoading = true;
                        register(params, header).then((res) => {
                            this.registerLoading = false;
                            if (res.status === 'ok') {
                                this.$message({
                                    message: res.data,
                                    center: true,
                                })
                                this.$router.push({name: 'Users'})
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
            }
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
