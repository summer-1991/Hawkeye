<template>
    <div class="manualSet" v-loading="this.loading">
        <el-form :inline="true" class="demo-form-inline search-style" size="small">
            <el-form-item label="用例名称">
                <el-input placeholder="请输入" v-model="form.caseName" clearable style="width: 150px">
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="handleCurrentChange(1)">搜索</el-button>
                <el-button type="primary" @click.native="initData()">新建用例</el-button>
                <el-button type="primary" @click.native="initImport()" v-if="role == 2">导入用例</el-button>
            </el-form-item>
        </el-form>
        <el-tabs v-model="numTab" class="table_padding" @tab-click="tabChange">
            <el-tab-pane label="测试集" name="first">
                <el-row>
                    <el-col :span="3"
                            style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
                        <el-row>
                            <el-col style="border:1px solid;border-color: #ffffff #ffffff rgb(234, 234, 234) #ffffff;padding:2px">
                                <el-dropdown @command="moduleCommand" style="float:right;">
                                      <span class="el-dropdown-link" style="color: #4ae2d5">
                                        操作<i class="el-icon-arrow-down el-icon--right"></i>
                                      </span>
                                    <el-dropdown-menu slot="dropdown">
                                        <el-dropdown-item command="add">添加</el-dropdown-item>
                                        <el-dropdown-item command="edit">编辑</el-dropdown-item>
                                        <el-dropdown-item command="del">删除</el-dropdown-item>
                                    </el-dropdown-menu>
                                </el-dropdown>
                            </el-col>
                        </el-row>
                        <el-row>
                            <el-scrollbar wrapStyle="height:720px;">
                                <el-tree
                                        ref="testTree"
                                        @node-click="treeClick"
                                        class="filter-tree"
                                        highlight-current
                                        node-key="moduleId"
                                        :data="moduleDataList"
                                        :props="defaultProps"

                                >
                                </el-tree>
                            </el-scrollbar>
                            <el-pagination
                                    small
                                    @current-change="handleModuleCurrentChange"
                                    :current-page="modulePage.currentPage"
                                    :page-size="30"
                                    layout="prev, pager, next"
                                    :total="modulePage.total">
                            </el-pagination>
                        </el-row>
                    </el-col>

                    <el-col :span="21" style="padding-left: 5px;">
                        <el-table
                                ref="caseMultipleTable"
                                @selection-change="handleManualCaseSelection"
                                :data="caseTableData"
                                stripe
                                max-height="725">
                            <el-table-column
                                    type="selection"
                                    width="45">
                            </el-table-column>
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="name"
                                    label="用例名称"
                                    width="200">
                            </el-table-column>
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="create_by"
                                    label="创建人">
                            </el-table-column>
                            <el-table-column label="用例类型">
                                <template slot-scope="scope">
                                    <el-tag size="small">
                                        {{caseTypeShow(caseTableData[scope.$index]['case_type'])}}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="desc"
                                    label="用例描述">
                            </el-table-column>
                            <el-table-column
                                    label="操作"
                                    width="320">
                                <template slot-scope="scope">
                                    <el-button type="primary" icon="el-icon-view" size="mini"
                                               @click.native="viewCaseApi(caseTableData[scope.$index]['id'],caseTableData[scope.$index]['name'])">
                                        查看
                                    </el-button>
                                    <el-button type="primary" icon="el-icon-edit" size="mini"
                                               @click.native="editCopyCaseApi(caseTableData[scope.$index]['id'],'edit')">
                                        编辑
                                    </el-button>
                                    <el-button type="primary" icon="el-icon-tickets" size="mini"
                                               @click.native="editCopyCaseApi(caseTableData[scope.$index]['id'],'copy')">
                                        复制
                                    </el-button>
                                    <el-button type="danger" icon="el-icon-delete" size="mini"
                                               @click.native="sureView(delApi,caseTableData[scope.$index]['id'],caseTableData[scope.$index]['name'])">
                                        删除
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <el-button @click="cancelCaseSelection()" size="mini" style="margin-top: 2px;">
                            取消选择
                        </el-button>
                        <el-select
                                v-model="manualTaskId"
                                placeholder="快速添加到测试任务"
                                size="mini"
                                style="padding-left:10px;margin-top: 2px;">
                            <el-option
                                    v-for="item in manualTaskList"
                                    :key="item.task_id"
                                    :label="item.task_name"
                                    :value="item.task_id">
                            </el-option>
                        </el-select>
                        <el-button @click="addManualCaseToTask()" size="mini" style="margin-top: 2px;">添加</el-button>
                        <div class="pagination">
                            <el-pagination
                                    @current-change="handleCurrentChange"
                                    @size-change="handleSizeChange"
                                    :current-page="casePage.currentPage"
                                    :page-size="casePage.sizePage"
                                    layout="total, sizes, prev, pager, next, jumper"
                                    :total="casePage.total">
                            </el-pagination>
                        </div>
                    </el-col>
                </el-row>
            </el-tab-pane>
            <el-tab-pane label="用例编辑" name="second" v-show="caseEditViewStatus"
                         style="min-height: 760px">
                <manualCase
                        :projectId="form.projectId"
                        :moduleId="form.module.moduleId"
                        :proModelData="proModelData"
                        ref="caseFunc"></manualCase>
            </el-tab-pane>
            <el-tab-pane label="导入用例" name="third" v-show="importStatus"
                         style="min-height: 760px" v-if="role == 2">
                <manualImport
                        :projectId="form.projectId"
                        :moduleId="form.module.moduleId"
                        :proModelData="proModelData"
                        ref="importFunc"></manualImport>
            </el-tab-pane>
        </el-tabs>

        <el-dialog title="测试集配置" :visible.sync="moduleData.viewStatus" width="30%">
            <el-form>
                <el-form-item label="测试集名称" label-width="100px">
                    <el-input v-model="moduleData.name">
                    </el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button size="small" @click="moduleData.viewStatus = false">取 消</el-button>
                <el-button type="primary" size="small" @click.native="addModule()">确 定</el-button>
            </div>
        </el-dialog>

        <el-drawer
                id="el-drawer"
                :title="'用例详情：'+dialogTitle"
                :visible.sync="caseViewStatus"
                :before-close="handleClose"
                :size="'40%'">
            <el-button-group style="position: absolute;top: 17px;right: 60px;">
                <el-button type="primary" icon="el-icon-arrow-left" round size="mini"
                           @click="switchManualCase('pre')"></el-button>
                <el-button type="primary" round size="mini" @click="switchManualCase('next')"><i
                        class="el-icon-arrow-right el-icon--right"></i></el-button>
            </el-button-group>
            <div>
                <table border="1" cellspacing="0" cellpadding="0" style="width: 95%;margin: 10px;table-layout: fixed">
                    <tr>
                        <th style="width: 25%;">前提条件</th>
                        <td style="word-wrap: break-word;word-break: break-all">
                            <template>
                                <div v-html='viewTableData.precondition'></div>
                            </template>
                        </td>
                    </tr>
                    <tr>
                        <th>执行步骤</th>
                        <td style="word-wrap: break-word;word-break: break-all">
                            <template>
                                <div v-html='viewTableData.steps'></div>
                            </template>
                        </td>
                    </tr>
                    <tr>
                        <th>期望结果</th>
                        <td style="word-wrap: break-word;word-break: break-all">
                            <template>
                                <div v-html='viewTableData.expect'></div>
                            </template>
                        </td>
                    </tr>
                </table>
            </div>
        </el-drawer>
    </div>
</template>

<script>
    import manualCase from '@/components/projectView/manualManage/manualCase'
    import manualImport from '@/components/projectView/manualManage/manualImport'

    export default {
        name: 'manualSet',
        components: {
            manualCase: manualCase,
            manualImport: manualImport
        },
        data() {
            return {
                caseEditViewStatus: false,//  接口配置组件显示控制
                caseViewStatus: false,
                importStatus: false,
                dialogTitle: "",
                numTab: 'first',  //  tab页的显示
                loading: false,  //  页面加载状态开关
                proModelData: Object(),
                caseTableData: Array(),
                moduleDataList: [],
                role: '',
                viewTableData: {
                    precondition: '',
                    steps: '',
                    expect: '',
                },
                selectCaseList: Array(),
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                manualTaskList: [],
                manualTaskId: '',
                casePage: {
                    total: 1,
                    currentPage: 1,
                    sizePage: 20,
                },
                modulePage: {
                    total: 1,
                    currentPage: 1,
                    sizePage: 30,
                },
                moduleData: {
                    viewStatus: false,
                    id: '',
                    num: '',
                    name: '',
                },
                form: {
                    module: {
                        name: '',
                        moduleId: '',
                        num: '',
                    },
                    projectId: -1,
                    caseName: null,
                },
                previousId: 0,
                nextId: 0,
                caseTypeList: ['最高', '较高', '一般', '较低', '最低'],
                features: 'ManualSet'
            }
        },
        methods: {
            initBaseData() {
                this.form.module = {name: null, moduleId: null,};
                this.modulePage.currentPage = 1;
                this.casePage.currentPage = 1;
                this.manualTaskId = '';
                this.findModule();
            },
            moduleCommand(command) {
                //  模块处理函数，根据命令执行不同操作
                if (command === 'add') {
                    this.initModuleData()
                } else if (command === 'edit') {
                    this.editModule()
                } else if (command === 'del') {
                    this.sureView(this.delModule, null, this.form.module.name)
                }
            },
            handleCurrentChange(val) {
                this.casePage.currentPage = val;
                this.findCase();
            },
            caseTypeShow(case_type) {
                return this.caseTypeList[case_type]
            },
            initData() {
                if (!this.form.module.moduleId) {
                    this.$message({
                        showClose: true,
                        message: '请先创建测试集',
                        type: 'warning',
                    });
                    return
                }
                this.caseEditViewStatus = true;
                this.numTab = 'second';
                setTimeout(() => {
                    this.$refs.caseFunc.initCaseData();
                }, 0)
            },
            tabChange(tab) {
                //  当tab切换到接口信息时，刷新列表
                if (tab.label === '测试集') {
                    this.findCase()
                }
            },
            handleSizeChange(val) {
                this.casePage.sizePage = val;
                this.findCase();

            },
            findCase() {
                if (this.form.module === null) {
                    this.$message({
                        showClose: true,
                        message: '请选择测试集',
                        type: 'warning',
                    });
                    return
                }
                this.$axios.post(this.$api.findManualCaseApi, {
                    'caseName': this.form.caseName,
                    'moduleId': this.form.module.moduleId,
                    'page': this.casePage.currentPage,
                    'sizePage': this.casePage.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.caseTableData = response.data['data'];
                            this.casePage.total = response.data['total'];
                            this.manualTaskList = response.data['manual_task'];
                            this.manualTaskId = '';
                        }
                    }
                )
            },
            viewCaseApi(caseId, caseName) {
                //  编辑或者复制接口信息
                this.caseViewStatus = true;
                this.$axios.post(this.$api.editAndCopyManualCaseApi, {
                    'caseId': caseId,
                    'setId': this.form.module.moduleId
                }).then((response) => {
                        this.dialogTitle = response.data['data']['name'];
                        this.viewTableData.precondition = response.data['data']['precondition'];
                        this.viewTableData.steps = response.data['data']['steps'];
                        this.viewTableData.expect = response.data['data']['expect'];
                        this.previousId = response.data['previous_id'];
                        this.nextId = response.data['next_id'];
                    }
                )
            },
            switchManualCase(type) {
                if (type == "pre") {
                    if (this.previousId == 0) {
                        this.$message({
                            showClose: true,
                            message: '已经是第一条了！',
                            type: 'warning',
                        });
                        return
                    }
                    this.viewCaseApi(this.previousId, "")
                }
                else {
                    if (this.nextId == 0) {
                        this.$message({
                            showClose: true,
                            message: '已经是最后一条了！',
                            type: 'warning',
                        });
                        return
                    }
                    this.viewCaseApi(this.nextId, "")
                }
            },
            editCopyCaseApi(caseId, status) {
                //  编辑或者复制接口信息
                this.caseEditViewStatus = true;
                this.numTab = 'second';
                setTimeout(() => {
                    this.$refs.caseFunc.editCopyCaseApi(caseId, status);
                }, 0)
            },
            handleManualCaseSelection(val) {
                this.selectCaseList = val;
            },
            cancelCaseSelection() {
                this.$refs.caseMultipleTable.clearSelection();
            },
            addManualCaseToTask() {
                if (this.selectCaseList.length === 0) {
                    this.$message({
                        showClose: true,
                        message: '请勾选用例进行添加',
                        type: 'warning',
                    });
                    return
                }

                if (this.manualTaskId === '') {
                    this.$message({
                        showClose: true,
                        message: '请选择测试任务',
                        type: 'warning',
                    });
                    return
                }

                let caseIds = [];
                for (let i = 0; i < this.selectCaseList.length; i++) {
                    caseIds.push(this.selectCaseList[i]['id'])
                }

                this.$axios.post(this.$api.addCaseToTaskApi, {
                    'caseIds': caseIds,
                    'moduleId': this.manualTaskId
                }).then((response) => {
                        this.messageShow(this, response)
                    }
                )

            },
            delApi(caseId) {
                //  删除接口信息
                this.$axios.post(this.$api.delManualCaseApi, {'caseId': caseId}).then((response) => {
                        this.messageShow(this, response);
                        this.form.caseName = null;
                        if ((this.casePage.currentPage - 1) * this.casePage.sizePage + 1 === this.casePage.total) {
                            this.casePage.currentPage = this.casePage.currentPage - 1
                        }
                        this.findCase();
                    }
                )
            },
            findModule() {
                //  查询接口模块
                this.$axios.post(this.$api.findModuleApi, {
                    'projectId': this.form.projectId,
                    'page': this.modulePage.currentPage,
                    'sizePage': this.modulePage.sizePage,
                    'features': this.features
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.moduleDataList = response.data['data'];
                            this.modulePage.total = response.data['total'];
                            this.proModelData = response.data['all_module'];
                            this.role = response.data['role'];
                            if (this.moduleDataList.length !== 0) {
                                this.form.module = this.moduleDataList[0];
                                this.$nextTick(function () {
                                    this.$refs.testTree.setCurrentKey(this.form.module.moduleId);  //"vuetree"是你自己在树形控件上设置的 ref="vuetree" 的名称
                                });
                                this.findCase();
                            } else {
                                this.caseTableData = []
                            }
                        }
                    }
                )
            },
            treeClick(data) {
                //  点击节点时，初始化数据并获取对应的接口信息
                let index = this.moduleDataList.map(item => item.moduleId).indexOf(data['moduleId']);  //  获取当前节点的下标
                this.form.module = this.moduleDataList[index];
                this.casePage.currentPage = 1;
                this.findCase();
            },
            handleModuleCurrentChange(val) {
                this.modulePage.currentPage = val;
                this.findModule()
            },
            initModuleData() {
                //  打开窗口时，初始化模块窗口数据
                this.moduleData.name = '';
                this.moduleData.id = '';
                this.moduleData.num = '';
                this.moduleData.viewStatus = true;
            },
            editModule() {
                //  编辑模块
                if (!this.form.module) {
                    this.$message({
                        showClose: true,
                        message: '请先创建接口模块',
                        type: 'warning',
                    });
                    return
                }
                this.moduleData.name = this.form.module.name;
                this.moduleData.id = this.form.module.moduleId;
                this.moduleData.num = this.form.module.num;
                this.moduleData.viewStatus = true;
            },
            addModule() {
                //  添加模块
                this.$axios.post(this.$api.addModuleApi, {
                    'projectId': this.form.projectId,
                    'name': this.moduleData.name,
                    'id': this.moduleData.id,
                    'num': this.moduleData.num,
                    'features': this.features
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.moduleData.viewStatus = false;
                            this.findModule();
                        }
                    }
                )
            },
            delModule() {
                //  删除模块
                this.$axios.post(this.$api.delModuleApi, {
                    'id': this.form.module.moduleId,
                    'features': this.features
                }).then((response) => {
                        this.messageShow(this, response);
                        this.moduleData.name = '';
                        if ((this.modulePage.currentPage - 1) * this.modulePage.sizePage + 1 === this.modulePage.total) {
                            this.modulePage.currentPage = this.modulePage.currentPage - 1
                        }
                        this.findModule();
                    }
                )
            },
            initImport() {
                if (!this.form.module.moduleId) {
                    this.$message({
                        showClose: true,
                        message: '请先创建测试集',
                        type: 'warning',
                    });
                    return
                }

                this.importStatus = true;
                this.numTab = 'third';
                setTimeout(() => {
                    this.$refs.importFunc.initImportData();
                }, 0)
            },
        },
        mounted() {
            this.initBaseData();
        },
    }
</script>
<style>
    :focus {
        outline: none;
    }

    .el-drawer__body {
        overflow: scroll;
    }
</style>