/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  i18n: {
    locales: ['fa', 'en'],
    defaultLocale: 'fa',
  },
  output: 'standalone',
  env: {
    NEXT_PUBLIC_APP_VERSION: require('./package.json').version,
  },
}

module.exports = nextConfig
