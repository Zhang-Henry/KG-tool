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
            <el-steps :active="1" align-center finish-status="success"
                style="width:600px;margin-left:auto;margin-right:auto;margin-top:40px;">
                    <el-step title="STEP 1" description="上传实体、关系文件"></el-step>
                    <el-step title="STEP 2" description="定义实体属性、关系"></el-step>
                    <el-step title="STEP 3" description="完成图谱构建"></el-step>
                </el-steps>
        </el-header>
        <el-main class="main">
            <div v-if="easyFlowVisible" style="height: calc(80vh);">
                <el-row>
                    <!--顶部工具菜单-->
                    <el-col :span="24">
                        <div class="ef-tooltar">
                            <el-link type="primary" :underline="false">自定义关系</el-link>
                            <el-divider direction="vertical"></el-divider>
                            <el-button type="text" icon="el-icon-delete" size="large" @click="deleteElement" :disabled="!this.activeElement.type"></el-button>
                            <el-divider direction="vertical"></el-divider>
                            <el-button type="text" icon="el-icon-download" size="large" @click="downloadData"></el-button>
                            <el-divider direction="vertical"></el-divider>
                            <el-button type="text" icon="el-icon-plus" size="large" @click="zoomAdd"></el-button>
                            <el-divider direction="vertical"></el-divider>
                            <el-button type="text" icon="el-icon-minus" size="large" @click="zoomSub"></el-button>
                            <div style="float: right;margin-right: 5px">
                                <el-button type="info" plain round icon="el-icon-document" @click="dataInfo" size="mini">流程信息</el-button>
                                <el-button type="info" round size="mini" @click="nextStep">下一步</el-button>
                            </div>
                        </div>
                    </el-col>
                </el-row>
                <div style="display: flex;height: calc(100% - 47px);">
                    <div style="width: 230px;border-right: 1px solid #dce3e8;">
                        <node-menu @addNode="addNode" ref="nodeMenu"></node-menu>
                    </div>
                    <div id="efContainer" ref="efContainer" class="container" v-flowDrag>
                        <template v-for="node in data.nodeList">
                            <flow-node
                                    :id="node.id"
                                    :key="node.id"
                                    :node="node"
                                    :activeElement="activeElement"
                                    @changeNodeSite="changeNodeSite"
                                    @nodeRightMenu="nodeRightMenu"
                                    @clickNode="clickNode"
                            >
                            </flow-node>
                        </template>
                        <!-- 给画布一个默认的宽度和高度 -->
                        <div style="position:absolute;top: 2000px;left: 2000px;">&nbsp;</div>
                    </div>
                    <!-- 右侧表单 -->
                    <div style="width: 300px;border-left: 1px solid #dce3e8;background-color: #FBFBFB">
                        <flow-node-form ref="nodeForm" @setLineLabel="setLineLabel" @repaintEverything="repaintEverything"></flow-node-form>
                    </div>
                </div>
                <!-- 流程数据详情 -->
                <flow-info v-if="flowInfoVisible" ref="flowInfo" :data="data"></flow-info>
                <flow-help v-if="flowHelpVisible" ref="flowHelp"></flow-help>
            </div>
        </el-main>
    </el-container>
</el-container>
</template>

<script>
    import draggable from 'vuedraggable'
    // import { jsPlumb } from 'jsplumb'
    // 使用修改后的jsplumb
    import './jsplumb'
    import { easyFlowMixin } from './mixins'
    import flowNode from './node'
    import nodeMenu from './node_menu'
    import FlowInfo from './info'
    import FlowHelp from './help'
    import FlowNodeForm from './node_form'
    import lodash from 'lodash'
    import { getDataA } from './data_A'
    import { getDataB } from './data_B'
    import { getDataC } from './data_C'
    import { getDataD } from './data_D'
    import { getDataE } from './data_E'
    import { ForceDirected } from './force-directed'
    import axios from 'axios'
    import icon_url from '@/assets/icon-2.png'


    export default {
        data() {
            return {
                // jsPlumb 实例
                jsPlumb: null,
                // 控制画布销毁
                easyFlowVisible: true,
                // 控制流程数据显示与隐藏
                flowInfoVisible: false,
                // 是否加载完毕标志位
                loadEasyFlowFinish: false,
                flowHelpVisible: false,
                // 数据
                data: {},
                // 激活的元素、可能是节点、可能是连线
                activeElement: {
                    // 可选值 node 、line
                    type: undefined,
                    // 节点ID
                    nodeId: undefined,
                    // 连线ID
                    sourceId: undefined,
                    targetId: undefined,
                },
                zoom: 0.5,
                iconPath:icon_url,
                lineColor:'',
                
            }
        },
        // 一些基础配置移动该文件中
        mixins: [easyFlowMixin],
        components: {
            draggable, flowNode, nodeMenu, FlowInfo, FlowNodeForm, FlowHelp
        },
        directives: {
            'flowDrag': {
                bind(el, binding, vnode, oldNode) {
                    if (!binding) {
                        return
                    }
                    el.onmousedown = (e) => {
                        if (e.button == 2) {
                            // 右键不管
                            return
                        }
                        //  鼠标按下，计算当前原始距离可视区的高度
                        let disX = e.clientX
                        let disY = e.clientY
                        el.style.cursor = 'move'

                        document.onmousemove = function (e) {
                            // 移动时禁止默认事件
                            e.preventDefault()
                            const left = e.clientX - disX
                            disX = e.clientX
                            el.scrollLeft += -left

                            const top = e.clientY - disY
                            disY = e.clientY
                            el.scrollTop += -top
                        }

                        document.onmouseup = function (e) {
                            el.style.cursor = 'auto'
                            document.onmousemove = null
                            document.onmouseup = null
                        }
                    }
                }
            }
        },
        mounted() {
            this.jsPlumb = jsPlumb.getInstance()
            this.$nextTick(() => {
                // 默认加载流程A的数据、在这里可以根据具体的业务返回符合流程数据格式的数据即可
                this.dataReload(getDataB())
            })
        

        },
        methods: {
            // 返回唯一标识
            getUUID() {
                return Math.random().toString(36).substr(3, 10)
            },
            nextStep(){
                let fileName=this.$store.state.fileName;
                axios.post("http://localhost:8000/creategraph/"+fileName+"/",JSON.stringify(this.data),{
                    headers: {
                        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
                    }
                }).then(res => {
                    console.log(res);
                });
                console.log(this.data)
                this.$router.push({ path:'/kgfinishDisease'  })
            },
            jsPlumbInit() {
                this.jsPlumb.ready(() => {
                    // 导入默认配置
                    this.jsPlumb.importDefaults(this.jsplumbSetting)
                    // 会使整个jsPlumb立即重绘。
                    this.jsPlumb.setSuspendDrawing(false, true);
                    // 初始化节点
                    this.loadEasyFlow()
                    // 单点击了连接线, https://www.cnblogs.com/ysx215/p/7615677.html
                    this.jsPlumb.bind('click', (conn, originalEvent) => {
                        this.activeElement.type = 'line'
                        this.activeElement.sourceId = conn.sourceId
                        this.activeElement.targetId = conn.targetId
                        this.$refs.nodeForm.lineInit({
                            from: conn.sourceId,
                            to: conn.targetId,
                            label: conn.getLabel(),
                            attribute: [],
                            lineId: conn.id,
                        })
                        if(this.lineColor == "#E0E3E7"){  // 点击前未被选中
                            this.jsPlumb.select().setPaintStyle({ outlineStroke: "transparent",outlineWidth:3,stroke: '#E0E3E7',strokeWidth:1});
                            var lines = this.jsPlumb.getAllConnections();
                            for(var i=0;i<lines.length;i++){
                                if(lines[i]._jsPlumb.paintStyle["stroke"] == "#E0E3E7"){
                                    lines[i].setHoverPaintStyle({ outlineStroke: "trasparent",outlineWidth:3,stroke: "#b0b2b5",strokeWidth:1})
                                }
                            }
                            conn.setPaintStyle({outlineStroke: "#C0DFFF",outlineWidth:3,stroke: '#409EFF',strokeWidth:1});
                            conn.setHoverPaintStyle({ outlineStroke: "#C0DFFF",outlineWidth:3,stroke: '#409EFF',strokeWidth:1})
                            

                        }else{   // 点击已被选中
                            conn.setPaintStyle({ outlineStroke: "transparent",outlineWidth:3,stroke: '#E0E3E7',strokeWidth:1});
                            conn.setHoverPaintStyle({outlineStroke: "transparent",outlineWidth:3,stroke: '#b0b2b5',strokeWidth:1});
                        }
                        console.log(conn._jsPlumb);
                        
                        
                    })
                    this.jsPlumb.bind('mousedown', (conn, originalEvent) => {
                        this.lineColor = conn._jsPlumb.paintStyle["stroke"];
                        
                    })
                    // 连线
                    this.jsPlumb.bind("connection", (evt) => {
                        console.log(evt.connection._jsPlumb);
                        let from = evt.source.id
                        let to = evt.target.id
                        let attribute = []
                        let id = evt.connection.id
                        if (this.loadEasyFlowFinish) {
                            this.data.lineList.push({lineId:id, from: from, to: to, attribute: attribute})
                        }
                        
                    })

                    // 删除连线回调
                    this.jsPlumb.bind("connectionDetached", (evt) => {
                        this.deleteLine(evt.sourceId, evt.targetId)
                    })

                    // 改变线的连接节点
                    this.jsPlumb.bind("connectionMoved", (evt) => {
                        this.changeLine(evt.originalSourceId, evt.originalTargetId)
                    })

                    // 连线右击
                    this.jsPlumb.bind("contextmenu", (evt) => {
                        console.log('contextmenu', evt)
                    })

                    // 连线
                    this.jsPlumb.bind("beforeDrop", (evt) => {
                        let from = evt.sourceId
                        let to = evt.targetId
                        let lineId = evt.id
                        // if (from === to) {
                        //     this.$message.error('节点不支持连接自己')
                        //     return false
                        // }
                        
                        if (this.hashOppositeLine(lineId, from, to)) {
                            this.$message.error('不支持两个节点之间连线回环');
                            return false
                        }
                        this.$message.success('连接成功')
                        return true
                    })

                    // beforeDetach
                    this.jsPlumb.bind("beforeDetach", (evt) => {
                        console.log('beforeDetach', evt)
                    })
                    this.jsPlumb.setContainer(this.$refs.efContainer)
                })
            },
            // 加载流程图
            loadEasyFlow() {
                // 初始化节点
                for (var i = 0; i < this.data.nodeList.length; i++) {
                    let node = this.data.nodeList[i]
                    // 设置源点，可以拖出线连接其他节点
                    this.jsPlumb.makeSource(node.id, lodash.merge(this.jsplumbSourceOptions, {}))
                    // // 设置目标点，其他源点拖出的线可以连接该节点
                    this.jsPlumb.makeTarget(node.id, this.jsplumbTargetOptions)
                    if (!node.viewOnly) {
                        this.jsPlumb.draggable(node.id, {
                            containment: 'parent',
                            stop: function (el) {
                                // 拖拽节点结束后的对调
                                console.log('拖拽结束: ', el)
                            }
                        })
                    }
                }
                // 初始化连线
                for (var i = 0; i < this.data.lineList.length; i++) {
                    let line = this.data.lineList[i]
                    var connParam = {
                        source: line.from,
                        target: line.to,
                        lineId: line.lineId,
                        label: line.label ? line.label : '',
                        connector: line.connector ? line.connector : '',
                        anchors: line.anchors ? line.anchors : undefined,
                        paintStyle: line.paintStyle ? line.paintStyle : undefined,
                    }
                    this.jsPlumb.connect(connParam, this.jsplumbConnectOptions)

                }
                this.$nextTick(function () {
                    this.loadEasyFlowFinish = true
                })
            },
            // 设置连线条件
            setLineLabel(from, to, label, attribute, lineId) {
                console.log("params:",from,to,lineId,attribute,);
                var conns = this.jsPlumb.getConnections({
                    source: from,
                    target: to
                })
                var conn;
                for(var i=0;i<conns.length;i++){
                    if(conns[i].id == lineId){
                        conn = conns[i];
                        break;
                    }
                }
                console.log(conn);
                if (!label || label === '') {
                    conn.removeClass('flowLabel')
                    conn.addClass('emptyFlowLabel')
                } else {
                    conn.addClass('flowLabel')
                }
                conn.setLabel({
                    label: label,
                })
                this.data.lineList.forEach(function (line) {
                    if (line.from == from && line.to == to && line.lineId == lineId) {
                        line.label = label
                        line.attribute = attribute
                    }
                })

            },
            // 删除激活的元素
            deleteElement() {
                if (this.activeElement.type === 'node') {
                    this.deleteNode(this.activeElement.nodeId)
                } else if (this.activeElement.type === 'line') {
                    this.$confirm('确定删除所点击的线吗?', '提示', {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'warning'
                    }).then(() => {
                        var conn = this.jsPlumb.getConnections({
                            source: this.activeElement.sourceId,
                            target: this.activeElement.targetId
                        })[0]
                        this.jsPlumb.deleteConnection(conn)
                    }).catch(() => {
                    })
                }
            },
            // 删除线
            deleteLine(from, to) {
                console.log("deleteLine PARAM:",from,to);
                this.data.lineList = this.data.lineList.filter(function (line) {
                    if (line.from == from && line.to == to && line.lineId == lineId) {
                        return false
                    }
                    return true
                })
            },
            // 改变连线
            changeLine(lineId, oldFrom, oldTo) {
                this.deleteLine(lineId, oldFrom, oldTo)
            },
            // 改变节点的位置
            changeNodeSite(data) {
                for (var i = 0; i < this.data.nodeList.length; i++) {
                    let node = this.data.nodeList[i]
                    if (node.id === data.nodeId) {
                        node.left = data.left
                        node.top = data.top
                    }
                }
            },
            /**
             * 拖拽结束后添加新的节点
             * @param evt
             * @param nodeMenu 被添加的节点对象
             * @param mousePosition 鼠标拖拽结束的坐标
             */
            addNode(evt, nodeMenu, mousePosition) {
                var screenX = evt.originalEvent.clientX, screenY = evt.originalEvent.clientY
                let efContainer = this.$refs.efContainer
                var containerRect = efContainer.getBoundingClientRect()
                var left = screenX, top = screenY
                // 计算是否拖入到容器中
                if (left < containerRect.x || left > containerRect.width + containerRect.x || top < containerRect.y || containerRect.y > containerRect.y + containerRect.height) {
                    this.$message.error("请把节点拖入到画布中")
                    return
                }
                left = left - containerRect.x + efContainer.scrollLeft
                top = top - containerRect.y + efContainer.scrollTop
                // 居中
                left -= 85
                top -= 16
                var nodeId = this.getUUID()
                // 动态生成名字
                var origName = nodeMenu.name
                var nodeName = origName
                var index = 1
                while (index < 10000) {
                    var repeat = false
                    for (var i = 0; i < this.data.nodeList.length; i++) {
                        let node = this.data.nodeList[i]
                        if (node.name === nodeName) {
                            nodeName = origName + index
                            repeat = true
                        }
                    }
                    if (repeat) {
                        index++
                        continue
                    }
                    break
                }
                var node = {
                    id: nodeId,
                    name: nodeName,
                    type: nodeMenu.type,
                    left: left + 'px',
                    top: top + 'px',
                    ico: nodeMenu.ico,
                    state: 'success',
                    attribute:[],
                }
                /**
                 * 这里可以进行业务判断、是否能够添加该节点
                 */
                this.data.nodeList.push(node)
                this.$nextTick(function () {
                    this.jsPlumb.makeSource(nodeId, this.jsplumbSourceOptions)
                    this.jsPlumb.makeTarget(nodeId, this.jsplumbTargetOptions)
                    this.jsPlumb.draggable(nodeId, {
                        containment: 'parent',
                        stop: function (el) {
                            // 拖拽节点结束后的对调
                            console.log('拖拽结束: ', el)
                        }
                    })
                })
            },
            /**
             * 删除节点
             * @param nodeId 被删除节点的ID
             */
            deleteNode(nodeId) {
                this.$confirm('确定要删除节点' + nodeId + '?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false
                }).then(() => {
                    /**
                     * 这里需要进行业务判断，是否可以删除
                     */
                    this.data.nodeList = this.data.nodeList.filter(function (node) {
                        if (node.id === nodeId) {
                            // 伪删除，将节点隐藏，否则会导致位置错位
                            // node.show = false
                            return false
                        }
                        return true
                    })
                    this.$nextTick(function () {
                        this.jsPlumb.removeAllEndpoints(nodeId);
                    })
                }).catch(() => {
                })
                return true
            },
            clickNode(nodeId) {
                this.activeElement.type = 'node'
                this.activeElement.nodeId = nodeId
                this.$refs.nodeForm.nodeInit(this.data, nodeId)
            },
            // 是否具有该线
            hasLine(lineId, from, to) {
                for (var i = 0; i < this.data.lineList.length; i++) {
                    var line = this.data.lineList[i]
                    if (line.from === from && line.to === to && line.lineId == lineId) {
                        return true
                    }
                }
                return false
            },
            // 是否含有相反的线
            hashOppositeLine(lineId, from, to) {
                return this.hasLine(lineId, to, from)
            },
            nodeRightMenu(nodeId, evt) {
                this.menu.show = true
                this.menu.curNodeId = nodeId
                this.menu.left = evt.x + 'px'
                this.menu.top = evt.y + 'px'
            },
            repaintEverything() {
                this.jsPlumb.repaint()
            },
            // 流程数据信息
            dataInfo() {
                this.flowInfoVisible = true
                this.$nextTick(function () {
                    this.$refs.flowInfo.init()
                })
            },
            // 加载流程图
            dataReload(data) {
                this.easyFlowVisible = false
                this.data.nodeList = []
                this.data.lineList = []
                this.$nextTick(() => {
                    data = lodash.cloneDeep(data)
                    this.easyFlowVisible = true
                    this.data = data
                    this.$nextTick(() => {
                        this.jsPlumb = jsPlumb.getInstance()
                        this.$nextTick(() => {
                            this.jsPlumbInit()
                        })
                    })
                })
            },
            
            zoomAdd() {
                if (this.zoom >= 1) {
                    return
                }
                this.zoom = this.zoom + 0.1
                this.$refs.efContainer.style.transform = `scale(${this.zoom})`
                this.jsPlumb.setZoom(this.zoom)
            },
            zoomSub() {
                if (this.zoom <= 0) {
                    return
                }
                this.zoom = this.zoom - 0.1
                this.$refs.efContainer.style.transform = `scale(${this.zoom})`
                this.jsPlumb.setZoom(this.zoom)
            },
            // 下载数据
            downloadData() {
                this.$confirm('确定要下载该流程数据吗？', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false
                }).then(() => {
                    var datastr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.data, null, '\t'));
                    var downloadAnchorNode = document.createElement('a')
                    downloadAnchorNode.setAttribute("href", datastr);
                    downloadAnchorNode.setAttribute("download", 'data.json')
                    downloadAnchorNode.click();
                    downloadAnchorNode.remove();
                    this.$message.success("正在下载中,请稍后...")
                }).catch(() => {
                })
            },
            openHelp() {
                this.flowHelpVisible = true
                this.$nextTick(function () {
                    this.$refs.flowHelp.init()
                })
            }
            
        }
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

</style>
