<template>
    <div class="font-set">

            <el-container style="min-height: 80vh">



            <el-aside :width="sideWidth +'px'"
                      style="text-align:center; background-color: black; box-shadow: 2px 0px 6px rgba(0,21,41,0.35);">


                <div style="position:relative;text-align: right;">
                    <font-awesome-icon style="margin: 5px; color: #e5f1fb" class="fa-2x" :icon="['fas', 'bars']" @click="collapse"/>
                </div>

                <div v-if="sideView == 1">
<!--                    <el-radio-group v-model="funcSelect" size="large" fill="#81f54b" @update:modelValue="changeFunc">-->
<!--                        <el-radio-button label="LLM对话" />-->
<!--                        <el-radio-button label="知识库问答" />-->
<!--                        <el-radio-button label="提示词" />-->
<!--                        <el-radio-button label="内容生成" />-->
<!--                    </el-radio-group>-->

                    <div v-if="funcSelect=='LLM对话'">
                        <h1 style="font-size: 24px;color: white;">请选择使用的模型</h1>
                        <el-radio-group v-model="modelSelect" size="large" fill="#81f54b" @update:modelValue="changeModel">
                            <el-radio-button label="ChatGLM2" />
                            <el-radio-button label="InternLM" />
                            <el-radio-button label="ChatGPT" />
                            <el-radio-button label="星火" />
                        </el-radio-group>

                        <h1 style="font-size: 24px;color: white;">系统提示词</h1>
                        <h2 style="font-size: 16px;color: white;">用户输入</h2>
                        <el-input
                            v-model="history[0][0]"
                            :rows="10"
                            type="textarea"
                            placeholder="请输入系统提示词"
                            style="width: 80%"
                        />
                        <h2 style="font-size: 16px;color: white;">AI输出</h2>
                        <el-input
                            v-model="history[0][1]"
                            :rows="10"
                            type="textarea"
                            placeholder="请输入系统提示词"
                            style="width: 80%;"
                        />
                    </div>

                    <div v-if="funcSelect=='知识库问答'">
                        <h1 style="font-size: 24px;color: white;">知识库选择</h1>

                        <el-select v-model="selectedValue" class="m-2" placeholder="请选择知识库" size="large">
                            <el-option
                                v-for="kb in kbs"
                                :key="kb"
                                :label="kb"
                                :value="kb"
                            />
                        </el-select>

                        <h2 style="font-size: 20px;color: white;">知识库包含内容</h2>

                        <ul class="list-files" style="overflow: auto">
                            <li v-for="i in listFiles" :key="i" class="list-files-item">{{ i }}</li>
                        </ul>

                        <div style="width: 80%;margin-left: 10%">
                            <el-upload
                                class="upload-demo"
                                drag
                                :http-request="upload"
                                :show-file-list=false
                            >
                                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                                <div class="el-upload__text">
                                    拖拽文件到此处或者 <em>点击上传</em>
                                </div>
                            </el-upload>

                            <div v-if="isUploading==1"  style="margin-left: 10%;margin-top: 15px">
                                <el-progress
                                    :percentage="100"
                                    status="warning"
                                    :indeterminate="true"
                                    :duration="1"
                                />
                            </div>
                        </div>
                    </div>

                    <div v-if="funcSelect=='提示词'">
                        <h1 style="font-size: 24px;color: white;">提示词仓库</h1>
                        <h2 style="font-size: 12px;color: white;">为鼓励使用国内模型，目前提示词仓库仅支持ChatGLM2</h2>

                        <el-select v-model="selectedPromptBase" class="m-2" style="width: 160px;margin-right: 20px" placeholder="请选择提示词仓库" size="large">
                            <el-option
                                v-for="pb in pbs"
                                :key="pb.Name"
                                :label="pb.Name"
                                :value="pb.Name"
                            />
                        </el-select>

                        <el-button type="primary" @click="pop8">新增</el-button>


                        <el-button type="danger" slot="reference" @click="pop7">删除</el-button>


                        <h2 style="font-size: 20px;color: white;">提示词仓库包含内容</h2>

                        <ul class="list-files" style="overflow: auto">
                            <li v-for="i in listPrompts" :key="i.Name" class="list-files-item" @click="setPrompt(i.Prompt)">{{ i.Name }} <el-button type="danger" style="margin-left: 10px" @click="deletePrompt(i.Name)">删除</el-button></li>
                        </ul>

                        <el-button type="primary" @click="pop9">新建提示词</el-button>

                        <div class="markdown-body" style="background-color: white;height: 240px;width: 80%;margin-left: 10%;margin-top: 20px;overflow: auto">
                            {{prompt}}
                        </div>

                    </div>

                    <div v-if="funcSelect=='内容生成'">
                        <h1 style="font-size: 24px;color: white;">一键内容生成</h1>
                        <el-radio-group v-model="modelSelect" size="large" fill="#81f54b" @update:modelValue="changeFunc">
                            <el-radio-button label="星火" />
                            <!-- <el-radio-button label="ChatGPT" /> -->
<!--                            <el-radio-button label="ChatGLM2" />-->

                        </el-radio-group>
                        <h1 style="font-size: 18px;color: white;">功能选择</h1>
                        <el-select v-model="selectedGCFunc" class="m-2" placeholder="请选择功能" size="large">
                            <el-option
                                v-for="func in gcfuncs"
                                :key="func"
                                :label="func"
                                :value="func"
                            />
                        </el-select>


                        <el-button :disabled="GCBtnDisabled" type="primary" @click="generateContent(0)">{{GCStateBtn}}</el-button>


                        <div v-if="selectedGCFunc=='arxiv文章总结'">
                            <h1 style="font-size: 18px;color: white;">数据库中现有文章数：{{articleNum}}</h1>
                            <el-button type="primary" @click="arxivSearchPage">{{arxivSearchBtn}}</el-button>
                            <ul class="list-files" style="overflow: auto;height: 200px">

                                <div v-for="i in listGCArticles" style="background-color: white;padding: 10px;margin-bottom: 10px">
                                    <li v-if="i.value == 0" class="list-files-item" @click="setGCArticle(i.title)">
                                        {{ i.title }}
                                    </li>
                                    <li v-if="i.value == 1" class="list-files-item" style="background-color: yellow" @click="setGCArticle(i.title)">
                                        {{ i.title }}
                                    </li>
                                    <div style="display: flex;">
                                        {{i.query}}

                                        <!-- ：{{i.key}} -->

                                        <el-button v-if="i.value == 0" type="warning" style="margin-left: 10px" @click="updateGCBase(i.value,i.title)">标记</el-button>
                                        <el-button v-if="i.value == 1" type="danger" style="margin-left: 10px" @click="updateGCBase(i.value,i.title)">取消标记</el-button>
                                    </div>

                                </div>

                            </ul>
                            <h1 style="font-size: 18px;color: white;">参数设置</h1>
                            <div style="width: 80%;margin-left: 10%;">
                                <div style="display: flex;height: 40px">
                                    <h2 style="font-size: 16px;color: white;width: 120px">搜索</h2>
                                    <el-input v-model="arxivgc.query" placeholder="查询内容，如:LLM Model" />
                                </div>

                                <!-- <div style="display: flex;height: 40px">
                                    <h2 style="font-size: 16px;color: white;width: 120px">关键词</h2>
                                    <el-input v-model="arxivgc.keyword" placeholder="关键词，如:langchain" />
                                </div> -->

                                <div style="display: flex;height: 40px">
                                    <h2 style="font-size: 16px;color: white;width: 120px">查询页数</h2>
                                    <el-input v-model="arxivgc.pagenum" placeholder="查询页数，如:1" />
                                </div>

                                <!-- <div style="display: flex;height: 40px">
                                    <h2 style="font-size: 16px;color: white;width: 120px">最大文章数</h2>
                                    <el-input v-model="arxivgc.maxresults" placeholder="最大文章数，如:3" />
                                </div> -->

                                <div style="display: flex;height: 40px">
                                    <h2 style="font-size: 16px;color: white;width: 120px">文章时限</h2>
                                    <el-input v-model="arxivgc.days" placeholder="文章时限，代表几天内，如:1" />
                                </div>
                            </div>

                        </div>


                        <div v-if="literatureReviewFunc.includes(selectedGCFunc)">
                            <h1 style="font-size: 18px;color: white;">选择总结领域</h1>
                            <el-select v-model="selectedQuery" class="m-2" placeholder="历史搜索" size="large">
                                <el-option
                                    v-for="query in queryHistory"
                                    :key="query"
                                    :label="query"
                                    :value="query"
                                />
                            </el-select>
                            <h1 style="font-size: 18px;color: white;">当前领域下共有文章 {{selectedQueryNum}} 篇</h1>
                            <div v-if="selectedGCFunc=='关键词综述生成'">
                                <h1 style="font-size: 18px;color: white;">选择关键词</h1>
                                <el-select v-model="selectedKey" class="m-2" placeholder="关键词" size="large">
                                    <el-option
                                        v-for="keyname in fieldKey"
                                        :key="keyname"
                                        :label="keyname"
                                        :value="keyname"
                                        />
                                </el-select>
                                <el-button :disabled="GCBtnDisabled" type="primary" @click="freshKey">刷新</el-button>
                                <h1 style="font-size: 18px;color: white;">选择文章采样方法</h1>
                                <el-select v-model="selectedselectmethod" class="m-2" placeholder="采样方法" size="large">
                                    <el-option
                                        v-for="selectmethod in selectmethods"
                                        :key="selectmethod"
                                        :label="selectmethod"
                                        :value="selectmethod"
                                        />
                                </el-select>
                            </div>

                        </div>

                        <div v-if="selectedGCFunc=='领域综述生成'">
                            <h1 style="font-size: 18px;color: white;">选择总结领域</h1>
                            <el-select v-model="selectedQuery" class="m-2" placeholder="历史搜索" size="large">
                                <el-option
                                    v-for="query in queryHistory"
                                    :key="query"
                                    :label="query"
                                    :value="query"
                                />
                            </el-select>
                            <h1 style="font-size: 18px;color: white;">当前领域下共有文章 {{selectedQueryNum}} 篇</h1>

                            <h1 style="font-size: 18px;color: white;">现有文献综述文章数：{{listGCSummaryArticles.length}}</h1>
                            <ul class="list-files" style="overflow: auto;height: 200px">

                                <div v-for="i in listGCSummaryArticles" style="background-color: white;padding: 10px;margin-bottom: 10px">
                                    <li class="list-files-item" @click="setGCSummaryArticle(i.value)">
                                        {{ i.key }}
                                    </li>
                                </div>

                            </ul>
                            <!-- <h1 style="font-size: 18px;color: white;">功能正在完善中...</h1> -->
                        </div>


                    </div>

                </div>

            </el-aside>

            <el-container>
                <el-main style="padding: 0">
                    <!--arxiv 文章查询-->
                    <div v-if="arxivSearch == 1" class="chat-container">
                        <div style="padding: 40px">
                            <el-input v-model="searchKeyword" style="width: 200px" placeholder="请输入要搜索的内容" />

                                <el-table ref="tableRef" row-key="date" :data="filteredData" style="width: 100%">
                                    <el-table-column type="index" :index="indexMethod" />

                                    <!-- <el-table-column

                                        prop="date"
                                        label="Date"
                                        sortable
                                        width="140"
                                        column-key="date"

                                    /> -->

                                    <el-table-column prop="title" label="文章标题" />
                                    <el-table-column prop="" label="文章概述" width="160">
                                        <template #default="scope">
                                            <el-button type="success" @click="setGCArticle(scope.row.title);arxivSearchPage()">查看</el-button>
                                        </template>
                                    </el-table-column>
<!--                                    <el-table-column prop="translated" label="是否翻译" width="120"/>-->

                                    <!-- <el-table-column prop="translated" label="翻译" width="120">

                                        <template #default="scope">
                                            <el-button v-if="scope.row.translated == 0" type="warning" style="margin-left: 10px" @click="translateFile(scope.row.title)">翻译</el-button>
                                            <el-button v-if="scope.row.translated == 1" type="danger" style="margin-left: 10px" @click="updateGCBase(scope.row.value,scope.row.title)">查看翻译</el-button>
                                        </template>

                                    </el-table-column> -->

                                    <el-table-column prop="query" label="类别" width="240"
                                                     :filters="[
                                        { text: 'LLM Model', value: 'LLM Model' },
                                        { text: 'Brain computer interface', value: 'Brain computer interface' },
                                      ]"
                                                     :filter-method="filterQuery"
                                                     filter-placement="bottom-end"/>

                                    <!-- <el-table-column prop="key" label="关键词" width="140"/> -->


                                    <el-table-column
                                        prop="value"
                                        label="提交状态"
                                        width="100"
                                        :filters="[
                                        { text: '未提交', value: 0 },
                                        { text: '已提交', value: 1 },
                                      ]"
                                        :filter-method="filterTag"
                                        filter-placement="bottom-end"
                                    >
                                        <template #default="scope">
                                            <el-tag
                                                :type="scope.row.value === 0 ? '' : 'success'"
                                                disable-transitions
                                            >{{ scope.row.value === 0? '未提交' : '已提交' }}</el-tag
                                            >
                                        </template>
                                    </el-table-column>
                                    <el-table-column prop="key" label="标记" width="160">
                                        <template #default="scope">
                                            <el-button v-if="scope.row.value == 0" type="warning" style="margin-left: 10px" @click="updateGCBase(scope.row.value,scope.row.title)">标记</el-button>
                                            <el-button v-if="scope.row.value == 1" type="danger" style="margin-left: 10px" @click="updateGCBase(scope.row.value,scope.row.title)">取消标记</el-button>
                                        </template>
                                    </el-table-column>
                                </el-table>
                        </div>
                    </div>

                    <!--对话界面-->
                    <div v-if="arxivSearch == 0" class="chat-container" ref="container">
                        <div class="chat-messages">
                            <div v-for="message in messages" :key="message.id" class="chat-message">
                                <div v-if="message.isUser" style="padding: 30px">

                                    <div class="user-message">
                                        <img src="../assets/logo2.png" style="width:50px;height: 50px; margin-right: 16px">
                                        {{ message.content }}
                                    </div>

                                </div>
                                <div v-else style="background-color: #f0f4ff;padding: 30px">
                                  <div class="assistant-message" style="display: block">
                                      <div style="display: flex">
                                      <img src="../assets/logo2.png" style="width:50px;height: 50px; margin-right: 16px">
                                      <!-- <pre><h style="margin-right: 16px">AI助手</h></pre> -->
        <!--                              <pre>{{ message.content }}</pre>-->
                                      <div class="markdown-body" style="background-color: #f0f4ff" v-html="message.content"></div>
                                      </div>
                                      <p v-if="message.isTyping != 0"><span class="typing-cursor" style="margin-left: 80px;"></span></p>

                                      <div v-if="funcSelect=='知识库问答'">
                                          <ul class="list-files" style="overflow: auto;width: 100%;height: 500px;">
                                              <li v-for="i in message.source" :key="i" class="list-files-item" style="background-color: black">{{ i }}</li>
                                          </ul>
                                      </div>

                                      <ul v-if="funcSelect=='内容生成' && message.article" >

                                          <img id="imageElement" style="width: 100%" :src=message.imageSrc alt="Image" @click="toggleZoom(message)">
                                          <div class="img-zoom" v-if="zoomedImage" @click="toggleZoom(null)">
                                            <img :src="zoomedImage.imageSrc" />
                                          </div>
                                          <el-button v-if="message.article != '0'" class="button" style="background-color: green;" text><h1 style="font-size: 20px;color: white;" @click="downloadFile(message.article, 'PDF')">下载PDF</h1></el-button>
                                          <el-button v-if="message.article != '0'" class="button" style="background-color: green;" text><h1 style="font-size: 20px;color: white;" @click="downloadFile(message.article, 'MD')">下载Markdown</h1></el-button>


<!--                                          <el-button class="button" style="background-color: green;" text><h1 style="font-size: 20px;color: white;" @click="translateFileP(message.article)">论文翻译</h1></el-button>-->
                                      </ul>

                                  </div>

                                </div>
                            </div>
                        </div>

                        <div :style="logoStyle">
                            <img src="../assets/logo3.png" style="width:auto;height: 50px;margin-top: 40px">

                            <h1 style="font-size: 40px;color: black;">AI学术</h1>

                            <!-- <h1 style="font-size: 32px;color: black;">Powered By LangChain & ChatGPT & 星火认知大模型</h1> -->
                        </div>

                        <div class="chat-input" >

                            <el-input
                                v-model="inputMessage"
                                placeholder="请输入消息"
                                @keyup.enter="sendMessage"
                                @input="handleInput"
                                size="large"
                            ><template #prepend>
                                插件
                                <img v-if="useplugin==1" src="../assets/logo2.png" style="width:auto;height: 30px;" @click="setplugin">
                                <img v-if="useplugin==0" src="../assets/logo1.png" style="width:auto;height: 30px;" @click="setplugin">
                            </template>
                            <template #suffix>
                                <el-icon v-if="iconState==0" style="font-size: large; padding: 5px;" @click="sendMessage"><promotion /></el-icon>
                                <el-icon v-if="iconState==1" style="font-size: large; color:white; background-color: seagreen; padding: 5px; border-radius: 20%" @click="sendMessage"><promotion /></el-icon>
        
                            </template></el-input>
                        </div>
                    </div>


                </el-main>
            </el-container>
            </el-container>


        <div v-if="popup>0" class="popup font-set">
            <div class="popup-content">
                <h2 class="gradient-text" style="margin-bottom: 80px">提示</h2>
                <h2 v-if="popup==6" style="font-size: 20px;color: black;margin-bottom: 80px">{{ popMsg }}</h2>
                <div v-if="popup==7">
                    <h2 style="margin-bottom: 80px">确定要删除吗？</h2>
                    <el-button class="button" style="background-color: red;" text><h1 style="font-size: 20px;color: white;" @click="deleteBase">确定</h1></el-button>
                </div>
                <div v-if="popup==8">
                    <h2 style="margin-bottom: 80px">请输入知识库名称</h2>
                    <el-input v-model="newpbname" placeholder="新建知识库" />
                    <el-button class="button" style="background-color: green;" text><h1 style="font-size: 20px;color: white;" @click="addBase">确定</h1></el-button>
                </div>
                <div v-if="popup==9">
                    <h2 style="margin-bottom: 80px">请输入提示词</h2>
                    <el-input v-model="newpromptname" placeholder="提示词名称，如：文本摘要" />
                    <el-input
                        v-model="newprompt"
                        :rows="5"
                        type="textarea"
                        placeholder="请输入提示词"
                    />
                    <el-button class="button" style="background-color: green;" text><h1 style="font-size: 20px;color: white;" @click="addPrompt">确定</h1></el-button>
                </div>

                <div v-if="popup==10">
                    <h2 v-if="popup==10" style="font-size: 20px;color: black;margin-bottom: 80px">{{ popMsg }}</h2>
                    <h2 v-if="popup==10" style="font-size: 20px;color: black;margin-bottom: 80px">是否继续？点击确定后不要关闭页面</h2>
                    <el-button class="button" style="background-color: green;" text><h1 style="font-size: 20px;color: white;" @click="checkAccount">确定</h1></el-button>
                </div>

                <div v-if="popup==11">
                    <h2 v-if="popup==11" style="font-size: 20px;color: black;margin-bottom: 80px">{{ popMsg }}</h2>
                    <el-button class="button" style="background-color: green;" text><h1 style="font-size: 20px;color: white;" @click="reverseplugin">确定</h1></el-button>
                </div>

                <el-button class="button" style="background-color: black;" text><h1 style="font-size: 20px;color: white;" @click="closepop">关闭</h1></el-button>
            </div>
        </div>


    </div>

</template>

<script>
import showdown from "showdown";
import {Promotion} from "@element-plus/icons-vue";
import request from "../utils/request";
import axios from 'axios'
import {globalVariables} from "../utils/globalVariables";
import startGeneration from "../utils/openaiStream"
import {ListBase,AddBase,DeleteBase,ListPrompt,AddPrompt,DeletePrompt} from "../utils/promptBase"

// import { Configuration, OpenAIApi } from "openai";
// import dotenv from "dotenv";
// dotenv.config({ override: true });

// const openai = new OpenAIApi(new Configuration({ apiKey: process.env.OPENAI_KEY }));

import { ref } from 'vue'

import * as base64 from "base-64"
import CryptoJS from "crypto-js"

const client = axios.create({
    baseURL: 'http://10.112.224.75:8000'
});

// 此处是文献综述系统后端地址，即 chat_server/main.py 中对应服务。应为服务器地址加对应端口号 'http://XX.XX.XX.XX:8008'
const content_generate_url = ''

// 此处是思维图优化后端地址，目前该部分后端代码暂未公开
const got_url = ''

const data_root_path = '/root/bbft/ChatPaper/export/'

client.interceptors.request.use(config => {
    config.headers['Content-Type'] = 'application/json;charset=utf-8';
    config.headers['Access-Control-Allow-Origin'] = '*';

    // config.headers['token'] = user.token;  // 设置请求头
    return config
}, error => {
    return Promise.reject(error)
});

export default {
    name: "chatbrain.vue",
    computed: {
        Promotion() {
            return Promotion
        },
        filteredData() {
            return this.listGCArticles.filter((data) =>
                data.title.toLowerCase().includes(this.searchKeyword.toLowerCase())
            );
        },
    },
    components: {

    },
    data() {
        return {
            inputMessage: "",
            messages: [],
            iconState: 0,
            collapseBtnClass: 'el-icon-s-fold',
            isCollapse: false,
            logoStyle: "height: 400px; text-align: center",
            history: [["当我问到你是谁，请回答我是脑基未来团队 BrainBase Future 的产品 ChatBrain","好的我会回答我是脑基未来 BrainBase Future 的产品 ChatBrain"]],
            popup: 0,
            popMsg: '',
            sideWidth: 400,
            sideView: 1,
            modelSelect: "星火",
            funcSelect: "内容生成",
            kbs: [],
            selectedValue: '',
            listFiles: [],
            isUploading: 0,
            pbs: [],
            selectedPromptBase: '',
            newpbname:'',
            listPrompts: [],
            prompt:'',
            newpromptname:'',
            newprompt:'',

            gcfuncs: ["arxiv文章总结", "领域文章每年数量", "词云图生成", "关键词频率直方图", "关键词首次出现时间及随时间累积频率", "关键词综述生成", "领域综述生成"],
            literatureReviewFunc: ["领域文章每年数量", "词云图生成", "关键词频率直方图", "关键词首次出现时间及随时间累积频率", "关键词综述生成"],
            queryHistory: [],
            queryHistoryArticleNum: {},
            fieldKey: [],
            selectmethods: ['random', 'linear'],
            selectedselectmethod: 'random',
            selectedKey: '',
            selectedQuery: '',
            selectedQueryNum: 0,
            needmoney: 0,
            selectedGCFunc: '',
            listGCArticles: '',
            listGCSummaryArticles: '',
            arxivgc: {
                query:'Brain computer interface',
                keyword:'',
                pagenum:'5',

                maxresults:'10000',
                days:'36500'
            },
            GCStateBtn: "内容生成",
            GCBtnDisabled: false,
            articleNum: 0,
            arxivSearch: 0,
            arxivSearchBtn: "数据库详情",
            searchKeyword: '',
            useplugin: 1,
            //星火模型

            APPID: import.meta.env.VITE_APP_SPARK_API_APPID, // 控制台获取填写
            APISecret: import.meta.env.VITE_APP_SPARK_API_SECRET,
            APIKey: import.meta.env.VITE_APP_SPARK_API_KEY,
            sparkResult: '',
            zoomedImage: null


        }

    },
    created() {
        if (globalVariables.login == 0) {
            this.popup = 6
            this.popMsg = "请登陆后使用此服务"
        }
        this.listQueryNum()
    },
    mounted() {

    },
    watch: {
        selectedValue(value) {
            // 处理选择器值变化的逻辑
            console.log('选择的值：', value)
            this.list_files(value)
        },
        selectedPromptBase(value) {
            console.log('prompt base 选择：',value)
            this.listPrompt()
        },
        selectedGCFunc(value) {
          console.log('选择的功能：', value)
          if(value == "arxiv文章总结"){
            this.listGCArticleBase()
          }else if(value == "领域综述生成"){
            this.listGCSummaryArticlesBase()
            this.listQueryNum()
          }else{
            this.listQueryNum()
          }
          console.log(globalVariables.userBasic.Email)
        },
        selectedQuery(value) {
            this.selectedQueryNum = this.queryHistoryArticleNum[value]
            if(this.selectedGCFunc=="关键词综述生成"){
                this.freshKey()
            }

        }
    },
    methods: {
        closepop() {
            this.popup = 0
            if (globalVariables.login == 0) {
                this.$emit('update-data', 3);
            }
        },
        pop7(){
            this.popup = 7
        },
        pop8(){
            this.popup = 8
        },
        pop9(){
            if (this.selectedPromptBase == ""){
                this.popup = 6
                this.popMsg = "请选择提示词仓库"
            } else {
                this.popup = 9
            }
        },

        toggleZoom(image) {
            this.zoomedImage = this.zoomedImage === image ? null : image;
        },

        changeModel() {
            console.log(this.modelSelect)
        },
        changeFunc() {
            console.log(this.funcSelect)
            if (this.funcSelect == "知识库问答") {
                this.listKnowledgeBase()
            }

            if (this.funcSelect == "提示词") {
                this.listBase()
            }

            if (this.funcSelect == "内容生成") {
                this.listGCArticleBase()
            }
        },
        collapse() { // 点击收缩按钮触发
            this.isCollapse = !this.isCollapse
            if (this.isCollapse) {
                this.sideWidth = 64
                this.collapseBtnClass = 'el-icon-s-unfold'
                this.logoTextShow = false
                this.sideView = 0
            } else {
                this.sideWidth = 400
                this.collapseBtnClass = 'el-icon-s-fold'
                this.logoTextShow = true
                this.sideView = 1
            }
        },
        scrollToBottom() {
            const container = this.$refs.container;
            container.scrollTop = container.scrollHeight;
        },
        handleInput() {
            if (this.inputMessage != "") {
                this.iconState = 1
            } else {
                this.iconState = 0
            }
        },

        setplugin() {
            this.popup = 11
            if(this.useplugin == 0){
                this.popMsg = "当前本地数据库插件未开启，是否开启？"
            }else{
                this.popMsg = "本地数据库插件已开启，点击确认关闭"
            }
        },

        reverseplugin() {
            if(this.useplugin == 0){
                this.useplugin = 1
            }else{
                this.useplugin = 0
            }
            this.popup=0
        },

        chatgpt() {
            const params = {
                prompt: this.inputMessage,
                model: "text-davinci-003",
                max_tokens: 1000,
                temperature: 0,
            };


            client.post("https://api.openai.com/v1/completions", params, {
                headers: {

                    Authorization: "Bearer " + import.meta.env.VITE_APP_OPENAI_API_KEY,

                },
            }).then(res => {
                if (res) {
                    console.log(res)


                    const assistantReply = {
                        id: Date.now(),
                        content: res.data.choices[0].text,
                        isUser: false,
                        isTyping: 0
                    };
                    this.messages.push(assistantReply);

                    // axios.post('https://api.github.com/markdown', { text:res.data.choices[0].text },
                    //     {
                    //         headers: {
                    //             'Content-Type': 'text/plain'
                    //         }
                    //     })
                    //     .then(response => {
                    //         const assistantReply = {
                    //             id: Date.now(),
                    //             content: response.data,
                    //             isUser: false
                    //         };
                    //         this.messages.push(assistantReply);
                    //         // console.log(response.data);
                    //     })
                    //     .catch(error => {
                    //         console.error(error);
                    //     });

                    this.scrollToBottom();
                    this.logoStyle = "height: 400px; text-align: center; opacity: 0.2"
                    this.inputMessage = ""; // 清空输入框

                } else {
                    console.log("接口调用失败")
                }
            })
        },

        chatglm2() {
            let data = new FormData()
            if (this.funcSelect == "提示词") {
                data.append("prompt", this.prompt + this.inputMessage)
            } else {
                data.append("prompt", this.inputMessage)
            }

            if (this.history == "") {

            } else {
                const jsonData = JSON.stringify(this.history);
                data.append("history", jsonData)
                // console.log("history")
                // console.log(jsonData)

            }


            client.post("http://10.112.224.75:8000", data).then(res => {
                if (res) {
                    console.log(res)
                    this.history = res.data.history
                    // const assistantReply = {
                    //     id: Date.now(),
                    //     content: res.data.response,
                    //     isUser: false
                    // };
                    // this.messages.push(assistantReply);

                    axios.post('https://api.github.com/markdown', {text: res.data.response},
                        {
                            headers: {
                                'Content-Type': 'text/plain'
                            }
                        })
                        .then(response => {
                            const assistantReply = {
                                id: Date.now(),
                                content: response.data,
                                isUser: false,
                                isTyping: 0
                            };
                            this.messages.push(assistantReply);
                            // console.log(response.data);
                        })
                        .catch(error => {
                            console.error(error);
                        });

                    this.scrollToBottom();
                    this.logoStyle = "height: 400px; text-align: center; opacity: 0.2"
                    this.inputMessage = ""; // 清空输入框

                } else {
                    console.log("接口调用失败")
                }
            })
        },

        chatglm2stream() {
            let data = new FormData()
            data.append("prompt", this.inputMessage)
            if (this.history == "") {

            } else {
                const jsonData = JSON.stringify(this.history);
                data.append("history", jsonData)

            }


            client.post("http://10.112.224.75:8000/v1/chat/completions", data).then(res => {
                if (res) {
                    console.log(res)
                    this.history = res.data.history

                    axios.post('https://api.github.com/markdown', {text: res.data.response},
                        {
                            headers: {
                                'Content-Type': 'text/plain'
                            }
                        })
                        .then(response => {
                            const assistantReply = {
                                id: Date.now(),
                                content: response.data,
                                isUser: false,
                                isTyping: 0
                            };
                            this.messages.push(assistantReply);
                            // console.log(response.data);
                        })
                        .catch(error => {
                            console.error(error);
                        });

                    this.scrollToBottom();
                    this.logoStyle = "height: 400px; text-align: center; opacity: 0.2"
                    this.inputMessage = ""; // 清空输入框

                } else {
                    console.log("接口调用失败")
                }
            })
        },

        internlm() {
            let data = new FormData()
            data.append("prompt", this.inputMessage)
            if (this.history == "") {

            } else {
                const jsonData = JSON.stringify(this.history);
                data.append("history", jsonData)
            }

            client.post("http://10.112.224.75:8001", data).then(res => {
                if (res) {
                    console.log(res)
                    this.history = res.data.history

                    axios.post('https://api.github.com/markdown', {text: res.data.response},
                        {
                            headers: {
                                'Content-Type': 'text/plain'
                            }
                        })
                        .then(response => {
                            const assistantReply = {
                                id: Date.now(),
                                content: response.data,
                                isUser: false,
                                isTyping: 0
                            };
                            this.messages.push(assistantReply);
                        })
                        .catch(error => {
                            console.error(error);
                        });

                    this.scrollToBottom();
                    this.logoStyle = "height: 400px; text-align: center; opacity: 0.2"
                    this.inputMessage = ""; // 清空输入框

                } else {
                    console.log("接口调用失败")
                }
            })
        },

        async spark_client(pre_prompt){

            const socket = new WebSocket("ws://119.3.238.159:8008/ws");
            const assistantReply = {
                    id: Date.now(),
                    content: '',
                    isUser: false,
                    isTyping: 1
                };
            this.messages.push(assistantReply);
            //console.log(this.messages)
            var that = this
            console.log(that.messages)

            // 当连接建立时
            socket.onopen = function(event) {
                console.log("WebSocket connection established.");
                // 发送消息到服务器
                console.log(that.messages)
                const message = that.messages[that.messages.length-2].content + pre_prompt;
                console.log(message)
                var send_messages = [...that.messages]
                send_messages[that.messages.length-2].content = message
                console.log("-------------------------------------")
                console.log(send_messages)
                socket.send(JSON.stringify(send_messages));
            };

            // 当从服务器接收到消息时
            socket.onmessage = function(event) {
                const message = event.data;
                console.log(message)
                that.messages[that.messages.length - 1].content = that.messages[that.messages.length - 1].content + message
            };

            // 当连接关闭时
            socket.onclose = function(event) {
                console.log("WebSocket connection closed.");
                that.messages[that.messages.length - 1].isTyping = 0
                that.inputMessage = ""; // 清空输入框
            };

        },

        spark_agent(){

            const message = {
                id: Date.now(),
                content: '',
                isUser: false,
                isTyping: 1
            };
            this.messages.push(message);

            let data = {
                "useremail": globalVariables.userBasic.Email,
                "userinput": this.messages[this.messages.length-2].content
            }

            axios.post(content_generate_url + '/v1/sparkagent', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("spark agent")
                    console.log(response)
                    this.messages.pop()
                    this.inputMessage = ""; // 清空输入框
                    if(response.data.success==2){
                        this.selectedGCFunc = response.data.category
                        this.selectedQuery = response.data.field

                        this.generateContent(0)

                    }else if (response.data.success==1 & response.data.field == ''){
                        //this.spark_client("（未在本地数据库检索到答案）")
                        this.spark_client("")
                    }else{
                        this.spark_client('')
                    }
                

                })
                .catch(error => {
                    console.error(error);
                });

        },

        async spark_literature_review(){

            const socket = new WebSocket("ws://119.3.238.159:8008/ws/literature?useremail=" + globalVariables.userBasic.Email +"&query=" + this.selectedQuery + "&keyword=None&selectmethod=" + this.selectedselectmethod);
            const assistantReply = {
                    id: Date.now(),
                    content: '',
                    isUser: false,
                    isTyping: 1
                };
            this.messages.push(assistantReply);
            //console.log(this.messages)
            var that = this
            console.log(that.messages)

            // 当连接建立时
            socket.onopen = function(event) {
                console.log("WebSocket connection established.");
                // 发送消息到服务器
                console.log(that.messages)
                const message = that.messages[that.messages.length-2].content;
                console.log(message)
                socket.send(JSON.stringify(that.messages));
                that.puretext = ""
            };

            // 当从服务器接收到消息时
            socket.onmessage = function(event) {
                var converter = new showdown.Converter();
                const message = event.data;
                console.log(message)
                that.puretext = that.puretext + message
                var html = converter.makeHtml(that.puretext);
                that.messages[that.messages.length - 1].content = html
                //that.messages[that.messages.length - 1].content = that.messages[that.messages.length - 1].content + message
            }

            // 当连接关闭时
            socket.onclose = function(event) {
                console.log("WebSocket connection closed.");
                that.messages[that.messages.length - 1].isTyping = 0
            };

         },


        async spark() {
            let myUrl = await this.getWebSocketUrl();
            this.sparkResult="";
            let realThis = this;
            this.socketTask = new WebSocket(myUrl);
            this.socketTask.onerror = (event) => {
                console.log("连接发生错误", event);
            };

            this.socketTask.onopen = (event) => {
                console.log(event, "ws成功连接...", myUrl);
                realThis.wsLiveFlag = true;

                // 第一帧..........................................
                console.log('open成功...');
                const formattedText = this.messages.map(item => {
                    return {
                        role: item.isUser == true ? 'user':'assistant',
                        content: item.content
                    };
                });
                console.log('ffffffffffffffffffffff')
                console.log(formattedText)
                let params = {
                    "header": {
                        "app_id": "cd72ab24",
                        "uid": "aef9f963-7"
                    },
                    "parameter": {
                        "chat": {
                            "domain": "general",
                            "temperature": 0.5,
                            "max_tokens": 1024
                        }
                    },
                    "payload": {
                        "message": {
                            "text": formattedText
                        }
                    }
                }
                console.log("发送第一帧...", params);
                realThis.socketTask.send(JSON.stringify(params));
                const assistantReply = {
                    id: Date.now(),
                    content: '',
                    isUser: false
                };
                this.messages.push(assistantReply);
            };

            this.socketTask.onmessage = (event) => {
                // 处理接收到的消息
                let temp = JSON.parse(event.data)
                this.messages[this.messages.length - 1].content = this.messages[this.messages.length - 1].content + temp.payload.choices.text[0].content
                if (temp.header.code !== 0) {
                    console.log(`${temp.header.code}:${temp.message}`);
                    this.socketTask.onclose = (event) => {
                        console.log("连接已关闭", event);
                    };
                }
                if (temp.header.code === 0) {
                    if (event.data && temp.header.status === 2) {
                        //realThis.sparkResult =realThis.sparkResult+ res.data;
                        //realThis.sparkResult =realThis.sparkResult+ temp.payload.choices.text[0].content
                        this.messages[this.messages.length - 1].content = this.messages[this.messages.length - 1].content + temp.payload.choices.text[0].content
                        //console.log("asdsadwasdsadsadsadas");
                        this.scrollToBottom();
                        this.logoStyle = "height: 400px; text-align: center; opacity: 0.2"
                        this.inputMessage = ""; // 清空输入框

                        setTimeout(() => {
                            this.socketTask.onclose = (event) => {
                                console.log("连接已关闭", event);
                            };
                        }, 10)
                    }
                }
            };
        },
        // 鉴权
        getWebSocketUrl() {
            return new Promise((resolve, reject) => {
                // 请求地址根据语种不同变化 https://spark-api.xf-yun.com/v1.1/chat
                var url = "wss://spark-api.xf-yun.com/v1.1/chat";
                var host = "spark-api.xf-yun.com";
                var apiKeyName = "api_key";
                var date = new Date().toGMTString();
                var algorithm = "hmac-sha256";
                var headers = "host date request-line";
                var signatureOrigin = `host: ${host}\ndate: ${date}\nGET /v1.1/chat HTTP/1.1`;
                var signatureSha = CryptoJS.HmacSHA256(signatureOrigin, this.APISecret);
                var signature = CryptoJS.enc.Base64.stringify(signatureSha);
                var authorizationOrigin =
                    `${apiKeyName}="${this.APIKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`;
                //var authorization = base64.encode(authorizationOrigin);
                var authorization = base64.encode(authorizationOrigin);
                url = `${url}?authorization=${authorization}&date=${encodeURI(date)}&host=${host}`;

                // console.log(url)
                resolve(url); // 主要是返回地址
            });
        },

        sendMessage() {
            this.iconState = 0
            const message = {
                id: Date.now(),
                content: this.inputMessage,
                isUser: true
            };
            this.messages.push(message);

            // 向ChatGPT发送消息，并接收回复
            // 这里可以调用你的ChatGPT交互逻辑，发送用户消息并接收助手回复
            // 示例中将回复添加到messages数组中，以便在界面上显示

            if (this.funcSelect == "知识库问答") {
                this.localDocChat()
            } else if(this.funcSelect == "提示词"){
                this.chatglm2()

            } else {
                if (this.modelSelect == "ChatGLM2") {
                    this.chatglm2()
                    //this.chatglm2stream()
                } else if (this.modelSelect == "InternLM") {
                    this.internlm()
                } else if (this.modelSelect == "ChatGPT") {
                    this.chatgpt()
                    console.log("select chatgpt")
                    //startGeneration()
                } else if (this.modelSelect == "星火") {
                    //this.spark()
                    if(this.useplugin==1){
                        this.spark_agent()
                    }else{
                        this.spark_client('')
                    }
                }
            }

        },

        //知识库问答相关函数
        listKnowledgeBase() {
            axios.get('http://10.112.224.75:7861/local_doc_qa/list_knowledge_base',
                {
                    headers: {
                        'Content-Type': 'text/plain'
                    }
                })
                .then(response => {
                    console.log(response.data.data)
                    this.kbs = response.data.data

                })
                .catch(error => {
                    console.error(error);
                });

        },

        list_files(value) {
            console.log(this.selectedValue)
            let da = {
                "knowledge_base_id": value,
                "question": ""
            }
            axios.post('http://10.112.224.75:7861/local_doc_qa/list_files', da,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("list files")
                    console.log(response.data.data)
                    this.listFiles = response.data.data


                })
                .catch(error => {
                    console.error(error);
                });
        },
        upload(param) {
            const formData = new FormData()
            formData.append('file', param.file) // 传入文件
            formData.append('knowledge_base_id', this.selectedValue)
            console.log(param)
            console.log(param.file)

            if (this.selectedValue == "") {
                this.popup = 6
                this.popMsg = "请选择知识库"
            } else {
                this.isUploading = 1
                axios.post('http://10.112.224.75:7861/local_doc_qa/upload_file', formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        },
                    })
                    .then(response => {
                        console.log(response)
                        this.list_files(this.selectedValue)
                        this.isUploading = 0
                    })
                    .catch(error => {
                        console.error(error)
                        this.isUploading = 0
                    });

            }

        },

        localDocChat() {
            let data = {
                "knowledge_base_id": this.selectedValue,
                "question": this.inputMessage,
                "history": []
            }
            axios.post('http://10.112.224.75:7861/local_doc_qa/local_doc_chat', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log(response.data)
                    console.log(response.data.source_documents)
                    this.history = response.data.history

                    const assistantReply = {
                        id: Date.now(),
                        content: response.data.response,
                        isUser: false,
                        source: response.data.source_documents
                    };
                    this.messages.push(assistantReply);


                    this.scrollToBottom();
                    this.logoStyle = "height: 400px; text-align: center; opacity: 0.2"
                    this.inputMessage = ""; // 清空输入框

                })
                .catch(error => {
                    console.error(error);
                });
        },

        // prompt base
        listBase() {
            axios.post("http://10.112.224.75:1016/api/prompt/listbase", null).then(res => {
                if (res) {
                    console.log(res.data.data)
                    this.pbs = res.data.data.promptBase

                } else {
                    console.log("接口调用失败")
                }
            })
        },

        addBase() {
            let data = new FormData()
            data.append("name", this.newpbname)

            console.log(this.newpbname)

            axios.post("http://10.112.224.75:1016/api/prompt/addbase", data).then(res => {
                if (res) {
                    console.log(res)
                    this.listBase()
                    this.popup=0
                    this.selectedPromptBase = ''

                } else {
                    console.log("接口调用失败")
                }
            })

        },

        deleteBase() {
            let data = new FormData()
            data.append("name", this.selectedPromptBase)

            axios.post("http://10.112.224.75:1016/api/prompt/deletebase", data).then(res => {
                if (res) {
                    console.log(res)
                    this.popup=0
                    this.listBase()
                    this.selectedPromptBase = ''

                } else {
                    console.log("接口调用失败")
                }
            })

        },

        listPrompt() {
            let data = new FormData()
            data.append("name", this.selectedPromptBase)

            axios.post("http://10.112.224.75:1016/api/prompt/listprompt", data).then(res => {
                if (res) {
                    console.log(res.data.data.promptDetail)
                    this.listPrompts = res.data.data.promptDetail


                } else {
                    console.log("接口调用失败")
                }
            })
        },

        addPrompt() {

            let data = new FormData()
            data.append("basename", this.selectedPromptBase)
            data.append("name", this.newpromptname)
            data.append("prompt", this.newprompt)

            axios.post("http://10.112.224.75:1016/api/prompt/addprompt", data).then(res => {
                if (res) {
                    console.log(res)
                    this.listPrompt()
                    this.popup = 0
                    this.newpromptname = ""
                    this.newprompt = ""

                } else {
                    console.log("接口调用失败")
                }
            })

        },

        deletePrompt(name) {

            let data = new FormData()
            data.append("basename", this.selectedPromptBase)
            data.append("name", name)
            console.log(name)

            axios.post("http://10.112.224.75:1016/api/prompt/deleteprompt", data).then(res => {
                if (res) {
                    console.log(res)
                    this.listPrompt()
                    this.prompt = ""

                } else {
                    console.log("接口调用失败")
                }
            })
        },

        setPrompt(prompt){
            console.log(prompt)
            this.prompt = prompt
        },


        queryMoney(){
            let data = {
                "useremail": globalVariables.userBasic.Email,
                "x": ""
            }

            axios.post(content_generate_url + '/v1/querymoney', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("queryMoney")
                    console.log(response)
                    globalVariables.userBasic.Money = response.data.res


                })
                .catch(error => {
                    console.error(error);
                });
        },

        checkAccount(){

            if(globalVariables.userBasic.Money >= this.needmoney) {
                let data = {
                "amount": this.needmoney.toString(),
                "useremail": globalVariables.userBasic.Email
            }

            axios.post(content_generate_url + '/v1/spendmoney', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("checkAccount")
                    console.log(response)
                    if (response.data.res == "success"){
                        this.generateContent(1)
                    } else{
                        this.popup = 6
                        this.popMsg = "支付失败，请重试"
                    }


                })
                .catch(error => {
                    console.error(error);
                });

            }else{
                this.popup = 6
                this.popMsg = "账户余额不足，请充值"
            }

        },

        // 内容生成相关函数
        generateContent(check) {
            this.queryMoney()

            if (this.selectedGCFunc==""){
                this.popup=6
                this.popMsg="请选择功能"
               // console.log(globalVariables.userBasic.Email)

            }
            else if(globalVariables.userBasic.Email != 'nxyqdl@163.com' && globalVariables.userBasic.Email != 'nxybupt@bupt.edu.cn') {

                this.popup=6
                this.popMsg="无权限操作"
            }
            else{
                if(this.modelSelect != "ChatGLM2" && this.modelSelect != "ChatGPT" && this.modelSelect != "星火"){
                    this.popup=6
                    this.popMsg="请选择模型"

                } 
                // else if (this.modelSelect == "星火"){
                //     this.popup=6
                //     this.popMsg="暂不支持，请选择其他模型"
                // } 
                else{

                    if(this.selectedGCFunc=="arxiv文章总结"){

                        let data = {
                            "query":this.arxivgc.query,
                            "keyword":this.arxivgc.keyword,
                            "pagenum":this.arxivgc.pagenum,
                            "maxresults":this.arxivgc.maxresults,
                            "days":this.arxivgc.days,

                            "model":this.modelSelect,
                            "useremail": globalVariables.userBasic.Email,
                            "check": check.toString()

                        }
                        this.GCBtnDisabled = true
                        this.GCStateBtn = "生成中"


                        if (check==1){
                            this.popup = 6
                            this.popMsg = "生成中，请勿关闭页面。因意外操作导致的资金损失将不予退还。"
                            //this.popMsg = "暂未开放"
                            //return
                        } else {
                            this.popup = 6
                            this.popMsg = "正在查询按配置参数可增添的文章数量，请勿关闭页面"
                        }



                        axios.post(content_generate_url+'/v1/chatglmarxiv', data,
                            {
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                            })
                            .then(response => {
                                console.log("GC finish")
                                console.log(response.data.num)

                                if (check == 1){
                                    this.popup = 6
                                    this.popMsg = "本次增加的文章数目为:" + response.data.num
                                } else {
                                    this.popup = 10
                                    this.popMsg = "本次增加的文章数目为:" + response.data.num +", 需支付 " + response.data.num * 2 + " 元"
                                    this.needmoney = response.data.num * 2
                                }



                                this.GCBtnDisabled = false
                                this.GCStateBtn = "内容生成"
                                this.listGCArticleBase()

                            })
                            .catch(error => {
                                console.error(error);
                            });

                    } else if (this.selectedGCFunc=="arxiv文章总结1") {
                        this.popup = 6
                        this.popMsg = "暂未开放"
                    }else if (this.selectedGCFunc=="词云图生成") {
                        if (this.selectedQuery==""){
                            this.popup = 6
                            this.popMsg = "请选择需要生成词云图的领域"
                        } else {

                            let data = {
                                "useremail": globalVariables.userBasic.Email,
                                "query": this.selectedQuery
                            }
                            this.GCBtnDisabled = true
                            this.GCStateBtn = "生成中"

                            //this.popup = 6
                            //this.popMsg = "生成中，请勿关闭页面"
                            const message = {
                                id: Date.now(),
                                content: '',
                                isUser: false,
                                isTyping: 1
                            };
                            this.messages.push(message);

                            axios.post(content_generate_url+'/v1/showwordcloud', data,
                                {
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                })
                                .then(response => {
                                    console.log("wordcloud finish")
                                    console.log(response.data)
                                    this.messages.pop()

                                    // 原始字符串
                                    var originalString = response.data.res;
                                    var res_zh = ""
                                    var res_en = ""

                                    // 要截取的目标句子
                                    var targetSentence = "The 20 most frequently occurring keywords in this field and their frequency are";

                                    // 使用正则表达式构建匹配模式
                                    var regexPattern = new RegExp(targetSentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

                                    // 使用正则表达式执行匹配
                                    var match = originalString.match(regexPattern);

                                    // 检查是否找到匹配的句子
                                    if (match) {
                                        // 获取匹配句子之前的内容
                                        res_zh = originalString.substring(0, match.index);
                                        res_en = targetSentence + originalString.substring(match.index + match[0].length);
                                    } else {
                                        res_zh = response.data.res
                                    }

                                    if (response.data.path_en != "" && response.data.path_zh != ""){
                                        this.getImageFromFile(response.data.path_en, "wordcloud", res_en)
                                        this.getImageFromFile(response.data.path_zh, "wordcloud", res_zh)
                                        this.popup = 0
                                    } else if (response.data.path_en != ""){
                                        this.getImageFromFile(response.data.path_en, "wordcloud", res_en)
                                        this.popup = 0
                                    } else if (response.data.path_zh != ""){
                                        this.getImageFromFile(response.data.path_zh, "wordcloud", res_zh)
                                        this.popup = 0
                                    } else {
                                        this.popup = 6
                                        this.popMsg = "生成失败"
                                    }

                                    this.GCBtnDisabled = false
                                    this.GCStateBtn = "内容生成"

                                })
                                .catch(error => {
                                    console.error(error);
                                });
                        }
                        
                    }else if (this.selectedGCFunc=="领域文章每年数量") {
                        if (this.selectedQuery==""){
                            this.popup = 6
                            this.popMsg = "请选择需要生成领域文章每年数量图的领域"
                        } else {

                            let data = {
                                "useremail": globalVariables.userBasic.Email,
                                "query": this.selectedQuery
                            }
                            this.GCBtnDisabled = true
                            this.GCStateBtn = "生成中"

                            //this.popup = 6
                            //this.popMsg = "生成中，请勿关闭页面"
                            const message = {
                                id: Date.now(),
                                content: '',
                                isUser: false,
                                isTyping: 1
                            };
                            this.messages.push(message);

                            axios.post(content_generate_url+'/v1/shownumofpublicationperyear', data,
                                {
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                })
                                .then(response => {
                                    console.log("shownumofpublicationperyear finish")
                                    console.log(response.data)
                                    this.messages.pop()

                                    if (response.data.path_en != ""){
                                        this.getImageFromFile(response.data.path, "pubPerYear", response.data.res)
                                        this.popup = 0
                                    } else {
                                        this.popup = 6
                                        this.popMsg = "生成失败"
                                    }

                                    this.GCBtnDisabled = false
                                    this.GCStateBtn = "内容生成"

                                })
                                .catch(error => {
                                    console.error(error);
                                });
                        }
                        
                    }else if (this.selectedGCFunc=="关键词频率直方图") {
                        if (this.selectedQuery==""){
                            this.popup = 6
                            this.popMsg = "请选择需要生成关键词频率直方图的领域"
                        } else {

                            let data = {
                                "useremail": globalVariables.userBasic.Email,
                                "query": this.selectedQuery
                            }
                            this.GCBtnDisabled = true
                            this.GCStateBtn = "生成中"

                            //this.popup = 6
                            //this.popMsg = "生成中，请勿关闭页面"
                            const message = {
                                id: Date.now(),
                                content: '',
                                isUser: false,
                                isTyping: 1
                            };
                            this.messages.push(message);

                            axios.post(content_generate_url+'/v1/showkeywordsfrequencybar', data,
                                {
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                })
                                .then(response => {
                                    console.log("showkeywordsfrequencybar finish")
                                    console.log(response.data)
                                    this.messages.pop()

                                    // 原始字符串
                                    var originalString = response.data.res;
                                    var res_zh = ""
                                    var res_en = ""

                                    // 要截取的目标句子
                                    var targetSentence = "The 20 most frequently occurring keywords in this field and their frequency are";

                                    // 使用正则表达式构建匹配模式
                                    var regexPattern = new RegExp(targetSentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

                                    // 使用正则表达式执行匹配
                                    var match = originalString.match(regexPattern);

                                    // 检查是否找到匹配的句子
                                    if (match) {
                                        // 获取匹配句子之前的内容
                                        res_zh = originalString.substring(0, match.index);
                                        res_en = targetSentence + originalString.substring(match.index + match[0].length);
                                    } else {
                                        res_zh = response.data.res
                                    }

                                    if (response.data.path_en != "" && response.data.path_zh != ""){
                                        this.getImageFromFile(response.data.path_en, "keywordFreq", res_en)
                                        this.getImageFromFile(response.data.path_zh, "keywordFreq", res_zh)
                                        this.popup = 0
                                    } else if (response.data.path_en != ""){
                                        this.getImageFromFile(response.data.path_en, "keywordFreq", res_en)
                                        this.popup = 0
                                    } else if (response.data.path_zh != ""){
                                        this.getImageFromFile(response.data.path_zh, "keywordFreq", res_zh)
                                        this.popup = 0
                                    } else {
                                        this.popup = 6
                                        this.popMsg = "生成失败"
                                    }

                                    this.GCBtnDisabled = false
                                    this.GCStateBtn = "内容生成"

                                })
                                .catch(error => {
                                    console.error(error);
                                });
                        }
                        
                    }else if (this.selectedGCFunc=="关键词首次出现时间及随时间累积频率") {
                        if (this.selectedQuery==""){
                            this.popup = 6
                            this.popMsg = "请选择需要生成关键词首次出现时间及随时间累积频率图的领域"
                        } else {

                            let data = {
                                "useremail": globalVariables.userBasic.Email,
                                "query": this.selectedQuery
                            }
                            this.GCBtnDisabled = true
                            this.GCStateBtn = "生成中"

                            //this.popup = 6
                            //this.popMsg = "生成中，请勿关闭页面"
                            const message = {
                                id: Date.now(),
                                content: '',
                                isUser: false,
                                isTyping: 1
                            };

                            axios.post(content_generate_url+'/v1/showkeywordstimeline', data,
                                {
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                })
                                .then(response => {
                                    console.log("showkeywordstimeline finish")
                                    console.log(response.data)
                                    this.messages.pop()

                                    // 原始字符串
                                    var originalString = response.data.res;
                                    var res_zh = ""
                                    var res_en = ""

                                    // 要截取的目标句子
                                    var targetSentence = "The 20 most frequently occurring keywords and their first appearance in this field are";

                                    // 使用正则表达式构建匹配模式
                                    var regexPattern = new RegExp(targetSentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

                                    // 使用正则表达式执行匹配
                                    var match = originalString.match(regexPattern);

                                    // 检查是否找到匹配的句子
                                    if (match) {
                                        // 获取匹配句子之前的内容
                                        res_zh = originalString.substring(0, match.index);
                                        res_en = targetSentence + originalString.substring(match.index + match[0].length);
                                    } else {
                                        res_zh = response.data.res
                                    }

                                    if (response.data.path_en != "" && response.data.path_zh != ""){
                                        this.getImageFromFile(response.data.path_en, "keywordTimeline", res_en)
                                        this.getImageFromFile(response.data.path_zh, "keywordTimeline", res_zh)
                                        this.popup = 0
                                    } else if (response.data.path_en != ""){
                                        this.getImageFromFile(response.data.path_en, "keywordTimeline", res_en)
                                        this.popup = 0
                                    } else if (response.data.path_zh != ""){
                                        this.getImageFromFile(response.data.path_zh, "keywordTimeline", res_zh)
                                        this.popup = 0
                                    } else {
                                        this.popup = 6
                                        this.popMsg = "生成失败"
                                    }

                                    this.GCBtnDisabled = false
                                    this.GCStateBtn = "内容生成"

                                })
                                .catch(error => {
                                    console.error(error);
                                });
                        }

                    }else if(this.selectedGCFunc=="关键词综述生成") {
                        if(this.selectedKey ==''){
                            this.popup = 6
                            this.popMsg = "请选择关键词"
                        }else{
                            let data = {
                            "useremail": globalVariables.userBasic.Email,
                            "query": this.selectedQuery,
                            "keyword": this.selectedKey,
                            "selectmethod": this.selectedselectmethod
                        }
                        this.GCBtnDisabled = true
                        this.GCStateBtn = "生成中"

                        this.popup = 6
                        this.popMsg = "生成中，请勿关闭页面"

                        axios.post(got_url+'/v1/summarykey', data,
                            {
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                            })
                            .then(response => {
                                console.log("showkeywordstimeline finish")
                                console.log(response)

                                this.popup = 0
                                var content = "<h1>根据 " + this.selectedQuery + " 领域下 " 
                                    + this.queryHistoryArticleNum[this.selectedQuery] + " 篇文章关键词 "
                                    + this.selectedKey + "</h1><h2>得到的关键词综述为</h2>"
                                    + "<p>" + response.data.res + "</p>"
                                const assistantReply = {
                                    id: Date.now(),
                                    content: content,
                                    isUser: false,
                                    article: '0',
                                    isTyping: 0
                                };

                                console.log(assistantReply)
                                this.messages.push(assistantReply);
                                this.scrollToBottom()
                                
                
                                this.GCBtnDisabled = false
                                this.GCStateBtn = "内容生成"

                            })
                            .catch(error => {
                                console.error(error);
                            });
                        }
                        

                    }else if(this.selectedGCFunc=="领域综述生成"){
                        if(this.selectedQuery == ''){
                            this.popup = 6
                            this.popMsg = "请选择总结领域"

                        }else{
                            // const assistantReply = {
                            //     id: Date.now(),
                            //     content: '请生成' + this.selectedQuery + '领域下的综述文章',
                            //     isUser: true,
                            //     isTyping: 0
                            // };
                            // this.messages.push(assistantReply);
                            this.spark_literature_review()
                        }
                        
                    }
                }
            }
        },

        freshKey(){
            if(this.selectedQuery==''){
                this.popup = 6
                this.popMsg = "请选择领域"
            }else{
                this.popup = 6
                this.popMsg = "刷新关键词中，请稍后"
                let data = {
                    "useremail": globalVariables.userBasic.Email,
                    "query": this.selectedQuery
                }
                axios.post(content_generate_url + '/v1/showkeywords', data,
                    {
                        headers: {
                            'Content-Type': 'application/json'
                        },
                    })
                    .then(response => {
                        console.log("freshKey")
                        console.log(response)
                        this.fieldKey = response.data.res_en
                        this.popup = 0

                    })
                    .catch(error => {
                        console.error(error);
                    });
            }

        },


        listQueryNum(){
            let data = {
                "useremail": globalVariables.userBasic.Email,
                "x": ""
            }

            axios.post(content_generate_url + '/v1/listquerycategory', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("list Category Num")
                    console.log(response)
                    const queryHistory = response.data.res.map(item => item[0]);

                    const queryHistoryArticleNum = {};

                    response.data.res.forEach(item => {
                        queryHistoryArticleNum[item[0]] = item[1];
                    });

                    this.queryHistory = queryHistory
                    this.queryHistoryArticleNum = queryHistoryArticleNum


                })
                .catch(error => {
                    console.error(error);
                });
        },

        countArticle(){
            let data = {
                "useremail": globalVariables.userBasic.Email,
                "x": ""
            }

            axios.post(content_generate_url + '/v1/countarticles', data,

                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("count articles")
                    console.log(response)
                    this.articleNum = response.data.num[0]


                })
                .catch(error => {
                    console.error(error);
                });
        },

        listGCSummaryArticlesBase() {
            let data = {
                "useremail": globalVariables.userBasic.Email,
                "x": ""
            }

            axios.post(content_generate_url + '/v1/searchsummaryresult', data,

                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("list articles summary")
                    console.log(response.data.res)

                    let result = response.data.res

                    this.listGCSummaryArticles = result


                })
                .catch(error => {
                    console.error(error);
                });
        },

        listGCArticleBase() {
            this.countArticle()

            let data = {
                "useremail": globalVariables.userBasic.Email,
                "query": ""
            }

            axios.post(content_generate_url + '/v1/listarticles', data,

                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("list articles")
                    console.log(response.data.gcarticles)

                    let result = response.data.gcarticles.map((item) => {
                        return {
                            title: item[0],
                            path: item[1],
                            value: item[2],
                            query: item[3],
                            key: item[4],
                            translated: item[5]
                        };
                    });

                    this.listGCArticles = result


                })
                .catch(error => {
                    console.error(error);
                });
        },

        setGCArticle(article) {
            let data = {
                "filename": data_root_path + article + "/md.md",
                "x": ""
            }
            axios.post(content_generate_url + '/v1/readmd', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("read markdown")
                    console.log(response)
                    console.log(response.data.content)

                    this.getArticleImage(article, response.data.content)



                })
                .catch(error => {
                    console.error(error);
                });
        },
        setGCSummaryArticle(article) {
            let data = {
                "filename": article,
                "x": ""
            }
            axios.post(content_generate_url + '/v1/readmd', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("read markdown")
                    console.log(response)
                    console.log(response.data.content)

                    this.getArticleImage(article, response.data.content)



                })
                .catch(error => {
                    console.error(error);
                });
        },

        getArticleImage(article, content) {
            let data = {
                "filename": data_root_path + article + "/",
                "x": ""
            }

            axios.post(content_generate_url + '/v1/getimage', data,
                {
                    responseType: 'blob',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log(response)
                    const imageURL = URL.createObjectURL(response.data)

                    const assistantReply = {
                        id: Date.now(),
                        content: content,
                        isUser: false,
                        article: article,
                        imageSrc: imageURL,
                        isTyping: 0
                    };

                    console.log(assistantReply)
                    this.messages.push(assistantReply);
                    this.scrollToBottom()

                })
                .catch(error => {
                    console.error(error);
                });

        },


        getImageFromFile(filename, content_type, res) {

            let data = {
                "filename": filename,
                "x": ""
            }

            var content = ''

            if (content_type == "wordcloud"){
                content = "<h1>根据 " + this.selectedQuery + " 领域下 " 
                            + this.queryHistoryArticleNum[this.selectedQuery] + " 篇文章关键词</h1><h2>得到的词云图为</h2>"
                            + "<p>" + res.replace(/\n/g, "<br>") + "</p>"
            } else if (content_type == "pubPerYear"){
                content = "<h1>根据 " + this.selectedQuery + " 领域下 " 
                            + this.queryHistoryArticleNum[this.selectedQuery] + " 篇文章</h1><h2>得到的领域下文章数量随时间变化的柱状图为</h2>"
                            + "<p>" + res.replace(/\n/g, "<br>") + "</p>"
            } else if (content_type == "keywordFreq"){
                content = "<h1>根据 " + this.selectedQuery + " 领域下 " 
                            + this.queryHistoryArticleNum[this.selectedQuery] + " 篇文章</h1><h2>得到的领域下文章关键词出现频率由高到低为</h2>"
                            + "<p>" + res.replace(/\n/g, "<br>") + "</p>"
            } else if (content_type == "keywordTimeline"){
                content = "<h1>根据 " + this.selectedQuery + " 领域下 " 
                            + this.queryHistoryArticleNum[this.selectedQuery] + " 篇文章</h1><h2>得到的关键词首次出现时间及随时间累积频率为</h2>"
                            + "<p>其中，箭头所指为该关键词首次出现所对应的时间</p>"
                            + "<p>" + res.replace(/\n/g, "<br>") + "</p>"
            }

            axios.post(content_generate_url + '/v1/getimagefromfile', data,
                {
                    responseType: 'blob',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log(response)
                    const imageURL = URL.createObjectURL(response.data)

                    const assistantReply = {
                        id: Date.now(),
                        content: content,
                        isUser: false,
                        article: '0',
                        imageSrc: imageURL,
                        isTyping: 0
                    };

                    console.log(assistantReply)
                    this.messages.push(assistantReply);
                    this.scrollToBottom()

                })
                .catch(error => {
                    console.error(error);
                });

        },


        updateGCBase(value, title) {
            let data = {
                "value": value.toString(),
                "title": title
            }
            console.log(value.toString())
            console.log(title)
            axios.post(content_generate_url + '/v1/updatearticle', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    this.listGCArticleBase()

                })
                .catch(error => {
                    console.error(error);
                });
        },

        downloadFile(article, filetype) {
            let filename = ""
            if (filetype == "PDF") {
                filename = "article.pdf"
            } else {
                filename = "md.md"
            }
            let data = {
                "filename": data_root_path + article + "/" + filename,
                "x": ""
            }
            axios.post(content_generate_url + '/v1/downloadfile', data,
                {
                    responseType: 'blob',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("download file")
                    console.log(response)
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = article + "_" + filename; // 替换为你希望的文件名
                    a.click();
                    window.URL.revokeObjectURL(url);


                })
                .catch(error => {
                    console.error(error);
                });
        },

        translateFile(article) {
            let data = {
                "filename": data_root_path + article + "/article.pdf",
                "x": ""
            }
            this.popup = 6
            this.popMsg = "翻译中"

            axios.post(content_generate_url + '/v1/sparktranslate', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log("download file")
                    console.log(response)
                    this.closepop()

                })
                .catch(error => {
                    console.error(error);
                });
        },

        translateFileP(article){
            //spark_translate.md
            console.log(article)
            let data = {
                "filename": data_root_path + article + "/article.pdf",
                "x": ""
            }
            axios.post(content_generate_url + '/v1/searchsparktranslate', data,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    console.log(response)
                    var translated = response.data.result[0][5]
                    console.log(translated)


                    if (translated == 1){
                        let data = {
                            "filename": data_root_path + article + "/spark_translate.md",
                            "x": ""
                        }

                        axios.post(content_generate_url + '/v1/readmd', data,
                            {
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                            })
                            .then(response => {
                                console.log("read markdown")
                                console.log(response)
                                console.log(response.data.content)
                                this.getArticleImage(article, response.data.content)


                            })
                            .catch(error => {
                                console.error(error);
                            });
                    } else {
                        this.translateFile(article)
                    }


                })
                .catch(error => {
                    console.error(error);
                });


        },

        // 文章搜索详情
        arxivSearchPage(){
            if (this.arxivSearch == 0) {
                this.arxivSearch = 1
                this.arxivSearchBtn = "返回对话"
            } else {
                this.arxivSearch = 0
                this.arxivSearchBtn = "数据库详情"
            }
        },

        filterTag(value, row) {
            return row.value === value;
        },

        filterQuery(value, row) {
            return row.query === value;
        },

        indexMethod(index) {
            return index;
        },


    }
}
</script>

<style scoped>
.font-set {
    font-family: Arial, sans-serif;
    text-align: left;
    padding: 0;
    /*text-transform: uppercase;*/
}


.chat-container {

    border: 2px black;
    height: 86vh;
    overflow-y: auto;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
    width: 15vw;
}

.chat-messages {

    display: flex;
    flex-direction: column;

    /*gap: 10px;*/
}

.chat-message {

}

.chat-input {
    position: absolute;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    margin-left: 24vw;
    height: 50px;
    width: 40vw;
    bottom: 16vh;
    display: flex;
}

.user-message {

    display: flex;
    width: 50%;
    margin-left: 20%;
}

.assistant-message {

    display: flex;
    width: 50%;
    margin-left: 20%;
}

/* 弹窗 */
.popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 9999;
}

.popup-content {
    background-color: #fff;
    max-width: 400px;
    margin: 100px auto;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
}

/*知识库问答*/
.list-files {
    height: 200px;
    list-style: none;
    width: 80%;
}

.list-files .list-files-item {
    display: flex;
    align-items: center;
    justify-content: center;
    height: auto;
    padding: 10px;
    background: #81f54b;
    margin: 10px;
    color: white;
}
.list-files .list-files-item + .list-item {
    margin-top: 10px;
}

.clickable-img {
  cursor: pointer;
  max-width: 100%;
  height: auto;
}

.img-zoom {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.img-zoom img {
  max-width: 80%;
  max-height: 80%;
}

/* 打字 */
/* 创建竖线光标的样式 */
.typing-cursor {
    display: inline-block;
    width: 1px; /* 光标的宽度 */
    height: 1em; /* 光标的高度 */
    background-color: black; /* 光标的颜色 */
    animation: blink 1s infinite; /* 闪烁动画 */
}

/* 定义闪烁动画 */
@keyframes blink {
    0%, 100% {
        opacity: 0; /* 闪烁时光标不可见 */
    }
    50% {
        opacity: 1; /* 闪烁时光标可见 */
    }
}

</style>