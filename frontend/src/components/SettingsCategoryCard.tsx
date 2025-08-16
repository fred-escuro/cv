import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Edit, Trash2, Plus, RotateCcw, Trash } from 'lucide-react';
import type { TypeAheadOption } from '@/types/system-settings';

interface SettingsCategoryCardProps {
  category: string;
  settings: TypeAheadOption[];
  onEdit: (setting: TypeAheadOption) => void;
  onDelete: (setting: TypeAheadOption) => void;
  onRestore?: (setting: TypeAheadOption) => void;
  onPermanentDelete?: (setting: TypeAheadOption) => void;
  onAddNew: (category: string) => void;
  editingSettingId?: number | null;
  editingItemRef?: React.RefObject<HTMLDivElement> | null;
  showDeletedItems?: boolean;
}

export const SettingsCategoryCard: React.FC<SettingsCategoryCardProps> = ({
  category,
  settings,
  onEdit,
  onDelete,
  onRestore,
  onPermanentDelete,
  onAddNew,
  editingSettingId,
  editingItemRef,
  showDeletedItems = false
}) => {
  const activeSettings = settings.filter(s => s.is_active);
  const inactiveSettings = settings.filter(s => !s.is_active);

  return (
    <Card className="w-full">
      <CardHeader className="p-3">
        <div className="flex items-center justify-between">
          <CardTitle className="capitalize text-sm">
            {category.replace(/_/g, ' ')}
            <Badge variant="secondary" className="ml-2 text-xs">
              {activeSettings.length} active
            </Badge>
            {inactiveSettings.length > 0 && (
              <Badge variant="outline" className="ml-1 text-xs text-red-600 border-red-300">
                {inactiveSettings.length} deleted
              </Badge>
            )}
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddNew(category)}
            className="gap-1 text-xs h-6"
          >
            <Plus className="h-3 w-3" />
            Add
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-3">
        <div className="space-y-2">
          {/* Active Settings */}
          {activeSettings.map((setting) => {
            const isEditing = editingSettingId === setting.id;
            return (
              <div
                key={setting.id}
                ref={isEditing && editingItemRef ? editingItemRef : undefined}
                className={`flex items-center justify-between p-2 rounded-md transition-all duration-200 ${
                  isEditing
                    ? 'bg-blue-50 border-2 border-blue-300 shadow-md ring-2 ring-blue-100'
                    : 'bg-green-50 border border-green-200 hover:bg-green-100 hover:border-green-300'
                }`}
              >
                <div className="flex-1">
                  <div className={`font-medium text-xs ${
                    isEditing ? 'text-blue-900' : 'text-green-900'
                  }`}>
                    {setting.label}
                    {isEditing && (
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Editing
                      </span>
                    )}
                  </div>
                  <div className={`text-xs ${
                    isEditing ? 'text-blue-700' : 'text-green-700'
                  }`}>
                    Key: <code className={`px-1 rounded text-xs ${
                      isEditing ? 'bg-blue-100' : 'bg-green-100'
                    }`}>{setting.setting_key}</code>
                    {setting.value && (
                      <>
                        {' • '}Value: <code className={`px-1 rounded text-xs ${
                          isEditing ? 'bg-blue-100' : 'bg-green-100'
                        }`}>{setting.value}</code>
                      </>
                    )}
                    {' • '}Order: {setting.sort_order}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant={isEditing ? "default" : "outline"}
                    size="sm"
                    onClick={() => onEdit(setting)}
                    className={`h-6 w-6 p-0 ${
                      isEditing
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'border-green-300 text-green-700 hover:bg-green-100'
                    }`}
                    disabled={isEditing}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onDelete(setting)}
                    className="border-red-300 text-red-700 hover:bg-red-100 h-6 w-6 p-0"
                    disabled={isEditing}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            );
          })}

          {/* Inactive Settings */}
          {inactiveSettings.length > 0 && showDeletedItems && (
            <div className="mt-3">
              <h4 className="text-xs font-medium text-muted-foreground mb-2">
                Deleted Settings ({inactiveSettings.length})
              </h4>
              {inactiveSettings.map((setting) => {
                const isEditing = editingSettingId === setting.id;
                return (
                  <div
                    key={setting.id}
                    className={`flex items-center justify-between p-2 rounded-md transition-all duration-200 ${
                      isEditing
                        ? 'bg-blue-50 border-2 border-blue-300 shadow-md ring-2 ring-blue-100 opacity-100'
                        : 'bg-red-50 border border-red-200 opacity-80 hover:opacity-100 hover:bg-red-100'
                    }`}
                  >
                    <div className="flex-1">
                      <div className={`font-medium text-xs ${
                        isEditing ? 'text-blue-900' : 'text-red-800'
                      }`}>
                        {setting.label}
                        {isEditing && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Editing
                          </span>
                        )}
                        <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Deleted
                        </span>
                      </div>
                      <div className={`text-xs ${
                        isEditing ? 'text-blue-700' : 'text-red-700'
                      }`}>
                        Key: <code className={`px-1 rounded text-xs ${
                          isEditing ? 'bg-blue-100' : 'bg-red-100'
                        }`}>{setting.setting_key}</code>
                        {setting.value && (
                          <>
                            {' • '}Value: <code className={`px-1 rounded text-xs ${
                              isEditing ? 'bg-blue-100' : 'bg-red-100'
                            }`}>{setting.value}</code>
                          </>
                        )}
                        {' • '}Order: {setting.sort_order}
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      {onRestore && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onRestore(setting)}
                          className="border-green-300 text-green-700 hover:bg-green-100 h-6 w-6 p-0"
                          disabled={isEditing}
                          title="Restore setting"
                        >
                          <RotateCcw className="h-3 w-3" />
                        </Button>
                      )}
                      {onPermanentDelete && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onPermanentDelete(setting)}
                          className="border-red-600 text-red-700 hover:bg-red-200 h-6 w-6 p-0"
                          disabled={isEditing}
                          title="Permanently delete"
                        >
                          <Trash className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {settings.length === 0 && (
            <div className="text-center py-4 text-muted-foreground">
              <p className="text-xs">No settings found for this category</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
