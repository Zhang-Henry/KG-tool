import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import Test from '@/components/test'
import Index from '@/components/Index'
import Define from '@/components/Define'
import Upload from '@/components/FileUpload'
import ViewResource from "vue-resource"
import Panel from "@/views/ef/panel"
import Kgshow from "@/components/Kgshow"
import KGfinish from "@/components/KGfinish"
import StructureSelect from "@/components/StructureSelect"
import Upload_Disease from "@/Disease-Build-components/Upload"
import Panel_Disease from "@/views-Disease/ef/panel"
import Kgfinish_Disease from "@/Disease-Build-components/KGfinish"
import Kgshow_Disease from "@/Disease-Build-components/Kgshow"
import Ner from "@/components/NER"

Vue.use(Router)
Vue.use(ViewResource)

export default new Router({
  routes: [
    {
      path: '/upload',
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
    },
    {
      path:'/kgshow',
      name:'Kgshow',
      component: Kgshow,
    },
    {
      path:'/kgfinish',
      name:'KGfinish',
      component: KGfinish,
    },
    {
      path:'/',
      name:'StructureSelect',
      component: StructureSelect,
    },
    {
      path:'/uploadDisease',
      name:'Upload_Disease',
      component: Upload_Disease,
    },
    {
      path:'/panelDisease',
      name:'Panel_Disease',
      component: Panel_Disease,
    },
    {
      path:'/kgshowDisease',
      name:'Kgshow_Disease',
      component: Kgshow_Disease,
    },
    {
      path:'/kgfinishDisease',
      name:'Kgfinish_Disease',
      component: Kgfinish_Disease,
    },
    {
      path:'/ner',
      name:'Ner',
      component: Ner,
    },

  ]
})
