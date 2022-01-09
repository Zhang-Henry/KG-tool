let dataB = {
    name: '流程B',
    "nodeList": [
        {
            "id": "0",
            "name": "Disease",
            "type": "task",
            "left": "79px",
            "top": "228px",
            "ico": "el-icon-star-on",
            "state": "success",
            "attribute": ["prevent","get_prob","symptom","acompany","cure_lasttime","cause","cured_prob","category","easy_get","desc"],
        },
        {
            "id": "1",
            "name": "Drug",
            "type": "task",
            "left": "81px",
            "top": "72px",
            "ico": "el-icon-circle-plus",
            "state": "success",
            "attribute": []
        },
        {
            "id": "2",
            "name": "Department",
            "type": "task",
            "left": "411px",
            "top": "361px",
            "ico": "el-icon-circle-plus",
            "state": "success",
            "attribute": []
        },
        {
            "id": "3",
            "name": "Symptom",
            "type": "task",
            "left": "419px",
            "top": "226px",
            "ico": "el-icon-circle-plus",
            "state": "success",
            "attribute": []
        },
        {
            "id": "4",
            "name": "Food",
            "type": "task",
            "left": "91px",
            "top": "426px",
            "ico": "el-icon-circle-plus",
            "state": "success",
            "attribute": []
        },
        {
            "id": "5",
            "name": "Check_item",
            "type": "task",
            "left": "418px",
            "top": "116px",
            "ico": "el-icon-circle-plus",
            "state": "success",
            "attribute": []
        }
    ],
    "lineList": [
        {
            "lineId": "0",
            "from": "0",
            "to": "1",
            "attribute": [],
            "label": "recommand_drug"
        },
        {
            "lineId": "1",
            "from": "0",
            "to": "1",
            "attribute": [],
            "label": "recommand_eat"
        },
        {
            "lineId": "2",
            "from": "0",
            "to": "4",
            "attribute": [],
            "label": "recommand_eat"
        },
        {
            "lineId": "3",
            "from": "0",
            "to": "4",
            "attribute": [],
            "label": "do_eat"
        },
        {
            "lineId": "4",
            "from": "0",
            "to": "4",
            "attribute": [],
            "label": "not_eat"
        },
        {
            "lineId": "5",
            "from": "0",
            "to": "5",
            "attribute": [],
            "label": "check"
        },
        {
            "lineId": "6",
            "from": "0",
            "to": "3",
            "attribute": [],
            "label": "symptom"
        },
        {
            "lineId": "7",
            "from": "0",
            "to": "2",
            "attribute": [],
            "label": "cure_department"
        }
    ]
}

export function getDataB () {
    return dataB
}
