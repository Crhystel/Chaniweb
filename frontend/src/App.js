import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [view, setView] = useState("landing"); // 'landing', 'search', 'detail'
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetch("/api/products/")
      .then((res) => res.json())
      .then((data) => setProducts(data))
      .catch((err) => console.error(err));
  }, []);

  // Agrupar productos por nombre normalizado (aproximación simple) para la vista de detalle
  const getComparisons = (product) => {
    return products.filter(
      (p) =>
        p.name.includes(product.name.split(" ")[0]) && p.name.includes("180")
    );
    // Nota: En un sistema real la lógica de agrupación es más compleja en el backend
  };

  const handleSearch = () => {
    setView("search");
  };

  // --- VISTAS ---

  const LandingPage = () => (
    <div className="landing-container">
      <nav className="navbar">
        <span className="logo">ChaniWeb</span>
      </nav>
      <div className="hero">
        <h1 className="hero-title">ChaniWeb</h1>
        <p className="hero-subtitle">Todo lo que necesitas, al mejor precio</p>
        <button className="btn-orange" onClick={handleSearch}>
          Aprender más
        </button>
      </div>
      <div className="landing-info-section">
        <div className="info-text">
          <p>
            ChaniWeb es una plataforma ecuatoriana que te permite comparar
            precios de supermercados en tiempo real.
          </p>
          <p>
            Encuentra el mejor precio en tu ciudad, ahorra en tus compras
            diarias.
          </p>
          <button className="btn-red" onClick={handleSearch}>
            Comienza a ahorrar
          </button>
        </div>
        <div className="info-image">
          {/* Imagen de stock similar a la captura */}
          <img
            src="https://images.pexels.com/photos/3769747/pexels-photo-3769747.jpeg?auto=compress&cs=tinysrgb&w=600"
            alt="Laptop"
          />
        </div>
      </div>
    </div>
  );

  const SearchPage = () => {
    // Filtrar solo productos únicos por nombre para mostrar en la lista principal
    // (Simulación visual para que no salgan repetidos en la lista, sino al entrar al detalle)
    const uniqueProducts = [];
    const names = new Set();
    products.forEach((p) => {
      const shortName = p.name.split(" ").slice(0, 3).join(" "); // Agrupa por nombre corto
      if (
        !names.has(shortName) &&
        p.name.toLowerCase().includes(searchTerm.toLowerCase())
      ) {
        names.add(shortName);
        uniqueProducts.push(p);
      }
    });

    return (
      <div className="main-layout">
        <header className="top-header">
          <div className="back-icon" onClick={() => setView("landing")}>
            ↩
          </div>
          <h2 className="logo-orange">ChaniWeb</h2>
        </header>

        <div className="content">
          <h3>Encuentra el mejor precio antes de salir de casa.</h3>
          <p className="subtitle">
            Compara productos en Mi Comisariato, Tía, Akí y más.
          </p>

          <div className="search-controls">
            <input
              type="text"
              className="search-input"
              placeholder="🔍 Buscar por nombre del producto"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button className="btn-outline">Más Filtros</button>
            <button className="btn-orange-pill">Buscar</button>
          </div>

          <div className="product-list">
            {uniqueProducts.map((p) => (
              <div
                className="product-card"
                key={p.id}
                onClick={() => {
                  setSelectedProduct(p);
                  setView("detail");
                }}
              >
                <div className="card-img-container">
                  <img src={p.image_url} alt={p.name} />
                </div>
                <div className="card-info">
                  <h4>{p.name}</h4>
                  <p className="card-desc">
                    Producto de alta calidad, ideal para el hogar.
                  </p>
                </div>
                <div className="card-price-block">
                  <div className="price-row">
                    <span>Mejor precio</span>
                    <span className="price-badge-green">
                      ${p.price.toFixed(2)}
                    </span>
                  </div>
                  <div className="price-row-sm">
                    <span>Precio Promedio</span>
                    <span>${(p.price * 1.2).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const DetailPage = () => {
    if (!selectedProduct) return null;

    // Simular comparación buscando productos similares en la base cargada
    const comparisons = products.filter(
      (p) => p.name.includes(selectedProduct.name.split(" ")[0]) // Coincidencia básica
    );

    return (
      <div className="main-layout">
        <header className="top-header">
          <div className="back-icon" onClick={() => setView("search")}>
            ↩
          </div>
        </header>

        <div className="detail-container">
          <div className="detail-top">
            <div className="detail-img">
              <img src={selectedProduct.image_url} alt={selectedProduct.name} />
            </div>
            <div className="detail-info">
              <h2>{selectedProduct.name}</h2>
              <ul className="detail-bullets">
                <li>Producto disponible en varios supermercados</li>
                <li>Comparación en tiempo real</li>
                <li>Ahorra comprando inteligentemente</li>
              </ul>

              <div className="best-price-box">
                <div className="best-price-label">
                  <span>Mejor precio:</span>
                  <small>{selectedProduct.supermarket}</small>
                </div>
                <div className="price-badge-lg">
                  ${selectedProduct.price.toFixed(2)}
                </div>
              </div>
              <button className="btn-orange-wide">Más información</button>
            </div>
          </div>

          <h3 className="comparison-title">Comparación de precios</h3>

          <table className="comparison-table">
            <thead>
              <tr>
                <th>Supermercado</th>
                <th>Precio Oferta</th>
                <th>Precio Normal</th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((comp, idx) => (
                <tr key={idx}>
                  <td>{comp.supermarket}</td>
                  <td>{comp.price.toFixed(2)}</td>
                  <td>{(comp.price * 1.15).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      {view === "landing" && <LandingPage />}
      {view === "search" && <SearchPage />}
      {view === "detail" && <DetailPage />}
    </div>
  );
}

export default App;
