import React, { useState, useEffect } from 'react';
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
import { Settings } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface CostParameters {
  // EV Analysis Parameters
  freightlinerEvRatioTotal: number;
  lightEvRatioTotal: number;
  // Heavy Vehicle Costs
  iceChassisHeavy: number;
  evChassisHeavy: number;
  // Van Costs
  iceChassisVan: number;
  evChassisVan: number;
  // Car/SUV Costs
  iceChassisCar: number;
  evChassisCar: number;
  // Pickup Costs
  iceChassisPickup: number;
  evChassisPickup: number;
}

export const CostParametersDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [parameters, setParameters] = useState<CostParameters>({
    // EV Analysis Parameters (from excel_reader.py constants)
    freightlinerEvRatioTotal: 7,
    lightEvRatioTotal: 4,
    // Heavy Vehicle Costs
    iceChassisHeavy: 125000,
    evChassisHeavy: 300000,
    // Van Costs
    iceChassisVan: 62000,
    evChassisVan: 55000,
    // Car/SUV Costs
    iceChassisCar: 43000,
    evChassisCar: 46000,
    // Pickup Costs
    iceChassisPickup: 44000,
    evChassisPickup: 54000,
  });

  // Load saved parameters from localStorage on component mount
  useEffect(() => {
    const savedParameters = localStorage.getItem('pseg_cost_parameters');
    if (savedParameters) {
      try {
        const parsed = JSON.parse(savedParameters);
        setParameters(parsed);
      } catch (error) {
        console.error('Error parsing saved cost parameters:', error);
      }
    }
  }, []);

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
      // EV Analysis Parameters (defaults from excel_reader.py)
      freightlinerEvRatioTotal: 7,
      lightEvRatioTotal: 4,
      // Heavy Vehicle Costs
      iceChassisHeavy: 125000,
      evChassisHeavy: 300000,
      // Van Costs
      iceChassisVan: 62000,
      evChassisVan: 55000,
      // Car/SUV Costs
      iceChassisCar: 43000,
      evChassisCar: 46000,
      // Pickup Costs
      iceChassisPickup: 44000,
      evChassisPickup: 54000,
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Settings className="w-4 h-4 mr-2" />
          EV Parameters
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-primary" />
            <span>EV Analysis Parameters</span>
          </DialogTitle>
          <p className="text-sm text-muted-foreground mt-2">
            Configure EV ratios and chassis costs used in Excel Analysis script execution.
            These parameters will be applied when running reports from the Reports page.
          </p>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* EV Ratios Section */}
          <div>
            <h4 className="text-sm font-semibold mb-3 text-primary">EV Ratios</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="freightliner-ev-ratio">Heavy EV Ratio (Total)</Label>
                <Input
                  id="freightliner-ev-ratio"
                  type="number"
                  step="1"
                  value={parameters.freightlinerEvRatioTotal}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    freightlinerEvRatioTotal: parseInt(e.target.value) || 0
                  }))}
                />
                <p className="text-xs text-muted-foreground">6 ICE : 1 EV = 7 total</p>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="light-ev-ratio">Light EV Ratio (Total)</Label>
                <Input
                  id="light-ev-ratio"
                  type="number"
                  step="1"
                  value={parameters.lightEvRatioTotal}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    lightEvRatioTotal: parseInt(e.target.value) || 0
                  }))}
                />
                <p className="text-xs text-muted-foreground">3 ICE : 1 EV = 4 total</p>
              </div>
            </div>
          </div>

          {/* Heavy Vehicle Costs */}
          <div className="border-t pt-4 mt-4">
            <h4 className="text-sm font-semibold mb-3 text-primary">Heavy Vehicle Chassis Costs</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="ice-chassis-heavy">ICE Heavy Chassis ($)</Label>
                <Input
                  id="ice-chassis-heavy"
                  type="number"
                  step="1000"
                  value={parameters.iceChassisHeavy}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    iceChassisHeavy: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="ev-chassis-heavy">EV Heavy Chassis ($)</Label>
                <Input
                  id="ev-chassis-heavy"
                  type="number"
                  step="1000"
                  value={parameters.evChassisHeavy}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    evChassisHeavy: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>
            </div>
          </div>

          {/* Van Costs */}
          <div className="border-t pt-4 mt-4">
            <h4 className="text-sm font-semibold mb-3 text-primary">Van Chassis Costs</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="ice-chassis-van">ICE Van Chassis ($)</Label>
                <Input
                  id="ice-chassis-van"
                  type="number"
                  step="1000"
                  value={parameters.iceChassisVan}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    iceChassisVan: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="ev-chassis-van">EV Van Chassis ($)</Label>
                <Input
                  id="ev-chassis-van"
                  type="number"
                  step="1000"
                  value={parameters.evChassisVan}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    evChassisVan: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>
            </div>
          </div>

          {/* Car/SUV Costs */}
          <div className="border-t pt-4 mt-4">
            <h4 className="text-sm font-semibold mb-3 text-primary">Car/SUV Chassis Costs</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="ice-chassis-car">ICE Car/SUV Chassis ($)</Label>
                <Input
                  id="ice-chassis-car"
                  type="number"
                  step="1000"
                  value={parameters.iceChassisCar}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    iceChassisCar: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="ev-chassis-car">EV Car/SUV Chassis ($)</Label>
                <Input
                  id="ev-chassis-car"
                  type="number"
                  step="1000"
                  value={parameters.evChassisCar}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    evChassisCar: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>
            </div>
          </div>

          {/* Pickup Costs */}
          <div className="border-t pt-4 mt-4">
            <h4 className="text-sm font-semibold mb-3 text-primary">Pickup Chassis Costs</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="ice-chassis-pickup">ICE Pickup Chassis ($)</Label>
                <Input
                  id="ice-chassis-pickup"
                  type="number"
                  step="1000"
                  value={parameters.iceChassisPickup}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    iceChassisPickup: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="ev-chassis-pickup">EV Pickup Chassis ($)</Label>
                <Input
                  id="ev-chassis-pickup"
                  type="number"
                  step="1000"
                  value={parameters.evChassisPickup}
                  onChange={(e) => setParameters(prev => ({
                    ...prev,
                    evChassisPickup: parseFloat(e.target.value) || 0
                  }))}
                />
              </div>
            </div>
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