/** @type {import('next').NextConfig} */

const CopyPlugin = require('copy-webpack-plugin');
const path = require('path');

module.exports = {
  poweredByHeader: false,
  productionBrowserSourceMaps: false,
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Referrer-Policy',
            value: 'same-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'autoplay=(self), fullscreen=(self)',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Expect-CT',
            value: 'max-age=86400, enforce',
          },
        ],
      },
    ];
  },
  output: 'standalone',
  reactStrictMode: true,

  webpack: (config) => {
    const destWasmFolder = 'static/chunks/app';
    config.plugins.push(
      new CopyPlugin({
        patterns: [
          { from: 'node_modules/scichart/_wasm/scichart2d.wasm', to: destWasmFolder },
          {
            from: path.resolve(__dirname, 'pages', 'runtimes'),
            to: 'pages/runtimes',
          },
        ],
      })
    );

    return config;
  },
};
