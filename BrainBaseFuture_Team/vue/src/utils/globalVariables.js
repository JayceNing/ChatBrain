import { reactive } from 'vue';

// 创建一个可修改的全局变量对象
export const globalVariables = reactive({
    login: 0,
    token: '',
    refreshToken: '',

    userBasic: {
        ImagePath: ''
    },

});