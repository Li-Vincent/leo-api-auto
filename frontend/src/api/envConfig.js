import request from '../utils/axios'

export function getEnvConfigs(params, header) {
  return request({
    url: `/api/envConfig/envConfigList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getEnvConfigInfo(test_env_id) {
  return request({
    url: `/api/envConfig/${test_env_id}`,
    method: 'GET'
  })
}

export function addEnvConfig(params, header) {
  return request({
    url: `/api/envConfig/addEnvConfig`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateEnvConfig(test_env_id, params, header) {
  return request({
    url: `/api/envConfig/updateEnvConfig/${test_env_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}
