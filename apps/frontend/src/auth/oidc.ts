import type { AuthProviderProps } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";

/**
 * OIDC config for Cognito Hosted UI (Authorization Code + PKCE).
 * Values come from `terraform output` (see infra/terraform/aws).
 */
export const oidcConfig: AuthProviderProps = {
  authority: import.meta.env.VITE_COGNITO_AUTHORITY,
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,
  redirect_uri: import.meta.env.VITE_REDIRECT_URI,
  response_type: "code",
  scope: "openid email profile",
  // Persist tokens so a page reload keeps the session.
  userStore: new WebStorageStateStore({ store: window.localStorage }),
  // Strip ?code=&state= from the URL after a successful login.
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname);
  },
};

/**
 * Cognito's OIDC discovery document has no end_session_endpoint, so sign-out is
 * done by redirecting to the Hosted UI /logout endpoint explicitly.
 */
export function cognitoLogoutUrl(): string {
  const domain = import.meta.env.VITE_COGNITO_DOMAIN;
  const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
  const logoutUri = import.meta.env.VITE_REDIRECT_URI;
  const params = new URLSearchParams({ client_id: clientId, logout_uri: logoutUri });
  return `https://${domain}/logout?${params.toString()}`;
}
