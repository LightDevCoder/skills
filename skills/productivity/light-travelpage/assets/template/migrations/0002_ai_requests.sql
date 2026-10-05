-- Store the exact prepared plan before passing it to the shared mutation API.
-- An uncertain AI request can then replay without generating another expense.
CREATE TABLE IF NOT EXISTS ai_requests (
  trip_id TEXT NOT NULL,
  mutation_id TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  plan TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (trip_id, mutation_id)
);
