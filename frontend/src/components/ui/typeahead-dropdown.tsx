import React, { useState, useEffect, useRef, forwardRef } from 'react';
import { Check, ChevronsUpDown, X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './button';
import { Input } from './input';
import { Badge } from './badge';
import type { TypeAheadOption } from '../../types/system-settings';

interface TypeAheadDropdownProps {
  options: TypeAheadOption[];
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  allowCustom?: boolean;
  multiple?: boolean;
  selectedValues?: string[];
  onMultipleChange?: (values: string[]) => void;
}

export const TypeAheadDropdown = forwardRef<HTMLDivElement, TypeAheadDropdownProps>(
  ({ 
    options, 
    value, 
    onChange, 
    placeholder = "Select an option...", 
    className,
    disabled = false,
    allowCustom = false,
    multiple = false,
    selectedValues = [],
    onMultipleChange
  }, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredOptions, setFilteredOptions] = useState<TypeAheadOption[]>([]);
    const [customValue, setCustomValue] = useState('');
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Filter options based on search term
    useEffect(() => {
      if (searchTerm.trim() === '') {
        setFilteredOptions(options);
      } else {
        const filtered = options.filter(option =>
          option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
          option.setting_key.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredOptions(filtered);
      }
    }, [searchTerm, options]);

    // Handle click outside to close dropdown
    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
          setIsOpen(false);
          setSearchTerm('');
        }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (option: TypeAheadOption) => {
      if (multiple && onMultipleChange) {
        const newValues = selectedValues.includes(option.setting_key)
          ? selectedValues.filter(v => v !== option.setting_key)
          : [...selectedValues, option.setting_key];
        onMultipleChange(newValues);
      } else {
        onChange(option.setting_key);
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    const handleCustomValue = () => {
      if (customValue.trim() && allowCustom) {
        onChange(customValue.trim());
        setIsOpen(false);
        setCustomValue('');
        setSearchTerm('');
      }
    };

    const removeSelected = (valueToRemove: string) => {
      if (onMultipleChange) {
        onMultipleChange(selectedValues.filter(v => v !== valueToRemove));
      }
    };

    const getDisplayValue = () => {
      if (multiple) {
        return selectedValues.length > 0 ? `${selectedValues.length} selected` : placeholder;
      }
      
      if (value) {
        const option = options.find(opt => opt.setting_key === value);
        return option ? option.label : value;
      }
      
      return placeholder;
    };

    const isSelected = (option: TypeAheadOption) => {
      if (multiple) {
        return selectedValues.includes(option.setting_key);
      }
      return option.setting_key === value;
    };

    return (
      <div className={cn("relative", className)} ref={dropdownRef}>
        <div className="relative">
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={isOpen}
            className="w-full justify-between"
            onClick={() => !disabled && setIsOpen(!isOpen)}
            disabled={disabled}
          >
            <span className={cn(
              "block truncate",
              (!value && !multiple) || (multiple && selectedValues.length === 0) 
                ? "text-muted-foreground" 
                : ""
            )}>
              {getDisplayValue()}
            </span>
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </div>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-popover text-popover-foreground rounded-md border shadow-md">
            <div className="p-2">
              <Input
                placeholder="Search options..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="mb-2"
                autoFocus
              />
              
              {multiple && selectedValues.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-1">
                  {selectedValues.map((selectedValue) => {
                    const option = options.find(opt => opt.setting_key === selectedValue);
                    return (
                      <Badge key={selectedValue} variant="secondary" className="gap-1">
                        {option?.label || selectedValue}
                        <button
                          onClick={() => removeSelected(selectedValue)}
                          className="ml-1 rounded-full outline-none focus:ring-2 focus:ring-ring"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    );
                  })}
                </div>
              )}

              <div className="max-h-60 overflow-auto">
                {filteredOptions.length === 0 ? (
                  <div className="px-2 py-3 text-sm text-muted-foreground text-center">
                    No options found
                  </div>
                ) : (
                  <>
                    {filteredOptions.map((option) => (
                      <div
                        key={option.id}
                        className={cn(
                          "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground",
                          isSelected(option) && "bg-accent text-accent-foreground"
                        )}
                        onClick={() => handleSelect(option)}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            isSelected(option) ? "opacity-100" : "opacity-0"
                          )}
                        />
                        {option.label}
                      </div>
                    ))}
                    
                    {allowCustom && searchTerm.trim() && !filteredOptions.some(opt => 
                      opt.label.toLowerCase() === searchTerm.toLowerCase()
                    ) && (
                      <div className="border-t pt-2 mt-2">
                        <div className="px-2 py-1.5 text-sm text-muted-foreground">
                          Add custom value:
                        </div>
                        <div className="flex gap-2 px-2">
                          <Input
                            value={customValue}
                            onChange={(e) => setCustomValue(e.target.value)}
                            placeholder={searchTerm}
                            className="flex-1"
                            onKeyDown={(e) => e.key === 'Enter' && handleCustomValue()}
                          />
                          <Button size="sm" onClick={handleCustomValue}>
                            Add
                          </Button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }
);

TypeAheadDropdown.displayName = 'TypeAheadDropdown';
