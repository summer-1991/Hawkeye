<template>
    <div class="projectManage">

        <el-form :inline="true" class="demo-form-inline search-style" size="small">

            <el-form-item label="项目名称" labelWidth="110px">
                <el-input placeholder="请输入" v-model="form.projectName">
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="proHandleCurrentChange(1)">
                    搜索
                </el-button>
                <el-button type="primary" @click.native="initProjectData()"
                           v-if="role == '2' || auth.api_project_add">添加项目
                </el-button>
            </el-form-item>

        </el-form>
        <el-tabs value="first" style="padding-left: 10px">
            <el-tab-pane label="项目列表" name="first" class="table_padding">

                <el-table :data="tableData" stripe max-height="725">
                    <el-table-column
                            prop="id"
                            label="id"
                            width="80"
                    >
                    </el-table-column>
                    <el-table-column
                            prop="name"
                            label="项目名称"
                            width="150">
                    </el-table-column>
                    <el-table-column
                            prop="team_names"
                            label="团队成员">
                    </el-table-column>
                    <el-table-column
                            prop="principal"
                            label="负责人"
                            width="150">
                    </el-table-column>
                    <el-table-column
                            label="操作"
                    >
                        <template slot-scope="scope">
                            <el-button type="primary" icon="el-icon-edit" size="mini"
                                       @click.native="editProject(tableData[scope.$index]['id'])"
                                       v-if="role == '2' || auth.api_project_edit">编辑
                            </el-button>
                            <el-button type="danger" icon="el-icon-delete" size="mini"
                                       @click.native="sureView(delProject,tableData[scope.$index]['id'],tableData[scope.$index]['name'])"
                                       v-if="role == '2' || auth.api_project_del">
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <div class="pagination">
                    <el-pagination
                            @current-change="proHandleCurrentChange"
                            @size-change="proHandleSizeChange"
                            :current-page="currentPage"
                            :page-size="sizePage"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="this.total">
                    </el-pagination>
                </div>
            </el-tab-pane>
        </el-tabs>

        <el-dialog title="项目配置" :visible.sync="projectData.modelFormVisible" width="40%"
                   :modal-append-to-body="false"
                   :append-to-body="false"
                   :close-on-click-modal="false"
        >
            <el-tabs>
                <el-tab-pane label="基础信息" style="margin-top: 10px">
                    <el-form :inline="true">
                        <el-form-item label="项目名称" :label-width="projectData.formLabelWidth">
                            <el-input v-model="projectData.projectName" size="mini" id="project_name"
                                      style="width: 150px">
                            </el-input>
                        </el-form-item>
                        <el-form-item label="负责人" label-width="60px">
                            <el-select v-model="form.user" value-key="user_id" id="user" size="mini"
                                       style="width: 100px">
                                <el-option
                                        v-for="item in userData"
                                        :key="item.user_id"
                                        :label="item.user_name"
                                        :value="item">
                                </el-option>
                            </el-select>
                        </el-form-item>
                        <el-form-item label="团队成员" label-width="80px">
                            <el-select v-model="form.team_ids" id="team_ids" size="mini"
                                       style="width: 200px" multiple>
                                <el-option
                                        v-for="item in userData"
                                        :key="item.user_id"
                                        :label="item.user_name"
                                        :value="item.user_id">
                                </el-option>
                            </el-select>
                        </el-form-item>
                        <el-form-item label="函数文件" :label-width="projectData.formLabelWidth">
                            <el-select v-model="projectData.funcFile" placeholder="请选择导入函数文件" size="mini" clearable>
                                <el-option
                                        v-for="item in funcAddress"
                                        :key="item.value"
                                        :label="item.value"
                                        :value="item.value">
                                </el-option>
                            </el-select>
                        </el-form-item>

                    </el-form>
                    <hr style="height:1px;border:none;border-top:1px solid rgb(241, 215, 215);margin-top: -10px"/>
                    <el-tabs v-model="environmentChoice" type="card">
                        <el-tab-pane v-for="(host,env) in environment"
                                     :key="env"
                                     :label="environmentName[env]"
                                     :name="env"
                                     :value="host">
                            <el-table :data="host" size="mini" stripe :show-header="false">
                                <el-table-column property="value" label="Value" header-align="center" minWidth="200">
                                    <template slot-scope="scope">
                                        <el-input v-model="scope.row.value" size="mini"
                                                  placeholder="http://127.0.0.1:8010">
                                        </el-input>
                                    </template>
                                </el-table-column>
                                <el-table-column property="value" label="操作" header-align="center" width="50">
                                    <template slot-scope="scope">
                                        <el-button type="danger" icon="el-icon-delete" size="mini"
                                                   @click.native="delTableRow(env,scope.$index)">
                                        </el-button>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </el-tab-pane>
                    </el-tabs>
                </el-tab-pane>

                <el-tab-pane label="公用变量" style="margin-top: 10px">
                    <span style="margin-left: 10px">变量信息：</span>
                    <el-button type="primary" size="mini" @click="addProjectVariable()">
                        添加
                    </el-button>
                    <el-table :data="projectData.variable" stripe :show-header="false" size="mini">
                        <el-table-column label="Key" header-align="center" minWidth="50">
                            <template slot-scope="scope">
                                <el-input v-model="scope.row.key" size="mini" placeholder="key">
                                </el-input>
                            </template>
                        </el-table-column>
                        <el-table-column label="Value" header-align="center" minWidth="80">
                            <template slot-scope="scope">
                                <el-input v-model="scope.row.value" size="mini" placeholder="value">
                                </el-input>
                            </template>
                        </el-table-column>
                        <el-table-column label="备注" header-align="center" width="150">
                            <template slot-scope="scope">
                                <el-input v-model="scope.row.remark" size="mini" placeholder="备注">
                                </el-input>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" header-align="center" width="80">
                            <template slot-scope="scope">
                                <el-button type="danger" icon="el-icon-delete" size="mini"
                                           @click.native="delProjectVariable(scope.$index)">删除
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                    <hr style="height:1px;border:none;border-top:1px solid rgb(241, 215, 215);"/>

                    <!--<div style="margin-top: 10px">-->
                    <!--<span style="margin-left: 10px">头部信息：</span>-->
                    <!--<el-button type="primary" size="mini" @click="addProjectHeader()">添加</el-button>-->
                    <!--</div>-->
                    <!--<el-table :data="projectData.header" stripe :show-header="false">-->
                    <!--<el-table-column label="Key" header-align="center" minWidth="50">-->
                    <!--<template slot-scope="scope">-->
                    <!--<el-input v-model="scope.row.key" size="mini" placeholder="key">-->
                    <!--</el-input>-->
                    <!--</template>-->
                    <!--</el-table-column>-->
                    <!--<el-table-column label="Value" header-align="center" minWidth="80">-->
                    <!--<template slot-scope="scope">-->
                    <!--<el-input v-model="scope.row.value" size="mini" placeholder="value">-->
                    <!--</el-input>-->
                    <!--</template>-->
                    <!--</el-table-column>-->
                    <!--<el-table-column label="操作" header-align="center" width="80">-->
                    <!--<template slot-scope="scope">-->
                    <!--<el-button type="danger" icon="el-icon-delete" size="mini"-->
                    <!--@click.native="delProjectHeader(scope.$index)">删除-->
                    <!--</el-button>-->
                    <!--</template>-->
                    <!--</el-table-column>-->
                    <!--</el-table>-->


                </el-tab-pane>

            </el-tabs>

            <div slot="footer" class="dialog-footer">
                <el-button @click="projectData.modelFormVisible = false" size="small">取 消</el-button>
                <el-button type="primary" id="sure_btn"
                           @click.native="addProjectBtn()" size="small">确 定
                </el-button>
            </div>
        </el-dialog>

    </div>
</template>

<script>

    export default {
        name: 'projectManage',
        data() {
            return {
                environmentChoice: 'testPre',
                environment: {
                    testPre: [{value: ''}],
                    test: [{value: ''}],
                    pre: [{value: ''}],
                    pro: [{value: ''}],
                    gm: [{value: ''}],
                },
                environmentName: {
                    testPre: "测试预发",
                    test: "测试",
                    pre: "预发",
                    pro: "灰度/正式",
                    gm: "GM"
                },
                tableData: Array(),
                total: 1,
                funcAddress: '',
                userData: [],
                currentPage: 1,
                sizePage: 20,
                form: {
                    projectName: null,
                    user: {
                        user_name: null,
                        user_id: null,
                    },
                    team_ids: Array(),
                },
                projectData: {
                    host: null,
                    hostTwo: null,
                    hostThree: null,
                    hostFour: null,
                    id: null,
                    userId: null,
                    modelFormVisible: false,
                    projectName: null,
                    principal: null,
                    formLabelWidth: '80px',
                    funcFile: '',
                    header: Array(),
                    variable: Array(),
                },
                currentUser: 0,
                auth: '',
                role: '',
            }
        },
        methods: {
            proHandleCurrentChange(val) {
                this.currentPage = val;
                this.findProject()
            },
            proHandleSizeChange(val) {
                this.sizePage = val;
                this.findProject()
            },

            findProject() {
                this.role = this.$store.state.roles;
                this.auth = JSON.parse(this.$store.state.auth);

                this.$axios.post(this.$api.findProApi, {
                    'projectName': this.form.projectName,
                    'page': this.currentPage,
                    'sizePage': this.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.tableData = response.data['data'];
                            this.total = response.data['total'];
                            this.userData = response.data['userData'];
                            this.currentUser = response.data['current_user'];
                        }
                    }
                )
            },
            findFuncAddress() {
                this.$axios.post(this.$api.getFuncAddressApi).then((response) => {
                        this.funcAddress = response['data']['data'];
                    }
                )
            },
            initProjectData() {
                this.projectData.projectName = null;
                this.form.user = {};
                this.form.team_ids = Array();
                this.projectData.principal = null;
                this.projectData.funcFile = null;
                this.projectData.header = Array();
                this.projectData.variable = Array();
                this.projectData.id = null;
                this.projectData.modelFormVisible = true;

                this.environment = {
                    testPre: [{value: ''}],
                    test: [{value: ''}],
                    pre: [{value: ''}],
                    pro: [{value: ''}],
                    gm: [{value: ''}],
                }
            },
            updateEnv(data, type) {
                let hostDict = {}
                for (let env in data) {
                    if (type == 'list') {
                        hostDict[env] = this.dealHostList(data[env])
                    }
                    else {
                        hostDict[env] = this.dealHostDict(data[env])
                    }
                }
                return hostDict;
            },
            dealHostList(data) {
                // 把[{value:xxx1},{value:xxx2}] 转为 [xxx1,xxx2]111
                let host = Array();
                for (let i = 0; i < data.length; i++) {
                    if (data[i].value != '') {
                        host.push(data[i].value);
                    }
                }
                return host
            },
            dealHostDict(data) {
                // 把[xxx1,xxx2] 转为 [{value:xxx1},{value:xxx2}]
                let host = Array();
                if (!data || data.length == 0) {
                    host.push({'value': ''});
                    return host;
                }
                for (let i = 0; i < data.length; i++) {
                    host.push({value: data[i]});
                }
                host.push({'value': ''});
                return host
            },
            addProjectBtn() {
                this.addProject();
            },
            addProject() {
                this.$axios.post(this.$api.addProApi, {
                    'projectName': this.projectData.projectName,
                    'principal': this.projectData.principal,
                    'funcFile': this.projectData.funcFile,
                    'environmentChoice': 'testPre',
                    'host': this.updateEnv(this.environment, 'list'),
                    'id': this.projectData.id,
                    'header': JSON.stringify(this.projectData.header),
                    'userId': this.form.user.user_id,
                    'variable': JSON.stringify(this.projectData.variable),
                    'team_ids': this.form.team_ids,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.projectData.modelFormVisible = false;
                            this.findProject();
                        }
                    }
                )
            },
            editProject(id) {
                this.$axios.post(this.$api.editProApi, {'id': id}).then((response) => {
                        response.data['data'] = JSON.parse(response.data['data']);
                        let index = this.userData.map(item => item.user_id).indexOf(response.data['data']['user_id']);
                        this.form.user = this.userData[index];
                        this.form.team_ids = response.data['data']['team_ids'];
                        this.projectData.projectName = response.data['data']['pro_name'];
                        this.projectData.principal = response.data['data']['principal'];
                        this.environmentChoice = response.data['data']['environment_choice'];
                        this.environment = this.updateEnv(response.data['data']['host'], 'dict');
                        this.projectData.header = response.data['data']['headers'];
                        this.projectData.variable = response.data['data']['variables'];
                        this.projectData.id = id;
                        this.projectData.funcFile = response.data['data']['func_file'];
                        this.projectData.modelFormVisible = true;
                    }
                )
            },
            delProject(id) {
                this.$axios.post(this.$api.delProApi, {'id': id}).then((response) => {
                        this.messageShow(this, response);

                        // 分页数量判断，当删除了某一页的最后一条数据后，分页数量-1
                        if ((this.currentPage - 1) * this.sizePage + 1 === this.total) {
                            this.currentPage = this.currentPage - 1
                        }
                        this.findProject();
                    }
                )
            },
            addProjectVariable() {
                this.projectData.variable.push({key: null, value: null, remark: null});
            },
            delProjectVariable(i) {
                this.projectData.variable.splice(i, 1);
            },
            addProjectHeader() {
                this.projectData.header.push({key: null, value: null});
            },
            delProjectHeader(i) {
                this.projectData.header.splice(i, 1);
            },
            delTableRow(type, i) {
                if (this.environment[type].length === 1) {
                    return false;
                }

                this.$confirm('删除url会影响到整体排序,接口那边的引用是依据url的顺序来的,请认真考虑一下?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.environment[type].splice(i, 1);
                }).catch(() => {
                });
            },
            addTableRow(type) {
                this.environment[type].push({value: ''});
            },
        },
        computed: {
            monitorEnvironment() {
                return this.environment;
            }
        },
        watch: {
            monitorEnvironment: {
                handler: function () {
                    let host_list = this.environment[this.environmentChoice];
                    let host_len = host_list.length;
                    if (host_len === 0) {
                        this.addTableRow(this.environmentChoice)
                    }
                    if (host_list[host_len - 1]['value']) {
                        this.addTableRow(this.environmentChoice)
                    }
                },
                deep: true
            }
        },
        mounted() {
            this.findProject();
            this.findFuncAddress();
        },
    }
</script>
<style>
</style>
