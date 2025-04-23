import { Toaster } from "./components/ui/toaster";
import { TooltipProvider } from "./components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import CreateUser from "./pages/CreateUser";
import ApiKeys from "./pages/ApiKeys";
import Transactions from "./pages/Transactions";
import EndpointTester from "./pages/EndpointTester";
import NotFound from "./pages/NotFound";
import { AdminLayout } from "./components/layout/AdminLayout";

const queryClient = new QueryClient();

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Routes configuration
const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Explicitly handle the /admin route to redirect to dashboard */}
      <Route path="/admin" element={<Navigate to="/dashboard" replace />} />

      {/* Protected routes */}
      <Route
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/users" element={<Users />} />
        <Route path="/users/create" element={<CreateUser />} />
        <Route path="/api-keys" element={<ApiKeys />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/settings" element={<div>Settings Page</div>} />
        <Route path="/endpoint-tester" element={<EndpointTester />} />
        {/* Add other admin routes here */}
        <Route path="*" element={<NotFound />} />
      </Route>

      {/* Redirect root to dashboard if logged in, otherwise to login */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter basename="/admin">
      <TooltipProvider>
        <AuthProvider>
          <AppRoutes />
          <Toaster />
        </AuthProvider>
      </TooltipProvider>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;
