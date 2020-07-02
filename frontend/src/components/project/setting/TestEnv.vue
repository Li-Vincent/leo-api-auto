<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}}</strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="margin-left: 35px">
          <router-link :to="{name:'ShowDBConfig'}" style="text-decoration: none;color: aliceblue;">
            <el-button type="primary"><i class="fa fa-database"></i> DB配置</el-button>
          </router-link>
        </el-form-item>
        <div style="float: right; margin-right: 95px">
          <el-form-item>
            <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getTestEnvList"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getTestEnvList"> 查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>

    <!--环境列表-->
    <el-table @sort-change='sortChange' :data="testEnvs" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="15%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <router-link :to="{ name: 'TestEnvParam', params: {test_env_id: scope.row._id}}"
                       style='text-decoration: none;color: #000000;'>
            {{ scope.row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="domain" label="域名" min-width="35%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createUser" label="创建者" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
    </el-table>

    <!--翻页工具条-->
    <el-col :span="24" class="toolbar">
      <!--<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>-->
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
    import {getEnvConfigs} from "../../../api/envConfig";

    export default {
        name: "TestEnv",
        data() {
            return {
                filters: {
                    name: ''
                },
                testEnvs: [],
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
                formVisible: false,//dialog是否显示
                loading: false,
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur'}
                    ],
                    domain: [
                        {required: true, message: '请输入域名', trigger: 'blur'},
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
                    domain: '',
                    description: ''
                },
                initForm: {
                    name: '',
                    domain: '',
                    description: ''
                }
            }
        },
        methods: {
            // 获取环境列表
            queryTestEnvs(params) {
                this.listLoading = true;
                let self = this;
                if (self.filters.name.trim() !== '') {
                    params['name'] = self.filters.name.trim()
                }
                let header = {};
                getEnvConfigs(params, header).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.testEnvs = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: '环境列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            getTestEnvList() {
                let self = this;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryTestEnvs(params);
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryTestEnvs(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                let params = {
                    size: self.size,
                    skip: self.skip,
                    sortBy: self.sortBy,
                    order: self.order
                };
                this.queryTestEnvs(params);
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
                this.queryTestEnvs(params);
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
            this.getTestEnvList();
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
</style>
