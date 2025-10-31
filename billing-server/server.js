const express = require('express');
const app = express();
const PORT = 4201;

app.use(express.json());

let successURL = 'https://www.google.com/'
let cancelURL = 'https://docs.github.com/'
let bearerToken = ''

app.get('/api/product-providers/payment-gateways/count', (req, res) => {
  console.log('Received request:', req.query);
  res.json(2);
});

app.post('/api/payment-start', (req, res) => {
  const body = req.body
  const authHeader = req.headers.authorization
  bearerToken = authHeader ? authHeader.replace('Bearer ', '') : ''
  console.log('received payment ref', body)
  successURL = body.processSuccessUrl
  cancelURL = body.processErrorUrl
  res.json({redirectUrl: 'http://localhost:4201/checkin'})
})

app.get('/checkin', (req, res) => {
  console.log('received checkin ', successURL)
  res.redirect(successURL + '&token=' + bearerToken)
})

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Billing server running on http://0.0.0.0:${PORT}`);
});
