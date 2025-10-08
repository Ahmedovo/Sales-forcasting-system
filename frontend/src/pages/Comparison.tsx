import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { Box, Container, Typography, CircularProgress, Alert } from "@mui/material";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import ProductSelector from "../components/ProductSelector";
import ChartCard from "../components/ChartCard";

const Comparison: React.FC = () => {
  const { token } = useAuth();
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
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/forecast/comparison?product_id=${selectedProduct}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error("Failed to fetch comparison data");
      }
      
      const data = await response.json();
      setComparisonData(data.comparison_data);
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
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Sales Forecast Comparison
      </Typography>
      
      <Box mb={3}>
        <ProductSelector onProductChange={handleProductChange} />
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {isLoading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : !selectedProduct ? (
        <Alert severity="info">Please select a product to view comparison data</Alert>
      ) : comparisonData.length === 0 ? (
        <Alert severity="info">No comparison data available for this product</Alert>
      ) : validComparisonData.length === 0 ? (
        <Alert severity="info">No forecast data available for comparison</Alert>
      ) : (
        <ChartCard title="Actual vs Predicted Sales">
          <ResponsiveContainer width="100%" height={400}>
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
                stroke="#8884d8"
                name="Actual Sales"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 8 }}
              />
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="#82ca9d"
                name="Predicted Sales"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      )}
    </Container>
  );
};

export default Comparison;