<template>
    <div class="sdkManage" v-loading="this.loading">
        <el-form :inline="true" class="demo-form-inline search-style" size="small">
            <el-form-item label="客户端id" labelWidth="110px">
                <el-input placeholder="请输入" v-model="form.c_key" clearable>
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="handleCurrentChange(1)">搜索
                </el-button>
                <el-button type="primary" @click.native="initClientData()" v-if="role == '2' || auth.api_sdk_add">
                    添加客户端配置
                </el-button>
            </el-form-item>
            <el-popconfirm title="是否确认删除选中的数据？" @onConfirm="batchDelClient()">
                <el-button type="danger" slot="reference" icon="el-icon-delete" size="small"
                           v-show="role === '2' || auth.api_report_del">批量删除
                </el-button>
            </el-popconfirm>
        </el-form>
        <el-tabs value="first" style="padding-left: 10px">
            <el-tab-pane label="客户端列表" name="first" class="table_padding">
                <el-table
                        ref="multipleTable"
                        :data="clientTableData"
                        stripe max-height="725"
                        @selection-change="handleSelectionChange">
                     <el-table-column
                            type="selection"
                            width="55">
                     </el-table-column>
                    <el-table-column
                            prop="c_key"
                            label="客户端id"
                            width="150">
                    </el-table-column>
                    <el-table-column
                            prop="c_value"
                            label="客户端密钥">
                    </el-table-column>
                    <el-table-column
                            prop="desc"
                            label="说明">
                    </el-table-column>
                    <el-table-column
                            label="操作"
                    >
                        <template slot-scope="scope">
                            <el-button type="primary" icon="el-icon-edit" size="mini"
                                       @click.native="editClient(clientTableData[scope.$index]['id'])"
                                       v-if="role == '2' || auth.api_sdk_edit">编辑
                            </el-button>
                            <el-button type="danger" icon="el-icon-delete" size="mini"
                                       @click.native="sureView(delClient,clientTableData[scope.$index]['id'],clientTableData[scope.$index]['c_key'])"
                                       v-if="role == '2' || auth.api_sdk_del">
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
                <div>
                    <el-button size="mini" @click="toggleSelection()">取消选择</el-button>
                </div>

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

        <el-dialog
                title="客户端设置"
                :visible.sync="clientData.clientAddStatus"
                width="30%"
        >
            <el-form>
                <el-form-item label="键key" :label-width="clientData.formLabelWidth" prop="num">
                    <el-input v-model.number="clientData.c_key">
                    </el-input>
                </el-form-item>
                <el-form-item label="密钥value" :label-width="clientData.formLabelWidth">
                    <el-input v-model="clientData.c_value">
                    </el-input>
                </el-form-item>
                <el-form-item label="说明" :label-width="clientData.formLabelWidth">
                    <el-input type="textarea" :rows="2" v-model="clientData.desc" placeholder="请输入"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                    <el-button @click="clientData.clientAddStatus = false" size="small">取 消</el-button>
                    <el-button type="primary" @click.native="addClient()" size="small">确 定</el-button>
                </span>
        </el-dialog>
    </div>
</template>

<script>

    export default {
        components: {},
        name: 'sdkManage',
        data() {
            return {
                loading: false,  //  页面加载状态开关
                clientTableData: Array(),
                tableCheckedIds: [],
                total: 1,
                currentPage: 1,
                sizePage: 20,
                form: {
                    c_key: '',
                },
                clientData: {
                    id: null,
                    c_key: '',
                    c_value: '',
                    desc: '',
                    clientAddStatus: false,
                    formLabelWidth: '100px',
                },
                configType: 'client',
                role: '',
                auth: '',
            }
        },
        methods: {
            addClient() {
                this.$axios.post(this.$api.addCommonConfigApi, {
                    'id': this.clientData.id,
                    'c_key': this.clientData.c_key,
                    'c_value': this.clientData.c_value,
                    'c_type': this.configType,
                    'desc': this.clientData.desc,
                }).then((response) => {
                        if (response.data['status'] === 0) {
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'warning',
                            });
                        } else {
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'success',
                            });
                            this.findClient();
                            this.clientData.clientAddStatus = false;
                        }
                    }
                )
            },

            handleCurrentChange(val) {
                this.currentPage = val;
                this.findClient()
            },
            handleSizeChange(val) {
                this.sizePage = val;
                this.findClient()
            },
            findClient() {
                this.role = this.$store.state.roles;
                this.auth = JSON.parse(this.$store.state.auth);

                this.$axios.post(this.$api.findCommonConfigApi, {
                    'c_key': this.form.c_key,
                    'c_type': this.configType,
                    'page': this.currentPage,
                    'sizePage': this.sizePage,
                }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.clientTableData = response.data['data'];
                            this.total = response.data['total'];
                        }
                    }
                )
            },
            initClientData() {
                this.clientData.id = null;
                this.clientData.c_key = '';
                this.clientData.c_value = '';
                this.clientData.desc = '';
                this.clientData.clientAddStatus = true;
            },
            editClient(id) {
                this.$axios.post(this.$api.editCommonConfigApi, {'id': id}).then((response) => {
                        this.clientData.id = id;
                        this.clientData.c_key = response.data['data']['c_key'];
                        this.clientData.c_value = response.data['data']['c_value'];
                        this.clientData.desc = response.data['data']['desc'];
                        this.clientData.clientAddStatus = true;
                    }
                )
            },
            delClient(id) {
                this.$axios.post(this.$api.delCommonConfigApi, {'id': id}).then((response) => {
                        this.messageShow(this, response);

                        // 分页数量判断，当删除了某一页的最后一条数据后，分页数量-1
                        if ((this.currentPage - 1) * this.sizePage + 1 === this.total) {
                            this.currentPage = this.currentPage - 1
                        }
                        this.findClient();
                    }
                )
            },
            toggleSelection() {
                this.$refs.multipleTable.clearSelection();
            },
            handleSelectionChange(val) {
//                console.log(val)
                let ids = []
                if (val && val.length > 0) {
                    for (var i = 0; i < val.length; i++) {
//                        console.log(val[i].id)
                        ids.push(val[i].id)
                    }
                    this.tableCheckedIds = ids
                } else {
                    this.tableCheckedIds = []
                }
            },
            batchDelClient(){
                if(this.tableCheckedIds.length==0){
                    return false
                }
                this.$axios.delete(
                    this.$api.batchDelClientApi,{"data":this.tableCheckedIds}
                ).then((response) => {
                        this.messageShow(this, response);
                        // 分页数量判断，当删除了某一页的最后一条数据后，分页数量-1
                        if ((this.currentPage - 1) * this.sizePage + 1 === this.total) {
                            this.currentPage = this.currentPage - 1
                        }
                        this.handleCurrentChange();
                    }
                )
            },
     },
        mounted() {
            this.findClient();
        }
        ,
    }
</script>
<style>
</style>
