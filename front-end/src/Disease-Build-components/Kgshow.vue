<template>
    <el-container class="main-container">
        <el-aside id="menu-aside" width="200px" class="el-aside">
            <el-col>
                <el-image class="icon-img" :src="iconPath" style="width:60%;margin-top:30px;"></el-image>
                <el-menu
                default-active="1-1"
                class="el-menu-vertical-demo"
                background-color="#2b3a49"
                text-color="#fff"
                active-text-color="#66c6a3" style="margin-top:16px;">
                <el-submenu index="1">
                    <template slot="title">
                    <i class="el-icon-s-opportunity"></i>
                    <span>图谱构建</span>
                    </template>
                    <el-menu-item-group>
                    <el-menu-item index="1-1">结构化</el-menu-item>
                    <el-menu-item index="1-2">非结构化</el-menu-item>
                    </el-menu-item-group>
                </el-submenu>
                <el-menu-item index="2">
                    <i class="el-icon-menu"></i>
                    <span slot="title">建设中...</span>
                </el-menu-item>
                <el-menu-item index="3">
                    <i class="el-icon-document"></i>
                    <span slot="title">建设中...</span>
                </el-menu-item>
                <el-menu-item index="4">
                    <i class="el-icon-setting"></i>
                    <span slot="title">建设中...</span>
                </el-menu-item>
                </el-menu>
            </el-col>    
        </el-aside>
        
        <el-container>
            <el-header class='el-header'> 
                <div style="font-size:24px;color:#333333;text-align:left;margin-left:50px;margin-top:30px;">
                    自定义知识图谱
                </div>
                <div style="font-size:12px;color:#333333;text-align:left;margin-left:50px;margin-top:4px;">
                    用户输入结构化文本 实现自定义知识图谱
                </div>
            </el-header>

            <el-container>

                <el-main class="main">
                <div id="myChart" :style="{width: '50%px', height: '660px'}"></div>
                </el-main>

                <el-aside class="info">
                    <el-tabs v-model="activeName" type="card" @tab-click="handleClick">

                        <el-tab-pane label="搜索" name="first">
                            <div style="margin-top:30px;font-size:14px;color:#b5b5b5;text-align:left;margin-left:30px;">
                                点击查询节点
                            </div>
                            <h2 style="margin-left:30px;margin-right:30px;height:1px;background-color:#b5b5b5"></h2>
                            <div>
                                <el-button v-for="(entity, index) in entities" :key="index" @click="searchEntity(entity)" round type="info" size="small" style="margin-left:10px;margin-bottom:12px"> 
                                    {{ entity }} 
                                </el-button>
                            </div>
                            <div style="margin-top:10px;font-size:14px;color:#b5b5b5;text-align:left;margin-left:30px;">
                                点击查询关系
                            </div>
                            <h2 style="margin-left:30px;margin-right:30px;height:1px;background-color:#b5b5b5"></h2>
                            <div>
                                <el-button v-for="(relation, index) in relations" :key="index" @click="searchRelation(relation)" round type="info" size="small" style="margin-left:10px;margin-bottom:12px"> 
                                    {{ relation }} 
                                </el-button>
                            </div>
                        </el-tab-pane>
                        
                        <el-tab-pane label="信息" name="second">
                            <div style="margin-top:20px;font-size:20px;color:#333333;text-align:left;margin-left:40px;">
                                Disease知识图谱
                            </div>
                            <div style="margin-top:30px;font-size:14px;color:#b5b5b5;text-align:left;margin-left:40px;">
                                当前节点信息
                            </div>
                            <transition name="el-zoom-in-top">
                            <div v-show="infoshow" class="table-content">
                                <el-table
                                    :show-header="false"
                                    :data="list"
                                    class="mt-10"
                                    fit
                                    empty-text="暂无数据"
                                    :highlight-current-row="true"
                                    style="margin-top:10px;"
                                >
                                    <el-table-column align="center">
                                        <template slot-scope="scope">
                                        <template>
                                            <el-tag>{{scope.row.id}}</el-tag>
                                        </template>
                                        </template>
                                    </el-table-column>
                                    <el-table-column
                                    v-for="(item, index) in table_title"
                                    :key="index"
                                    :prop="item.prop"
                                    :label="item.label"
                                    >
                                    </el-table-column>
                                    
                                </el-table>
                            </div>
                            </transition>

                            <div style="margin-top:30px;font-size:14px;color:#b5b5b5;text-align:left;margin-left:40px;">
                                当前节点属性
                            </div>
                            <div class="table-content">
                                <el-table
                                    :show-header="false"
                                    :data="list_ch"
                                    class="mt-10"
                                    fit
                                    empty-text="暂无数据"
                                    :highlight-current-row="true"
                                    style="margin-top:10px;"
                                    max-height="280px"
                                >
                                    <el-table-column align="center">
                                        <template slot-scope="scope">
                                        <template>
                                            <el-tag>{{scope.row.id}}</el-tag>
                                        </template>
                                        </template>
                                    </el-table-column>
                                    <el-table-column
                                    v-for="(item, index) in table_title"
                                    :key="index"
                                    :prop="item.prop"
                                    :label="item.label"
                                    >
                                    </el-table-column>
                                    
                                </el-table>
                            </div>
                        </el-tab-pane>
                    </el-tabs>
                </el-aside>

            </el-container>
        </el-container>
    </el-container>
    
</template>

<script>
import axios from 'axios'
import icon_url from '@/assets/icon-2.png'
import echarts from 'echarts'

export default {
    name:"upload",
    data() {
        return {
            name: "上传文件",
            checkStatus: "",
            activeTab: 'first',
            iconPath:icon_url,
            data:[],
            links:[],
            entities:[],
            relations:[],
            activeName: 'first',
            myChart:null,
            table_title:[
                {
                    prop: 'input',
                    label: '属性',
                    width: '100',
                    titleAlign: 'center',
                    columnAlign: 'center',

                },
            ],
            list:[],
            list_ch:[],
            infoshow:true,
            myChart:undefined,
        }
    },
    created() {
        this.getRouterData()
    },
    methods: {
        searchEntity(entity){
            console.log(entity);
            axios.post("http://localhost:8000/get_entity/"+entity+"/",{
                    headers: {
                        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
                    }
                }).then(res => {
                    console.log(res);
            });
        },

        searchRelation(relation){
            console.log(relation);
            axios.post("http://localhost:8000/get_relation/"+relation+"/",{
                    headers: {
                        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
                    }
                }).then(res => {
                    console.log(res);
                    this.refreshGraph(res.data.data,res.data.links);
            });
        },

        handleClick(tab, event) {
            console.log(tab, event);
        },

        getRouterData(){
            this.data = this.$route.params.data;
            this.links = this.$route.params.links;
            this.entities = this.$route.params.entities;
            this.relations = this.$route.params.relations;
            console.log("getRouterData");
            console.log(this.data);
            console.log(this.links);
        },

        show(){

            let echarts = require('echarts/lib/echarts');

            this.myChart = echarts.init(document.getElementById('myChart'));

            var categories = [];

            for (var i = 0; i < this.entities.length; i++) {

                categories[i] = {name: this.entities[i]};
            }

            let option = {
                // title: {text: 'ECharts 关系图'},

                tooltip: {
                    formatter: function (x) {
                    return x.data.des;
                    }
                },

                toolbox: {
                    show: true,
                    feature: {
                        mark: {
                        show: true
                        },
                        restore: {
                        show: true
                        },
                        saveAsImage: {
                        show: true
                        }
                    }
                },
                legend: [{
                    data: categories.map(function (a) {
                    return a.name;
                    })
                }],

                series: [{
                    type: 'graph', // 类型:关系图
                    layout: 'force', //图的布局，类型为力导图
                    symbolSize: 40, // 调整节点的大小
                    roam: true, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移,可以设置成 'scale' 或者 'move'。设置成 true 为都开启
                    edgeSymbol: ['circle', 'arrow'],
                    edgeSymbolSize: [2, 10],
                    edgeLabel: {
                        normal: {
                            textStyle: {
                            fontSize: 20
                            }
                        }
                    },
                    force: {
                    repulsion: 2500,
                    edgeLength: [10, 50]
                    },
                    draggable: true,
                    lineStyle: {
                        normal: {
                        width: 2,
                        color: '#4b565b',
                        }
                    },
                    edgeLabel: {
                        normal: {
                        show: true,
                        formatter: function (x) {
                            return x.data.name;
                        }
                        }
                    },
                    label: {
                        normal: {
                        show: true,
                        textStyle: {}
                        }
                    },
                    data: this.data,
                    links: this.links,
                    categories: categories,
                    
                    // data: [{'name':'肺泡蛋白质沉积症','properties':{'test1':'okk','test2':'666'},'symbolSize':80,'category':'Disease'},{'name':'呼吸内科','symbolSize':70,'category':'Category'}],
                    // links:[{'target':'呼吸内科','source':'肺泡蛋白质沉积症','name':'category','des':'属于'}],
                    // categories: [{'name':'Disease'},{'name':'Category'}]
                }]
            };
            this.myChart.setOption(option);
            
            
            this.myChart.on('click', (params)  => {
                console.log(params);
                var data = params.data;
                this.activeName = 'second';
                if(params.dataType == "node"){
                    this.list=[
                    {
                        id: "实体类别",
                        input: params.data.category,
                    }, {
                        id: "实体名称",
                        input: params.data.name,
                    }];
                    var properties = params.data.properties;
                    if(typeof(properties)!="undefined"){
                        this.list_ch = [];
                        for(var item in properties){
                        this.list_ch.push({
                            id:item,
                            input:properties[item],
                        })
                    }}else{
                        this.list_ch = [];
                    }
                    
                }else if(params.dataType == "edge"){
                    this.list=[
                    {
                        id: "关系类别",
                        input: params.data.name,
                    }, {
                        id: "关系名称",
                        input: params.data.des,
                    }];
                    var properties = params.data.properties;
                    if(typeof(properties)!="undefined"){
                        for(var item in properties){
                        this.list_ch.push({
                            id:item,
                            input:properties[item],
                        })
                    }}else{
                        this.list_ch = [];
                    }
                    
                }
                
                
                
            });
            
        },
        refreshGraph(data,links){
            var option = this.myChart.getOption();
            option.series[0].data = data;
            options.series[0].links = links;
            this.myChart.setOption(option);    
        }
        
    },
    mounted: function(){
	    this.show();//需要触发的函数
    }
}
</script>
<style scoped>
    #menu-aside{
        background-color: #2b3a49;
    }
    
    .main{
        background-color: #f3f3f4;
        margin-top:42px;
    }
    .main-container{
        position:absolute;
        height:100%;
        width:100%;
    }
    .card-box{
        margin-top:100px;
    }
    .tab-title{
        color:#fff;
    }
    .info{
        margin-top:42px;
    }

</style>