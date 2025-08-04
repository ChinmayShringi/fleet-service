import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const chartData = [
  { month: 'Jan', expenses: 32000, vehicles: 6200 },
  { month: 'Feb', expenses: 38000, vehicles: 6250 },
  { month: 'Mar', expenses: 42000, vehicles: 6300 },
  { month: 'Apr', expenses: 45385, vehicles: 6350 },
  { month: 'May', expenses: 41000, vehicles: 6380 },
  { month: 'Jun', expenses: 39000, vehicles: 6408 },
];

export const FleetOverviewChart: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-semibold text-foreground">
          Fleet Expenses Trend
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="month" 
              axisLine={false}
              tickLine={false}
              className="text-xs text-muted-foreground"
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              className="text-xs text-muted-foreground"
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              formatter={(value, name) => [
                name === 'expenses' ? `$${value.toLocaleString()}` : value,
                name === 'expenses' ? 'Monthly Expenses' : 'Fleet Size'
              ]}
              labelFormatter={(label) => `Month: ${label}`}
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px',
              }}
            />
            <Line 
              type="monotone" 
              dataKey="expenses" 
              stroke="hsl(var(--primary))" 
              strokeWidth={2}
              dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: 'hsl(var(--primary))', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};