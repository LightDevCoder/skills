/** Public generation switch. Provider credentials belong only in server env. */
export function normalizeAiConfig(raw = { provider: "off" }) {
  if (!raw || typeof raw !== "object" || Array.isArray(raw) ||
      Object.keys(raw).some((key) => key !== "provider") ||
      !["off", "openai"].includes(raw.provider)) {
    throw new Error("ai-config.json must contain only provider: off or openai");
  }
  return { provider: raw.provider };
}
