import Vue from 'vue'

import Cookies from "js-cookie";

import './assets/css/theme/index.css'
import ElementUI from 'element-ui'
import VueClipboard from 'vue-clipboard2'
import ToggleButton from 'vue-js-toggle-button'
import './assets/css/reset.css'
import './assets/fonts/iconfont.css'
import './assets/fonts/icomoon.css'
import 'font-awesome/css/font-awesome.css'
import easyDialog from 'leiang-easy-dialog'

import App from './App'
import router from './router'
import store from './store'
import './permission' // permission control
import Header from "./components/common/Header";


Vue.use(easyDialog)
Vue.use(ElementUI, {
  size: Cookies.get('size') || 'medium' // set element-ui default size
})
Vue.use(ToggleButton)
Vue.use(VueClipboard)

Vue.config.productionTip = false
Vue.component("header-view", Header)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  render: h => h(App)
})
