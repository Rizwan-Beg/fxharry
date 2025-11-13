/**
 * Market Data Routes
 * REST API endpoints for market data
 */

import { Router } from 'express';

const router = Router();

router.get('/market/:symbol', async (req, res) => {
  // TODO: Implement market data endpoint
  res.json({ symbol: req.params.symbol, data: null });
});

router.get('/market/:symbol/history', async (req, res) => {
  // TODO: Implement historical market data endpoint
  res.json({ symbol: req.params.symbol, history: [] });
});

export default router;
