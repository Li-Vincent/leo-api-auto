import request from '../utils/axios'

export function getDBConfigs(params, header) {
  return request({
    url: `/api/dbConfig/dbConfigList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getDBConfig(db_config_id) {
  return request({
    url: `/api/dbConfig/${db_config_id}`,
    method: 'GET'
  })
}

export function addDBConfig(params, header) {
  return request({
    url: `/api/dbConfig/addDBConfig`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateDBConfig(db_config_id, params, header) {
  return request({
    url: `/api/dbConfig/updateDBConfig/${db_config_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function getDBEnvConnect(params, header) {
  return request({
    url: `/api/dbConfig/getDBEnvConnect`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function updateDBEnvConnect(params, header) {
  return request({
    url: `/api/dbConfig/updateDBEnvConnect`,
    method: 'POST',
    headers: header,
    data: params
  })
}
