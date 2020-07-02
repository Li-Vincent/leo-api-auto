import request from '../utils/axios'

export function getMails(params) {
  return request({
    url: `/api/mailConfig/mailList`,
    params: params,
    method: 'GET'
  })
}

export function addMail(params, headers) {
  return request({
    url: `/api/mailConfig/addMail`,
    method: 'POST',
    headers: headers,
    data: params
  })
}

export function updateMail(mail_id, params, headers) {
  return request({
    url: `/api/mailConfig/updateMail/${mail_id}`,
    method: 'POST',
    headers: headers,
    data: params
  })
}

export function getMailGroups(params) {
  return request({
    url: `/api/mailConfig/mailGroupList`,
    params: params,
    method: 'GET'
  })
}

export function addMailGroup(params, headers) {
  return request({
    url: `/api/mailConfig/addMailGroup`,
    method: 'POST',
    headers: headers,
    data: params
  })
}

export function updateMailGroup(mail_group_id, params, headers) {
  return request({
    url: `/api/mailConfig/updateMailGroup/${mail_group_id}`,
    method: 'POST',
    headers: headers,
    data: params
  })
}
