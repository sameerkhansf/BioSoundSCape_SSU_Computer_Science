/**
 * App.js
 * 
 * Sets up routing, global states, and top-level components.
 * Manages global states such as selected categories and marker selections.
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import { Sidebar } from './components/layout/Sidebar';
import { TopBar } from './components/layout/TopBar';

import MapContainer from './components/maps/MapContainer';
import ScatterPlotPage from './components/plots/ScatterPlotPage';
import BarPlotPage from './components/plots/BarPlotPage';
import HexCartoPage from './components/plots/HexCartoPage';

import './styles/App.css';

function App() {
  // Global states: categories for filtering, selected markers for plots, and hex layer toggle
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedScatterMarkers, setSelectedScatterMarkers] = useState([]);
  const [selectedBarMarkers, setSelectedBarMarkers] = useState([]);
  const [showHexLayer, setShowHexLayer] = useState(false);

  useEffect(() => {
    // Predefined categories. In future, could be fetched from the server but im lazy i guess
    const categoryList = [
      "Built-up",
      "Consolidated Barren",
      "Shrubs and Natural Grassland",
      "Natural Wooded Land",
      "Permanent Crops",
      "Planted Forest",
      "Annual Crops",
      "Unconsolidated Barren",
      "Waterbodies"
    ];
    setCategories(categoryList);
  }, []);

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
  };

  return (
    <Router>
      <div className="App">
        <TopBar title="Land Classification Visualization" />
        <div className="layout">
          <Sidebar
            categories={categories}
            selectedCategory={selectedCategory}
            onCategorySelect={handleCategorySelect}
            selectedScatterMarkers={selectedScatterMarkers}
            selectedBarMarkers={selectedBarMarkers}
          />
          <div className="map-container">
            <Routes>
              <Route
                path="/"
                element={
                  <MapContainer
                    selectedCategory={selectedCategory}
                    selectedScatterMarkers={selectedScatterMarkers}
                    setSelectedScatterMarkers={setSelectedScatterMarkers}
                    selectedBarMarkers={selectedBarMarkers}
                    setSelectedBarMarkers={setSelectedBarMarkers}
                    showHexLayer={showHexLayer}
                    setShowHexLayer={setShowHexLayer}
                  />
                }
              />
              <Route
                path="/scatter"
                element={
                  <ScatterPlotPage
                    selectedMarkers={selectedScatterMarkers}
                    setSelectedMarkers={setSelectedScatterMarkers}
                  />
                }
              />
              <Route
                path="/bar"
                element={
                  <BarPlotPage
                    selectedMarkers={selectedBarMarkers}
                    setSelectedMarkers={setSelectedBarMarkers}
                  />
                }
              />
              <Route
                path="/hex-carto"
                element={<HexCartoPage />}
              />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
