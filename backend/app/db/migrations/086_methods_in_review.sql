-- Migration 086: all methods enter curation review (review_status = 'in_review').
BEGIN;
UPDATE methods SET review_status = 'in_review' WHERE review_status = 'not_reviewed';
COMMIT;
