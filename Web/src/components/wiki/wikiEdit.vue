<template>
    <div class="wikiEdit">
        <el-form :inline="true" style="padding: 10px 20px -10px 10px;">
            <el-form-item prop="name" style="margin-bottom: 5px" label="文档库">
                <el-select v-model="form.moduleId"
                           placeholder="请选择文档库"
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
            <el-form-item prop="name" style="margin-bottom: 5px" label="文档名称">
                <el-input v-model="wikiData.name" placeholder="请输入" size="small"
                          style="width: 200px;padding-right:10px">
                </el-input>
            </el-form-item>
            <el-form-item label="文档编号"
                          label-width="80px"
                          prop="num"
                          v-if="wikiData.id"
                          style="margin-bottom: 5px">

                <el-input v-model.number="wikiData.num"
                          placeholder="文档编号"
                          size="small"
                          style="width: 70px;text-align:center;">
                </el-input>
            </el-form-item>
        </el-form>
        <el-form :inline="true" style="padding: 10px 20px -10px 10px;">
            <el-form-item prop="name" style="margin-bottom: 5px" label="文档描述">
                <el-input type="textarea" :rows="2" v-model="wikiData.desc" placeholder="请输入"
                          style="width: 185px;padding-right:10px">
                </el-input>
            </el-form-item>
            <el-form-item prop="name" style="margin-bottom: 5px;" label="文档权限">
                <el-radio-group v-model="wikiData.auth" @change="radioChange">
                    <el-radio label="0">公开</el-radio>
                    <el-radio label="1">指定人员</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-form-item prop="name" style="margin-bottom: 5px" v-if="wikiData.auth==1">
                <el-select v-model="wikiData.team" id="team" size="mini"
                           style="width: 200px" multiple>
                    <el-option
                            v-for="item in userData"
                            :key="item.user_id"
                            :label="item.user_name"
                            :value="item.user_id">
                    </el-option>
                </el-select>
            </el-form-item>
        </el-form>
        <hr style="height:1px;border:none;border-top:1px solid rgb(241, 215, 215);margin-top: 5px"/>
        <el-form style="margin: 0 0 0 10px">
            <el-form-item>
                <editor-bar :value="wikiData.content" :isClear="isClear" @change="change"></editor-bar>
            </el-form-item>
        </el-form>
        <el-upload :auto-upload="false" multiple :limit="5" :file-list="fileList"
                   :http-request="uploadFile"
                   ref="upload"
                   :before-upload="beforeUpload"
                   :on-preview="handlePreview"
                   :on-change="handleChange"
                   :on-remove="handleRemove"
                   :on-exceed="handleExceed">
            <el-button slot="trigger" size="small" type="primary">附件</el-button>
            <el-button style="margin-left: 133px;" size="small" type="success" @click="submitUpload">保存</el-button>
            <div slot="tip" class="el-upload__tip" style="color: #bd2c00">同时只能上传5个文件，且单个文件不超过1MB</div>
        </el-upload>
    </div>
</template>

<script>
    import EditorBar from '@/components/wiki/wangeditor'

    export default {
        name: "wikiEdit",
        components: {
            EditorBar: EditorBar
        },
        props: ['moduleId', 'projectId', 'proModelData', 'userData'],
        data() {
            return {
                isClear: false,
                bodyShow: 'second',
                form: {
                    projectId: -1,
                    moduleId: null,
                },
                wikiData: {
                    id: null,
                    name: null,
                    num: null,
                    desc: null,
                    annex_name: [],
                    auth: '0',
                    team: null,
                    content: ''
                },
                fileList: [],
                uploadData: '',
            }
        },
        methods: {
            initWikiData() {
                this.wikiData.name = '';
                this.wikiData.num = '';
                this.wikiData.id = null;
                this.wikiData.desc = '';
                this.wikiData.auth = '0';
                this.wikiData.annex_name = [];
                this.wikiData.team = '';
                this.wikiData.content = '';
                this.fileList = [];
                this.form.moduleId = this.moduleId;
                this.form.projectId = this.projectId;
                this.$refs.upload.clearFiles();
            },
            radioChange(val){
                if(val=='0'){
                    this.wikiData.team='';
                }
            },
            change(val) {
                this.wikiData.content = val
            },
            // 上传文件
            uploadFile(file) {
                this.uploadData.append('files', file.file);  // append增加数据
                this.wikiData.annex_name = this.fileList;
            },
            beforeUpload() {
            },
            // 上传到服务器
            submitUpload() {
                if (this.form.moduleId === null) {
                    this.$message({
                        showClose: true,
                        message: '请选择文档库',
                        type: 'warning',
                    });
                    return
                }

                if (this.wikiData.name == null || this.wikiData.name.trim() == '') {
                    this.$message({
                        message: '请输入文档名称',
                        type: 'warning'
                    })
                } else {
                    this.uploadData = new FormData();  // new formData对象
                    this.$refs.upload.submit();
                    this.uploadData.append('name', this.wikiData.name);
                    this.uploadData.append('num', this.wikiData.num);
                    this.uploadData.append('desc', this.wikiData.desc);
                    this.uploadData.append('auth', this.wikiData.auth);
                    this.uploadData.append('team', this.wikiData.team);
                    this.uploadData.append('moduleId', this.form.moduleId);
                    this.uploadData.append('content', this.wikiData.content);
                    this.uploadData.append('wikiId', this.wikiData.id);
                    this.uploadData.append('annex_name', JSON.stringify(this.wikiData.annex_name));

                    this.$axios.post(this.$api.addWikiApi, this.uploadData).then((response) => {
                            if (this.messageShow(this, response)) {
                                this.wikiData.id = response.data['wiki_id'];
                                this.wikiData.num = response.data['num'];
                                this.fileList = response.data['file_list'];
                                this.wikiData.annex_name = response.data['file_list'];
                                return true
                            }
                        }
                    )
                }
            },
            editCopyWikiApi(wikiId, status) {
                this.$axios.post(this.$api.editAndCopyWikiApi, {'wikiId': wikiId}).then((response) => {
                        this.wikiData.name = response.data['data']['name'];
                        if (status === 'edit') {
                            this.wikiData.num = response.data['data']['num'];
                            this.wikiData.id = wikiId;
                        } else {
                            this.wikiData.num = '';
                            this.wikiData.id = '';
                        }

                        this.fileList = response.data['data']['annex_name'];
                        this.wikiData.desc = response.data['data']['desc'];
                        this.wikiData.auth = response.data['data']['auth'];
                        this.wikiData.team = response.data['data']['team'];
                        this.wikiData.content = response.data['data']['content'];
                        this.wikiData.annex_name = response.data['data']['annex_name'];

                        this.form.projectId = this.projectId;
                        this.form.moduleId = this.moduleId;
                    }
                );
            },
            handlePreview(file) {
                let params = {};
                params = file.url;
                let type = params.split('.')[1];
                let path_url = window.location.origin + params;
                if (type === 'doc' || type === 'docx' || type === 'xlsx' ||
                    type === 'xls' || type === 'ppt' || type === 'pptx'
                ) {
                    document.location.href = path_url
                } else {
                    window.open(path_url, 'hello')
                }
            },
            //移除
            handleRemove(file, fileList) {
                this.fileList = fileList;
                if (file.status != "ready") {
                    this.wikiData.annex_name = this.fileList;
                    this.$axios.post(this.$api.delWikiAnnexApi, {
                        file_name: file.name,
                        annex_name: this.wikiData.annex_name,
                        wikiId: this.wikiData.id
                    }).then((response) => {
                            this.messageShow(this, response)
                        }
                    )
                }
            },
            // 选取文件超过数量提示
            handleExceed(files, fileList) {
                this.$message.warning(`当前限制选择 5 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
            },
            //监控上传文件列表
            handleChange(file, fileList) {
                let existFile = fileList.slice(0, fileList.length - 1).find(f => f.name === file.name);
                if (existFile) {
                    this.$message.error('当前文件已经存在!');
                    fileList.pop();
                } else {
                    this.$axios.post(this.$api.checkWikiAnnexApi,
                        {
                            file_name: file.name
                        }).then((response) => {
                        if (response.data['status'] === 0) {
                            this.messageShow(this, response);
                            fileList.pop();
                        } else {
                            const isLt10M = file.size / 1024 / 1024 < 10;
                            if (!isLt10M) {
                                this.$message.error('请检查，上传文件大小不能超过1MB!');
                                fileList.pop();
                            }
                        }
                    });
                }
                this.fileList = fileList;
            },
        }
    }
</script>

<style>
    .el-upload-list {
        width: 500px;
    }
</style>