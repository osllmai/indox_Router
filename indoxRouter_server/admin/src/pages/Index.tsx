
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Index = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to admin dashboard if authenticated
    const token = localStorage.getItem('admin_token');
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-lg text-center">
        <h1 className="text-3xl font-bold mb-6 text-admin-primary">Indox Router Admin</h1>
        <p className="text-gray-600 mb-8">
          Welcome to the Indox Router Admin Panel. Log in to manage users, 
          view statistics, and configure your system.
        </p>
        <Button 
          onClick={() => navigate('/login')} 
          className="w-full bg-admin-primary hover:bg-slate-800 text-white"
        >
          Go to Login
        </Button>
      </div>
    </div>
  );
};

export default Index;
