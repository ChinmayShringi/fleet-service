import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Settings, DollarSign } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface CostParameters {
  fuelCostPerGallon: number;
  maintenanceRate: number;
  insuranceRate: number;
  depreciationRate: number;
  utilityRate: number;
}

export const CostParametersDialog: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [parameters, setParameters] = useState<CostParameters>({
    fuelCostPerGallon: 3.45,
    maintenanceRate: 0.15,
    insuranceRate: 0.08,
    depreciationRate: 0.12,
    utilityRate: 0.95,
  });

  const handleSave = () => {
    // Save parameters to local storage or API
    localStorage.setItem('pseg_cost_parameters', JSON.stringify(parameters));
    
    toast({
      title: "Cost Parameters Updated",
      description: "Fleet cost calculations will use the new parameters.",
    });
    
    setIsOpen(false);
  };

  const handleReset = () => {
    setParameters({
      fuelCostPerGallon: 3.45,
      maintenanceRate: 0.15,
      insuranceRate: 0.08,
      depreciationRate: 0.12,
      utilityRate: 0.95,
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <DollarSign className="w-4 h-4 mr-2" />
          Cost Parameters
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-primary" />
            <span>Fleet Cost Parameters</span>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="fuel-cost">Fuel Cost per Gallon ($)</Label>
            <Input
              id="fuel-cost"
              type="number"
              step="0.01"
              value={parameters.fuelCostPerGallon}
              onChange={(e) => setParameters(prev => ({
                ...prev,
                fuelCostPerGallon: parseFloat(e.target.value) || 0
              }))}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="maintenance-rate">Maintenance Rate (%)</Label>
            <Input
              id="maintenance-rate"
              type="number"
              step="0.01"
              value={parameters.maintenanceRate * 100}
              onChange={(e) => setParameters(prev => ({
                ...prev,
                maintenanceRate: (parseFloat(e.target.value) || 0) / 100
              }))}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="insurance-rate">Insurance Rate (%)</Label>
            <Input
              id="insurance-rate"
              type="number"
              step="0.01"
              value={parameters.insuranceRate * 100}
              onChange={(e) => setParameters(prev => ({
                ...prev,
                insuranceRate: (parseFloat(e.target.value) || 0) / 100
              }))}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="depreciation-rate">Depreciation Rate (%)</Label>
            <Input
              id="depreciation-rate"
              type="number"
              step="0.01"
              value={parameters.depreciationRate * 100}
              onChange={(e) => setParameters(prev => ({
                ...prev,
                depreciationRate: (parseFloat(e.target.value) || 0) / 100
              }))}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="utility-rate">Fleet Utilization Rate (%)</Label>
            <Input
              id="utility-rate"
              type="number"
              step="0.01"
              value={parameters.utilityRate * 100}
              onChange={(e) => setParameters(prev => ({
                ...prev,
                utilityRate: (parseFloat(e.target.value) || 0) / 100
              }))}
            />
          </div>

          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={handleReset}>
              Reset to Defaults
            </Button>
            <Button onClick={handleSave}>
              Save Parameters
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};