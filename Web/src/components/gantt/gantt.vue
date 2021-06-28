<template>
    <div class="app-container">
        <el-form :inline="true" class="demo-form-inline search-style" size="small">
            <el-form-item label="选择时间段">
                <el-date-picker
                        v-model="begin"
                        type="date"
                        placeholder="选择开始日期">
                </el-date-picker>
                ~
                <el-date-picker
                        v-model="end"
                        type="date"
                        placeholder="选择结束日期">
                </el-date-picker>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="el-icon-search" @click.native="reload()">查询</el-button>
            </el-form-item>
        </el-form>
        <div ref="gantt_div" class="left-container"/>
    </div>
</template>
<script>
    import gantt from 'dhtmlx-gantt'  // 引入模块
    import 'dhtmlx-gantt/codebase/dhtmlxgantt.css'

    export default {
        name: 'DhtmlxGantt',
        data() {
            return {
                tasks: {
                    data: [],
                    links: []
                },
                rowDragParent: 0,
                begin: '',
                end: ''
            }
        },
        methods: {
            period() {
                var firstDate = new Date();
                this.begin = firstDate.setDate(1); //第一天
                var endDate = new Date(firstDate);
                endDate.setMonth(firstDate.getMonth() + 1);
                this.end = endDate.setDate(0);
            },
            reload() {
                gantt.config.start_date = new Date(this.begin);
                gantt.config.end_date = new Date(this.end);

                //初始化
                gantt.init(this.$refs.gantt_div);
                gantt.showDate(new Date());
            },
            initGantt() {
                this.period();

                gantt.i18n.setLocale("cn");
                gantt.config.scale_unit = "day";
                gantt.config.date_scale = "%D,%d";
                gantt.config.min_column_width = 60;
                gantt.config.duration_unit = "day";
                gantt.config.scale_height = 20 * 3;
                gantt.config.row_height = 40;
                gantt.config.order_branch = true;
                gantt.config.order_branch_free = true;
                gantt.config.work_time = true;
                gantt.config.correct_work_time = true;
                gantt.config.open_tree_initially = true;
                gantt.config.initial_scroll = false;
                gantt.config.subscales = [{
                    unit: "month",
                    step: 1,
                    date: "%F,%Y"
                }, {
                    unit: "week",
                    step: 1,
                    template: function (date) {
                        var dateToStr = gantt.date.date_to_str("%m/%d");
                        var weekNum = gantt.date.date_to_str("(周%W)");
                        var endDate = gantt.date.add(gantt.date.add(date, 1, "week"), -1, "day");
                        return dateToStr(date) + " - " + dateToStr(endDate) + "" + weekNum(date);
                    }
                }];

                gantt.templates.task_text = function (start, end, task) {
                    if (task.progress != 0) {
                        var num = (task.progress * 100).toFixed(0);
                        return num + "%";
                    } else {
                        return "0%";
                    }
                };

                gantt.templates.timeline_cell_class = function (item, date) {
                    if (date.getDay() == 0 || date.getDay() == 6) {
                        return "weekend";
                    }
                    var formatDate = gantt.date.date_to_str("%Y/%n/%j")(date);
                    var currentDateStr = new Date().toLocaleDateString();
                    if (formatDate == currentDateStr) {
                        return "today";
                    }
                };

                gantt.templates.scale_cell_class = function (date) {
                    if (date.getDay() == 0 || date.getDay() == 6) {
                        return "weekend";
                    }
                    var formatDate = gantt.date.date_to_str("%Y/%n/%j")(date);
                    var currentDateStr = new Date().toLocaleDateString();
                    if (formatDate == currentDateStr) {
                        return "today";
                    }
                };

                gantt.config.start_date = new Date(this.begin);
                gantt.config.end_date = new Date(this.end);

                gantt.config.columns = [
                    {name: "text", tree: true, width: '300', align: "left", resize: true},
                    {name: "start_date", align: "center", resize: true},
                    {name: "duration", align: "center"},
                    {name: "add", label: ""}
                ];
                //初始化
                gantt.init(this.$refs.gantt_div);
            },
            addEvents() {
                gantt.attachEvent("onAfterTaskAdd", (id) => {
                    var task = gantt.getTask(id);
                    var task_data = {
                        text: task.text,
                        start_date: Date.parse(task.start_date) / 1000,
                        end_date: Date.parse(task.end_date) / 1000,
                        duration: task.duration,
                        progress: task.progress,
                        parent: task.parent,
                    };
                    this.doUpdateTask(id, task_data, 'GanttData');

                    if (task.parent != 0) {
                        this.updateParentDate(id, task.parent);
                    }
                    gantt.render();
                    return true;
                });

                gantt.attachEvent("onAfterTaskDelete", (id) => {
                    this.doDelTask(id, 'GanttData');
                    gantt.render();
                    return true;
                });

                gantt.attachEvent("onRowDragStart", (id) => {
                    this.rowDragParent = gantt.getTask(id).parent;
                    return true;
                });

                gantt.attachEvent("onRowDragEnd", (id) => {
                    var task = gantt.getTask(id);
                    if (task.parent != 0) {
                        this.updateParentDate(id, task.parent);
                    }

                    if (this.rowDragParent != task.parent) {
                        gantt.updateTask(id);
                    }
                    return true;
                });

                gantt.attachEvent("onAfterTaskDrag", (id) => {
                    var task = gantt.getTask(id);
                    if (task.parent != 0) {
                        this.updateParentDate(id, task.parent);
                    }
                    gantt.render();
                    return true;
                });

                gantt.attachEvent("onAfterTaskUpdate", (id) => {
                    var task = gantt.getTask(id);
                    var task_data = {
                        id: task.id,
                        text: task.text,
                        start_date: Date.parse(task.start_date) / 1000,
                        end_date: Date.parse(task.end_date) / 1000,
                        duration: task.duration,
                        progress: task.progress,
                        parent: task.parent,
                    };
                    this.doUpdateTask(0, task_data, 'GanttData');
                    gantt.render();
                    return true;
                });

                gantt.attachEvent("onAfterLinkAdd", (id) => {
                    var task = gantt.getLink(id);
                    var task_link = {
                        source: task.source,
                        target: task.target,
                        type: task.type,
                    };
                    this.doUpdateTask(id, task_link, 'GanttLink');
                    gantt.render();
                    return true;
                });

                gantt.attachEvent("onAfterLinkDelete", (id) => {
                    gantt.render();
                    this.doDelTask(id, 'GanttLink');
                    return true;
                });
            },
            findTasks() {
                this.$axios.post(this.$api.findGanttTask).then((response) => {
                        if (this.messageShow(this, response)) {
                            this.tasks.data = response.data['data'];
                            this.tasks.links = response.data['link'];
                            gantt.parse(this.tasks);
                        }
                    }
                )
            },
            updateParentDate(id, parent) {
                var task = gantt.getTask(id);
                var task_start_time = Date.parse(task.start_date);
                var task_end_time = Date.parse(task.end_date);

                var parent_task = gantt.getTask(parent);
                var parent_task_start_time = Date.parse(parent_task.start_date);
                var parent_task_end_time = Date.parse(parent_task.end_date);

                if (task_start_time < parent_task_start_time || task_end_time < parent_task_start_time) {
                    parent_task.start_date = new Date(task_start_time);
                    gantt.updateTask(parent);
                }

                if (task_end_time > parent_task_end_time || task_start_time > parent_task_end_time) {
                    parent_task.end_date = new Date(task_end_time);
                    gantt.updateTask(parent);
                }

                if (parent_task.parent != 0) {
                    this.updateParentDate(parent, parent_task.parent);
                }
                return true;
            },
            doUpdateTask(id, item, update_type) {
                this.$axios.post(this.$api.updateGanttTask, {
                    item: item,
                    'update_by': update_type
                }).then((response) => {
                        if (response.data['status'] === 1) {
                            if (id != 0) {
                                gantt.clearAll();
                                this.findTasks();
                            }
                        } else {
                            this.$message({
                                showClose: true,
                                message: response.data['msg'],
                                type: 'warning'
                            });
                        }
                    }
                )
            },
            doDelTask(id, update_type) {
                this.$axios.post(this.$api.delGanttTask, {
                    id: id,
                    'update_by': update_type
                }).then((response) => {
                        this.messageShow(this, response)
                    }
                )
            }
        },
        watch: {
            "$route": function () {
                gantt.showDate(new Date());
            }
        },
        mounted() {
            this.initGantt();
            //console.log(gantt.getTaskCount());
            // 数据解析
            this.findTasks();
            if (gantt.getTaskCount() == 0) {
                this.addEvents();
            }
            gantt.showDate(new Date());
        }
    }
</script>
<style>
    .left-container {
        height: 700px;
    }

    .weekend {
        background: #f4f7f4;
    }

    .gantt_selected .weekend {
        background: #f7eb91;
    }

    .today {
        background: #d0dc15;
    }
</style>