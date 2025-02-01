import React, { useState, useEffect } from 'react';
import { AmbientLight, PointLight, LightingEffect } from '@deck.gl/core';
import { HexagonLayer } from '@deck.gl/aggregation-layers';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import maplibregl from 'maplibre-gl';

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json';

const ambientLight = new AmbientLight({ color: [255, 255, 255], intensity: 1.0 });
const pointLight1 = new PointLight({ color: [255, 255, 255], intensity: 0.8, position: [-0.144528, 49.739968, 80000] });
const pointLight2 = new PointLight({ color: [255, 255, 255], intensity: 0.8, position: [-3.807751, 54.104682, 8000] });
const lightingEffect = new LightingEffect({ ambientLight, pointLight1, pointLight2 });

const INITIAL_VIEW_STATE = {
    longitude: 18.4241,
    latitude: -33.9249,
    zoom: 12,
    minZoom: 5,
    maxZoom: 15,
    pitch: 50,
    bearing: -27,
};

const colorRange = [
    [1, 152, 189],
    [73, 227, 206],
    [216, 254, 181],
    [254, 237, 177],
    [254, 173, 84],
    [209, 55, 78],
];

function getTooltip({ object }) {
    if (!object) return null;
    const lat = object.position[1];
    const lng = object.position[0];
    const count = object.points.length;
    return `latitude: ${lat.toFixed(6)}\nlongitude: ${lng.toFixed(6)}\n${count} points\nElevation: ${object.elevationValue.toFixed(2)}`;
}

function calculateCentroid(coordinates) {
    let centroidLat = 0;
    let centroidLng = 0;
    coordinates.forEach(([lng, lat]) => {
        centroidLat += lat;
        centroidLng += lng;
    });
    const numPoints = coordinates.length;
    return { lat: centroidLat / numPoints, lng: centroidLng / numPoints };
}

export default function HexCartoPage() {
    const [hexData, setHexData] = useState([]);
    const [coverage, setCoverage] = useState(0.9);
    const [radius, setRadius] = useState(500);
    const [upperPercentile, setUpperPercentile] = useState(100);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const backendUrl = process.env.REACT_APP_BACKEND_URL;
                console.log('[HexCartoPage] Fetching polygons from:', backendUrl);

                const polygonsRes = await fetch(`${backendUrl}/api/polygons`);
                if (!polygonsRes.ok) throw new Error('Failed to fetch polygons');
                let polygons = await polygonsRes.json();
                console.log('[HexCartoPage] Fetched polygons count:', polygons.length);

                polygons = polygons.slice(0, 5000);

                const validPolygons = polygons.filter(
                    (polygon) => polygon.ground_truth_label && polygon.predicted_label_name
                );
                console.log('[HexCartoPage] Valid polygons count:', validPolygons.length);

                const sampleNums = [...new Set(validPolygons.map(p => p.sample_num))];
                console.log('[HexCartoPage] Unique sample_nums count:', sampleNums.length);

                // Get tah frequency summaries
                const freqUrl = `${backendUrl}/api/frequency_summary?sample_nums=${sampleNums.join(',')}`;
                const freqRes = await fetch(freqUrl);
                if (!freqRes.ok) throw new Error('Failed to fetch frequency summary');
                const freqSummaries = await freqRes.json();

                const freqMap = freqSummaries.reduce((acc, fs) => {
                    acc[fs.Sample_num] = fs.frequency_sum;
                    return acc;
                }, {});

                const hexPoints = validPolygons.map((polygon) => {
                    const centroid = calculateCentroid(polygon.coordinates);
                    const polySampleNum = polygon.sample_num;
                    const frequencyValue = freqMap[polySampleNum] || 0;
                    return {
                        position: [centroid.lng, centroid.lat],
                        frequency: frequencyValue
                    };
                });

                console.log('[HexCartoPage] hexData length:', hexPoints.length);
                setHexData(hexPoints);
            } catch (error) {
                console.error('[HexCartoPage] Error fetching data:', error);
            }
        };

        fetchData();
    }, []);

    const elevationScale = hexData.length ? 10 : 1;

    const layer = new HexagonLayer({
        id: 'hexagon-layer',
        data: hexData,
        colorRange,
        coverage: coverage,
        elevationRange: [0, 3000],
        elevationScale: elevationScale,
        extruded: true,
        getPosition: d => d.position,
        pickable: true,
        radius: radius,
        upperPercentile: upperPercentile,
        material: {
            ambient: 0.64,
            diffuse: 0.6,
            shininess: 32,
            specularColor: [51, 51, 51],
        },
        getColorValue: (points) => points.reduce((acc, p) => acc + p.frequency, 0),
        getElevationValue: (points) => points.reduce((acc, p) => acc + p.frequency, 0),
    });

    return (
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
            <DeckGL
                layers={[layer]}
                effects={[lightingEffect]}
                initialViewState={INITIAL_VIEW_STATE}
                controller={true}
                getTooltip={getTooltip}
                style={{ position: 'relative', width: '100%', height: '100%' }}
            >
                <Map reuseMaps mapLib={maplibregl} mapStyle={MAP_STYLE} />
            </DeckGL>

            {/* Control Panel */}
            <div style={{
                position: 'absolute',
                top: 10,
                left: 10,
                background: 'rgba(255,255,255,0.9)',
                padding: '10px',
                borderRadius: '4px',
                fontFamily: 'Arial, sans-serif',
                fontSize: '12px'
            }}>
                <h4 style={{ margin: '0 0 10px 0' }}>Hex Layer Controls</h4>
                <label>
                    Coverage: {coverage.toFixed(2)}
                    <input
                        type="range"
                        min="0.1"
                        max="1"
                        step="0.05"
                        value={coverage}
                        onChange={(e) => setCoverage(Number(e.target.value))}
                    />
                </label><br />
                <label>
                    Radius: {radius}m
                    <input
                        type="range"
                        min="100"
                        max="2000"
                        step="100"
                        value={radius}
                        onChange={(e) => setRadius(Number(e.target.value))}
                    />
                </label><br />
                <label>
                    Upper Percentile: {upperPercentile}%
                    <input
                        type="range"
                        min="1"
                        max="100"
                        step="1"
                        value={upperPercentile}
                        onChange={(e) => setUpperPercentile(Number(e.target.value))}
                    />
                </label>
            </div>

            {/* Color Legend */}
            <div style={{
                position: 'absolute',
                top: 10,
                right: 10,
                background: 'rgba(255,255,255,0.9)',
                padding: '10px',
                borderRadius: '4px',
                fontFamily: 'Arial, sans-serif',
                fontSize: '12px'
            }}>
                <h4 style={{ margin: '0 0 10px 0' }}>Frequency Legend</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {colorRange.map((color, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
                            <div style={{
                                width: '20px',
                                height: '10px',
                                background: `rgb(${color.join(',')})`,
                                marginRight: '5px'
                            }}></div>
                            <span>Level {i + 1}</span>
                        </div>
                    ))}
                </div>
                <small>(Darker to Lighter indicates increasing frequency)</small>
            </div>
        </div>
    );
}
