import Link from 'next/link';
import { t } from '@/lib/i18n';

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100" dir="rtl">
      <div className="text-center p-8 md:p-12 bg-white rounded-2xl shadow-xl max-w-2xl mx-4">
        <div className="text-6xl mb-6">🤖</div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-indigo-600 mb-4">
          DocuChat
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-700 mb-2">
          {t('ready')}
        </p>
        
        <p className="text-gray-500 mb-8">
          {t('description')}
        </p>

        <Link
          href="/chat"
          className="inline-block px-8 py-4 bg-indigo-600 text-white text-lg font-medium rounded-xl hover:bg-indigo-700 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform"
        >
          {t('startChat')}
        </Link>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            {t('version')} {process.env.NEXT_PUBLIC_APP_VERSION || '0.1.0'}
          </p>
          <div className="flex items-center justify-center gap-4 mt-4 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              {t('backendActive')}
            </span>
            <span>•</span>
            <span>{t('openaiOnly')}</span>
            <span>•</span>
            <span>{t('rtlPersian')}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
