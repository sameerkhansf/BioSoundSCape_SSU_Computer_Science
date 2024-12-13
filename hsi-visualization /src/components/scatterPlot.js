// scatterPlot.js
import {
    scaleLinear,
    scalePoint,
    extent,
    axisLeft,
    axisBottom,
    transition,
    scaleOrdinal,
    schemeCategory10
} from 'd3';

export const scatterPlot = () => {
    let width;
    let height;
    let data;
    let yType; // 'categorical' or 'quantitative'
    let margin;
    let radius;
    let selectedFrequencies;

    const my = (selection) => {
        const t = transition().duration(1000);
        const yValues = [...new Set(data.map(d => d.y))];

        let xDomain = extent(data.map(d => d.x));
        if (xDomain[0] === xDomain[1]) {
            xDomain = [xDomain[0] - 1, xDomain[1] + 1];
        }

        const x = scaleLinear().domain(xDomain).range([margin.left, width - margin.right]);
        const y = (yType === 'categorical'
            ? scalePoint().domain(yValues).padding(0.5)
            : scaleLinear().domain(extent(data, d => d.y)))
            .range([height - margin.bottom, margin.top]);

        const color = scaleOrdinal(schemeCategory10).domain(selectedFrequencies || []);

        const positionCircles = (circles) => {
            circles
                .attr('cx', d => x(d.x))
                .attr('cy', d => y(d.y));
        };

        const initializeRadius = (circles) => {
            circles.attr('r', 0);
        };

        const growRadius = (enter) => {
            enter.transition(t).attr('r', radius);
        };

        selection
            .selectAll('circle')
            .data(data)
            .join(
                enter =>
                    enter.append('circle')
                        .call(positionCircles)
                        .call(initializeRadius)
                        .call(growRadius)
                        .attr('fill', d => color(d.freq))
                        .attr('opacity', 0.7),
                update =>
                    update.call(update =>
                        update.transition(t)
                            .call(positionCircles)
                            .attr('fill', d => color(d.freq))
                    ),
                exit => exit.remove()
            );

        // Y Axis
        selection
            .selectAll('.y-axis')
            .data([null])
            .join('g')
            .attr('class', 'y-axis')
            .attr('transform', `translate(${margin.left},0)`)
            .transition(t)
            .call(axisLeft(y));

        // X Axis
        selection
            .selectAll('.x-axis')
            .data([null])
            .join('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .transition(t)
            .call(axisBottom(x));
    };

    my.width = function (_) {
        return arguments.length ? ((width = +_), my) : width;
    };

    my.height = function (_) {
        return arguments.length ? ((height = +_), my) : height;
    };

    my.data = function (_) {
        return arguments.length ? ((data = _), my) : data;
    };

    my.yType = function (_) {
        return arguments.length ? ((yType = _), my) : yType;
    };

    my.margin = function (_) {
        return arguments.length ? ((margin = _), my) : margin;
    };

    my.radius = function (_) {
        return arguments.length ? ((radius = +_), my) : radius;
    };

    my.selectedFrequencies = function (_) {
        return arguments.length ? ((selectedFrequencies = _), my) : selectedFrequencies;
    };

    return my;
};
