import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { scatterPlot } from './scatterPlot';
import { menu } from './menu';
import '../styles/ScatterPlotPage.css';

function ScatterPlotPage({ selectedMarkers }) {
    const [data, setData] = useState([]);
    const [selectedSampleOption, setSelectedSampleOption] = useState('All');
    const [selectedFrequencies, setSelectedFrequencies] = useState([]);

    const svgRef = useRef();
    const menuContainerRef = useRef();

    // Extract sample_nums from selectedMarkers
    const sampleNums = useMemo(() => selectedMarkers.map(m => m.sample_num), [selectedMarkers]);

    useEffect(() => {
        if (sampleNums.length > 0) {
            const backendUrl = process.env.REACT_APP_BACKEND_URL;
            fetch(`${backendUrl}/api/samples?sample_nums=${sampleNums.join(',')}`)
                .then(res => res.json())
                .then(docs => {
                    setData(docs);
                })
                .catch(err => console.error('Error fetching samples:', err));
        } else {
            setData([]);
        }
    }, [sampleNums]);

    // Compute frequency fields once data is available
    const frequencyFields = useMemo(() => {
        if (data.length > 0) {
            return Object.keys(data[0]).filter(k => k.startsWith('frq'));
        }
        return [];
    }, [data]);

    useEffect(() => {
        if (data.length === 0 || frequencyFields.length === 0) return;

        const container = d3.select(menuContainerRef.current);
        container.selectAll('*').remove(); // Clear old menus

        const sampleOptions = [{ value: 'All', text: 'All' }]
            .concat(sampleNums.map(s => ({ value: s.toString(), text: `Sample ${s}` })));

        container.append('div')
            .attr('class', 'menu-block')
            .call(
                menu()
                    .id('sample-menu')
                    .labelText('Sample:')
                    .options(sampleOptions)
                    .on('change', (val) => {
                        if (val !== selectedSampleOption) {
                            setSelectedSampleOption(val);
                        }
                    })
            )
            .select('select')
            .property('value', selectedSampleOption);

        // Create a scrollable checkbox list for frequencies
        const freqContainer = container.append('div')
            .attr('class', 'menu-block frequency-container')
            .style('max-height', '200px')
            .style('overflow-y', 'scroll')
            .style('border', '1px solid #ccc')
            .style('padding', '5px');

        freqContainer.append('label')
            .text('Select Frequencies (up to 10):');

        const freqCheckboxes = freqContainer.selectAll('div.freq-option')
            .data(frequencyFields)
            .join('div')
            .attr('class', 'freq-option')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('margin', '2px 0');

        freqCheckboxes.append('input')
            .attr('type', 'checkbox')
            .attr('value', d => d)
            .on('change', (event, d) => {
                const checked = event.target.checked;
                if (checked) {
                    if (selectedFrequencies.length < 10) {
                        setSelectedFrequencies(prev => [...prev, d]);
                    } else {
                        event.target.checked = false;
                        alert('You can select a maximum of 10 frequencies.');
                    }
                } else {
                    // Remove frequency
                    setSelectedFrequencies(prev => prev.filter(f => f !== d));
                }
            })
            .property('checked', d => selectedFrequencies.includes(d));

        freqCheckboxes.append('label')
            .text(d => d)
            .style('margin-left', '5px');

    }, [data, frequencyFields, sampleNums, selectedSampleOption, selectedFrequencies]);

    // Draw the chart and legend whenever data or parameters change
    useEffect(() => {
        if (data.length === 0 || frequencyFields.length === 0) return;
        if (selectedFrequencies.length === 0) {
            const svg = d3.select(svgRef.current);
            svg.selectAll('*').remove();
            const width = 800;
            const height = 600;
            svg.attr('width', width)
                .attr('height', height);
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', height / 2)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .text('Select up to 10 frequencies to display.');
            return;
        }

        const width = 800;
        const height = 600;
        const margin = { top: 20, right: 220, bottom: 40, left: 150 };

        const svg = d3.select(svgRef.current)
            .attr('width', width)
            .attr('height', height);

        svg.selectAll('*').remove(); // Clear previous chart content

        let displayData = data;
        if (selectedSampleOption !== 'All') {
            const selectedNum = parseInt(selectedSampleOption, 10);
            displayData = data.filter(d => d.Sample_num === selectedNum);
        }

        const classMapping = Object.fromEntries(
            selectedMarkers.map(marker => [String(marker.sample_num), marker.groundTruthLabel])
        );

        const marks = [];
        displayData.forEach(d => {
            const yVal = classMapping[String(d.Sample_num)] || 'Unknown';
            selectedFrequencies.forEach(f => {
                const xVal = +d[f];
                if (!isNaN(xVal)) {
                    marks.push({ x: xVal, y: yVal, freq: f });
                }
            });
        });

        if (marks.length === 0) {
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', height / 2)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .text('No valid data points to display.');
            return;
        }

        // Create the plot
        const plot = scatterPlot()
            .width(width)
            .height(height)
            .data(marks)
            .selectedFrequencies(selectedFrequencies)
            .yType('categorical')
            .margin(margin)
            .radius(5);

        svg.call(plot);

        // Build Legend for frequencies
        const legendGroup = svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(${width - margin.right + 20},${margin.top})`);

        const freqColor = d3.scaleOrdinal(d3.schemeCategory10).domain(selectedFrequencies);

        const legendItems = legendGroup.selectAll('.legend-item-freq')
            .data(selectedFrequencies)
            .join('g')
            .attr('class', 'legend-item-freq')
            .attr('transform', (d, i) => `translate(0, ${i * 20})`);

        legendItems.append('rect')
            .attr('width', 12)
            .attr('height', 12)
            .attr('fill', d => freqColor(d));

        legendItems.append('text')
            .attr('x', 20)
            .attr('y', 10)
            .style('font-size', '12px')
            .text(d => d);

    }, [data, frequencyFields, selectedSampleOption, sampleNums, selectedMarkers, selectedFrequencies]);

    return (
        <div className="scatter-page-container">
            {data.length === 0 && (
                <p style={{ textAlign: 'center', marginTop: '20px' }}>
                    No samples selected. Please go back and select some markers.
                </p>
            )}
            {data.length > 0 && (
                <>
                    <div ref={menuContainerRef} className="menu-container"></div>
                    <svg ref={svgRef}></svg>
                </>
            )}
        </div>
    );
}

export default ScatterPlotPage;
