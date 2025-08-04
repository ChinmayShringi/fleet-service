import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { LoadingScreen } from "@/components/ui/loading-screen";
import { RegisterPage } from "@/pages/RegisterPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { FleetPage } from "@/pages/FleetPage";
import { UploadPage } from "@/pages/UploadPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { UsersPage } from "@/pages/UsersPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { ExcelDataPage } from "@/pages/ExcelDataPage";
import { VehicleFleetDataPage } from "@/pages/VehicleFleetDataPage";
import { ElectricVehicleBudgetPage } from "@/pages/ElectricVehicleBudgetPage";
import { RadioEquipmentCostPage } from "@/pages/RadioEquipmentCostPage";
import NotFound from "./pages/NotFound";
import React, { Suspense } from "react";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Suspense fallback={<LoadingScreen message="Initializing PSEG Fleet Management..." />}>
            <Routes>
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Dashboard..." />}>
                    <DashboardLayout>
                      <DashboardPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Dashboard..." />}>
                    <DashboardLayout>
                      <DashboardPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/fleet" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Fleet Data..." />}>
                    <DashboardLayout>
                      <FleetPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/upload" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Upload Interface..." />}>
                    <DashboardLayout>
                      <UploadPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/reports" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Reports..." />}>
                    <DashboardLayout>
                      <ReportsPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/analytics" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Analytics..." />}>
                    <DashboardLayout>
                      <AnalyticsPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/users" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading User Management..." />}>
                    <DashboardLayout>
                      <UsersPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/settings" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Settings..." />}>
                    <DashboardLayout>
                      <SettingsPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/excel-data/:fileKey" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Excel Data..." />}>
                    <DashboardLayout>
                      <ExcelDataPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/vehicle-fleet-data" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Vehicle Fleet Data..." />}>
                    <DashboardLayout>
                      <VehicleFleetDataPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/electric-vehicle-budget" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading EV Budget Data..." />}>
                    <DashboardLayout>
                      <ElectricVehicleBudgetPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/radio-equipment-cost" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingScreen message="Loading Radio Equipment Data..." />}>
                    <DashboardLayout>
                      <RadioEquipmentCostPage />
                    </DashboardLayout>
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
