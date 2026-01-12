import React, { useEffect, useState } from "react";

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/products/")
      .then((res) => {
        if (!res.ok) throw new Error("Error en la respuesta del servidor");
        return res.json();
      })
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error cargando productos:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Cargando precios de supermercados...</div>;

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>🛒 ChaniWeb - Comparador de Precios (Sprint 2)</h1>
      <table
        border="1"
        cellPadding="10"
        style={{ borderCollapse: "collapse", width: "100%" }}
      >
        <thead>
          <tr style={{ background: "#f0f0f0" }}>
            <th>Producto</th>
            <th>Supermercado</th>
            <th>Precio</th>
            <th>Normalizado (Comparación)</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{p.supermarket}</td>
              <td style={{ fontWeight: "bold" }}>${p.price.toFixed(2)}</td>
              <td>
                {p.quantity} {p.unit} a ${p.price_per_unit.toFixed(2)}/{p.unit}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
