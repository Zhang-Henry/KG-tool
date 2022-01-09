//state
let state = {
    isShow: true,  //是否显示
    fileName: ''
}

//getters
let getters = {
    //这里说下我见过的三种形式，以name属性为例

    //第一种形式
    getFileName(state) {
        return state.fileName
    },
    //第二种形式
    
}

//mutations，以isShow属性为例
let mutations = {
    changeShow(state) {
        state.isShow = !state.isShow
    },
    changeName(state, data) {
        state.name = data
    }
}

//ctions
let actions = {
    //这里有两种写法，本质上一样
    //写法1，无参
    asChangeShow(context) {
        context.commit('changeShow')
    },
    //写法2，无参
    // asChangeShow({ commit }) {
    //     commit('changeShow')
    // }

    //有参
    asChangeName({ commit }, data) {
        commit('changeName', data)
    }
}

//导出模块
export default {
    namespaced: true,//是否开启模块
    //键和值相同时可以简写
    state,
    getters,
    mutations,
    actions
}
