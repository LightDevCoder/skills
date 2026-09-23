/** Shared contract for trip seeds and live todo records. */
export function validTodoRecord(value) {
  return Boolean(
    value && typeof value === "object" && !Array.isArray(value) &&
    typeof value.id === "string" && /^[a-zA-Z0-9_-]{1,100}$/.test(value.id) &&
    typeof value.text === "string" && Boolean(value.text.trim()) &&
    value.text.length <= 1000 && typeof value.completed === "boolean"
  );
}

export function validTodoRecords(values) {
  return Array.isArray(values) && values.every(validTodoRecord) &&
    new Set(values.map((value) => value.id)).size === values.length;
}
