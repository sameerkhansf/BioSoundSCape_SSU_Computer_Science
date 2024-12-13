// App.js
import React, { useState, useEffect } from 'react';
import MapContainer from './components/MapContainer';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import './styles/App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ScatterPlotPage from './components/ScatterPlotPage';
import BarPlotPage from './components/BarPlotPage';

function App() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);

  // Two separate sets of selected markers
  const [selectedScatterMarkers, setSelectedScatterMarkers] = useState([]);
  const [selectedBarMarkers, setSelectedBarMarkers] = useState([]);

  useEffect(() => {
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
            // Pass both lists to the sidebar to show which samples are selected for each
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
                  />
                }
              />
              <Route
                path="/scatter"
                element={
                  <ScatterPlotPage
                    selectedMarkers={selectedScatterMarkers} // scatter page uses scatter markers
                    setSelectedMarkers={setSelectedScatterMarkers}
                  />
                }
              />
              <Route
                path="/bar"
                element={
                  <BarPlotPage
                    selectedMarkers={selectedBarMarkers} // bar page uses bar markers
                    setSelectedMarkers={setSelectedBarMarkers}
                  />
                }
              />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
