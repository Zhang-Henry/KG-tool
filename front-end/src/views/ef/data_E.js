var dataE = {
    name: '流程E，力导图',
    nodeList: [
        {
            id: 'nodeA',
            name: '流程D-节点A',
            type: 'task',
            ico: 'el-icon-user-solid',
            state: 'success',
            attribute:[],
        },
        {
            id: 'nodeB',
            type: 'task',
            name: '流程D-节点B',
            ico: 'el-icon-goods',
            state: 'error',
            attribute:[],
        },
        {
            id: 'nodeC',
            name: '流程D-节点C',
            type: 'task',
            ico: 'el-icon-present',
            state: 'warning',
            attribute:[],
        }, {
            id: 'nodeD',
            name: '流程D-节点D',
            type: 'task',
            ico: 'el-icon-present',
            state: 'running',
            attribute:[],
        }
    ],
    lineList: [{
        from: 'nodeA',
        to: 'nodeB',
        attribute:[],
    }, {
        from: 'nodeA',
        to: 'nodeC',
        label: 'hello',
        attribute:[],
    }, {
        from: 'nodeB',
        to: 'nodeD',
        attribute:[],
    }, {
        from: 'nodeC',
        to: 'nodeD',
        attribute:[],
    }, 
    ]
}

export function getDataE() {
    return dataE
}
