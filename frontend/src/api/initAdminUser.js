import request from '@/utils/axios.js'

export function checkAdminUserExist() {
  return request({
    url: '/api/checkAdminUserExist',
    method: 'POST',
  })
}

export function addAdminUser(params) {
  return request({
    url: '/api/addAdminUser',
    method: 'POST',
    data: params
  })
}
