import { useAuth } from "react-oidc-context";

/** The current Cognito access token, sent as a Bearer credential to the API. */
export function useToken(): string {
  return useAuth().user?.access_token ?? "";
}
