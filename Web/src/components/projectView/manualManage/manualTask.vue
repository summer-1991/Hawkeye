<template>
    <div class="manualTask" v-loading="this.loading">
        <el-form :inline="true" class="demo-form-inline search-style" size="small">
            <el-form-item label="用例名称">
                <el-input placeholder="请输入" v-model="form.caseName" clearable style="width: 150px">
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="handleCurrentChange(1)">搜索</el-button>
                <el-button type="primary" @click.native="initData()">选择用例</el-button>
            </el-form-item>
        </el-form>
        <el-tabs v-model="numTab" class="table_padding">
            <el-tab-pane label="测试任务" name="first">
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
                                :data="caseTableData"
                                stripe
                                max-height="725">
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="name"
                                    label="用例名称"
                                    width="200">
                            </el-table-column>
                            <el-table-column
                                    prop="desc"
                                    label="用例描述">
                            </el-table-column>
                            <el-table-column
                                    prop="count"
                                    label="执行次数">
                            </el-table-column>
                            <el-table-column label="用例类型">
                                <template slot-scope="scope">
                                    <el-tag size="small">
                                        {{caseTypeShow(caseTableData[scope.$index]['case_type'])}}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column
                                    prop="last_by"
                                    label="最新执行人">
                            </el-table-column>
                            <el-table-column label="最新执行结果">
                                <template slot-scope="scope">
                                    <el-tag size="small"
                                            :type="caseTableData[scope.$index]['last_res'] === 0 ?
                                    'info' : caseTableData[scope.$index]['last_res'] === 1 ?
                                     'success' :  caseTableData[scope.$index]['last_res'] === 2 ?
                                     'warning' : caseTableData[scope.$index]['last_res'] === 3 ? 'danger':'primary'">
                                        {{resultShow(caseTableData[scope.$index]['last_res'])}}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column
                                    prop="last_desc"
                                    label="最新执行描述">
                            </el-table-column>
                            <el-table-column
                                    label="操作"
                                    width="320">
                                <template slot-scope="scope">
                                    <el-button type="primary" icon="el-icon-edit" size="mini"
                                               @click.native="runCaseApi(caseTableData[scope.$index]['id'],caseTableData[scope.$index]['name'])">
                                        执行
                                    </el-button>
                                    <el-button type="danger" icon="el-icon-delete" size="mini"
                                               @click.native="sureView(delApi,caseTableData[scope.$index]['id'],caseTableData[scope.$index]['name'])">
                                        删除
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
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
        </el-tabs>

        <el-dialog title="测试任务配置" :visible.sync="moduleData.viewStatus" width="30%">
            <el-form>
                <el-form-item label="测试任务名称" label-width="100px">
                    <el-input v-model="moduleData.name">
                    </el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button size="small" @click="moduleData.viewStatus = false">取 消</el-button>
                <el-button type="primary" size="small" @click.native="addModule()">确 定</el-button>
            </div>
        </el-dialog>

        <el-dialog title="用例选择" :visible.sync="searchStatus" width="50%">
            <el-form :inline="true" class="" size="small">
                <el-form-item label="测试集">
                    <el-select v-model="searchForm.manualSet"
                               id="set"
                               placeholder="请选择测试集"
                               size="small"
                               style="width: 200px;padding-right:10px" multiple>
                        <el-option
                                v-for="(item) in manualSetData"
                                :key="item.set_id"
                                :label="item.set_name"
                                :value="item.set_id">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="用例名称">
                    <el-input placeholder="请输入" v-model="searchForm.caseName" clearable style="width: 150px">
                    </el-input>
                </el-form-item>
                <el-form-item label="类型">
                    <el-select v-model="searchForm.caseType"
                               placeholder="请选择测试集"
                               size="small"
                               style="width: 200px;padding-right:10px" multiple>
                        <el-option
                                v-for="item in caseTypeList"
                                :key="item"
                                :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="创建人">
                    <el-select v-model="searchForm.createBy"
                               id="user" size="mini"
                               style="width: 100px" multiple>
                        <el-option
                                v-for="item in userData"
                                :key="item.user_id"
                                :label="item.user_name"
                                :value="item.user_id">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" icon="el-icon-search" @click.native="handleCaseSearchChange(1)">搜索
                    </el-button>
                    <el-button type="primary" icon="el-icon-plus" @click.native="addCaseToTask">添加
                    </el-button>
                </el-form-item>
            </el-form>
            <el-table
                    ref="caseMultipleTable"
                    @selection-change="handleCaseSelection"
                    :data="searchData">
                <el-table-column
                        type="selection"
                        width="45">
                </el-table-column>
                <el-table-column
                        prop="name"
                        label="用例名称"
                        width="180">
                </el-table-column>
                <el-table-column
                        prop="desc"
                        label="用例描述">
                </el-table-column>
                <el-table-column
                        prop="manual_set"
                        label="测试集">
                </el-table-column>
                <el-table-column
                        prop="create_by"
                        label="创建人">
                </el-table-column>
                <el-table-column
                        prop="case_type"
                        label="用例类型"
                        width="180">
                    <template slot-scope="scope">
                        <el-tag size="small">
                            {{caseTypeShow(searchData[scope.$index]['case_type'])}}
                        </el-tag>
                    </template>
                </el-table-column>
            </el-table>
            <el-button @click="cancelSelection()" size="mini" style="margin-top: 2px;">
                取消选择
            </el-button>
            <div class="pagination">
                <el-pagination
                        small
                        @current-change="handleCaseSearchChange"
                        :current-page="caseSearchPage.currentPage"
                        :page-size="caseSearchPage.sizePage"
                        layout="prev, pager, next"
                        :total="caseSearchPage.total">
                </el-pagination>
            </div>
        </el-dialog>

        <el-drawer
                id="el-drawer"
                :title="'用例执行：'+dialogTitle"
                :visible.sync="caseRunStatus"
                :before-close="handleClose"
                :size="'40%'">
            <el-button-group style="position: absolute;top: 17px;right: 60px;">
                <el-button type="primary" icon="el-icon-arrow-left" round size="mini"
                           @click="switchTaskManualCase('pre')"></el-button>
                <el-button type="primary" round size="mini" @click="switchTaskManualCase('next')"><i
                        class="el-icon-arrow-right el-icon--right"></i></el-button>
            </el-button-group>
            <div>
                <table border="1" cellspacing="0" cellpadding="0" style="width: 95%;margin: 10px;table-layout: fixed">
                    <tr>
                        <th style="width: 25%;">前提条件</th>
                        <td style="word-wrap: break-word;word-break: break-all">
                            <template>
                                <div v-html='runCaseData.precondition'></div>
                            </template>
                        </td>
                    </tr>
                    <tr>
                        <th>执行步骤</th>
                        <td style="word-wrap: break-word;word-break: break-all">
                            <template>
                                <div v-html='runCaseData.steps'></div>
                            </template>
                        </td>
                    </tr>
                    <tr>
                        <th>期望结果</th>
                        <td style="word-wrap: break-word;word-break: break-all">
                            <template>
                                <div v-html='runCaseData.expect'></div>
                            </template>
                        </td>
                    </tr>
                </table>
            </div>
            <el-form style="margin: 20px 10px;">
                <el-form-item label="执行结果">
                    <el-select v-model="runCaseData.runRes"
                               placeholder="请选择"
                               size="small"
                               style="padding-right:10px">
                        <el-option
                                v-for="item in resultList"
                                :key="item"
                                :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="备注">
                    <el-input type="textarea" :rows="2" v-model="runCaseData.runDesc"
                              placeholder="请输入">
                    </el-input>
                </el-form-item>
            </el-form>
            <div class="drawer_footer" style="margin: 20px;">
                <el-button type="primary" size="small" @click.native="updateRunCaseApi">确 定</el-button>
            </div>
        </el-drawer>
    </div>
</template>

<script>
    export default {
        name: "manualTask",
        data() {
            return {
                caseRunStatus: false,
                searchStatus: false,
                dialogTitle: "",
                numTab: 'first',  //  tab页的显示
                loading: false,  //  页面加载状态开关
                manualSetData: [],
                caseTableData: Array(),
                moduleDataList: [],
                userData: [],
                runCaseData: {
                    id: '',
                    precondition: '',
                    steps: '',
                    expect: '',
                    runRes: '',
                    runDesc: '',
                },
                caseList: Array(),
                searchData: Array(),
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                casePage: {
                    total: 1,
                    currentPage: 1,
                    sizePage: 20,
                },
                caseSearchPage: {
                    total: 1,
                    currentPage: 1,
                    sizePage: 10,
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
                searchForm: {
                    manualSet: '',
                    caseName: null,
                    createBy: '',
                    caseType: '',
                },
                previousId: 0,
                nextId: 0,
                caseTypeList: ['最高', '较高', '一般', '较低', '最低'],
                resultList: ['未执行', '成功', '失败', '阻塞', 'N/A'],
                features: 'ManualTask',
            }
        },
        methods: {
            initBaseData() {
                this.form.module = {name: null, moduleId: null,};
                this.modulePage.currentPage = 1;
                this.casePage.currentPage = 1;
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
            handleCaseSearchChange(val) {
                this.caseSearchPage.currentPage = val;
                this.findSearchCase();
            },
            caseTypeShow(case_type) {
                return this.caseTypeList[case_type]
            },
            resultShow(last_res) {
                return this.resultList[last_res]
            },
            initData() {
                if (!this.form.module.moduleId) {
                    this.$message({
                        showClose: true,
                        message: '请先创建测试任务',
                        type: 'warning',
                    });
                    return
                }
                this.caseSearchPage.total = 1;
                this.caseSearchPage.currentPage = 1;
                this.searchForm.manualSet = '';
                this.searchForm.caseName = null;
                this.searchForm.createBy = '';
                this.searchForm.caseType = '';
                this.searchData = Array();
                this.searchStatus = true;
            },
            handleSizeChange(val) {
                this.casePage.sizePage = val;
                this.findCase();

            },
            handleCaseSelection(val) {
                this.caseList = val;
            },
            cancelSelection() {
                this.$refs.caseMultipleTable.clearSelection();
            },
            findCase() {
                if (this.form.module === null) {
                    this.$message({
                        showClose: true,
                        message: '请选择测试任务',
                        type: 'warning',
                    });
                    return
                }
                this.$axios.post(this.$api.findTaskCaseApi, {
                    'caseName': this.form.caseName,
                    'moduleId': this.form.module.moduleId,
                    'page': this.casePage.currentPage,
                    'sizePage': this.casePage.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.caseTableData = response.data['data'];
                            this.casePage.total = response.data['total'];
                            this.userData = response.data['user_data'];
                            this.manualSetData = response.data['set_data'];
                        }
                    }
                )
            },
            findSearchCase() {
                let sel_type = this.searchForm.caseType;
                let caseType = [];
                for (let i = 0; i < sel_type.length; i++) {
                    caseType.push(this.caseTypeList.indexOf(sel_type[i]))
                }

                this.$axios.post(this.$api.searchCaseApi, {
                    'taskId': this.form.module.moduleId,
                    'manualSet': this.searchForm.manualSet,
                    'caseName': this.searchForm.caseName,
                    'createBy': this.searchForm.createBy,
                    'caseType': caseType,
                    'page': this.caseSearchPage.currentPage,
                    'sizePage': this.caseSearchPage.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.searchData = response.data['data'];
                            this.caseSearchPage.total = response.data['total'];
                        }
                    }
                )
            },
            addCaseToTask() {
                if (this.caseList.length === 0) {
                    this.$message({
                        showClose: true,
                        message: '请勾选用例进行添加',
                        type: 'warning',
                    });
                    return
                }

                let caseIds = [];
                for (let i = 0; i < this.caseList.length; i++) {
                    caseIds.push(this.caseList[i]['id'])
                }

                this.$axios.post(this.$api.addCaseToTaskApi, {
                    'caseIds': caseIds,
                    'moduleId': this.form.module.moduleId
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.searchStatus = false;
                            this.findCase();
                        }
                    }
                )
            },
            runCaseApi(taskCaseId, caseName) {
                this.caseRunStatus = true;
                this.$axios.post(this.$api.runManualCaseApi, {
                    'taskCaseId': taskCaseId,
                    'taskId': this.form.module.moduleId
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.dialogTitle = response.data['data']['name'];
                            this.runCaseData.id = response.data['data']['id'];
                            this.runCaseData.precondition = response.data['data']['precondition'];
                            this.runCaseData.steps = response.data['data']['steps'];
                            this.runCaseData.expect = response.data['data']['expect'];
                            this.runCaseData.runRes = this.resultList[response.data['data']['lastRes']];
                            this.runCaseData.runDesc = response.data['data']['runDesc'];
                            this.previousId = response.data['previous_id'];
                            this.nextId = response.data['next_id'];
                        }
                    }
                )
            },
            switchTaskManualCase(type) {
                if (type == "pre") {
                    if (this.previousId == 0) {
                        this.$message({
                            showClose: true,
                            message: '已经是第一条了！',
                            type: 'warning',
                        });
                        return
                    }
                    this.runCaseApi(this.previousId, "")
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
                    this.runCaseApi(this.nextId, "")
                }
            },
            updateRunCaseApi() {
                if (this.runCaseData.length > 1) {
                    this.$message({
                        showClose: true,
                        message: '后台错误，请刷新页面',
                        type: 'warning',
                    });
                    return
                }

                this.$axios.post(this.$api.runManualCaseApi, {
                    'taskCaseId': this.runCaseData.id,
                    'runDesc': this.runCaseData.runDesc,
                    'runRes': this.resultList.indexOf(this.runCaseData.runRes)
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.caseRunStatus = false;
                            this.runCaseData.id = '';
                            this.runCaseData.precondition = '';
                            this.runCaseData.steps = '';
                            this.runCaseData.expect = '';
                            this.runCaseData.runRes = '';
                            this.runCaseData.runDesc = '';
                            this.findCase();
                        }
                    }
                )
            },
            delApi(taskCaseId) {
                //  删除接口信息
                this.$axios.post(this.$api.delTaskCaseApi, {'taskCaseId': taskCaseId}).then((response) => {
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
                            this.userData = response.data['user_data'];
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
                        this.form.module.moduleId = ' ';
                        this.findModule();
                    }
                )
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