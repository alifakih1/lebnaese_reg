module.exports = {
  entry: {
    'lebanese_regulations': './lebanese_regulations/public/js/index.js',
  },
  output: {
    filename: '[name].bundle.js',
    path: __dirname + '/lebanese_regulations/public/dist',
  },
  resolve: {
    extensions: ['.js', '.json'],
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
};