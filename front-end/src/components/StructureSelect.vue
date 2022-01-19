<template>
    <el-container class="main-container">
        <el-aside width="200px" class="el-aside">
            <el-col>
                <el-image class="icon-img" :src="iconPath" style="width:60%;margin-top:30px;"></el-image>
                <el-menu
                class="el-menu-vertical-demo"
                background-color="#2b3a49"
                text-color="#fff"
                active-text-color="#66c6a3" style="margin-top:16px;"
                :router="true">
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
                <el-menu-item index="/ner">
                    <i class="el-icon-menu"></i>
                    <span slot="title">实体识别</span>
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
                <div style="font-size:24px;color:#333333;text-align:left;margin-left:50px;margin-top:35px;">
                    结构化文件构建知识图谱
                </div>
                <div style="font-size:12px;color:#333333;text-align:left;margin-left:50px;margin-top:4px;">
                    用户输入结构化文本 实现自定义知识图谱
                </div>
            </el-header>

            <el-main class="main">
                <div style="display:flex;margin-top:60px;">
                    <el-card class="box-card">
                    <i class="el-icon-document-copy" style="font-size:80px;color:#555555;margin-top:30px;"></i>
                    <div style="font-size:20px;color:#555555;margin-top:10px;"> 
                        实体+关系文件
                    </div>

                    <div style="font-size:10px;color:#555555;margin-top:10px;"> 
                        输入实体文件和关系<br>文件构建知识图谱
                    </div>
                    <el-button type="info" round style="margin-top:20px;" @click="goTo1">开始</el-button>
                    </el-card>

                    <el-card class="box-card">
                    <i class="el-icon-s-order" style="font-size:80px;color:#555555;margin-top:30px;"></i>
                    <div style="font-size:20px;color:#555555;margin-top:10px;"> 
                        医学疾病文件
                    </div>

                    <div style="font-size:10px;color:#555555;margin-top:10px;"> 
                        输入以疾病为实体的<br>文件构建知识图谱
                    </div>
                    <el-button type="info" round style="margin-top:20px;" @click="goTo2">开始</el-button>
                    </el-card>

                    <el-card class="box-card">
                    <i class="el-icon-more-outline" style="font-size:80px;color:#555555;margin-top:30px;"></i>
                    <div style="font-size:20px;color:#555555;margin-top:10px;"> 
                        更多
                    </div>

                    <div style="font-size:10px;color:#555555;margin-top:10px;"> 
                        haiyougengduo<br>houxugengxin
                    </div>
                    <el-button type="info" round style="margin-top:20px;">开始</el-button>
                    </el-card>
                </div>
            </el-main>
        </el-container>
    </el-container>
    
</template>

<script>
import axios from 'axios'
import icon_url from '@/assets/icon-2.png'
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
        goTo1(){
            this.$router.push({ path:'/upload' })
        },
        goTo2(){
            this.$router.push({ path:'/uploadDisease' })
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
    .box-card{
        width:300px;
        height:320px;
        margin:auto;
    }

</style>