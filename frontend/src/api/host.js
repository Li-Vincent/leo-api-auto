import request from '../utils/axios'

// 已弃用
export function getHosts(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/hostList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addHost(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addHost`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateHost(project_id, host_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateHost/${host_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}
