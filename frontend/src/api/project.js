import request from '../utils/axios'

export function getProjects(params, header) {
  return request({
    url: `/api/project/projectList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getProjectInfo(project_id) {
  return request({
    url: `/api/project/${project_id}`,
    method: 'GET'
  })
}

export function addProject(params, header) {
  return request({
    url: `/api/project/addProject`,
    headers: header,
    data: params,
    method: 'POST'
  })
}

export function updateProject(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateProject`,
    headers: header,
    data: params,
    method: 'POST'
  })
}
