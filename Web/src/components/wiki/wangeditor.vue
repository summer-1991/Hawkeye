<template lang="html">
    <div class="editor">
        <div ref="toolbar" class="toolbar">
        </div>
        <div ref="editor" class="text">
        </div>
    </div>
</template>

<script>
    import './wangeditor/wangEditor.css'

    var E = require('./wangeditor/wangEditor.js');

    export default {
        name: 'editoritem',
        data() {
            return {
                editor: null,
                info_: null,
                isChange: false,
            }
        },
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            value: {
                type: String,
                default: ''
            },
            isClear: {
                type: Boolean,
                default: false
            }
        },
        watch: {
            isClear(val) {
                if (val) {
                    this.editor.txt.clear();
                    this.info_ = null;
                }
            },
            value: function (value) {
                if (!this.isChange) {
                    this.editor.txt.html(this.value);
                }
                this.isChange = false;
            }
            //value为编辑框输入的内容，这里我监听了一下值，当父组件调用得时候，如果给value赋值了，子组件将会显示父组件赋给的值
        },
        mounted() {
            this.seteditor();
            this.editor.txt.html(this.value);
        },
        methods: {
            seteditor() {
                this.editor = new E(this.$refs.toolbar, this.$refs.editor);
                this.editor.customConfig.showLinkImg = false;
                this.editor.customConfig.uploadImgShowBase64 = false; // base 64 存储图片
                this.editor.customConfig.uploadImgServer = '/api/upload/pic';// 配置服务器端地址
                this.editor.customConfig.uploadImgHeaders = {};// 自定义 header
                this.editor.customConfig.uploadFileName = 'file'; // 后端接受上传文件的参数名
                this.editor.customConfig.uploadImgMaxSize = 2 * 1024 * 1024; // 将图片大小限制为 2M
                this.editor.customConfig.uploadImgMaxLength = 6; // 限制一次最多上传 3 张图片
                this.editor.customConfig.uploadImgTimeout = 3 * 60 * 1000; // 设置超时时间

                // 配置菜单
                this.editor.customConfig.menus = [
                    'head', // 标题
                    'bold', // 粗体
                    'fontSize', // 字号
                    'fontName', // 字体
                    'italic', // 斜体
                    'underline', // 下划线
                    'strikeThrough', // 删除线
                    'foreColor', // 文字颜色
                    'backColor', // 背景颜色
                    'link', // 插入链接
                    'list', // 列表
                    'justify', // 对齐方式
                    'quote', // 引用
                    'emoticon', // 表情
                    'image', // 插入图片
                    'table', // 表格
                    'code', // 插入代码
                    'undo', // 撤销
                    'redo', // 重复
                ];

                this.editor.customConfig.uploadImgHooks = {
                    fail: (xhr, editor, result) => {
                        // 插入图片失败回调
                    },
                    success: (xhr, editor, result) => {
                        // 图片上传成功回调
                    },
                    timeout: (xhr, editor) => {
                        // 网络超时的回调
                    },
                    error: (xhr, editor) => {
                        // 图片上传错误的回调
                    },
                    customInsert: (insertImg, result, editor) => {
                        // 图片上传成功，插入图片的回调
                        //result为上传图片成功的时候返回的数据，这里我打印了一下发现后台返回的是data：[{url:"路径的形式"},...]

                        //insertImg()为插入图片的函数
                        //循环插入图片
                        let data = result.data;
                        let data_len = data.length;
                        for (let i = 0; i < data_len; i++) {
                            let url = window.location.origin + data[i];
                            insertImg(url);
                        }
                    }
                };
                this.editor.customConfig.onchange = (html) => {
                    this.isChange = true;
                    this.info_ = html; // 绑定当前逐渐地值
                    this.$emit('change', this.info_) // 将内容同步到父组件中
                };
                // 创建富文本编辑器
                this.editor.create()
            }
        }
    }
</script>

<style>
    .editor {
        position: relative;
        z-index: 0;
    }

    .toolbar {
        border: 1px solid #ccc;
    }

    .text {
        border: 1px solid #ccc;
        height: 400px;
    }
</style>