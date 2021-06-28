<template>
    <div class="test_resource" v-loading="this.loading">
        <el-form :inline="true" class="demo-form-inline search-style" size="small">
            <el-form-item label="资源名称">
                <el-input placeholder="请输入" v-model="form.resourceName" clearable style="width: 150px">
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="findResource()">搜索</el-button>
                <el-button type="primary" @click.native="addResource()"
                           v-show="role === '2' || auth.others_resources_add">添加资源
                </el-button>
            </el-form-item>
        </el-form>
        <el-tabs v-model="numTab" class="table_padding" @tab-click="tabChange">
            <el-tab-pane label="手机资源" name="first">
                <el-row>
                    <el-col :span="24" style="padding-left: 5px;">
                        <el-table
                                :data="resourceTableData"
                                stripe
                                max-height="725">
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="name"
                                    label="型号"
                                    width="300">
                            </el-table-column>
                            <el-table-column
                                    prop="desc"
                                    label="描述">
                            </el-table-column>
                            <el-table-column
                                    prop="version"
                                    label="版本">
                            </el-table-column>
                            <el-table-column
                                    prop="borrower"
                                    label="借用人">
                            </el-table-column>
                            <el-table-column
                                    label="操作">
                                <template slot-scope="scope">
                                    <el-button type="primary" icon="el-icon-edit" size="mini"
                                               @click.native="editResource(resourceTableData[scope.$index]['id'])"
                                               v-show="role === '2' || auth.others_resources_edit">
                                        编辑
                                    </el-button>
                                    <el-button type="danger" icon="el-icon-delete" size="mini"
                                               @click.native="sureView(delResource,resourceTableData[scope.$index]['id'],resourceTableData[scope.$index]['name'])"
                                               v-show="role === '2' || auth.others_resources_del">
                                        删除
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="pagination">
                            <el-pagination
                                    @current-change="handleCurrentChange"
                                    @size-change="handleSizeChange"
                                    :current-page="resourcePage.currentPage"
                                    :page-size="resourcePage.sizePage"
                                    layout="total, sizes, prev, pager, next, jumper"
                                    :total="resourcePage.total">
                            </el-pagination>
                        </div>
                    </el-col>
                </el-row>
            </el-tab-pane>
            <el-tab-pane label="账号资源" name="second">
                <el-row>
                    <el-col :span="24" style="padding-left: 5px;">
                        <el-table
                                :data="resourceTableData"
                                stripe
                                max-height="725">
                            <el-table-column
                                    :show-overflow-tooltip=true
                                    prop="name"
                                    label="账号名"
                                    width="300">
                            </el-table-column>
                            <el-table-column
                                    prop="version"
                                    label="账号密码">
                            </el-table-column>
                            <el-table-column
                                    prop="desc"
                                    label="描述">
                            </el-table-column>
                            <el-table-column
                                    label="操作">
                                <template slot-scope="scope">
                                    <el-button type="primary" icon="el-icon-edit" size="mini"
                                               @click.native="editResource(resourceTableData[scope.$index]['id'])"
                                               v-show="role === '2' || auth.others_resources_edit">
                                        编辑
                                    </el-button>
                                    <el-button type="danger" icon="el-icon-delete" size="mini"
                                               @click.native="sureView(delResource,resourceTableData[scope.$index]['id'],resourceTableData[scope.$index]['name'])"
                                               v-show="role === '2' || auth.others_resources_del">
                                        删除
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="pagination">
                            <el-pagination
                                    @current-change="handleCurrentChange"
                                    @size-change="handleSizeChange"
                                    :current-page="resourcePage.currentPage"
                                    :page-size="resourcePage.sizePage"
                                    layout="total, sizes, prev, pager, next, jumper"
                                    :total="resourcePage.total">
                            </el-pagination>
                        </div>
                    </el-col>
                </el-row>
            </el-tab-pane>
        </el-tabs>

        <el-dialog :title=dialogInfo.title :visible.sync="addStatus" width="30%">
            <el-form>
                <el-form-item :label="dialogInfo.name" label-width="80px">
                    <el-input v-model="resourceData.name">
                    </el-input>
                </el-form-item>
                <el-form-item :label="dialogInfo.desc" label-width="80px">
                    <el-input v-model="resourceData.desc" type="textarea">
                    </el-input>
                </el-form-item>
                <el-form-item :label="dialogInfo.version" label-width="80px">
                    <el-input v-model="resourceData.version">
                    </el-input>
                </el-form-item>
                <el-form-item :label="dialogInfo.borrower" label-width="80px" v-if="form.type == 0">
                    <el-input v-model="resourceData.borrower">
                    </el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button size="small" @click="addStatus = false">取 消</el-button>
                <el-button type="primary" size="small" @click.native="updateResource()">确 定</el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
    export default {
        name: 'testResource',
        data() {
            return {
                numTab: 'first',  //  tab页的显示
                loading: false,  //  页面加载状态开关
                addStatus: false,
                resourceTableData: Array(),
                resourcePage: {
                    total: 1,
                    currentPage: 1,
                    sizePage: 20,
                },
                form: {
                    projectId: -1,
                    resourceName: null,
                    type: 0,
                },
                resourceData: {
                    id: '',
                    name: '',
                    desc: '',
                    version: '',
                    borrower: '',
                    status: ''
                },
                dialogInfo: {
                    title: '',
                    name: '型号',
                    desc: '描述',
                    version: '版本',
                    borrower: '借用人',
                },
                role: '',
                auth: '',
            }
        },
        methods: {
            initData() {
                this.role = this.$store.state.roles;
                this.auth = JSON.parse(this.$store.state.auth);

                this.form.resourceName = null;
                this.resourcePage.currentPage = 1;
                this.findResource();
            },
            handleCurrentChange(val) {
                this.resourcePage.currentPage = val;
                this.findResource();
            },
            handleSizeChange(val) {
                this.resourcePage.sizePage = val;
                this.findResource();

            },
            tabChange(tab) {
                //  当tab切换到接口信息时，刷新列表
                if (tab.label === '手机资源') {
                    this.form.type = 0
                }
                else if (tab.label === '账号资源') {
                    this.form.type = 1
                }
                this.resourceTableData = [];
                this.resourcePage.currentPage = 1;
                this.findResource()
            },
            findResource() {
                this.$axios.post(this.$api.findResourceApi, {
                    'name': this.form.resourceName,
                    'type': this.form.type,
                    'page': this.resourcePage.currentPage,
                    'sizePage': this.resourcePage.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.resourceTableData = response.data['data'];
                            this.resourcePage.total = response.data['total'];
                        }
                    }
                )
            },
            addResource() {
                this.addStatus = true;
                this.dialogInfo.title = '添加资源';
                this.updateDialogInfo();

                this.resourceData.id = '';
                this.resourceData.name = '';
                this.resourceData.desc = '';
                this.resourceData.version = '';
                this.resourceData.borrower = '';
            },
            editResource(resourceId) {
                this.addStatus = true;
                this.dialogInfo.title = '修改资源';
                this.updateDialogInfo();

                this.$axios.post(this.$api.editResourceApi, {
                    'resourceId': resourceId,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.resourceData.id = response.data['data']['id'];
                            this.resourceData.name = response.data['data']['name'];
                            this.resourceData.desc = response.data['data']['desc'];
                            this.resourceData.version = response.data['data']['version'];
                            this.resourceData.borrower = response.data['data']['borrower'];
                        }
                    }
                )
            },
            updateDialogInfo() {
                if (this.form.type == 0) {
                    this.dialogInfo.name = '型号';
                    this.dialogInfo.desc = '描述';
                    this.dialogInfo.version = '版本';
                    this.dialogInfo.borrower = '借用人';
                } else {
                    this.dialogInfo.name = '账号';
                    this.dialogInfo.desc = '描述';
                    this.dialogInfo.version = '密码';
                    this.dialogInfo.borrower = '';
                }
            },
            updateResource() {
                if (this.resourceData.name == '') {
                    this.$message({
                        showClose: true,
                        message: '型号/账号必须填写！',
                        type: 'warning',
                    });
                    return
                }
                this.$axios.post(this.$api.addResourceApi, {
                    'resourceId': this.resourceData.id,
                    'resourceType': this.form.type,
                    'name': this.resourceData.name,
                    'desc': this.resourceData.desc,
                    'version': this.resourceData.version,
                    'borrower': this.resourceData.borrower,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.addStatus = false;
                            this.findResource();
                        }
                    }
                )
            },
            delResource(resourceId) {
                this.$axios.post(this.$api.delResourceApi, {
                    'resourceId': resourceId,
                }).then((response) => {
                        this.messageShow(this, response);
                        if ((this.resourcePage.currentPage - 1) * this.resourcePage.sizePage + 1 === this.resourcePage.total) {
                            this.resourcePage.currentPage = this.resourcePage.currentPage - 1
                        }
                        this.findResource();
                    }
                )
            }
        },
        mounted() {
            this.initData();
        },
    }
</script>

<style scoped>

</style>