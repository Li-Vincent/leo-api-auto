<template>
  <section>
    <!--页面title-->
    <strong class="title">{{$route.meta.title}}</strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" @submit.native.prevent>
        <router-link to="" style="text-decoration: none;color: aliceblue;">
          <el-button class="return-list" @click="$router.back(-1)">
            <i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回
          </el-button>
        </router-link>
      </el-form>
    </el-col>

    <!--DB列表-->
    <el-table :data="dbConfigs" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="dbType" label="DB类型" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createUser" label="创建者" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%">
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="20%">
        <template slot-scope="scope">
          <el-button type="primary" size="small">
            <router-link :to="{name:'ShowDBEnvConnect',params:{db_config_id: scope.row._id}}" style="color: #fff">连接信息
            </router-link>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script>
    import {getDBConfigs} from "../../../../api/dbConfig";

    export default {
        name: "ShowDBConfig",
        data() {
            return {
                dbConfigs: [],
                dbTypeOptions: [
                    {name: 'MongoDB', value: 'MongoDB'},
                    {name: 'MySQL', value: 'MySQL'}
                ],
                listLoading: false,
                statusChangeLoading: false,
                selects: [],//列表选中列
            }
        },
        methods: {
            // 获取环境列表
            queryDBConfigs(params) {
                this.listLoading = true;
                let self = this;
                let header = {};
                getDBConfigs(params, header).then((res) => {
                    let {status, data} = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                        self.totalNum = data.totalNum;
                        self.dbConfigs = data.rows
                    } else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    self.$message.error({
                        message: 'DB配置列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                    self.listLoading = false;
                });
            },
            getDBConfigList() {
                let params = {};
                this.queryDBConfigs(params);
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
        created() {
            this.getDBConfigList()
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
