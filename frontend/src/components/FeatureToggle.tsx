import React, { useState, useEffect } from 'react';
import type { FeatureFlags } from '@/types';
import { t } from '@/lib/i18n';

interface FeatureToggleProps {
  onFlagsChange?: (flags: FeatureFlags) => void;
}

export const FeatureToggle: React.FC<FeatureToggleProps> = ({ onFlagsChange }) => {
  const [flags, setFlags] = useState<FeatureFlags>({
    enableWs: false,
    enablePdfUpload: false,
    enableTeamSharing: false,
  });

  useEffect(() => {
    // Load feature flags from environment
    const newFlags: FeatureFlags = {
      enableWs: process.env.NEXT_PUBLIC_ENABLE_WS === 'true',
      enablePdfUpload: process.env.ENABLE_PDF_UPLOAD === 'true',
      enableTeamSharing: process.env.ENABLE_TEAM_SHARING === 'true',
    };
    setFlags(newFlags);
    
    if (onFlagsChange) {
      onFlagsChange(newFlags);
    }
  }, [onFlagsChange]);

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4" dir="rtl">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{t('settings')}</h3>
      
      <div className="space-y-2">
        <FeatureItem
          label={flags.enableWs ? t('wsEnabled') : t('wsDisabled')}
          enabled={flags.enableWs}
          icon="🔄"
        />
        
        <FeatureItem
          label={flags.enablePdfUpload ? t('pdfUploadEnabled') : t('pdfUploadDisabled')}
          enabled={flags.enablePdfUpload}
          icon="📄"
        />
        
        {flags.enableTeamSharing && (
          <FeatureItem
            label="اشتراک‌گذاری تیمی فعال"
            enabled={flags.enableTeamSharing}
            icon="👥"
          />
        )}
      </div>
    </div>
  );
};

interface FeatureItemProps {
  label: string;
  enabled: boolean;
  icon: string;
}

const FeatureItem: React.FC<FeatureItemProps> = ({ label, enabled, icon }) => {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-lg">{icon}</span>
      <span className={enabled ? 'text-green-600 font-medium' : 'text-gray-500'}>
        {label}
      </span>
      <span
        className={`mr-auto w-2 h-2 rounded-full ${
          enabled ? 'bg-green-500' : 'bg-gray-400'
        }`}
      />
    </div>
  );
};
