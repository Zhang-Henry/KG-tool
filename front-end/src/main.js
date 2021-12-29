// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import VueAxios from "vue-axios";
import axios from 'axios'
import 'element-ui/lib/theme-chalk/index.css'
import './views/ef/index.css'
import vuex from 'vuex'

Vue.config.productionTip = false;
Vue.use(ElementUI);
Vue.use(vuex);
var store = new vuex.Store({//store对象
    state:{
        fileName:""
    }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})


