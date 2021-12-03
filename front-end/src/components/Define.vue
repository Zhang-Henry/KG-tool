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
                <div style="font-size:24px;color:#333333;text-align:left;margin-left:50px;margin-top:40px;">
                    知识图谱构建
                </div>
                <div style="font-size:12px;color:#333333;text-align:left;margin-left:50px;margin-top:4px;">
                    用户输入结构化文本 实现自定义知识图谱
                </div>
            </el-header>

            <el-main class="main">
                <el-steps :active="1" align-center 
                style="width:600px;margin-left:auto;margin-right:auto;margin-top:10px;">
                    <el-step title="STEP 1" description="上传实体、关系文件"></el-step>
                    <el-step title="STEP 2" description="定义实体属性、关系"></el-step>
                    <el-step title="STEP 3" description="完成图谱构建"></el-step>
                </el-steps>

                
                <div id="diagramContainer">
                <div id="item_left" class="item"></div>
                <div id="item_right" class="item" style="margin-left:50px;"></div>
                
                </div>
                
            <el-button type="info" round style="margin-top:20px;" @click="goToPrev">上一步</el-button>
            <el-button type="info" round style="margin-top:20px;" @click="goToNext">下一步</el-button>
            </el-main>
        </el-container>
    </el-container>
    
</template>

<script>
import axios from 'axios'
import icon_url from '../assets/icon-2.png'


export default {
    name:"upload",
    data() {
        return {
            name: "上传文件",
            checkStatus: "",
            activeTab: 'first',
            iconPath:icon_url,
        }
    },
    methods: {
        goToNext(){
            this.$router.push({ path:'/define'  })
        },
        goToPrev(){
            this.$router.go(-1)
        }
        
    },
}

</script>
<style scoped>
    .el-aside{
        background-color: #2b3a49;
    }
    
    .main{
        background-color: #f3f3f4;
        margin-top:80px;
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