import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, DollarSign, Truck, Zap, Calendar } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const costAnalysisData = [
  { category: 'Fuel', amount: 12500, percentage: 35 },
  { category: 'Maintenance', amount: 8900, percentage: 25 },
  { category: 'Insurance', amount: 5600, percentage: 16 },
  { category: 'Depreciation', amount: 4800, percentage: 13 },
  { category: 'Other', amount: 3900, percentage: 11 },
];

const vehicleTypeData = [
  { type: 'Sedans', count: 2840, percentage: 44.3 },
  { type: 'SUVs', count: 1920, percentage: 30.0 },
  { type: 'Trucks', count: 960, percentage: 15.0 },
  { type: 'Vans', count: 480, percentage: 7.5 },
  { type: 'Electric', count: 208, percentage: 3.2 },
];

const evTransitionData = [
  { year: '2024', gas: 6200, electric: 208, target: 300 },
  { year: '2025', gas: 5800, electric: 608, target: 700 },
  { year: '2026', gas: 5200, electric: 1208, target: 1200 },
  { year: '2027', gas: 4400, electric: 2008, target: 2000 },
  { year: '2028', gas: 3200, electric: 3208, target: 3200 },
];

const COLORS = ['#f97316', '#ea580c', '#c2410c', '#9a3412', '#7c2d12'];

export const AnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Fleet Analytics</h1>
        <Badge variant="outline" className="text-success border-success">
          <TrendingUp className="w-3 h-3 mr-1" />
          Performance Up 12%
        </Badge>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Fleet Value</p>
                <p className="text-2xl font-bold">$127.3M</p>
                <div className="flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 text-success mr-1" />
                  <span className="text-xs text-success">+8.2%</span>
                </div>
              </div>
              <DollarSign className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Vehicle Age</p>
                <p className="text-2xl font-bold">4.2 yrs</p>
                <div className="flex items-center mt-1">
                  <TrendingDown className="w-3 h-3 text-success mr-1" />
                  <span className="text-xs text-success">-0.3 yrs</span>
                </div>
              </div>
              <Calendar className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Electric Vehicles</p>
                <p className="text-2xl font-bold">208</p>
                <div className="flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 text-success mr-1" />
                  <span className="text-xs text-success">+45%</span>
                </div>
              </div>
              <Zap className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Fleet Efficiency</p>
                <p className="text-2xl font-bold">94.2%</p>
                <div className="flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 text-success mr-1" />
                  <span className="text-xs text-success">+2.1%</span>
                </div>
              </div>
              <Truck className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Cost Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={costAnalysisData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name} ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="amount"
                  >
                    {costAnalysisData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Amount']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Vehicle Type Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Fleet Composition</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={vehicleTypeData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis 
                    dataKey="type" 
                    axisLine={false}
                    tickLine={false}
                    className="text-xs"
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    className="text-xs"
                  />
                  <Tooltip 
                    formatter={(value, name) => [value, 'Vehicle Count']}
                    labelFormatter={(label) => `Type: ${label}`}
                  />
                  <Bar 
                    dataKey="count" 
                    fill="hsl(var(--primary))"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* EV Transition Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Electric Vehicle Transition Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={evTransitionData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis 
                  dataKey="year" 
                  axisLine={false}
                  tickLine={false}
                  className="text-xs"
                />
                <YAxis 
                  axisLine={false}
                  tickLine={false}
                  className="text-xs"
                />
                <Tooltip 
                  formatter={(value, name) => [
                    value,
                    name === 'gas' ? 'Gas Vehicles' : name === 'electric' ? 'Electric Vehicles' : 'Target'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="gas" 
                  stroke="#94a3b8" 
                  strokeWidth={2}
                  name="gas"
                />
                <Line 
                  type="monotone" 
                  dataKey="electric" 
                  stroke="hsl(var(--primary))" 
                  strokeWidth={2}
                  name="electric"
                />
                <Line 
                  type="monotone" 
                  dataKey="target" 
                  stroke="#22c55e" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="target"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};