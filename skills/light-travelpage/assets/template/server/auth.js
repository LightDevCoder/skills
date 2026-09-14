const encoder = new TextEncoder();
const cookieName = "light_travel_session";
export async function digest(value) {
  return [
    ...new Uint8Array(
      await crypto.subtle.digest("SHA-256", encoder.encode(value)),
    ),
  ]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
}
function equal(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length)
    return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
async function sign(value, secret) {
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  return [
    ...new Uint8Array(
      await crypto.subtle.sign("HMAC", key, encoder.encode(value)),
    ),
  ]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
}
export function configured(env) {
  return (
    /^[a-zA-Z0-9_-]{1,100}$/.test(env.TRIP_ID || "") &&
    /^[a-f0-9]{64}$/.test(env.ACCESS_CODE_HASH || "") &&
    (env.SESSION_SECRET || "").length >= 32
  );
}
export async function sessionValid(request, env) {
  if (!configured(env)) return false;
  const cookie = (request.headers.get("cookie") || "")
    .split(";")
    .map((x) => x.trim())
    .find((x) => x.startsWith(`${cookieName}=`))
    ?.slice(cookieName.length + 1);
  if (!cookie) return false;
  const [expires, signature, extra] = cookie.split(".");
  if (
    extra ||
    !/^\d{13}$/.test(expires || "") ||
    Number(expires) < Date.now() ||
    Number(expires) > Date.now() + 8 * 86400000
  )
    return false;
  return equal(
    signature,
    await sign(
      `${env.TRIP_ID}:${expires}:${env.ACCESS_CODE_HASH}`,
      env.SESSION_SECRET,
    ),
  );
}
export function sameOrigin(request) {
  return request.headers.get("origin") === new URL(request.url).origin;
}
const loginPage = (error = "") =>
  `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Light-TravelPage · 同行入口</title><script src="/i18n.js" defer></script><style>body{margin:0;background:#f3f6f2;color:#263a32;font:300 17px/1.7 Baskerville,"Songti SC","Noto Serif CJK SC",STSong,SimSun,serif;display:grid;min-height:100svh;place-items:center}main{max-width:360px;padding:32px}h1{font-size:34px;font-weight:300;line-height:1.4}input,button{box-sizing:border-box;width:100%;padding:14px;margin-top:16px;border:1px solid #a5b2a8;border-radius:12px;font:inherit}button{background:#36584a;color:white}p{line-height:1.7}.error{color:#a32424}</style><main><button type="button" id="language-toggle" data-no-translate>中文 / EN</button><p>LIGHT / TRAVELPAGE</p><h1>和同行的人<br>一起出发</h1><p>输入旅行小组的访问码，查看行程、门票和共享账本。</p><form method="post" action="/auth/login"><label for="code">小组访问码</label><input id="code" name="code" type="password" autocomplete="current-password" required maxlength="256"><button>进入旅程</button></form><p role="alert" class="error">${error}</p></main></html>`;
export function secure(response) {
  const headers = new Headers(response.headers);
  headers.set("Cache-Control", "no-store");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "same-origin");
  headers.set(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-src 'self' https://www.google.com https://maps.google.com; object-src 'self'; base-uri 'self'; frame-ancestors 'self'; form-action 'self'",
  );
  return new Response(response.body, { status: response.status, headers });
}
export async function authenticate(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  if (!configured(env))
    return secure(
      new Response("Travel group access is not configured.", { status: 503 }),
    );
  if (url.pathname === "/i18n.js" && ["GET", "HEAD"].includes(request.method)) return null;
  if (url.pathname === "/login" && request.method === "GET")
    return secure(
      new Response(loginPage(), {
        headers: { "content-type": "text/html; charset=utf-8" },
      }),
    );
  if (url.pathname === "/auth/login" && request.method === "POST") {
    if (!sameOrigin(request))
      return secure(new Response("Forbidden", { status: 403 }));
    if (Number(request.headers.get("content-length")) > 4096)
      return secure(new Response("Too large", { status: 413 }));
    const body = await request.text();
    if (body.length > 4096)
      return secure(new Response("Too large", { status: 413 }));
    const code = new URLSearchParams(body).get("code") || "";
    if (!equal(await digest(code), env.ACCESS_CODE_HASH))
      return secure(
        new Response(loginPage("访问码不正确，请重试。"), {
          status: 401,
          headers: { "content-type": "text/html; charset=utf-8" },
        }),
      );
    const expires = String(Date.now() + 7 * 86400000);
    const signature = await sign(
      `${env.TRIP_ID}:${expires}:${env.ACCESS_CODE_HASH}`,
      env.SESSION_SECRET,
    );
    return secure(
      new Response(null, {
        status: 303,
        headers: {
          location: "/",
          "set-cookie": `${cookieName}=${expires}.${signature}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=604800`,
        },
      }),
    );
  }
  if (!(await sessionValid(request, env))) {
    return secure(
      url.pathname.startsWith("/api/")
        ? Response.json({ error: "请重新登录旅行小组。" }, { status: 401 })
        : new Response(null, { status: 303, headers: { location: "/login" } }),
    );
  }
  if (!["GET", "HEAD"].includes(request.method) && !sameOrigin(request))
    return secure(new Response("Forbidden", { status: 403 }));
  if (url.pathname === "/auth/logout" && request.method === "POST")
    return secure(
      new Response(null, {
        status: 303,
        headers: {
          location: "/login",
          "set-cookie": `${cookieName}=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0`,
        },
      }),
    );
  return null;
}
