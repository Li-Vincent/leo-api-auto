import request from '../utils/axios'

export function getTestEnvParams(project_id, test_env_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testEnv/${test_env_id}/paramList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addTestEnvParam(project_id, test_env_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testEnv/${test_env_id}/addParam`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateTestEnvParam(project_id, test_env_param_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testEnv/updateParam/${test_env_param_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}
