<template>
    <div class="auth" v-loading="this.loading">
        <el-row>
            <el-col :span="4"
                    style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
                <el-row>
                    <el-scrollbar wrapStyle="height:720px;">
                        <el-tree
                                ref="testTree"
                                @node-click="treeClick"
                                class="filter-tree"
                                highlight-current
                                node-key="roleId"
                                :data="roleList"
                                :props="defaultProps"

                        >
                        </el-tree>
                    </el-scrollbar>
                    <el-pagination
                            small
                            @current-change="handleCurrentChange"
                            :current-page="rolePage.currentPage"
                            :page-size="30"
                            layout="prev, pager, next"
                            :total="rolePage.total">
                    </el-pagination>
                </el-row>
            </el-col>

            <el-col :span="20" style="padding-left: 5px;">
                <div v-for="(item1,key1) in auth" :key="key1">
                    <fieldset style="margin: 20px;">
                        <legend>{{item1.title}}</legend>
                        <table style="margin: 10px; width: 90%;">
                            <tr v-for="(item2,key2) in item1.manage" :key="key2">
                                <td style="width: 100px;">
                                    <el-checkbox :indeterminate="item2.isIndeterminate" v-model="item2.checked"
                                                 @change="handleCheckAllChange(key1,key2)">{{item2.title}}
                                    </el-checkbox>
                                </td>
                                <td>
                                    <el-checkbox v-for="(item3,key3) in item2.option" :key="key3"
                                                 v-model="item3.checked" style="margin: 5px;"
                                                 @change="handleCheckedChange(key1,key2)">
                                        {{item3.title}}
                                    </el-checkbox>
                                </td>
                            </tr>
                        </table>
                    </fieldset>
                </div>
                <el-button type="primary" size="small" @click="save" style="margin-left: 50px">保存</el-button>
            </el-col>
        </el-row>
    </div>
</template>

<script>
    export default {
        name: 'auth',
        components: {},
        data() {
            return {
                roleList: [],
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                rolePage: {
                    total: 1,
                    currentPage: 1,
                    sizePage: 30,
                },
                role: {
                    "name": "",
                    "roleId": 0,
                },
                auth: {},
            }
        },
        methods: {
            initBaseData() {
                this.rolePage.currentPage = 1;
                this.findRole();
            },
            initAuth(authData) {
                this.auth = {
                    "api": {
                        "title": "接口测试",
                        "manage": {
                            "api": {
                                "title": "API用例",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "录入接口信息", "checked": false},
                                    "todo": {"title": "操作", "checked": false},
                                    "run": {"title": "测试", "checked": false},
                                    "edit": {"title": "编辑", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                            "config": {
                                "title": "项目函数",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "添加配置", "checked": false},
                                    "edit": {"title": "编辑", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                            "func": {
                                "title": "函数文件",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "创建", "checked": false},
                                    "run": {"title": "调试", "checked": false},
                                    "save": {"title": "保存", "checked": false},
                                }
                            },
                            "project": {
                                "title": "项目管理",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "添加项目", "checked": false},
                                    "edit": {"title": "编辑", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                            "scene": {
                                "title": "业务用例",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "添加接口用例", "checked": false},
                                    "todo": {"title": "操作", "checked": false},
                                    "edit": {"title": "编辑", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                    "run": {"title": "运行", "checked": false},
                                    "batch": {"title": "批量运行", "checked": false},
                                }
                            },
                            "sdk": {
                                "title": "SDK配置",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "添加客户端配置", "checked": false},
                                    "edit": {"title": "编辑", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                            "report": {
                                "title": "测试报告",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                            "task": {
                                "title": "定时任务",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "添加任务", "checked": false},
                                    "edit": {"title": "修改", "checked": false},
                                    "todo": {"title": "启动", "checked": false},
                                    "run": {"title": "单次运行", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                        }
                    },
                    "manual": {
                        "title": "功能测试",
                        "manage": {
                            "case": {
                                "title": "测试用例",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "todo": {"title": "操作", "checked": false},
                                    "save": {"title": "保存", "checked": false},
                                }
                            },
                        }
                    },
                    "others": {
                        "title": "其他程序",
                        "manage": {
                            "mind": {
                                "title": "脑图",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                }
                            },
                            "resources": {
                                "title": "测试资源",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "添加资源", "checked": false},
                                    "edit": {"title": "编辑", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                            "wiki": {
                                "title": "文档库",
                                "checked": false,
                                "isIndeterminate": false,
                                "option": {
                                    "view": {"title": "查看", "checked": false},
                                    "add": {"title": "新建文档", "checked": false},
                                    "todo": {"title": "操作", "checked": false},
                                    "edit": {"title": "编辑", "checked": false},
                                    "del": {"title": "删除", "checked": false},
                                }
                            },
                        }
                    }
                };
                for (let iKey in authData) {
                    if (iKey in this.auth) {
                        const manageTemp = authData[iKey]['manage'];
                        const mange = this.auth[iKey]['manage'];
                        for (let jKey in manageTemp) {
                            if (jKey in mange) {
                                mange[jKey] = manageTemp[jKey]
                            }
                        }
                    }
                }
            },
            findRole() {
                this.$axios.post(this.$api.findRoleApi, {
                    'page': this.rolePage.currentPage,
                    'sizePage': this.rolePage.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.roleList = response.data['data'];
                            this.rolePage.total = response.data['total'];
                            this.role = this.roleList[0];
                            this.$nextTick(function () {
                                this.$refs.testTree.setCurrentKey(this.role.roleId);  //"vuetree"是你自己在树形控件上设置的 ref="vuetree" 的名称
                            });
                            this.findAuth();
                        }
                    }
                )
            },
            treeClick(data) {
                let index = this.roleList.map(item => item.roleId).indexOf(data['roleId']);  //  获取当前节点的下标
                this.role = this.roleList[index];
                this.findAuth();
            },
            findAuth() {
                this.$axios.post(this.$api.findAuthApi, {
                    'roleId': this.role.roleId,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.initAuth(response.data["data"]);
                        }
                    }
                )
            },
            handleCurrentChange(val) {
                this.rolePage.currentPage = val;
                this.findRole()
            },
            handleCheckAllChange(key1, key2) {
                let manageTemp = this.auth[key1]["manage"];
                let optionTemp = manageTemp[key2]["option"];
                for (let i  in optionTemp) {
                    optionTemp[i]["checked"] = (manageTemp[key2]["checked"] == true) ? true : false;
                }
                manageTemp[key2]["isIndeterminate"] = false;
            },
            handleCheckedChange(key1, key2) {
                let manageTemp = this.auth[key1]["manage"];
                let optionTemp = manageTemp[key2]["option"];
                let len = Object.keys(optionTemp).length;
                let check = 0;
                for (let i  in optionTemp) {
                    if (optionTemp[i]["checked"] == true) {
                        check = check + 1;
                    }
                }
                if (check == 0) {
                    manageTemp[key2]["checked"] = false;
                    manageTemp[key2]["isIndeterminate"] = false;
                } else {
                    manageTemp[key2]["checked"] = true;
                    manageTemp[key2]["isIndeterminate"] = (len == check) ? false : true;
                }

            },
            save() {
                this.$axios.post(this.$api.addAuthApi, {
                    'roleId': this.role.roleId,
                    'auth': this.auth,
                }).then((response) => {
                        if (this.messageShow(this, response)) {

                        }
                    }
                )
            }
        },
        mounted() {
            this.initBaseData();
        },
    }
</script>

<style>

</style>