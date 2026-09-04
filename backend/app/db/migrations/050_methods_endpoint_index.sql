-- Recreate methods.endpoint_category index dropped when the TEXT column was replaced.

CREATE INDEX IF NOT EXISTS idx_methods_endpoint ON methods(endpoint_category);
