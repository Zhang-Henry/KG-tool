<template>
    <el-container class="main-container">
        <el-aside width="200px" class="elaside">
            <el-col>
                <el-image class="icon-img" :src="iconPath" style="width:60%;margin-top:30px;"></el-image>
                <el-menu
                default-active="2"
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
                <div style="font-size:24px;color:#333333;text-align:left;margin-left:50px;margin-top:30px;">
                    实体识别
                </div>
            </el-header>

            <el-main style="height:100%;width:100%;margin-bottom:-20px;">
                <el-container style="height:100%;">
                    <el-aside style="background-color:#f3f3f4;width:40%;margin-left:-20px;">
                        
                        <div style="text-align:left;color:#B8B8B8;margin-top:70px;font-size:14px;margin-left:50px;">请输入文本，点击确定抽取实体</div>
                        <div >
                        <el-input
                        type="textarea"
                        :autosize="{ minRows: 2, maxRows: 20}"
                        placeholder="请输入内容"
                        v-model="textarea" style="margin-top:20px;width:70%;">

                        </el-input>
                        </div>
                        <el-button @click="uploadText" style="margin-top:50px;">确定</el-button>
                    </el-aside>
                    <el-main style="background-color:#D9D8D8;margin-right:-20px">
                        
                        <div v-show="infoshow" class="table-content">
                            <el-table
                                :show-header="false"
                                :data="list"
                                :cell-style="cellStyle"
                                class="mt-10"
                                fit
                                empty-text="上传文本查看结果"
                                :highlight-current-row="true"
                                style="margin-top:50px;"
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
                    </el-main>
                </el-container>    
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
            textarea:'',
            table_title:[
                {
                    prop: 'input',
                    label: '属性',
                    width: '100',
                    titleAlign: 'center',
                    columnAlign: 'center',

                },
            ],
            infoshow:true,
            list:[],
            cellStyle:{background:"#D9D8D8"},
        }
    },
    methods: {
        uploadText(){
            console.log(this.textarea);
            axios.post("http://localhost:8000/nerText/",JSON.stringify(this.textarea),{
                headers: {
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
                }
            }).then(res => {
                console.log(res);
                this.list = res.data.list;
            });
        },


        
        
    },
}
</script>
<style scoped>
    .elaside{
        background-color: #2b3a49;
    }
    
    .main{
        background-color: #f3f3f4;  
        margin-top:40px;   
    }
    .main-container{
        position:absolute;
        height:100%;
        width:100%;
    }
    .tab-title{
        color:#fff;
    }

</style>