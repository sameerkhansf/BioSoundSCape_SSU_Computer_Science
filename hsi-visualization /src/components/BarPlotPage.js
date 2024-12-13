import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import '../styles/BarPlotPage.css';

function BarPlotPage({ selectedMarkers }) {
    const [samplesData, setSamplesData] = useState([]);
    const [predictionsData, setPredictionsData] = useState([]);
    const containerRef = useRef(null);

    const sampleNums = useMemo(() => selectedMarkers.map(m => m.sample_num), [selectedMarkers]);

    useEffect(() => {
        const backendUrl = process.env.REACT_APP_BACKEND_URL;

        // Fetch predictions
        fetch(`${backendUrl}/api/predictions`)
            .then(res => res.json())
            .then(preds => setPredictionsData(preds))
            .catch(err => console.error('Error fetching predictions:', err));

        // Fetch samples
        const url = sampleNums.length > 0
            ? `${backendUrl}/api/samples?sample_nums=${sampleNums.join(',')}`
            : `${backendUrl}/api/samples`;

        fetch(url)
            .then(res => res.json())
            .then(docs => setSamplesData(docs))
            .catch(err => console.error('Error fetching samples:', err));
    }, [sampleNums]);

    const frequencyFields = useMemo(() => {
        if (samplesData.length > 0) {
            return Object.keys(samplesData[0]).filter(key => key.startsWith('frq'));
        }
        return [];
    }, [samplesData]);

    const groundTruthMap = useMemo(() => {
        const map = new Map();
        predictionsData.forEach(p => {
            map.set(p.sample_num, p.ground_truth_label || 'Unknown');
        });
        return map;
    }, [predictionsData]);

    useEffect(() => {
        const container = d3.select(containerRef.current);
        container.selectAll('.chart-container').remove();

        if (sampleNums.length === 0 || samplesData.length === 0 || frequencyFields.length === 0) {
            return;
        }

        sampleNums.forEach(sNum => {
            const sample = samplesData.find(d => d.Sample_num === sNum);
            if (!sample) return;

            const freqs = frequencyFields.map(f => sample[f]).filter(v => typeof v === 'number');

            const xDomain = [-0.5, 0.5];
            const binSize = 0.05; 
            const histogram = d3.histogram()
                .domain(xDomain)
                .thresholds(d3.range(-0.5, 0.51, binSize)); 
            const bins = histogram(freqs);

            // Convert bins to data for the bar chart
            const binsData = bins.map(bin => {
                const rangeLabel = `${bin.x0.toFixed(2)} to ${bin.x1.toFixed(2)}`;
                return { class: rangeLabel, value: bin.length };
            });

            const chartContainer = container.append('div')
                .attr('class', 'chart-container')
                .style('margin-bottom', '30px');

            const width = 500;
            const height = 200;
            const margin = { top: 50, right: 30, bottom: 70, left: 90 };

            const svg = chartContainer.append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);

            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);

            const x = d3.scaleBand()
                .domain(binsData.map(d => d.class))
                .range([0, width])
                .padding(0.2);

            const y = d3.scaleLinear()
                .domain([0, d3.max(binsData, d => d.value) || 0])
                .nice()
                .range([height, 0]);

            // X axis
            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x))
                .selectAll('text')
                .attr('text-anchor', 'end')
                .attr('transform', 'rotate(-45) translate(-5,-5)');

            // Y axis
            g.append('g')
                .call(d3.axisLeft(y));

            // Bars
            g.selectAll('rect')
                .data(binsData)
                .enter()
                .append('rect')
                .attr('x', d => x(d.class))
                .attr('y', d => y(d.value))
                .attr('width', x.bandwidth())
                .attr('height', d => height - y(d.value))
                .attr('fill', '#69b3a2');

            // Title
            const groundTruth = groundTruthMap.get(sNum) || 'Unknown';
            g.append('text')
                .attr('x', width / 2)
                .attr('y', -margin.top / 2)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .style('font-weight', 'bold')
                .text(`Sample ${sNum} - Ground Truth: ${groundTruth}`);

            // X label
            g.append('text')
                .attr('x', width / 2)
                .attr('y', height + margin.bottom - 10)
                .attr('text-anchor', 'middle')
                .style('font-size', '12px')
                .text('Frequency Ranges');

            // Y label
            g.append('text')
                .attr('text-anchor', 'middle')
                .attr('transform', `translate(${-margin.left + 20}, ${height / 2}) rotate(-90)`)
                .style('font-size', '12px')
                .text('Count');
        });
    }, [samplesData, predictionsData, frequencyFields, sampleNums, groundTruthMap]);

    return (
        <div className="bar-plot-page" style={{ overflowY: 'scroll', height: '90vh', padding: '20px' }}>
            <div ref={containerRef} />
            {(sampleNums.length === 0 || samplesData.length === 0) && (
                <p style={{ textAlign: 'center', marginTop: '20px' }}>
                    No data available. Please select some markers or ensure data is loaded.
                </p>
            )}
        </div>
    );
}

export default BarPlotPage;
