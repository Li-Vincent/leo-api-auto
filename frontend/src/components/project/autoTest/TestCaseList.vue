<template>
  <section>
    <strong class="title">{{$route.meta.title}} <span v-if="testSuiteName"> - Suite: {{testSuiteName}}</span> </strong>
    <!--新增用例 弹框-->
    <el-dialog width=80% title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false"
               style="width:75%; left: 12.5%">
      <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
        <el-row :gutter="16">
          <el-col :span="18">
            <el-form-item label="用例名称" prop="name">
              <el-input v-model="addForm.name" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="服务名" prop="service">
              <el-input v-model.trim="addForm.service" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="请求方法" prop='requestMethod'>
              <el-select v-model="addForm.requestMethod" placeholder="请选择">
                <el-option v-for="item in methodOptions" :key="item.value" :label="item.label" :value="item.value">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="接口路由" prop='route'>
              <el-input v-model.trim="addForm.route" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="6" v-model="addForm.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="addFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
      </div>
    </el-dialog>

    <!--临时变量 弹框-->
    <el-dialog  title="临时变量" :visible.sync="tempParamVisible" :close-on-click-modal="false">
        <el-tag type="warning">变量失效时间：{{tempParams.expiresTime}}</el-tag>
        <el-table :data="tempParams.params">
            <el-table-column prop="name" label="参数名" min-width="30%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="value" label="参数值"  sortable='custom' show-overflow-tooltip>
            </el-table-column>
        </el-table>
    </el-dialog>

    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true">
        <router-link :to="{ name: 'TestSuiteList', params: { project_id: this.$route.params.project_id } }"
                     style='text-decoration: none;color: aliceblue;'>
          <el-button class="return-list">
            <i class="el-icon-d-arrow-left" return-list style="margin-right: 5px"></i>用例组列表
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 30px">
          <el-button class="el-icon-plus" type="primary" @click="handleAdd"> 新建接口用例</el-button>
        </el-form-item>
        <el-form-item style="margin-left: 30px">
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getTestCaseList"></el-input>
        </el-form-item>
        <el-form-item >
            <el-button type="primary" class="el-icon-search" @click="getTestCaseList"> 查询</el-button>
        </el-form-item>
        <el-form-item style="margin-left: 30px;">
          <el-button type="primary" class="el-icon-search" @click="showTempParams">查看临时变量</el-button>
        </el-form-item>
        <el-form-item style="float: right;  margin-right: 50px">
            <el-select v-model="testEnv" style="margin-right: 20px" @visible-change='checkActiveTestEnv' clearable
                     placeholder="测试环境">
                <el-option
                v-for="(item,index) in testEnvs"
                :key="index+''"
                :label="item.name"
                :value="item._id">
                </el-option>
            </el-select>
            <el-tooltip placement="top">
                <div slot="content">
                　  <span>执行顺序：批量测试完全按照勾选顺序执行</span>
                </div>
                <el-button type="primary" class="el-icon-caret-right" :disabled="!hasSelected" @click="batchTest()"> 批量测试</el-button>
            </el-tooltip>
        </el-form-item>
      </el-form>
    </el-col>

    <!--列表-->
    <el-table @sort-change='sortChange' @selection-change="selectsChange" :data="caseList" :row-style="reportRowStyle"
              :row-class-name="ReportTableRow" highlight-current-row v-loading="listLoading" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="接口用例名称" min-width="40%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <router-link :to="{ name: 'EditTestCase', params: {test_case_id: scope.row._id}}"
                       style='text-decoration: none;color: #000000;'>{{ scope.row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="route" label="Request" min-width="40%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <span class="HttpStatus">{{scope.row.requestMethod}}</span>
          <span style="font-size: 16px">{{scope.row.route}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="用例描述" min-width="20%" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{scope.row.description}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="service" label="Service" min-width="20%" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{scope.row.service}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sequence" label="Sequence" min-width="25%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <el-input v-model.number="scope.row.sequence" type="number" auto-complete="false"
                    @keyup.enter.native="updateSequence(scope.$index, scope.row)" style="width: 70px"></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="25%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="result" label="测试结果" min-width="25%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <span
            v-show="!scope.row.hasOwnProperty('lastManualResult') || scope.row.lastManualResult.status!='ok'&&scope.row.lastManualResult.status!='failed'">尚无测试结果</span>
          <span v-show="scope.row.lastManualResult && scope.row.lastManualResult.status==='ok'"
                style="color: #11b95c;cursor:pointer;" @click="showResult(scope.row)">通过,查看详情</span>
          <span v-show="scope.row.lastManualResult && scope.row.lastManualResult.status==='failed'"
                style="color: #cc0000;cursor:pointer;" @click="showResult(scope.row)">失败,查看详情</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="20%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="80%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" :loading="testLoading" @click="onTest(scope.$index, scope.row)">测试
          </el-button>
          <el-button class="copyBtn" size="small" :loading="copyLoading" @click="copyCase(scope.$index, scope.row)">复制
          </el-button>
          <el-button type="info" size="small" :loading="statusChangeLoading"
                     @click="handleChangeStatus(scope.$index, scope.row)"> {{scope.row.status===false?'启用':'禁用'}}
          </el-button>
          <el-button type="danger" size="small" :loading="delLoading" @click="handleDel(scope.$index, scope.row)">删除
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
        :current-page.sync="currentPage"
        v-if="totalNum != 0"
        :page-sizes="[10, 20, 40]"
        :page-size="size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalNum">
      </el-pagination>
    </el-col>

    <!--测试结果-->
    <el-dialog title="测试结果" :visible.sync="testResultStatus" :close-on-click-modal="false">
      <div slot="title" class="header-title">
        <span style="font-size: 28px">测试结果</span>
        <span v-show="result.name" style="font-size: 20px"> - {{ result.name }}</span>
      </div>
      <div class="test-result">
        <div v-show="result.env">测试环境 : {{result.env}}</div>
        <div>请求地址 : {{result.url}}</div>
        <div>请求方式 : {{result.requestMethod}}</div>
        <div>请求开始时间 : {{result.testStartTime}}</div>
        <div>延迟调用时间 : {{result.delaySeconds}}s</div> 
        <div>请求所用时间 : {{result.elapsedSeconds}}s</div> 
        <div>用例执行时间 : {{result.spendTimeInSec}}s</div>
        <div class="divider-line"></div>
        <div style="font-size: 25px;">数据初始化:</div>
        <div v-for="(item,index) in result.dataInitResult">
          <pre>{{item}}</pre>
        </div>
        <div v-if="!result.dataInitResult || result.dataInitResult && Object.keys(result.dataInitResult).length <= 0">
          (无需数据初始化)
        </div>
        <div class="divider-line"></div>
        <div style="font-size: 25px;">请求头部:</div>
        <div v-for="(value, key) in result.headers" :key="key">{{key}}:&nbsp;&nbsp;{{value}}</div>
        <div v-if="!result.headers || result.headers && Object.keys(result.headers).length <= 0">
          (无任何header)
        </div>
        <div class="divider-line"></div>
        <div style="font-size: 25px;">Cookies:</div>
        <div v-for="(item,index) in result.cookies">{{item.name}} = {{item.value}}</div>
        <div v-if="!result.cookies || result.cookies && result.cookies.length <= 0 ">(无任何Cookie)
        </div>
        <div class="divider-line"></div>
        <div style="font-size: 25px;">请求参数:</div>
        <div v-show="result.filePath">FilePath:  {{result.filePath}}</div>
        <div v-show="result.requestBody" class="resultStyle resultData">
          <pre>{{result.requestBody}}</pre>
        </div>
        <div v-show="!result.requestBody" class="resultStyle resultData">无</div>
        <div class="divider-line"></div>
        <div style="font-size: 25px;">预期结果:</div>
        <div>HTTP状态码: {{result.checkResponseCode}}</div>
        <div>请求耗时: {{result.checkSpendSeconds}}</div>
        <div>JSON正则校验:
          <pre>{{result.checkResponseBody}}</pre>
          <span v-show="!result.checkResponseBody">(无)</span>
        </div>
        <div>数值校验:
          <pre>{{result.checkResponseNumber}}</pre>
          <span v-show="!result.checkResponseNumber">(无)</span>
        </div>
        <div class="divider-line"></div>
        <div style="font-size: 25px;">实际结果:</div>
        <div>HTTP状态码: {{result.responseStatusCode}}</div>
        <div>请求耗时: {{result.elapsedSeconds}}s</div>
        <div>实际返回内容:</div>
        <div v-show="result.responseData" class="resultStyle resultData">
          <pre>{{result.responseData}}</pre>
        </div>
        <div v-show="!result.responseData" class="resultStyle resultData">(无返回内容)</div>
        <div class="divider-line"></div>
        <div style="font-size: 25px">测试结论:</div>
        <div v-for="(item,index) in result.testConclusion" v-show="result.testConclusion" :key="index"
             style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 88%;
                    word-break: break-all;line-height:25px">
          结论：{{item.resultType}} <br/>
          原因：{{item.reason}}
        </div>
        <div v-show="!result.testConclusion"
             style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px;text-align: center">
          无测试结论
        </div>
      </div>
    </el-dialog>
  </section>
</template>

<script>
    import {getTestCases, getCaseLastResult, updateTestCase, addTestCase, copyTestCase} from "../../../api/testCase";
    import {getSuiteTempParams} from "../../../api/tempSuiteParam";
    import {getTestSuiteInfo} from "../../../api/testSuite";
    import {getEnvConfigs} from "../../../api/envConfig";
    import {startAPITestByCase} from "../../../api/execution";
    import moment from "moment";

    export default {
        name: "TestCaseList",
        data() {
            let checkRoute = (rule, value, callback) => {
                if (value != "" && value != null) {
                    if (value.indexOf('/') == 0) {
                        callback()
                    } else {
                        callback(new Error('请输入路由(如: /chat)'))
                        this.$message.warning({
                            message: '路由格式不正确!',
                            center: true,
                        });
                    }
                } else {
                    callback()
                }
            };
            return {
                testSuiteName: '',
                methodOptions: [{label: "GET", value: "GET"},
                    {label: "POST", value: "POST"},
                    {label: "PUT", value: "PUT"},
                    {label: "DELETE", value: "DELETE"},
                    {label: "OPTIONS", value: "OPTIONS"},
                    {label: "PATCH", value: "PATCH"},
                    {label: "HEAD", value: "HEAD"}],
                caseList: [],
                listLoading: false,
                copyLoading: false,
                testLoading: false,
                statusChangeLoading: false,
                delLoading: false,
                pageInfoIndex: -1,
                size: 10,
                skip: 0,
                sortBy: 'sequence',
                order: 'ascending',
                currentPage: 1,
                totalNum: 0,

                testEnv: '',
                testEnvs: [],

                tempParams:{},

                hasSelected: false,
                selects: [],//列表选中列

                testResultStatus: false,
                result: {},

                tempParamVisible: false,
                addFormVisible: false,
                activeIndex: "",

                //新增界面数据
                addForm: {
                    name: '',
                    description: '',
                    requestMethod: '',
                    route: '',
                    service: ''
                },
                addLoading: false,
                addFormRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
                    ],
                    requestMethod: [
                        {required: true, message: '请选择请求方法', trigger: 'blur'}
                    ],
                    route: [
                        {required: true, message: '请输入路由(如:/chat)', trigger: 'blur'},
                        {validator: checkRoute, trigger: 'blur'}
                    ],
                    service: [
                        {required: false, message: '请输入服务名', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入描述', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ]
                },
                filters: {
                    name: ''
                }
            }
        },
        methods: {
            handleSelect(key, keyPath) {
                this.activeIndex = key;
            },
            queryTestCases(params) {
                let self = this;
                this.listLoading = true;
                if (self.filters.name.trim() !== '') {
                    params['name'] = self.filters.name.trim()
                }
                let header = {};
                getTestCases(self.$route.params.project_id, self.$route.params.test_suite_id, params, header).then((res) => {
                    self.listLoading = false;
                    let {status, data} = res;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.caseList = data.rows;
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '接口用例列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                })
            },
            async getTestCaseList() {
                let self = this;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id, testSuiteId: self.$route.params.test_suite_id
                };
                this.queryTestCases(params);
            },
            showTempParams() {
                let self = this;
                getSuiteTempParams(self.$route.params.test_suite_id).then((res) => {
                    let {status, data} = res;
                    if (status === 'ok') {
                        if (data.params) {
                            self.tempParams.params = data.params;
                            self.tempParams.expiresTime = moment(data.expires_time).format("YYYY-MM-DD HH:mm:ss");
                            this.tempParamVisible = true;
                        } else {
                            self.$message.warning({
                                message: "当前用例组还没有设置临时变量",
                                center: true,
                            })
                        }
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    console.log(error)
                    self.$message.error({
                        message: '用例组临时变量获取失败，请稍后重试哦~',
                        center: true,
                    });
                })
                
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
                updateTestCase(this.$route.params.project_id, this.$route.params.test_suite_id, row._id, params, headers).then(res => {
                    let {status, data} = res;
                    self.statusChangeLoading = false;
                    if (status == 'ok') {
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
                    self.getTestCaseList()
                }).catch(() => {
                    self.$message.error({
                        message: '用例状态更新失败,请稍后重试哦',
                        center: true
                    })
                    self.statusChangeLoading = false;
                    this.getTestCaseList()
                });
            },
            handleSizeChange(val) {
                let self = this;
                self.$store.dispatch('pageInfo/setTestCasePageInfo', {
                    size: val,
                    testSuiteId: self.$route.params.test_suite_id
                })
                self.size = val
                self.listLoading = true;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id, testSuiteId: self.$route.params.test_suite_id
                };
                this.queryTestCases(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.listLoading = true;
                self.$store.dispatch('pageInfo/setTestCasePageInfo', {
                    skip: (val - 1) * self.size,
                    currentPage: val,
                    testSuiteId: self.$route.params.test_suite_id
                })
                self.skip = (val - 1) * self.size
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id, testSuiteId: self.$route.params.test_suite_id
                };
                this.queryTestCases(params);
            },
            //排序
            sortChange(column) {
                let self = this;
                self.listLoading = true;
                self.sortBy = column.prop;
                self.order = column.order;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id, testSuiteId: self.$route.params.test_suite_id
                };
                this.queryTestCases(params);
            },
            //新增用例
            addSubmit: function () {
                this.$refs.addForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.addLoading = true;
                            let params = {
                                name: self.addForm.name.trim(),
                                requestMethod: self.addForm.requestMethod,
                                route: self.addForm.route,
                                service: self.addForm.service,
                                description: self.addForm.description.trim(),
                                createUser: self.$store.getters.email,
                            };
                            let header = {};
                            addTestCase(self.$route.params.project_id, self.$route.params.test_suite_id, params, header).then((res) => {
                                self.addLoading = false;
                                let {status, data} = res;
                                if (status === 'ok') {
                                    self.$message.success({
                                        message: '保存成功',
                                        center: true,
                                    });
                                    self.$refs['addForm'].resetFields();
                                    self.addFormVisible = false;
                                    self.getTestCaseList();
                                } else {
                                    self.$message.error({
                                        message: data,
                                        center: true,
                                    })
                                }
                            }).catch(() => {
                                self.$message.error({
                                    message: '新增接口用例失败,请稍后重试哦',
                                    center: true
                                })
                                self.addLoading = false;
                            });
                        });
                    }
                });
            },
            checkSequence(number) {
                return new RegExp("^[1-9][0-9]*$").test(number);
            },
            updateSequence(index, row) {
                this.$confirm('确认更新执行顺序吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    if (!this.checkSequence(row.sequence)) {
                        this.$message.error({
                            message: "请输入正整数",
                            center: true
                        })
                        this.getTestCaseList();
                        return
                    }
                    let self = this;
                    self.listLoading = true;
                    let params = {
                        sequence: row.sequence,
                    };
                    let header = {};
                    updateTestCase(self.$route.params.project_id, self.$route.params.test_suite_id, row._id, params, header).then((res) => {
                        self.listLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.success({
                                message: '更新执行顺序成功',
                                center: true
                            })
                            self.getTestCaseList();
                        } else {
                            self.$message.error({
                                message: data,
                                center: true
                            })
                            self.getTestCaseList();
                        }
                    }).catch(() => {
                        self.$message.error({
                            message: '更新失败,请稍后重试哦',
                            center: true
                        })
                        self.listLoading = false;
                    });
                });
            },
            handleDel(index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    let self = this;
                    self.delLoading = true;
                    let params =
                        {
                            isDeleted: true,
                        };
                    let header = {};
                    updateTestCase(self.$route.params.project_id, self.$route.params.test_suite_id, row._id, params, header).then((res) => {
                        self.delLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.success({
                                message: '删除成功',
                                center: true
                            })
                            self.getTestCaseList();
                        } else {
                            self.$message.error({
                                message: data,
                                center: true
                            })
                            self.getTestCaseList();
                        }
                    }).catch(() => {
                        self.$message.error({
                            message: '删除失败,请稍后重试哦',
                            center: true
                        })
                        self.delLoading = false;
                    });
                });
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
            //显示新增界面
            handleAdd: function () {
                this.addFormVisible = true;
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
            selectsChange: function (selects) {
                if (selects.length > 0) {
                    this.selects = selects;
                    this.hasSelected = true;
                } else {
                    this.hasSelected = false;
                }
            },
            warmPrompt() {
                let self = this;
                let showPrompt = self.$router.history.current.params.showWarmPrompt;
                if (showPrompt) {
                    self.$message.info({
                        message: '测试用例默认按照「Sequence」和「创建时间」正序执行~',
                        center: true,
                    })
                }
            },
            onTest(index, row) {
                if (this.testEnv) {
                    row.testStatus = true;
                    let self = this;
                    self.testLoading = true;
                    let headers = {"Content-Type": "application/json"};
                    let params = {
                        testCaseIdList: [row._id],
                        testEnvId: self.testEnv,
                        executionUser: self.$store.getters.email,
                        executionMode: 'manual'
                    };
                    startAPITestByCase(params, headers).then((res) => {
                        self.testLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.getTestCaseList()
                            row.testStatus = false;
                        } else {
                            self.$message.warning({
                                message: data,
                                center: true,
                            })
                        }
                        self.getTestCaseList()
                        row.testStatus = false;
                    }).catch((error) => {
                        self.$message.error({
                            message: '接口用例执行异常/超时，请稍后重试哦~',
                            center: true,
                        });
                        self.testLoading = false;
                        self.getTestCaseList()
                        row.testStatus = false;
                    })
                } else {
                    this.$message({
                        message: '请选择测试环境, 在测试按钮上方哦~',
                        center: true,
                        type: 'warning'
                    })
                }
            },
            batchTest(){
                if (this.testEnv) {
                    let self = this;
                    self.testLoading = true;
                    let testCaseIdList = self.selects.map(item => item._id);
                    let headers = {"Content-Type": "application/json"};
                    let params = {
                        testCaseIdList: testCaseIdList,
                        testEnvId: self.testEnv,
                        executionUser: self.$store.getters.email,
                        executionMode: 'manual'
                    };
                    startAPITestByCase(params, headers).then((res) => {
                        self.testLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.getTestCaseList()
                        } else {
                            self.$message.warning({
                                message: data,
                                center: true,
                            })
                        }
                        self.getTestCaseList()
                    }).catch((error) => {
                        self.$message.error({
                            message: '接口用例执行异常/超时，请稍后重试哦~',
                            center: true,
                        });
                        self.testLoading = false;
                        self.getTestCaseList()
                    })
                } else {
                    this.$message({
                        message: '请选择测试环境, 在「批量测试」左侧哦~',
                        center: true,
                        type: 'warning'
                    })
                }
            },
            showResult(row) {
                this.listLoading = true;
                this.result["name"] = row.name;
                this.getResult(row._id);
            },
            getResult(test_case_id) {
                let self = this;
                getCaseLastResult(test_case_id).then((res) => {
                    if (res.status === 'ok') {
                        this.listLoading = false;
                        let testResult = res.data;
                        self.result["env"] = testResult.env;
                        self.result["url"] = testResult.testCaseDetail.url;
                        self.result["requestMethod"] = testResult.testCaseDetail.requestMethod;
                        self.result["delaySeconds"] = testResult.testCaseDetail.delaySeconds;
                        if (testResult.testCaseDetail.filePath) {
                            self.result["filePath"] = testResult.testCaseDetail.filePath;
                        }
                        if (testResult.dataInitResult && testResult.dataInitResult.length > 0) {
                            testResult.dataInitResult.forEach(item => {
                                try {
                                    if (item.query && typeof (item.query) == "string") {
                                        item.query = JSON.parse(item.query);
                                    }
                                    if (item.set && typeof (item.set) == "string") {
                                        item.set = JSON.parse(item.set);
                                    }
                                } catch (e) {
                                    console.log(e)
                                }
                            })
                        }
                        self.result["dataInitResult"] = testResult.dataInitResult;
                        self.result["headers"] = testResult.headers;
                        self.result["cookies"] = testResult.testCaseDetail.cookies;
                        self.result["requestBody"] = testResult.testCaseDetail.requestBody;
                        if (testResult.checkResponseCode) {
                            self.result["checkResponseCode"] = testResult.checkResponseCode;
                        } else {
                            self.result["checkResponseCode"] = '无'
                        }
                        if (testResult.checkSpendSeconds) {
                            self.result["checkSpendSeconds"] = testResult.checkSpendSeconds + " s";
                        } else {
                            self.result["checkSpendSeconds"] = '无'
                        }
                        if (testResult.checkResponseBody && !(testResult.checkResponseBody.length === 1 && testResult.checkResponseBody[0]['regex'].trim() === '')) {
                            self.result["checkResponseBody"] = testResult.checkResponseBody;
                        } else {
                            self.result["checkResponseBody"] = '无'
                        }
                        if (testResult.checkResponseNumber && !(testResult.checkResponseNumber.length === 1 && testResult.checkResponseNumber[0]['expression'].trim() === '')) {
                            self.result["checkResponseNumber"] = testResult.checkResponseNumber;
                        } else {
                            self.result["checkResponseNumber"] = '无'
                        }
                        self.result["result"] = testResult.status;
                        self.result["responseStatusCode"] = testResult.responseStatusCode;
                        try {
                            self.result["responseData"] = JSON.parse(testResult.responseData);
                            //self.result["responseData"] = JSON.parse(testResult.responseData.replace(/'/g, "\"")
                            // .replace(/None/g, "null").replace(/True/g, "true").replace(/False/g, "false"));
                        } catch (error) {
                            self.result["responseData"] = testResult.responseData;
                        }
                        self.result["testConclusion"] = testResult.testConclusion;
                        self.result["testStartTime"] = moment(testResult.testStartTime).format("YYYY年MM月DD日HH时mm分ss秒");
                        self.result["spendTimeInSec"] = testResult.spendTimeInSec;
                        self.result["elapsedSeconds"] = testResult.elapsedSeconds;
                        self.testResultStatus = true;
                    } else {
                        self.$message.warning({
                            message: res.data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '用例执行结果获取失败，请稍后重试哦~',
                        center: true,
                    });
                });
            },
            copyCase(index, row) {
                let self = this;
                this.$confirm('确认复制吗？', '提示', {}).then(() => {
                    self.copyLoading = true;
                    let header = {"Content-Type": "application/json"};
                    let params = {
                        createUser: self.$store.getters.email || 'anonymous'
                    };
                    copyTestCase(self.$route.params.project_id, self.$route.params.test_suite_id, row._id, params, header).then((res) => {
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
                        self.getTestCaseList()
                    }).catch((error) => {
                        self.$message.error({
                            message: '用例复制失败，请稍后重试哦~',
                            center: true,
                        });
                        self.copyLoading = false;
                    })
                });
            }
        },
        mounted() {
            this.getTestCaseList();
            this.getTestEnvList();
            getTestSuiteInfo(this.$route.params.project_id, this.$route.params.test_suite_id).then((res) => {
                if (res.status === 'ok') {
                    this.testSuiteName = res.data.name;
                }
            });
            this.warmPrompt();
        },
        created() {
            this.pageInfoIndex = this.$store.getters.testCasePageInfo.findIndex(ele => ele.testSuiteId === this.$route.params.test_suite_id)
            this.size = this.pageInfoIndex === -1 ?
                10 : (this.$store.getters.testCasePageInfo[this.pageInfoIndex]
                && this.$store.getters.testCasePageInfo[this.pageInfoIndex].size) || 10
            this.skip = this.pageInfoIndex === -1 ?
                0 : (this.$store.getters.testCasePageInfo[this.pageInfoIndex]
                && this.$store.getters.testCasePageInfo[this.pageInfoIndex].skip) || 0
            this.sortBy = this.pageInfoIndex === -1 ?
                'sequence' : (this.$store.getters.testCasePageInfo[this.pageInfoIndex]
                && this.$store.getters.testCasePageInfo[this.pageInfoIndex].sortBy) || 'sequence'
            this.order = this.pageInfoIndex === -1 ?
                'ascending' : (this.$store.getters.testCasePageInfo[this.pageInfoIndex]
                && this.$store.getters.testCasePageInfo[this.pageInfoIndex].order) || 'ascending'
            this.currentPage = this.pageInfoIndex === -1 ?
                1 : (this.$store.getters.testCasePageInfo[this.pageInfoIndex]
                && this.$store.getters.testCasePageInfo[this.pageInfoIndex].currentPage) || 1
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

  .HttpStatus {
    border-radius: 25px;
    padding: 10px;
    box-sizing: border-box;
    color: #fff;
    font-size: 15px;
    background-color: $--color-primary;
    text-align: center;
    margin-right: 10px;
  }

  .test-result {
    height: 800px;
    margin-top: -20px;
    overflow: auto;
    overflow-x: hidden;
    border: 1px solid #e6e6e6;
    font-size: 14px;
    line-height: 25px;

    div {
      margin-left: 2%;
      margin-top: 10px;
      margin-bottom: 10px;
      word-wrap: break-word; //文本过长自动换行
    }

    .title {
      font-weight: bold;
      font-size: 14px;
    }

    pre {
      white-space: pre-wrap;
      white-space: -moz-pre-wrap;
      white-space: -o-pre-wrap;
      word-wrap: break-word;
    }

    .resultData {
      overflow: auto;
      display: block;
      overflow-x: hidden;
      padding: 0.5em;
      background: #333;
      color: white;
      border: 1px solid #e6e6e6;
      word-break: break-all;
      line-height: 25px;
      width: 90%;
    }

    .divider-line {
      margin-top: 20px;
      margin-bottom: 10px;
      border: 1px solid #e6e6e6;
      width: 92%;
      position: relative
    }
  }

  .copyBtn {
    color: #fff;
    background-color: #33CC00;
    border-color: #33CC00;
  }

</style>
