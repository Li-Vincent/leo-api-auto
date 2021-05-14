import request from '../utils/axios'

export function getTestCases(project_id, test_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}/testCaseList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getCaseLastResult(test_case_id) {
  return request({
    url: `/api/testCaseLastManualResult/${test_case_id}`,
    method: 'GET',
  })
}

export function addTestCase(project_id, test_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}/addCase`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function copyTestCase(project_id, test_suite_id, test_case_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}/copyCase/${test_case_id}`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateTestCase(project_id, test_suite_id, test_case_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}/updateCase/${test_case_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function getCaseDetail(project_id, test_suite_id, test_case_id, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}/testCase/${test_case_id}`,
    method: 'GET',
    headers: header,
    params: null
  })
}

export function exportTestCases(params, header) {
  return request({
    url: `/api/exportTestCases`,
    method: 'POST',
    headers: header,
    responseType: 'blob',
    data: params
  })
}




