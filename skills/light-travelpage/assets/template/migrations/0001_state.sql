CREATE TABLE IF NOT EXISTS trip_state (
  trip_id TEXT PRIMARY KEY,
  revision INTEGER NOT NULL DEFAULT 0,
  payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mutation_receipts (
  trip_id TEXT NOT NULL,
  mutation_id TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  revision INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (trip_id, mutation_id)
);
