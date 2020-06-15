import request from '../utils/axios'

//  Not yet used

export function getTestSuiteParams(project_id, test_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}/paramList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addTestSuiteParam(project_id, test_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/${test_suite_id}/addParam`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateTestSuiteParam(project_id, test_suite_param_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testSuite/updateParam/${test_suite_param_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}
