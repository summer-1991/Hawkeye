<template>
    <div class="caseHeader">
        <el-container>
            <el-container>
                <el-header style="height: 30px;">
                    <!--                    <div style="margin-top: -15px"><a style="color: #fff8f8" target="_blank" href="https://www.aliyun.com/minisite/goods?userCode=xd46ktom&share_source=aliyun_app">阿里云双12，服务器优化大促，想学习的可以买一台</a></div>-->
                    <!--                    <div style="float: left;">-->
                    <!--                        <el-breadcrumb separator-class="el-icon-arrow-right">-->
                    <!--                            <el-breadcrumb-item-->
                    <!--                                    v-for="(item, index) in title"-->
                    <!--                                    :key="index"-->
                    <!--                            >-->
                    <!--                                {{title[index]}}-->
                    <!--                            </el-breadcrumb-item>-->

                    <!--                        </el-breadcrumb>-->
                    <!--                    </div>-->
                    <el-dropdown style="float:right;line-height:20px;top:6px;color: rgb(255, 255, 255);"
                                 @command="logOut">
                        <span class="el-dropdown-link">{{userName}}<i
                                class="el-icon-arrow-down el-icon--right"></i></span>
                        <el-dropdown-menu slot="dropdown" style="line-height:10px">
                            <el-dropdown-item command="b">修改密码</el-dropdown-item>
                            <el-dropdown-item command="a">退出系统</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </el-header>

                <!--<el-footer style="height: 30px;">-->
                <!--<span class="demonstration">author</span>-->
                <!--</el-footer>-->
            </el-container>
        </el-container>
        <el-dialog
                title="修改密码"
                :visible.sync="passwordData.formVisible"
                width="30%"
                customClass="password-style"
        >
            <el-form>

                <el-form-item label="旧密码" :label-width="passwordData.formLabelWidth">
                    <el-input v-model="passwordData.oldPassword" type="password">
                    </el-input>
                </el-form-item>
                <el-form-item label="新密码" :label-width="passwordData.formLabelWidth">
                    <el-input v-model="passwordData.newPassword" type="password">
                    </el-input>
                </el-form-item>
                <el-form-item label="确认密码" :label-width="passwordData.formLabelWidth">
                    <el-input v-model="passwordData.surePassword" type="password">
                    </el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                    <el-button @click="passwordData.formVisible = false" size="small">取 消</el-button>
                    <el-button type="primary" @click.native="changePassword()" size="small">确 定</el-button>
                </span>
        </el-dialog>
    </div>
</template>

<script>
    import * as types from '../../store/types'

    export default {

        name: 'caseHeader',
        data() {
            return {
                title: ['项目管理', '项目'],
                userName: '',
                passwordData: {
                    oldPassword: '',
                    newPassword: '',
                    surePassword: '',
                    formVisible: false,
                    formLabelWidth: '80px',
                },
            }
        },
        methods: {
            getUserName() {
                // this.$store.state.userName = this.userName;
                this.userName = this.$store.state.userName;
            },
            changePassword() {
                // this.$store.state.userName = this.userName;
                this.$axios.post(this.$api.changePasswordApi,
                    {
                        'oldPassword': this.passwordData.oldPassword,
                        'newPassword': this.passwordData.newPassword,
                        'surePassword': this.passwordData.surePassword,

                    }).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.passwordData.formVisible = false;
                        }
                    }
                );
            },
            logOut(command) {
                if (command === "a") {
                    this.$store.commit(types.LOGOUT);
                    this.$router.push({path: '/login'});
                    this.$axios.get(this.$api.logoutApi).then((response) => {
                            if (response.data['status'] === 0) {
                                this.$message({
                                    showClose: true,
                                    message: response.data['msg'],
                                    type: 'warning',
                                });
                            }
                            else {
                                this.tableData = response.data['msg'];
                            }
                        }
                    );
                }
                else if (command === 'b') {
                    this.passwordData.oldPassword = '';
                    this.passwordData.newPassword = '';
                    this.passwordData.surePassword = '';
                    this.passwordData.formVisible = true;
                }
            },

            showTitle(path) {
                if (path === '/manage/projectManage') {
                    this.title = ['接口测试', '项目管理']
                }
                else if (path === '/manage/sdkManage') {
                    this.title = ['接口测试', 'SDK配置']
                }
                else if (path === '/manage/sceneConfig') {
                    this.title = ['接口测试', '项目函数']
                }
                else if (path === '/manage/buildInFunc') {
                    this.title = ['接口测试', '函数文件']
                }
                else if (path === '/manage/caseManage') {
                    this.title = ['接口测试', 'API用例']
                }
                else if (path === '/manage/sceneManage') {
                    this.title = ['接口测试', '业务用例']
                }
                else if (path === '/manage/reportManage') {
                    this.title = ['接口测试', '测试报告']
                }
                else if (path === '/manage/taskManage') {
                    this.title = ['接口测试', '定时任务']
                }
                else if (path === '/manage/manualSet') {
                    this.title = ['功能测试', '功能用例']
                }
                else if (path === '/manage/manualTask') {
                    this.title = ['功能测试', '测试任务']
                }
                else if (path === '/manage/wikiManage') {
                    this.title = ['其他程序', '文档库']
                }
                else if (path === '/manage/ganttModel') {
                    this.title = ['其他程序', '甘特图']
                }
                else if (path === '/manage/testResource') {
                    this.title = ['其他程序', '测试资源']
                }
                else if (path === '/manage/userManage') {
                    this.title = ['系统管理', '用户&权限']
                }
            },
            getTitle: function () {
                this.showTitle(this.$route.path);
            },
        },
        watch: {
            "$route": function (to) {

                this.showTitle(to.path);
                //from 对象中包含当前地址
                //to 对象中包含目标地址
                //其实还有一个next参数的，这个参数是控制路由是否跳转的，如果没写，可以不用写next()来代表允许路由跳转，如果写了就必须写next(),否则路由是不会生效的。
            }
        },
        mounted() {
            this.getTitle();
            this.getUserName()
        },
    }
</script>

<style>
    .el-header {
        background-color: #434650;
        color: #434650;

        line-height: 60px;
    }

    .password-style {
        line-height: 10px;
        border-radius: 5px;
    }

    .el-breadcrumb__inner {
        color: rgb(255, 255, 255);
    }

    .el-breadcrumb__item:last-child .el-breadcrumb__inner, .el-breadcrumb__item:last-child .el-breadcrumb__inner a, .el-breadcrumb__item:last-child .el-breadcrumb__inner a:hover, .el-breadcrumb__item:last-child .el-breadcrumb__inner:hover {
        color: rgb(255, 255, 255);
    }


</style>
