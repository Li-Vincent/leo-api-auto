import router from './router'
import store from './store'
import {Message} from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style
import {getToken} from './utils/auth'
import {checkAdminUserExist} from "./api/initAdminUser";

NProgress.configure({showSpinner: false}) // NProgress Configuration

const whiteList = ['/login', '/404'] // no redirect whitelist

const title = 'Leo API Auto Test'

function getPageTitle(pageTitle) {
  if (pageTitle) {
    return `${pageTitle} - ${title}`
  }
  return `${title}`
}

// combine routes
function combineRoutes(combinedRoutes, routes) {
  routes.forEach(route => {
    const tmp = {...route}
    combinedRoutes.push(tmp)
    if (tmp.children) {
      combineRoutes(combinedRoutes, tmp.children)
    }
  })
  return combinedRoutes
}


function filterExistedRoutes(toName, routes) {
  let existed = false
  const combinedRoutes = []
  combineRoutes(combinedRoutes, routes).some(route => {
    const tmp = {...route}
    if (toName && toName == tmp.name) {
      existed = true
      return true
    }
  })
  return existed
}


router.beforeEach(async (to, from, next) => {
  // start progress bar
  NProgress.start()

  // set page title
  document.title = getPageTitle(to.meta.title)

  if (to.meta.firstAccess) {
    checkAdminUserExist().then((res) => {
      if (res.status) {
        Message({
          message: "管理员账号已存在：" + res.data,
          center: true,
        })
        next({path: '/login'})
      } else {
        if (res.data) {
          Message.error({
            message: res.data,
            center: true,
          });
        } else {
          next()
        }
      }
    })
  } else {

    // determine whether the user has logged in
    const hasToken = getToken()

    if (hasToken) {
      if (to.path === '/login') {
        // if is logged in, redirect to the home page
        next({path: '/'})
        NProgress.done()
      } else {
        // determine whether the user has obtained his permission roles through getInfo
        const hasRoles = store.getters.roles && store.getters.roles.length > 0
        if (hasRoles) {
          next()
        } else {
          try {
            // get user info
            // note: roles must be a object array! such as: ['admin'] or ,['developer','editor']
            const {roles} = await store.dispatch('user/getUserInfo')

            // generate accessible routes map based on roles
            const accessRoutes = await store.dispatch('permission/generateRoutes', roles)

            // dynamically add accessible routes
            // router.options.routes = store.getters.routes
            // router.addRoutes(accessRoutes)

            // hack method to ensure that addRoutes is complete
            // set the replace: true, so the navigation will not leave a history record
            // next({...to, replace: true})
            next()
          } catch (error) {
            // remove token and go to login page to re-login
            await store.dispatch('user/resetToken')
            Message.error(error || 'Has Error')
            next(`/login?redirect=${to.path}`)
            NProgress.done()
          }
        }
      }
    } else {
      /* has no token*/
      if (whiteList.indexOf(to.path) !== -1) {
        // in the free login whitelist, go directly
        next()
      } else {
        // other pages that do not have permission to access are redirected to the login page.
        next(`/login?redirect=${to.path}`)
        NProgress.done()
      }
    }
  }
})

router.afterEach(() => {
  // finish progress bar
  NProgress.done()
})
