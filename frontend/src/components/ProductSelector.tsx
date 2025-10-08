import React, { useEffect, useState } from "react";
import { FormControl, InputLabel, Select, MenuItem, SelectChangeEvent } from "@mui/material";
import api from "../lib/api";

interface ProductSelectorProps {
  onProductChange: (productId: string) => void;
}

interface Product {
  id: string;
  name: string;
}

const ProductSelector: React.FC<ProductSelectorProps> = ({ onProductChange }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get("/products");
        const productList = response.data.items || [];
        setProducts(productList);
        
        if (productList.length > 0) {
          setSelectedProduct(productList[0].id);
          onProductChange(productList[0].id);
        }
      } catch (error) {
        console.error("Error fetching products:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [onProductChange]);

  const handleChange = (event: SelectChangeEvent) => {
    const productId = event.target.value;
    setSelectedProduct(productId);
    onProductChange(productId);
  };

  if (loading) {
    return <div>Loading products...</div>;
  }

  return (
    <FormControl fullWidth>
      <InputLabel id="product-select-label">Product</InputLabel>
      <Select
        labelId="product-select-label"
        id="product-select"
        value={selectedProduct}
        label="Product"
        onChange={handleChange}
      >
        {products.map((product) => (
          <MenuItem key={product.id} value={product.id}>
            {product.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default ProductSelector;