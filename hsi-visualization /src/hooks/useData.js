import { useEffect, useState } from 'react';

export function useData() {
    const [polygons, setPolygons] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const backendUrl = process.env.REACT_APP_BACKEND_URL;
        fetch(`${backendUrl}/api/polygons`)
            .then(res => {
                if (!res.ok) throw new Error(`Error fetching polygons: ${res.statusText}`);
                return res.json();
            })
            .then(polyData => {
                setPolygons(polyData);

                // Get the unique categories from ground_truth_label
                const uniqueCategories = [...new Set(polyData.map(item => item.ground_truth_label))].filter(Boolean);
                setCategories(uniqueCategories);
            })
            .catch(err => {
                setError(err.message);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    return { polygons, categories, loading, error };
}
