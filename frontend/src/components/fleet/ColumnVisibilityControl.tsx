import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Columns } from 'lucide-react';

interface Column {
  key: string;
  label: string;
  visible: boolean;
}

interface ColumnVisibilityProps {
  columns: Column[];
  onColumnChange: (columns: Column[]) => void;
}

export const ColumnVisibilityControl: React.FC<ColumnVisibilityProps> = ({
  columns,
  onColumnChange,
}) => {
  const handleColumnToggle = (columnKey: string) => {
    const updatedColumns = columns.map(col =>
      col.key === columnKey ? { ...col, visible: !col.visible } : col
    );
    onColumnChange(updatedColumns);
  };

  const visibleCount = columns.filter(col => col.visible).length;

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm">
          <Columns className="w-4 h-4 mr-2" />
          Columns ({visibleCount})
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-56" align="end">
        <div className="space-y-2">
          <h4 className="font-medium text-sm">Toggle Columns</h4>
          <div className="space-y-2">
            {columns.map((column) => (
              <div key={column.key} className="flex items-center space-x-2">
                <Checkbox
                  id={column.key}
                  checked={column.visible}
                  onCheckedChange={() => handleColumnToggle(column.key)}
                />
                <label
                  htmlFor={column.key}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {column.label}
                </label>
              </div>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};