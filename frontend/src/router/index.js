import Vue from 'vue'
import Router from 'vue-router'

// fix NavigationDuplicated error
const originalPush = Router.prototype.push
Router.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err)
}

Vue.use(Router)

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar
    noCache: true                if set true, the page will no be cached(default is false)
    affix: true                  if set true, the tag will affix in the tags-view
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/components/user/Login'),
    hidden: true
  },
  {
    path: '/initAdminUser',
    name: 'InitAdminUser',
    component: () => import('@/components/user/InitAdminUser'),
    hidden: true,
    meta: {
      title: 'InitAdminUser',
      firstAccess: true
    }
  },
  {
    path: '/404',
    name: 'notFound',
    component: () => import('@/components/NotFound'),
    hidden: true
  },
  {
    path: '/project/:project_id',
    name: 'Project',
    component: () => import('@/components/project/Project'),
    hidden: true,
    projectMenu: true,
    children: [
      {
        path: '/project/:project_id/autoTest',
        component: () => import('@/components/project/autoTest/AutoTest'),
        redirect: '/project/:project_id/autoTest/testSuites',
        name: 'AutoTest',
        nav: 'autoTest',
        meta: {
          title: '自动化测试'
        },
        leaf: true,  // 只显示一级导航
        child: true,
        children: [
          {
            path: '/project/:project_id/autoTest/testSuites',
            component: () => import('@/components/project/autoTest/TestSuiteList'),
            name: 'TestSuiteList',
            nav: 'autoTest',
            meta: {
              title: '用例组列表'
            }
          },
          {
            path: '/project/:project_id/autoTest/testSuite/:test_suite_id/testCases',
            component: () => import('@/components/project/autoTest/TestCaseList'),
            name: 'TestCaseList',
            nav: 'autoTest',
            meta: {
              title: '接口用例列表'
            }
          },
          {
            path: '/project/:project_id/autoTest/testSuite/:test_suite_id/testCase/:test_case_id/edit',
            component: () => import('@/components/project/autoTest/EditTestCase'),
            name: 'EditTestCase',
            nav: 'autoTest',
            meta: {
              title: '编辑用例'
            },
          }
        ]
      },
      {
        path: '/project/:project_id/globalParam',
        component: () => import('@/components/project/setting/GlobalParam'),
        name: 'GlobalParam',
        leaf: true,   // 只显示一级导航
        child: true,
        nav: 'env',
        meta: {
          title: '全局参数配置'
        },
        children: [
          {
            path: '/project/:project_id/globalParam/testEnv/',
            component: () => import('@/components/project/setting/TestEnv'),
            name: 'TestEnv',
            nav: 'env',
            meta: {
              title: '环境配置'
            }
          },
          {
            path: '/project/:project_id/globalParam/testEnv/:test_env_id/envParams',
            component: () => import('@/components/project/setting/TestEnvParam'),
            name: 'TestEnvParam',
            nav: 'env',
            meta: {
              title: '参数配置'
            }
          },
          {
            path: '/project/:project_id/globalParam/ShowDBConfig',
            component: () => import('@/components/project/setting/dbConfig/ShowDBConfig'),
            name: 'ShowDBConfig',
            nav: 'env',
            meta: {
              title: 'DB配置'
            }
          },
          {
            path: '/project/:project_id/globalParam/DBConfig/:db_config_id/ShowDBEnvConnect',
            component: () => import('@/components/project/setting/dbConfig/ShowDBEnvConnect'),
            name: 'ShowDBEnvConnect',
            nav: 'env',
            meta: {
              title: 'DB环境连接配置'
            }
          }
        ]
      },
      {
        path: '/project/:project_id/cronJob',
        component: () => import('@/components/project/cronJob/CronJobList'),
        name: 'CronJobList',
        nav: 'cron',
        meta: {
          title: '定时任务'
        },
        leaf: true  // 只显示一级导航
      },
      {
        path: '/project/:project_id/testReport',
        component: () => import('@/components/project/report/TestReport'),
        name: 'TestReport',
        child: true,
        nav: 'report',
        meta: {
          title: '测试报告'
        },
        children: [
          {
            path: '/project/:project_id/testReports/manual',
            component: () => import('@/components/project/report/TestReportManual'),
            name: 'TestReportManual',
            nav: 'report',
            meta: {
              title: '手动报告'
            },
          },
          {
            path: '/project/:project_id/testReports/cronJob',
            component: () => import('@/components/project/report/TestReportCronJob'),
            name: 'TestReportCronJob',
            nav: 'report',
            meta: {
              title: '任务报告'
            }
          },
          {
            path: '/project/:project_id/testReport/:report_id',
            component: () => import('@/components/project/report/TestReportDetail'),
            name: 'TestReportDetail',
            nav: 'report',
            hidden: true,
            meta: {
              title: '报告详情'
            },
          }
        ]
      }
    ]
  }
]

/**
 * asyncRoutes
 * the routes that need to be dynamically loaded based on user roles
 */
export const asyncRoutes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/components/Home'),
    redirect: '/projects',   // 主页指定为projects页面
    children: [
      {
        path: '/projects',
        name: 'ProjectList',
        component: () => import('@/components/project/ProjectList'),
        meta: {
          menu: '/projects',
          title: '接口测试',
          icon: 'fa fa-meetup'
        }
      },
      {
        path: '/plan',
        component: () => import('@/components/plan/Plan'),
        name: 'Plan',
        redirect: '/plans',
        meta: {
          menu: '/plan',
          title: '执行计划',
          icon: 'fa fa-etsy',
          roles: ['admin', 'project'] // you can set roles in root nav
        },
        children: [
          {
            path: '/plans',
            component: () => import('@/components/plan/PlanList'),
            name: 'PlanList',
            nav: 'planList',
            meta: {
              menu: '/plan',
              title: '执行计划列表'
            }
          },
          {
            path: '/plan/:plan_id',
            component: () => import('@/components/plan/PlanDetail'),
            name: 'PlanDetail',
            nav: 'planDetail',
            meta: {
              menu: '/plan',
              title: '执行计划'
            }
          },
          {
            path: '/plan/:plan_id/reports',
            component: () => import('@/components/plan/PlanReportList'),
            name: 'PlanReportList',
            nav: 'PlanReportList',
            meta: {
              menu: '/plan',
              title: '执行计划报告列表'
            }
          },
          {
            path: '/plan/:plan_id/reportDetail/:plan_report_id',
            component: () => import('@/components/plan/PlanReportDetail'),
            name: 'PlanReportDetail',
            nav: 'PlanReportDetail',
            meta: {
              menu: '/plan',
              title: '执行计划报告'
            }
          },
          {
            path: '/plan/:plan_id/reportDetail/:plan_report_id/project/:project_id',
            component: () => import('@/components/plan/PlanProjectReport'),
            name: 'PlanProjectReport',
            nav: 'PlanProjectReport',
            meta: {
              menu: '/plan',
              title: '执行计划-项目报告'
            }
          }
        ]
      },
      {
        path: '/envConfig',
        component: () => import('@/components/config/EnvConfig'),
        name: 'EnvConfig',
        meta: {
          menu: '/envConfig',
          title: '环境配置',
          icon: 'fa fa-cog',
          roles: ['admin'] // you can set roles in root nav
        }
      },
      {
        path: '/DBConfig',
        component: () => import('@/components/config/dbConfig/DBConfig'),
        name: 'DBConfig',
        meta: {
          menu: '/envConfig',
          title: 'DB配置'
        },
        hidden: true
      },
      {
        path: '/DBConfig/:db_config_id/DBEnvConnect',
        component: () => import('@/components/config/dbConfig/DBEnvConnect'),
        name: 'DBEnvConnect',
        meta: {
          menu: '/envConfig',
          title: 'DB环境连接配置'
        },
        hidden: true
      },
      {
        path: '/mailConfig',
        component: () => import('@/components/config/mailConfig/MailConfig'),
        name: 'MailConfig',
        meta: {
          menu: '/mailConfig',
          title: '邮件配置',
          icon: 'fa fa-envelope-o',
          roles: ['admin', 'project'] // you can set roles in root nav
        }
      },
      {
        path: '/mailListConfig/:mail_group_id',
        component: () => import('@/components/config/mailConfig/MailListConfig'),
        name: 'MailListConfig',
        meta: {
          menu: '/mailConfig',
          title: '收件人配置',
          icon: 'fa fa-id-card-o',
          roles: ['admin', 'project'] // you can set roles in root nav
        },
        hidden: true
      },
      {
        path: '/users',
        component: () => import('@/components/user/UserList'),
        name: 'Users',
        meta: {
          menu: '/users',
          title: '用户管理',
          icon: 'fa fa-id-card-o',
          roles: ['admin'] // you can set roles in root nav
        }
      },
      {
        path: '/mock',
        component: () => import('@/components/mock/Mock'),
        name: 'Mock',
        redirect: '/mocks',
        meta: {
          menu: '/mock',
          title: 'Mock数据',
          icon: 'fa fa-maxcdn',
          roles: ['admin', 'project'] // you can set roles in root nav
        },
        children: [
          {
            path: '/mocks',
            component: () => import('@/components/mock/MockList'),
            name: 'MockList',
            nav: 'mockList',
            meta: {
              menu: '/mock',
              title: 'Mock列表'
            }
          }]
      },
      {
        path: '/user/register',
        component: () => import('@/components/user/Register'),
        name: 'Register',
        meta: {
          menu: '/users',
          title: '用户注册',
          icon: 'fa fa-id-card-o',
          roles: ['admin'] // you can set roles in root nav
        },
        hidden: true
      },
      {
        path: '/user/changePassword',
        component: () => import('@/components/user/ChangePassword'),
        name: 'ChangePassword',
        meta: {
          menu: '/users',
          title: '修改密码',
          icon: 'fa fa-id-card-o'
        },
        hidden: true
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('@/components/About'),
        meta: {
          menu: '/about',
          title: '功能介绍',
          icon: 'fa fa-eye'
        }
      }
    ]
  },
  // 404 page must be placed at the end !!!
  {path: '*', redirect: '/404', hidden: true}
]

export const createRouter = () => new Router({
  mode: 'history', // require service support
  scrollBehavior: () => ({y: 0}),
  routes: constantRoutes.concat(asyncRoutes)
})


export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

const router = createRouter()

export default router
