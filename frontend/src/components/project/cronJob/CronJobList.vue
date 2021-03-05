<template>
  <section style="margin:10px 35px">
    <!--页面title-->
    <strong class="title">{{$route.meta.title}}</strong>

    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 35px">
          <el-button class="el-icon-plus" type="primary" @click="handleAdd"> 新增定时任务</el-button>
        </el-form-item>
        <div style="float: right; margin-right: 100px">
          <el-form-item>
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getCronJobList"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getCronJobList"> 查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>

    <!--定时任务列表-->
    <el-table @sort-change='sortChange' :row-style="reportRowStyle" :row-class-name="ReportTableRow" :data="cronJobs"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="_id" label="任务ID" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="name" label="任务名称" min-width="30%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="25%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="createUser" label="创建者" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="25%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="15%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="next_run_time" label="next执行时间" min-width="25%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%">
        <template slot-scope="scope">
          <img v-show="scope.row.status!=='PAUSED'" src="../../../assets/imgs/icon-yes.svg"/>
          <img v-show="scope.row.status==='PAUSED'" src="../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="50%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          <el-button
            type="info"
            size="small"
            :loading="statusChangeLoading"
            @click="handleChangeStatus(scope.$index, scope.row)">
            {{scope.row.status==='PAUSED'?'启动':'停用'}}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--编辑-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="formVisible" width="70%" :close-on-click-modal="false"
               style="width:70%;left: 15%">
      <el-form :model="form" :rules="formRules" ref="form" label-width="120px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" auto-complete="off"></el-input>
        </el-form-item>

        <el-form-item label="用例组" prop="testSuiteIdList">
          <el-select style="width: 60%;" v-model="form.testSuiteIdList" @visible-change="checkActiveTestSuite"
                     clearable multiple auto-complete="off">
            <el-option v-for="(item,index) in testSuites" :key="index+''" :label="item.name"
                       :value="item._id"></el-option>
          </el-select>
          <el-checkbox style="margin-left: 50px" label='是否执行禁用的用例(组)' v-model="form.includeForbidden">
          </el-checkbox>
        </el-form-item>
        <el-form-item label="测试环境" prop="testEnvId">
          <el-select
            v-model="form.testEnvId"
            @visible-change="checkActiveTestEnv"
            clearable
            auto-complete="off">
            <el-option v-for="(item,index) in testEnvs" :key="index" :label="item.name" :value="item._id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="触发类型" prop="triggerType">
          <el-select clearable v-model.trim="form.triggerType" @change="triggerTypeChange" auto-complete="off">
            <el-option v-for="(item,index) in TriggerTypes" :key="index+''" :label="item.name"
                       :value="item.value"></el-option>
          </el-select>
        </el-form-item>

        <transition name="el-zoom-in-top">
          <div class="form-item-sub form-item-short"
               v-if="form.triggerType.toString()==='interval' || form.triggerType.toString()==='date'">
            <el-form-item v-if="form.triggerType.toString()==='interval'" label="间隔/秒" prop="interval">
              <el-input style="width:50%" v-model.trim="form.interval" type="number" auto-complete="off"></el-input>
            </el-form-item>

            <el-form-item v-if="form.triggerType.toString()==='date'" label="具体日期" prop="runDate">
              <el-date-picker
                :picker-options="pickerOptions"
                v-model.trim="form.runDate"
                type="datetime"
                placeholder="请选择触发日期">
              </el-date-picker>
            </el-form-item>
          </div>
        </transition>
        <!--通知策略-->
        <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;">
          <!--企业微信通知-->
          <el-form-item label="企业微信通知" label-width="120px" prop="enableWXWorkNotify">
            <el-radio v-model="form.enableWXWorkNotify" :label="true">是</el-radio>
            <el-radio v-model="form.enableWXWorkNotify" :label="false">否</el-radio>
          </el-form-item>
          <transition name="el-zoom-in-top">
            <div class="form-item-sub form-item-short" v-if="form.enableWXWorkNotify">
              <el-form-item label="企业微信APIKey" prop="WXWorkAPIKey">
                <el-input style="width:80%"
                          placeholder="请填写企业微信群机器人WebhookAPIKey，如: 6789f5f7-736a-423b-b140-98d8324cb8cb"
                          v-model.trim="form.WXWorkAPIKey" auto-complete="off"></el-input>
              </el-form-item>
              <el-form-item v-show="form.enableWXWorkNotify" label="通知策略">
                <el-radio v-model="form.alwaysWXWorkNotify" :label="true">执行成功也发送通知</el-radio>
                <el-radio v-model="form.alwaysWXWorkNotify" :label="false">执行失败才发送通知</el-radio>
              </el-form-item>
              <el-form-item v-show="form.enableWXWorkNotify" label="提醒手机号列表">
                <el-select style="width: 80%;" v-model.trim="form.WXWorkMentionMobileList"
                           multiple clearable filterable default-first-option allow-create
                           placeholder="手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人">
                </el-select>
              </el-form-item>
            </div>
          </transition>
          <!--钉钉通知-->
          <el-form-item label="钉钉通知" label-width="120px" prop="enableDingTalkNotify">
            <el-radio v-model="form.enableDingTalkNotify" :label="true">是</el-radio>
            <el-radio v-model="form.enableDingTalkNotify" :label="false">否</el-radio>
          </el-form-item>

          <transition name="el-zoom-in-top">
            <div class="form-item-sub form-item-short" v-if="form.enableDingTalkNotify">
              <el-form-item label-width="120px" label="AccessToken" prop="DingTalkAccessToken">
                <el-input style="width:80%" placeholder="请填写钉钉群机器人DingTalkAccessToken"
                          v-model.trim="form.DingTalkAccessToken" auto-complete="off"></el-input>
              </el-form-item>
              <el-form-item label-width="120px" label="钉钉加签密钥" prop="DingTalkSecret">
                <el-input style="width:80%" placeholder="钉钉机器人安全设置勾选加签后须填写Secret,如不勾选可不填"
                          v-model.trim="form.DingTalkSecret" auto-complete="off"></el-input>
              </el-form-item>
              <el-form-item v-show="form.enableDingTalkNotify" label-width="120px" label="通知策略">
                <el-radio v-model="form.alwaysDingTalkNotify" :label="true">执行成功也发送通知</el-radio>
                <el-radio v-model="form.alwaysDingTalkNotify" :label="false">执行失败才发送通知</el-radio>
              </el-form-item>
              <el-form-item v-show="form.enableDingTalkNotify" label-width="120px" label="提醒手机号列表">
                <el-select style="width: 80%;" v-model.trim="form.DingTalkAtMobiles"
                           multiple clearable filterable default-first-option allow-create
                           placeholder="手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人">
                </el-select>
              </el-form-item>
            </div>
          </transition>
          <!--邮件通知-->
          <el-form-item label="告警邮件组" prop="alarmMailGroupList">
            <el-select style="width: 60%;" v-model="form['alarmMailGroupList']" @visible-change="checkActiveMail"
                       clearable multiple placeholder="请选择告警报告接受者(可多选)">
              <el-option v-for="(item,index) in mailGroupList" :key="index" :label="item.name"
                         :value="item._id"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="触发邮件" prop="alwaysSendMail">
            <el-radio-group v-model="form['alwaysSendMail']">
              <el-radio :label="true">执行成功也触发邮件</el-radio>
              <el-radio :label="false">执行失败才触发邮件</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>
        <el-form-item label="任务描述" prop='description'>
          <el-input type="textarea" :rows="4" v-model="form.description"></el-input>
        </el-form-item>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="formVisible = false">取消</el-button>
        <el-button type="primary" @click.native="submit" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

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
  </section>
</template>

<script>
    import {
        getCronJobs, addCronJob, updateCronJob, deleteCronJob, pauseCronJob, resumeCronJob
    } from "../../../api/cronJob";
    import {getEnvConfigs} from "../../../api/envConfig";
    import {getTestSuites} from "../../../api/testSuite";
    import {getMailGroups} from "../../../api/mail";

    export default {
        name: "CronJobList",
        data() {
            let checkTriggerInterval = (rule, value, callback) => {
                if (value !== "" && value !== null && value !== undefined) {
                    if (value >= 60) {
                        callback()
                    } else {
                        callback(new Error('请输入大于或等于一分钟的触发间隔！'))
                        this.$message.warning({
                            message: '请输入大于或等于一分钟的触发间隔！',
                            center: true,
                        });
                    }
                } else {
                    callback()
                }
            };
            return {
                filters: {
                    name: ''
                },
                testSuites: [],
                mailGroupList: [],
                TriggerTypes: [{name: '触发间隔', value: 'interval'},
                    {name: '具体日期', value: 'date'}],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                selects: [],//列表选中列
                delLoading: false,
                disDel: true,
                TestStatus: false,
                listLoading: false,
                statusChangeLoading: false,
                cronJobs: [],
                testEnvs: [],

                titleMap: {
                    add: '新增定时任务',
                    edit: '编辑定时任务'
                },
                dialogStatus: '',
                formVisible: false,//编辑界面是否显示
                editLoading: false,
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
                    ],
                    testSuiteIdList: [
                        {required: true, message: '请选择测试用例组', trigger: 'blur'}
                    ],
                    testEnvId: [
                        {required: true, message: '请选择测试环境', trigger: 'blur'}
                    ],
                    triggerType: [
                        {required: true, message: '请选择触发类型', trigger: 'blur'}
                    ],
                    interval: [
                        {required: false, message: '请输入触发间隔', trigger: 'blur'},
                        {validator: checkTriggerInterval, trigger: 'blur'}
                    ],
                    runDate: [
                        {required: false, message: '请输入触发时间', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入版本号', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ]
                },
                //编辑界面数据
                form: {
                    name: '',
                    testSuiteIdList: [],
                    includeForbidden: false,
                    testEnvId: '',
                    // 企业微信通知
                    enableWXWorkNotify: false,
                    WXWorkAPIKey: '',
                    WXWorkMentionMobileList: [],
                    alwaysWXWorkNotify: false,
                    // 钉钉通知
                    enableDingTalkNotify: false,
                    DingTalkAccessToken: '',
                    DingTalkAtMobiles: [],
                    DingTalkSecret: '',
                    alwaysDingTalkNotify: false,
                    // 邮件通知
                    alarmMailGroupList: [],
                    alwaysSendMail: false,
                    triggerType: '',
                    interval: 0,
                    runDate: '',
                    description: ''
                },
                initForm: {
                    name: '',
                    testSuiteIdList: [],
                    includeForbidden: false,
                    testEnvId: '',
                    // 企业微信通知
                    enableWXWorkNotify: false,
                    WXWorkAPIKey: '',
                    WXWorkMentionMobileList: [],
                    alwaysWXWorkNotify: false,
                    // 钉钉通知
                    enableDingTalkNotify: false,
                    DingTalkAccessToken: '',
                    DingTalkAtMobiles: [],
                    DingTalkSecret: '',
                    alwaysDingTalkNotify: false,
                    // 邮件通知
                    alarmMailGroupList: [],
                    alwaysSendMail: false,
                    triggerType: '',
                    interval: 0,
                    runDate: '',
                    description: ''
                },
                pickerOptions: {
                    disabledDate: (time) => {
                        return time.getTime() < (Date.now() - 8.64e7)
                    }
                }
            }
        },
        methods: {
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
            getMailGroupList() {
                this.listLoading = true;
                let self = this;
                let params = {status: true}
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
            checkActiveMail: function () {
                let self = this;
                if (self.mailGroupList.length < 1) {
                    self.$message.warning({
                        message: '未找到「启用的邮件组」哦, 请通知管理员前往「邮件配置」进行设置',
                        center: true,
                    })
                }
            },
            // 获取用例组列表
            getTestSuiteList() {
                let self = this;
                let params = {
                    status: true,
                    projectId: self.$route.params.project_id
                }
                this.listLoading = true;
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
            checkActiveTestSuite: function () {
                let self = this;
                if (self.testSuites.length < 1) {
                    self.$message.warning({
                        message: '未找到「启用的测试用例组」哦, 请前往「自动化测试」进行设置',
                        center: true,
                    })
                }
            },
            queryCronJobs(params) {
                let self = this;
                if (self.filters.name.trim() !== '') {
                    params['name'] = self.filters.name.trim()
                }
                let header = {};
                getCronJobs(self.$route.params.project_id, params, header).then((res) => {
                    self.listLoading = false;
                    let {status, data} = res;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.cronJobs = data.rows;
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '定时任务列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                })
            },
            getCronJobList() {
                this.listLoading = true;
                let self = this
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryCronJobs(params);
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                self.listLoading = true;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryCronJobs(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                self.listLoading = true;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryCronJobs(params);
            },

            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let self = this;
                    let header = {};
                    let params = {}
                    deleteCronJob(this.$route.params.project_id, row._id, params, header).then((res) => {
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.success({
                                message: data,
                                center: true,
                            });
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            });
                        }
                        self.getCronJobList();
                    });
                })
            },
            selectsChange: function (selects) {
                if (selects.length > 0) {
                    this.selects = selects;
                    this.update = false
                } else {
                    this.update = true
                }
            },
            stringToDate: function (dateStr, separator) {
                if (!separator) {
                    separator = "-";
                }
                let dateArr = dateStr.toString().split(separator);
                let year = parseInt(dateArr[0]);
                let month;
                //处理月份为04这样的情况
                if (dateArr[1].indexOf("0") == 0) {
                    month = parseInt(dateArr[1].substring(1));
                } else {
                    month = parseInt(dateArr[1]);
                }
                let day = parseInt(dateArr[2]);
                let date = new Date(year, month - 1, day);
                return date;
            },
            //显示编辑界面
            handleEdit: function (index, row) {
                this.formVisible = true;
                if (row['runDate'] && row['runDate'].constructor === String) {
                    row['runDate'] = this.stringToDate(row['runDate'])
                }
                this.form = Object.assign({}, this.form, row);
                this.dialogStatus = 'edit'
            },
            //显示新增界面
            handleAdd: function () {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, this.initForm);
                this.dialogStatus = 'add';
            },

            submit() {
                this.$refs.form.validate((valid) => {
                    let self = this;
                    if (valid) {
                        if (self.form.enableWXWorkNotify && !self.form.WXWorkAPIKey) {
                            self.$message.error({
                                message: "企业微信APIKey不能为空！",
                                center: true,
                            })
                            return
                        }
                        if (self.form.enableDingTalkNotify && !self.form.DingTalkAccessToken) {
                            self.$message.error({
                                message: "钉钉AccessToken不能为空！",
                                center: true,
                            })
                            return
                        }
                        if (!(self.form.runDate && self.form.runDate.toString().trim() !== '') &&
                            !(self.form.interval && self.form.interval.toString().trim() !== '')) {
                            if (self.form.triggerType === 'interval')
                                self.$message.warning({
                                    message: '请输入触发间隔',
                                    center: true,
                                })
                            else if (self.form.triggerType === 'date') {
                                self.$message.warning({
                                    message: '请输入具体日期',
                                    center: true,
                                })
                            }
                        } else if (self.form.triggerType === 'date' && self.form.runDate < Date.now()) {
                            self.$message.warning({
                                message: '人生不能重来哦 ~ 请输入「此刻」以后的日期',
                                center: true,
                            })
                        } else {
                            this.$confirm('确认提交吗？', '提示', {}).then(() => {
                                self.editLoading = true;
                                let headers = {
                                    "Content-Type": "application/json",
                                };
                                if (this.dialogStatus == 'add') {
                                    let params = {
                                        name: self.form.name.trim(),
                                        testSuiteIdList: self.form.testSuiteIdList,
                                        testEnvId: self.form.testEnvId,
                                        includeForbidden: self.form.includeForbidden,
                                        triggerType: self.form.triggerType,
                                        description: self.form.description.trim(),
                                        enableWXWorkNotify: self.form.enableWXWorkNotify,
                                        WXWorkAPIKey: self.form.WXWorkAPIKey,
                                        WXWorkMentionMobileList: self.form.WXWorkMentionMobileList,
                                        alwaysWXWorkNotify: self.form.alwaysWXWorkNotify,
                                        enableDingTalkNotify: self.form.enableDingTalkNotify,
                                        DingTalkAccessToken: self.form.DingTalkAccessToken,
                                        DingTalkAtMobiles: self.form.DingTalkAtMobiles,
                                        DingTalkSecret: self.form.DingTalkSecret,
                                        alwaysDingTalkNotify: self.form.alwaysDingTalkNotify,
                                        alarmMailGroupList: self.form.alarmMailGroupList,
                                        alwaysSendMail: self.form.alwaysSendMail,
                                        createUser: self.$store.getters.email || 'anonymous',
                                    };
                                    if (self.form.runDate && self.form.runDate.toString().trim() !== '') {
                                        params['runDate'] = self.form.runDate
                                    }
                                    if (self.form.interval && self.form.interval.toString().trim() !== '') {
                                        params['interval'] = Number(self.form.interval)
                                    }
                                    addCronJob(self.$route.params.project_id, params, headers).then((res) => {
                                        self.editLoading = false;
                                        let {status, data} = res;
                                        if (status === 'ok') {
                                            self.formVisible = false
                                            self.$message.success({
                                                message: '添加成功',
                                                center: true,
                                            });
                                            self.$refs['form'].resetFields();
                                            self.formVisible = false;
                                            self.getCronJobList();
                                        } else {
                                            self.formVisible = false
                                            self.$message.error({
                                                message: data,
                                                center: true,
                                            })
                                            self.$refs['form'].resetFields();
                                            self.formVisible = false;
                                            self.getCronJobList()
                                        }
                                    });
                                } else if (this.dialogStatus == 'edit') {
                                    let params = {
                                        name: self.form.name.trim(),
                                        testSuiteIdList: self.form.testSuiteIdList,
                                        testEnvId: self.form.testEnvId,
                                        includeForbidden: self.form.includeForbidden,
                                        triggerType: self.form.triggerType,
                                        description: self.form.description.trim(),
                                        enableWXWorkNotify: self.form.enableWXWorkNotify,
                                        WXWorkAPIKey: self.form.WXWorkAPIKey,
                                        WXWorkMentionMobileList: self.form.WXWorkMentionMobileList,
                                        alwaysWXWorkNotify: self.form.alwaysWXWorkNotify,
                                        enableDingTalkNotify: self.form.enableDingTalkNotify,
                                        DingTalkAccessToken: self.form.DingTalkAccessToken,
                                        DingTalkAtMobiles: self.form.DingTalkAtMobiles,
                                        DingTalkSecret: self.form.DingTalkSecret,
                                        alwaysDingTalkNotify: self.form.alwaysDingTalkNotify,
                                        alarmMailGroupList: self.form.alarmMailGroupList,
                                        alwaysSendMail: self.form.alwaysSendMail,
                                        lastUpdateUser: self.$store.getters.email || 'anonymous',
                                    };
                                    if (self.form.runDate && self.form.runDate.toString().trim() !== '') {
                                        params['runDate'] = self.form.runDate
                                    }
                                    if (self.form.interval && self.form.interval.toString().trim() !== '') {
                                        params['interval'] = Number(self.form.interval)
                                    }
                                    updateCronJob(self.$route.params.project_id, self.form._id, params, headers).then((res) => {
                                        self.editLoading = false;
                                        let {status, data} = res;
                                        if (status === 'ok') {
                                            self.formVisible = false
                                            self.$message.success({
                                                message: '更新成功',
                                                center: true,
                                            });
                                            self.$refs['form'].resetFields();
                                            self.formVisible = false;
                                            self.getCronJobList();
                                        } else {
                                            self.formVisible = false
                                            self.$message.error({
                                                message: data,
                                                center: true,
                                            })
                                            self.$refs['form'].resetFields();
                                            self.formVisible = false;
                                            self.getCronJobList()
                                        }
                                    });
                                }
                            });
                        }
                    }
                });
            },
            //排序
            sortChange(column) {
                let self = this;
                self.listLoading = true;
                self.sortBy = column.prop;
                self.order = column.order;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectId: self.$route.params.project_id
                };
                this.queryCronJobs(params);
            },
            handleChangeStatus(index, row) {
                let self = this;
                self.statusChangeLoading = true;
                let header = {};
                let params = {
                    updateUser: self.$store.getters.email
                };
                if (row.status !== 'PAUSED') {
                    pauseCronJob(self.$route.params.project_id, row._id, params, header).then((res) => {
                        self.statusChangeLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.success({
                                message: data,
                                center: true,
                            });
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            });
                        }
                        self.getCronJobList();
                    }).catch((error) => {
                        self.$message.error({
                            message: '定时任务状态变更失败，请稍后刷新重试哦~',
                            center: true,
                        });
                        self.statusChangeLoading = false;
                    })
                } else {
                    resumeCronJob(self.$route.params.project_id, row._id, params, header).then((res) => {
                        self.statusChangeLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.success({
                                message: data,
                                center: true,
                            });
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            });
                        }
                        self.getCronJobList();
                    }).catch((error) => {
                        self.$message.error({
                            message: '定时任务状态变更失败，请稍后刷新重试哦~',
                            center: true,
                        });
                        self.statusChangeLoading = false;
                        self.getCronJobList();
                    })
                }
            },

            triggerTypeChange(selVal) {
                if (selVal === 'interval') {
                    this.form.runDate = ''
                } else if (selVal === 'date') {
                    this.form.interval = ''
                }
            },
            // 修改table tr行的背景色
            reportRowStyle({row, rowIndex}) {
                if (row.status === 'PAUSED')
                    return 'background-color: #DDDDDD'
                else {
                    return ''
                }
            },
            ReportTableRow({row, rowIndex}) {
                return 'reportTableRow';
            },
        },
        created() {
            this.getTestEnvList();
            this.getCronJobList();
            this.getMailGroupList();
            this.getTestSuiteList();
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

  .sub-form-item {
    padding-left: 40px;
  }

  .form-item-sub {
    position: relative;
    background-color: #f5f7fa;
    padding: 10px 0;
    margin-bottom: 10px;
    border-radius: 4px;
    box-shadow: inset 0 0 3px 0px #7c7c7c61;
  }

  .form-item-sub::before {
    position: absolute;
    content: '';
    display: block;
    width: 0;
    height: 0;
    top: -8px;
    left: 220px;
    border-bottom: 8px solid #ecedef;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 0px solid transparent;
  }

  .form-item-short > .el-form-item__content {
    margin-left: 100px !important;
  }

  .form-item-short > .el-input {
    margin: 0 10px;
  }

  .el-form-item:last-child {
    margin-bottom: 0;
  }

  ::-webkit-scrollbar {
    display: none;
  }
</style>
