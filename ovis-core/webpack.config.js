const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const isDevelopment = process.env.NODE_ENV !== 'production';

module.exports = {
  mode: isDevelopment ? 'development' : 'production',
  target: 'electron-renderer',
  entry: {
    main: './src/main.ts',
    renderer: './src/renderer.tsx',
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@store': path.resolve(__dirname, 'src/store'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@assets': path.resolve(__dirname, 'src/assets'),
    },
  },
  module: {
    rules: [
      // TypeScript 처리
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
      // JavaScript 처리 (Babel)
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-env',
              '@babel/preset-react',
              '@babel/preset-typescript',
            ],
          },
        },
      },
      // CSS 처리
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      // Less 처리 (Ant Design)
      {
        test: /\.less$/,
        use: [
          'style-loader',
          'css-loader',
          {
            loader: 'less-loader',
            options: {
              lessOptions: {
                javascriptEnabled: true,
              },
            },
          },
        ],
      },
      // 이미지 및 폰트 처리
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html',
      filename: 'index.html',
      chunks: ['renderer'],
    }),
  ],
  devtool: isDevelopment ? 'inline-source-map' : 'source-map',
  ...(isDevelopment && {
    watch: true,
    watchOptions: {
      ignored: /node_modules/,
    },
  }),
  node: {
    __dirname: false,
    __filename: false,
  },
  externals: [
    // 네이티브 노드 모듈 제외
    function({ request }, callback) {
      if (['fs', 'path', 'electron'].includes(request)) {
        return callback(null, `commonjs ${request}`);
      }
      callback();
    },
  ],
}; 