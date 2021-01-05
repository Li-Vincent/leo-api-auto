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
          <el-button class="el-icon-plus" type="primary" @click="handleAdd"> 新增测试环境</el-button>
        </el-form-item>
        <el-form-item style="margin-left: 30px">
          <router-link :to="{name:'DBConfig'}" style="text-decoration: none;color: aliceblue;">
            <el-button type="primary"><i class="fa fa-database"></i> DB配置</el-button>
          </router-link>
        </el-form-item>
        <div style="float: right; margin-right: 95px">
          <el-form-item>
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getEnvConfigList"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getEnvConfigList"> 查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>

    <!--环境列表-->
    <el-table @sort-change='sortChange' :data="envConfigs" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="_id" label="ID" min-width="30%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="15%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="protocol" label="协议" min-width="15%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="domain" label="域名" min-width="35%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createUser" label="创建者" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="30%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button
            type="info"
            size="small"
            :loading="statusChangeLoading"
            @click="handleChangeStatus(scope.$index, scope.row)">
            {{scope.row.status===false?'启用':'禁用'}}
          </el-button>
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
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="formVisible"
               :close-on-click-modal="false"
               style="width: 60%; left: 20%">
      <el-form :model="form" :rules="formRules" ref="form" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input placeholder="请输入环境名称" v-model="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item  label="HTTP协议" prop='protocol'>
          <el-select v-model="form.protocol" placeholder="HTTP协议">
            <el-option v-for="(item,index) in ProtocolOptions" :key="index+''" :label="item.label"
                       :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="域名" prop='domain'>
          <el-input placeholder="www.test.com/www.service-${service}.com" v-model.trim="form.domain"
                    auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop='description'>
          <el-input placeholder="请输入环境描述..." type="textarea" :rows="5" v-model="form.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="formVisible = false">取消</el-button>
        <el-button type="primary" @click.native="submit" :loading="loading">提交</el-button>
      </div>
    </el-dialog>
  </section>
</template>

<script>
    import {addEnvConfig, getEnvConfigs, updateEnvConfig} from "../../api/envConfig";

    export default {
        name: "EnvConfig",
        data() {
            return {
                filters: {
                    name: ''
                },
                envConfigs: [],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
                statusChangeLoading: false,
                selects: [],//列表选中列

                titleMap: {
                    add: '新增',
                    edit: '编辑'
                },
                ProtocolOptions: [
                    {value: 'HTTP', label: 'HTTP'},
                    {value: 'HTTPS', label: 'HTTPS'}
                ],
                dialogStatus: '',
                formVisible: false,//dialog是否显示
                loading: false,
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur'}
                    ],
                    protocol: [
                        {required: true, message: '请选择协议', trigger: 'blur'},
                        {min: 4, max: 5, message: 'HTTP or HTTPS', trigger: 'blur'}
                    ],
                    domain: [
                        {required: true, message: '请输入域名', trigger: 'blur'},
                        {min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入描述', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ]
                },
                //编辑界面数据
                form: {
                    name: '',
                    protocol: 'HTTP',
                    domain: '',
                    description: ''
                },
                initForm: {
                    name: '',
                    protocol: 'HTTP',
                    domain: '',
                    description: ''
                }
            }
        },
        methods: {
            // 获取环境列表
            queryEnvConfigs(params) {
                this.listLoading = true;
                let self = this;
                if (self.filters.name.trim() !== '') {
                    params['name'] = self.filters.name.trim()
                }
                let header = {};
                getEnvConfigs(params, header).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.envConfigs = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '环境列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            getEnvConfigList() {
                let self = this;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryEnvConfigs(params);
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
                this.queryEnvConfigs(params);
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
                this.queryEnvConfigs(params);
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
                this.queryEnvConfigs(params);
            },
            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let self = this;
                    let params = {
                        'isDeleted': true
                    };
                    let headers = {
                        "Content-Type": "application/json",
                    };
                    updateEnvConfig(row._id, params, headers).then(res => {
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message({
                                message: '删除成功',
                                center: true,
                                type: 'success'
                            })
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                        }
                        self.getEnvConfigList()
                    });
                });
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
                updateEnvConfig(row._id, params, headers).then(res => {
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
                    self.getEnvConfigList()
                }).catch(() => {
                    self.$message.error({
                        message: '环境状态更新失败,请稍后重试哦',
                        center: true
                    })
                    self.statusChangeLoading = false;
                    self.getEnvConfigList()
                });
            },
            //显示编辑界面
            handleEdit: function (index, row) {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, row);
                this.dialogStatus = 'edit'
            },
            //显示新增界面
            handleAdd: function () {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, this.initForm);
                this.dialogStatus = 'add';
            },
            //提交修改
            submit: function () {
                let self = this;
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.loading = true;
                            //NProgress.start();
                            let headers = {
                                "Content-Type": "application/json",
                            };
                            if (this.dialogStatus == 'add') {
                                let params = {
                                    name: self.form.name.trim(),
                                    protocol: self.form.protocol,
                                    domain: self.form.domain,
                                    description: self.form.description.trim(),
                                    createUser: this.$store.getters.email || 'anonymous'
                                };
                                addEnvConfig(params, headers).then((res) => {
                                    let {status, data} = res;
                                    self.loading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '添加成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getEnvConfigList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getEnvConfigList()
                                    }
                                })
                            } else if (this.dialogStatus == 'edit') {
                                let params = {
                                    name: self.form.name.trim(),
                                    protocol: self.form.protocol,
                                    domain: self.form.domain,
                                    description: self.form.description.trim(),
                                    lastUpdateUser: this.$store.getters.email || 'anonymous'
                                };
                                updateEnvConfig(self.form._id, params, headers).then(res => {
                                    let {status, data} = res;
                                    self.loading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getEnvConfigList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        })
                                        self.getEnvConfigList()
                                    }
                                })
                            } else {
                                self.$message.error({
                                    message: "系统出错",
                                    center: true,
                                });
                                self.getEnvConfigList()
                            }
                        });
                    }
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
            }
        },
        mounted() {
            this.getEnvConfigList();
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
