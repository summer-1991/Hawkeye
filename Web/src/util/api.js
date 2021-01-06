const baseDataApi = '/api/proGather/list';
const getFuncAddressApi = '/api/func/getAddress';

const findProApi = '/api/project/find';
const addProApi = '/api/project/add';
const editProApi = '/api/project/edit';
const delProApi = '/api/project/del';

const findReportApi = '/api/report/find';
const delReportApi = '/api/report/del';

const findModuleApi = '/api/module/find';
const addModuleApi = '/api/module/add';
const editModuleApi = '/api/module/edit';
const delModuleApi = '/api/module/del';
const stickModuleApi = '/api/module/stick';

const findConfigApi = '/api/config/find';
const addConfigApi = '/api/config/add';
const editConfigApi = '/api/config/edit';
const delConfigApi = '/api/config/del';

const loginApi = '/api/login';
const logoutApi = '/api/logout';
const registerApi = '/api/register';
const addRoleApi = '/api/addRole';
const delRoleApi = '/api/delRole';
const changePasswordApi = '/api/changePassword';

const findApiApi = '/api/apiMsg/find';
const delApiApi = '/api/apiMsg/del';
const runApiApi = '/api/apiMsg/run';
const addApiApi = '/api/apiMsg/add';
const editAndCopyApiApi = '/api/apiMsg/editAndCopy';

const findCaseSetApi = '/api/caseSet/find';
const delCaseSetApi = '/api/caseSet/del';
const addCaseSetApi = '/api/caseSet/add';
const stickCaseSetApi = '/api/caseSet/stick';

const startTaskApi = '/api/task/start';
const pauseTaskApi = '/api/task/pause';
const resumeTaskApi = '/api/task/resume';
const removeTaskApi = '/api/task/remove';
const runTaskApi = '/api/task/run';
const delTaskApi = '/api/task/del';
const editTaskApi = '/api/task/edit';
const addTaskApi = '/api/task/add';
const findTaskApi = '/api/task/find';

const findCaseApi = '/api/case/find';
const delCaseApi = '/api/case/del';
const runCaseApi = '/api/report/run';
const editCaseApi = '/api/case/edit';
const addCaseApi = '/api/case/add';
const configDataApi = '/api/config/data';


const fileUploadingApi = '/api/upload';
const checkFileApi = '/api/checkFile';
const importApiApi = '/api/apiMsg/fileChange';

const findFuncApi = '/api/func/find';
const createFuncApi = '/api/func/create';
const checkFuncApi = '/api/func/check';
const saveFuncApi = '/api/func/save';

const findUserApi = '/api/user/find';
const editUserApi = '/api/user/edit';
const delUserApi = '/api/user/del';
const changeStatusUserApi = '/api/user/changeStatus';

const addTestCaseFileApi = '/api/testCaseFile/add';
const findTestCaseFileApi = '/api/testCaseFile/find';
const delTestCaseFileApi = '/api/testCaseFile/del';
const getTestCaseFileApi = '/api/testCaseFile/get';
const saveTestCaseFileApi = '/api/testCaseFile/save';

const findCommonConfigApi = '/api/commonConfig/find';
const editCommonConfigApi = '/api/commonConfig/edit';
const delCommonConfigApi = '/api/commonConfig/del';
const addCommonConfigApi = '/api/commonConfig/add';

const findWikiApi = '/api/wiki/find';
const delWikiAnnexApi = '/api/wiki/annex';
const delWikiApi = '/api/wiki/del';
const addWikiApi = '/api/wiki/add';
const editAndCopyWikiApi = '/api/wiki/edit';
const checkWikiAnnexApi = '/api/wiki/check';

const findManualCaseApi = '/api/manual/findBySet';
const addManualCaseApi = '/api/manual/add';
const editAndCopyManualCaseApi = '/api/manual/edit';
const delManualCaseApi = '/api/manual/del';
const findTaskCaseApi = '/api/manual/findByTask';
const delTaskCaseApi = '/api/manual/delByTask';
const searchCaseApi = '/api/manual/searchCase';
const addCaseToTaskApi = '/api/manual/addToTask';
const runManualCaseApi = '/api/manual/runTaskCase';
const importCaseFile = '/api/manual/importCase';
const importManualCaseApi = '/api/manual/doImport';

const findGanttTask = '/api/gantt/find';
const updateGanttTask = '/api/gantt/update';
const delGanttTask = '/api/gantt/del';

export default {
    addTestCaseFileApi,
    findTestCaseFileApi,
    delTestCaseFileApi,
    getTestCaseFileApi,
    saveTestCaseFileApi,

    baseDataApi,
    getFuncAddressApi,
    checkFileApi,

    findUserApi,
    editUserApi,
    delUserApi,
    changeStatusUserApi,

    findReportApi,
    delReportApi,

    findFuncApi,
    createFuncApi,
    checkFuncApi,
    saveFuncApi,

    startTaskApi,
    pauseTaskApi,
    resumeTaskApi,
    removeTaskApi,
    runTaskApi,
    delTaskApi,
    editTaskApi,
    addTaskApi,
    findTaskApi,

    findCaseApi,
    delCaseApi,
    runCaseApi,
    editCaseApi,
    addCaseApi,
    configDataApi,

    findCaseSetApi,
    delCaseSetApi,
    addCaseSetApi,
    stickCaseSetApi,

    findProApi,
    addProApi,
    editProApi,
    delProApi,

    findModuleApi,
    addModuleApi,
    editModuleApi,
    delModuleApi,
    stickModuleApi,

    findConfigApi,
    addConfigApi,
    editConfigApi,
    delConfigApi,

    loginApi,
    logoutApi,
    registerApi,
    addRoleApi,
    delRoleApi,
    changePasswordApi,

    findApiApi,
    delApiApi,
    runApiApi,
    addApiApi,
    editAndCopyApiApi,

    fileUploadingApi,
    importApiApi,

    findCommonConfigApi,
    editCommonConfigApi,
    delCommonConfigApi,
    addCommonConfigApi,

    findWikiApi,
    editAndCopyWikiApi,
    delWikiApi,
    addWikiApi,
    delWikiAnnexApi,
    checkWikiAnnexApi,

    findManualCaseApi,
    editAndCopyManualCaseApi,
    delManualCaseApi,
    addManualCaseApi,
    findTaskCaseApi,
    delTaskCaseApi,
    searchCaseApi,
    addCaseToTaskApi,
    runManualCaseApi,
    importCaseFile,
    importManualCaseApi,

    findGanttTask,
    updateGanttTask,
    delGanttTask,
}