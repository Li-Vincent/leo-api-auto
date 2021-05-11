<template>
  <section class="report">
    <!--页面title-->
    <el-row>
      <el-col :span="24" class="title">
        <span>{{$route.meta.title}} </span>
        <span class="report-id"> - Report ID: {{$route.params.plan_report_id}}</span>
      </el-col>
    </el-row>

    <!--基本信息和饼图-->
    <el-row class="report-basic">
      <el-col :span="10">
        <el-col style="width:160px">
          <span style="text-align:left; font-size: 18px; font-weight: bold">项目概要信息</span>
        </el-col>
        <table style="margin-right:30px;width:70%;height:12px">
          <tbody>
          <tr class="info">
            <td class="label">项目名称</td>
            <td class="text-center">{{projectName}}</td>
          </tr>
          <tr class="info">
            <td class="label">测试环境</td>
            <td class="text-center">{{projectReport.testEnvName}}</td>
          </tr>
          <tr class="info">
            <td class="label">开始时间</td>
            <td class="text-center">{{projectReport.testStartTime}}</td>
          </tr>
          <tr class="info">
            <td class="label">测试用时</td>
            <td class="text-center">{{projectReport.spendTimeInSec}} s</td>
          </tr>
          <tr class="info">
            <td class="label">总用例数</td>
            <td class="text-center">{{projectReport.totalCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">通过数</td>
            <td class="text-center">{{projectReport.passCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">失败数</td>
            <td class="text-center">{{projectReport.failCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">错误数</td>
            <td class="text-center">{{projectReport.errorCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">通过率</td>
            <td class="text-center">{{getPassRate(projectReport.passCount,projectReport.totalCount,true)}}</td>
          </tr>
          </tbody>
        </table>
      </el-col>
      <el-col :span="10">
        <div style="height:230px;width: 100%;" id="report-chart"></div>
      </el-col>
    </el-row>

    <!--按照testSuite分组显示详细信息-->
    <el-row>
      <el-table :data="testSuites" highlight-current-row style="width: 100%;">
        <el-table-column prop="suiteName" label="用例组名" min-width="10%" show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="testStartTime" label="开始时间" min-width="12%" sortable='custom' show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="spendTimeInSec" label="用时(秒)" min-width="10%" sortable='custom' show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="totalCount" label="总数" min-width="8%" show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="passCount" label="通过数" min-width="8%" show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="failCount" label="失败数" min-width="8%" show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="errorCount" label="错误数" min-width="8%" show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="passRate" label="通过率" min-width="10%" show-overflow-tooltip>
          <template slot-scope="scope">
            {{ getPassRate(scope.row.passCount,scope.row.totalCount,true) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="测试结果" min-width="10%">
          <template slot-scope="scope">
            <img v-show="scope.row.totalCount==scope.row.passCount" src="../../assets/imgs/icon-yes.svg"/>
            <img v-show="scope.row.totalCount>scope.row.passCount" src="../../assets/imgs/icon-no.svg"/>
          </template>
        </el-table-column>
        <!--        测试用例详细报告-->
        <el-table-column type="expand">
          <template slot-scope="props">
            <el-table :data="props.row.testCaseReports" highlight-current-row style="width: 100%;">
              <el-table-column label="序号" prop="" width="50" align="center">
                <template slot-scope="scope">
                  {{scope.$index+1}}
                </template>
              </el-table-column>
              <el-table-column prop="resultDetail.name" label="用例名" min-width="15%" show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="resultDetail.testCaseDetail.requestMethod" label="Method" min-width="8%"
                               show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="resultDetail.testCaseDetail.url" label="URL" min-width="25%" show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="headers" label="Headers" min-width="8%" show-overflow-tooltip>
                <template slot-scope="scope">
                  {{scope.row.resultDetail.headers}}
                </template>
              </el-table-column>
              <el-table-column prop="requestBody" label="请求参数" min-width="8%" show-overflow-tooltip>
                <template slot-scope="scope">
                  {{scope.row.resultDetail.testCaseDetail.requestBody}}
                </template>
              </el-table-column>
              <el-table-column prop="resultDetail.responseStatusCode" label="返回状态" min-width="8%" show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="resultDetail.responseData" label="返回值" min-width="8%" show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="status" label="结果" min-width="5%">
                <template slot-scope="scope">
                  <img v-show="scope.row.resultDetail.status==='ok'" src="../../assets/imgs/icon-yes.svg"/>
                  <img v-show="scope.row.resultDetail.status==='failed'" src="../../assets/imgs/icon-no.svg"/>
                </template>
              </el-table-column>
              <el-table-column prop="resultDetail.testStartTime" label="开始时间" min-width="10%" show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="resultDetail.spendTimeInSec" label="用时(s)" min-width="8%" show-overflow-tooltip>
              </el-table-column>
              <el-table-column label="操作" min-width="10%">
                <template slot-scope="scope">
                  <el-button type="primary" size="small" @click="showDetail(scope.row.resultDetail)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-table-column>
      </el-table>
    </el-row>

    <!--测试用例详细结果-->
    <el-dialog title="测试结果" :visible.sync="showDetailDialog" :close-on-click-modal="false">
      <div slot="title" class="header-title">
        <span style="font-size: 28px">测试结果</span>
        <span v-show="result.name" style="font-size: 20px"> - {{ result.name }}</span>
      </div>
      <div class="test-result-dialog">
        <div>请求地址 : {{result.url}}</div>
        <div>请求方式 : {{result.requestMethod}}</div>
        <div>请求开始时间 : {{result.testStartTime}}</div>
        <div>请求所用时间 : {{result.spendTimeInSec}}s</div>
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
        <div class="divider-line"></div>
        <div style="font-size: 25px;">数据初始化:</div>
        <div v-for="(item,index) in result.dataInitResult" :key="index">
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
        <div v-for="(item,index) in result.cookies" :key="index">{{item.name}} = {{item.value}}</div>
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
        <div>JSON正则校验:
          <pre>{{result.checkResponseBody}}</pre>
          <span v-show="!result.checkResponseBody">(无)</span>
        </div>
        <div class="divider-line"></div>
        <div style="font-size: 25px;">实际结果:</div>
        <div>HTTP状态码: {{result.responseStatusCode}}</div>
        <div>实际返回内容:</div>
        <div v-show="result.responseData" class="resultStyle resultData">
          <pre>{{result.responseData}}</pre>
        </div>
        <div v-show="!result.responseData" class="resultStyle resultData">(无返回内容)</div>
      </div>
    </el-dialog>
  </section>
</template>

<script>
    import echarts from 'echarts'
    import moment from "moment";
    import {getPlanProjectReport} from "../../api/planReport";
    import {getTestCaseReports} from "../../api/testReport";
    import {getProjectInfo} from "../../api/project";

    export default {
        name: "PlanProjectReport",
        data() {
            return {
                projectName: '',
                projectReport: {
                    testEnv: "",
                    executionUser: "",
                    testStartTime: "",
                    totalCount: 0,
                    passCount: 0,
                    failCount: 0,
                    errorCount: 0,
                    spendTimeInSec: 0.0,
                    createAt: "",
                },
                testSuites: [],
                reportChart: null,
                showDetailDialog: false,
                result: {}
            }
        },
        methods: {
            getReport() {
                getPlanProjectReport(this.$route.params.plan_report_id, this.$route.params.project_id).then((res) => {
                        if (res.status === 'ok') {
                            this.projectReport = res.data;
                            if (res.data.testSuites) {
                                this.testSuites = Object.values(res.data.testSuites)
                                for (let i = 0; i < this.testSuites.length; i++) {
                                    let item = this.testSuites[i];
                                    item['testCaseReports'] = [];
                                    let params = {
                                        sortBy: 'createAt',
                                        order: 'ascending',
                                        testSuiteId: item._id,
                                        reportId: this.projectReport._id
                                    };
                                    getTestCaseReports(this.projectReport._id, item._id, params).then(detailRes => {
                                        if (detailRes.status == 'ok') {
                                            detailRes.data.rows.forEach(caseReport => {
                                                item['testCaseReports'].push(caseReport)
                                            })
                                        }
                                    })
                                }
                            }
                        }
                    }
                )
            },
            getProjectInfo() {
                getProjectInfo(this.$route.params.project_id).then((res) => {
                        if (res.status === 'ok') {
                            this.projectName = res.data.name;
                        }
                    }
                )
            },
            getPassRate(passCount, totalCount, isHasPercentStr) {
                passCount = parseFloat(passCount);
                totalCount = parseFloat(totalCount);
                if (isNaN(passCount) || isNaN(totalCount)) {
                    return '-';
                }
                return isHasPercentStr ?
                    totalCount <= 0 ? '0%' : (Math.round(passCount / totalCount * 10000) / 100.00 + '%') :
                    totalCount <= 0 ? 0 : (Math.round(passCount / totalCount * 10000) / 100.00);
            },
            setChartOptions(passCount, failCount, errorCount) {
                this.reportChart.setOption({
                    title: {
                        text: '通过率统计'
                    },
                    legend: {
                        data: ['Pass', 'Fail', 'Error']
                    },
                    series: [
                        {
                            type: 'pie',
                            radius: '55%',
                            center: ['50%', '50%'],
                            data: [
                                {value: passCount, name: 'Pass', itemStyle: {color: '#54ac21'}},
                                {value: failCount, name: 'Fail', itemStyle: {color: '#d6443f'}},
                                {value: errorCount, name: 'Error', itemStyle: {color: '#e0aa1c'}}
                            ]
                        }
                    ]
                })
            },
            showDetail(detail) {
                let self = this;
                self.result["name"] = detail.name;
                self.result["url"] = detail.testCaseDetail.url;
                self.result["requestMethod"] = detail.testCaseDetail.requestMethod;
                if (detail.dataInitResult && detail.dataInitResult.length > 0) {
                    detail.dataInitResult.forEach(item => {
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
                self.result["dataInitResult"] = detail.dataInitResult;

                self.result["headers"] = detail.headers;
                self.result["cookies"] = detail.testCaseDetail.cookies;
                self.result["requestBody"] = detail.testCaseDetail.requestBody;
                if (detail.testCaseDetail.filePath) {
                    self.result["filePath"] = detail.testCaseDetail.filePath; 
                }
                if (detail.checkResponseCode) {
                    self.result["checkResponseCode"] = detail.checkResponseCode;
                } else {
                    self.result["checkResponseCode"] = '无'
                }
                if (detail.checkResponseBody && !(detail.checkResponseBody === 1 && detail.checkResponseBody[0]['regex'].trim() == '')) {
                    self.result["checkResponseBody"] = detail.checkResponseBody;
                } else {
                    self.result["checkResponseBody"] = '无'
                }
                self.result["result"] = detail.status;
                self.result["responseStatusCode"] = detail.responseStatusCode;
                try {
                    self.result["responseData"] = JSON.parse(detail.responseData);
                } catch (error) {
                    self.result["responseData"] = detail.responseData;
                }
                self.result["testConclusion"] = detail.testConclusion;
                self.result["testStartTime"] = moment(detail.testStartTime).format("YYYY年MM月DD日HH时mm分ss秒");
                self.result["spendTimeInSec"] = detail.spendTimeInSec;
                self.showDetailDialog = true;
            },
        },
        mounted() {
            this.reportChart = echarts.init(document.getElementById('report-chart'));
            this.setChartOptions(this.projectReport.passCount, this.projectReport.failCount, this.projectReport.errorCount);
        },
        watch: {
            projectReport: {//深度监听，可监听到对象、数组的变化
                handler(val, oldVal) {
                    this.setChartOptions(val.passCount, val.failCount, val.errorCount)
                },
                deep: true
            }
        },
        beforeDestroy() {
            if (!this.reportChart) {
                return
            }
            this.reportChart.dispose()
            this.reportChart = null
        },
        created() {
            this.getReport()
            this.getProjectInfo()
        }
    }
</script>

<style lang="scss" scoped>
  .report {
    font-family: "Arial", "Microsoft YaHei", "黑体", "宋体", sans-serif;
    color: #333;
  }

  .title {
    color: #333;
    font-size: 28px;
    height: 60px;
    line-height: 39px;
    padding: 10px 5px 10px;
    border-bottom: 1px solid #ddd;

    .report-id {
      font-size: 20px;
    }

    .execution-info {
      float: right;
      margin-right: 20px;
      font-size: 16px;
    }
  }

  .report-basic {
    padding: 10px 5px 10px;
    margin: 0;
    font-size: 18px;
    line-height: 1.5;
    line-height: 1.5;
    border-bottom: 1px solid #ddd;

    table {
      tr {
        height: 16px;
        border-bottom: 1px solid $--color-primary;
      }
    }
  }

  .test-result-dialog {
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

</style>
