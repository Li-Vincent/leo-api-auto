import request from '../utils/axios'


export function getSuiteTempParams(test_suite_id) {
    return request({
        url: `/api/getTestSuiteTempParams/${test_suite_id}`,
        method: 'GET'
    })
}