import request from '../utils/axios'

export function getPlanReportInfo(plan_report_id) {
  return request({
    url: `/api/plan/planReport/${plan_report_id}`,
    method: 'GET'
  })
}

export function getPlanReportDetail(plan_report_id) {
  return request({
    url: `/api/plan/planReport/${plan_report_id}/detail`,
    method: 'GET'
  })
}

export function getPlanProjectReport(plan_report_id, project_id) {
  return request({
    url: `/api/plan/planReport/${plan_report_id}/project/${project_id}`,
    method: 'GET'
  })
}

export function getPlanReports(plan_id, params, header) {
  return request({
    url: `/api/plan/${plan_id}/planReportList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function cleanPlanReports(plan_id, params, header) {
  return request({
    url: `/api/plan/${plan_id}/cleanPlanReports`,
    headers: header,
    method: 'POST',
    data: params
  })
}
