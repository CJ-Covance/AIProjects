import { Router } from "express";
import { getWebOrigin, isDevAuthBypassEnabled } from "../lib/auth.js";
import {
  buildAuthorizationUrl,
  createDevSession,
  endOidcSession,
  exchangeMobileCode,
  handleAuthCallback,
} from "../lib/oidc.js";
import { deleteSession } from "../lib/session-store.js";
import { issueSession, requireAuth } from "../middlewares/authMiddleware.js";

const router = Router();

router.get("/login", async (req, res, next) => {
  try {
    if (isDevAuthBypassEnabled()) {
      const dev = createDevSession();
      await issueSession(res, dev.session);
      return res.redirect(getWebOrigin());
    }
    const url = await buildAuthorizationUrl(req);
    return res.redirect(url.toString());
  } catch (error) {
    return next(error);
  }
});

router.get("/callback", async (req, res, next) => {
  try {
    const result = await handleAuthCallback(req);
    await issueSession(res, result.session);
    return res.redirect(result.redirectTo);
  } catch (error) {
    return next(error);
  }
});

router.get("/logout", async (req, res, next) => {
  try {
    const sid = req.sessionId;
    const idToken = req.session?.idToken;
    if (sid) {
      await deleteSession(sid);
    }
    res.clearCookie("sid");
    const endUrl = await endOidcSession(idToken);
    if (endUrl) {
      return res.redirect(endUrl);
    }
    return res.redirect(getWebOrigin());
  } catch (error) {
    return next(error);
  }
});

router.get("/auth/user", (req, res) => {
  res.json({ user: req.session?.user ?? null });
});

router.post("/mobile-auth/token-exchange", async (req, res, next) => {
  try {
    const { code, codeVerifier, redirectUri } = req.body ?? {};
    if (!code || !codeVerifier || !redirectUri) {
      return res.status(400).json({ error: "code, codeVerifier, and redirectUri are required" });
    }
    const result = await exchangeMobileCode({ code, codeVerifier, redirectUri });
    const token = await issueSession(res, result.session);
    return res.json({ token });
  } catch (error) {
    return next(error);
  }
});

router.post("/mobile-auth/logout", requireAuth, async (req, res, next) => {
  try {
    if (req.sessionId) {
      await deleteSession(req.sessionId);
    }
    res.clearCookie("sid");
    return res.status(204).send();
  } catch (error) {
    return next(error);
  }
});

export default router;
