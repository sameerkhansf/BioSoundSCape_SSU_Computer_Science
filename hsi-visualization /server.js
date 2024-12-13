require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => {
    console.log("MongoDB Connected");
}).catch(err => console.error("MongoDB connection error:", err));

const polygonSchema = new mongoose.Schema({
    sample_num: Number,
    coordinates: [[Number]] // array of [lng, lat] pairs
});

const Polygon = mongoose.model('Polygon', polygonSchema);

// Predictions schema
const predictionSchema = new mongoose.Schema({
    sample_num: Number,
    ground_truth: Number,
    predicted_label: Number,
    ground_truth_label: String,
    predicted_label_name: String
});

const Prediction = mongoose.model('Prediction', predictionSchema);

const sampleSchema = new mongoose.Schema({
    Sample_num: Number,
    // ... all the frq fields
}, { collection: 'samples' });

const Sample = mongoose.model('Sample', sampleSchema);

// Updated /api/polygons route
app.get('/api/polygons', async (req, res) => {
    try {
        const polygons = await Polygon.find({});
        const sampleNums = polygons.map(p => p.sample_num);
        const predictions = await Prediction.find({ sample_num: { $in: sampleNums } });

        // Create a map from sample_num to prediction object for quick lookup
        const predictionMap = predictions.reduce((acc, pred) => {
            acc[pred.sample_num] = pred;
            return acc;
        }, {});

        // Combine polygons with their corresponding predictions
        const polygonsWithPredictions = polygons.map(p => {
            const pred = predictionMap[p.sample_num] || {};
            return {
                ...p.toObject(),
                ground_truth_label: pred.ground_truth_label || null,
                predicted_label_name: pred.predicted_label_name || null,
                ground_truth: pred.ground_truth || null,
                predicted_label: pred.predicted_label || null
            };
        });

        res.json(polygonsWithPredictions);
    } catch (error) {
        console.error("Error fetching polygons with predictions:", error);
        res.status(500).send('Server error fetching polygons with predictions');
    }
});

app.get('/api/samples', async (req, res) => {
    const sampleNums = req.query.sample_nums ? req.query.sample_nums.split(',').map(n => parseInt(n)) : [];
    if (!sampleNums.length) {
        return res.json([]);
    }

    const docs = await Sample.find({ Sample_num: { $in: sampleNums } }).lean();
    res.json(docs);
});

app.get('/api/samples', async (req, res) => {
    const sampleNums = req.query.sample_nums ? req.query.sample_nums.split(',').map(n => parseInt(n)) : [];
    if (!sampleNums.length) {
        return res.json([]);
    }

    const docs = await Sample.find({ Sample_num: { $in: sampleNums } }).lean();
    res.json(docs);
});

app.get('/api/predictions', async (req, res) => {
    try {
        const predictions = await Prediction.find({});
        res.json(predictions);
    } catch (error) {
        console.error("Error fetching predictions:", error);
        res.status(500).send('Server error fetching predictions');
    }
});


const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
