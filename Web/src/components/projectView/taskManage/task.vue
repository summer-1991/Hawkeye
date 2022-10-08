<template>
    <div class="modeManage">

        <el-form :inline="true" class="demo-form-inline search-style" size="small">
            <el-form-item label="项目" labelWidth="80px">
                <el-select v-model="form.projectId" placeholder="选择项目">
                    <el-option
                            v-for="(item) in proAndIdData"
                            :key="item.id"
                            :label="item.name"
                            :value="item.id">
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="任务" labelWidth="50px">


                <el-input placeholder="请输入任务名称" v-model="form.taskName">
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="handleCurrentChange(1)">搜索</el-button>
                <el-button type="primary" @click.native="initTaskData()" v-show="role === '2' || auth.api_task_add">添加任务
                </el-button>
            </el-form-item>
        </el-form>

        <el-tabs value="first" class="table_padding">
            <el-tab-pane label="任务列表" name="first" style="margin: 0 0 -10px;">
                <el-table :data="tableData"
                          max-height="725"
                          stripe>
                    <!--<el-table-column-->
                    <!--prop="num"-->
                    <!--label="编号"-->
                    <!--min-width="40">-->
                    <!--</el-table-column>-->
                    <el-table-column
                            prop="task_name"
                            label="任务名称"
                            min-width="100">
                    </el-table-column>
                    <el-table-column
                            prop="task_config_time"
                            label="cron"
                            min-width="100">
                    </el-table-column>
                    <el-table-column
                            prop="status"
                            label="状态"
                            min-width="100">
                        <template slot-scope="scope">
                            <!--<div :style="scope.row.read_status === '已读' ? 'color:#2bef2b': 'color:rgb(255, 74, 74)'">-->
                            <!--{{scope.row.read_status}}-->
                            <!--</div>-->
                            <el-tag size="small" :type="scope.row.status === '创建' ?
                             'info' :  scope.row.status === '启动' ? 'success' : 'warning'">
                                {{scope.row.status}}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column
                            label="操作"
                            min-width="200">
                        <template slot-scope="scope">
                            <el-button type="primary" v-show="false">{{null}}</el-button>
                            <el-button type="primary" size="mini" v-if="tableData[scope.$index]['status'] === '创建'"
                                       @click.native="editTask(tableData[scope.$index]['id'])"
                                       v-show="role === '2' || auth.api_task_edit">修改
                            </el-button>
                            <el-button type="primary" size="mini" v-if="tableData[scope.$index]['status'] === '创建'"
                                       @click.native="startTask(tableData[scope.$index]['id'])"
                                       v-show="role === '2' || auth.api_task_todo">启动
                            </el-button>
                            <el-button type="primary" size="mini" v-if="tableData[scope.$index]['status'] !== '创建'"
                                       v-show="(role === '2' || auth.api_task_todo) && tableData[scope.$index]['status'] !== '暂停'"
                                       @click.native="pauseTask(tableData[scope.$index]['id'])">暂停
                            </el-button>
                            <el-button type="primary" size="mini" v-if="tableData[scope.$index]['status'] !== '创建'"
                                       v-show="(role === '2' || auth.api_task_todo) && tableData[scope.$index]['status'] !== '启动'"
                                       @click.native="resumeTask(tableData[scope.$index]['id'])">启动
                            </el-button>
                            <el-button type="primary" size="mini" v-if="tableData[scope.$index]['status'] !== '创建'"
                                       @click.native="removeTask(tableData[scope.$index]['id'])"
                                       v-show="role === '2' || auth.api_task_todo">移除
                            </el-button>
                            <el-button type="success" size="mini" :loading="scope.row.isShow"
                                       @click.native="runNow(scope.row)"
                                       v-show="role === '2' || auth.api_task_run">单次运行
                            </el-button>
                            <el-button type="danger" icon="el-icon-delete" size="mini"
                                       @click.native="sureView(delTask,tableData[scope.$index]['id'],tableData[scope.$index]['task_name'])"
                                       v-show="role === '2' || auth.api_task_del">
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
                <div class="pagination">
                    <el-pagination
                            @current-change="handleCurrentChange"
                            @size-change="handleSizeChange"
                            :current-page="currentPage"
                            :page-size="sizePage"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="this.total">
                    </el-pagination>
                </div>
            </el-tab-pane>
        </el-tabs>


        <el-dialog title="任务配置" :visible.sync="taskData.modelFormVisible" width="42%">
            <el-tabs>
                <el-tab-pane label="messages" style="margin-top: 10px">
                    <el-form>

                        <!--<el-form-item label="执行类别" :label-width="taskData.formLabelWidth">-->
                        <!--<el-select v-module="taskData.taskType" size="medium">-->
                        <!--<el-option v-for="item in taskTypes" :key="item" :value="item">-->
                        <!--</el-option>-->
                        <!--</el-select>-->
                        <!--</el-form-item>-->
                        <el-form-item label="执行选择" :label-width="taskData.formLabelWidth">
                            <el-select v-model="form.projectId" placeholder="选择项目"
                                       style="width: 150px;padding-right:5px"
                                       @change="changeProjectChoice">
                                <el-option
                                        v-for="(item) in proAndIdData"
                                        :key="item.id"
                                        :label="item.name"
                                        :value="item.id">
                                </el-option>
                            </el-select>

                            <el-select v-model="form.set" multiple filterable placeholder="选择用例集" value-key="id"
                                       @change="changeSceneChoice"
                                       style="width: 150px;padding-right:5px">
                                <el-option
                                        v-for="item in allSetList[this.form.projectId]"
                                        :key="item.id"
                                        :label="item.label"
                                        :value="item">
                                </el-option>
                            </el-select>

                            <el-select v-model="form.case" multiple filterable placeholder="选择用例" value-key="id"
                                       :disabled="caseStatus"
                                       style="width: 150px">
                                <el-option
                                        v-for="item in allSceneList[this.form.set_id]"
                                        :key="item.id"
                                        :label="item.label"
                                        :value="item">
                                </el-option>
                            </el-select>

                        </el-form-item>
                        <el-form-item label="执行环境" :label-width="taskData.formLabelWidth">
                            <el-select v-model="taskData.environment" clearable value-key="envId" placeholder="执行环境"
                                       style="width: 150px;padding-right:5px"
                                       @change="changeEnvChoice">
                                <el-option
                                        v-for="(item,key) in environmentList"
                                        :key="key"
                                        :label="item"
                                        :value="key">
                                </el-option>
                            </el-select>

                            <el-select v-model="taskData.choiceUrl"
                                       clearable placeholder="请选择url"
                                       style="width: 150px;padding-right:5px">
                                <el-option
                                        v-for="item in currentUrlData"
                                        :key="item"
                                        :label="item"
                                        :value="item"
                                >
                                </el-option>
                            </el-select>

                            <el-select v-model="taskData.clientId"
                                       filterable style="width: 150px;padding-right:5px" clearable>
                                <el-option
                                        v-for="(item) in clientsList"
                                        :key="item"
                                        :label="item"
                                        :value="item"
                                >
                                </el-option>
                            </el-select>

                            <el-input v-model="taskData.gm" clearable style="width: 200px;padding-right:5px"
                                      placeholder="输入需替换的gm_url"></el-input>

                        </el-form-item>
                        <el-form-item label="全局变量" :label-width="taskData.formLabelWidth">
                            <el-button type="primary" size="mini"
                                       style="margin-left:20px"
                                       @click="formatData()">格式化
                            </el-button>
                            <div style="border:1px solid rgb(234, 234, 234) ">
                                <el-container>
                                    <editor
                                            v-model="taskData.jsonVariable"
                                            style="font-size: 15px"
                                            @init="editorInit"
                                            lang="json"
                                            theme="chrome"
                                            width="100%"
                                            height="100px"
                                            :options="{}"
                                    >
                                    </editor>
                                </el-container>
                            </div>
                        </el-form-item>
                        <el-form-item label="任务名称" :label-width="taskData.formLabelWidth">
                            <el-input v-model="taskData.name" auto-complete="off">
                            </el-input>
                        </el-form-item>
                        <el-form-item label="收件人邮箱" :label-width="taskData.formLabelWidth">
                            <el-input v-model="taskData.toEmail">
                            </el-input>
                        </el-form-item>
                        <el-form-item label="发件人邮箱" :label-width="taskData.formLabelWidth">
                            <el-input v-model="taskData.SendEmail">
                            </el-input>
                        </el-form-item>
                        <el-form-item label="邮箱密码" :label-width="taskData.formLabelWidth"
                                      prop="desc">
                            <el-input v-model="taskData.password" type="password">
                            </el-input>
                        </el-form-item>

                        <el-form-item label="时间配置" :label-width="taskData.formLabelWidth">
                            <el-input v-model="taskData.timeConfig"
                                      placeholder="second minute hour day month day_of_week(0 0 12 * * ? 每天中午12点触发)">
                            </el-input>
                        </el-form-item>
                    </el-form>
                </el-tab-pane>


            </el-tabs>

            <div slot="footer" class="dialog-footer">
                <el-button @click="taskData.modelFormVisible = false" size="small">取 消</el-button>
                <el-button type="primary"
                           @click.native="addTask()" size="small">确 定
                </el-button>
            </div>
        </el-dialog>

    </div>
</template>

<script>
    export default {
        components: {
            editor: require('vue2-ace-editor'),
        },
        name: 'modeManage',
        data() {
            return {
                proAndIdData: '',
                runStatus: false,
                caseStatus: false,
                allSetList: '',
                allSceneList: '',
                tableData: [],
                total: 1,
                currentPage: 1,
                sizePage: 20,
                form: {
                    set: {
                        label: null,
                        id: null,
                    },
                    case: {
                        label: null,
                        id: null,
                    },
                    set_id: '',
                    projectId: '',
                    taskName: '',
                },
                taskData: {
                    id: '',
                    num: '',
                    modelFormVisible: false,
                    projectName: '',
                    name: '',
                    taskType: '',
                    toEmail: '',
                    SendEmail: '',
                    timeConfig: '',
                    password: '',
                    formLabelWidth: '90px',
                    environment: '',
                    choiceUrl: '',
                    gm: '',
                    clientId: '1012',
                    jsonVariable: '',
                },
                environmentList: {
                    testPre: "测试预发",
                    test: "测试",
                    pre: "预发",
                    pro: "灰度/正式",
                },
                currentUrlData: Array(),
                baseUrlData: Array(),
                clientsList: Array(),
                tole: '',
                auth: '',
            }
        },


        methods: {
            editorInit() {
                require('brace/ext/language_tools');
                require('brace/mode/json');
                require('brace/theme/chrome');
                require('brace/snippets/json')
            },
            formatData() {
                // 格式化json字符串
                try {
                    this.taskData.jsonVariable = JSON.parse(this.taskData.jsonVariable);
                    this.taskData.jsonVariable = JSON.stringify(this.taskData.jsonVariable, null, 4);
                } catch (err) {
                    this.$message({
                        showClose: true,
                        message: 'json格式错误',
                        type: 'warning',
                    });
                }
            },
            httpSend() {
                this.role = this.$store.state.roles;
                this.auth = JSON.parse(this.$store.state.auth);

                this.$axios.get(this.$api.baseDataApi).then((response) => {
                        this.proAndIdData = response.data['pro_and_id'];
                        this.allSetList = response.data['set_list'];
                        this.allSceneList = response.data['scene_list'];
                        this.baseUrlData = response.data['baseUrlData'];
                        if (response.data['user_pros']) {
                            this.form.projectId = this.proAndIdData[0].id;
                            this.findTask();
                        }

                    }
                );

            },
            changeProjectChoice() {
                this.form.set = [];
                this.form.case = [];
                this.changeEnvChoice();
            },
            changeEnvChoice() {
                this.currentUrlData = Array();
                this.taskData.choiceUrl = '';
                this.taskData.gm = '';
                if (this.taskData.environment.length != 0) {
                    this.currentUrlData = this.baseUrlData[this.form.projectId][this.taskData.environment];
                }
            },
            changeSceneChoice() {
                if (this.form.set.length === 1) {
                    this.caseStatus = false;
                    this.form.set_id = this.form.set[0].id;
                } else {
                    this.caseStatus = true;
                    this.form.case = [];
                    this.form.set_id = ''
                }
            },
            handleCurrentChange(val) {
                this.currentPage = val;
                this.findTask()
            },
            handleSizeChange(val) {
                this.sizePage = val;
                this.findTask()
            },
            findTask() {
                this.$axios.post(this.$api.findTaskApi, {
                    'projectId': this.form.projectId,
                    'taskName': this.form.taskName,
                    'page': this.currentPage,
                    'sizePage': this.sizePage,
                }).then((response) => {
                        if (response.data['status'] === 0) {
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'warning',
                            });
                        } else {
                            this.tableData = response.data['data'];
                            this.total = response.data['total'];
                            this.clientsList = response.data['clients'];
                        }

                    }
                )
            },
            initTaskData() {
                this.taskData.name = '';
                this.taskData.id = '';
                this.taskData.taskType = '';
                this.taskData.toEmail = '';
                this.taskData.SendEmail = '';
                this.taskData.timeConfig = '';
                this.taskData.password = '';
                this.taskData.environment = '';
                this.taskData.choiceUrl = '';
                this.taskData.gm = '';
                this.taskData.clientId = '1012';
                this.form.set = [];
                this.form.case = [];
                this.currentUrlData = [];
                this.taskData.num = '';
                this.taskData.modelFormVisible = true;
                this.taskData.jsonVariable = '';
            },
            addTask() {
                if (this.taskData.environment != '' && this.taskData.choiceUrl == '') {
                    this.$message({
                        showClose: true,
                        message: '选择了环境必须选择url',
                        type: 'warning',
                    });
                    return
                }

                if (this.taskData.jsonVariable) {
                    try {
                        JSON.parse(this.taskData.jsonVariable)
                    } catch (err) {
                        this.$message({
                            showClose: true,
                            message: 'json格式错误',
                            type: 'warning',
                        });
                        return
                    }
                }

                this.$axios.post(this.$api.addTaskApi, {
                    'projectId': this.form.projectId,
                    'setIds': this.form.set,
                    'caseIds': this.form.case,
                    'id': this.taskData.id,
                    'num': this.taskData.num,
                    'name': this.taskData.name,
                    'taskType': this.taskData.taskType,
                    'toEmail': this.taskData.toEmail,
                    'sendEmail': this.taskData.SendEmail,
                    'timeConfig': this.taskData.timeConfig,
                    'password': this.taskData.password,
                    'url_index': this.currentUrlData.indexOf(this.taskData.choiceUrl),
                    'status_url': this.taskData.choiceUrl,
                    'environment': this.taskData.environment,
                    'gm': this.taskData.gm,
                    'json_variable': this.taskData.jsonVariable,
                    'clientId': this.taskData.clientId
                }).then((response) => {

                        if (response.data['status'] === 0) {
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'warning',
                            });
                        } else {
                            this.taskData.modelFormVisible = false;
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'success',
                            });
                            this.findTask();

                        }
                    }
                )
            },
            editTask(id) {
                this.$axios.post(this.$api.editTaskApi, {'id': id}).then((response) => {
                        this.taskData.name = response.data['data']['task_name'];
                        this.taskData.timeConfig = response.data['data']['task_config_time'];
                        // this.form.projectName = response.data['data']['project_name'];
                        this.taskData.taskType = response.data['data']['task_type'];
                        this.taskData.toEmail = response.data['data']['task_to_email_address'];
                        this.taskData.SendEmail = response.data['data']['task_send_email_address'];
                        this.taskData.password = response.data['data']['password'];
                        this.taskData.num = response.data['data']['num'];
                        this.taskData.projectName = this.form.projectName;
                        this.taskData.id = id;
                        this.form.set = response.data['data']['set_ids'];

                        if (response.data['data']['set_ids'].length === 1) {
                            // 当用例集只有1个时，赋值set_id，让用例下拉框有数据显示
                            this.form.set_id = response.data['data']['set_ids'][0]['id']
                        } else {
                            this.caseStatus = true;
                        }
                        this.form.case = response.data['data']['case_ids'];
                        this.taskData.modelFormVisible = true;

                        this.taskData.environment = response.data['data']['environment'];
                        this.changeEnvChoice();
                        this.taskData.choiceUrl = this.currentUrlData[response.data['data']['url_index']];
                        this.taskData.gm = response.data['data']['gm'];
                        this.taskData.jsonVariable = response.data['data']['json_variable'];
                        this.taskData.clientId = response.data['data']['client']
                    }
                )
            },
            startTask(id) {
                this.$axios.post(this.$api.startTaskApi, {'id': id}).then((response) => {
                        this.messageShow(this, response);
                        this.findTask();
                    }
                )
            },
            pauseTask(id) {
                this.$axios.post(this.$api.pauseTaskApi, {'id': id}).then((response) => {
                        this.messageShow(this, response);
                        this.findTask();
                    }
                )
            },
            resumeTask(id) {
                this.$axios.post(this.$api.resumeTaskApi, {'id': id}).then((response) => {
                        this.messageShow(this, response);
                        this.findTask();
                    }
                )
            },
            removeTask(id) {
                this.$axios.post(this.$api.removeTaskApi, {'id': id}).then((response) => {
                        this.messageShow(this, response);
                        this.findTask();
                    }
                )
            },
            runNow(item) {
                if (!item.isShow) {
                    this.$set(item, 'isShow', true)
                } else {
                    item.isShow = true
                }
                this.$axios.post(this.$api.runTaskApi, {'id': item.id}).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.findTask();
                            let {href} = this.$router.resolve({
                                path: 'reportShow',
                                query: {reportId: response.data['data']['report_id']}
                            });
                            window.open(href, '_blank');
                        }
                        // this.runStatus = false;
                        item.isShow = false
                    }
                )
            },
            delTask(id) {
                this.$axios.post(this.$api.delTaskApi, {'id': id}).then((response) => {
                        this.messageShow(this, response);
                        this.form.taskName = '';
                        if ((this.currentPage - 1) * this.sizePage + 1 === this.total) {
                            this.currentPage = this.currentPage - 1
                        }
                        this.findTask();
                    }
                )
            },
        },
        mounted() {
            this.httpSend();


        },
    }
</script>

<style>

</style>
