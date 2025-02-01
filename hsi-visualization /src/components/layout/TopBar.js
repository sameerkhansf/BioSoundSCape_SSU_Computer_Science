/**
 * TopBar.js
 * 
 * Displays a top bar with a title.
 * Fixed position with subtle styling.
 */

import React from 'react';
import '../../styles/TopBar.css';

export function TopBar({ title }) {
    return (
        <div className="top-bar">
            <h1>{title}</h1>
        </div>
    );
}
