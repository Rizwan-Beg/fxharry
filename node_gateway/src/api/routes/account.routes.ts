/**
 * Account Routes
 * REST API endpoints for account information
 */

import { Router, Request, Response } from 'express';

const router = Router();

router.get('/account', async (req: Request, res: Response) => {
  // TODO: Implement account info endpoint
  res.json({ account: null });
});

router.get('/account/positions', async (req: Request, res: Response) => {
  // TODO: Implement positions endpoint
  res.json({ positions: [] });
});

router.get('/account/balance', async (req: Request, res: Response) => {
  // TODO: Implement balance endpoint
  res.json({ balance: null });
});

export default router;
