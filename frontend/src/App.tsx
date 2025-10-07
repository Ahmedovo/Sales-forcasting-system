import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import Sales from "./pages/Sales";
import Forecast from "./pages/Forecast";
import Admin from "./pages/Admin";

function PrivateRoute({ children }: { children: React.ReactElement }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export default function App(): React.ReactElement {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={<PrivateRoute><Dashboard /></PrivateRoute>}
        />
        <Route
          path="/products"
          element={<PrivateRoute><Products /></PrivateRoute>}
        />
        <Route
          path="/sales"
          element={<PrivateRoute><Sales /></PrivateRoute>}
        />
        <Route
          path="/forecast"
          element={<PrivateRoute><Forecast /></PrivateRoute>}
        />
        <Route
          path="/admin"
          element={<PrivateRoute><Admin /></PrivateRoute>}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}


