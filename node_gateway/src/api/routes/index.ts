/**
 * API Routes Registry
 * Central export for all REST API routes
 */

import { Router } from 'express';
import marketRoutes from './market.routes.js';
import tradesRoutes from './trades.routes.js';
import accountRoutes from './account.routes.js';

const router = Router();

router.use('/market', marketRoutes);
router.use('/trades', tradesRoutes);
router.use('/account', accountRoutes);

export default router;
