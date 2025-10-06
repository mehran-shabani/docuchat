import React, { useState, useEffect } from 'react';
import { ALLOWED_OPENAI_MODELS, type OpenAIModel } from '@/types';
import { t } from '@/lib/i18n';

interface ModelPickerProps {
  onModelChange: (model: OpenAIModel) => void;
  currentModel?: OpenAIModel;
}

export const ModelPicker: React.FC<ModelPickerProps> = ({
  onModelChange,
  currentModel,
}) => {
  const [selectedModel, setSelectedModel] = useState<OpenAIModel>(
    currentModel || (process.env.NEXT_PUBLIC_OPENAI_MODEL as OpenAIModel) || 'gpt-3.5-turbo'
  );
  const [availableModels, setAvailableModels] = useState<OpenAIModel[]>([]);

  useEffect(() => {
    // Parse available models from environment variable
    const modelOptions = process.env.NEXT_PUBLIC_MODEL_OPTIONS || 'gpt-3.5-turbo,gpt-4o,gpt-4o-mini';
    const models = modelOptions
      .split(',')
      .map(m => m.trim())
      .filter(m => ALLOWED_OPENAI_MODELS.includes(m as OpenAIModel)) as OpenAIModel[];

    setAvailableModels(models.length > 0 ? models : ['gpt-3.5-turbo']);
  }, []);

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const model = event.target.value as OpenAIModel;
    if (ALLOWED_OPENAI_MODELS.includes(model)) {
      setSelectedModel(model);
      onModelChange(model);
    }
  };

  return (
    <div className="flex items-center gap-2" dir="rtl">
      <label htmlFor="model-select" className="text-sm font-medium text-gray-700">
        {t('model')}:
      </label>
      <select
        id="model-select"
        value={selectedModel}
        onChange={handleChange}
        className="px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        dir="rtl"
      >
        {availableModels.map(model => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
    </div>
  );
};
