let dataB = {
    name: '流程B',
    nodeList: [
        {
            id: 'nodeA',
            name: '实体A',
            type: 'task',
            left: '18px',
            top: '223px',
            ico: 'el-icon-user-solid',
            state: 'success',
            attribute:[],
        },
        {
            id: 'nodeB',
            type: 'task',
            name: '实体B',
            left: '351px',
            top: '96px',
            ico: 'el-icon-goods',
            state: 'error',
            attribute:[],
        },
        {
            id: 'nodeC',
            name: '实体C',
            type: 'task',
            left: '354px',
            top: '351px',
            ico: 'el-icon-present',
            state: 'warning',
            attribute:[],
        }, {
            id: 'nodeD',
            name: '实体D',
            type: 'task',
            left: '723px',
            top: '215px',
            ico: 'el-icon-present',
            state: 'running',
            attribute:[],
        }
    ],
    lineList: [{
        from: 'nodeA',
        to: 'nodeB',
        label: '关系1',
        attribute:[],
    }, {
        from: 'nodeB',
        to: 'nodeC',
        label: '关系2',
        attribute:[],
    }, {
        from: 'nodeB',
        to: 'nodeD',
        label: '关系3',
        attribute:[],
    }, {
        from: 'nodeC',
        to: 'nodeD',
        label: '关系4',
        attribute:[],
    }
    ]
}

export function getDataB () {
    return dataB
}
