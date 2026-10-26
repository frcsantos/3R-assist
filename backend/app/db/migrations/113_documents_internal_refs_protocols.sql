-- =============================================================================
-- Migration 113: internal_doc_refs for the protocol documents added in 110.
-- Each OECD document gets the ids of the catalogue documents that appear in its
-- own reference list (checked against the full TG texts):
--   TG 439: ref 32 EpiSkin SOP (DB-ALM 131), ref 34 SkinEthic RHE SOP (DB-ALM
--           135), ref 35 LabCyte EPI-MODEL24 SIT SOP v8.3.
--   TG 431: ref 42 LabCyte EPI-MODEL24 SCT SOP v1.6, ref 43 peer review report
--           of the LabCyte skin corrosion validation (same report as the 2018
--           panel evaluation, to be confirmed).
--   TG 492: refs 45-48 EpiOcular EIT SOP (DB-ALM 164), SkinEthic HCE EIT SOP
--           (DB-ALM 190 and 191), LabCyte CORNEA-MODEL24 SOP and MCTT HCE SOP;
--           the catalogue holds newer versions of the last two (v2.7, v1.8; the
--           TG cites v2.5.6 and v1.7).
--   TG 492B: refs 28-29 SkinEthic HCE TTL and TTS SOPs.
-- Not linked: the EpiSensA SOP (TG 442D cites only the validation and peer
-- review reports) and the KeraSkin phototoxicity SOP (TG 498 is not in the
-- catalogue).
-- =============================================================================

BEGIN;

WITH links(citing, cited) AS (
  VALUES
    ('oecd-test-no-439-2025-06-25-in-vitro-skin-irritation-reconstructed-human-epidermis-tes', ARRAY[
      'db-alm-protocol-131-episkin-skin-irritation-test',
      'db-alm-protocol-135-skinethic-skin-irritation-test',
      'jtec-labcyte-epi-model24-skin-irritation-test-sop-v8-3']),
    ('oecd-test-no-431-2025-06-25-in-vitro-skin-corrosion-reconstructed-human-epidermis-rhe-', ARRAY[
      'jtec-labcyte-epi-model24-skin-corrosion-test-sop-v1-6',
      'jacvam-labcyte-epi-model24-skin-corrosion-peer-review-report-2018']),
    ('oecd-test-no-492-2025-06-25-reconstructed-human-cornea-like-epithelium-rhce-test-metho', ARRAY[
      'db-alm-protocol-164-epiocular-eye-irritation-test',
      'db-alm-protocol-190-skinethic-hce-eye-irritation-test-liquid',
      'db-alm-protocol-191-skinethic-hce-eye-irritation-test-solid',
      'jtec-labcyte-cornea-model24-eye-irritation-test-protocol-v2-7',
      'biosolution-mctt-hce-eye-irritation-test-sop-v1-8']),
    ('oecd-test-no-492b-2024-06-25-reconstructed-human-cornea-like-epithelium', ARRAY[
      'db-alm-skinethic-hce-time-to-toxicity-liquids-ttl',
      'db-alm-skinethic-hce-time-to-toxicity-solids-tts'])
), resolved AS (
  SELECT c.id AS citing_id,
         ARRAY(SELECT d.id FROM documents d WHERE d.slug = ANY (l.cited)) AS cited_ids
  FROM links l
  JOIN documents c ON c.slug = l.citing
)
UPDATE documents d
SET internal_doc_refs = ARRAY(
  SELECT DISTINCT x FROM unnest(d.internal_doc_refs || r.cited_ids) AS x ORDER BY x
)
FROM resolved r
WHERE d.id = r.citing_id;

COMMIT;
