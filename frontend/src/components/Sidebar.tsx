import React from "react";
import { NavLink } from "react-router-dom";

const linkClasses = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium hover:bg-gray-100 ${
    isActive ? "bg-gray-100 text-gray-900" : "text-gray-600"
  }`;

export default function Sidebar(): React.ReactElement {
  return (
    <aside className="hidden w-64 border-r bg-white p-4 md:block">
      <nav className="space-y-1">
        <NavLink to="/" className={linkClasses} end>
          <span className="h-2 w-2 rounded-full bg-brand-600" /> Dashboard
        </NavLink>
        <NavLink to="/products" className={linkClasses}>
          <span className="h-2 w-2 rounded-full bg-brand-600" /> Products
        </NavLink>
        <NavLink to="/sales" className={linkClasses}>
          <span className="h-2 w-2 rounded-full bg-brand-600" /> Sales
        </NavLink>
        <NavLink to="/forecast" className={linkClasses}>
          <span className="h-2 w-2 rounded-full bg-brand-600" /> Forecast
        </NavLink>
      </nav>
    </aside>
  );
}


