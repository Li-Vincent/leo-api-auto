import request from '../utils/axios'

export function getPlans(params, header) {
  return request({
    url: `/api/plan/planList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getPlanInfo(plan_id) {
  return request({
    url: `/api/plan/${plan_id}`,
    method: 'GET'
  })
}

export function addPlan(params, header) {
  return request({
    url: `/api/plan/addPlan`,
    headers: header,
    data: params,
    method: 'POST'
  })
}

export function updatePlan(plan_id, params, header) {
  return request({
    url: `/api/plan/${plan_id}/updatePlan`,
    headers: header,
    data: params,
    method: 'POST'
  })
}

export function executePlan(plan_id, params, header) {
  return request({
    url: `/api/plan/${plan_id}/executePlanByManual`,
    headers: header,
    data: params,
    method: 'POST'
  })
}
