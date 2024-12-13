import React from 'react';
import '../styles/TopBar.css';

export function TopBar({ title }) {
    return (
        <div className="top-bar">
            <h1>{title}</h1>
        </div>
    );
}
