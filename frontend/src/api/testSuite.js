import request from '../utils/axios'

export function getTestSuites(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuiteList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getTestSuiteInfo(project_id, test_suite_id) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}`,
    method: 'GET'
  })
}

export function addTestSuite(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addTestSuite`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateTestSuite(project_id, test_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateTestSuite/${test_suite_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}


export function copyTestSuite(project_id, test_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/copyTestSuite/${test_suite_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}
