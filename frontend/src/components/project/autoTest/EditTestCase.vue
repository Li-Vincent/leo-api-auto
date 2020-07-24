<template>
  <section>
    <!--页面title-->
    <el-col :span="24"><strong class="title">{{$route.meta.title}}</strong></el-col>

    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px">
      <router-link :to="{
                    name: 'TestCaseList', params: {
                      project_id: this.$route.params.project_id,
                      test_case_id: this.$route.params.test_case_id
                    }
                }" style='text-decoration: none;color: aliceblue;'>
        <el-button class="return-list"><i class="el-icon-d-arrow-left" return-list style="margin-right: 5px"></i>返回
        </el-button>
      </router-link>
      <div style="float: right;  margin-right: 80px">
        <router-link :to="{
                    name: 'TestCaseList', params: {
                      project_id: this.$route.params.project_id,
                      test_case_id: this.$route.params.test_case_id
                    }
                }" style='text-decoration: none;color: aliceblue;'>
          <el-button class="return-list">
            <i class="el-icon-close" return-list style="margin-right: 5px"></i>取消
          </el-button>
        </router-link>
        <el-button class="return-list" type="primary" @click.native="updateCaseInfo">
          <i class="el-icon-check" return-list style="margin-right: 5px"></i>保存
        </el-button>
      </div>
    </el-col>

    <el-col :span="24">
      <el-form :model="form" ref="form" :rules="formRules">
        <!--基本信息-->
        <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
          <el-row :gutter="10">
            <el-col :span="18">
              <el-form-item label="接口名称:" label-width="83px" prop="name">
                <el-input v-model="form.name" placeholder="名称" auto-complete></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="Service:" label-width="83px" prop="service">
                <el-input v-model.trim="form.service" placeholder="所属Service" auto-complete></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-col :span="4">
              <el-form-item label="URL:" label-width="83px">
                <el-select v-model="form.requestMethod" placeholder="请求方式" @change="checkRequestMethod">
                  <el-option v-for="(item,index) in MethodOptions" :key="index+''" :label="item.label"
                             :value="item.value"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="3">
              <el-form-item>
                <el-select v-model="form.requestProtocol" placeholder="HTTP协议">
                  <el-option v-for="(item,index) in ProtocolOptions" :key="index+''" :label="item.label"
                             :value="item.value"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span='6'>
              <el-form-item prop="domain">
                <el-input v-model.trim="form.domain" placeholder="请输入访问域名(优先级最高)" auto-complete></el-input>
              </el-form-item>
            </el-col>
            <el-col :span='8'>
              <el-form-item prop="route">
                <el-input v-model.trim="form.route" placeholder="请输入接口路由" auto-complete></el-input>
              </el-form-item>
            </el-col>
            <el-col :span='3' style="float: right">
              <el-checkbox label='请求前是否清除Cookie' v-model.trim="form.isClearCookie">
              </el-checkbox>
            </el-col>
          </el-row>
          <el-row :gutter="10">
            <el-form-item prop="description">
              <el-input type="textarea" :rows="5" v-model="form.description" placeholder="请输入用例描述"
                        auto-complete></el-input>
            </el-form-item>
          </el-row>
        </div>

        <el-row :span="24">
          <el-collapse v-model="activeNames" @change="handleChange">

            <el-collapse-item title="数据初始化" name="1">
              <el-table :data="form.dataInitializes" highlight-current-row>
                <el-table-column prop="dbType" label="DB Type" min-width="10%" sortable>
                  <template slot-scope="scope">
                    <el-select placeholder="请选择DB类型" clearable filterable allow-create default-first-option
                               v-model="scope.row.dbType" style="width:90%">
                      <el-option v-for="(item,index) in DBTypeOptions" :key="index+''" :label="item.label"
                                 :value="item.value"></el-option>
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column prop="dbConfig" label="选择DB" min-width="10%" sortable>
                  <template slot-scope="scope">
                    <el-select placeholder="请选择DB" clearable filterable allow-create default-first-option
                               v-model="scope.row.dbConfigId" style="width:90%">
                      <el-option v-for="(item,index) in dbConfigs" :key="index+''" :label="item.name"
                                 :value="item._id"></el-option>
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column type="expand">
                  <template slot-scope="props">
                    <el-row :gutter="10" v-if="props.row.dbType == 'MongoDB'">
                      <el-col :span="10">
                        <el-form-item label="Mongo CRUD:" label-width="120px">
                          <el-select placeholder="请选择方法" clearable filterable allow-create default-first-option
                                     v-model="props.row.mongoCrud" style="width:90%">
                            <el-option v-for="(item,index) in MongoCRUDOptions" :key="index+''" :label="item.label"
                                       :value="item.value"></el-option>
                          </el-select>
                        </el-form-item>
                      </el-col>
                      <el-col :span="10">
                        <el-form-item label="Collection:" label-width="83px">
                          <el-input v-model="props.row.collection" :value="props.row.collection"
                                    placeholder="请输入要变更的collection"></el-input>
                        </el-form-item>
                      </el-col>
                    </el-row>
                    <el-row :gutter="10" v-if="props.row.dbType == 'MongoDB'">
                      <el-col :span="10" v-if="props.row.mongoCrud != 'insert_one'">
                        <el-form-item label="查询条件:" label-width="120px">
                          <el-input type="textarea" :rows="5" v-model="props.row.query" :value="props.row.query"
                                    placeholder="请输入查询条件,Update适用,例:{'key': 'value'}, 注意：true->True,false->False,null->None"></el-input>
                        </el-form-item>
                      </el-col>
                      <el-col :span="10">
                        <el-form-item label="变更内容:" label-width="120px">
                          <el-input type="textarea" :rows="5" v-model="props.row.set" :value="props.row.set"
                                    placeholder="请输入要变更(插入)的内容,例:{'key': 'value'}, 注意：true->True,false->False,null->None"></el-input>
                        </el-form-item>
                      </el-col>
                    </el-row>
                    <el-row :gutter="10" v-if="props.row.dbType != 'MongoDB'">
                      <el-col :span="20">
                        <el-form-item label="SQL:" label-width="80px">
                          <el-input type="textarea" :rows="5" v-model="props.row.sql" :value="props.row.sql"
                                    placeholder="请输入SQL语句"></el-input>
                        </el-form-item>
                      </el-col>
                    </el-row>
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="5%">
                  <template slot-scope="scope">
                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;"
                       @click="delDataInit(scope.$index)"></i>
                  </template>
                </el-table-column>
                <el-table-column label="" min-width="10%">
                  <template slot-scope="scope">
                    <el-button v-if="scope.$index===(form.dataInitializes.length-1)" size="mini" class="el-icon-plus"
                               @click="addDataInit"></el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-collapse-item>

            <el-collapse-item title="请求头部" name="2">
              <el-table :data="form.headers" highlight-current-row>
                <el-table-column prop="name" label="标签" min-width="15%" sortable>
                  <template slot-scope="scope">
                    <el-select placeholder="请输入/选择标签" clearable filterable allow-create default-first-option
                               v-model.trim="scope.row.name" style="width:90%">
                      <el-option v-for="(item,index) in HeaderOptions" :key="index+''" :label="item.label"
                                 :value="item.value"></el-option>
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="内容" min-width="20%" sortable>
                  <template slot-scope="scope">
                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入内容"></el-input>
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="5%">
                  <template slot-scope="scope">
                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;"
                       @click="delHeader(scope.$index)"></i>
                  </template>
                </el-table-column>
                <el-table-column label="" min-width="10%">
                  <template slot-scope="scope">
                    <el-button v-if="scope.$index===(form.headers.length-1)" size="mini" class="el-icon-plus"
                               @click="addHeader"></el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-collapse-item>

            <el-collapse-item title="请求参数" name="3">
              <div style="margin: 5px">
                <el-row :span="24">
                  <!--                  <el-col :span="4">-->
                  <!--                    <el-radio v-model="radio" label="form-data">表单(form-data)</el-radio>-->
                  <!--                  </el-col>-->
                  <el-col v-if="showRequestBody" :span="4">
                    <el-radio v-model="radio" label="raw">源数据(raw) —— 支持json数组</el-radio>
                  </el-col>
                  <el-col :span='3' style="float: right">
                    <el-checkbox label='是否 json数组' v-model.trim="form.isJsonArray">
                    </el-checkbox>
                  </el-col>
                  <!--                  <el-col v-if="showRequestBody" :span="16">-->
                  <!--                    <el-checkbox v-model="radioType" label="3" v-show="parameterType">表单转源数据</el-checkbox>-->
                  <!--                  </el-col>-->
                </el-row>
                <template>
                  <el-form-item label="" prop="parameterRaw">
                    <el-input type="textarea" :rows="8" placeholder="请输入参数内容({'username': 'test'})"
                              v-model.trim="form.parameterRaw"></el-input>
                  </el-form-item>
                </template>
              </div>
              <!--<el-table :data="form.parameter" highlight-current-row :class="ParameterType? 'parameter-a': 'parameter-b'">-->
              <!--<el-table-column prop="name" label="参数名" min-width="28%" sortable>-->
              <!--<template slot-scope="scope">-->
              <!--<el-input v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>-->
              <!--</template>-->
              <!--</el-table-column>-->
              <!--<el-table-column prop="value" label="参数值" min-width="40%" sortable>-->
              <!--<template slot-scope="scope">-->
              <!--<el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>-->
              <!--</template>-->
              <!--</el-table-column>-->
              <!--<el-table-column prop="interrelate" label="是否关联" min-width="13%" sortable>-->
              <!--<template slot-scope="scope">-->
              <!--<el-switch v-model="scope.row.interrelate">-->
              <!--</el-switch>-->
              <!--</template>-->
              <!--</el-table-column>-->
              <!--<el-table-column min-width="7%">-->
              <!--<template slot-scope="scope">-->
              <!--<el-button type="primary" size="mini" style="margin-bottom: 5px" v-show="scope.row.interrelate" @click="handleCorrelation(scope.$index, scope.row)">关联</el-button>-->
              <!--</template>-->
              <!--</el-table-column>-->
              <!--<el-table-column label="操作" min-width="7%">-->
              <!--<template slot-scope="scope">-->
              <!--<i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delParameter(scope.$index)"></i>-->
              <!--</template>-->
              <!--</el-table-column>-->
              <!--<el-table-column label="" min-width="5%">-->
              <!--<template slot-scope="scope">-->
              <!--<el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>-->
              <!--</template>-->
              <!--</el-table-column>-->
              <!--</el-table>-->

            </el-collapse-item>

            <el-collapse-item title="返回结果设置全局变量(Suite级别)" name="4">
              <el-table :data="form.setGlobalVars" highlight-current-row>
                <el-table-column prop="name" label="变量名" min-width="20%">
                  <template slot-scope="scope">
                    <el-input v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入变量名"></el-input>
                  </template>
                </el-table-column>
                <el-table-column prop="query" label="变量查询语句" min-width="30%" sortable>
                  <template slot-scope="scope">
                    <el-select style="width: 70%;" v-model.trim="scope.row.query"
                               @change="addSuffix(scope.row.query)" multiple clearable filterable default-first-option
                               allow-create placeholder="请输入变量查询语句(不输入则返回整个JSON字符串)">
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="5%">
                  <template slot-scope="scope">
                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;"
                       @click="delGlobalVars(scope.$index)"></i>
                  </template>
                </el-table-column>
                <el-table-column label="" min-width="10%">
                  <template slot-scope="scope">
                    <el-button v-if="scope.$index===(form.setGlobalVars.length-1)" size="mini" class="el-icon-plus"
                               @click="addGlobalVars"></el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-collapse-item>

            <el-collapse-item title="测试结果校验" name="5">
              <el-card class="box-card">
                <div slot="header">
                  <el-radio-group v-model="form.checkResponse">
                    <el-radio-button label="noCheck">
                      <div>不校验</div>
                    </el-radio-button>
                    <el-radio-button label="checkResponseCode">
                      <div>HTTP状态校验</div>
                    </el-radio-button>
                    <el-radio-button label="checkResponseBody">
                      <div>JSON正则校验</div>
                    </el-radio-button>
                    <el-radio-button label="checkResponseNumber">
                      <div>数值校验</div>
                    </el-radio-button>
                  </el-radio-group>
                </div>

                <div v-show="showResponseCodeCheck">
                  <el-select v-model="form.checkResponseCode" clearable placeholder="HTTP返回状态">
                    <el-option v-for="(item,index) in ResponseCodeOptions" :key="index+''" :label="item.label"
                               :value="item.value"></el-option>
                  </el-select>
                </div>
                <div v-show="showResponseBodyCheck">
                  <el-collapse-item title="JSON正则校验" name="4">
                    <el-table :data="form.checkResponseBody" highlight-current-row>
                      <el-table-column prop="regex" label="正则语句" min-width="20%">
                        <template slot-scope="scope">
                          <el-input v-model.trim="scope.row.regex" placeholder="请输入正则语句"></el-input>
                        </template>
                      </el-table-column>
                      <el-table-column prop="query" label="变量查询语句" min-width="30%">
                        <template slot-scope="scope">
                          <el-select style="width: 70%;" v-model.trim="scope.row.query"
                                     @change="addSuffix(scope.row.query)" multiple filterable clearable
                                     default-first-option allow-create
                                     placeholder="请输入变量查询语句(不输入则返回整个JSON字符串)">
                          </el-select>
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" min-width="5%">
                        <template slot-scope="scope">
                          <i class="el-icon-delete" style="font-size:30px;cursor:pointer;"
                             @click="delCheckResBody(scope.$index)"></i>
                        </template>
                      </el-table-column>
                      <el-table-column label="" min-width="10%">
                        <template slot-scope="scope">
                          <el-button v-if="scope.$index===(form.checkResponseBody.length-1)" size="mini"
                                     class="el-icon-plus"
                                     @click="addCheckResBody"></el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </el-collapse-item>
                </div>
                <div v-show="showResponseNumCheck">
                  <el-collapse-item title="数值校验" name="5">
                    <el-table :data="form.checkResponseNumber" highlight-current-row>
                      <el-table-column label="数值一" min-width="5%">
                        <template slot-scope="scope">
                          <el-input v-model.trim="scope.row.expressions.firstArg" placeholder="请输入数值一"></el-input>
                        </template>
                      </el-table-column>
                      <el-table-column label="运算" min-width="3%">
                        <template slot-scope="scope">
                          <el-select v-model.trim="scope.row.expressions.operator" clearable placeholder="请选择运算">
                            <el-option v-for="(item,index) in operatorOptions" :key="index" :label="item.label"
                                       :value="item.value"></el-option>
                          </el-select>
                        </template>
                      </el-table-column>
                      <el-table-column label="数值二" min-width="5%">
                        <template slot-scope="scope">
                          <el-input v-model.trim="scope.row.expressions.secondArg" placeholder="请输入数值二"></el-input>
                        </template>
                      </el-table-column>
                      <el-table-column label="判断" min-width="3%">
                        <template slot-scope="scope">
                          <el-select v-model.trim="scope.row.expressions.judgeCharacter" clearable placeholder="请选择判断">
                            <el-option v-for="(item,index) in judgeCharacterOptions" :key="index" :label="item.label"
                                       :value="item.value"></el-option>
                          </el-select>
                        </template>
                      </el-table-column>
                      <el-table-column label="期待结果" min-width="5%">
                        <template slot-scope="scope">
                          <el-input v-model.trim="scope.row.expressions.expectResult" placeholder="请输入期待结果"></el-input>
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" min-width="1%">
                        <template slot-scope="scope">
                          <i class="el-icon-delete" style="font-size:30px;cursor:pointer;"
                             @click="delCheckResNum(scope.$index)"></i>
                        </template>
                      </el-table-column>
                      <el-table-column label="" min-width="5%">
                        <template slot-scope="scope">
                          <el-button v-if="scope.$index===(form.checkResponseNumber.length-1)" size="mini"
                                     class="el-icon-plus" @click="addCheckResNum"></el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </el-collapse-item>
                </div>
              </el-card>
            </el-collapse-item>
          </el-collapse>
        </el-row>
      </el-form>
    </el-col>
  </section>
</template>

<script>
    import {getCaseDetail, updateTestCase} from "../../../api/testCase";
    import {getDBConfigs} from "../../../api/dbConfig";

    export default {
        name: "EditTestCase",
        data() {
            let checkJson = (rule, value, callback) => {
                if (value !== "" && value !== null) {
                    value = value.replace(/'/g, "\"")
                    try {
                        let obj = JSON.parse(value)
                        if (typeof obj == 'object' && obj) {
                            callback()
                        } else {
                            callback(new Error('参数格式不正确!'))
                            this.$message.warning({
                                message: '参数格式不正确!',
                                center: true,
                            });
                        }
                    } catch (e) {
                        console.log(value, e)
                        callback(new Error('参数格式不正确!'))
                        this.$message.warning({
                            message: '参数格式不正确!',
                            center: true,
                        });
                    }
                } else {
                    callback()
                }
            };
            let checkRoute = (rule, value, callback) => {
                if (value !== "" && value !== null) {
                    if (value.indexOf('/') == 0) {
                        callback()
                    } else {
                        callback(new Error('请输入路由(如: /chat)'))
                        this.$message.warning({
                            message: '路由格式不正确!',
                            center: true,
                        });
                    }
                } else {
                    callback()
                }
            };
            return {
                activeNames: ['1', '2', '3', '4', '5', '6'],
                MethodOptions: [
                    {label: "GET", value: "GET"},
                    {label: "POST", value: "POST"},
                    {label: "PUT", value: "PUT"},
                    {label: "DELETE", value: "DELETE"},
                    {label: "OPTIONS", value: "OPTIONS"},
                    {label: "PATCH", value: "PATCH"},
                    {label: "HEAD", value: "HEAD"}
                ],
                ProtocolOptions: [
                    {value: '', label: '未选择'},
                    {value: 'HTTP', label: 'HTTP'},
                    {value: 'HTTPS', label: 'HTTPS'}
                ],
                DBTypeOptions: [
                    {value: 'MongoDB', label: 'MongoDB'},
                    {value: 'MySQL', label: 'MySQL'}
                ],
                MongoCRUDOptions: [
                    {value: 'insert_one', label: 'Insert One'},
                    {value: 'update_one', label: 'Update One'},
                    {value: 'update_many', label: 'Update Many'},
                ],
                dbConfigs: [{_id: '', name: ''}],
                HeaderOptions: [
                    {value: 'Accept', label: 'Accept'},
                    {value: 'Accept-Charset', label: 'Accept-Charset'},
                    {value: 'Accept-Encoding', label: 'Accept-Encoding'},
                    {value: 'Accept-Language', label: 'Accept-Language'},
                    {value: 'Accept-Ranges', label: 'Accept-Ranges'},
                    {value: 'Authorization', label: 'Authorization'},
                    {value: 'Cache-Control', label: 'Cache-Control'},
                    {value: 'Connection', label: 'Connection'},
                    {value: 'Cookie', label: 'Cookie'},
                    {value: 'Content-Length', label: 'Content-Length'},
                    {value: 'Content-Type', label: 'Content-Type'},
                    {value: 'Content-MD5', label: 'Content-MD5'},
                    {value: 'Date', label: 'Date'},
                    {value: 'Expect', label: 'Expect'},
                    {value: 'From', label: 'From'},
                    {value: 'Host', label: 'Host'},
                    {value: 'If-Match', label: 'If-Match'},
                    {value: 'If-Modified-Since', label: 'If-Modified-Since'},
                    {value: 'If-None-Match', label: 'If-None-Match'},
                    {value: 'If-Range', label: 'If-Range'},
                    {value: 'If-Unmodified-Since', label: 'If-Unmodified-Since'},
                    {value: 'Max-Forwards', label: 'Max-Forwards'},
                    {value: 'Origin', label: 'Origin'},
                    {value: 'Pragma', label: 'Pragma'},
                    {value: 'Proxy-Authorization', label: 'Proxy-Authorization'},
                    {value: 'Range', label: 'Range'},
                    {value: 'Referer', label: 'Referer'},
                    {value: 'TE', label: 'TE'},
                    {value: 'Upgrade', label: 'Upgrade'},
                    {value: 'User-Agent', label: 'User-Agent'},
                    {value: 'Via', label: 'Via'},
                    {value: 'Warning', label: 'Warning'}
                ],
                ResponseCodeOptions: [
                    {value: '200', label: '200'},
                    {value: '302', label: '302'},
                    {value: '400', label: '400'},
                    {value: '401', label: '401'},
                    {value: '403', label: '403'},
                    {value: '404', label: '404'},
                    {value: '500', label: '500'},
                    {value: '502', label: '502'},
                    {value: '504', label: '504'}
                ],
                operatorOptions: [
                    {value: '+', label: '加上'},
                    {value: '-', label: '减去'},
                    {value: '*', label: '乘以'},
                    {value: '/', label: '除以'}
                ],
                judgeCharacterOptions: [
                    {value: '<', label: '小于'},
                    {value: '<=', label: '小于等于'},
                    {value: '>', label: '大于'},
                    {value: '>=', label: '大于等于'},
                    {value: '==', label: '等于'}
                ],
                showRequestBody: true,
                radio: "raw",
                radioType: '',
                parameterType: 'raw',
                form: {
                    name: '',
                    service: '',
                    requestMethod: 'GET',
                    requestProtocol: '',
                    route: '',
                    domain: '',
                    description: '',
                    isClearCookie: false,
                    dataInitializes: [{
                        dbConfigId: '',
                        dbType: '',
                        mongoCrud: '',
                        collection: '',
                        query: '',
                        set: '',
                        sql: ''
                    }],
                    headers: [{name: "", value: ""}],
                    parameterType: "",
                    parameterRaw: "",
                    isJsonArray: false,
                    parameterForm: [{name: "", value: ""}, {name: "", value: ""}],
                    setGlobalVars: [{name: "", query: []}],
                    checkResponse: "noCheck",
                    checkResponseCode: "",
                    checkResponseBody: [{regex: "", query: []}],
                    checkResponseNumber: [{
                        expressions: {
                            'firstArg': '',
                            'operator': '',
                            'secondArg': '',
                            'judgeCharacter': '',
                            'expectResult': ''
                        }
                    }],
                },
                formRules: {
                    name: [
                        {required: true, message: '请输入名称', trigger: 'blur'},
                        {min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur'}
                    ],
                    requestProtocol: [
                        {required: false, message: '请选择协议', trigger: 'blur'},
                        {min: 4, max: 5, message: 'HTTP or HTTPS', trigger: 'blur'}
                    ],
                    requestMethod: [
                        {required: true, message: '请选择请求方法', trigger: 'blur'}
                    ],
                    route: [{required: true, message: '请输入接口路由', trigger: 'blur'},
                        {validator: checkRoute, trigger: 'blur'}],
                    service: [
                        {required: false, message: '请输入服务名', trigger: 'blur'}
                    ],
                    parameterRaw: [{required: false, message: '请输入名称', trigger: 'blur'},
                        {validator: checkJson, trigger: 'blur'}],
                    checkResponseBody: [{required: false, message: '请输入名称', trigger: 'blur'}]
                },
                showResponseCodeCheck: false,
                showResponseBodyCheck: false,
                showResponseNumCheck: false
            }
        },
        methods: {
            checkJsonFormat(json, err_msg) {
                if (json !== "" && json !== null) {
                    try {
                        let obj = JSON.parse(json)
                        if (typeof obj == 'object' && obj) {
                            return true
                        } else {
                            this.$message.warning({
                                message: err_msg,
                                center: true,
                            });
                            return false
                        }
                    } catch (e) {
                        console.log(json, e)
                        this.$message.warning({
                            message: err_msg,
                            center: true,
                        });
                        return false;
                    }
                }
                return true;
            },
            getDBConfigList() {
                let header = {};
                let params = {
                    "status": true
                };
                getDBConfigs(params, header).then((res) => {
                    let {status, data} = res;
                    if (status === 'ok') {
                        this.dbConfigs = data.rows
                    } else {
                        this.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                    this.$message.error({
                        message: 'DB配置列表获取失败，请稍后刷新重试哦~',
                        center: true,
                    });
                });
            },
            checkRequestMethod() {
                let request = this.form.requestMethod;
                if (request === "GET" || request === "DELETE") {
                    this.showRequestBody = false
                } else {
                    this.showRequestBody = true
                }
            },
            handleChange(val) {
            },
            addDataInit() {
                let dataInit = {
                    dbConfigId: '',
                    dbType: '',
                    mongoCrud: '',
                    collection: '',
                    query: '',
                    set: '',
                    sql: ''
                };
                this.form.dataInitializes.push(dataInit)
            },
            delDataInit(index) {
                this.form.dataInitializes.splice(index, 1);
                if (this.form.dataInitializes.length === 0) {
                    this.form.dataInitializes.push({
                        dbConfigId: '',
                        dbType: '',
                        mongoCrud: '',
                        collection: '',
                        query: '',
                        set: '',
                        sql: ''
                    })
                }
            },
            addHeader() {
                let header = {name: "", value: ""};
                this.form.headers.push(header)
            },
            delHeader(index) {
                this.form.headers.splice(index, 1);
                if (this.form.headers.length === 0) {
                    this.form.headers.push({name: "", value: ""})
                }
            },
            addSuffix(query) {
                const isValidQuery = query.constructor === Array && query.length > 0;
                if (isValidQuery) {
                    query.forEach((item, index) => {
                        const suffixStartIndex = item.search(/\([0-9]+\)/);
                        const expectedSuffix = '(' + (index + 1).toString() + ')';
                        if (suffixStartIndex === -1) {
                            query[index] = item + expectedSuffix;
                        } else {
                            query[index] = item.substring(0, suffixStartIndex) + expectedSuffix;
                        }
                    })
                }
                return query
            },
            addGlobalVars() {
                let globalVars = {name: "", query: []};
                this.form.setGlobalVars.push(globalVars)
            },
            delGlobalVars(index) {
                this.form.setGlobalVars.splice(index, 1);
                if (this.form.setGlobalVars.length === 0) {
                    this.form.setGlobalVars.push({name: "", query: []})
                }
            },
            addCheckResBody() {
                let checkResBody = {regex: "", query: []};
                this.form.checkResponseBody.push(checkResBody)
            },
            delCheckResBody(index) {
                this.form.checkResponseBody.splice(index, 1);
                if (this.form.checkResponseBody.length === 0) {
                    this.form.checkResponseBody.push({regex: "", query: []})
                }
            },
            addCheckResNum() {
                let checkResNumber = {
                    expressions: {
                        'firstArg': '',
                        'operator': '',
                        'secondArg': '',
                        'judgeCharacter': '',
                        'expectResult': ''
                    }
                };
                this.form.checkResponseNumber.push(checkResNumber)
            },
            delCheckResNum(index) {
                this.form.checkResponseNumber.splice(index, 1);
                if (this.form.checkResponseNumber.length === 0) {
                    this.form.checkResponseNumber.push({
                        expressions: {
                            'firstArg': '',
                            'operator': '',
                            'secondArg': '',
                            'judgeCharacter': '',
                            'expectResult': ''
                        }
                    });
                }
            },
            // 获取Case详细信息
            getCaseDetailInfo() {
                let self = this;
                getCaseDetail(self.$route.params.project_id, self.$route.params.test_suite_id, self.$route.params.test_case_id, {})
                    .then((res) => {
                        let {status, data} = res;
                        if (status === 'ok') {
                            self.form.name = data.name;
                            self.form.service = data.service;
                            self.form.requestMethod = data.requestMethod;
                            self.form.requestProtocol = data.requestProtocol;
                            self.form.route = data.route;
                            if (data.dataInitializes && data.dataInitializes.length > 0) {
                                data.dataInitializes.forEach(item => {
                                    item.set = JSON.stringify(item.set, undefined, 4);
                                    item.query = JSON.stringify(item.query, undefined, 4);
                                })
                                self.form.dataInitializes = data.dataInitializes;
                            }
                            self.form.headers = data.headers;
                            self.form.domain = data.domain;
                            self.form.isClearCookie = data.isClearCookie;
                            self.form.description = data.description;
                            self.form.isJsonArray = data.isJsonArray;
                            // 加后缀ww
                            data.setGlobalVars.forEach((setGlobalVar) => {
                                setGlobalVar.query = this.addSuffix(setGlobalVar.query)
                            });
                            self.form.setGlobalVars = data.setGlobalVars;
                            try {
                                self.form.parameterRaw = JSON.stringify(data.requestBody, undefined, 4);
                                self.form.parameterRaw = self.form.parameterRaw.replace(/'/g, "\"").replace(/None/g, "null").replace(/True/g, "true").replace(/False/g, "false");
                                if (self.form.parameterRaw === '{}') {
                                    self.form.parameterRaw = ''
                                }
                            } catch (e) {
                                self.$message.error({
                                    message: '获取请求参数出现异常！' + e,
                                    center: true,
                                });
                            }
                            self.form.checkResponseCode = data.checkResponseCode;
                            if (data.checkResponseCode != null) {
                                self.form.checkResponse = 'checkResponseCode';
                            }
                            if (data.checkResponseBody === null || data.checkResponseBody === undefined) {
                                self.form.checkResponseBody = [{regex: "", query: []}]
                            } else {
                                self.form.checkResponse = 'checkResponseBody';
                                // 加后缀
                                data.checkResponseBody.forEach((data) => {
                                    data.query = this.addSuffix(data.query);
                                });
                                self.form.checkResponseBody = data.checkResponseBody;
                            }
                            if (data.checkResponseNumber === null || data.checkResponseNumber === undefined) {
                                self.form.checkResponseNumber = [{
                                    expressions: {
                                        'firstArg': '',
                                        'operator': '',
                                        'secondArg': '',
                                        'judgeCharacter': '',
                                        'expectResult': ''
                                    }
                                }]
                            } else {
                                self.form.checkResponseNumber = data.checkResponseNumber
                            }
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            });
                        }
                    })
                    .catch((error) => {
                        self.$message.error({
                            message: '接口用例详情获取失败，请稍后刷新重试哦~',
                            center: true,
                        });
                        self.listLoading = false;
                    })
            },
            // 更新Case信息
            updateCaseInfo() {
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        let self = this;
                        let flag = true;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            // if (!self.form.domain && !this.form.service) {
                            //     self.$message.error({
                            //         message: "由于没有输入domain，请输入service",
                            //         center: true,
                            //     });
                            //     return
                            // }
                            if (self.form.domain && !this.form.requestProtocol || !self.form.domain && this.form.requestProtocol) {
                                self.$message.error({
                                    message: "domain 和 requestProtocol 立誓同生共死！",
                                    center: true,
                                });
                                return
                            }
                            // 删除后缀
                            self.form.setGlobalVars.forEach((setGlobalVar) => {
                                setGlobalVar.query.forEach((query, index) => {
                                    setGlobalVar.query[index] = query.replace(/\([0-9]+\)/, "");
                                })
                            });
                            self.form.checkResponseBody.forEach((checkRegex) => {
                                checkRegex.query.forEach((query, index) => {
                                    checkRegex.query[index] = query.replace(/\([0-9]+\)/, "");
                                })
                            });
                            let params = {
                                name: self.form.name.trim(),
                                service: self.form.service,
                                requestMethod: self.form.requestMethod,
                                requestProtocol: self.form.requestProtocol,
                                route: self.form.route,
                                domain: self.form.domain,
                                description: self.form.description.trim(),
                                headers: self.form.headers,
                                isClearCookie: self.form.isClearCookie,
                                isJsonArray: self.form.isJsonArray,
                                setGlobalVars: self.form.setGlobalVars,
                                checkResponseBody: self.form.checkResponseBody,
                                checkResponseNumber: self.form.checkResponseNumber,
                                requestBody: self.form.parameterRaw,
                                lastUpdateUser: self.$store.getters.email || 'anonymous'
                            };
                            // check dataInitializes
                            if (self.form.dataInitializes && self.form.dataInitializes.length > 0) {
                                self.form.dataInitializes.forEach((item, index) => {
                                        if (item.dbType) {
                                            if (item.dbType == "MongoDB") {
                                                if (item.mongoCrud && item.collection && item.set) {
                                                    if (!this.checkJsonFormat(item.set, "MongoDB 参数:set 格式不正确")) {
                                                        flag = false;
                                                    }
                                                    if (item.query && !this.checkJsonFormat(item.query, "MongoDB 参数:query 格式不正确")) {
                                                        flag = false;
                                                    }
                                                    item.set = JSON.parse(item.set);
                                                    item.query = JSON.parse(item.query);
                                                }
                                            } else {
                                                if (!item.query) {
                                                    this.$message.warning({
                                                        message: 'SQL不正确!',
                                                        center: true,
                                                    });
                                                    flag = false;
                                                }
                                            }
                                        }
                                    }
                                )
                                params["dataInitializes"] = self.form.dataInitializes;
                            }
                            if (self.form.checkResponseCode) {
                                params["checkResponseCode"] = self.form.checkResponseCode
                            } else {
                                params["checkResponseCode"] = null
                            }
                            if (flag) {
                                let header = {};
                                updateTestCase(self.$route.params.project_id, self.$route.params.test_suite_id, self.$route.params.test_case_id,
                                    params, header).then((res) => {
                                    let {status, data} = res;
                                    if (status === 'ok') {
                                        self.$router.push({
                                            name: 'TestCaseList', params: {
                                                project_id: self.$route.params.project_id,
                                                test_suite_id: self.$route.params.test_suite_id,
                                            }
                                        });
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
                            } else {
                                return
                            }
                        })
                    }
                })
            },
        },
        watch: {
            form: {
                //注意：当观察的数据为对象或数组时，curVal和oldVal是相等的，因为这两个形参指向的是同一个数据对象
                handler(curVal, oldVal) {
                    if (curVal.checkResponse === 'noCheck') {
                        this.showResponseCodeCheck = false
                        this.showResponseBodyCheck = false
                        this.showResponseNumCheck = false
                    } else if (curVal.checkResponse === 'checkResponseCode') {
                        this.showResponseCodeCheck = true
                        this.showResponseBodyCheck = false
                        this.showResponseNumCheck = false
                    } else if (curVal.checkResponse === 'checkResponseBody') {
                        this.showResponseCodeCheck = false
                        this.showResponseBodyCheck = true
                        this.showResponseNumCheck = false
                    } else if (curVal.checkResponse === 'checkResponseNumber') {
                        this.showResponseCodeCheck = false
                        this.showResponseBodyCheck = false
                        this.showResponseNumCheck = true
                    }
                },
                deep: true
            },
        },
        created() {
            this.getDBConfigList();
            this.getCaseDetailInfo();
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
    /*margin-left: 7px;*/
    padding-left: 9px;
    width: 180px;
    /*border-radius:0px;*/
    /*height: 38px;*/
    left: 1px;
    border-right: 0px;

    input {
      border-right: 0px;
      border-radius: 4px 0px 0px 4px;
    }
  }
</style>
