import { authenticate, secure } from "../server/auth.js";
export async function onRequest(context) {
  const denied = await authenticate(context);
  return denied || secure(await context.next());
}
