<template>
    <div>
        <div class="ef-node-form">
            <div class="ef-node-form-header">
                编辑
            </div>
            <div class="ef-node-form-body">
                <el-form :model="node" ref="dataForm" label-width="80px" v-show="type === 'node'">
                    <el-form-item label="实体名称">
                        <el-input v-model="node.name"></el-input>
                    </el-form-item>

                    <el-form-item label="实体属性">
                        <el-tag :key="tag" v-for="tag in node.attribute" closable :disable-transitions="false" @click="changeValue(node,tag)"
                        @close="handleClose(node,tag)">
                        {{tag}}
                        </el-tag>

                        <el-input class="input-new-tag" v-if="inputVisible" v-model="inputValue" ref="saveTagInput" size="small"
                        @keyup.enter.native="handleInputConfirm(node)" @blur="handleInputConfirm(node)"></el-input>
                        <el-button v-else class="button-new-tag" size="small" @click="showInput">+ New Tag</el-button>
                        
                    </el-form-item>

                    <!--<el-form-item label="状态">
                        <el-select v-model="node.state" placeholder="请选择">
                            <el-option
                                    v-for="item in stateList"
                                    :key="item.state"
                                    :label="item.label"
                                    :value="item.state">
                            </el-option>
                        </el-select>
                    </el-form-item>-->
                    
                    <el-form-item>
                        <el-button icon="el-icon-close">重置</el-button>
                        <el-button type="primary" icon="el-icon-check" @click="save">保存</el-button>
                    </el-form-item>
                </el-form>

                <el-form :model="line" ref="dataForm" label-width="80px" v-show="type === 'line'">
                    <el-form-item label="关系名称">
                        <el-select v-model="line.label" placeholder="请选择">
                            <el-option
                            v-for="item in options"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                            :disabled="item.disabled">
                            </el-option>
                        </el-select>
                    </el-form-item>

                    <el-form-item label="关系属性">
                        <el-tag :key="tag" v-for="tag in line.attribute" closable :disable-transitions="false" @click="changeValue_line(line,tag)"
                        @close="handleClose_line(line,tag)">
                        {{tag}}
                        </el-tag>

                        <el-input class="input-new-tag" v-if="inputVisible" v-model="inputValue" ref="saveTagInput" size="small"
                        @keyup.enter.native="handleInputConfirm_line(line)" @blur="handleInputConfirm_line(line)"></el-input>
                        <el-button v-else class="button-new-tag" size="small" @click="showInput">+ New Tag</el-button>
                        
                    </el-form-item>

                    <el-form-item>
                        <el-button icon="el-icon-close">重置</el-button>
                        <el-button type="primary" icon="el-icon-check" @click="saveLine(line)">保存</el-button>
                    </el-form-item>
                </el-form>
            </div>
            <!--            <div class="el-node-form-tag"></div>-->
        </div>
    </div>

</template>

<script>
    import { cloneDeep } from 'lodash'
    import axios from 'axios'

    export default {
        data() {
            return {
                visible: true,
                // node 或 line
                type: 'node',
                node: {},
                line: {},
                data: {},
                stateList: [{
                    state: 'success',
                    label: '成功'
                }, {
                    state: 'warning',
                    label: '警告'
                }, {
                    state: 'error',
                    label: '错误'
                }, {
                    state: 'running',
                    label: '运行中'
                }],
                dynamicTags: [],
                inputVisible: false,
                inputValue: '',
                tempTag: '',
                // 是否是重复数据
                isRepeatedData: false,
                // 是否改变原来的值
                isChange: false,

                options: [],
                options_disabled: {},
            }
        },
        mounted(){
            let fileName=this.$store.state.fileName;
            console.log(fileName)
            axios.post("http://localhost:8000/attr/"+fileName+"/",{
                headers: {
                    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
                }
            }).then(res => {
                console.log(res.data.attri)
                var data_list = res.data.attri;
                for(var i = 0;i<data_list.length;i++){
                    var option = {};
                    var num = i+1;
                    option["value"] = data_list[i];
                    option["label"] = data_list[i];
                    option["disabled"] = false;
                    this.options.push(option)
                }
                console.log("options:",this.options)
            });
        },
        methods: {
            /**
             * 表单修改，这里可以根据传入的ID进行业务信息获取
             * @param data
             * @param id
             */
            nodeInit(data, id) {
                this.type = 'node'
                this.data = data
                data.nodeList.filter((node) => {
                    if (node.id === id) {
                        this.node = cloneDeep(node)
                    }
                })
            },
            lineInit(line) {
                this.type = 'line'
                this.line = line
            },
            // 修改连线
            saveLine(line) {
                console.log(this.line.attribute)
                this.$emit('setLineLabel', this.line.from, this.line.to, this.line.label, this.line.attribute, this.line.lineId)
            },
            save() {
                this.data.nodeList.filter((node) => {
                    if (node.id === this.node.id) {
                        node.name = this.node.name
                        node.left = this.node.left
                        node.top = this.node.top
                        node.ico = this.node.ico
                        node.state = this.node.state
                        node.attribute = this.node.attribute
                        this.$emit('repaintEverything')
                    }
                })
            },

            // 添加属性的函数：
            handleClose(node,tag) {
                this.node.attribute.splice(this.node.attribute.indexOf(tag), 1);
            },
            handleClose_line(line,tag) {
                this.line.attribute.splice(this.line.attribute.indexOf(tag), 1);
            },

            showInput() {
                this.tempTag = ''
                this.inputVisible = true;
                this.inputValue = ''
                this.isChange = false

                this.$nextTick(_ => {
                this.$refs.saveTagInput.$refs.input.focus();
                });
            },

            handleInputConfirm(node) {
                console.log(node.attribute)
                this.isRepeatedData = false
                let inputValue = this.inputValue;
                // 去空格
                inputValue = inputValue.replace(/^\s\s*/, '').replace(/\s\s*$/, '')
                if (inputValue == '') {
                this.inputVisible = false
                return
                }
                // console.log(inputValue+'uuu:'+this.tempTag)
                // 判断新增的值是否重复
                if (this.node.attribute.indexOf(inputValue) != -1 && this.tempTag === inputValue) {
                this.isRepeatedData = true
                this.$message.warning("不允许添加重复数据！")
                return
                } else {
                this.isRepeatedData = false
                // this.isChange = false
                }
                // 判断是否修改原有值，是 替换修改好的值，否新增
                if (this.isChange) {
                this.node.attribute[this.node.attribute.indexOf(this.tempTag)] = this.inputValue
                this.inputVisible = false
                return
                }
                // 点击添加时，追加
                if (inputValue) {
                this.node.attribute.push(inputValue);
                console.log(inputValue+'tt:'+this.node.attribute)
                }
                this.inputVisible = false;
                this.inputValue = '';
            },
            handleInputConfirm_line(line) {
                console.log(line.attribute)
                this.isRepeatedData = false
                let inputValue = this.inputValue;
                // 去空格
                inputValue = inputValue.replace(/^\s\s*/, '').replace(/\s\s*$/, '')
                if (inputValue == '') {
                this.inputVisible = false
                return
                }
                // console.log(inputValue+'uuu:'+this.tempTag)
                // 判断新增的值是否重复
                if (this.line.attribute.indexOf(inputValue) != -1 && this.tempTag === inputValue) {
                this.isRepeatedData = true
                this.$message.warning("不允许添加重复数据！")
                return
                } else {
                this.isRepeatedData = false
                // this.isChange = false
                }
                // 判断是否修改原有值，是 替换修改好的值，否新增
                if (this.isChange) {
                this.line.attribute[this.line.attribute.indexOf(this.tempTag)] = this.inputValue
                this.inputVisible = false
                return
                }
                // 点击添加时，追加
                if (inputValue) {
                this.line.attribute.push(inputValue);
                console.log(inputValue+'tt:'+this.line.attribute)
                }
                this.inputVisible = false;
                this.inputValue = '';
            },
            changeValue(node,tag) {
                this.inputVisible = true
                this.$nextTick(_ => {
                this.$refs.saveTagInput.$refs.input.focus();
                });
                this.inputValue = tag
                this.tempTag = tag
                this.isChange = true
            },
            changeValue_line(line,tag) {
                this.inputVisible = true
                this.$nextTick(_ => {
                this.$refs.saveTagInput.$refs.input.focus();
                });
                this.inputValue = tag
                this.tempTag = tag
                this.isChange = true
            }
        }

    }
</script>

<style>
    .el-node-form-tag {
        position: absolute;
        top: 50%;
        margin-left: -15px;
        height: 40px;
        width: 15px;
        background-color: #fbfbfb;
        border: 1px solid rgb(220, 227, 232);
        border-right: none;
        z-index: 0;
    }
    .el-tag + .el-tag {
    margin-left: 10px;
    }
    .button-new-tag {
        margin-left: 10px;
        height: 32px;
        line-height: 30px;
        padding-top: 0;
        padding-bottom: 0;
    }
    .input-new-tag {
        width: 90px;
        margin-left: 10px;
        vertical-align: bottom;
    }
</style>
