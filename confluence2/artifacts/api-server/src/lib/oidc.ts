import * as client from "openid-client";
import type { AppUser } from "./auth.js";
import {
  getAllowedDomains,
  getApiBaseUrl,
  getCallbackUrl,
  getDevUser,
  isDevAuthBypassEnabled,
} from "./auth.js";

let oidcConfig: client.Configuration | null = null;
const pendingLogins = new Map<
  string,
  { codeVerifier: string; nonce: string; redirectTo: string }
>();

function getIssuerUrl(): string {
  return process.env.ISSUER_URL ?? "https://replit.com/oidc";
}

function getClientId(): string {
  const replId = process.env.REPL_ID;
  if (!replId) {
    throw new Error("REPL_ID is required for Replit Auth");
  }
  return replId;
}

export async function getOidcConfig(): Promise<client.Configuration> {
  if (!oidcConfig) {
    oidcConfig = await client.discovery(
      new URL(getIssuerUrl()),
      getClientId(),
      undefined,
    );
  }
  return oidcConfig;
}

export async function buildAuthorizationUrl(req: {
  protocol: string;
  get(name: string): string | undefined;
}) {
  const config = await getOidcConfig();
  const codeVerifier = client.randomPKCECodeVerifier();
  const codeChallenge = await client.calculatePKCECodeChallenge(codeVerifier);
  const state = client.randomState();
  const nonce = client.randomNonce();
  const redirectTo = getAllowedDomains()[0]
    ? `${req.protocol === "https" ? "https" : "http"}://${getAllowedDomains()[0]}`
    : process.env.WEB_ORIGIN ?? "http://localhost:5173";

  pendingLogins.set(state, { codeVerifier, nonce, redirectTo });

  const url = client.buildAuthorizationUrl(config, {
    redirect_uri: getCallbackUrl(req as never),
    scope: "openid email profile offline_access",
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
    state,
    nonce,
  });

  return url;
}

export async function handleAuthCallback(req: {
  originalUrl: string;
  protocol: string;
  get(name: string): string | undefined;
}) {
  const config = await getOidcConfig();
  const currentUrl = new URL(`${getApiBaseUrl(req as never)}${req.originalUrl}`);
  const state = currentUrl.searchParams.get("state");
  if (!state) {
    throw new Error("Missing state");
  }

  const pending = pendingLogins.get(state);
  pendingLogins.delete(state);
  if (!pending) {
    throw new Error("Invalid or expired login state");
  }

  const tokens = await client.authorizationCodeGrant(config, currentUrl, {
    pkceCodeVerifier: pending.codeVerifier,
    expectedState: state,
    expectedNonce: pending.nonce,
  });

  const claims = tokens.claims();
  const user: AppUser = {
    id: String(claims?.sub ?? ""),
    email: (claims?.email as string | undefined) ?? null,
    firstName: (claims?.given_name as string | undefined) ?? null,
    lastName: (claims?.family_name as string | undefined) ?? null,
    profileImageUrl: (claims?.picture as string | undefined) ?? null,
  };

  return {
    user,
    session: {
      user,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      idToken: tokens.id_token,
      expiresAt: tokens.expires_in ? Date.now() + tokens.expires_in * 1000 : undefined,
    },
    redirectTo: pending.redirectTo,
  };
}

export async function refreshSessionTokens(session: {
  user: AppUser;
  accessToken?: string;
  refreshToken?: string;
  idToken?: string;
  expiresAt?: number;
}) {
  if (!session.refreshToken) {
    return session;
  }
  if (session.expiresAt && session.expiresAt > Date.now() + 60_000) {
    return session;
  }

  const config = await getOidcConfig();
  const tokens = await client.refreshTokenGrant(config, session.refreshToken);
  return {
    ...session,
    accessToken: tokens.access_token ?? session.accessToken,
    refreshToken: tokens.refresh_token ?? session.refreshToken,
    idToken: tokens.id_token ?? session.idToken,
    expiresAt: tokens.expires_in ? Date.now() + tokens.expires_in * 1000 : session.expiresAt,
  };
}

export async function endOidcSession(idToken?: string) {
  if (!idToken || isDevAuthBypassEnabled()) return null;
  const config = await getOidcConfig();
  const url = client.buildEndSessionUrl(config, {
    id_token_hint: idToken,
  });
  return url.toString();
}

export function createDevSession() {
  const user = getDevUser();
  return {
    user,
    session: { user },
    redirectTo: process.env.WEB_ORIGIN ?? "http://localhost:5173",
  };
}

export async function exchangeMobileCode(input: {
  code: string;
  codeVerifier: string;
  redirectUri: string;
}) {
  const config = await getOidcConfig();
  const currentUrl = new URL(input.redirectUri);
  currentUrl.searchParams.set("code", input.code);
  const tokens = await client.authorizationCodeGrant(config, currentUrl, {
    pkceCodeVerifier: input.codeVerifier,
  });
  const claims = tokens.claims();
  const user: AppUser = {
    id: String(claims?.sub ?? ""),
    email: (claims?.email as string | undefined) ?? null,
    firstName: (claims?.given_name as string | undefined) ?? null,
    lastName: (claims?.family_name as string | undefined) ?? null,
    profileImageUrl: (claims?.picture as string | undefined) ?? null,
  };
  return {
    user,
    session: {
      user,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      idToken: tokens.id_token,
      expiresAt: tokens.expires_in ? Date.now() + tokens.expires_in * 1000 : undefined,
    },
  };
}
