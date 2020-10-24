const state = {
  initTestCasePageInfo: {
    size: 10,
    skip: 0,
    sortBy: 'sequence',
    order: 'ascending',
    currentPage: 1
  },
  initTestSuitePageInfo: {
    size: 10,
    skip: 0,
    sortBy: 'createAt',
    order: 'descending',
    currentPage: 1
  },
  testCasePageInfo: [],
  testSuitePageInfo: []
}

const mutations = {
  SET_CASE_PAGE_INFO: (state, info) => {
    let testCasePageInfoIndex = state.testCasePageInfo.findIndex(ele => ele.testSuiteId === info.testSuiteId)
    testCasePageInfoIndex === -1 ?
      state.testCasePageInfo.push(Object.assign({}, state.initTestCasePageInfo, info)) :
      state.testCasePageInfo[testCasePageInfoIndex] =
        Object.assign({}, state.testCasePageInfo[testCasePageInfoIndex], info)
  },
  SET_SUITE_PAGE_INFO: (state, info) => {
    let testSuitePageInfoIndex = state.testSuitePageInfo.findIndex(ele => ele.projectId === info.projectId)
    testSuitePageInfoIndex === -1 ?
      state.testSuitePageInfo.push(Object.assign({}, state.initTestSuitePageInfo, info)) :
      state.testSuitePageInfo[testSuitePageInfoIndex] =
        Object.assign({}, state.testSuitePageInfo[testSuitePageInfoIndex], info)
  }
}

const actions = {
  setTestCasePageInfo({commit}, info) {
    return new Promise(resolve => {
      commit('SET_CASE_PAGE_INFO', info)
      resolve()
    })
  },
  setTestSuitePageInfo({commit}, info) {
    return new Promise(resolve => {
      commit('SET_SUITE_PAGE_INFO', info)
      resolve()
    })
  },

}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
