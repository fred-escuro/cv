import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Header } from '@/components/Header';
import { PageWrapper, PageSection } from '@/components/PageWrapper';
import { Plus, Edit, Trash2, Save, X, Download, Upload } from 'lucide-react';
import { toast } from 'sonner';
import type { TypeAheadOption } from '@/types/system-settings';
import { TypeAheadDropdown } from '@/components/ui/typeahead-dropdown';
import { SettingsCategoryCard } from '@/components/SettingsCategoryCard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface SettingFormData {
  category: string;
  setting_key: string;
  label: string;
  value?: string;
  sort_order: number;
  is_active: boolean;
}

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<Record<string, TypeAheadOption[]>>({});
  const [deletedSettings, setDeletedSettings] = useState<Record<string, TypeAheadOption[]>>({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [editingSetting, setEditingSetting] = useState<TypeAheadOption | null>(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [showDeletedItems, setShowDeletedItems] = useState(false);
  const [formData, setFormData] = useState<SettingFormData>({
    category: '',
    setting_key: '',
    label: '',
    value: '',
    sort_order: 0,
    is_active: true
  });
  
  const editingItemRef = useRef<HTMLDivElement>(null);

  // Fetch all settings on component mount
  useEffect(() => {
    fetchAllSettings();
    fetchDeletedSettings();
  }, []);

  // Scroll to editing item when it changes
  useEffect(() => {
    if (editingSetting && editingItemRef.current) {
      editingItemRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
    }
  }, [editingSetting]);

  // Update form data when editing setting changes
  useEffect(() => {
    if (editingSetting) {
      setFormData({
        category: editingSetting.category,
        setting_key: editingSetting.setting_key,
        label: editingSetting.label,
        value: editingSetting.value || '',
        sort_order: editingSetting.sort_order,
        is_active: editingSetting.is_active
      });
    }
  }, [editingSetting]);

  const fetchAllSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/settings`);
      if (!response.ok) {
        throw new Error(`Failed to fetch settings: ${response.statusText}`);
      }
      
      const result = await response.json();
      if (result.success) {
        // Convert string IDs to numbers to match TypeAheadOption interface
        const convertedData: Record<string, TypeAheadOption[]> = {};
        Object.entries(result.data).forEach(([category, settings]) => {
          convertedData[category] = (settings as any[]).map(setting => ({
            ...setting,
            id: parseInt(setting.id.toString()),
            category: setting.category,
            setting_key: setting.setting_key,
            label: setting.label,
            value: setting.value || '',
            sort_order: setting.sort_order || 0,
            is_active: setting.is_active || false
          }));
        });
        setSettings(convertedData);
      } else {
        throw new Error('Failed to fetch settings');
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDeletedSettings = async () => {
    try {
      console.log('🔍 Frontend: Fetching deleted settings...');
      const response = await fetch(`${API_BASE_URL}/api/settings/deleted`);
      if (!response.ok) {
        throw new Error(`Failed to fetch deleted settings: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('🔍 Frontend: API response:', result);
      
      if (result.success) {
        // Convert string IDs to numbers to match TypeAheadOption interface
        const convertedData: Record<string, TypeAheadOption[]> = {};
        Object.entries(result.data).forEach(([category, settings]) => {
          convertedData[category] = (settings as any[]).map(setting => ({
            ...setting,
            id: parseInt(setting.id.toString()),
            category: setting.category,
            setting_key: setting.setting_key,
            label: setting.label,
            value: setting.value || '',
            sort_order: setting.sort_order || 0,
            is_active: setting.is_active || false
          }));
        });
        console.log('🔍 Frontend: Converted deleted settings:', convertedData);
        setDeletedSettings(convertedData);
      } else {
        throw new Error('Failed to fetch deleted settings');
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching deleted settings:', err);
    }
  };

  const handleAddNew = (category?: string) => {
    setIsAddingNew(true);
    setFormData({
      category: category || '',
      setting_key: '',
      label: '',
      value: '',
      sort_order: 0,
      is_active: true
    });
  };

  const handleEdit = (setting: TypeAheadOption) => {
    setEditingSetting(setting);
    setFormData({
      category: setting.category,
      setting_key: setting.setting_key,
      label: setting.label,
      value: setting.value || '',
      sort_order: setting.sort_order,
      is_active: setting.is_active
    });
  };

  const handleCancel = () => {
    setEditingSetting(null);
    setIsAddingNew(false);
    setFormData({
      category: '',
      setting_key: '',
      label: '',
      value: '',
      sort_order: 0,
      is_active: true
    });
  };

  const handleSave = async () => {
    try {
      if (!formData.category || !formData.setting_key || !formData.label) {
        toast.error('Please fill in all required fields');
        return;
      }

      // Validate setting_key format (should be lowercase with underscores)
      if (!/^[a-z0-9_]+$/.test(formData.setting_key)) {
        toast.error('Setting key should contain only lowercase letters, numbers, and underscores');
        return;
      }

      // Check for duplicate setting_key within the same category
      const existingSettings = settings[formData.category] || [];
      const duplicateExists = existingSettings.some(
        s => s.setting_key === formData.setting_key && s.id !== editingSetting?.id
      );
      
      if (duplicateExists) {
        toast.error('A setting with this key already exists in this category');
        return;
      }

      if (editingSetting) {
        // Update existing setting
        const response = await fetch(`${API_BASE_URL}/api/settings/${editingSetting.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          throw new Error(`Failed to update setting: ${response.statusText}`);
        }

        toast.success('Setting updated successfully');
      } else {
        // Create new setting
        const response = await fetch(`${API_BASE_URL}/api/settings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          throw new Error(`Failed to create setting: ${response.statusText}`);
        }

        toast.success('Setting created successfully');
      }

      // Refresh settings and reset form
      await fetchAllSettings();
      handleCancel();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error saving setting:', err);
    }
  };

  const handleDelete = async (setting: TypeAheadOption) => {
    if (!confirm(`Are you sure you want to delete "${setting.label}"?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/${setting.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete setting: ${response.statusText}`);
      }

      toast.success('Setting deleted successfully');
      await fetchAllSettings();
      await fetchDeletedSettings();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error deleting setting:', err);
    }
  };

  const handleRestore = async (setting: TypeAheadOption) => {
    if (!confirm(`Are you sure you want to restore "${setting.label}"?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/${setting.id}/restore`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Failed to restore setting: ${response.statusText}`);
      }

      toast.success('Setting restored successfully');
      await fetchAllSettings();
      await fetchDeletedSettings();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error restoring setting:', err);
    }
  };

  const handlePermanentDelete = async (setting: TypeAheadOption) => {
    if (!confirm(`Are you sure you want to PERMANENTLY delete "${setting.label}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/${setting.id}/permanent`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to permanently delete setting: ${response.statusText}`);
      }

      toast.success('Setting permanently deleted');
      await fetchAllSettings();
      await fetchDeletedSettings();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error permanently deleting setting:', err);
    }
  };

  // Generate category options for the type-ahead dropdown
  const categoryOptions = Object.keys(settings).map(category => ({
    id: category,
    category: category,
    setting_key: category,
    label: category.replace(/_/g, ' '),
    value: category,
    sort_order: 0,
    is_active: true
  }));

  const filteredSettings = searchTerm 
    ? Object.entries(settings).filter(([category]) =>
        category.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : Object.entries(settings);

  // Merge active and deleted settings for display
  const getMergedSettings = (category: string): TypeAheadOption[] => {
    const activeSettings = settings[category] || [];
    const deletedSettingsForCategory = deletedSettings[category] || [];
    console.log(`🔍 Merging settings for category ${category}:`, {
      active: activeSettings.length,
      deleted: deletedSettingsForCategory.length,
      activeSettings,
      deletedSettings: deletedSettingsForCategory
    });
    return [...activeSettings, ...deletedSettingsForCategory];
  };

  const debugDatabase = async () => {
    try {
      console.log('🔍 Debug: Checking database state...');
      const response = await fetch(`${API_BASE_URL}/api/settings/debug`);
      if (response.ok) {
        console.log('🔍 Debug: Database check completed, check console for output');
      }
    } catch (err) {
      console.error('Debug failed:', err);
    }
  };

  const mergedFilteredSettings = searchTerm 
    ? Object.entries(settings).filter(([category]) =>
        category.toLowerCase().includes(searchTerm.toLowerCase())
      ).map(([category]) => [category, getMergedSettings(category)] as [string, TypeAheadOption[]])
    : Object.entries(settings).map(([category]) => [category, getMergedSettings(category)] as [string, TypeAheadOption[]]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <PageWrapper className="mx-auto max-w-full px-2 sm:px-4 lg:px-6 py-2">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-current border-t-transparent mx-auto mb-4"></div>
              <p>Loading settings...</p>
            </div>
          </div>
        </PageWrapper>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <PageWrapper className="mx-auto max-w-full px-20 sm:px-22 lg:px-26 py-2">
        {/* Header Section */}
        <PageSection index={0}>
          <div className="mb-6">
            <h1 className="text-3xl font-bold tracking-tight">System Settings</h1>
            <p className="text-muted-foreground">
              Manage system-wide settings and configurations
            </p>
          </div>
        </PageSection>

        {/* Settings Management */}
        <PageSection index={1}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* First Column - Settings List */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">Settings by Category</CardTitle>
                    <div className="flex gap-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={async () => {
                          setShowDeletedItems(!showDeletedItems);
                          if (!showDeletedItems) {
                            // Only fetch deleted settings when showing them
                            await fetchDeletedSettings();
                          }
                        }}
                        className="gap-1 text-xs"
                      >
                        {showDeletedItems ? 'Hide' : 'Show'} Deleted
                      </Button>
                      <Button variant="outline" size="sm" className="gap-1 text-xs">
                        <Upload className="h-3 w-3" />
                        Import
                      </Button>
                      <Button variant="outline" size="sm" className="gap-1 text-xs">
                        <Download className="h-3 w-3" />
                        Export
                      </Button>
                      <Button onClick={() => handleAddNew()} size="sm" className="gap-1 text-xs">
                        <Plus className="h-3 w-3" />
                        Add New
                      </Button>
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-medium mb-2 block">Search Categories</label>
                    <TypeAheadDropdown
                      options={categoryOptions}
                      value={searchTerm}
                      onChange={(value) => setSearchTerm(value)}
                      placeholder="Search or select a category..."
                      allowCustom={true}
                      className="text-xs"
                    />
                  </div>
                </CardHeader>
                <CardContent className="p-3">
                  <div className="space-y-3">
                     {mergedFilteredSettings.map(([category, categorySettings]) => (
                       <SettingsCategoryCard
                         key={category}
                         category={category}
                         settings={categorySettings}
                         onEdit={handleEdit}
                         onDelete={handleDelete}
                         onRestore={handleRestore}
                         onPermanentDelete={handlePermanentDelete}
                         onAddNew={handleAddNew}
                         editingSettingId={editingSetting?.id || null}
                         editingItemRef={editingItemRef}
                         showDeletedItems={showDeletedItems}
                       />
                     ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Second Column - Add/Edit Form - Sticky */}
            <div className="lg:col-span-1">
              <div className="sticky top-4">
                <Card>
                  <CardHeader className="p-3">
                    <CardTitle className="text-sm">
                      {editingSetting ? 'Edit Setting' : isAddingNew ? 'Add New Setting' : 'Setting Details'}
                    </CardTitle>
                    {editingSetting && (
                      <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-md">
                        <div className="text-xs text-blue-800">
                          <strong>Currently editing:</strong> {editingSetting.label}
                          <br />
                          <span className="text-blue-600">
                            Category: {editingSetting.category} • Key: {editingSetting.setting_key}
                          </span>
                        </div>
                      </div>
                    )}
                  </CardHeader>
                  <CardContent className="p-3">
                    {(editingSetting || isAddingNew) ? (
                      <div className="space-y-3">
                        <div>
                          <label className="text-xs font-medium mb-1 block">Category *</label>
                          <Input
                            value={formData.category}
                            onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                            placeholder="e.g., gender, civil_status"
                            className="text-xs h-8"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Use lowercase with underscores
                          </p>
                        </div>
                        
                        <div>
                          <label className="text-xs font-medium mb-1 block">Setting Key *</label>
                          <Input
                            value={formData.setting_key}
                            onChange={(e) => setFormData(prev => ({ ...prev, setting_key: e.target.value }))}
                            placeholder="e.g., male, single"
                            className="text-xs h-8"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Unique identifier (lowercase, no spaces)
                          </p>
                        </div>
                        
                        <div>
                          <label className="text-xs font-medium mb-1 block">Label *</label>
                          <Input
                            value={formData.label}
                            onChange={(e) => setFormData(prev => ({ ...prev, label: e.target.value }))}
                            placeholder="e.g., Male, Single"
                            className="text-xs h-8"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Human-readable display text
                          </p>
                        </div>
                        
                        <div>
                          <label className="text-xs font-medium mb-1 block">Value (Optional)</label>
                          <Input
                            value={formData.value}
                            onChange={(e) => setFormData(prev => ({ ...prev, value: e.target.value }))}
                            placeholder="e.g., 1 for proficiency level"
                            className="text-xs h-8"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Additional data (e.g., numeric values)
                          </p>
                        </div>
                        
                        <div>
                          <label className="text-xs font-medium mb-1 block">Sort Order</label>
                          <Input
                            type="number"
                            value={formData.sort_order}
                            onChange={(e) => setFormData(prev => ({ ...prev, sort_order: parseInt(e.target.value) || 0 }))}
                            placeholder="0"
                            className="text-xs h-8"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Display order (lower numbers first)
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="is_active"
                            checked={formData.is_active}
                            onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                            className="rounded"
                          />
                          <label htmlFor="is_active" className="text-xs font-medium">
                            Active
                          </label>
                        </div>
                        
                        <div className="flex gap-2 pt-3">
                          <Button onClick={handleSave} size="sm" className="flex-1 text-xs h-8">
                            <Save className="h-3 w-3 mr-1" />
                            {editingSetting ? 'Update' : 'Create'}
                          </Button>
                          <Button variant="outline" onClick={handleCancel} size="sm" className="text-xs h-8">
                            <X className="h-3 w-3 mr-1" />
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center text-muted-foreground py-6">
                        <p className="text-xs">Select a setting to edit or click "Add New" to create one</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </PageSection>
      </PageWrapper>
    </div>
  );
};
