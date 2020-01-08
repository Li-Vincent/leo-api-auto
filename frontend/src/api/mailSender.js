import request from '../utils/axios'

export function getMailSender(project_id, params) {
  return request({
    url: `/api/project/${project_id}/mailSenderList`,
    params: params,
    method: 'GET'
  })
}

export function addMailSender(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addMailSender`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function updateMailSender(project_id, sender_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateMailSender/${sender_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function mailSenderTest(project_id, params) {
  return request({
    url: `/api/project/${project_id}/mailSenderTest`,
    method: 'POST',
    data: params
  })
}


