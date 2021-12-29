let dataB = {
    name: '流程B',
    nodeList: [
        {
            id: 'nodeA',
            name: 'Film',
            type: 'task',
            left: '18px',
            top: '223px',
            ico: 'el-icon-user-solid',
            state: 'success',
            attribute:['movie','director','boxOffice','releaseTime'],
        },
        {
            id: 'nodeB',
            type: 'task',
            name: 'Person',
            left: '351px',
            top: '96px',
            ico: 'el-icon-goods',
            state: 'error',
            attribute:['name','birthday','nationality','profession'],
        },
    ],
    lineList: [{
        from: 'nodeA',
        to: 'nodeB',
        label: '主演',
        attribute:[],
    }, 
    ]
}

export function getDataB () {
    return dataB
}
