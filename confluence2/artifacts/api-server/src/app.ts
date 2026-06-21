import cookieParser from "cookie-parser";
import cors from "cors";
import express from "express";
import askRoutes from "./routes/ask.js";
import authRoutes from "./routes/auth.js";
import healthRoutes from "./routes/health.js";
import pagesRoutes from "./routes/pages.js";
import { authMiddleware } from "./middlewares/authMiddleware.js";

export function createApp() {
  const app = express();

  app.use(
    cors({
      origin: process.env.WEB_ORIGIN ?? "http://localhost:5173",
      credentials: true,
    }),
  );
  app.use(express.json({ limit: "2mb" }));
  app.use(cookieParser());
  app.use(authMiddleware);

  app.use("/api", healthRoutes);
  app.use("/api", authRoutes);
  app.use("/api", pagesRoutes);
  app.use("/api", askRoutes);

  app.use(
    (
      error: unknown,
      _req: express.Request,
      res: express.Response,
      _next: express.NextFunction,
    ) => {
      console.error(error);
      if (error instanceof Error) {
        return res.status(500).json({ error: error.message });
      }
      return res.status(500).json({ error: "Internal server error" });
    },
  );

  return app;
}
