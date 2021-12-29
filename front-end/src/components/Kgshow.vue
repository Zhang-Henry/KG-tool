<template>
    <el-container class="main-container">
        <el-aside width="200px" class="el-aside">
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

            <el-main class="main">
            <div id="myChart" :style="{width: '1000px', height: '600px'}"></div>
            </el-main>
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
            labels:[],
        }
    },
    created() {
    this.getRouterData()
    },
    methods: {
        getRouterData(){
            this.data = this.$route.params.data;
            this.links = this.$route.params.links;
            this.labels = this.$route.params.labels;
            console.log("getRouterData");
            console.log(this.labels);
        },

        show(){

            let echarts = require('echarts/lib/echarts');

            let myChart = echarts.init(document.getElementById('myChart'));

            var categories = [];

            for (var i = 0; i < this.labels.length; i++) {

                categories[i] = {name: this.labels[i]};
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
                }]
            };
            myChart.setOption(option);
        }
        
    },
    mounted: function(){
	    this.show();//需要触发的函数
    }
}
</script>
<style scoped>
    .el-aside{
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

</style>