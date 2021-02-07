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
        <el-form-item style="margin-left: 50px;">
          <el-button type="primary" class="el-icon-plus" @click="handleAdd">新增用例组</el-button>
        </el-form-item>
        <!--        case import-->
        <el-form-item style="margin-left: 10px">
          <el-tooltip class="item" effect="dark" content="只接收 xls / xlsx 哦~" placement="top-start">
            <el-upload
              :action="getImportUrl"
              :before-upload="onBeforeUpload"
              :on-success="onSuccessUpload"
              :on-error="onErrorUpload"
              :on-progress="onProgressUpload"
              :show-file-list="false"
              :with-credentials="true"
              :data="importExtraData"
            >
              <el-button class="el-icon-upload2" :disabled="importLoading" type="primary"
                         style="margin-left: 5px">用例导入
              </el-button>
            </el-upload>
          </el-tooltip>
        </el-form-item>
        <el-form-item style="margin-left: 5px">
          <el-tooltip class="item" effect="dark" content="导出格式是 xlsx 哦~" placement="top-start">
            <el-button class="el-icon-download" :loading="exportLoading" :disabled="!hasSelected"
                       type="primary"
                       style="margin-right: 3px" @click="exportCases"> 用例导出
            </el-button>
          </el-tooltip>
        </el-form-item>

        <div style="float: right; margin-right: 20px">
          <el-form-item>
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getTestSuiteList"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getTestSuiteList"> 查询</el-button>
          </el-form-item>
        </div>
        <div style="float: right; margin-right: 30px">
          <el-select v-model="testEnv" style="margin-right: 20px" @visible-change='checkActiveTestEnv' clearable
                     placeholder="测试环境">
            <el-option v-for="(item,index) in testEnvs" :key="index+''" :label="item.name"
                       :value="item._id"></el-option>
          </el-select>
          <el-form-item>
            <el-button type="primary" class="el-icon-caret-right" :disabled="!hasSelected" @click="onTest">执行测试
            </el-button>
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
      <el-table-column sortable='custom' prop="name" label="用例组名称" min-width="40%" show-overflow-tooltip>
        <template slot-scope="scope">
          <router-link :to="{ name: 'TestCaseList', params: {
                        test_suite_id: scope.row._id,
                        showWarmPrompt: true}}" style='text-decoration: none;'>
            {{ scope.row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column sortable='custom' prop="priority" label="优先级" min-width="10%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="service" label="服务" min-width="10%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="sprint" label="Sprint" min-width="10%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="storyId" label="StoryID" min-width="10%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="testCaseId" label="TestCaseID" min-width="10%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="createAt" label="创建时间" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="createUser" label="创建者" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="40%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button class="copyBtn" size="small" :loading="copyLoading" @click="copySuite(scope.$index, scope.row)">复制
          </el-button>
          <el-button type="info" size="small" :loading="statusChangeLoading"
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
        :current-page.sync="currentPage"
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
          <el-input v-model="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="4" v-model="form.description"></el-input>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="form.priority" placeholder="请选择">
            <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="所属服务" prop="service">
          <el-input v-model.trim="form.service" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="Sprint" prop="sprint">
          <el-input v-model.trim="form.sprint" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="storyId" prop="storyId">
          <el-input v-model.trim="form.storyId" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="testCaseId" prop="testCaseId">
          <el-input v-model.trim="form.testCaseId" auto-complete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="formVisible = false">取消</el-button>
        <el-button type="primary" @click.native="submit" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

    <!--    for export case download-->
    <a class="js-download-doc" :href="downloadLink" :download="downloadName" v-show="false"/>
  </section>
</template>

<script>
    import {addTestSuite, copyTestSuite, getTestSuites, updateTestSuite} from "../../../api/testSuite";
    import {getEnvConfigs} from "../../../api/envConfig";
    import {startAPITestBySuite} from "../../../api/execution";
    import {exportTestCases} from '../../../api/testCase';
    import moment from "moment";

    export default {
        name: "TestSuiteList",
        data() {
            return {
                downloadLink: '',
                downloadName: '',
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
                importLoading: false,
                exportLoading: false,
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
                        {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入描述', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ],
                    priority: [
                        {required: true, message: '请输入优先级，P1 or P2', trigger: 'blur'},
                        {min: 2, max: 2, message: '请输入 P1 or P2', trigger: 'blur'}
                    ],
                    service: [
                        {required: false, message: '请输入服务', trigger: 'blur'},
                        {max: 30, message: '所属服务', trigger: 'blur'}
                    ],
                    sprint: [
                        {required: false, message: '请输入Sprint', trigger: 'blur'},
                        {max: 30, message: '用例所属Sprint，30字符以内', trigger: 'blur'}
                    ],
                    storyId: [
                        {required: false, message: '请输入Story ID', trigger: 'blur'},
                        {max: 30, message: '用例story ID，30字符以内', trigger: 'blur'}
                    ],
                    testCaseId: [
                        {required: false, message: '请输入Test Case ID', trigger: 'blur'},
                        {max: 30, message: '用例Test Case ID，30字符以内', trigger: 'blur'}
                    ]
                },
                //编辑界面数据
                form: {
                    name: '',
                    description: ''
                },
                initForm: {
                    name: '',
                    description: '',
                    priority: 'P1'
                },
                priorityOptions: [{label: "P1", value: "P1"},
                    {label: "P2", value: "P2"}],
                // For import cases.
                importExtraData: {
                    projectId: this.$route.params.project_id,
                    user: this.$store.getters.email || '未知anonymous'
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
                self.$store.dispatch('pageInfo/setTestSuitePageInfo', {
                    size: val,
                    projectId: self.$route.params.project_id
                })
                self.size = val
                self.listLoading = true;
                let params = {
                    skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryTestSuites(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.listLoading = true;
                self.$store.dispatch('pageInfo/setTestSuitePageInfo', {
                    skip: (val - 1) * self.size,
                    currentPage: val,
                    projectId: self.$route.params.project_id
                })
                self.skip = (val - 1) * self.size
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
                                    name: self.form.name.trim(),
                                    priority: self.form.priority.trim(),
                                    service: self.form.service,
                                    sprint: self.form.sprint,
                                    storyId: self.form.storyId,
                                    testCaseId: self.form.testCaseId,
                                    createUser: self.$store.getters.email || '未知anonymous'
                                };
                                if (self.form.description) {
                                    params['description'] = self.form.description.trim();
                                }
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
                                    name: self.form.name.trim(),
                                    priority: self.form.priority.trim(),
                                    service: self.form.service,
                                    sprint: self.form.sprint,
                                    storyId: self.form.storyId,
                                    testCaseId: self.form.testCaseId,
                                    description: self.form.description.trim(),
                                    lastUpdateUser: self.$store.getters.email || '未知anonymous'
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
            copySuite(index, row) {
                let self = this;
                this.$confirm('确认复制吗？', '提示', {}).then(() => {
                    self.copyLoading = true;
                    let header = {"Content-Type": "application/json"};
                    let params = {
                        createUser: self.$store.getters.email || '未知anonymous'
                    };
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
                });
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
                let params = {status: true};
                getEnvConfigs(params, header).then((res) => {
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
                                message: data,
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
            },

            // For Import Test Cases
            onBeforeUpload(file) {
                let fileSuffix = file.name.substring(file.name.lastIndexOf(".") + 1)
                if (fileSuffix === 'xls' || fileSuffix === 'xlsx') {
                    return file
                } else {
                    this.$message.warning('只接收 .xls / .xlsx 文件哦 ~ ')
                    return false
                }
            },
            onSuccessUpload(response) {
                let {status, data} = response
                if (status === 'ok') {
                    this.$message.success(data)
                } else {
                    this.$message.error(data)
                }
                this.getTestSuiteList()
                this.importLoading = false
            },
            onProgressUpload(event) {
                this.importLoading = true
            },
            onErrorUpload(err) {
                this.importLoading = false
                this.$message.error(err)
            },

            // For Export Test Case
            async exportCases() {
                let self = this;
                self.exportLoading = true;
                let testSuiteIds = self.selects.map(item => item._id);
                let header = {
                    "Content-Type": "application/json"
                };
                let params = JSON.stringify({
                    "testSuiteIds": testSuiteIds
                });
                exportTestCases(params, header).then((res) => {
                    const blob = new Blob([res])
                    self.downloadLink = window.URL.createObjectURL(blob)
                    self.downloadName = `测试用例_${moment().format('YYYY-MM-DD_HH-mm-ss')}.xlsx`
                    self.$nextTick(() => {
                        self.$el.querySelector('.js-download-doc').click()
                        window.URL.revokeObjectURL(this.downloadLink)
                        self.exportLoading = false;
                        self.$message.success({
                            message: '用例导出成功',
                            center: true,
                        });
                    })
                }).catch((error) => {
                    console.log("Export Cases error:", error)
                    self.$message.error({
                        message: '用例导出失败，请稍后重试哦~',
                        center: true,
                    });
                    self.exportLoading = false;
                })
            },
        },
        computed: {
            getImportUrl() {
                return `${process.env.CASE_IMPORT_URI}`
            }
        },
        mounted() {
            this.getTestEnvList();
            this.getTestSuiteList();
        },
        created() {
            this.pageInfoIndex = this.$store.getters.testSuitePageInfo.findIndex(ele => ele.projectId === this.$route.params.project_id)
            this.size = this.pageInfoIndex === -1 ?
                10 : (this.$store.getters.testSuitePageInfo[this.pageInfoIndex]
                && this.$store.getters.testSuitePageInfo[this.pageInfoIndex].size) || 10
            this.skip = this.pageInfoIndex === -1 ?
                0 : (this.$store.getters.testSuitePageInfo[this.pageInfoIndex]
                && this.$store.getters.testSuitePageInfo[this.pageInfoIndex].skip) || 0
            this.sortBy = this.pageInfoIndex === -1 ?
                'createAt' : (this.$store.getters.testSuitePageInfo[this.pageInfoIndex]
                && this.$store.getters.testSuitePageInfo[this.pageInfoIndex].sortBy) || 'createAt'
            this.order = this.pageInfoIndex === -1 ?
                'descending' : (this.$store.getters.testSuitePageInfo[this.pageInfoIndex]
                && this.$store.getters.testSuitePageInfo[this.pageInfoIndex].order) || 'descending'
            this.currentPage = this.pageInfoIndex === -1 ?
                1 : (this.$store.getters.testSuitePageInfo[this.pageInfoIndex]
                && this.$store.getters.testSuitePageInfo[this.pageInfoIndex].currentPage) || 1
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

  .copyBtn {
    color: #fff;
    background-color: #33CC00;
    border-color: #33CC00;
  }
</style>
