// barPlot.js
import { scaleBand, scaleLinear, axisLeft, axisBottom, select, transition } from 'd3';

export const barPlot = () => {
    let width;
    let height;
    let data; // data = [{ class: '...', value: number }]
    let margin;
    let titleText = '';
    let xLabel = 'Class';
    let yLabel = 'Frequency';

    const my = (selection) => {
        const t = transition().duration(1000);

        const classes = data.map(d => d.class);
        const x = scaleBand()
            .domain(classes)
            .range([margin.left, width - margin.right])
            .padding(0.1);

        const yMax = Math.max(0, ...data.map(d => d.value));
        const y = scaleLinear()
            .domain([0, yMax]).nice()
            .range([height - margin.bottom, margin.top]);

        // Axes
        selection.selectAll('.x-axis')
            .data([null])
            .join('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(axisBottom(x));

        selection.selectAll('.y-axis')
            .data([null])
            .join('g')
            .attr('class', 'y-axis')
            .attr('transform', `translate(${margin.left},0)`)
            .call(axisLeft(y));

        // Bars
        const rects = selection.selectAll('.bar')
            .data(data, d => d.class);

        rects.join(
            enter => enter.append('rect')
                .attr('class', 'bar')
                .attr('x', d => x(d.class))
                .attr('y', height - margin.bottom)
                .attr('width', x.bandwidth())
                .attr('height', 0)
                .transition(t)
                .attr('y', d => y(d.value))
                .attr('height', d => height - margin.bottom - y(d.value))
                .attr('fill', '#69b3a2'),
            update => update.transition(t)
                .attr('x', d => x(d.class))
                .attr('y', d => y(d.value))
                .attr('width', x.bandwidth())
                .attr('height', d => height - margin.bottom - y(d.value)),
            exit => exit.remove()
        );

        // Title
        selection.selectAll('.chart-title')
            .data([null])
            .join('text')
            .attr('class', 'chart-title')
            .attr('x', (width / 2))
            .attr('y', margin.top / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .text(titleText);

        // Labels
        selection.selectAll('.x-label')
            .data([null])
            .join('text')
            .attr('class', 'x-label')
            .attr('x', width / 2)
            .attr('y', height - 5)
            .attr('text-anchor', 'middle')
            .style('font-size', '12px')
            .text(xLabel);

        selection.selectAll('.y-label')
            .data([null])
            .join('text')
            .attr('class', 'y-label')
            .attr('transform', `translate(${margin.left - 40},${height / 2}) rotate(-90)`)
            .attr('text-anchor', 'middle')
            .style('font-size', '12px')
            .text(yLabel);
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

    my.margin = function (_) {
        return arguments.length ? ((margin = _), my) : margin;
    };

    my.titleText = function (_) {
        return arguments.length ? ((titleText = _), my) : titleText;
    };

    my.xLabel = function (_) {
        return arguments.length ? ((xLabel = _), my) : xLabel;
    };

    my.yLabel = function (_) {
        return arguments.length ? ((yLabel = _), my) : yLabel;
    };

    return my;
};
