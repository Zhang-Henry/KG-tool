graph_info = {
    "name": "流程B",
    "nodeList": [
        {
            "id": "nodeA",
            "name": "Disease",
            "type": "task",
            "left": "108px",
            "top": "132px",
            "ico": "el-icon-user-solid",
            "state": "success",
            "attribute": []
        },
        {
            "id": "6og21qnw4s",
            "name": "Drug",
            "type": "timer",
            "left": "114px",
            "top": "279px",
            "ico": "el-icon-circle-plus",
            "state": "success",
            "attribute": []
        },
        {
            "id": "kwmdm4xwhk",
            "name": "Drug",
            "type": "timer",
            "left": "103.827px",
            "top": "29.5568px",
            "ico": "el-icon-circle-plus",
            "state": "success",
            "attribute": []
        }
    ],
    "lineList": [
        {},
        {
            "lineId": "con_7",
            "from": "nodeA",
            "to": "6og21qnw4s",
            "attribute": [],
            "label": "not_eat"
        },
        {
            "lineId": "con_24",
            "from": "nodeA",
            "to": "6og21qnw4s",
            "attribute": [],
            "label": "do_eat"
        },
        {
            "lineId": "con_41",
            "from": "nodeA",
            "to": "kwmdm4xwhk",
            "attribute": [],
            "label": "recommand_drug"
        }
    ]
}
