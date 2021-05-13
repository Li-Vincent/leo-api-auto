import request from '@/utils/axios.js'

export function register(params, header) {
  return request({
    url: '/api/register',
    headers: header,
    method: 'POST',
    data: params
  })
}

export function login(params) {
  return request({
    url: '/api/login',
    method: 'POST',
    data: params
  })
}

export function logout() {
  return request({
    url: '/api/logout',
    method: 'POST'
  })
}


export function getUserRoles(email) {
  return request({
    url: `/api/user/${email}/role`,
    method: 'GET'
  })
}


export function getUserList(params) {
  return request({
    url: `/api/user/users`,
    method: 'GET',
    params: params
  })
}


export function getRoleList() {
  return request({
    url: `/api/user/roles`,
    method: 'GET'
  })
}


export function updateUserStatus(params, header) {
  return request({
    url: `/api/user/updateStatus`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function changeUserProjects(email, params, header) {
  return request({
    url: `/api/user/${email}/changeProjects`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function changePassword(params, header) {
  return request({
    url: `/api/user/changePassword`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function changeRoles(email, params, header) {
  return request({
    url: `/api/user/${email}/changeRoles`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function resetPassword(email, params, header) {
  return request({
    url: `/api/user/${email}/resetPassword`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function deleteUser(params, header) {
  return request({
    url: `/api/user/deleteUsers`,
    headers: header,
    method: 'POST',
    data: params
  })
}
