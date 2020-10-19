<template>
    <div class="manualCase">
        <el-form :inline="true" style="padding: 10px 20px -10px 10px;">
            <el-form-item prop="module" style="margin-bottom: 5px" label="测试集">
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
            <el-form-item prop="name" style="margin-bottom: 5px" label="用例名称">
                <el-input v-model="caseData.name" placeholder="请输入" size="small"
                          style="width: 200px;padding-right:10px">
                </el-input>
            </el-form-item>
            <el-form-item prop="case_type" style="margin-bottom: 5px" label="用例类型">
                <el-select v-model="caseData.case_type"
                           placeholder="请选择测试集"
                           size="small"
                           style="width: 200px;padding-right:10px">
                    <el-option
                            v-for="item in caseTypeList"
                            :key="item"
                            :value="item">
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="文档编号"
                          label-width="80px"
                          prop="id"
                          v-if="caseData.id"
                          style="margin-bottom: 5px">

                <el-input v-model.number="caseData.id"
                          placeholder="文档编号"
                          size="small"
                          style="width: 70px;text-align:center;">
                </el-input>
            </el-form-item>
        </el-form>
        <el-form :inline="true" style="padding: 10px 20px -10px 10px;">
            <el-form-item prop="desc" style="margin-bottom: 5px" label="用例描述">
                <el-input type="textarea" :rows="2" v-model="caseData.desc" placeholder="请输入"
                          style="width: 185px;padding-right:10px">
                </el-input>
            </el-form-item>
        </el-form>
        <hr style="height:1px;border:none;border-top:1px solid rgb(241, 215, 215);margin-top: 5px"/>
        <el-form :inline="true" style="padding: 10px 20px -10px 10px;">
            <el-form-item prop="precondition" style="margin-bottom: 5px" label="前置条件">
                <el-input type="textarea" :rows="2" v-model="caseData.precondition" placeholder="请输入"
                          style="width: 300px;padding-right:10px">
                </el-input>
            </el-form-item>
        </el-form>
        <el-form :inline="true" style="padding: 10px 20px -10px 10px;">
            <el-form-item prop="steps" style="margin-bottom: 5px" label="执行步骤">
                <editor-bar :value="caseData.steps" :isClear="isClear" @change="changeSteps"></editor-bar>
            </el-form-item>
            <el-form-item prop="expect" style="margin-bottom: 5px" label="期望结果">
                <editor-bar :value="caseData.expect" :isClear="isClear" @change="changeExpect"></editor-bar>
            </el-form-item>
        </el-form>
        <hr style="height:1px;border:none;border-top:1px solid rgb(241, 215, 215);margin-top: 5px"/>
        <el-button style="margin-left: 133px;" size="small" type="success" @click="submitUpload">保存</el-button>
    </div>
</template>

<script>
    import EditorBar from '@/components/wiki/wangeditor'

    export default {
        name: "manualCase",
        components: {
            EditorBar: EditorBar
        },
        props: ['moduleId', 'projectId', 'proModelData'],
        data() {
            return {
                isClear: false,
                bodyShow: 'second',
                form: {
                    projectId: -1,
                    moduleId: null,
                },
                caseData: {
                    id: null,
                    name: null,
                    desc: null,
                    case_type: '',
                    precondition: '',
                    expect: '',
                    steps: ''
                },
                caseTypeList: ['最高', '较高', '一般', '较低', '最低']
            }
        },
        methods: {
            initCaseData() {
                this.caseData.name = '';
                this.caseData.id = null;
                this.caseData.desc = '';
                this.caseData.case_type = this.caseTypeList[0];
                this.caseData.precondition = '';
                this.caseData.expect = '';
                this.caseData.steps = '';
                this.form.moduleId = this.moduleId;
                this.form.projectId = this.projectId;
            },
            changeSteps(val) {
                this.caseData.steps = val
            },
            changeExpect(val) {
                this.caseData.expect = val
            },
            // 上传到服务器
            submitUpload() {
                if (this.form.moduleId == null) {
                    this.$message({
                        message: '请选择测试集',
                        type: 'warning'
                    });
                    return
                }
                if (this.caseData.name == null || this.caseData.name.trim() == '') {
                    this.$message({
                        message: '请输入文档名称',
                        type: 'warning'
                    });
                    return
                }
                if (this.caseData.case_type == null || this.caseData.case_type == '') {
                    this.$message({
                        message: '请选择用例类型',
                        type: 'warning'
                    });
                    return
                }

                return this.$axios.post(this.$api.addManualCaseApi, {
                    'caseId': this.caseData.id,
                    'moduleId': this.form.moduleId,
                    'caseName': this.caseData.name,
                    'desc': this.caseData.desc,
                    'case_type': this.caseTypeList.indexOf(this.caseData.case_type),
                    'precondition': this.caseData.precondition,
                    'steps': this.caseData.steps,
                    'expect': this.caseData.expect,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.caseData.id = response.data['case_id'];
                            return true
                        }
                    }
                )
            },
            editCopyCaseApi(caseId, status) {
                this.$axios.post(this.$api.editAndCopyManualCaseApi, {'caseId': caseId}).then((response) => {
                        this.caseData.name = response.data['data']['name'];
                        if (status === 'edit') {
                            this.caseData.id = caseId;
                        } else {
                            this.caseData.id = '';
                        }
                        this.caseData.desc = response.data['data']['desc'];
                        this.caseData.case_type = this.caseTypeList[response.data['data']['case_type']];
                        this.caseData.precondition = response.data['data']['precondition'];
                        this.caseData.steps = response.data['data']['steps'];
                        this.caseData.expect = response.data['data']['expect'];

                        this.form.projectId = this.projectId;
                        this.form.moduleId = this.moduleId;
                    }
                );
            },
        }
    }
</script>

<style>
</style>