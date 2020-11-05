const getters = {
  token: state => state.user.token,
  email: state => state.user.email,
  roles: state => state.user.roles,
  routes: state => state.permission.routes,
  dynamicRoutes: state => state.permission.dynamicRoutes,
  testCasePageInfo: state => state.pageInfo.testCasePageInfo,
  testSuitePageInfo: state => state.pageInfo.testSuitePageInfo
}
export default getters
