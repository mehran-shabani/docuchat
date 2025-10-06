import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import Head from 'next/head';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="DocuChat - دستیار هوشمند مکالمه با اسناد" />
        <title>DocuChat</title>
      </Head>
      <Component {...pageProps} />
    </>
  );
}
