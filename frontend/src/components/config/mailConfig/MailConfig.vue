<template>
  <section>
    <!--页面title-->
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
          <el-button class="el-icon-plus" type="primary" @click="handleConfig">发件人配置</el-button>
        </el-form-item>
        <el-form-item style="margin-left: 20px" v-if="$store.getters.roles.includes('admin')">
          <el-button class="el-icon-plus" type="primary" @click="handleAdd">新增收件人分组</el-button>
        </el-form-item>
        <div style="float: right; margin-right: 95px">
          <el-form-item>
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getMailGroupList"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getMailGroupList">查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>

    <!--列表-->
    <el-table @sort-change='sortChange' :data="mailGroupList" :row-style="reportRowStyle"
              :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="10%">
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="30%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <router-link :to="{name:'MailListConfig',params:{mail_group_id: scope.row._id}}">
            {{scope.row.name}}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="30%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="30%">
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="30%" v-if="$store.getters.roles.includes('admin')">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="info" size="small" :loading="statusChangeLoading"
                     @click="handleChangeStatus(scope.$index, scope.row)">
            {{scope.row.status===false?'启用':'禁用'}}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--工具条-->
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

    <!--Mail编辑界面-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="mailGroupFormVisible" :close-on-click-modal="false"
               style="width: 70%; left: 15%">
      <el-form :model="mailGroupForm" :rules="mailGroupFormRules" ref="form" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="mailGroupForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="3" v-model="mailGroupForm.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="mailGroupFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="submitMailGroup" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

    <!--配置界面-->
    <el-dialog title="发件人配置" :visible.sync="configFormVisible" :close-on-click-modal="false"
               style="width: 70%; left: 15%">
      <el-form :model="configForm" label-width="120px" :rules="configFormRules" ref="configForm">
        <el-form-item label="名称" prop="name">
          <el-input v-model="configForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="发件人邮箱" prop="email">
          <el-input v-model.trim="configForm.email" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="邮箱授权码" prop='password'>
          <el-input v-model.trim="configForm.password" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="SMTP Server" prop='SMTPServer'>
          <el-input v-model.trim="configForm.SMTPServer" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="SMTP Port" prop='SMTPPort'>
          <el-input v-model.trim="configForm.SMTPPort" auto-complete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button :disabled="isMailSenderChecked" type="info" @click.native="testMailSender"
                   :loading="testMailSenderLoading">请先验证
        </el-button>
        <el-button @click.native="configFormVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!isMailSenderChecked" @click.native="configSubmit"
                   :loading="configLoading">提交
        </el-button>
      </div>
    </el-dialog>
  </section>
</template>

<script>
    import {getMailGroups, addMailGroup, updateMailGroup} from "../../../api/mail";
    import {getMailSender, addMailSender, updateMailSender, mailSenderTest} from "../../../api/mailSender";

    export default {
        name: "MailConfig",
        data() {
            return {
                filters: {
                    name: ''
                },
                mailGroupList: [],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
                statusChangeLoading: false,
                testMailSenderLoading: false,
                isMailSenderChecked: false,
                selects: [],//列表选中列

                // mail 编辑dialog
                titleMap: {
                    add: '新增',
                    edit: '编辑'
                },
                dialogStatus: '',
                mailGroupFormVisible: false,//编辑界面是否显示
                editLoading: false,
                //编辑界面数据
                mailGroupForm: {
                    name: '',
                    email: '',
                    description: ''
                },
                initForm: {
                    name: '',
                    email: '',
                    description: ''
                },
                mailGroupFormRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入描述', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ]
                },
                // 发件人Form
                configFormVisible: false,
                configLoading: false,
                //配置界面数据
                senderMailExisted: false,
                configForm: {
                    name: '',
                    email: '',
                    password: '',
                    SMTPServer: 'smtp.qq.com',
                    SMTPPort: 465
                },
                configFormRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur'}
                    ],
                    email: [
                        {required: true, message: '请输入邮箱地址', trigger: 'blur'},
                        {type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur'}
                    ],
                    password: [
                        {required: true, message: '请输入邮箱校验码', trigger: 'blur'},
                        {max: 256, message: '不能超过256个字符', trigger: 'blur'}
                    ],
                    SMTPServer: [
                        {required: true, message: '请输入SMTP Server', trigger: 'blur'},
                        {max: 50, message: '不能超过50个字符', trigger: 'blur'}
                    ],
                    SMTPPort: [
                        {required: true, message: '请输入SMTP Port', trigger: 'blur'},
                        {type: 'number', message: '请输入正确的Port', trigger: 'blur'}
                    ],
                },
            }
        },
        methods: {
            queryMailGroupList(params) {
                let self = this;
                getMailGroups(params).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.mailGroupList = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '邮件组列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            // 获取Mail列表
            getMailGroupList() {
                this.listLoading = true;
                let self = this;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order
                };
                if (self.filters.name.trim() !== '') {
                    params['name'] = self.filters.name.trim()
                }
                self.queryMailGroupList(params);
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                self.listLoading = true;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order
                };
                self.queryMailGroupList(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                self.listLoading = true;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order
                };
                self.queryMailGroupList(params);
            },
            //排序
            sortChange(column) {
                let self = this;
                self.listLoading = true;
                self.sortBy = column.prop;
                self.order = column.order;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order
                };
                self.queryMailGroupList(params);
            },
            handleChangeStatus: function (index, row) {
                let self = this;
                self.statusChangeLoading = true;
                let status = !row.status;
                let params = {
                    'status': status
                };
                let headers = {
                    "Content-Type": "application/json",
                };
                updateMailGroup(row._id, params, headers).then(res => {
                    let {status, data} = res;
                    self.statusChangeLoading = false;
                    if (status === 'ok') {
                        self.$message({
                            message: '状态变更成功',
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
                    self.getMailGroupList()
                }).catch(() => {
                    self.$message.error({
                        message: '邮件组状态更新失败,请稍后重试哦',
                        center: true
                    })
                    self.statusChangeLoading = false;
                    self.getMailGroupList()
                });
            },
            selectsChange: function (selects) {
                this.selects = selects;
            },
            // 修改table tr行的背景色
            reportRowStyle({row, rowIndex}) {
                if (!(row.status === true))
                    return 'background-color: #DDDDDD'
                else {
                    return ''
                }
            },
            ReportTableRow({row, rowIndex}) {
                return 'reportTableRow';
            },
            //显示Mail编辑界面
            handleEdit: function (index, row) {
                this.mailGroupFormVisible = true;
                this.mailGroupForm = Object.assign({}, this.mailGroupForm, row);
                this.dialogStatus = 'edit'
            },
            //显示Mail新增界面
            handleAdd: function () {
                this.mailGroupFormVisible = true;
                this.mailGroupForm = Object.assign({}, this.mailGroupForm, this.initForm);
                this.dialogStatus = 'add';
            },
            //显示配置邮箱界面
            handleConfig: function () {
                this.isMailSenderChecked = false;
                this.configFormVisible = true;
            },
            //提交修改
            submitMailGroup: function () {
                let self = this;
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.listLoading = true;
                            let headers = {
                                "Content-Type": "application/json",
                            };
                            if (this.dialogStatus == 'add') {
                                let params = {
                                    name: self.mailGroupForm.name.trim(),
                                    description: self.mailGroupForm.description.trim(),
                                    createUser: self.$store.getters.email || 'anonymous'
                                };
                                addMailGroup(params, headers).then((res) => {
                                    let {status, data} = res;
                                    self.listLoading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '添加成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['form'].resetFields();
                                        self.mailGroupFormVisible = false;
                                        self.getMailGroupList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['form'].resetFields();
                                        self.mailGroupFormVisible = false;
                                        self.getMailGroupList()
                                    }
                                })
                            } else if (this.dialogStatus == 'edit') {
                                let params = {
                                    name: self.mailGroupForm.name.trim(),
                                    email: self.mailGroupForm.email,
                                    description: self.mailGroupForm.description.trim(),
                                    lastUpdateUser: self.$store.getters.email || 'anonymous'
                                };
                                updateMailGroup(self.mailGroupForm._id, params, headers).then(res => {
                                    let {status, data} = res;
                                    self.listLoading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['form'].resetFields();
                                        self.mailGroupFormVisible = false;
                                        self.getMailGroupList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        })
                                        self.getMailGroupList()
                                    }
                                })
                            } else {
                                self.$message.error({
                                    message: "系统出错",
                                    center: true,
                                });
                                self.getMailGroupList()
                            }
                        });
                    }
                });
            },
            // 获取MailSender, 一般只配置一个，所以默认取第一个设置form
            getSender() {
                this.configLoading = true;
                let params = {};
                getMailSender(params).then((res) => {
                    let {status, data} = res;
                    this.configLoading = false;
                    if (status === 'ok') {
                        if (data.totalNum > 0) {
                            this.senderMailExisted = true;
                            this.configForm = data.rows[0];
                        }
                    } else {
                        this.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    this.$message.error({
                        message: '发件人获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    this.configLoading = false;
                });
            },
            testMailSender() {
                this.testMailSenderLoading = true;
                let self = this;
                let params = {
                    email: self.configForm.email,
                    password: self.configForm.password,
                    SMTPServer: self.configForm.SMTPServer,
                    SMTPPort: self.configForm.SMTPPort
                };
                mailSenderTest(params).then((res) => {
                    let {status, data} = res;
                    self.testMailSenderLoading = false;
                    if (status === 'ok') {
                        self.$message.success({
                            message: data,
                            center: true,
                        });
                        self.isMailSenderChecked = true;
                    } else {
                        self.$message.warning({
                            message: data,
                            center: true,
                        });
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '发件人邮箱测试失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.testMailSenderLoading = false;
                });
            },
            //配置发件人
            configSubmit() {
                this.$refs.configForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.configLoading = true;
                            let params = {
                                name: self.configForm.name.trim(),
                                email: self.configForm.email,
                                password: self.configForm.password,
                                SMTPServer: self.configForm.SMTPServer,
                                SMTPPort: self.configForm.SMTPPort
                            };
                            let header = {
                                "Content-Type": "application/json",
                            };
                            if (this.senderMailExisted) {
                                params['lastUpdateUser'] = self.$store.getters.email || 'anonymous'
                                updateMailSender(this.configForm._id, params, header).then((res) => {
                                    let {status, data} = res;
                                    self.configLoading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '配置成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['configForm'].resetFields();
                                        self.configFormVisible = false;
                                        self.getSender()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['configForm'].resetFields();
                                        self.configFormVisible = false;
                                        self.getSender()
                                    }
                                });
                            } else {
                                params['createUser'] = self.$store.getters.email || 'anonymous'
                                addMailSender(params, header).then((res) => {
                                    let {status, data} = res;
                                    self.configLoading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '配置成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['configForm'].resetFields();
                                        self.configFormVisible = false;
                                        self.getSender()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['configForm'].resetFields();
                                        self.configFormVisible = false;
                                        self.getSender()
                                    }
                                });
                            }
                        });
                    }
                });
            },
        },
        created() {
            this.getMailGroupList();
            this.getSender();
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
