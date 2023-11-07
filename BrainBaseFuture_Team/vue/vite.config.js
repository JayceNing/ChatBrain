import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import obfuscatorPlugin from "vite-plugin-javascript-obfuscator";




// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),

    // obfuscatorPlugin({
    //   options: {
    //     compact: true,
    //     controlFlowFlattening: true,
    //     controlFlowFlatteningThreshold: 0.75,
    //     deadCodeInjection: true,
    //     deadCodeInjectionThreshold: 0.4,
    //     debugProtection: false,
    //     debugProtectionInterval: 0,
    //     disableConsoleOutput: true,
    //     identifierNamesGenerator: 'hexadecimal',
    //     log: false,
    //     numbersToExpressions: true,
    //     renameGlobals: false,
    //     selfDefending: true,
    //     simplify: true,
    //     splitStrings: true,
    //     splitStringsChunkLength: 10,
    //     stringArray: true,
    //     stringArrayCallsTransform: true,
    //     stringArrayCallsTransformThreshold: 0.75,
    //     stringArrayEncoding: ['base64'],
    //     stringArrayIndexShift: true,
    //     stringArrayRotate: true,
    //     stringArrayShuffle: true,
    //     stringArrayWrappersCount: 2,
    //     stringArrayWrappersChainedCalls: true,
    //     stringArrayWrappersParametersMaxCount: 4,
    //     stringArrayWrappersType: 'function',
    //     stringArrayThreshold: 0.75,
    //     transformObjectKeys: true,
    //     unicodeEscapeSequence: false
    // },
    // }),

  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }

  },
  // build: {
  //   sourcemap: false, // 不生成 source map 
  //   minify: 'terser',
  //   terserOptions: { 
  //     compress: { // 打包时清除 console 和 debug 相关代码
  //       drop_console: true,
  //       drop_debugger: true,
  //     },
  //   },
  // },

})
