import { useState, useEffect } from 'react';
import type { TypeAheadOption } from '../types/system-settings';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useSystemSettings = () => {
  const [settings, setSettings] = useState<Record<string, TypeAheadOption[]>>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAllSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/settings`);
      if (!response.ok) {
        throw new Error(`Failed to fetch settings: ${response.statusText}`);
      }
      
      const result = await response.json();
      if (result.success) {
        setSettings(result.data);
      } else {
        throw new Error('Failed to fetch settings');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSettingsByCategory = async (category: string): Promise<TypeAheadOption[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/${category}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${category} settings: ${response.statusText}`);
      }
      
      const result = await response.json();
      if (result.success) {
        return result.data;
      } else {
        throw new Error(`Failed to fetch ${category} settings`);
      }
    } catch (err) {
      console.error(`Error fetching ${category} settings:`, err);
      return [];
    }
  };

  const getSettingsByCategory = (category: string): TypeAheadOption[] => {
    return settings[category] || [];
  };

  const getSettingLabel = (category: string, settingKey: string): string => {
    const categorySettings = settings[category] || [];
    const setting = categorySettings.find(s => s.setting_key === settingKey);
    return setting ? setting.label : settingKey;
  };

  useEffect(() => {
    fetchAllSettings();
  }, []);

  return {
    settings,
    loading,
    error,
    fetchAllSettings,
    fetchSettingsByCategory,
    getSettingsByCategory,
    getSettingLabel,
  };
};
