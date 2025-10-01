import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar(): React.ReactElement {
  const { user, logout } = useAuth();
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2 text-lg font-semibold">
          <span className="h-6 w-6 rounded bg-brand-600"></span>
          Mini Grocery
        </Link>
        <div className="flex items-center gap-3">
          {user && <span className="hidden text-sm text-gray-600 sm:block">{user.username}</span>}
          <button onClick={logout} className="btn btn-primary">Logout</button>
        </div>
      </div>
    </header>
  );
}


