import request from '../utils/axios'

export function getMockAPIs(params, header) {
  return request({
    url: `/api/mock/mockAPIList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getMockAPI(mock_api_id) {
  return request({
    url: `/api/mock/mockAPI/${mock_api_id}`,
    method: 'GET'
  })
}

export function addMockAPI(params, header) {
  return request({
    url: `/api/mock/addMockAPI`,
    headers: header,
    data: params,
    method: 'POST'
  })
}

export function updateMockAPI(mock_api_id, params, header) {
  return request({
    url: `/api/mock/updateMockAPI/${mock_api_id}`,
    headers: header,
    data: params,
    method: 'POST'
  })
}
