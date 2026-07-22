-- ============================================================
-- SolarAIM Hierarchy Seed Script
-- Populates: sections (4) -> inverters (36, 9/section) -> strings (864, 24/inverter)
-- Naming:
--   Section-1 .. Section-4
--   INV-01 .. INV-36            (sequential across all sections)
--   STR-<inverter_num>-<string_num>   e.g. STR-01-03
-- Usage:
--   docker exec -i timescaledb psql -U postgres -d solaraim < solaraim_seed.sql
-- ============================================================

DO $$
DECLARE
    section_count   INT := 4;
    inverters_per   INT := 9;
    strings_per     INT := 24;

    sec_id          INT;
    inv_id          INT;
    inv_global_num  INT := 0;

    sec_num         INT;
    inv_num         INT;
    str_num         INT;
BEGIN
    FOR sec_num IN 1..section_count LOOP
        INSERT INTO sections (code, name)
        VALUES (
            'Section-' || sec_num,
            'Section ' || sec_num
        )
        ON CONFLICT (code) DO NOTHING
        RETURNING id INTO sec_id;

        -- If it already existed (conflict), fetch its id
        IF sec_id IS NULL THEN
            SELECT id INTO sec_id FROM sections WHERE code = 'Section-' || sec_num;
        END IF;

        FOR inv_num IN 1..inverters_per LOOP
            inv_global_num := inv_global_num + 1;

            INSERT INTO inverters (code, section_id, name)
            VALUES (
                'INV-' || lpad(inv_global_num::text, 2, '0'),
                sec_id,
                'Inverter ' || lpad(inv_global_num::text, 2, '0')
            )
            ON CONFLICT (code) DO NOTHING
            RETURNING id INTO inv_id;

            IF inv_id IS NULL THEN
                SELECT id INTO inv_id FROM inverters
                WHERE code = 'INV-' || lpad(inv_global_num::text, 2, '0');
            END IF;

            FOR str_num IN 1..strings_per LOOP
                INSERT INTO strings (code, inverter_id, name)
                VALUES (
                    'STR-' || lpad(inv_global_num::text, 2, '0') || '-' || lpad(str_num::text, 2, '0'),
                    inv_id,
                    'String ' || lpad(str_num::text, 2, '0')
                )
                ON CONFLICT (code) DO NOTHING;
            END LOOP;
        END LOOP;
    END LOOP;
END $$;

-- ============================================================
-- Verification queries
-- ============================================================

SELECT COUNT(*) AS section_count FROM sections;
SELECT COUNT(*) AS inverter_count FROM inverters;
SELECT COUNT(*) AS string_count FROM strings;

-- Sample: first inverter's strings
SELECT s.code AS string_code, i.code AS inverter_code, sec.code AS section_code
FROM strings s
JOIN inverters i ON s.inverter_id = i.id
JOIN sections sec ON i.section_id = sec.id
WHERE i.code = 'INV-01'
ORDER BY s.code
LIMIT 5;
