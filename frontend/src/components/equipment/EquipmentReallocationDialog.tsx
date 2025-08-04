import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Calendar, Truck } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface EquipmentReallocationData {
  equipmentIds: string[];
  newReplacementYear: number;
}

export const EquipmentReallocationDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [reallocationData, setReallocationData] = useState<EquipmentReallocationData>({
    equipmentIds: [],
    newReplacementYear: new Date().getFullYear() + 1,
  });
  const [equipmentIdsText, setEquipmentIdsText] = useState('');

  const handleEquipmentIdsChange = (value: string) => {
    setEquipmentIdsText(value);
    // Parse equipment IDs from textarea (comma, space, or newline separated)
    const ids = value
      .split(/[,\s\n]+/)
      .map(id => id.trim())
      .filter(id => id.length > 0);
    
    setReallocationData(prev => ({
      ...prev,
      equipmentIds: ids
    }));
  };

  const handleSubmit = async () => {
    if (reallocationData.equipmentIds.length === 0) {
      toast({
        title: "Validation Error",
        description: "Please enter at least one equipment ID.",
        variant: "destructive"
      });
      return;
    }

    if (reallocationData.newReplacementYear < 2024 || reallocationData.newReplacementYear > 2050) {
      toast({
        title: "Validation Error", 
        description: "Please enter a valid replacement year between 2024 and 2050.",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:3300/api/equipment/reallocate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          equipmentIds: reallocationData.equipmentIds,
          newReplacementYear: reallocationData.newReplacementYear
        }),
      });

      const result = await response.json();

      if (result.success) {
        toast({
          title: "Equipment Reallocation Successful",
          description: `Updated replacement schedules for ${reallocationData.equipmentIds.length} equipment(s) to year ${reallocationData.newReplacementYear}.`,
        });
        
        // Reset form and close dialog
        setEquipmentIdsText('');
        setReallocationData({
          equipmentIds: [],
          newReplacementYear: new Date().getFullYear() + 1,
        });
        setIsOpen(false);
      } else {
        throw new Error(result.message || 'Equipment reallocation failed');
      }
    } catch (error) {
      toast({
        title: "Equipment Reallocation Failed",
        description: error instanceof Error ? error.message : 'An unexpected error occurred.',
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setEquipmentIdsText('');
    setReallocationData({
      equipmentIds: [],
      newReplacementYear: new Date().getFullYear() + 1,
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Calendar className="w-4 h-4 mr-2" />
          Equipment Reallocation
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Truck className="w-5 h-5 text-primary" />
            <span>Equipment Replacement Schedule</span>
          </DialogTitle>
          <p className="text-sm text-muted-foreground mt-2">
            Update replacement schedules for specific equipment based on their lifecycle data.
            This will modify the vehicle fleet master data with new forecast schedules.
          </p>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Equipment IDs Input */}
          <div className="space-y-2">
            <Label htmlFor="equipment-ids">Equipment IDs</Label>
            <Textarea
              id="equipment-ids"
              placeholder="Enter equipment IDs separated by commas, spaces, or new lines (e.g., VV12205, VV18683, VV19001)"
              value={equipmentIdsText}
              onChange={(e) => handleEquipmentIdsChange(e.target.value)}
              className="min-h-[100px]"
            />
            {reallocationData.equipmentIds.length > 0 && (
              <p className="text-xs text-muted-foreground">
                {reallocationData.equipmentIds.length} equipment(s) parsed: {reallocationData.equipmentIds.join(', ')}
              </p>
            )}
          </div>

          {/* New Replacement Year */}
          <div className="space-y-2">
            <Label htmlFor="replacement-year">New Replacement Year</Label>
            <Input
              id="replacement-year"
              type="number"
              min="2024"
              max="2050"
              step="1"
              value={reallocationData.newReplacementYear}
              onChange={(e) => setReallocationData(prev => ({
                ...prev,
                newReplacementYear: parseInt(e.target.value) || new Date().getFullYear() + 1
              }))}
            />
            <p className="text-xs text-muted-foreground">
              The system will calculate future replacement years based on each equipment's lifecycle data.
            </p>
          </div>

          {/* Preview Information */}
          {reallocationData.equipmentIds.length > 0 && (
            <div className="bg-muted/50 p-4 rounded-lg">
              <h4 className="text-sm font-semibold mb-2">Preview</h4>
              <ul className="text-sm space-y-1">
                <li>• Equipment Count: <strong>{reallocationData.equipmentIds.length}</strong></li>
                <li>• Starting Replacement Year: <strong>{reallocationData.newReplacementYear}</strong></li>
                <li>• Future schedules will be calculated based on individual equipment lifecycle data</li>
                <li>• All existing forecast schedules for these equipment will be reset</li>
              </ul>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={handleReset} disabled={isLoading}>
              Reset
            </Button>
            <Button 
              onClick={handleSubmit} 
              disabled={isLoading || reallocationData.equipmentIds.length === 0}
            >
              {isLoading ? "Processing..." : "Update Replacement Schedule"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};