import request from '../utils/axios'

export function getTestEnvs(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testEnvList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getTestEnvInfo(project_id, test_env_id) {
  return request({
    url: `/api/project/${project_id}/testEnv/${test_env_id}`,
    method: 'GET'
  })
}

export function addTestEnv(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addTestEnv`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateTestEnv(project_id, test_env_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateTestEnv/${test_env_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}
