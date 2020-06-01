import Vue from 'vue'
import App from './App.vue'

import 'bootswatch/dist/united/bootstrap.min.css'

Vue.config.debug = true
Vue.config.devtools = true
new Vue({
  render: h => h(App)
}).$mount('#app')