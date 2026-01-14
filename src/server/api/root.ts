import { initTRPC } from '@trpc/server';
import { riskCheckerRouter } from './routers/riskChecker';

const t = initTRPC.create();

export const appRouter = t.router({
  riskChecker: riskCheckerRouter,
});

export type AppRouter = typeof appRouter;
