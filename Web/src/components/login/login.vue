<template>
    <div class="page-login">
<!--        <img src="../assets/logo.png">-->
        <div class="page-login--layer page-login--layer-area">
            <ul class="circles">
                <li v-for="n in 10" :key="n"></li>
            </ul>
        </div>
        <div class="page-login--layer">
            <div
                    class="page-login--content"
                    flex="dir:top main:justify cross:center box:justify">
                <div class="page-login--content-header">
                </div>
                <div
                        class="page-login--content-main"
                        flex="dir:top main:center cross:center">
                    <!-- logo -->
                    <!-- 表单 -->

                    <div class="page-login--form">
                        <div class="page-login--content-footer">
                            <p class="page-login--content-footer-copyright"
                               style="font-size:26px;font-weight:700;font-family:KaiTi">
                                测试平台
                            </p>
                        </div>
                        <el-card shadow="never">
                            <el-form ref="loginForm" label-position="top" size="default">
                                <el-form-item>
                                    <el-input type="text" v-model="account" placeholder="用户名">
                                        <i slot="prepend" class="my-icon-yonghu"></i>
                                    </el-input>
                                </el-form-item>
                                <el-form-item>
                                    <el-input type="password" v-model="password" placeholder="密码">
                                        <i slot="prepend" class="my-icon-jianpan"></i>
                                    </el-input>
                                </el-form-item>
                                <el-button size="default" @click.native="login()" type="primary" class="button-login">
                                    登录
                                </el-button>
                            </el-form>
                        </el-card>
                        <p class="page-login--options"
                           flex="main:justify cross:center">
                            <el-tooltip class="item" effect="dark" content="请联系管理员重置密码" placement="bottom">
                                <span> 忘记密码</span>
                            </el-tooltip>
                        </p>
                    </div>
                </div>
<!--                <div class="page-login&#45;&#45;content-footer">

                    <p class="page-login&#45;&#45;content-footer-copyright">
                        <a href="https://github.com/pencil1/ApiTestWeb" target="view_window">ApiTestWeb 作品</a> |
                        <a href="https://github.com/pencil1/ApiTestManage" target="view_window">ApiTestManage 作品</a>
                    </p>

                </div>-->
            </div>
        </div>
    </div>
</template>

<script>
    import * as types from '../../store/types'

    export default {
        data() {
            return {
                token: '',
                account: '',
                password: '',
            }
        },

        methods: {

            login() {
                this.$axios.post(this.$api.loginApi, {
                    'account': this.account,
                    'password': this.password,
                }).then((response) => {
                        if (response.data['status'] === 0) {
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'warning',
                            });
                        } else {
                            this.token = response.data['token'];
                            if (this.token) {
                                this.$store.commit(types.LOGIN, this.token);
                                this.$store.commit(types.ROLES, response.data['roles']);
                                this.$store.commit('roles', response.data['roles']);
                                // console.log(this.$store.state.role)
                                // console.log(this.$store.state.userName)
                                this.$store.commit(types.USERNAME, response.data['name']);
                                this.$store.commit('userName', response.data['name']);
                                this.initAuth(response.data['auth']);

                                let redirect = decodeURIComponent(this.$route.query.redirect || '/manage/projectManage');
                                this.$router.push({path: redirect})
                            }
                        }
                    }
                );

            },
            initAuth(authData) {
                const auth = {
                    "api_project": false,
                    "api_project_add": false,
                    "api_project_edit": false,
                    "api_project_del": false,
                    "api_sdk": false,
                    "api_sdk_add": false,
                    "api_sdk_edit": false,
                    "api_sdk_del": false,
                    "api_config": false,
                    "api_config_add": false,
                    "api_config_edit": false,
                    "api_config_del": false,
                    "api_func": false,
                    "api_func_add": false,
                    "api_func_run": false,
                    "api_func_save": false,
                    "api_api": false,
                    "api_api_add": false,
                    "api_api_todo": false,
                    "api_api_edit": false,
                    "api_api_del": false,
                    "api_api_run": false,
                    "api_scene": false,
                    "api_scene_add": false,
                    "api_scene_todo": false,
                    "api_scene_edit": false,
                    "api_scene_del": false,
                    "api_scene_run": false,
                    "api_scene_batch": false,
                    "api_task": false,
                    "api_task_add": false,
                    "api_task_todo": false,
                    "api_task_edit": false,
                    "api_task_del": false,
                    "api_task_run": false,
                    "api_report": false,
                    "api_report_del": false,
                    "manual_case": false,
                    "manual_case_todo": false,
                    "manual_case_save": false,
                    "others_wiki": false,
                    "others_wiki_add": false,
                    "others_wiki_todo": false,
                    "others_wiki_edit": false,
                    "others_wiki_del": false,
                    "others_mind": false,
                    "others_resources": false,
                    "others_resources_add": false,
                    "others_resources_edit": false,
                    "others_resources_del": false,
                };

                if (authData != 0) {
                    let temp = "";
                    let un = 0;
                    for (let key in auth) {
                        if (un == 1 && key.indexOf(temp) != -1) {
                            auth[key] = false;
                            continue;
                        } else {
                            un = 0;
                            temp = '';
                        }

                        let keyList = key.split("_");
                        if (keyList.length == 2) {
                            let i = keyList[0];
                            let j = keyList[1];
                            if (authData[i] == undefined || authData[i]["manage"][j] == undefined) {
                                temp = key;
                                un = 1;
                                auth[key] = false;
                                continue;
                            } else {
                                auth[key] = authData[i]["manage"][j]["checked"];
                            }
                        } else {
                            let i = keyList[0];
                            let j = keyList[1];
                            let k = keyList[2];
                            if (authData[i]["manage"][j]["option"][k] == undefined) {
                                auth[key] = false;
                            } else {
                                auth[key] = authData[i]["manage"][j]["option"][k]["checked"]
                            }
                        }
                    }
                }

                this.$store.commit(types.AUTH, JSON.stringify(auth));
                this.$store.commit("auth", JSON.stringify(auth));
            },
        }
    }
</script>

<style lang="scss">


    .page-login {
        @extend %unable-select;
        $backgroundColor: #F0F2F5;
        // ---
        background-color: $backgroundColor;
        height: 100%;
        width: 100%;
        position: absolute;
        // 层
        .page-login--layer {
            @extend %full;
            overflow: auto;
            position: absolute;
        }

        .page-login--layer-area {
            overflow: hidden;
        }

        // 时间
        .page-login--layer-time {
            font-size: 24em;
            font-weight: bold;
            color: rgba(0, 0, 0, 0.03);
            overflow: hidden;
        }

        // 登陆页面控件的容器
        .page-login--content {
            height: 100%;
            min-height: 500px;
        }

        // header
        .page-login--content-header {
            padding: 1em 0;

            .page-login--content-header-motto {
                margin: 0px;
                padding: 0px;
                color: $color-text-normal;
                text-align: center;
                font-size: 12px;

                span {
                    color: $color-text-sub;
                }
            }
        }

        // main
        .page-login--logo {
            width: 240px;
            margin-bottom: 2em;
            margin-top: -2em;
        }

        // 登录表单
        .page-login--form {
            margin: auto;
            width: 280px;
            margin-top: 10%;
            // 卡片
            .el-card {
                margin-bottom: 15px;
            }

            // 登录按钮
            .button-login {
                width: 100%;
            }

            // 输入框左边的图表区域缩窄
            .el-input-group__prepend {
                padding: 0px 14px;
            }

            .login-code {
                height: 40px - 2px;
                display: block;
                margin: 0px -20px;
                border-top-right-radius: 2px;
                border-bottom-right-radius: 2px;
            }

            // 登陆选项
            .page-login--options {
                margin: 0px;
                padding: 0px;
                font-size: 14px;
                color: $color-primary;
                margin-bottom: 15px;
                font-weight: bold;
            }

            .page-login--quick {
                width: 100%;
            }
        }

        // 快速选择用户面板
        .page-login--quick-user {
            @extend %flex-center-col;
            padding: 10px 0px;
            border-radius: 4px;

            &:hover {
                background-color: $color-bg;

                i {
                    color: $color-text-normal;
                }

                span {
                    color: $color-text-normal;
                }
            }

            i {
                font-size: 36px;
                color: $color-text-sub;
            }

            span {
                font-size: 12px;
                margin-top: 10px;
                color: $color-text-sub;
            }
        }

        // footer
        .page-login--content-footer {
            padding: 1em 0;

            .page-login--content-footer-options {
                padding: 0px;
                margin: 0px;
                margin-bottom: 10px;
                font-size: 14px;
                text-align: center;

                a {
                    color: $color-text-normal;
                    margin: 0 1em;
                }
            }

            .page-login--content-footer-copyright {
                text-align: center;
                padding: 0px;
                margin: 0px;
                font-size: 12px;
                color: $color-text-normal;

                a {
                    color: $color-text-normal;
                }
            }
        }

        // 背景
        .circles {
            position: absolute;
            top: 0;
            left: 0;
            width: 96%;
            height: 96%;
            overflow: hidden;

            li {
                position: absolute;
                display: block;
                list-style: none;
                width: 20px;
                height: 20px;
                background: #FFF;
                animation: animate 25s linear infinite;
                bottom: -200px;
                @keyframes animate {
                    0% {
                        transform: translateY(0) rotate(0deg);
                        opacity: 1;
                        border-radius: 0;
                    }
                    100% {
                        transform: translateY(-1000px) rotate(720deg);
                        opacity: 0;
                        border-radius: 50%;
                    }
                }

                &:nth-child(1) {
                    left: 15%;
                    width: 80px;
                    height: 80px;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    left: 5%;
                    width: 20px;
                    height: 20px;
                    animation-delay: 2s;
                    animation-duration: 12s;
                }

                &:nth-child(3) {
                    left: 70%;
                    width: 20px;
                    height: 20px;
                    animation-delay: 4s;
                }

                &:nth-child(4) {
                    left: 40%;
                    width: 60px;
                    height: 60px;
                    animation-delay: 0s;
                    animation-duration: 18s;
                }

                &:nth-child(5) {
                    left: 65%;
                    width: 20px;
                    height: 20px;
                    animation-delay: 0s;
                }

                &:nth-child(6) {
                    left: 75%;
                    width: 150px;
                    height: 150px;
                    animation-delay: 3s;
                }

                &:nth-child(7) {
                    left: 35%;
                    width: 200px;
                    height: 200px;
                    animation-delay: 7s;
                }

                &:nth-child(8) {
                    left: 50%;
                    width: 25px;
                    height: 25px;
                    animation-delay: 15s;
                    animation-duration: 45s;
                }

                &:nth-child(9) {
                    left: 20%;
                    width: 15px;
                    height: 15px;
                    animation-delay: 2s;
                    animation-duration: 35s;
                }

                &:nth-child(10) {
                    left: 85%;
                    width: 150px;
                    height: 150px;
                    animation-delay: 0s;
                    animation-duration: 11s;
                }
            }
        }
    }
</style>
