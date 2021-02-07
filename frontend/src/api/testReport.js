import request from '../utils/axios'

export function getTestReports(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testReportList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}


export function getReportInfo(project_id, report_id) {
  return request({
    url: `/api/project/${project_id}/testReport/${report_id}`,
    method: 'GET'
  })
}

export function getTestCaseReports(report_id, suite_id, params) {
  return request({
    url: `/api/testReport/${report_id}/testSuite/${suite_id}`,
    method: 'GET',
    params: params
  })
}

export function cleanProjectReports(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testReport/cleanReports`,
    headers: header,
    method: 'POST',
    data: params
  })
}
