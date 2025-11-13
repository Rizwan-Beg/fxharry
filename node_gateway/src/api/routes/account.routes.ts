/**
 * Account Routes
 * REST API endpoints for account information
 */

import { Router } from 'express';

const router = Router();

router.get('/account', async (req, res) => {
  // TODO: Implement account info endpoint
  res.json({ account: null });
});

router.get('/account/positions', async (req, res) => {
  // TODO: Implement positions endpoint
  res.json({ positions: [] });
});

router.get('/account/balance', async (req, res) => {
  // TODO: Implement balance endpoint
  res.json({ balance: null });
});

export default router;
