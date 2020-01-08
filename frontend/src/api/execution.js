import request from '../utils/axios'

export function startAPITestByCase(params, headers) {
  return request({
    url: `/api/startAPITestByCase`,
    method: 'POST',
    headers: headers,
    data: params
  })
}

export function startAPITestBySuite(params, headers) {
  return request({
    url: `/api/startAPITestBySuite`,
    method: 'POST',
    headers: headers,
    data: params
  })
}
