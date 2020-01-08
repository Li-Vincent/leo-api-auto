import jwt_decode from "jwt-decode";
import {getToken, setToken, removeToken} from "../../utils/auth";
import {login, logout, getUserRoles} from "../../api/user";
import {resetRouter} from "../../router";
import {Message} from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style

const state = {
  token: getToken(),
  email: '',
  roles: []
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_EMAIL: (state, email) => {
    state.email = email
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  }
}

const actions = {
  login({commit}, params) {
    return new Promise((resolve, reject) => {
      // start progress bar
      NProgress.start()

      login(params).then(res => {
        const {status, data} = res
        if (status === 'ok') {
          commit('SET_TOKEN', data.token)
          commit('SET_EMAIL', data.email)
          setToken(data.token)
          NProgress.done()
          resolve()
        } else {
          Message.error({
            message: data,
            center: true,
          });
          NProgress.done()
        }
      }).catch(error => {
        NProgress.done()
        reject(error)
      })
    })
  },

  // get user info
  getUserInfo({commit, state}) {
    return new Promise((resolve, reject) => {
      getUserRoles(state.email).then(res => {
        if (res.status !== 'ok') {
          reject('Verification failed, please Login again.')
        }
        const {roles} = res.data
        // roles must be a non-empty array
        if (!roles || roles.length <= 0) {
          reject('getInfo: roles must be a non-null array!')
        }
        commit('SET_ROLES', roles)
        resolve(res.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // user logout
  logout({commit}) {
    return new Promise((resolve, reject) => {
      logout().then((res) => {
        const {status, data} = res
        if (status === 'ok') {
          console.log("logout successfully")
          commit('SET_EMAIL', '')
          commit('SET_TOKEN', '')
          commit('SET_ROLES', [])
          removeToken()
          resetRouter()
          resolve(data)
        } else {
          Message.error({
            message: data,
            center: true,
          });
        }
      }).catch(error => {
        reject(error)
      })
    })
  },

  // remove token
  resetToken({commit}) {
    return new Promise(resolve => {
      commit('SET_TOKEN', '')
      commit('SET_ROLES', [])
      commit('SET_EMAIL', '')
      removeToken()
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
