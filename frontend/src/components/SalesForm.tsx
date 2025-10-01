import React, { useState } from "react";

export type SaleInput = {
  productId: string;
  quantity: number;
  date: string; // ISO
};

export type ProductOption = { id: string; name: string };

export default function SalesForm({
  products,
  initial,
  onSubmit,
  onCancel,
}: {
  products: ProductOption[];
  initial?: SaleInput;
  onSubmit: (data: SaleInput) => void;
  onCancel?: () => void;
}): React.ReactElement {
  const [form, setForm] = useState<SaleInput>(
    initial ?? { productId: products[0]?.id ?? "", quantity: 1, date: new Date().toISOString().slice(0, 10) }
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate(values: SaleInput): Record<string, string> {
    const e: Record<string, string> = {};
    if (!values.productId) e.productId = "Product is required";
    if (values.quantity <= 0) e.quantity = "Quantity must be positive";
    if (!values.date) e.date = "Date is required";
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
        <label className="block text-sm font-medium">Product</label>
        <select
          className="input mt-1"
          value={form.productId}
          onChange={(e) => setForm({ ...form, productId: e.target.value })}
        >
          <option value="" disabled>
            Select a product
          </option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        {errors.productId && <p className="mt-1 text-sm text-red-600">{errors.productId}</p>}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium">Quantity</label>
          <input
            type="number"
            className="input mt-1"
            value={form.quantity}
            onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })}
          />
          {errors.quantity && <p className="mt-1 text-sm text-red-600">{errors.quantity}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium">Date</label>
          <input
            type="date"
            className="input mt-1"
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
          />
          {errors.date && <p className="mt-1 text-sm text-red-600">{errors.date}</p>}
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


