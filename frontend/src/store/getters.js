const getters = {
  token: state => state.user.token,
  email: state => state.user.email,
  roles: state => state.user.roles,
  routes: state => state.permission.routes,
  dynamicRoutes: state => state.permission.dynamicRoutes,
}
export default getters
