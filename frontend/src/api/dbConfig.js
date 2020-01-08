import request from '../utils/axios'

export function getDBConfigs(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/dbConfigList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getDBConfig(project_id, db_config_id) {
  return request({
    url: `/api/project/${project_id}/dbConfig/${db_config_id}`,
    method: 'GET'
  })
}

export function addDBConfig(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addDBConfig`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateDBConfig(project_id, db_config_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateDBConfig/${db_config_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function getDBEnvConnect(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/getDBEnvConnect`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function updateDBEnvConnect(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateDBEnvConnect`,
    method: 'POST',
    headers: header,
    data: params
  })
}
