<template>
  <section>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <el-form-item>
          <el-input v-model="filters.name" placeholder="项目名称" @keyup.enter.native="getProjectList"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-search" @click="getProjectList">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-plus" @click="handleAdd">新增项目</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--项目列表-->
    <el-table @sort-change='sortChange' :data="projects" :row-style="reportRowStyle" :row-class-name="ReportTableRow"
              highlight-current-row v-loading="listLoading" @selection-change="selectsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="项目名称" min-width="30%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <el-icon name="name"></el-icon>
          <router-link :to="{ name: 'TestSuiteList', params: {project_id: scope.row._id}}"
                       style='text-decoration: none;color: #000000;'>
            {{ scope.row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="version" label="版本号" min-width="12%">
      </el-table-column>
      <el-table-column prop="description" label="项目描述" min-width="20%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createUser" label="创建者" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="更新时间" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateUser" label="更新者" min-width="20%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="13%" sortable>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="50%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          <el-button type="info" size="small" @click="handleChangeStatus(scope.$index, scope.row)">
            {{scope.row.status===false?'启用':'禁用'}}
          </el-button>
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
        v-if="totalNum != 0"
        :page-sizes="[10, 20, 40]"
        :page-size="size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalNum">
      </el-pagination>
    </el-col>

    <!--编辑界面-->
    <el-dialog :title="titleMap[dialogStatus]" :visible.sync="formVisible" :close-on-click-modal="false"
               style="width: 75%; left: 12.5%">
      <el-form :model="form" label-width="80px" :rules="formRules" ref="form">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="版本号" prop='version'>
              <el-input v-model="form.version" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="6" v-model="form.description"></el-input>
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
    import {addProject, updateProject, getProjects} from "../../api/project";

    export default {
        name: "ProjectList",
        data() {
            return {
                projectTestType: "apiTest",
                filters: {
                    name: ""
                },
                projects: [],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
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
                        {min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur'}
                    ],
                    version: [
                        {required: true, message: '请输入版本号', trigger: 'blur'},
                        {min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur'}
                    ],
                    description: [
                        {required: false, message: '请输入描述', trigger: 'blur'},
                        {max: 1024, message: '不能超过1024个字符', trigger: 'blur'}
                    ]
                },
                //编辑界面数据
                form: {
                    _id: '',
                    name: '',
                    version: '',
                    description: ''
                },
                initForm: {
                    _id: '',
                    name: '',
                    version: '',
                    description: ''
                }
            }
        },
        methods: {
            queryProjects(params) {
                this.listLoading = true;
                if (this.filters.name.trim() !== "") {
                    params['name'] = this.filters.name.trim();
                }
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
            // 获取项目列表
            getProjectList() {
                let params = {
                    size: this.size,
                    skip: this.skip,
                    sortBy: this.sortBy,
                    order: this.order,
                    projectTestType: this.projectTestType
                };
                this.queryProjects(params);
            },
            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let self = this;
                    let params = {isDeleted: true};
                    let header = {
                        "Content-Type": "application/json",
                        Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                    };
                    updateProject(row._id, params, header).then(_data => {
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
                        self.getProjectList()
                    });
                })
            },
            handleSizeChange(val) {
                let self = this;
                self.size = val;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectTestType: self.projectTestType
                };
                this.queryProjects(params);
            },
            handleCurrentChange(val) {
                let self = this;
                self.skip = (val - 1) * self.size;
                let params = {
                    size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                    projectTestType: self.projectTestType
                };
                this.queryProjects(params);
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
                    projectTestType: self.projectTestType
                };
                this.queryProjects(params);
            },
            // 改变项目状态
            handleChangeStatus: function (index, row) {
                let self = this;
                this.listLoading = true;

                let header = {
                    "Content-Type": "application/json",
                    Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                };
                if (row.status) {
                    let params = {status: false};
                    updateProject(row._id, params, header).then(_data => {
                        let {status, data} = _data;
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
                        self.getProjectList()
                    });
                } else {
                    let params = {status: true};
                    updateProject(row._id, params, header).then(_data => {
                        let {status, data} = _data;
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
                        self.getProjectList()
                    });
                }
            },
            //显示编辑界面
            handleEdit: function (index, row) {
                this.formVisible = true;
                this.form = Object.assign({}, this.form, row);
                this.dialogStatus = 'edit';
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
                            //NProgress.start();
                            let header = {
                                "Content-Type": "application/json",
                                Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                            };
                            if (this.dialogStatus == 'edit') {
                                let params = {
                                    name: self.form.name,
                                    version: self.form.version,
                                    description: self.form.description,
                                    lastUpdateUser: self.$store.getters.email || '匿名用户'
                                };
                                updateProject(self.form._id, params, header).then(_data => {
                                    let {status, data} = _data;
                                    self.loading = false;
                                    if (status === 'ok') {
                                        self.$message({
                                            message: '修改成功',
                                            center: true,
                                            type: 'success'
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getProjectList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        })
                                    }
                                });
                            } else if (this.dialogStatus == 'add') {
                                let params = JSON.stringify({
                                    name: self.form.name,
                                    projectTestType: self.projectTestType,
                                    version: self.form.version,
                                    description: self.form.description,
                                    createUser: self.$store.getters.email || '匿名用户'
                                });
                                addProject(params, header).then(res => {
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
                                        self.getProjectList()
                                    } else {
                                        self.$message.error({
                                            message: data,
                                            center: true,
                                        });
                                        self.$refs['form'].resetFields();
                                        self.formVisible = false;
                                        self.getProjectList()
                                    }
                                })
                            } else {
                                self.$message.error({
                                    message: "系统出错",
                                    center: true,
                                });
                                self.getProjectList()
                            }
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
            }
        },
        mounted() {
            this.getProjectList()
        }
    }
</script>

<style lang="scss" scoped>
  .el-table .el-table__body .reportTableRow:hover > td {
    background-color: #F2F2F2;
  }
</style>
