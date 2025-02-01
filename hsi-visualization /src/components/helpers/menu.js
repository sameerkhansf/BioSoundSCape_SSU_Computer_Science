import { select } from 'd3';

export const menu = () => {
    let id;
    let labelText;
    let options;
    let onChange;
    let multiSelect = false; 

    const my = (selection) => {
        const container = selection.append('div').attr('id', id);

        container.append('label')
            .attr('for', id + '-select')
            .text(labelText + ' ');

        const selectEl = container.append('select')
            .attr('id', id + '-select')
            .attr('multiple', multiSelect) 
            .on('change', function () {
                const selectedValues = Array.from(this.selectedOptions).map(opt => opt.value);
                onChange(selectedValues);
            });

        selectEl.selectAll('option')
            .data(options)
            .join('option')
            .attr('value', d => d.value)
            .text(d => d.text);
    };

    my.id = function (_) {
        return arguments.length ? ((id = _), my) : id;
    };

    my.labelText = function (_) {
        return arguments.length ? ((labelText = _), my) : labelText;
    };

    my.options = function (_) {
        return arguments.length ? ((options = _), my) : options;
    };

    my.multiSelect = function (_) {
        return arguments.length ? ((multiSelect = _), my) : multiSelect;
    };

    my.on = function (eventType, handler) {
        if (eventType === 'change') {
            onChange = handler;
        }
        return my;
    };

    return my;
};
