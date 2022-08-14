const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  publicPath:'./',
  outputDir:'dist',
  assetsDir:'static',
  devServer: {
      proxy: {
        '/api': {	
          target: 'http://124.70.221.116:8010/',//接口域名
          changeOrigin: true,             //是否跨域
          ws: false,
        },
        '/static': {	
          target: 'http://124.70.221.116:8010/',//接口域名
          changeOrigin: true,             //是否跨域
          ws: false,
        },
      }
  }
};