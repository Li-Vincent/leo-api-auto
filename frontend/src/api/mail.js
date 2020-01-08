import request from '../utils/axios'

export function getMails(project_id, params) {
  return request({
    url: `/api/project/${project_id}/mailList`,
    params: params,
    method: 'GET'
  })
}

export function addMail(project_id, params, headers) {
  return request({
    url: `/api/project/${project_id}/addMail`,
    method: 'POST',
    headers: headers,
    data: params
  })
}

export function updateMail(project_id, mail_id, params, headers) {
  return request({
    url: `/api/project/${project_id}/updateMail/${mail_id}`,
    method: 'POST',
    headers: headers,
    data: params
  })
}
