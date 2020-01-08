import request from '../utils/axios'

export function getCronJobs(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/cronJobList`,
    method: 'GET',
    headers: header,
    params: params
  })
}

export function addCronJob(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addCronJob`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function updateCronJob(project_id, cron_job_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateCronJob/${cron_job_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function pauseCronJob(project_id, cron_job_id, params, header) {
  return request({
    url: `/api/project/${project_id}/pauseCronJob/${cron_job_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function deleteCronJob(project_id, cron_job_id, params, header) {
  return request({
    url: `/api/project/${project_id}/deleteCronJob/${cron_job_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function resumeCronJob(project_id, cron_job_id, params, header) {
  return request({
    url: `/api/project/${project_id}/resumeCronJob/${cron_job_id}`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function startScheduler(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/cronJob/start`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function shutdownScheduler(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/cronJob/shutdown`,
    method: 'POST',
    headers: header,
    data: params
  })
}




