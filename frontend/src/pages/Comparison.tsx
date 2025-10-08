import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ProductSelector from "../components/ProductSelector";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import api from "../lib/api";

export default function Comparison(): React.ReactElement {
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedProduct) {
      fetchComparisonData();
    }
  }, [selectedProduct]);

  const fetchComparisonData = async () => {
    if (!selectedProduct) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/forecast/comparison`, {
        params: { product_id: selectedProduct }
      });
      
      setComparisonData(response.data.comparison_data || []);
    } catch (err) {
      setError("Error fetching comparison data. Please try again later.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProductChange = (productId: string) => {
    setSelectedProduct(productId);
  };

  // Filter out entries where predicted is null
  const validComparisonData = comparisonData.filter(item => item.predicted !== null);

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold">Sales Forecast Comparison</h1>
          </div>
          
          <div className="card p-4 space-y-4">
            <div className="mb-4">
              <ProductSelector onProductChange={handleProductChange} />
            </div>
            
            {error && (
              <div className="bg-red-50 text-red-700 p-3 rounded-md">
                {error}
              </div>
            )}
            
            {isLoading ? (
              <div className="flex justify-center my-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              </div>
            ) : !selectedProduct ? (
              <div className="bg-blue-50 text-blue-700 p-3 rounded-md">
                Please select a product to view comparison data
              </div>
            ) : comparisonData.length === 0 ? (
              <div className="bg-blue-50 text-blue-700 p-3 rounded-md">
                No comparison data available for this product
              </div>
            ) : validComparisonData.length === 0 ? (
              <div className="bg-blue-50 text-blue-700 p-3 rounded-md">
                No forecast data available for comparison
              </div>
            ) : (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={comparisonData}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="actual"
                      name="Actual Sales"
                      stroke="#8884d8"
                      activeDot={{ r: 8 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      name="Predicted Sales"
                      stroke="#82ca9d"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}