<template>
    <div class="wiki" v-loading="this.loading">
        <el-form :inline="true" class="demo-form-inline search-style" size="small">
            <el-form-item label="文档名称">
                <el-input placeholder="请输入" v-model="form.wikiName" clearable style="width: 150px">
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="handleCurrentChange(1)">搜索</el-button>
                <el-button type="primary" @click.native="initData()">新建文档</el-button>
            </el-form-item>
        </el-form>
        <el-tabs v-model="numTab" class="table_padding" @tab-click="tabChange">
            <el-tab-pane label="文档库" name="first">
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
                                :data="wikiTableData"
                                stripe
                                max-height="725">
                            <el-table-column
                                    prop="num"
                                    label="编号"
                                    width="60">
                            </el-table-column>
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="name"
                                    label="文档名称"
                                    width="200">
                            </el-table-column>
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="desc"
                                    label="文档描述">
                            </el-table-column>
                            <el-table-column
                                    prop="create_by"
                                    label="创建人">
                            </el-table-column>
                            <el-table-column
                                    label="操作">
                                <template slot-scope="scope">
                                    <el-button type="primary" icon="el-icon-view" size="mini"
                                               @click.native="viewWikiApi(wikiTableData[scope.$index]['wikiId'],wikiTableData[scope.$index]['name'])">
                                        查看
                                    </el-button>
                                    <el-button type="primary" icon="el-icon-edit" size="mini"
                                               @click.native="editCopyWikiApi(wikiTableData[scope.$index]['wikiId'],'edit')">
                                        编辑
                                    </el-button>
                                    <el-button type="danger" icon="el-icon-delete" size="mini"
                                               @click.native="sureView(delApi,wikiTableData[scope.$index]['wikiId'],wikiTableData[scope.$index]['name'])">
                                        删除
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="pagination">
                            <el-pagination
                                    @current-change="handleCurrentChange"
                                    @size-change="handleSizeChange"
                                    :current-page="wikiPage.currentPage"
                                    :page-size="wikiPage.sizePage"
                                    layout="total, sizes, prev, pager, next, jumper"
                                    :total="wikiPage.total">
                            </el-pagination>
                        </div>
                    </el-col>
                </el-row>
            </el-tab-pane>
            <el-tab-pane label="文档编辑" name="second" v-show="wikiEditViewStatus"
                         style="min-height: 760px">
                <wikiEdit
                        :projectId="form.projectId"
                        :moduleId="form.module.moduleId"
                        :proModelData="proModelData"
                        :userData="userData"
                        @findWiki="findWiki"
                        ref="wikiFunc">
                </wikiEdit>
            </el-tab-pane>
        </el-tabs>

        <el-dialog title="文档库配置" :visible.sync="moduleData.viewStatus" width="30%">
            <el-form>
                <el-form-item label="文档库名称" label-width="100px">
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
                :title="'文档查看：'+dialogTitle"
                :visible.sync="wikiViewStatus"
                :before-close="handleClose"
                :size="'60%'">
            <template>
                <div v-html='wikiInfo' style="margin: 20px"></div>
            </template>
            <strong>附件</strong>
            <div id="annexDiv"></div>
        </el-drawer>
    </div>
</template>

<script>
    import wikiEdit from '@/components/wiki/wikiEdit'

    export default {
        name: 'wikiManage',
        components: {
            wikiEdit: wikiEdit,
        },
        data() {
            return {
                wikiEditViewStatus: false,//  接口配置组件显示控制
                wikiViewStatus: false,
                dialogTitle: "",
                wikiInfo: "",
                numTab: 'first',  //  tab页的显示
                loading: false,  //  页面加载状态开关
                proModelData: Object(),
                wikiTableData: Array(),
                moduleDataList: [],
                userData: [],
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                wikiPage: {
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
                    apiName: null,
                },
                features: 'DocLib'
            }
        },
        methods: {
            initBaseData() {
                this.form.module = {name: null, moduleId: null,};
                this.modulePage.currentPage = 1;
                this.wikiPage.currentPage = 1;
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
            tabChange(tab) {
                //  当tab切换到接口信息时，刷新列表
                if (tab.label === '文档库') {
                    this.findWiki()
                }
            },
            handleCurrentChange(val) {
                this.wikiPage.currentPage = val;
                this.findWiki();
            },
            initData() {
                if (!this.form.module.moduleId) {
                    this.$message({
                        showClose: true,
                        message: '请先创建接口模块',
                        type: 'warning',
                    });
                    return
                }
                this.wikiEditViewStatus = true;
                this.numTab = 'second';
                setTimeout(() => {
                    this.$refs.wikiFunc.initWikiData();
                }, 0)
            },
            handleSizeChange(val) {
                this.wikiPage.sizePage = val;
                this.findWiki();

            },
            findWiki() {
                if (this.form.module === null) {
                    this.$message({
                        showClose: true,
                        message: '请选择文档库',
                        type: 'warning',
                    });
                    return
                }
                this.$axios.post(this.$api.findWikiApi, {
                    'wikiName': this.form.wikiName,
                    'moduleId': this.form.module.moduleId,
                    'page': this.wikiPage.currentPage,
                    'sizePage': this.wikiPage.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.wikiTableData = response.data['data'];
                            this.wikiPage.total = response.data['total'];
                            this.userData = response.data['user_data'];
                        }
                    }
                )
            },
            viewWikiApi(wikiId, wikiName) {
                //  编辑或者复制接口信息
                this.wikiViewStatus = true;
                this.$axios.post(this.$api.editAndCopyWikiApi, {'wikiId': wikiId}).then((response) => {
                        this.dialogTitle = wikiName;
                        this.wikiInfo = response.data['data']['content'];
                        let annex_list = response.data['data']['annex_name'];
                        let ul_str = "<ul>";
                        for (let i = 0; i < annex_list.length; i++) {
                            let annex_name = annex_list[i]["name"];
                            let annex_url = annex_list[i]["url"];
                            let type = annex_name.split('.')[1];
                            if (type === 'doc' || type === 'docx' || type === 'xlsx' ||
                                type === 'xls' || type === 'ppt' || type === 'pptx'
                            ) {
                                ul_str = ul_str + "<li><a href='" + window.location.origin + annex_url + "'>" + annex_name + "</a></li>"
                            } else {
                                ul_str = ul_str + "<li><a href='" + window.location.origin + annex_url + "' target='_blank'>" + annex_name + "</a></li>"
                            }
                        }
                        ul_str = ul_str + "</ul>";
                        document.getElementById("annexDiv").innerHTML = ul_str;
                    }
                )
            },
            editCopyWikiApi(wikiId, status) {
                //  编辑或者复制接口信息
                this.wikiEditViewStatus = true;
                this.numTab = 'second';
                setTimeout(() => {
                    this.$refs.wikiFunc.editCopyWikiApi(wikiId, status);
                }, 0)
            },

            delApi(wikiId) {
                //  删除接口信息
                this.$axios.post(this.$api.delWikiApi, {'wikiId': wikiId}).then((response) => {
                        this.messageShow(this, response);
                        this.form.wikiName = null;
                        if ((this.wikiPage.currentPage - 1) * this.wikiPage.sizePage + 1 === this.wikiPage.total) {
                            this.wikiPage.currentPage = this.wikiPage.currentPage - 1
                        }
                        this.findWiki();
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
                            if (this.moduleDataList.length !== 0) {
                                this.form.module = this.moduleDataList[0];
                                this.$nextTick(function () {
                                    this.$refs.testTree.setCurrentKey(this.form.module.moduleId);  //"vuetree"是你自己在树形控件上设置的 ref="vuetree" 的名称
                                });
                                this.findWiki();
                            } else {
                                this.wikiTableData = []
                            }
                        }
                    }
                )
            },
            treeClick(data) {
                //  点击节点时，初始化数据并获取对应的接口信息
                let index = this.moduleDataList.map(item => item.moduleId).indexOf(data['moduleId']);  //  获取当前节点的下标
                this.form.module = this.moduleDataList[index];
                this.wikiPage.currentPage = 1;
                this.findWiki();
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
        },
        mounted() {
            this.initBaseData();
        },
    }
</script>

<style>
    .el-drawer__body {
        overflow: scroll;
    }

    :focus {
        outline: none;
    }
</style>
