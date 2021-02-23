<template>
  <section>
    <!--页面title-->
    <el-row><strong class="title">{{$route.meta.title}}</strong></el-row>

    <!--工具条-->
    <el-row class="toolbar" style="padding-bottom: 0px">
      <router-link :to="{
                    name: 'PlanList'
                }" style='text-decoration: none;color: aliceblue;'>
        <el-button class="return-list"><i class="el-icon-d-arrow-left" return-list style="margin-right: 5px"></i>返回
        </el-button>
      </router-link>
      <div style="float: right;  margin-right: 80px">
        <router-link :to="{
                    name: 'PlanList'
                }" style='text-decoration: none;color: aliceblue;'>
          <el-button class="return-list">
            <i class="el-icon-close" return-list style="margin-right: 5px"></i>取消
          </el-button>
        </router-link>
        <el-button class="return-list" type="primary" @click.native="updatePlanInfo">
          <i class="el-icon-check" return-list style="margin-right: 5px"></i>保存
        </el-button>
      </div>
    </el-row>

    <el-row>
      <el-form :model="form" ref="form" :rules="formRules">
        <!--基本信息-->
        <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
          <el-row>
            <el-col :span="20">
              <el-form-item label="计划名称:" label-width="120px" prop="name">
                <el-input v-model="form.name" placeholder="名称" auto-complete></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-col>
              <el-form-item label="是否并行:" label-width="120px" prop="isParallel">
                <el-radio v-model="form.isParallel" :label="true">是</el-radio>
                <el-radio v-model="form.isParallel" :label="false">否</el-radio>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-col :span="20">
              <el-form-item label="计划描述:" label-width="120px" prop="description">
                <el-input type="textarea" :rows="5" v-model="form.description" placeholder="请输入计划描述"
                          auto-complete></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-col :span="20">
              <el-form-item label="secretToken:" label-width="120px" prop="secretToken">
                <el-tooltip placement="top">
                  <div slot="content">
                    　<span>secretToken：通过第三方平台trigger执行plan时用于进行校验的token，如不需要第三方trigger，可不填</span>
                  </div>
                  <el-input v-model="form.secretToken" auto-complete="off"></el-input>
                </el-tooltip>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-col :span="20">
              <el-form-item label="CURL Script:" label-width="120px" prop="curlScript">
                <el-tooltip effect="dark" placement="top">
                  <div slot="content">
                    　<span>请将如下脚本信息补全（ testEnvId请进入环境配置查询ID，remark为自定义标记,可填入jenkins job name）</span><br/>
                    　<span>将补全的curl Script 填入jenkins job - Build - Execute Shell中即可通过jenkins trigger执行plan</span><br/>
                    　<span>注意:curl脚本不能换行</span>
                  </div>
                  <el-input type="textarea" v-model="form.curlScript" auto-complete="off" readonly></el-input>
                </el-tooltip>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-col :span="22">
              <el-form-item label="测试范围:" prop="executionRange" label-width="120px">
                <el-table :data="form.executionRange" highlight-current-row>
                  <el-table-column label="项目" min-width="30%" sortable>
                    <template slot-scope="scope">
                      <el-form-item :prop="'executionRange.' + scope.$index + '.projectId'"
                                    :rules="formRules.range_projectId">
                        <el-select :prop="'executionRange.' + scope.$index + '.projectId'" placeholder="请选择项目" clearable
                                   filterable allow-create default-first-option
                                   v-model="scope.row.projectId" style="width:90%">
                          <el-option v-for="(item,index) in projects" :key="index+''" :label="item.name"
                                     :value="item._id"></el-option>
                        </el-select>
                      </el-form-item>
                    </template>
                  </el-table-column>
                  <el-table-column label="优先级" min-width="10%">
                    <template slot-scope="scope">
                      <el-form-item :prop="'executionRange.' + scope.$index + '.priority'"
                                    :rules="formRules.range_priority">
                        <el-select placeholder="请选择优先级" clearable
                                   filterable allow-create default-first-option
                                   v-model="scope.row.priority" style="width:90%">
                          <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label"
                                     :value="item.value">
                          </el-option>
                        </el-select>
                      </el-form-item>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" min-width="5%">
                    <template slot-scope="scope">
                      <el-form-item>
                        <i class="el-icon-delete" style="font-size:30px;cursor:pointer;"
                           @click="delExecutionRange(scope.$index)"></i>
                      </el-form-item>
                    </template>
                  </el-table-column>
                  <el-table-column label="" min-width="10%">
                    <template slot-scope="scope">
                      <el-form-item>
                        <el-button v-if="scope.$index===(form.executionRange.length-1)" size="mini" class="el-icon-plus"
                                   @click="addExecutionRange"></el-button>
                      </el-form-item>
                    </template>
                  </el-table-column>
                </el-table>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        <!--通知策略-->
        <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
          <el-row :gutter="10">
            <el-col :span="20" style="border-bottom: 1px solid #e6e6e6;margin:20px">
              <el-form-item label="企业微信通知" label-width="120px" prop="enableWXWorkNotify">
                <el-radio v-model="form.enableWXWorkNotify" :label="true">是</el-radio>
                <el-radio v-model="form.enableWXWorkNotify" :label="false">否</el-radio>
              </el-form-item>

              <transition name="el-zoom-in-top">
                <div class="form-item-sub form-item-short" v-if="form.enableWXWorkNotify">
                  <el-form-item label-width="120px" label="企业微信APIKey" prop="WXWorkAPIKey">
                    <el-input placeholder="请填写企业微信群机器人WebhookAPIKey，如: 6789f5f7-736a-423b-b140-98d8324cb8cb"
                              v-model.trim="form.WXWorkAPIKey" auto-complete="off"></el-input>
                  </el-form-item>
                  <el-form-item v-show="form.enableWXWorkNotify" label-width="120px" label="通知策略">
                    <el-radio v-model="form.alwaysWXWorkNotify" :label="true">执行成功也发送通知</el-radio>
                    <el-radio v-model="form.alwaysWXWorkNotify" :label="false">执行失败才发送通知</el-radio>
                  </el-form-item>
                  <el-form-item v-show="form.enableWXWorkNotify" label-width="120px" label="提醒手机号列表">
                    <el-select style="width: 70%;" v-model.trim="form.WXWorkMentionMobileList"
                               multiple clearable filterable default-first-option allow-create
                               placeholder="手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人">
                    </el-select>
                  </el-form-item>
                </div>
              </transition>
            </el-col>
          </el-row>
           <el-row :gutter="10">
            <el-col :span="20" style="border-bottom: 1px solid #e6e6e6;margin:20px">
              <el-form-item label="钉钉通知" label-width="120px" prop="enableDingTalkNotify">
                <el-radio v-model="form.enableDingTalkNotify" :label="true">是</el-radio>
                <el-radio v-model="form.enableDingTalkNotify" :label="false">否</el-radio>
              </el-form-item>

              <transition name="el-zoom-in-top">
                <div class="form-item-sub form-item-short" v-if="form.enableDingTalkNotify">
                  <el-form-item label-width="120px" label="AccessToken" prop="DingTalkAccessToken">
                    <el-input placeholder="请填写钉钉群机器人DingTalkAccessToken"
                              v-model.trim="form.DingTalkAccessToken" auto-complete="off"></el-input>
                  </el-form-item>
                  <el-form-item label-width="120px" label="钉钉加签密钥" prop="DingTalkSecret">
                    <el-input placeholder="钉钉机器人安全设置勾选加签后须填写Secret,如不勾选可不填"
                              v-model.trim="form.DingTalkSecret" auto-complete="off"></el-input>
                  </el-form-item>
                  <el-form-item v-show="form.enableDingTalkNotify" label-width="120px" label="通知策略">
                    <el-radio v-model="form.alwaysDingTalkNotify" :label="true">执行成功也发送通知</el-radio>
                    <el-radio v-model="form.alwaysDingTalkNotify" :label="false">执行失败才发送通知</el-radio>
                  </el-form-item>
                  <el-form-item v-show="form.enableDingTalkNotify" label-width="120px" label="提醒手机号列表">
                    <el-select style="width: 70%;" v-model.trim="form.DingTalkAtMobiles"
                               multiple clearable filterable default-first-option allow-create
                               placeholder="手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人">
                    </el-select>
                  </el-form-item>
                </div>
              </transition>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-col :span="20" style="border-bottom: 1px solid #e6e6e6;margin:20px">
              <el-form-item label="告警邮件组" label-width="120px" prop="alarmMailGroupList">
                <el-select style="width: 60%;" v-model="form.alarmMailGroupList" @visible-change="checkActiveMail"
                           clearable multiple placeholder="请选择告警报告接受者(可多选)">
                  <el-option v-for="(item,index) in mailGroupList" :key="index" :label="item.name"
                             :value="item._id"></el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="触发邮件" label-width="120px" prop="alwaysSendMail">
                <el-radio-group v-model="form.alwaysSendMail">
                  <el-radio :label="true">执行成功也触发邮件</el-radio>
                  <el-radio :label="false">执行失败才触发邮件</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>
    </el-row>
  </section>
</template>

<script>
    import {getProjects} from "../../api/project";
    import {getPlanInfo, updatePlan} from "../../api/plan";
    import {getMailGroups} from "../../api/mail";

    export default {
        name: "PlanDetail",
        data() {
            let checkPriority = (rule, value, callback) => {
                if (value != 'ALL' && value != 'P1' && value != 'P2') {
                    callback(new Error('请正确选择优先级'))
                    this.$message.warning({
                        message: '请正确选择优先级!',
                        center: true,
                    });
                } else {
                    callback()
                }
            };
            return {
                mailGroupList: [],
                projects: [],
                priorityOptions: [
                    {label: "ALL", value: "ALL"},
                    {label: "P1", value: "P1"},
                    {label: "P2", value: "P2"}
                ],
                form: {
                    name: '',
                    description: "",
                    isParallel: false,
                    secretToken: '',
                    hookUrl: '',
                    curlScript: '',
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
                    executionRange: [{
                        projectId: '',
                        priority: 'ALL'
                    }]
                },
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
                    ],
                    executionRange: [{required: true, message: '请选择测试范围', trigger: 'blur'}],
                    isParallel: [{required: true, type: 'boolean', message: '请选择是否并发', trigger: 'blur'}],
                    range_projectId: [{required: true, message: '请选择项目', trigger: 'blur'}],
                    range_priority: [{required: true, message: '请选择优先级', trigger: 'blur'},
                        {validator: checkPriority, trigger: 'blur'}]
                }
            }
        },
        methods: {
            // 获取项目列表
            getProjectList() {
                let params = {
                    size: this.size,
                    skip: this.skip,
                    sortBy: this.sortBy,
                    order: this.order,
                    projectTestType: 'apiTest'
                };
                this.listLoading = true;
                let header = {};
                getProjects(params, header).then((res) => {
                    this.listLoading = false;
                    let {status, data} = res;
                    if (status === "ok") {
                        this.totalNum = data.totalNum;
                        this.projects = data.rows
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
                    this.listLoading = false;
                })
            },
            addExecutionRange() {
                let rangeInit = {
                    projectId: '',
                    priority: 'ALL'
                };
                this.form.executionRange.push(rangeInit)
            },
            delExecutionRange(index) {
                this.form.executionRange.splice(index, 1);
                if (this.form.executionRange.length === 0) {
                    this.form.executionRange.push({
                        projectId: '',
                        priority: ''
                    })
                }
            },
            checkExecutionRange() {
                if (this.form.executionRange.length > 1) {
                    let len = this.form.executionRange.length
                    for (let i = 0; i < len; i++) {
                        for (let j = i + 1; j < len; j++) {
                            if (this.form.executionRange[i]['projectId'] == this.form.executionRange[j]['projectId']) {
                                this.$message.warning({
                                    message: '请不要重复选择项目!',
                                    center: true,
                                });
                                return false
                            }
                        }
                    }
                }
                return true
            },
            // 获取Case详细信息
            getPlanDetailInfo() {
                let self = this;
                getPlanInfo(self.$route.params.plan_id)
                    .then((res) => {
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.form.name = data.name;
                            self.form.description = data.description;
                            self.form.isParallel = data.isParallel;
                            self.form.secretToken = data.secretToken;
                            self.form.executionRange = data.executionRange;
                            self.form.hookUrl = window.document.location.protocol + '//'
                                + window.document.location.host + '/api/plan/'
                                + self.$route.params.plan_id + '/executePlanByWebHook';
                            self.form.curlScript = "curl -d \"testEnvId=${testEnvId}&secretToken="
                                + self.form.secretToken
                                + "&executionRemark=${remark}\" \"" + self.form.hookUrl + "\"";
                            // 通知策略
                            // 企业微信通知
                            self.form.enableWXWorkNotify = data.enableWXWorkNotify;
                            self.form.WXWorkAPIKey = data.WXWorkAPIKey;
                            self.form.WXWorkMentionMobileList = data.WXWorkMentionMobileList;
                            if (data.enableWXWorkNotify) {
                                self.form.alwaysWXWorkNotify = data.alwaysWXWorkNotify;
                            }
                            // 钉钉通知
                            self.form.enableDingTalkNotify = data.enableDingTalkNotify;
                            self.form.DingTalkAccessToken = data.DingTalkAccessToken;
                            self.form.DingTalkAtMobiles = data.DingTalkAtMobiles;
                            self.form.DingTalkSecret = data.DingTalkSecret;
                            if (data.enableDingTalkNotify) {
                                self.form.alwaysDingTalkNotify = data.alwaysDingTalkNotify;
                            }
                            // 邮件通知
                            self.form.alarmMailGroupList = data.alarmMailGroupList;
                            if (data.alwaysSendMail) {
                                self.form.alwaysSendMail = data.alwaysSendMail;
                            }
                        }
                    }).catch((error) => {
                    self.$message.error({
                        message: '计划详情获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                })
            },
            updatePlanInfo() {
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        if (this.checkExecutionRange()) {
                            this.$confirm('确认提交吗？', '提示', {}).then(() => {
                                let self = this;
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
                                let params = {
                                    name: self.form.name.trim(),
                                    description: self.form.description.trim(),
                                    isParallel: self.form.isParallel,
                                    secretToken: self.form.secretToken,
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
                                    executionRange: self.form.executionRange,
                                    lastUpdateUser: self.$store.getters.email || 'anonymous'
                                };
                                let header = {};
                                updatePlan(self.$route.params.plan_id, params, header).then((res) => {
                                    let {status, data} = res;
                                    if (status === 'ok') {
                                        self.$router.push({name: 'PlanList'});
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        })
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        })
                                    }
                                })
                            })
                        }
                    }
                })
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
            }
        },
        mounted() {
            this.getProjectList()
            this.getPlanDetailInfo()
            this.getMailGroupList()
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

  .head-class {
    font-size: 17px
  }

  .parameter-a {
    display: block;
  }

  .parameter-b {
    display: none;
  }

  .selectInput {
    position: absolute;
    padding-left: 9px;
    width: 180px;
    left: 1px;
    border-right: 0px;

    input {
      border-right: 0px;
      border-radius: 4px 0px 0px 4px;
    }
  }
</style>
