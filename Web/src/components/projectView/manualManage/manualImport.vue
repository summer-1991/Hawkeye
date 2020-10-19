<template>
    <div class="manualImport">
        <el-row>
            <el-col :span="3">
                <el-steps finish-status="success" direction="vertical" :active="active" space="100px"
                          style="margin-top: 20px">
                    <el-step title="步骤 1" description="选择excel文件"></el-step>
                    <el-step title="步骤 2" description="设置表格头的对应关系"></el-step>
                    <el-step title="步骤 3" description="批量修改"></el-step>
                </el-steps>
            </el-col>
            <el-col :span="readSpan" style="padding-left: 5px;">
                <el-form>
                    <el-form-item prop="module" style="margin-bottom: 5px" label="测试集" label-width="100px">
                        <el-select v-model="form.moduleId"
                                   placeholder="请选择测试集"
                                   size="small"
                                   style="width: 200px;padding-right:10px">
                            <el-option
                                    v-for="(item) in proModelData"
                                    :key="item.moduleId"
                                    :label="item.name"
                                    :value="item.moduleId">
                            </el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="文件类型" style="margin-bottom: 5px" label-width="100px">
                        <el-select v-model="importSelectType"
                                   placeholder="请选择导入文件类型"
                                   size="small"
                                   style="width: 200px;padding-right:10px">
                            <el-option
                                    v-for="item in importFileType"
                                    :key="item"
                                    :value="item">
                            </el-option>
                        </el-select>
                    </el-form-item>
                </el-form>
                <el-upload :auto-upload="false" :file-list="importFileList"
                           :http-request="importFile"
                           ref="import"
                           :before-upload="beforeImport"
                           :on-change="handleChange"
                           :on-remove="handleRemove"
                           :on-exceed="handleExceed">
                    <el-button slot="trigger" size="small" type="primary" style="margin: 30px;">附件</el-button>
                    <el-button type="success" size="small" @click="submitImport" style="margin: 10px;"
                               :disabled="nextFlag">下一步
                    </el-button>
                    <el-button type="danger" size="small" @click="cancelImport" style="margin: 10px;">取消</el-button>
                </el-upload>
            </el-col>
            <el-col :span="settingSpan" style="padding-left: 5px;">
                <el-table
                        :data="tableHeader">
                    <el-table-column
                            label="表格头"
                            width="180">
                        <template slot-scope="scope">
                            <div v-html='scope.row'></div>
                        </template>
                    </el-table-column>
                    <el-table-column label="平台用例头">
                        <template slot-scope="scope">
                            <el-select v-model="platformSelectData[scope.$index]"
                                       placeholder="请选择对应平台用例头"
                                       size="small"
                                       clearable
                                       style="width: 200px;padding-right:10px">
                                <el-option
                                        v-for="item in headerList"
                                        :key="item"
                                        :value="item">
                                </el-option>
                            </el-select>
                        </template>
                    </el-table-column>
                </el-table>
                <el-button type="success" size="small" @click="settingImport" style="margin: 10px;"
                           :disabled="nextFlag">下一步
                </el-button>
                <el-button type="danger" size="small" @click="cancelImport" style="margin: 10px;">取消</el-button>
            </el-col>
            <el-col :span="importSpan" style="padding-left: 5px;">
                <el-table :data="platformData">
                    <el-table-column
                            label="用例名称">
                        <template slot-scope="scope">
                            <el-input v-model="platformData[scope.$index][0]"></el-input>
                        </template>
                    </el-table-column>
                    <el-table-column
                            label="用例类型">
                        <template slot-scope="scope">
                            <el-select v-model="platformData[scope.$index][1]"
                                       size="small">
                                <el-option
                                        v-for="item in caseTypeList"
                                        :key="item"
                                        :value="item">
                                </el-option>
                            </el-select>
                        </template>
                    </el-table-column>
                    <el-table-column
                            label="用例描述">
                        <template slot-scope="scope">
                            <el-input v-model="platformData[scope.$index][2]" type="textarea" :rows="2"></el-input>
                        </template>
                    </el-table-column>
                    <el-table-column
                            label="前提条件">
                        <template slot-scope="scope">
                            <el-input v-model="platformData[scope.$index][3]" type="textarea" :rows="2"></el-input>
                        </template>
                    </el-table-column>
                    <el-table-column
                            label="执行步骤">
                        <template slot-scope="scope">
                            <el-input v-model="platformData[scope.$index][4]" type="textarea" :rows="2"></el-input>
                        </template>
                    </el-table-column>
                    <el-table-column
                            label="期望结果">
                        <template slot-scope="scope">
                            <el-input v-model="platformData[scope.$index][5]" type="textarea" :rows="2"></el-input>
                        </template>
                    </el-table-column>
                    <el-table-column>
                        <template slot-scope="scope">
                            <el-button type="danger" icon="el-icon-delete" size="mini"
                                       @click.native="sureView(delImportCase,scope.$index,platformData[scope.$index][0])">
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
                <el-button type="success" size="small" @click="doImport" style="margin: 10px;"
                           :disabled="nextFlag">导入
                </el-button>
                <el-button type="danger" size="small" @click="cancelImport" style="margin: 10px;">取消</el-button>
            </el-col>
        </el-row>
    </div>
</template>

<script>
    export default {
        name: "manualImport",
        components: {},
        props: ['moduleId', 'projectId', 'proModelData'],
        data() {
            return {
                active: 0,
                nextFlag: true,
                numTab: 'third',  //  tab页的显示
                loading: false,  //  页面加载状态开关
                readSpan: 10,
                settingSpan: 0,
                importSpan: 0,
                form: {
                    projectId: -1,
                    moduleId: null,
                },
                importFileType: ['Excel'],
                importSelectType: 'Excel',
                importFileList: [],
                tableHeader: Array(),
                headerList: ['用例名称', '用例类型', '用例描述', '前置条件', '执行步骤', '期望结果'],
                caseTypeList: ['最高', '较高', '一般', '较低', '最低'],
                selectHeader: '',
                readData: Array(),
                platformSelectData: Array(),
                platformData: Array(),
            }
        },
        methods: {
            initImportData() {
                this.readSpan = 10;
                this.settingSpan = 0;
                this.importSpan = 0;
                this.importFileList = [];
                this.importSelectType = 'Excel';
                this.form.moduleId = this.moduleId;
                this.form.projectId = this.projectId;
            },
            next() {
                if (this.active++ > 2) this.active = 0;
            },
            // 上传文件
            importFile(file) {
                this.importData.append('files', file.file);  // append增加数据
            },
            beforeImport() {

            },
            delImportCase(index) {
                this.platformData.splice(index, 1);
            },
            cancelImport() {
                this.readSpan = 10;
                this.settingSpan = 0;
                this.importSpan = 0;

                this.nextFlag = true;
                this.active = 0;
                this.importFileList = [];
                this.tableHeader = [];
                this.selectHeader = '';
                this.readData = [];
                this.platformSelectData = [];
                this.platformData = [];
            },
            // 上传到服务器
            submitImport() {
                if (!this.form.moduleId) {
                    this.$message({
                        showClose: true,
                        message: '请先创建测试集',
                        type: 'warning',
                    });
                    return
                }

                this.importData = new FormData();  // new formData对象
                this.$refs.import.submit();
                this.importData.append('importSteps', 'read');
                this.$axios.post(this.$api.importCaseFile, this.importData).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.tableHeader = response.data['data']['key'];
                            this.readData = response.data['data']['value'];
                            this.next();
                            this.readSpan = 0;
                            this.settingSpan = 10;
                        }
                    }
                )
            },
            settingImport() {
                let platformObject = {};
                for (let k = 0; k < this.platformSelectData.length; k++) {
                    let tempKey = this.platformSelectData[k];

                    if (tempKey == null || tempKey == '') {
                        continue;
                    }

                    let tempList = [];
                    if (platformObject[tempKey] != null) {
                        tempList = platformObject[tempKey];
                    }

                    tempList.push(this.tableHeader[k]);
                    platformObject[tempKey] = tempList;
                }

                for (let i = 0; i < this.readData.length; i++) {
                    let tempList = [];
                    let tempData = this.readData[i];

                    for (let j = 0; j < this.headerList.length; j++) {
                        if (j == 1) {
                            tempList.push(this.caseTypeList[0]);
                            continue;
                        }

                        let tempHeaderValueList = platformObject[this.headerList[j]];
                        let res = '';
                        if (tempHeaderValueList == null) {
                            tempList.push('');
                            continue;
                        }
                        for (let m = 0; m < tempHeaderValueList.length; m++) {
                            res = res + tempData[tempHeaderValueList[m]];
                        }
                        tempList.push(res);
                    }
                    this.platformData.push(tempList);
                }
                this.next();
                this.readSpan = 0;
                this.settingSpan = 0;
                this.importSpan = 21;
            },
            doImport() {
                for (let n = 0; n < this.platformData.length; n++) {
                    let tempData = this.platformData[n];
                    let caseName = tempData[0];
                    if (caseName == '' || caseName == null) {
                        this.$message({
                            showClose: true,
                            message: '用例名称不能为空！',
                            type: 'warning',
                        });
                        return false;
                    }
                }

                for (let n = 0; n < this.platformData.length; n++) {
                    let tempData = this.platformData[n];
                    tempData[1] = this.caseTypeList.indexOf(tempData[1])
                }

                this.$axios.post(this.$api.importManualCaseApi, {
                    'importCases': this.platformData,
                    'moduleId': this.moduleId,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.cancelImport();
                        }
                    }
                )
            },
            //移除
            handleRemove(file, fileList) {
                this.importFileList = fileList;
                this.nextFlag = true;
            },
            // 选取文件超过数量提示
            handleExceed(files, fileList) {
                this.$message.warning(`当前限制选择 5 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
            },
            //监控上传文件列表
            handleChange(file, fileList) {
                let existFile = fileList.slice(0, fileList.length - 1).find(f => f.name === file.name);
                const isLt10M = file.size / 1024 / 1024 < 1;
                let extension = file.name.substring(file.name.lastIndexOf('.') + 1);
                let allowList = ['xlsx', 'xls'];
                if (allowList.indexOf(extension) == -1) {
                    this.$message.error('上传的不是Excel格式的文件，请检查！');
                    fileList.pop();
                }
                if (existFile) {
                    this.$message.error('当前文件已经存在!');
                    fileList.pop();
                } else if (!isLt10M) {
                    this.$message.error('请检查，上传文件大小不能超过1MB!');
                    fileList.pop();
                }
                this.importFileList = fileList;
                this.nextFlag = false;
            },
        },
        mounted() {
        },
    }
</script>

<style>

</style>