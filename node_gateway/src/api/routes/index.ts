/**
 * API Routes Registry
 * Central export for all REST API routes
 */

import { Router } from 'express';
import marketRoutes from './market.routes';
import tradesRoutes from './trades.routes';
import accountRoutes from './account.routes';

const router = Router();

router.use('/market', marketRoutes);
router.use('/trades', tradesRoutes);
router.use('/account', accountRoutes);

export default router;
