// Sidebar.js
import React from 'react';
import '../styles/Sidebar.css';
import { useLocation, useNavigate } from 'react-router-dom';

const categoryColors = {
    "Built-up": "rgba(255, 0, 0, 0.7)",
    "Consolidated Barren": "rgba(77, 77, 77, 0.7)",
    "Shrubs and Natural Grassland": "rgba(0, 255, 0, 0.7)",
    "Natural Wooded Land": "rgba(0, 100, 0, 0.7)",
    "Permanent Crops": "rgba(173, 216, 230, 0.7)",
    "Planted Forest": "rgba(128, 0, 128, 0.7)",
    "Annual Crops": "rgba(230, 230, 250, 0.7)",
    "Unconsolidated Barren": "rgba(165, 42, 42, 0.7)",
    "Waterbodies": "rgba(0, 0, 255, 0.7)",
};

export function Sidebar({
    categories,
    selectedCategory,
    onCategorySelect,
    selectedScatterMarkers,
    selectedBarMarkers,
}) {
    const navigate = useNavigate();
    const location = useLocation();

    const isOnMap = location.pathname === '/';

    const hasScatterMarkers = selectedScatterMarkers && selectedScatterMarkers.length > 0;
    const hasBarMarkers = selectedBarMarkers && selectedBarMarkers.length > 0;

    const onScatterPlotClick = () => {
        if (hasScatterMarkers) {
            navigate('/scatter');
        }
    };

    const onBarPlotClick = () => {
        navigate('/bar');
    };

    return (
        <div className="sidebar">
            <ul>
                <li
                    className={!selectedCategory ? 'active' : ''}
                    onClick={() => onCategorySelect(null)}
                    style={{ backgroundColor: 'rgba(255, 255, 255, 0.7)', color: '#000' }}
                >
                    Show All
                </li>
                {categories.map((cat, index) => (
                    <li
                        key={index}
                        className={selectedCategory === cat ? 'active' : ''}
                        onClick={() => onCategorySelect(cat)}
                        style={{
                            backgroundColor: categoryColors[cat],
                            color: '#000',
                        }}
                    >
                        {cat}
                    </li>
                ))}
            </ul>

            <h3>Visualization Options</h3>
            <ul>
                <li
                    className={location.pathname === '/scatter' ? 'active' : ''}
                    style={{
                        backgroundColor: hasScatterMarkers
                            ? 'rgba(200,200,200,0.7)'
                            : 'rgba(200,200,200,0.3)',
                        color: '#000',
                        cursor: hasScatterMarkers ? 'pointer' : 'not-allowed',
                        opacity: hasScatterMarkers ? 1 : 0.5,
                    }}
                    onClick={onScatterPlotClick}
                >
                    Show Scatter plots
                </li>
                <li
                    className={location.pathname === '/bar' ? 'active' : ''}
                    style={{
                        backgroundColor: 'rgba(200,200,200,0.7)',
                        color: '#000',
                        cursor: 'pointer',
                    }}
                    onClick={onBarPlotClick}
                >
                    Show Bar plots
                </li>
            </ul>

            {hasScatterMarkers && (
                <div style={{ marginTop: '10px', fontSize: '14px' }}>
                    <strong>Scatter Plot Samples:</strong>
                    <ul style={{ paddingLeft: '20px' }}>
                        {selectedScatterMarkers.map((m) => (
                            <li key={m.sample_num}>Sample {m.sample_num}</li>
                        ))}
                    </ul>
                </div>
            )}

            {hasBarMarkers && (
                <div style={{ marginTop: '10px', fontSize: '14px' }}>
                    <strong>Bar Plot Samples:</strong>
                    <ul style={{ paddingLeft: '20px' }}>
                        {selectedBarMarkers.map((m) => (
                            <li key={m.sample_num}>Sample {m.sample_num}</li>
                        ))}
                    </ul>
                </div>
            )}

            {isOnMap && (hasScatterMarkers || hasBarMarkers) && (
                <button
                    onClick={() => window.location.reload()}
                    style={{ marginTop: '10px' }}
                >
                    X (Clear Selections)
                </button>
            )}

            <div style={{ position: 'absolute', bottom: '20px', left: '20px' }}>
                <button
                    onClick={() => (window.location.href = '/')}
                    style={{ fontSize: '20px' }}
                >
                    🏠
                </button>
            </div>
        </div>
    );
}
