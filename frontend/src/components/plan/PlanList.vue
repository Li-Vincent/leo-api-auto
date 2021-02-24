<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}}</strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <el-form-item>
          <el-input v-model="filters.name" placeholder="计划名称" @keyup.enter.native="getPlanList"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-search" @click="getPlanList">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-plus" @click="handleAdd">新增计划</el-button>
        </el-form-item>
        <el-form-item style="float: right;  margin-right: 100px">
          <el-select v-model="testEnv" style="margin-right: 20px" @visible-change='checkActiveTestEnv' clearable
                     placeholder="测试环境">
            <el-option
              v-for="(item,index) in testEnvs"
              :key="index+''"
              :label="item.name"
              :value="item._id">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </el-col>

    <!--计划列表-->
    <el-table @sort-change='sortChange' :data="planList" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="计划名称" min-width="25%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <router-link :to="{ name: 'PlanDetail', params: {plan_id: scope.row._id}}"
                       style='text-decoration: none;color: #000000;'>{{ scope.row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="计划描述" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="isParallel" label="是否并行" min-width="15%" show-overflow-tooltip>
        <template slot-scope="scope">
          <img v-show="scope.row.isParallel" src="../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.isParallel" src="../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="10%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createUser" label="创建者" min-width="10%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="10%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="10%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="40%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" :loading="executeLoading"
                     @click="executePlanByManual(scope.$index, scope.row)">执行
          </el-button>
          <el-button type="success" size="small" @click="checkReport(scope.$index, scope.row._id)">查看报告</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          <el-button type="info" size="small" :loading="statusChangeLoading"
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
        v-if="totalNum != 0"
        :page-sizes="[10, 20, 40]"
        :page-size="size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalNum">
      </el-pagination>
    </el-col>

    <!--编辑界面-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="formVisible" :close-on-click-modal="false"
               style="width: 75%; left: 10%">
      <el-form :model="form" label-width="100px" :rules="formRules" ref="form">
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="4" v-model="form.description"></el-input>
        </el-form-item>
        <el-form-item label="是否并行">
          <el-radio v-model="form.isParallel" :label="true">是</el-radio>
          <el-radio v-model="form.isParallel" :label="false">否</el-radio>
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
    import {addPlan, updatePlan, getPlans, executePlan} from "../../api/plan";
    import {getEnvConfigs} from "../../api/envConfig";

    export default {
        name: "PlanList",
        data() {
            return {
                filters: {
                    name: ""
                },
                testEnvs: [],
                testEnv: '',
                planList: [],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
                executeLoading: false,
                statusChangeLoading: false,
                selects: [],// 列表选中列

                formVisible: false,//编辑界面是否显示
                loading: false,
                titleMap: {
                    add: '新增',
                    edit: '编辑'
                },
                dialogStatus: '',
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入描述', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ]
                },
                //编辑界面数据
                form: {
                    name: '',
                    isParallel: false,
                    description: ''
                },
                initForm: {
                    name: '',
                    isParallel: false,
                    description: ''
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
            queryPlans(params) {
                this.listLoading = true;
                if (this.filters.name.trim() !== "") {
                    params['name'] = this.filters.name.trim();
                }
                let header = {};
                getPlans(params, header).then((res) => {
                    this.listLoading = false;
                    let {status, data} = res;
                    if (status === "ok") {
                        this.totalNum = data.totalNum;
                        this.planList = data.rows
                    } else {
                        this.$message.error({
                            message: data,
                            center: true
                        })
                    }
                }).catch((err) => {
                    this.$message.err({
                        message: '执行获取失败，请稍后刷新重试哦~',
                        center: true
                    });
                    this.listLoading = false;
                })
            },
            // 获取项目列表
            getPlanList() {
                let params = {
                    size: this.size,
                    skip: this.skip,
                    sortBy: this.sortBy,
                    order: this.order
                };
                this.queryPlans(params);
            },
            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该计划吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let self = this;
                    let params = {isDeleted: true};
                    let header = {
                        "Content-Type": "application/json",
                        "Authorization": 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                    };
                    updatePlan(row._id, params, header).then(_data => {
                        let {status, data} = _data;
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
                        self.getPlanList()
                    });
                })
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order
                };
                this.queryPlans(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order
                };
                this.queryPlans(params);
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
                this.queryPlans(params);
            },
            // 改变项目状态
            handleChangeStatus: function (index, row) {
                let self = this;
                this.statusChangeLoading = true;

                let header = {
                    "Content-Type": "application/json",
                    Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                };
                if (row.status) {
                    let params = {status: false};
                    updatePlan(row._id, params, header).then(_data => {
                        let {status, data} = _data;
                        this.statusChangeLoading = false;
                        if (status === 'ok') {
                            self.$message({
                                message: '状态变更成功',
                                center: true,
                                type: 'success'
                            })
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                        }
                        self.getPlanList()
                    });
                } else {
                    let params = {status: true};
                    updatePlan(row._id, params, header).then(_data => {
                        let {status, data} = _data;
                        this.statusChangeLoading = false;
                        if (status === 'ok') {
                            self.$message({
                                message: '状态变更成功',
                                center: true,
                                type: 'success'
                            })
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                        }
                        self.getPlanList()
                    });
                }
            },
            //显示新增界面
            handleAdd: function () {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, this.initForm);
                this.dialogStatus = 'add';
            },
            //编辑
            submit: function () {
                let self = this;
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.loading = true;
                            let header = {
                                "Content-Type": "application/json",
                                "Authorization": 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                            };
                            let params = JSON.stringify({
                                name: self.form.name.trim(),
                                description: self.form.description.trim(),
                                isParallel: self.form.isParallel,
                                createUser: self.$store.getters.email || 'anonymous'
                            });
                            addPlan(params, header).then(res => {
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
                                    self.getPlanList()
                                } else {
                                    self.$message.error({
                                        message: data,
                                        center: true,
                                    });
                                    self.$refs['form'].resetFields();
                                    self.formVisible = false;
                                    self.getPlanList()
                                }
                            })
                        });
                    }
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
            selectsChange: function (selects) {
                this.sels = selects;
            },
            executePlanByManual(index, row) {
                if (this.testEnv) {
                    row.executeStatus = true;
                    let self = this;
                    let headers = {"Content-Type": "application/json"};
                    let params = {
                        testEnvId: self.testEnv,
                        executionUser: self.$store.getters.email,
                    };
                    executePlan(row._id, params, headers).then((res) => {
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
                        self.getPlanList()
                    }).catch((error) => {
                        self.$message.error({
                            message: '计划执行异常/超时，请稍后重试哦~',
                            center: true,
                        });
                        self.getPlanList()
                    })
                } else {
                    this.$message({
                        message: '请选择测试环境, 在执行按钮上方哦~',
                        center: true,
                        type: 'warning'
                    })
                }
            },
            checkReport(index, plan_id) {
                this.$router.push({name: 'PlanReportList', params: {plan_id: plan_id}})
            }
        },
        mounted() {
            this.getPlanList()
            this.getTestEnvList()
        }
    }
</script>

<style lang="scss" scoped>
  .el-table .el-table__body .reportTableRow:hover > td {
    background-color: #F2F2F2;
  }

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
