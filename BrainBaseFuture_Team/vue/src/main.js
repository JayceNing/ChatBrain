import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import 'animate.css';
import Typed from 'typed.js';
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { faZhihu } from '@fortawesome/free-brands-svg-icons'
import { faTiktok } from '@fortawesome/free-brands-svg-icons'
import { faBilibili } from '@fortawesome/free-brands-svg-icons'
import { faResearchgate } from '@fortawesome/free-brands-svg-icons'
import { faKaggle } from '@fortawesome/free-brands-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'
import 'github-markdown-css'

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faGithub)
library.add(faZhihu)
library.add(faTiktok)
library.add(faBilibili)
library.add(faResearchgate)
library.add(faKaggle)
library.add(fas)


const app = createApp(App)
app.config.globalProperties.$typed = Typed;

app.use(ElementPlus)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')

