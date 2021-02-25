webpackJsonp([17],{"5ADG":function(t,e,o){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var a=o("XLwt"),s=o.n(a),l=(o("PJh5"),o("x5Vx")),r={name:"PlanReportDetail",data:function(){return{activeName:1,planReport:{testEnv:"",planName:"",executionUser:"",planId:"",testStartTime:"",totalCount:0,passCount:0,failCount:0,errorCount:0,spendTimeInSec:0,createAt:""},projectReports:[],reportChart:null}},methods:{getReport:function(){var t=this;Object(l.d)(this.$route.params.plan_report_id).then(function(e){"ok"===e.status&&(t.planReport=e.data,Object(l.c)(t.$route.params.plan_report_id).then(function(e){"ok"==e.status&&e.data.rows.forEach(function(e){t.projectReports.push(e)})}))})},getPassRate:function(t,e,o){return t=parseFloat(t),e=parseFloat(e),isNaN(t)||isNaN(e)?"-":o?e<=0?"0%":Math.round(t/e*1e4)/100+"%":e<=0?0:Math.round(t/e*1e4)/100},setChartOptions:function(t,e,o){this.reportChart.setOption({title:{text:"通过率统计"},legend:{data:["Pass","Fail","Error"]},series:[{type:"pie",radius:"55%",center:["50%","50%"],data:[{value:t,name:"Pass",itemStyle:{color:"#54ac21"}},{value:e,name:"Fail",itemStyle:{color:"#d6443f"}},{value:o,name:"Error",itemStyle:{color:"#e0aa1c"}}]}]})}},mounted:function(){this.reportChart=s.a.init(document.getElementById("report-chart")),this.setChartOptions(this.planReport.passCount,this.planReport.failCount,this.planReport.errorCount)},watch:{planReport:{handler:function(t,e){this.setChartOptions(t.passCount,t.failCount,t.errorCount)},deep:!0}},beforeDestroy:function(){this.reportChart&&(this.reportChart.dispose(),this.reportChart=null)},created:function(){this.getReport()}},n={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("section",{staticClass:"report"},[a("el-row",[a("el-col",{staticClass:"title",attrs:{span:24}},[a("span",[t._v(t._s(t.$route.meta.title)+" ")]),t._v(" "),a("span",{staticClass:"report-id"},[t._v(" - Report ID: "+t._s(t.$route.params.plan_report_id))])])],1),t._v(" "),a("el-row",{staticClass:"report-basic"},[a("el-col",{attrs:{span:10}},[a("el-col",{staticStyle:{width:"160px"}},[a("span",{staticStyle:{"text-align":"left","font-size":"18px","font-weight":"bold"}},[t._v("测试计划基本信息")])]),t._v(" "),a("table",{staticStyle:{"margin-right":"30px",width:"70%",height:"12px"}},[a("tbody",[a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("计划名称")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.planName))])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("测试环境")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.testEnvName))])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("开始时间")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.testStartTime))])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("测试用时")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.spendTimeInSec)+" s")])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("总用例数")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.totalCount))])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("通过数")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.passCount))])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("失败数")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.failCount))])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("错误数")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.planReport.errorCount))])]),t._v(" "),a("tr",{staticClass:"info"},[a("td",{staticClass:"label"},[t._v("通过率")]),t._v(" "),a("td",{staticClass:"text-center"},[t._v(t._s(t.getPassRate(t.planReport.passCount,t.planReport.totalCount,!0)))])])])])],1),t._v(" "),a("el-col",{attrs:{span:10}},[a("div",{staticStyle:{height:"230px",width:"100%"},attrs:{id:"report-chart"}})])],1),t._v(" "),a("el-row",[a("el-table",{staticStyle:{width:"100%"},attrs:{data:t.projectReports,"highlight-current-row":""}},[a("el-table-column",{attrs:{prop:"projectName",label:"项目名","min-width":"10%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"testStartTime",label:"开始时间","min-width":"10%",sortable:"custom","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"spendTimeInSec",label:"用时(秒)","min-width":"10%",sortable:"custom","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"totalCount",label:"总数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"passCount",label:"通过数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"failCount",label:"失败数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"errorCount",label:"错误数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"passRate",label:"通过率","min-width":"10%","show-overflow-tooltip":""},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v("\n          "+t._s(t.getPassRate(e.row.passCount,e.row.totalCount,!0))+"\n        ")]}}])}),t._v(" "),a("el-table-column",{attrs:{prop:"status",label:"测试结果","min-width":"10%"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("img",{directives:[{name:"show",rawName:"v-show",value:e.row.totalCount==e.row.passCount,expression:"scope.row.totalCount==scope.row.passCount"}],attrs:{src:o("7shL")}}),t._v(" "),a("img",{directives:[{name:"show",rawName:"v-show",value:e.row.totalCount>e.row.passCount,expression:"scope.row.totalCount>scope.row.passCount"}],attrs:{src:o("IT+J")}})]}}])}),t._v(" "),a("el-table-column",{attrs:{label:"操作","min-width":"10%"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("router-link",{staticStyle:{"text-decoration":"none",color:"#000000"},attrs:{to:{name:"PlanProjectReport",params:{report_id:t.$route.params.report_id,project_id:e.row.projectId}}}},[a("el-button",{attrs:{type:"primary",size:"small"}},[t._v("查看项目报告")])],1)]}}])}),t._v(" "),a("el-table-column",{attrs:{type:"expand"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("el-table",{staticStyle:{width:"100%"},attrs:{data:Object.values(e.row.testSuites),"highlight-current-row":""}},[a("el-table-column",{attrs:{label:"序号",prop:"",width:"50",align:"center"},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v("\n                "+t._s(e.$index+1)+"\n              ")]}}],null,!0)}),t._v(" "),a("el-table-column",{attrs:{prop:"suiteName",label:"用例组名","min-width":"15%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"testStartTime",label:"开始时间","min-width":"10%",sortable:"custom","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"spendTimeInSec",label:"用时(秒)","min-width":"10%",sortable:"custom","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"totalCount",label:"总数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"passCount",label:"通过数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"failCount",label:"失败数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"errorCount",label:"错误数","min-width":"8%","show-overflow-tooltip":""}}),t._v(" "),a("el-table-column",{attrs:{prop:"passRate",label:"通过率","min-width":"10%","show-overflow-tooltip":""},scopedSlots:t._u([{key:"default",fn:function(e){return[t._v("\n                "+t._s(t.getPassRate(e.row.passCount,e.row.totalCount,!0))+"\n              ")]}}],null,!0)}),t._v(" "),a("el-table-column",{attrs:{prop:"status",label:"测试结果","min-width":"10%"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("img",{directives:[{name:"show",rawName:"v-show",value:e.row.totalCount==e.row.passCount,expression:"scope.row.totalCount==scope.row.passCount"}],attrs:{src:o("7shL")}}),t._v(" "),a("img",{directives:[{name:"show",rawName:"v-show",value:e.row.totalCount>e.row.passCount,expression:"scope.row.totalCount>scope.row.passCount"}],attrs:{src:o("IT+J")}})]}}],null,!0)})],1)]}}])})],1)],1)],1)},staticRenderFns:[]};var i=o("VU/8")(r,n,!1,function(t){o("gzw7")},"data-v-8b3b2560",null);e.default=i.exports},gzw7:function(t,e){}});
//# sourceMappingURL=17.1f460e38b624162aed9e.js.map