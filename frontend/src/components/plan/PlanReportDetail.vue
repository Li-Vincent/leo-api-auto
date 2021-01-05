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
          <span style="text-align:left; font-size: 18px; font-weight: bold">测试计划基本信息</span>
        </el-col>
        <table style="margin-right:30px;width:70%;height:12px">
          <tbody>
          <tr class="info">
            <td class="label">计划名称</td>
            <td class="text-center">{{planReport.planName}}</td>
          </tr>
          <tr class="info">
            <td class="label">测试环境</td>
            <td class="text-center">{{planReport.testEnvName}}</td>
          </tr>
          <tr class="info">
            <td class="label">开始时间</td>
            <td class="text-center">{{planReport.testStartTime}}</td>
          </tr>
          <tr class="info">
            <td class="label">测试用时</td>
            <td class="text-center">{{planReport.spendTimeInSec}} s</td>
          </tr>
          <tr class="info">
            <td class="label">总用例数</td>
            <td class="text-center">{{planReport.totalCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">通过数</td>
            <td class="text-center">{{planReport.passCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">失败数</td>
            <td class="text-center">{{planReport.failCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">错误数</td>
            <td class="text-center">{{planReport.errorCount}}</td>
          </tr>
          <tr class="info">
            <td class="label">通过率</td>
            <td class="text-center">{{getPassRate(planReport.passCount,planReport.totalCount,true)}}</td>
          </tr>
          </tbody>
        </table>
      </el-col>
      <el-col :span="10">
        <div style="height:230px;width: 100%;" id="report-chart"></div>
      </el-col>
    </el-row>

    <!--按照projectReports分组显示详细信息-->
    <el-row>
      <el-table :data="projectReports" highlight-current-row style="width: 100%;">
        <el-table-column prop="projectName" label="项目名" min-width="10%" show-overflow-tooltip>
        </el-table-column>
        <el-table-column prop="testStartTime" label="开始时间" min-width="10%" sortable='custom' show-overflow-tooltip>
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
        <el-table-column label="操作" min-width="10%">
          <template slot-scope="scope">
            <router-link
              :to="{ name: 'PlanProjectReport', params: {report_id:$route.params.report_id, project_id: scope.row.projectId}}"
              style='text-decoration: none;color: #000000;'>
              <el-button type="primary" size="small">查看项目报告</el-button>
            </router-link>
          </template>
        </el-table-column>
        <!--        用例组报告-->
        <el-table-column type="expand">
          <template slot-scope="props">
            <el-table :data="Object.values(props.row.testSuites)" highlight-current-row style="width: 100%;">
              <el-table-column label="序号" prop="" width="50" align="center">
                <template slot-scope="scope">
                  {{scope.$index+1}}
                </template>
              </el-table-column>
              <el-table-column prop="suiteName" label="用例组名" min-width="15%" show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="testStartTime" label="开始时间" min-width="10%" sortable='custom'
                               show-overflow-tooltip>
              </el-table-column>
              <el-table-column prop="spendTimeInSec" label="用时(秒)" min-width="10%" sortable='custom'
                               show-overflow-tooltip>
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
            </el-table>
          </template>
        </el-table-column>
      </el-table>
    </el-row>
  </section>
</template>

<script>
    import echarts from 'echarts'
    import moment from "moment";
    import {getPlanReportInfo, getPlanReportDetail} from "../../api/planReport";


    export default {
        name: "PlanReportDetail",
        data() {
            return {
                activeName: 1,
                planReport: {
                    testEnv: "",
                    planName: "",
                    executionUser: "",
                    planId: "",
                    testStartTime: "",
                    totalCount: 0,
                    passCount: 0,
                    failCount: 0,
                    errorCount: 0,
                    spendTimeInSec: 0.0,
                    createAt: "",
                },
                projectReports: [],
                reportChart: null,
            }
        },
        methods: {
            getReport() {
                getPlanReportInfo(this.$route.params.plan_report_id).then((res) => {
                        if (res.status === 'ok') {
                            this.planReport = res.data;
                            getPlanReportDetail(this.$route.params.plan_report_id).then(detailRes => {
                                if (detailRes.status == 'ok') {
                                    detailRes.data.rows.forEach(row => {
                                        this.projectReports.push(row)
                                    })
                                }
                            })
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
            }
        },
        mounted() {
            this.reportChart = echarts.init(document.getElementById('report-chart'));
            this.setChartOptions(this.planReport.passCount, this.planReport.failCount, this.planReport.errorCount);
        },
        watch: {
            planReport: {//深度监听，可监听到对象、数组的变化
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

    .report-name {
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
