const path = require("path");
const webpack = require("webpack");
const Dotenv = require("dotenv-webpack");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  entry: "./src/index.jsx",
  output: {
    path: path.resolve(__dirname, "./static/frontend"),
    filename: "[name].js",
  },
  module: {
    rules: [
      {
        test: /\.jsx$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      {
        test: /\.module\.css$/i,
        use: [
          "style-loader",
          {
            loader: "css-loader",
            options: {
              modules: {
                namedExport: false,
              },
            },
          },
        ],
      },
      {
        test: /\.css$/i,
        exclude: /\.module\.css$/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  optimization: {
    minimize: true,
  },
  plugins: [
    new CopyWebpackPlugin({
      patterns: [
        {
          from: "node_modules/cesium/Build/Cesium/Workers",
          to: "../cesium/Workers",
        },
        {
          from: "node_modules/cesium/Build/Cesium/ThirdParty",
          to: "../cesium/ThirdParty",
        },
        {
          from: "node_modules/cesium/Build/Cesium/Assets",
          to: "../cesium/Assets",
        },
        {
          from: "node_modules/cesium/Build/Cesium/Widgets",
          to: "../cesium/Widgets",
        },
      ],
    }),
    new Dotenv({
      path: "../../.env",
      safe: false,
      systemvars: true,
    }),
    new webpack.DefinePlugin({
      "process.env": {
        NODE_END: JSON.stringify("development"),
      },
      CESIUM_BASE_URL: JSON.stringify("/static/cesium"),
    }),
  ],
  resolve: {
    extensions: [".js", ".jsx"],
  },
};
