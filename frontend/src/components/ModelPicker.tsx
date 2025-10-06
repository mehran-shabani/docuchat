import React, { useState, useEffect } from 'react';
import { ALLOWED_OPENAI_MODELS, type OpenAIModel } from '@/types';
import { t } from '@/lib/i18n';

interface ModelPickerProps {
  onModelChange: (model: OpenAIModel) => void;
  currentModel?: OpenAIModel;
}

const resolveModel = (value?: string | null): OpenAIModel => {
  const allowed: string[] = [...ALLOWED_OPENAI_MODELS];
  return value && allowed.includes(value)
    ? (value as OpenAIModel)
    : 'gpt-3.5-turbo';
};

export const ModelPicker: React.FC<ModelPickerProps> = ({
  onModelChange,
  currentModel,
}) => {
  const [selectedModel, setSelectedModel] = useState<OpenAIModel>(
    resolveModel(currentModel ?? process.env.NEXT_PUBLIC_OPENAI_MODEL)
  );
  const [availableModels, setAvailableModels] = useState<OpenAIModel[]>([]);

  useEffect(() => {
    // Parse available models from environment variable
    const modelOptions = process.env.NEXT_PUBLIC_MODEL_OPTIONS || 'gpt-3.5-turbo,gpt-4o,gpt-4o-mini';
    const allowed: string[] = [...ALLOWED_OPENAI_MODELS];
    const models = modelOptions
      .split(',')
      .map(m => m.trim())
      .filter(m => allowed.includes(m)) as OpenAIModel[];

    const safeModels: OpenAIModel[] = models.length > 0 ? models : ['gpt-3.5-turbo'];
    setAvailableModels(safeModels);
    setSelectedModel(prev => (safeModels.includes(prev) ? prev : safeModels[0]));
  }, []);

  useEffect(() => {
    if (currentModel) {
      setSelectedModel(resolveModel(currentModel));
    }
  }, [currentModel]);

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const model = event.target.value as OpenAIModel;
    const allowed: string[] = [...ALLOWED_OPENAI_MODELS];
    if (allowed.includes(model)) {
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
