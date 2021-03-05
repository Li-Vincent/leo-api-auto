<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}} <span v-if="dbConfig.name"> - DB: {{dbConfig.name}}</span> </strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
        <el-form-item style="float: right; margin-right: 95px">
          <el-button>*请点击列表中元素的空白处以刷新数据*</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--DB列表-->
    <el-table :data="dbEnvConnects" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="testEnvName" label="环境名称" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="dbType" label="DB Type" min-width="20%" show-overflow-tooltip>
        <template>
          <span v-if="dbConfig.dbType">{{dbConfig.dbType}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="dbHost" label="DB Host" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="dbPort" label="DB Port" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="dbUser" label="DB User" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="dbPassword" label="DB Password" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="dbName" label="Database Name" min-width="20%" show-overflow-tooltip>
      </el-table-column>
    </el-table>
  </section>
</template>

<script>
    import {getTestEnvs} from "../../../../api/testEnv";
    import {getEnvConfigs} from "../../../../api/envConfig";
    import {getDBEnvConnect, getDBConfig, updateDBEnvConnect} from "../../../../api/dbConfig";

    export default {
        name: "ShowDBEnvConnect",
        data() {
            return {
                dbConfigName: "",
                listLoading: false,
                statusChangeLoading: false,
                selects: [],//列表选中列
                testEnvs: [],
                dbConfig: {
                    name: '',
                    dbType: ''
                },
                dbEnvConnects: [{
                    testEnvId: '',
                    testEnvName: '',
                    dbHost: '',
                    dbPort: '',
                    dbUser: '',
                    dbPassword: '',
                    dbName: ''
                }],
                loading: false,
            }
        },
        methods: {
            selectsChange: function (selects) {
                this.selects = selects;
            },
            // 修改table tr行的背景色
            reportRowStyle({row, rowIndex}) {
                if (!(row.status === true))
                    return 'background-color: #FFF'
                else {
                    return ''
                }
            },
            ReportTableRow({row, rowIndex}) {
                return 'reportTableRow';
            },
            getTestEnvList() {
                let header = {};
                let params = {}
                getEnvConfigs(params, header).then((res) => {
                    let {status, data} = res;
                    if (status === 'ok') {
                        this.testEnvs = data.rows
                    } else {
                        this.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                    return data.rows
                }).catch((error) => {
                    this.$message.error({
                        message: '环境列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                });
            },
            getDBConfigInfo() {
                getDBConfig(this.$route.params.db_config_id).then((res) => {
                    let {status, data} = res;
                    if (status === 'ok') {
                        this.dbConfig = data
                    } else {
                        this.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    this.$message.error({
                        message: 'DB Config获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                });
            },
            getDBEnvConnects() {
                let testEnvs = this.testEnvs;
                this.dbEnvConnects = [];
                for (let i in testEnvs) {
                    let env = testEnvs[i];
                    let dbEnvConnect = {}
                    dbEnvConnect['testEnvId'] = env['_id'];
                    dbEnvConnect['testEnvName'] = env['name'];
                    let header = {
                        'Content-Type': 'application/json'
                    }
                    let params = {
                        testEnvId: env['_id'],
                        dbConfigId: this.$route.params.db_config_id
                    }
                    getDBEnvConnect(params, header).then((res) => {
                        let {status, data} = res;
                        if (status === 'ok') {
                            if (data['dbHost']) {
                                dbEnvConnect['dbHost'] = data['dbHost'];
                                dbEnvConnect['dbPort'] = data['dbPort'];
                                dbEnvConnect['dbUser'] = data['dbUser'];
                                dbEnvConnect['dbPassword'] = data['dbPassword'];
                                dbEnvConnect['dbName'] = data['dbName'];
                            }
                        } else {
                            this.$message.error({
                                message: data,
                                center: true,
                            })
                        }
                    }).catch((error) => {
                        this.$message.error({
                            message: 'DB连接获取失败，请稍后刷新重试哦~',
                            center: true,
                        });
                    });
                    this.dbEnvConnects.push(dbEnvConnect)
                }
            }
        },
        watch: {
            testEnvs: {//深度监听，可监听到对象、数组的变化
                handler(val, oldVal) {
                    this.getDBEnvConnects()
                },
                deep: true
            }
        },
        created() {
            this.getTestEnvList();
            this.getDBConfigInfo();
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
