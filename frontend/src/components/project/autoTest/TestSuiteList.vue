<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}}</strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <router-link to="" style="text-decoration: none; color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 30px;">
          <el-button type="primary" class="el-icon-plus" @click="handleAdd">新增用例组</el-button>
        </el-form-item>
        <el-form-item style="margin-left: 5px">
          <el-button type="primary" class="el-icon-caret-right" :disabled="!hasSelected" @click="onTest">执行测试
          </el-button>
        </el-form-item>
        <el-select v-model="testEnv" style="margin-right: 20px" @visible-change='checkActiveTestEnv' clearable
                   placeholder="测试环境">
          <el-option v-for="(item,index) in testEnvs" :key="index+''" :label="item.name" :value="item._id"></el-option>
        </el-select>
        <div style="float: right; margin-right: 100px">
          <el-form-item>
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getTestSuiteList"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getTestSuiteList"> 查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>
    <!--用例组列表-->
    <!--列表-->
    <el-table @sort-change='sortChange' :data="testSuites" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column sortable='custom' prop="name" label="用例名称" min-width="40%" show-overflow-tooltip>
        <template slot-scope="scope">
          <el-icon name="name"></el-icon>
          <router-link :to="{ name: 'TestCaseList', params: {
                        test_suite_id: scope.row._id,
                        showWarmPrompt: true}}" style='text-decoration: none;'>
            {{ scope.row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="createAt" label="创建时间" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="createUser" label="创建者" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="lastUpdateTime" label="更新时间" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="lastUpdateUser" label="更新者" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="50%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button class="copyBtn" size="small" :loading="copyLoading"
                     @click="copyTestSuite(scope.$index, scope.row)">复制
          </el-button>
          <el-button
            type="info"
            size="small"
            :loading="statusChangeLoading"
            @click="handleChangeStatus(scope.$index, scope.row)">
            {{scope.row.status===false?'启用':'禁用'}}
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
        v-if="totalNum != 0"
        :page-sizes="[10, 20, 40]"
        :page-size="size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalNum">
      </el-pagination>
    </el-col>

    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="formVisible" :close-on-click-modal="false"
               style="width: 65%; left: 17.5%">
      <el-form :model="form" :rules="formRules" ref="form" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model.trim="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="4" v-model.trim="form.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="formVisible = false">取消</el-button>
        <el-button type="primary" @click.native="submit" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

  </section>
</template>

<script>
    import {getCookie} from "../../../utils/cookies";
    import {addTestSuite, copyTestSuite, getTestSuites, updateTestSuite} from "../../../api/testSuite";
    import {getTestEnvs} from "../../../api/testEnv";
    import {startAPITestBySuite} from "../../../api/execution";

    export default {
        name: "TestSuiteList",
        data() {
            return {
                testSuites: [],
                filters: {
                    name: ""
                },
                pageInfoIndex: -1,
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                currentPage: 1,
                totalNum: 0,
                listLoading: false,
                copyLoading: false,
                hasSelected: false,
                selects: [],//列表选中列
                delLoading: false,
                statusChangeLoading: false,
                testEnvs: [],
                testEnv: '',
                titleMap: {
                    add: '新增',
                    edit: '编辑'
                },
                dialogStatus: '',
                formVisible: false,//编辑界面是否显示
                editLoading: false,
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
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
                    description: ''
                },
                initForm: {
                    name: '',
                    description: ''
                }
            }
        },
        methods: {
            // 获取用例组列表
            getTestSuiteList() {
                let self = this;
                let params = {
                    skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                }
                this.queryTestSuites(params);
            },
            queryTestSuites(params) {
                this.listLoading = true;
                let self = this;
                if (self.filters.name.trim() !== '') {
                    params['name'] = self.filters.name.trim()
                }
                ;
                let header = {};
                getTestSuites(self.$route.params.project_id, params, header).then((res) => {
                    self.listLoading = false;
                    let {status, data} = res;
                    if (status === 'ok') {
                        self.testSuites = data.rows;
                        self.totalNum = data.totalNum;
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '用例列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                })
            },
            handleSizeChange(val) {
                let self = this;
                // self.$store.commit('setApiCaseSuitePageInfo', {size: val, projectId: self.$route.params.project_id})
                // self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
                // self.size = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].size) || 10
                let params = {
                    skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryTestSuites(params);
            },
            handleCurrentChange(val) {
                let self = this;
                // self.$store.commit('setApiCaseSuitePageInfo', {
                //     skip: (val - 1) * self.size,
                //     projectId: self.$route.params.project_id
                // })
                // self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
                // self.skip = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].skip) || 0
                // self.$store.commit('setApiCaseSuitePageInfo', {
                //     currentPage: self.currentPage,
                //     projectId: self.$route.params.project_id
                // })
                // self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
                let params = {
                    skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryTestSuites(params);
            },
            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then((res) => {
                    this.editLoading = true;
                    //NProgress.start();
                    let self = this;
                    let header = {};
                    let params = {"isDeleted": true}
                    updateTestSuite(self.$route.params.project_id, row._id, params, header).then((res) => {
                        self.editLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.success({
                                message: '删除成功',
                                center: true,
                            });
                            self.getTestSuiteList();
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                            self.getTestSuiteList()
                        }
                    }).catch(() => {
                        self.$message.error({
                            message: '删除用例失败,请稍后重试哦',
                            center: true
                        })
                        self.editLoading = false;
                    });
                })
            },
            //排序
            sortChange(column) {
                let self = this;
                // self.$store.commit('setApiCaseSuitePageInfo',{sortBy: column.prop, projectId: self.$route.params.project_id})
                // self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
                // self.sortBy = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].sortBy) || 'createAt'
                // self.$store.commit('setApiCaseSuitePageInfo',{order: column.order, projectId: self.$route.params.project_id})
                // self.order = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].order) || 'descending'
                self.sortBy = column.prop;
                self.order = column.order;
                let params = {
                    skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryTestSuites(params);
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
                updateTestSuite(this.$route.params.project_id, row._id, params, headers).then(res => {
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
                    self.getTestSuiteList()
                }).catch(() => {
                    self.$message.error({
                        message: '用例组状态更新失败,请稍后重试哦',
                        center: true
                    })
                    self.statusChangeLoading = false;
                    this.getTestSuiteList()
                });
            },
            selectsChange: function (selects) {
                if (selects.length > 0) {
                    this.selects = selects;
                    this.hasSelected = true
                } else {
                    this.hasSelected = false
                }
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
                                Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                            };
                            if (this.dialogStatus == 'add') {
                                let params = {
                                    name: self.form.name,
                                    description: self.form.description,
                                    createUser: unescape(getCookie('email').replace(/\\u/g, '%u')) || '未知用户'
                                };
                                addTestSuite(this.$route.params.project_id, params, headers).then((res) => {
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
                                        self.getTestSuiteList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getTestSuiteList()
                                    }
                                })
                            } else if (this.dialogStatus == 'edit') {
                                let params = {
                                    project_id: this.$route.params.project_id,
                                    name: self.form.name,
                                    description: self.form.description,
                                    lastUpdateUser: unescape(getCookie('email').replace(/\\u/g, '%u')) || '未知用户'
                                };
                                updateTestSuite(this.$route.params.project_id, self.form._id, params, headers).then(res => {
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
                                        self.getTestSuiteList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        })
                                        self.getTestSuiteList()
                                    }
                                })
                            } else {
                                self.$message.error({
                                    message: "系统出错",
                                    center: true,
                                });
                                self.getTestSuiteList()
                            }
                        });
                    }
                });
            },
            copyTestSuite(index, row) {
                let self = this;
                self.copyLoading = true;
                let header = {"Content-Type": "application/json"};
                let params = {};
                copyTestSuite(self.$route.params.project_id, row._id, params, header).then((res) => {
                    self.copyLoading = false;
                    let {status, data} = res;
                    if (status === 'ok') {
                        self.$message.success({
                            message: data,
                            center: true,
                        })
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                    self.getTestSuiteList()
                }).catch((error) => {
                    self.$message.error({
                        message: '用例组复制失败，请稍后重试哦~',
                        center: true,
                    });
                    self.copyLoading = false;
                })
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
            getTestEnvList() {
                let self = this;
                let header = {};
                let params = {status: true, projectId: self.$route.params.project_id};
                getTestEnvs(self.$route.params.project_id, params, header).then((res) => {
                    let {status, data} = res
                    if (status === 'ok') {
                        this.testEnvs = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '暂时无法获取环境列表，请稍后刷新重试~',
                        center: true,
                    });
                })
            },
            checkActiveTestEnv: function () {
                let self = this;
                if (self.testEnvs.length < 1) {
                    self.$message.warning({
                        message: '未找到「启用的测试环境」哦, 请前往「环境配置」进行设置',
                        center: true,
                    })
                }
            },
            onTest() {
                let self = this;
                if (self.testEnv) {
                    self.listLoading = true;
                    let suiteIds = self.selects.map(item => item._id);
                    let headers = {
                        "Content-Type": "application/json",
                    };
                    let params = {
                        testSuiteIdList: suiteIds,
                        testEnvId: self.testEnv,
                        projectId: self.$route.params.project_id,
                        executionUser: self.$store.getters.email,
                        executionMode: 'manual'
                    };
                    startAPITestBySuite(params, headers).then((res) => {
                        self.listLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.success({
                                message: '测试已成功启动，请稍后前往「测试报告」查看报告',
                                center: true,
                            });
                        } else {
                            self.$message.warning({
                                message: data,
                                center: true
                            });
                        }
                        self.getTestSuiteList();
                    }).catch((error) => {
                        self.$message.error({
                            message: '用例执行异常/超时，请稍后重试哦~',
                            center: true,
                        });
                        self.listLoading = false;
                        self.update = false;
                    })
                } else {
                    this.$message({
                        message: '请选择「测试环境」, 在「执行测试」按钮右边哦~',
                        center: true,
                        type: 'warning'
                    })
                }
            }
        },
        mounted() {
            this.getTestEnvList();
            this.getTestSuiteList();
        }
    }
</script>
f

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
