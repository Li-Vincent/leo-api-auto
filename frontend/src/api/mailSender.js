import request from '../utils/axios'

export function getMailSender(params) {
  return request({
    url: `/api/mailConfig/mailSenderList`,
    params: params,
    method: 'GET'
  })
}

export function addMailSender(params, header) {
  return request({
    url: `/api/mailConfig/addMailSender`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function updateMailSender(sender_id, params, header) {
  return request({
    url: `/api/mailConfig/updateMailSender/${sender_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function mailSenderTest(params) {
  return request({
    url: `/api/mailConfig/mailSenderTest`,
    method: 'POST',
    data: params
  })
}


