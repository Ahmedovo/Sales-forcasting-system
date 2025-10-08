import React, { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/ChartCard";
import api from "../lib/api";

export default function Forecast(): React.ReactElement {
  const [productId, setProductId] = useState<string>("");
  const [forecast, setForecast] = useState<{ label: string; value: number }[]>([]);
  const [products, setProducts] = useState<{ id: string; name: string }[]>([]);
  const [isTraining, setIsTraining] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedProduct, setSelectedProduct] = useState<string>("");

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get<{ items: { id: string; name: string }[] }>("/products");
        const list = res.data.items ?? [];
        setProducts(list);
        if (list.length) {
          setProductId(list[0]!.id);
          setSelectedProduct(list[0]!.name);
        }
      } catch {}
    })();
  }, []);

  useEffect(() => {
    if (!productId) return;
    
    const fetchForecast = async () => {
      setIsLoading(true);
      try {
        const res = await api.get<{ 
          forecast: { date: string; prediction: number; lower_bound?: number; upper_bound?: number }[]; 
          training_in_progress: boolean 
        }>("/forecast", { 
          params: { product_id: productId, horizon_days: 7 } 
        });
        
        setIsTraining(res.data.training_in_progress || false);
        
        // Format dates for display
        const forecastData = (res.data.forecast || []).map(item => ({
          label: new Date(item.date).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
          }),
          value: item.prediction,
          // Store additional data if available
          lowerBound: item.lower_bound,
          upperBound: item.upper_bound
        }));
        
        setForecast(forecastData);
        
        // Find the selected product name
        const product = products.find(p => p.id === productId);
        if (product) {
          setSelectedProduct(product.name);
        }
      } catch (error) {
        console.error("Error fetching forecast:", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchForecast();
  }, [productId, products]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="space-y-6">
          <div className="card p-4">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold">7-day Sales Forecast</h3>
                {selectedProduct && (
                  <p className="text-xs text-gray-600">Showing forecast for: {selectedProduct}</p>
                )}
              </div>
              <select 
                className="input" 
                value={productId} 
                onChange={(e) => setProductId(e.target.value)}
                disabled={isLoading}
              >
                {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            
            {isTraining && (
              <div className="mb-4 rounded-md bg-yellow-50 p-3 text-sm">
                <div className="flex items-center">
                  <svg className="mr-2 h-5 w-5 animate-spin text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="font-medium text-yellow-700">
                    Model training in progress. Forecast may be less accurate until training completes.
                  </span>
                </div>
              </div>
            )}
            
            {isLoading ? (
              <div className="flex h-64 items-center justify-center">
                <svg className="h-8 w-8 animate-spin text-brand-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            ) : (
              <ChartCard title="" data={forecast} />
            )}
            
            {!isLoading && forecast.length === 0 && (
              <div className="py-8 text-center text-gray-500">
                No forecast data available. Please ensure the model has been trained.
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}


