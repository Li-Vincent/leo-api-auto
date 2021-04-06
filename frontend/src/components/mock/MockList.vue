<template>
  <section>
    <!--页面title-->
    <strong class="title">{{ $route.meta.title }}</strong>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <el-form-item>
          <el-input
            v-model="filters.name"
            placeholder="MockAPI名称"
            @keyup.enter.native="getMockList"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="filters.category"
            placeholder="MockAPI分类"
            @keyup.enter.native="getMockList"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-search" @click="getMockList"
            >查询</el-button
          >
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-plus" @click="handleAdd"
            >新增MockAPI</el-button
          >
        </el-form-item>
      </el-form>
    </el-col>

    <!--计划列表-->
    <el-table
      @sort-change="sortChange"
      :data="mockList"
      :row-style="reportRowStyle"
      :row-class-name="ReportTableRow"
      highlight-current-row
      v-loading="listLoading"
      @selection-change="selectsChange"
      style="width: 100%"
    >
      <el-table-column type="selection" min-width="5%"> </el-table-column>
      <el-table-column
        prop="name"
        label="Mock名称"
        min-width="25%"
        sortable="custom"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="category"
        label="Mock分类"
        min-width="15%"
        sortable="custom"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="requestMethod"
        label="Method"
        min-width="15%"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="path"
        label="Path"
        min-width="15%"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="description"
        label="描述"
        min-width="15%"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="lastUpdateTime"
        label="更新时间"
        min-width="10%"
        sortable="custom"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../assets/imgs/icon-yes.svg" />
          <img v-show="!scope.row.status" src="../../assets/imgs/icon-no.svg" />
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="40%">
        <template slot-scope="scope">
          <el-button
            type="success"
            size="small"
            @click="checkDetail(scope.$index, scope.row)"
            >查看详情
          </el-button>
          <el-button
            type="primary"
            size="small"
            @click="handleEdit(scope.$index, scope.row)"
            >编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="handleDel(scope.$index, scope.row)"
            >删除
          </el-button>
          <el-button
            type="info"
            size="small"
            :loading="statusChangeLoading"
            @click="handleChangeStatus(scope.$index, scope.row)"
          >
            {{ scope.row.status === false ? "启用" : "禁用" }}
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
        :total="totalNum"
      >
      </el-pagination>
    </el-col>

    <!--编辑界面-->
    <el-dialog
      :title="titleMap[dialogStatus]"
      :visible.sync="formVisible"
      :close-on-click-modal="false"
      style="width: 80%; left: 10%"
    >
      <el-form :model="form" label-width="120px" :rules="formRules" ref="form">
        <el-form-item label="Mock名称" prop="name">
          <el-input v-model="form.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="Mock分类" prop="category">
          <el-input v-model.trim="form.category" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="Method" prop="requestMethod">
          <el-select v-model="form.requestMethod" placeholder="请求方式">
            <el-option
              v-for="(item, index) in MethodOptions"
              :key="index + ''"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Path" prop="path">
          <el-input v-model="form.path" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="返回状态码" prop="responseCode">
          <el-select
            v-model="form.responseCode"
            clearable
            placeholder="返回状态码"
          >
            <el-option
              v-for="(item, index) in ResponseCodeOptions"
              :key="index + ''"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="responseBody" prop="responseBody">
          <el-input
            type="textarea"
            :rows="8"
            placeholder="请输入返回体，Json格式，如{'username': 'test'}"
            v-model.trim="form.responseBody"
          ></el-input>
        </el-form-item>
        <el-form-item label="延迟（秒）" prop="delaySeconds">
          <el-input
            v-model="form.delaySeconds"
            oninput="value=value.replace(/[^0-9.]/g,'')"
            auto-complete="off"
          ></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            type="textarea"
            :rows="4"
            v-model="form.description"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="formVisible = false">取消</el-button>
        <el-button type="primary" @click.native="submit" :loading="loading"
          >提交</el-button
        >
      </div>
    </el-dialog>

    <!--查看Mock详情-->
    <el-dialog
      title="Mock API 详情"
      :visible.sync="showMockDetail"
      :close-on-click-modal="false"
    >
      <div slot="title" class="header-title">
        <span style="font-size: 28px">Mock API 详情</span>
        <span v-show="mockDetail.name" style="font-size: 20px">
          - {{ mockDetail.name }}</span
        >
      </div>
      <div class="mock-detail">
        <div>Mock分类 : {{ mockDetail.category }}</div>
        <div>请求地址 : {{ mockDetail.url }}</div>
        <div>请求方式 : {{ mockDetail.requestMethod }}</div>
        <div>请求延迟 : {{ mockDetail.delaySeconds }} 秒</div>
        <div class="divider-line"></div>
        <div>返回状态码 : {{ mockDetail.responseCode }}</div>
        <div>返回体:</div>
        <div v-show="mockDetail.responseBody" class="resultStyle resultData">
          <pre>{{ mockDetail.responseBody }}</pre>
        </div>
      </div>
    </el-dialog>
  </section>
</template>

<script>
import { addMockAPI, getMockAPIs, updateMockAPI } from "../../api/mock";

export default {
  name: "PlanList",
  data() {
    return {
      filters: {
        name: "",
        category: "",
      },
      MethodOptions: [
        { label: "GET", value: "GET" },
        { label: "POST", value: "POST" },
        { label: "PUT", value: "PUT" },
        { label: "DELETE", value: "DELETE" },
        { label: "PATCH", value: "PATCH" },
        { label: "HEAD", value: "HEAD" },
        { label: "OPTIONS", value: "OPTIONS" },
      ],
      ResponseCodeOptions: [
        // 2xx （成功）
        { value: "200", label: "200 - 成功" },
        { value: "201", label: "201 - 已创建" },
        { value: "202", label: "202 - 已接受" },
        { value: "203", label: "203 - 非授权信息" },
        { value: "204", label: "204 - 无内容" },
        { value: "205", label: "205 - 重置内容" },
        { value: "206", label: "206 - 部分内容" },
        // 3xx （重定向）
        { value: "300", label: "300 - 多种选择" },
        { value: "301", label: "301 - 永久移动" },
        { value: "302", label: "302 - 临时移动" },
        { value: "303", label: "303 - 查看其他位置" },
        { value: "304", label: "304 - 未修改" },
        { value: "305", label: "305 - 使用代理" },
        { value: "307", label: "307 - 临时重定向" },
        // 4xx（请求错误）
        { value: "400", label: "400 - 错误请求" },
        { value: "401", label: "401 - 未授权" },
        { value: "403", label: "403 - 服务器拒绝请求" },
        { value: "404", label: "404 - 服务器找不到请求的网页" },
        { value: "405", label: "405 - 禁用请求中指定的方法" },
        // 5xx（服务器错误）
        { value: "500", label: "500 - 服务器内部错误" },
        { value: "501", label: "501 - 尚未实施" },
        { value: "502", label: "502 - 错误网关" },
        { value: "503", label: "503 - 服务不可用" },
        { value: "504", label: "504 - 网关超时" },
        { value: "505", label: "505 - HTTP 版本不受支持" },
        // 1xx（临时响应）
        { value: "100", label: "100 - 继续" },
        { value: "101", label: "101 - 切换协议" },
      ],
      mockList: [],
      size: 10,
      skip: 0,
      sortBy: "createAt",
      order: "descending",
      pageNum: 1,
      totalNum: 0,
      listLoading: false,
      statusChangeLoading: false,
      selects: [], // 列表选中列

      formVisible: false, //编辑界面是否显示
      loading: false,
      titleMap: {
        add: "新增",
        edit: "编辑",
      },
      dialogStatus: "",
      showMockDetail: false,
      mockDetail: {},
      formRules: {
        name: [
          { required: true, message: "请输入名称", trigger: "blur" },
          {
            min: 1,
            max: 100,
            message: "长度在 1 到 100 个字符",
            trigger: "blur",
          },
        ],
        requestMethod: [
          { required: true, message: "请选择RequestMethod", trigger: "blur" },
        ],
        path: [{ required: true, message: "请设置path", trigger: "blur" }],
        responseCode: [
          { required: true, message: "请选择ResponseCode", trigger: "blur" },
        ],
        responseBody: [
          { required: true, message: "请输入ResponseBody", trigger: "blur" },
        ],
        delaySeconds: [
          { required: true, message: "请输入延迟（秒）", trigger: "blur" },
        ],
        description: [
          { max: 1024, message: "不能超过1024个字符", trigger: "blur" },
        ],
      },
      //编辑界面数据
      form: {
        name: "",
        category: "",
        requestMethod: "GET",
        path: "/",
        responseCode: "200",
        responseBody: "",
        delaySeconds: 0.0,
        description: "",
      },
      initForm: {
        name: "",
        category: "",
        requestMethod: "GET",
        path: "/",
        responseCode: "200",
        responseBody: "",
        delaySeconds: 0.0,
        description: "",
      },
    };
  },
  methods: {
    queryMocks(params) {
      this.listLoading = true;
      if (this.filters.name.trim() !== "") {
        params["name"] = this.filters.name.trim();
      }
      if (this.filters.category.trim() !== "") {
        params["category"] = this.filters.category.trim();
      }
      let header = {};
      getMockAPIs(params, header)
        .then((res) => {
          this.listLoading = false;
          let { status, data } = res;
          if (status === "ok") {
            this.totalNum = data.totalNum;
            this.mockList = data.rows;
          } else {
            this.$message.error({
              message: data,
              center: true,
            });
          }
        })
        .catch((err) => {
          this.$message.err({
            message: "MockAPIList获取失败，请稍后刷新重试哦~",
            center: true,
          });
          this.listLoading = false;
        });
    },
    // 获取项目列表
    getMockList() {
      let params = {
        size: this.size,
        skip: this.skip,
        sortBy: this.sortBy,
        order: this.order,
      };
      this.queryMocks(params);
    },
    //删除
    handleDel: function (index, row) {
      this.$confirm("确认删除该Mock吗?", "提示", {
        type: "warning",
      }).then(() => {
        this.listLoading = true;
        let self = this;
        let params = { isDeleted: true };
        let header = {
          "Content-Type": "application/json",
          Authorization: "Token " + JSON.parse(sessionStorage.getItem("token")),
        };
        updateMockAPI(row._id, params, header).then((_data) => {
          let { status, data } = _data;
          if (status === "ok") {
            self.$message({
              message: "删除成功",
              center: true,
              type: "success",
            });
          } else {
            self.$message.error({
              message: data,
              center: true,
            });
          }
          self.getMockList();
        });
      });
    },
    handleSizeChange(val) {
      let self = this;
      self.size = val;
      let params = {
        size: self.size,
        skip: self.skip,
        sortBy: self.sortBy,
        order: self.order,
      };
      this.queryMocks(params);
    },
    handleCurrentChange(val) {
      let self = this;
      self.skip = (val - 1) * self.size;
      let params = {
        size: self.size,
        skip: self.skip,
        sortBy: self.sortBy,
        order: self.order,
      };
      this.queryMocks(params);
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
      };
      this.queryMocks(params);
    },
    // 改变Mock状态, 启用，禁用
    handleChangeStatus: function (index, row) {
      let self = this;
      this.statusChangeLoading = true;

      let header = {
        "Content-Type": "application/json",
        Authorization: "Token " + JSON.parse(sessionStorage.getItem("token")),
      };
      if (row.status) {
        let params = { status: false };
        updateMockAPI(row._id, params, header).then((_data) => {
          let { status, data } = _data;
          this.statusChangeLoading = false;
          if (status === "ok") {
            self.$message({
              message: "状态变更成功",
              center: true,
              type: "success",
            });
          } else {
            self.$message.error({
              message: data,
              center: true,
            });
          }
          self.getMockList();
        });
      } else {
        let params = { status: true };
        updateMockAPI(row._id, params, header).then((_data) => {
          let { status, data } = _data;
          this.statusChangeLoading = false;
          if (status === "ok") {
            self.$message({
              message: "状态变更成功",
              center: true,
              type: "success",
            });
          } else {
            self.$message.error({
              message: data,
              center: true,
            });
          }
          self.getMockList();
        });
      }
    },
    //显示新增界面
    handleAdd: function () {
      this.formVisible = true;
      this.form = Object.assign({}, this.form, this.initForm);
      this.dialogStatus = "add";
    },
    //显示编辑界面
    handleEdit: function (index, row) {
      this.formVisible = true;
      this.form = Object.assign({}, this.form, row);
      this.form.responseBody = JSON.stringify(
        this.form.responseBody,
        undefined,
        4
      );
      this.form.responseBody = this.form.responseBody
        .replace(/'/g, '"')
        .replace(/None/g, "null")
        .replace(/True/g, "true")
        .replace(/False/g, "false");
      if (this.form.responseBody === "{}") {
        this.form.responseBody = "";
      }
      this.dialogStatus = "edit";
    },
    //编辑
    submit: function () {
      let self = this;
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.$confirm("确认提交吗？", "提示", {}).then(() => {
            self.loading = true;
            let header = {
              "Content-Type": "application/json",
              Authorization:
                "Token " + JSON.parse(sessionStorage.getItem("token")),
            };
            if (this.dialogStatus == "add") {
              let params = JSON.stringify({
                name: self.form.name.trim(),
                category: self.form.category.trim(),
                requestMethod: self.form.requestMethod.trim(),
                path: self.form.path.trim(),
                responseCode: self.form.responseCode.trim(),
                responseBody: self.form.responseBody.trim(),
                delaySeconds: parseFloat(self.form.delaySeconds),
                description: self.form.description.trim(),
              });
              addMockAPI(params, header).then((res) => {
                let { status, data } = res;
                self.loading = false;
                if (status === "ok") {
                  self.$message({
                    message: "添加成功",
                    center: true,
                    type: "success",
                  });
                  self.$refs["form"].resetFields();
                  self.formVisible = false;
                  self.getMockList();
                } else {
                  self.$message.error({
                    message: data,
                    center: true,
                  });
                  self.$refs["form"].resetFields();
                  self.formVisible = false;
                  self.getMockList();
                }
              });
            } else if (this.dialogStatus == "edit") {
              console.log(self.form.delaySeconds);
              let params = {
                name: self.form.name.trim(),
                category: self.form.category.trim(),
                requestMethod: self.form.requestMethod.trim(),
                path: self.form.path.trim(),
                responseCode: self.form.responseCode.trim(),
                responseBody: self.form.responseBody.trim(),
                delaySeconds: parseFloat(self.form.delaySeconds),
                description: self.form.description.trim(),
              };
              updateMockAPI(self.form._id, params, header).then((res) => {
                let { status, data } = res;
                self.loading = false;
                if (status === "ok") {
                  self.$message({
                    message: "更新成功",
                    center: true,
                    type: "success",
                  });
                  self.$refs["form"].resetFields();
                  self.formVisible = false;
                  self.getMockList();
                } else {
                  self.$message.error({
                    message: data,
                    center: true,
                  });
                  self.getMockList();
                }
              });
            } else {
              self.$message.error({
                message: "系统出错",
                center: true,
              });
              self.getMockList();
            }
          });
        }
      });
    },
    // 修改table tr行的背景色
    reportRowStyle({ row, rowIndex }) {
      if (!(row.status === true)) return "background-color: #DDDDDD";
      else {
        return "";
      }
    },
    ReportTableRow({ row, rowIndex }) {
      return "reportTableRow";
    },
    selectsChange: function (selects) {
      this.sels = selects;
    },
    checkDetail(index, mock_api) {
      this.showMockDetail = true;
      this.mockDetail = mock_api;
      this.mockDetail["url"] =
        window.document.location.protocol +
        "//" +
        window.document.location.host +
        "/mock" +
        this.mockDetail["path"];
    },
  },
  mounted() {
    this.getMockList();
  },
};
</script>

<style lang="scss" scoped>
.el-table .el-table__body .reportTableRow:hover > td {
  background-color: #f2f2f2;
}

.title {
  width: 200px;
  float: left;
  color: #475669;
  font-size: 25px;
  margin: 10px 5px;
  font-family: Arial;
}

.mock-detail {
  min-height: 400px;
  margin-top: -20px;
  overflow: auto;
  overflow-x: hidden;
  border: 1px solid #e6e6e6;
  font-size: 16px;
  font-family: Consolas, "Microsoft YaHei";
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
    position: relative;
  }
}

.return-list {
  margin-top: 0px;
  margin-bottom: 10px;
  margin-left: 20px;
  border-radius: 25px;
}
</style>
