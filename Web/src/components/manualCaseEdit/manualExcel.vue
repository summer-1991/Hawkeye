<template>
    <div class="manualExcel" v-loading="this.loading">
        <div class="hello">
            <el-card class="box-card"
                     style="width: 15%;height:90%;position: absolute;margin-top: 0px;margin-left: 0px;z-index: 20"
                     :body-style="{ padding: '10px' ,height:'100%'}" shadow="always" v-show="showView">
                <el-button-group style="float: right;">
                    <el-button type="primary" size="mini" @click.native="initTestCaseFile()">新增</el-button>
                    <el-button type="primary" size="mini" @click.native="initEditTestCaseFile()">编辑</el-button>
                    <el-button type="primary" size="mini" @click.native="refreshEditTestCaseFile()">刷新</el-button>
                    <el-button type="danger" size="mini" @click.native="delTestCaseFileBtn">删除</el-button>
                    <el-button type="info" size="mini" @click="showView = false">关闭</el-button>
                </el-button-group>
                <hr style="height:1px;border:none;border-top:1px solid rgb(241, 215, 215);margin-top:30px"/>
                <el-scrollbar>
                    <el-tree :data="treeData"
                             :props="defaultProps"
                             @node-click="handleNodeClick"
                             highlight-current>
                            <span class="custom-tree-node span-ellipsis" slot-scope="{ node, data }">
                            <span :title="node.label">
                                <i :class=" data.status === 0? 'el-icon-folder test1' :  'el-icon-document test'"
                                ></i>{{ node.label }}
                            </span>
                        </span>
                    </el-tree>
                </el-scrollbar>
            </el-card>

            <el-dialog title="用例配置" :visible.sync="tempCaseFileData.viewStatus">
                <el-divider></el-divider>
                <el-radio-group v-model="addCaseFileData.status" :disabled="this.addCaseFileData.id !== null">
                    <el-radio :label=0>测试集</el-radio>
                    <el-radio :label=1>测试用例</el-radio>
                </el-radio-group>
                <el-divider direction="vertical"></el-divider>

                <el-radio-group v-model="addCaseFileData.idChoice" :disabled="this.addCaseFileData.id !== null">
                    <el-radio :label=1>新增同级</el-radio>
                    <el-radio :label=2>新增下级</el-radio>
                </el-radio-group>
                <el-divider></el-divider>
                <el-form>
                    <el-form-item label="名称" label-width="100px">
                        <el-input v-model="addCaseFileData.name">
                        </el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button size="small" @click="tempCaseFileData.viewStatus = false">取 消</el-button>
                    <el-button type="primary" size="small" @click.native="addTestCaseFile()">确 定</el-button>
                </div>
            </el-dialog>

            <el-button type="primary" icon="el-icon-d-arrow-right" size="mini" style="position: absolute;"
                       @click="showView = true"></el-button>
            <el-tag type="success" id="excel_name"
                    style="position: absolute;font-size: 14px;margin-left: 30%;width: 15%;"></el-tag>
            <input id='excel_file' style="font-size: 16px;position: absolute;right: 80px;" type="file"
                   @change="uploadExcel"/>
            <el-button type="primary" size="small" @click="saveTestCaseFile(true)"
                       style="position: absolute;right: 20px;"
                       v-if="role == '2' || auth.manual_case_save">保存
            </el-button>
            <div id="luckysheet"
                 style="margin:0px;padding:0px;position:absolute;width:100%;top: 35px;bottom:0px;z-index: 10;"></div>
        </div>
    </div>
</template>

<script>
    import LuckyExcel from 'luckyexcel'
    import {mapGetters, mapActions, mapMutations} from "vuex";

    export default {
        name: 'manualExcel',
        components: {},
        computed: {},
        data() {
            return {
                showView: false,
                role: '',
                auth: '',
                privates: false,
                excel_title: '',
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                tempCaseFileData: {
                    name: null,
                    viewStatus: false,
                    id: null,
                    higherId: 0,
                    status: 0,
                },
                addCaseFileData: {
                    name: null,
                    id: null,
                    higherId: 0,
                    status: 0,
                    idChoice: 1,
                    num: null,
                },
                tempTreeData: {
                    data: Object,
                    node: Object,
                },
                treeData: [],
            }
        },
        methods: {
            initBaseData() {
                this.role = this.$store.state.roles;
                this.auth = JSON.parse(this.$store.state.auth);
                this.findTestCaseFile();
                this.clearInit();
                this.initLuckySheet();
            },
            initLuckySheet() {
                const options = {
                    container: 'luckysheet',
                    lang: 'zh',
                    showinfobar: false,
                    column: 26,
                    data: [{
                        "name": "Sheet1",
                        "color": "",
                        "index": 1,
                        "status": 0,
                        "order": 1,
                        "celldata": [],
                        "config": {},
                    }],
                    showtoolbarConfig: {
                        chart: false, // '图表'
                        print: false, // '打印'
                    },
                    cellRightClickConfig: {
                        chart: false, // 图表生成
                        data: false,
                    }
                };

                window.luckysheet.destroy();
                window.luckysheet.create(options);
            },
            saveTestCaseFile(show) {
                if (this.tempCaseFileData.status == 0) {
                    return false;
                }

                const wookData = window.luckysheet.getAllSheets();
                for (let i = 0; i < wookData.length; i++) {
                    const sheetData = wookData[i];
                    delete sheetData['data']
                }

                this.$axios.post(this.$api.saveTestCaseFileApi, {
                    'ids': this.tempCaseFileData.id,
                    'show': show,
                    'data': JSON.stringify(wookData)
                }).then((response) => {
                        this.messageShow(this, response)
                    }
                )
            },
            uploadExcel(evt) {
                const files = evt.target.files;
                if (files == null || files.length == 0) {
                    return;
                }
                let name = files[0].name;
                let suffixArr = name.split("."), suffix = suffixArr[suffixArr.length - 1];
                if (suffix != "xlsx") {
                    alert("现在只支持xlsx文件！");
                    return;
                }
                LuckyExcel.transformExcelToLucky(files[0], (exportJson) => {
                    if (exportJson.sheets == null || exportJson.sheets.length == 0) {
                        alert("读取文件失败!");
                        return;
                    }
                    this.updateLuckySheet(exportJson.sheets);
                });
            },
            updateLuckySheet(exportJson) {
                window.luckysheet.destroy();
                window.luckysheet.create({
                    container: 'luckysheet',
                    lang: 'zh',
                    showinfobar: false,
                    column: 26,
                    data: exportJson,
                    showtoolbarConfig: {
                        chart: false, // '图表'
                        print: false, // '打印'
                    },
                    cellRightClickConfig: {
                        chart: false, // 图表生成
                        data: false,
                    }
                });
            },

            collapse: function () {
                this.showView = !this.showView;
                if (this.showView) {
                    let leftNums = {headerMenuNum: '400px', mainEditorNum: '400px', navigatorNum: '420px'};
                    this.$eventBus.$emit('setLeftNum', leftNums)
                } else {
                    let leftNums = {headerMenuNum: '80px', mainEditorNum: '80px', navigatorNum: '100px'};
                    this.$eventBus.$emit('setLeftNum', leftNums)
                }

            },
            initTestCaseFile() {
                this.addCaseFileData.status = 0;
                this.addCaseFileData.idChoice = 1;
                this.addCaseFileData.id = null;
                this.addCaseFileData.name = null;
                this.tempCaseFileData.viewStatus = true

            },
            initEditTestCaseFile() {
                if (!this.tempCaseFileData.id) {
                    this.$message({
                        showClose: true,
                        message: '没有选择文件无法编辑',
                        type: 'warning',
                    });
                    return
                }

                //this.addCaseFileData = this.tempCaseFileData;
                this.addCaseFileData.id = this.tempCaseFileData.id;
                this.addCaseFileData.higherId = this.tempCaseFileData.higherId;
                this.addCaseFileData.name = this.tempCaseFileData.name;
                this.addCaseFileData.status = this.tempCaseFileData.status;
                this.tempCaseFileData.viewStatus = true

            },
            refreshEditTestCaseFile() {
                this.findTestCaseFile();
                this.clearInit();
                this.initLuckySheet();
            },
            getTestCaseFile(ids) {
                this.$axios.post(this.$api.getTestCaseFileApi, {'id': ids}).then((response) => {
                        if (this.messageShow(this, response)) {
                            document.getElementById('excel_name').innerHTML = this.tempCaseFileData.name;
                            if (response.data['data'] == '') {
                                this.initLuckySheet();
                            }
                            else {
                                this.updateLuckySheet(JSON.parse(response.data['data']));
                            }
                        }
                    }
                )
            },
            delTestCaseFileBtn() {
                if (!this.tempCaseFileData.id) {
                    this.$message({
                        showClose: true,
                        message: '请先选择需要删除的文件',
                        type: 'warning',
                    });
                    return
                }
                this.sureView(this.delTestCaseFile, this.tempCaseFileData.id, this.tempCaseFileData.name)
            },
            delTestCaseFile(id) {
                this.$axios.post(this.$api.delTestCaseFileApi, {'id': id}).then((response) => {
                        if (this.messageShow(this, response)) {
                            const parent = this.tempTreeData.node.parent;
                            const children = parent.data.children || parent.data;
                            const index = children.findIndex(d => d.id === this.tempTreeData.data.id);
                            children.splice(index, 1);

                            // 顺便初始化临时数据
                            this.tempCaseFileData.status = 0;
                            this.tempCaseFileData.idChoice = 1;
                            this.tempCaseFileData.higherId = 0;
                            this.tempCaseFileData.id = null;
                            this.tempCaseFileData.name = null;

                            this.initLuckySheet();
                        }
                    }
                )
            },
            addTestCaseFile() {
                //  添加文件
                if (this.addCaseFileData.idChoice === 1) {
                    if (this.tempCaseFileData.higherId == null) {
                        this.addCaseFileData.higherId = 0
                    } else {
                        this.addCaseFileData.higherId = this.tempCaseFileData.higherId
                    }
                } else if (this.addCaseFileData.idChoice === 2) {
                    if (!this.tempCaseFileData.id) {
                        this.$message({
                            showClose: true,
                            message: '没有选择父级，无法新增下级，请选择新增同级',
                            type: 'warning',
                        });
                        return
                    }
                    this.addCaseFileData.higherId = this.tempCaseFileData.id
                }
                this.$axios.post(this.$api.addTestCaseFileApi, {
                    'name': this.addCaseFileData.name,
                    'higherId': this.addCaseFileData.higherId,
                    'status': this.addCaseFileData.status,
                    'id': this.addCaseFileData.id,
                    'num': this.addCaseFileData.num,
                    'fileType': 'm'
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.tempCaseFileData.viewStatus = false;
                            if (this.addCaseFileData.id) {
                                this.tempTreeData.data.name = this.addCaseFileData.name
                            } else {
                                if (this.addCaseFileData.idChoice === 1) {
                                    const newChild = {
                                        name: this.addCaseFileData.name,
                                        children: [],
                                        status: this.addCaseFileData.status,
                                        'higherId': response.data.higher_id,
                                        'id': response.data.id,
                                    };
                                    if (response.data.higher_id === 0) {
                                        this.treeData.push(newChild);
                                    } else {

                                        this.tempTreeData.node.parent.data.children.push(newChild);
                                    }
                                } else if (this.addCaseFileData.idChoice === 2) {
                                    const newChild = {
                                        name: this.addCaseFileData.name,
                                        children: [],
                                        status: this.addCaseFileData.status,
                                        'higherId': response.data.higher_id,
                                        'id': response.data.id,
                                    };
                                    if (!this.tempTreeData.data.children) {
                                        this.$set(this.tempTreeData.data, 'children', []);
                                    }
                                    this.tempTreeData.data.children.push(newChild);
                                }
                            }
                        }
                    }
                )
            },

            handleNodeClick(data, node) {
                this.tempTreeData.data = data;
                this.tempTreeData.node = node;

                this.tempCaseFileData.id = data.id;
                this.tempCaseFileData.higherId = data.higher_id;
                this.tempCaseFileData.name = data.name;
                this.tempCaseFileData.num = data.num;
                this.tempCaseFileData.status = data.status;

                this.clearInit();

                if (data.status === 1) {
                    this.getTestCaseFile(data.id)
                }
            },

            findTestCaseFile() {
                this.$axios.post('/api/testCaseFile/find', {
                    'privates': this.privates,
                    'fileType': 'm'
                }).then((response) => {
                        if (response.data['status'] === 0) {
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'warning',
                            });
                        } else {
                            this.treeData = response.data['data'];

                        }
                    }
                )
            },
            clearInit() {
                var obj = document.getElementById('excel_file');
                obj.value = '';

                document.getElementById('excel_name').innerHTML = '';
            },
        },
        watch: {},
        mounted() {
            this.initBaseData();
        },
        beforeDestroy: function () {
            window.luckysheet.destroy();
        }
    }
</script>
<style>
    :focus {
        outline: none;
    }

    .test {
        color: #66b1ff;
    }

    .test1 {
        color: #d27676;
    }

    .span-ellipsis {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }
</style>