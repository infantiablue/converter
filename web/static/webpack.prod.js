const merge = require('webpack-merge');
const common = require('./webpack.common.js');
//const UglifyJsPlugin = require('uglifyjs-webpack-plugin')
const TerserPlugin = require('terser-webpack-plugin');

module.exports = merge(common, {
  mode: 'production'
});