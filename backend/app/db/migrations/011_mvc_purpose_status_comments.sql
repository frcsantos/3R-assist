-- Column comments for Admin Database hints on new MVC fields.

COMMENT ON COLUMN method_validation_contexts.purpose IS
  'What the method is recognized/validated for in this context (endpoint, use, or regulatory purpose).';

COMMENT ON COLUMN method_validation_contexts.regulatory_status IS
  'Regulatory standing: not_approved | approved | recommended | mandatory.';
