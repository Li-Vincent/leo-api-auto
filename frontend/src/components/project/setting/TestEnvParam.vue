<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}} <span v-if="testEnvName"> - 环境: {{testEnvName}}</span> </strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 35px">
          <el-button class="el-icon-plus" type="primary" @click="handleAdd">新增参数</el-button>
        </el-form-item>
        <div style="float: right; margin-right: 95px">
          <el-form-item>
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getEnvParamList"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getEnvParamList"> 查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>

    <!--参数列表-->
    <el-table @sort-change='sortChange' :data="testEnvParams" :row-style="reportRowStyle"
              :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="参数名" min-width="20%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column prop="paramValue" label="参数值" min-width="40%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="35" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="15%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createUser" label="创建者" min-width="15%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="15%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="15%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="30%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
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
      <el-form :model="form" :rules="formRules" ref="form" label-width="80px">
        <el-form-item label="参数名" prop="name">
          <el-input placeholder="请输入参数名" v-model.trim="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="参数值" prop='paramValue'>
          <el-input placeholder="请输入参数值" v-model="form.paramValue" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop='description'>
          <el-input placeholder="请输入描述..." type="textarea" :rows="5" v-model="form.description"></el-input>
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
    import {getTestEnvInfo} from "../../../api/testEnv";
    import {getTestEnvParams, addTestEnvParam, updateTestEnvParam} from "../../../api/testEnvParam";

    export default {
        name: "TestEnvParam",
        data() {
            return {
                testEnvName: '',
                filters: {
                    name: ''
                },
                testEnvParams: [],
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
                dialogStatus: '',
                formVisible: false,  //dialog是否显示
                loading: false,
                formRules: {
                    name: [
                        {required: true, message: '请输入参数名', trigger: 'blur'},
                        {min: 1, max: 30, message: '长度在 1 到 30 个字符', trigger: 'blur'}
                    ],
                    paramValue: [
                        {required: true, message: '请输入参数值', trigger: 'blur'},
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
                    paramValue: '',
                    description: ''
                },
                initForm: {
                    name: '',
                    paramValue: '',
                    description: ''
                }
            }
        },
        methods: {
            // 获取参数列表
            queryEnvParams(params) {
                this.listLoading = true;
                let self = this;
                if (self.filters.name.trim() !== '') {
                    params['name'] = self.filters.name.trim()
                }
                let header = {};
                getTestEnvParams(this.$route.params.project_id, this.$route.params.test_env_id, params, header).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.testEnvParams = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '参数列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            getEnvParamList() {
                let self = this;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    projectId: self.$route.params.project_id,
                    testEnvId: self.$route.params.test_env_id
                };
                this.queryEnvParams(params);
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    projectId: self.$route.params.project_id,
                    testEnvId: self.$route.params.test_env_id
                };
                this.queryEnvParams(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    projectId: self.$route.params.project_id,
                    testEnvId: self.$route.params.test_env_id
                };
                this.queryEnvParams(params);
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
                    order: self.order,
                    projectId: self.$route.params.project_id,
                    testEnvId: self.$route.params.test_env_id
                };
                this.queryEnvParams(params);
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
                    updateTestEnvParam(this.$route.params.project_id, row._id, params, headers).then(res => {
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
                        self.getEnvParamList()
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
                updateTestEnvParam(this.$route.params.project_id, row._id, params, headers).then(res => {
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
                    self.getEnvParamList()
                }).catch(() => {
                    self.$message.error({
                        message: '环境状态更新失败,请稍后重试哦',
                        center: true
                    })
                    self.statusChangeLoading = false;
                    self.getEnvParamList()
                });
            },
            //显示编辑界面
            handleEdit: function (index, row) {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, row);
                this.dialogStatus = 'edit';
            },
            //显示新增界面
            handleAdd: function () {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, this.initForm);
                this.dialogStatus = 'add';
            },
            // 提交修改
            submit: function () {
                let self = this;
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.loading = true;
                            let headers = {
                                "Content-Type": "application/json",
                            };
                            //NProgress.start();
                            if (this.dialogStatus == 'edit') {
                                let params = {
                                    project_id: this.$route.params.project_id,
                                    name: self.form.name,
                                    paramValue: self.form.paramValue,
                                    description: self.form.description.trim(),
                                    lastUpdateUser: self.$store.getters.email || 'anonymous'
                                };
                                updateTestEnvParam(this.$route.params.project_id, self.form._id, params, headers).then(res => {
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
                                        self.getEnvParamList();
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        })
                                        self.getEnvParamList();
                                    }
                                })
                            } else if (this.dialogStatus == 'add') {
                                let params = {
                                    name: self.form.name,
                                    paramValue: self.form.paramValue,
                                    description: self.form.description.trim(),
                                    createUser: self.$store.getters.email || 'anonymous',
                                };
                                addTestEnvParam(this.$route.params.project_id, this.$route.params.test_env_id, params, headers).then((res) => {
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
                                        self.getEnvParamList();
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getEnvParamList();
                                    }
                                });
                            } else {
                                self.$message.error({
                                    message: "系统出错",
                                    center: true,
                                });
                                self.getEnvParamList()
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
            this.getEnvParamList();
            getTestEnvInfo(this.$route.params.project_id, this.$route.params.test_env_id).then((res) => {
                if (res.status === 'ok') {
                    this.testEnvName = res.data.name;
                }
            })
        }
    }
</script>

<style lang="scss" scoped>
  .title {
    float: left;
    color: #475669;
    font-size: 25px;
    margin: 10px 5px;
    font-family: Arial;

    span {
      font-size: 20px;
    }
  }

  .return-list {
    margin-top: 0px;
    margin-bottom: 10px;
    margin-left: 20px;
    border-radius: 25px;
  }
</style>
