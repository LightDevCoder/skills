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
  `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Light-TravelPage · 同行入口</title>
  <script src="/i18n.js" defer></script>
  <style>
    :root{--paper:#eeeae0;--surface:#fffdf6;--ink:#2b2e27;--muted:#62645c;--line:#cecbbf;--accent:#954434;--serif:Georgia,"Songti SC","Noto Serif CJK SC","Source Han Serif SC","STSong","SimSun",serif;--ui:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Noto Sans CJK SC",sans-serif}
    *{box-sizing:border-box}
    body{margin:0;min-height:100svh;display:grid;place-items:center;padding:32px 24px;background:var(--paper);color:var(--ink);font:14px/1.65 var(--ui)}
    main{width:min(100%,520px);padding:32px 44px 38px;background:var(--surface);border:1px solid var(--line);box-shadow:0 3px 0 #d6d2c7}
    header{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-bottom:20px;border-bottom:1px solid var(--ink)}
    .wordmark{font-size:11px;letter-spacing:.08em;color:var(--muted)}
    h1{margin:32px 0 14px;font:400 42px/1.35 var(--serif);letter-spacing:.02em}
    .intro{margin:0 0 30px;color:var(--muted)}
    label{display:block;margin-bottom:8px}
    input,button{font:inherit;border:1px solid var(--line);border-radius:3px}
    input{width:100%;min-height:48px;padding:12px;background:var(--surface);color:var(--ink)}
    button{cursor:pointer}
    #language-toggle{padding:6px 10px;background:transparent;color:var(--muted);font-size:12px;white-space:nowrap}
    .submit{width:100%;min-height:48px;margin-top:16px;padding:12px;background:var(--accent);border-color:var(--accent);color:var(--surface)}
    .submit:hover{background:#7e392c}
    input:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:4px}
    .error{margin:16px 0 0;color:var(--accent)}
    .error:empty{display:none}
    @media(max-width:540px){body{padding:24px 16px}main{padding:24px}h1{font-size:36px;margin-top:28px}}
  </style>
</head>
<body>
  <main aria-labelledby="login-title">
    <header><span class="wordmark" data-no-translate>LIGHT / TRAVELPAGE</span><button type="button" id="language-toggle" data-no-translate>中文 / EN</button></header>
    <h1 id="login-title">旅行手册</h1>
    <p class="intro">输入访问码，查看行程、预订和同行账本。</p>
    <form method="post" action="/auth/login">
      <label for="code">小组访问码</label>
      <input id="code" name="code" type="password" autocomplete="current-password" required maxlength="256">
      <button class="submit" type="submit">打开手册</button>
    </form>
    <p role="alert" class="error">${error}</p>
  </main>
</body>
</html>`;
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
