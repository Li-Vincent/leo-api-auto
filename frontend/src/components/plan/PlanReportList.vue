<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}} <span v-if="planName"> - Plan: {{planName}}</span> </strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 35px">
          <el-button type="primary" @click="getManualReports"><i class="fa fa-hand-pointer-o"></i> 手动执行报告</el-button>
        </el-form-item>
        <el-form-item style="margin-left: 35px">
          <el-button type="primary" @click="getWebhookReports"><i class="fa fa-link"></i> Webhook执行报告</el-button>
        </el-form-item>

        <el-form-item style="float: right;  margin-right: 40px" v-if="$store.getters.roles.includes('admin')">
          <el-select v-model="cleanDate" style="margin-right: 20px" placeholder="删除日期">
            <el-option v-for="(item,index) in cleanDateOptions" :key="index+''" :label="item.label"
                       :value="item.value"></el-option>
          </el-select>
          <el-form-item>
            <el-button type="danger" class="el-icon-delete" @click="cleanPlanReports"> 删除报告</el-button>
          </el-form-item>
        </el-form-item>
      </el-form>
    </el-col>

    <!--报告列表-->
    <el-table @sort-change='sortChange' :data="planReports" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="3%">
      </el-table-column>
      <el-table-column prop="_id" label="报告编号" min-width="10%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="testEnvName" label="测试环境" min-width="8%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="testStartTime" label="开始时间" min-width="12%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="spendTimeInSec" label="用时(秒)" min-width="10%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="executionUser" label="执行人" min-width="8%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="executionRemark" label="备注" min-width="8%" sortable='custom' show-overflow-tooltip>
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
      <el-table-column label="操作" min-width="20%">
        <template slot-scope="scope">
          <router-link
            :to="{ name: 'PlanReportDetail', params: {plan_id:$route.params.plan_id, plan_report_id: scope.row._id}}"
            style='text-decoration: none;color: #000000;'>
            <el-button type="primary" size="small">查看详情</el-button>
          </router-link>
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

  </section>
</template>


<script>
    import {getPlanReports, cleanPlanReports} from "../../api/planReport";
    import {getPlanInfo} from "../../api/plan";

    export default {
        name: "PlanReportList",
        data() {
            return {
                filters: {
                    executionUser: ''
                },
                planName: '',
                planReports: [],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
                statusChangeLoading: false,
                selects: [],//列表选中列
                cleanDate: null,
                cleanDateOptions: [
                    {value: null, label: '未选择'},
                    {value: 30, label: '30天之前'},
                    {value: 7, label: '7天之前'},
                    {value: 0, label: '全部删除'}
                ]
            }
        },
        methods: {
            queryPlanReports(params) {
                this.listLoading = true;
                let self = this;
                if (self.filters.executionUser.trim() !== '') {
                    params['executionUser'] = self.filters.executionUser.trim()
                }
                let header = {};
                getPlanReports(this.$route.params.plan_id, params, header).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.planReports = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '报告列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            getWebhookReports() {
                let self = this;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    planId: self.$route.params.plan_id,
                    executionMode: 'webHook'
                };
                this.queryPlanReports(params);
            },
            getManualReports() {
                let self = this;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    planId: self.$route.params.plan_id,
                    executionMode: 'planManual'
                };
                this.queryPlanReports(params);
            },
            getReports() {
                let self = this;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    planId: self.$route.params.plan_id
                };
                this.queryPlanReports(params);
            },
            selectsChange: function (selects) {
                this.selects = selects;
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    planId: self.$route.params.plan_id
                };
                this.queryPlanReports(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order,
                    planId: self.$route.params.plan_id
                };
                this.queryPlanReports(params);
            },
            // 修改table tr行的背景色
            reportRowStyle({row, rowIndex}) {
                if (row.totalCount > row.passCount)
                    return 'background-color: #ddd;'
                else {
                    return ''
                }
            },
            ReportTableRow({row, rowIndex}) {
                return 'reportTableRow';
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
                    projectId: self.$route.params.project_id
                };
                this.queryPlanReports(params);
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
            cleanPlanReports() {
                this.$confirm('确认删除报告吗?', '提示', {
                    type: 'warning'
                }).then((res) => {
                    if (this.cleanDate == null) {
                        this.$message.error({
                            message: "请选择删除日期",
                            center: true,
                        })
                        return
                    }
                    let self = this;
                    self.listLoading = true;
                    let params = {
                        cleanDate: self.cleanDate,
                        planId: self.$route.params.plan_id,
                        operator: self.$store.getters.email
                    };
                    let header = {};
                    cleanPlanReports(this.$route.params.plan_id, params, header).then((res) => {
                        self.listLoading = false;
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.$message.info({
                                message: '~~删除计划报告成功~~',
                                center: true,
                            });
                            this.getReports();
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                            this.getReports();
                        }
                    }).catch((error) => {
                        self.listLoading = false;
                        self.$message.error({
                            message: '删除计划报告失败，请稍后刷新重试哦~',
                            center: true,
                        });
                        this.getReports();
                    })
                });
            }
        },
        mounted() {
            getPlanInfo(this.$route.params.plan_id).then((res) => {
                if (res.status === 'ok') {
                    this.planName = res.data.name;
                }
            });
        },
        created() {
            this.getReports()
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
