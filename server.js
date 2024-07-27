const express = require('express');
const axios = require('axios');
const cron = require('node-cron');
const cors = require('cors'); // Import CORS
const db = require('./database'); // Import the database module
require('dotenv').config();

const app = express();
const port = 3000;

const API_KEY = process.env.API_KEY;
const BASE_URL = 'https://www.alphavantage.co/query';

// Middleware
app.use(cors()); // Enable CORS
app.use(express.json());

// Function to fetch stock price
async function fetchStockPrice(symbol) {
  try {
    const response = await axios.get(BASE_URL, {
      params: {
        function: 'TIME_SERIES_INTRADAY',
        symbol: symbol,
        interval: '5min',
        outputsize: 'compact',
        datatype: 'json',
        apikey: API_KEY
      }
    });

    const timeSeries = response.data['Time Series (5min)'];
    if (!timeSeries) {
      throw new Error('Invalid response data from API');
    }

    const latestDataPoint = Object.entries(timeSeries)[0];
    const [timestamp, values] = latestDataPoint;

    return {
      price: parseFloat(values['4. close']),
      lastUpdated: timestamp
    };
  } catch (error) {
    console.error('Error fetching stock data:', error);
    throw error;
  }
}

// Endpoint to set an alert
app.post('/set-alert', (req, res) => {
  const { symbol, threshold, email } = req.body;

  db.run("INSERT INTO alerts (symbol, threshold, email) VALUES (?, ?, ?)", [symbol, threshold, email], function (err) {
    if (err) {
      console.error('Error setting alert:', err);
      return res.status(500).send('Error setting alert');
    }
    res.status(200).send('Alert set successfully');
  });
});

// Endpoint to get all alerts
app.get('/get-alerts', (req, res) => {
  db.all("SELECT * FROM alerts", [], (err, rows) => {
    if (err) {
      console.error('Error retrieving alerts:', err);
      return res.status(500).send('Error retrieving alerts');
    }
    res.json(rows);
  });
});

// Endpoint to get stock price
app.get('/stock/:symbol', async (req, res) => {
  const symbol = req.params.symbol;

  try {
    const data = await fetchStockPrice(symbol);
    res.json(data);
  } catch (error) {
    res.status(500).send('Error fetching stock data');
  }
});

// Function to check alerts periodically
async function checkAlerts() {
  db.all("SELECT * FROM alerts", [], async (err, rows) => {
    if (err) {
      console.error('Error retrieving alerts', err);
      return;
    }

    for (const row of rows) {
      try {
        const { price } = await fetchStockPrice(row.symbol);
        if (price >= row.threshold) {
          console.log(`ALERT: ${row.symbol} has reached the threshold of ${row.threshold}. Current price: ${price}`);
          // Here you can send an email or SMS alert
        }
      } catch (error) {
        console.error(`Error checking price for ${row.symbol}`, error.message);
      }
    }
  });
}

// Schedule the price check to run every 5 minutes
cron.schedule('*/5 * * * *', checkAlerts);

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
