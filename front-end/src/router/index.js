import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import Test from '@/components/test'
import Index from '@/components/Index'
import Define from '@/components/Define'
import Upload from '@/components/FileUpload'
import ViewResource from "vue-resource"
import Panel from "@/views/ef/panel"

Vue.use(Router)
Vue.use(ViewResource)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Upload',
      component: Upload
    },
    {
      path:'/index',
      name:'Index',
      component: Index,
    },
    {
      path:'/define',
      name:'Define',
      component: Define,
    },
    {
      path:'/panel',
      name:'Panel',
      component: Panel,
    }
  ]
})
