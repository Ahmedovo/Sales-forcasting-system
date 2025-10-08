import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/ChartCard";
import api from "../lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

type Point = { label: string; value: number };

export default function Dashboard(): React.ReactElement {
  const [salesSeries, setSalesSeries] = useState<Point[]>([]);
  const [alerts, setAlerts] = useState<{ id: string; name: string; stock: number }[]>([]);
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth());
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Generate array of month names
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  // Generate array of years (current year and 2 years back)
  const currentYear = new Date().getFullYear();
  const years = [currentYear - 2, currentYear - 1, currentYear];

  // Function to fetch sales data for the selected month and year
  const fetchMonthlySales = async () => {
    setIsLoading(true);
    try {
      // Fetch sales data for the selected month and year
      const salesRes = await api.get<{ items: Point[] }>("/sales/series", { 
        params: { 
          year: selectedYear,
          month: selectedMonth + 1 // API expects 1-12 for months
        } 
      });
      
      // Get the data from the response
      const monthData = salesRes.data.items ?? [];
      
      // Format the labels to show only the day
      const formattedData = monthData.map(item => {
        const date = new Date(item.label);
        return {
          ...item,
          label: date.getDate().toString()
        };
      });
      
      setSalesSeries(formattedData);
    } catch (error) {
      console.error("Error fetching monthly sales data:", error);
      setSalesSeries([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch alerts and initial sales data
  useEffect(() => {
    (async () => {
      try {
        const alertsRes = await api.get<{ items: { id: string; name: string; stock: number }[] }>(
          "/products/alerts", 
          { params: { threshold: 10 } }
        );
        setAlerts(alertsRes.data.items ?? []);
      } catch (error) {
        console.error("Error fetching alerts:", error);
      }
    })();
  }, []);

  // Fetch sales data when month or year changes
  useEffect(() => {
    fetchMonthlySales();
  }, [selectedMonth, selectedYear]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-6">
          <div className="card p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-800">Monthly Sales</h3>
              <div className="flex gap-2">
                <select 
                  className="input" 
                  value={selectedMonth} 
                  onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                  disabled={isLoading}
                >
                  {months.map((month, index) => (
                    <option key={month} value={index}>{month}</option>
                  ))}
                </select>
                <select 
                  className="input" 
                  value={selectedYear} 
                  onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                  disabled={isLoading}
                >
                  {years.map((year) => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="h-64">
              {isLoading ? (
                <div className="flex h-full items-center justify-center">
                  <svg className="h-8 w-8 animate-spin text-brand-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
              ) : salesSeries.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={salesSeries} margin={{ top: 10, right: 10, bottom: 0, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis 
                      dataKey="label" 
                      tickLine={false} 
                      axisLine={false}
                      label={{ value: 'Day of Month', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis tickLine={false} axisLine={false} />
                    <Tooltip 
                      formatter={(value) => [`${value} units`, 'Sales']}
                      labelFormatter={(label) => `Day ${label}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#6366f1" 
                      strokeWidth={2} 
                      dot={true}
                      name="Sales"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-gray-500">
                  No sales data available for this period
                </div>
              )}
            </div>
          </div>
          <div className="card p-4">
            <h3 className="mb-2 text-sm font-semibold">Stock Alerts</h3>
            {alerts.length > 0 ? (
              <ul className="list-disc space-y-1 pl-6 text-sm text-red-700">
                {alerts.map(a => (
                  <li key={a.id}>{a.name} is low ({a.stock} left)</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No stock alerts at this time</p>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}


