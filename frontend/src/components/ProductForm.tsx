import React, { useState } from "react";

export type ProductInput = {
  name: string;
  sku: string;
  price: number;
  stock: number;
};

export default function ProductForm({
  initial,
  onSubmit,
  onCancel,
}: {
  initial?: ProductInput;
  onSubmit: (data: ProductInput) => void;
  onCancel?: () => void;
}): React.ReactElement {
  const [form, setForm] = useState<ProductInput>(
    initial ?? { name: "", sku: "", price: 0, stock: 0 }
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate(values: ProductInput): Record<string, string> {
    const e: Record<string, string> = {};
    if (!values.name) e.name = "Name is required";
    if (!values.sku) e.sku = "SKU is required";
    if (values.price <= 0) e.price = "Price must be positive";
    if (values.stock < 0) e.stock = "Stock cannot be negative";
    return e;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const v = validate(form);
    setErrors(v);
    if (Object.keys(v).length === 0) onSubmit(form);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Name</label>
        <input
          className="input mt-1"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
      </div>
      
      <div>
        <label className="block text-sm font-medium">SKU</label>
        <input
          className="input mt-1"
          value={form.sku}
          onChange={(e) => setForm({ ...form, sku: e.target.value })}
        />
        {errors.sku && <p className="mt-1 text-sm text-red-600">{errors.sku}</p>}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium">Price</label>
          <input
            type="number"
            step="0.01"
            className="input mt-1"
            value={form.price}
            onChange={(e) => setForm({ ...form, price: Number(e.target.value) })}
          />
          {errors.price && <p className="mt-1 text-sm text-red-600">{errors.price}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium">Stock</label>
          <input
            type="number"
            className="input mt-1"
            value={form.stock}
            onChange={(e) => setForm({ ...form, stock: Number(e.target.value) })}
          />
          {errors.stock && <p className="mt-1 text-sm text-red-600">{errors.stock}</p>}
        </div>
      </div>
      <div className="flex justify-end gap-2">
        {onCancel && (
          <button type="button" onClick={onCancel} className="btn border border-gray-300">
            Cancel
          </button>
        )}
        <button type="submit" className="btn btn-primary">Save</button>
      </div>
    </form>
  );
}


