<template>
  <div>    <!--页面title-->
    <strong class="title">{{$route.meta.title}}</strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 35px" v-if="$store.getters.roles.includes('admin')">
          <router-link :to="{ name: 'Register'}" style="text-decoration: none;color: aliceblue;">
            <el-button class="el-icon-plus" type="primary">新增用户</el-button>
          </router-link>
        </el-form-item>
        <div style="float: right; margin-right: 95px">
          <el-form-item>
            <el-input v-model.trim="filters.email" placeholder="邮箱" @keyup.enter.native="getUsers"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getUsers"> 查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>

    <!--用户列表-->
    <el-table @sort-change='sortChange' :data="users" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="_id" label="ID" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="roleNames" label="角色" min-width="50%" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{formatRoles(scope.row.roleNames)}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="active" label="状态" min-width="10%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.active" src="../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.active" src="../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="30%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="info" size="small" :loading="statusChangeLoading"
                     @click="handleChangeStatus(scope.$index, scope.row)">
            {{scope.row.active===false?'启用':'禁用'}}
          </el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--翻页工具条-->
    <el-col :span="24" class="toolbar">
      <el-pagination
        style="float: right"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :page-sizes="[10, 20, 40]"
        :page-size="size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalNum">
      </el-pagination>
    </el-col>


    <!--添加/编辑/查看 界面-->
    <el-dialog title="编辑用户" :visible.sync="editFormVisible" :close-on-click-modal="false"
               style="width: 70%; left: 15%">
      <el-form :model="editForm" :rules="editFormRules" ref="editForm" label-width="80px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model.trim="editForm.email" disabled></el-input>
        </el-form-item>
        <el-form-item label="角色" prop='roleNames'>
          <el-checkbox-group v-for="(role,index) in rolesOption" v-model="editForm.roleNames" :key="index">
            <el-checkbox :label="role.name">{{role.description}}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="项目权限" prop='userProjects'>
          <el-checkbox-group v-for="project in projectsOption" v-model="editForm.userProjects" :key="project._id">
            <el-checkbox :label="project._id">{{project.name}}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <span>初始密码: {{initPassword}}</span>
        <el-button type="primary" @click.native="resetPwd">重置密码</el-button>
        <br>
        <br>
        <el-button type="primary" @click.native="changeProjects" :loading="editLoading">修改项目权限</el-button>
        <el-button type="primary" @click.native="changeUserRoles" :loading="editLoading">修改角色</el-button>
        <el-button @click.native="editFormVisible = false">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
    import {getUserList, updateUserStatus, changeRoles, resetPassword, deleteUser, changeUserProjects} from "../../api/user";
    import {getProjects} from "../../api/project";


    export default {
        name: "UserList",
        data() {
            return {
                filters: {
                    email: ''
                },
                users: [],
                roles: {
                    'admin': '超级管理员',
                    'project': '项目管理员',
                    'user': '普通用户'
                },
                rolesOption: [
                    {'name': 'admin', 'description': '超级管理员'},
                    {'name': 'project', 'description': '项目管理员'},
                    {'name': 'user', 'description': '普通用户'}
                ],
                projectsOption:[],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
                statusChangeLoading: false,
                selects: [],//列表选中列

                editFormVisible: false,//dialog是否显示
                editLoading: false,
                editFormRules: {
                    email: [{required: true, type: 'email', trigger: 'blur'}],
                    roles: [{required: true, message: '请选择角色', trigger: 'blur'}]
                },
                //编辑界面数据
                editForm: {
                    email: '',
                    password: '',
                    roleNames: [],
                    userProjects:[]
                },
                initPassword: 'leo-api-test'
            }
        },
        methods: {
            queryUsers(params) {
                this.listLoading = true;
                let self = this;
                if (self.filters.email.trim() !== '') {
                    params['email'] = self.filters.email.trim()
                }
                getUserList(params).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.users = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '用户列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            getUsers() {
                let self = this;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryUsers(params);
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryUsers(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryUsers(params);
            },
            handleChangeStatus: function (index, row) {
                let self = this;
                self.statusChangeLoading = true;
                let active = !row.active;
                let params = {
                    'email': row.email,
                    'active': active
                };
                let headers = {
                    "Content-Type": "application/json",
                };
                updateUserStatus(params, headers).then(res => {
                    let {status, data} = res;
                    self.statusChangeLoading = false;
                    if (status === 'ok') {
                        self.$message({
                            message: data,
                            center: true,
                            type: 'success'
                        });
                        row.status = !row.status;
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                    self.getUsers()
                }).catch(() => {
                    self.$message.error({
                        message: '用户状态更新失败,请稍后重试哦',
                        center: true
                    })
                    self.statusChangeLoading = false;
                    self.getUsers()
                });
            },
            //排序
            sortChange(column) {
                let self = this;
                self.sortBy = column.prop;
                self.order = column.order;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryUsers(params);
            },
            selectsChange: function (selects) {
                this.selects = selects;
            },
            // 修改table tr行的背景色
            reportRowStyle({row, rowIndex}) {
                if (!(row.active === true))
                    return 'background-color: #DDDDDD'
                else {
                    return ''
                }
            },
            ReportTableRow({row, rowIndex}) {
                return 'reportTableRow';
            },
            formatRoles(roles) {
                let roleNames = '';
                roleNames = roles.map(item => this.roles[item]).join(" / ");
                return roleNames
            },
            handleEdit: function (index, row) {
                this.editFormVisible = true;
                console.log(row)
                this.editForm = Object.assign({}, this.editForm, row);
            },
            changeUserRoles() {
                this.$refs.editForm.validate(valid => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            let header = {};
                            let params = {
                                email: this.editForm.email,
                                roleNames: this.editForm.roleNames
                            }
                            this.editLoading = true;
                            changeRoles(this.editForm.email, params, header).then((res) => {
                                this.editLoading = false;
                                if (res.status === 'ok') {
                                    this.$message({
                                        message: res.data,
                                        center: true,
                                    })
                                } else {
                                    this.$message.error({
                                        message: res.data,
                                        center: true,
                                    })
                                }
                                this.$refs['editForm'].resetFields();
                                this.editFormVisible = false;
                                this.getUsers()
                            });
                        });
                    } else {
                        this.$message.error({
                            message: "表单验证失败",
                            center: true,
                        })
                    }
                })
            },
            resetPwd() {
                this.$confirm('确认提交吗？', '提示', {}).then(() => {
                    let header = {};
                    let params = {
                        email: this.editForm.email,
                        password: this.initPassword
                    }
                    this.editLoading = true;
                    resetPassword(this.editForm.email, params, header).then((res) => {
                        this.editLoading = false;
                        if (res.status === 'ok') {
                            this.$message({
                                message: res.data,
                                center: true,
                            })
                        } else {
                            this.$message.error({
                                message: res.data,
                                center: true,
                            })
                        }
                        this.$refs['editForm'].resetFields();
                        this.editFormVisible = false;
                        this.getUsers()
                    });
                });
            },
            handleDel: function (index, row) {
                this.$confirm('确认删除用户吗？', '提示', {}).then(() => {
                    let self = this;
                    self.statusChangeLoading = true;
                    let params = {
                        'users': [row.email]
                    };
                    let headers = {
                        "Content-Type": "application/json",
                    };
                    deleteUser(params, headers).then(res => {
                        let {status, data} = res;
                        self.statusChangeLoading = false;
                        if (status === 'ok') {
                            self.$message({
                                message: data,
                                center: true,
                                type: 'success'
                            });
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                        }
                        self.getUsers()
                    }).catch(() => {
                        self.$message.error({
                            message: '删除用户失败,请稍后重试哦',
                            center: true
                        })
                        self.statusChangeLoading = false;
                        self.getUsers()
                    });
                })
            },
            getAllProjects(){
                let params = {};
                let header = {};
                getProjects(params, header).then((res) => {
                    let {status, data} = res;
                    if (status === "ok") {
                        this.projectsOption = data.rows
                    } else {
                        this.$message.error({
                            message: data,
                            center: true
                        })
                    }
                }).catch((err) => {
                    this.$message.err({
                        message: '项目获取失败，请稍后刷新重试哦~',
                        center: true
                    });
                })
            },
            changeProjects() {
                this.$confirm('确认提交吗？', '提示', {}).then(() => {
                    let header = {};
                    let params = {
                        email: this.editForm.email,
                        userProjects: this.editForm.userProjects
                    }
                    this.editLoading = true;
                    changeUserProjects(this.editForm.email, params, header).then((res) => {
                        this.editLoading = false;
                        if (res.status === 'ok') {
                            this.$message({
                                message: res.data,
                                center: true,
                            })
                        } else {
                            this.$message.error({
                                message: res.data,
                                center: true,
                            })
                        }
                        this.$refs['editForm'].resetFields();
                        this.editFormVisible = false;
                        this.getUsers()
                    });
                });
            },
        },
        created() {
            this.getUsers()
            this.getAllProjects()
        }
    }

</script>

<style lang="scss" scoped>
  .title {
    width: 200px;
    float: left;
    color: #475669;
    font-size: 25px;
    margin: 10px 5px;
    font-family: Arial;
  }

  .return-list {
    margin-top: 0px;
    margin-bottom: 10px;
    margin-left: 20px;
    border-radius: 25px;
  }
</style>
