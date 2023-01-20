-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler version: 0.9.4
-- PostgreSQL version: 13.0
-- Project Site: pgmodeler.io
-- Model Author: ---
-- object: administrator | type: ROLE --
DROP ROLE IF EXISTS administrator;


CREATE ROLE administrator WITH 
	CREATEDB
	LOGIN
	ENCRYPTED PASSWORD '';
-- ddl-end --

-- object: doctor | type: ROLE --
DROP ROLE IF EXISTS doctor;
CREATE ROLE doctor WITH 
	LOGIN
	ENCRYPTED PASSWORD '';
-- ddl-end --


-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: polyclinic | type: DATABASE --
-- DROP DATABASE IF EXISTS polyclinic;
CREATE DATABASE polyclinic;
ALTER DATABASE polyclinic SET search_path TO polyclinic, public;
\c polyclinic
-- ddl-end --


SET check_function_bodies = false;
-- ddl-end --

-- object: polyclinic | type: SCHEMA --
-- DROP SCHEMA IF EXISTS polyclinic CASCADE;
CREATE SCHEMA polyclinic;
-- ddl-end --
ALTER SCHEMA polyclinic OWNER TO administrator;
-- ddl-end --

SET search_path TO pg_catalog,public,polyclinic;
-- ddl-end --

-- object: polyclinic.title | type: DOMAIN --
-- DROP DOMAIN IF EXISTS polyclinic.title CASCADE;
CREATE DOMAIN polyclinic.title AS varchar(45)
	CONSTRAINT check_title CHECK (VALUE = initcap(VALUE));
-- ddl-end --
ALTER DOMAIN polyclinic.title OWNER TO administrator;
-- ddl-end --

-- object: polyclinic.doctor | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.doctor CASCADE;
CREATE TABLE polyclinic.doctor (
	id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ,
	first_name polyclinic.title NOT NULL,
	second_name polyclinic.title NOT NULL,
	third_name polyclinic.title NOT NULL,
	ward_number smallint NOT NULL,
	name_speciality polyclinic.title,
	CONSTRAINT ward_number UNIQUE (ward_number),
	CONSTRAINT doctor_pk PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE polyclinic.doctor OWNER TO administrator;
-- ddl-end --

-- object: polyclinic.drag | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.drag CASCADE;
CREATE TABLE polyclinic.drag (
	id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ,
	drag_name varchar(100) NOT NULL,
	id_allergy bigint NOT NULL,
	CONSTRAINT drag_pk PRIMARY KEY (id),
	CONSTRAINT drag_uq UNIQUE (drag_name)
);
-- ddl-end --
ALTER TABLE polyclinic.drag OWNER TO administrator;
-- ddl-end --

-- object: polyclinic.allergy | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.allergy CASCADE;
CREATE TABLE polyclinic.allergy (
	id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ,
	allergy_prep varchar(100) NOT NULL,
	CONSTRAINT allergy_pk PRIMARY KEY (id),
	CONSTRAINT allergy_uq UNIQUE (allergy_prep)
);
-- ddl-end --
ALTER TABLE polyclinic.allergy OWNER TO administrator;
-- ddl-end --

-- object: polyclinic.patient | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.patient CASCADE;
CREATE TABLE polyclinic.patient (
	card_no varchar(7) NOT NULL,
	med_policy varchar(16) NOT NULL,
	passport varchar(10) NOT NULL,
	first_name polyclinic.title NOT NULL,
	second_name polyclinic.title NOT NULL,
	third_name polyclinic.title NOT NULL,
	CONSTRAINT patient_pk PRIMARY KEY (card_no),
	CONSTRAINT card_form CHECK (card_no ~ '[А-Я]{2}\d{4}[А-Я]{1}'),
	CONSTRAINT policy_form CHECK (med_policy ~ '\d{16}'),
	CONSTRAINT passport_form CHECK (passport ~ '\d{10}'),
	CONSTRAINT passport_uq UNIQUE (passport),
	CONSTRAINT med_policy_uq UNIQUE (med_policy)
);
-- ddl-end --
ALTER TABLE polyclinic.patient OWNER TO administrator;
-- ddl-end --

-- object: allergy_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.drag DROP CONSTRAINT IF EXISTS allergy_fk CASCADE;
ALTER TABLE polyclinic.drag ADD CONSTRAINT allergy_fk FOREIGN KEY (id_allergy)
REFERENCES polyclinic.allergy (id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: polyclinic.treatment | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.treatment CASCADE;
CREATE TABLE polyclinic.treatment (
	id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ,
	date_in date NOT NULL,
	date_out date,
	diagnosis varchar(120),
	symptom varchar(120) NOT NULL,
	id_doctor bigint NOT NULL,
	card_no_patient varchar(7) NOT NULL,
	CONSTRAINT treatment_pk PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE polyclinic.treatment OWNER TO administrator;
-- ddl-end --

-- object: doctor_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.treatment DROP CONSTRAINT IF EXISTS doctor_fk CASCADE;
ALTER TABLE polyclinic.treatment ADD CONSTRAINT doctor_fk FOREIGN KEY (id_doctor)
REFERENCES polyclinic.doctor (id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: patient_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.treatment DROP CONSTRAINT IF EXISTS patient_fk CASCADE;
ALTER TABLE polyclinic.treatment ADD CONSTRAINT patient_fk FOREIGN KEY (card_no_patient)
REFERENCES polyclinic.patient (card_no) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: polyclinic.check_allergy | type: FUNCTION --
-- DROP FUNCTION IF EXISTS polyclinic.check_allergy() CASCADE;
CREATE FUNCTION polyclinic.check_allergy ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	PARALLEL UNSAFE
	COST 100
	AS $$
DECLARE
	drag_group drag.id_allergy%TYPE;
	patient_allergy RECORD;
	allergy allergy.id%TYPE;
BEGIN
	SELECT pa.id_allergy  INTO patient_allergy
	FROM treatment t
		JOIN patient p ON p.card_no = t.card_no_patient
		JOIN patient_has_allergy pa ON p.card_no = pa.card_no_patient
	WHERE t.id = NEW.id_treatment;
	IF patient_allergy IS NOT NULL THEN		
		SELECT d.id_allergy INTO drag_group
		FROM drag d WHERE d.id = NEW.id_drag;			
		FOR allergy IN
				SELECT  a.id 
				FROM treatment t
					JOIN patient p ON p.card_no = t.card_no_patient
					JOIN patient_has_allergy pa ON p.card_no = pa.card_no_patient
					JOIN allergy a ON pa.id_allergy = a.id
				WHERE t.id = NEW.id_treatment
		LOOP
			IF drag_group = allergy THEN
				RAISE EXCEPTION 'У пациента аллергия на %!', (SELECT a.allergy_prep
														  												FROM allergy AS a
														  												WHERE a.id = allergy);
				EXIT;
			END IF;
		END LOOP;
	END IF;
	RETURN NEW;
END;

$$;
-- ddl-end --
ALTER FUNCTION polyclinic.check_allergy() OWNER TO administrator;
-- ddl-end --

-- object: polyclinic.treatment_has_drag | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.treatment_has_drag CASCADE;
CREATE TABLE polyclinic.treatment_has_drag (
	id_treatment bigint NOT NULL,
	id_drag bigint NOT NULL,
	CONSTRAINT treatment_has_drag_pk PRIMARY KEY (id_treatment,id_drag)
);
-- ddl-end --
ALTER TABLE polyclinic.treatment_has_drag OWNER TO administrator;
-- ddl-end --

-- object: treatment_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.treatment_has_drag DROP CONSTRAINT IF EXISTS treatment_fk CASCADE;
ALTER TABLE polyclinic.treatment_has_drag ADD CONSTRAINT treatment_fk FOREIGN KEY (id_treatment)
REFERENCES polyclinic.treatment (id) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: drag_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.treatment_has_drag DROP CONSTRAINT IF EXISTS drag_fk CASCADE;
ALTER TABLE polyclinic.treatment_has_drag ADD CONSTRAINT drag_fk FOREIGN KEY (id_drag)
REFERENCES polyclinic.drag (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE CASCADE;
-- ddl-end --

-- object: tg_treatment_drag | type: TRIGGER --
-- DROP TRIGGER IF EXISTS tg_treatment_drag ON polyclinic.treatment_has_drag CASCADE;
CREATE TRIGGER tg_treatment_drag
	BEFORE INSERT OR UPDATE OF id_treatment,id_drag
	ON polyclinic.treatment_has_drag
	FOR EACH ROW
	EXECUTE PROCEDURE polyclinic.check_allergy();
-- ddl-end --

-- object: polyclinic.speciality | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.speciality CASCADE;
CREATE TABLE polyclinic.speciality (
	name polyclinic.title NOT NULL,
	department_name polyclinic.title NOT NULL,
	CONSTRAINT speciality_pk PRIMARY KEY (name)
);
-- ddl-end --
ALTER TABLE polyclinic.speciality OWNER TO administrator;
-- ddl-end --

-- object: treatment_uq | type: CONSTRAINT --
-- ALTER TABLE polyclinic.treatment DROP CONSTRAINT IF EXISTS treatment_uq CASCADE;
ALTER TABLE polyclinic.treatment ADD CONSTRAINT treatment_uq UNIQUE (id_doctor,card_no_patient,date_in);
-- ddl-end --

-- object: idx_symptom | type: INDEX --
-- DROP INDEX IF EXISTS polyclinic.idx_symptom CASCADE;
CREATE INDEX idx_symptom ON polyclinic.treatment
USING btree
(
	symptom
);
-- ddl-end --

-- object: polyclinic.check_insert_date_treatment | type: FUNCTION --
-- DROP FUNCTION IF EXISTS polyclinic.check_insert_date_treatment() CASCADE;
CREATE FUNCTION polyclinic.check_insert_date_treatment ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	PARALLEL UNSAFE
	COST 100
	AS $$
DECLARE
	d_in treatment.date_in%TYPE;
	d_out treatment.date_out%TYPE;
BEGIN
	IF NEW.date_in > NEW.date_out THEN
		RAISE EXCEPTION 'Нельзя выписать пациента раньше чем приняли!';
	END IF;

	SELECT date_in, date_out INTO d_in, d_out
	FROM treatment 
	WHERE card_no_patient = NEW.card_no_patient AND date_in = (SELECT MAX(date_in) FROM treatment
																										WHERE card_no_patient = NEW.card_no_patient);
	IF d_in IS NOT NULL AND d_out IS NULL THEN
		RAISE EXCEPTION 'У пациента ещё не закончилось предыдущее лечение!';
	 ELSE
		IF NEW.date_in <= d_out THEN
			 RAISE EXCEPTION 'Дата поступления должна быть позже предыдущего лечения!';
		END IF;
	END IF;
	RETURN NEW;
END;
	
$$;
-- ddl-end --
ALTER FUNCTION polyclinic.check_insert_date_treatment() OWNER TO administrator;
-- ddl-end --

-- object: tg_insert_date_treatment | type: TRIGGER --
-- DROP TRIGGER IF EXISTS tg_insert_date_treatment ON polyclinic.treatment CASCADE;
CREATE TRIGGER tg_insert_date_treatment
	BEFORE INSERT 
	ON polyclinic.treatment
	FOR EACH ROW
	EXECUTE PROCEDURE polyclinic.check_insert_date_treatment();
-- ddl-end --

-- object: polyclinic.query_c | type: VIEW --
-- DROP VIEW IF EXISTS polyclinic.query_c CASCADE;
CREATE VIEW polyclinic.query_c
AS 

SELECT
   d.ward_number,
   MAX(DATE_PART('day', tr.date_out::timestamp - tr.date_in::timestamp)) AS days
FROM
   treatment tr JOIN doctor d ON tr.id_doctor = d.id
   GROUP BY d.ward_number;
-- ddl-end --
ALTER VIEW polyclinic.query_c OWNER TO administrator;
-- ddl-end --

-- object: polyclinic.query_a | type: VIEW --
-- DROP VIEW IF EXISTS polyclinic.query_a CASCADE;
CREATE VIEW polyclinic.query_a
AS 

SELECT
   d.first_name,
   d.second_name,
   d.third_name,
   tr.symptom,
       trunc((count(tr.id_doctor)::double precision / (date_part('year'::text, age(max(tr.date_out)::timestamp with time zone, min(tr.date_in)::timestamp with time zone)) * 12::double precision + date_part('month'::text, age(max(tr.date_out)::timestamp with time zone, min(tr.date_in)::timestamp with time zone))+1))::numeric, 2) AS avg_count_in_month
FROM
   treatment tr JOIN doctor d ON d.id = tr.id_doctor
   GROUP BY tr.id_doctor, tr.symptom, d.first_name, d.second_name, d.third_name;
-- ddl-end --
ALTER VIEW polyclinic.query_a OWNER TO administrator;
-- ddl-end --

-- object: speciality_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.doctor DROP CONSTRAINT IF EXISTS speciality_fk CASCADE;
ALTER TABLE polyclinic.doctor ADD CONSTRAINT speciality_fk FOREIGN KEY (name_speciality)
REFERENCES polyclinic.speciality (name) MATCH FULL
ON DELETE NO ACTION ON UPDATE CASCADE;
-- ddl-end --

-- object: polyclinic.query_b | type: VIEW --
-- DROP VIEW IF EXISTS polyclinic.query_b CASCADE;
CREATE VIEW polyclinic.query_b
AS 

SELECT
   pa.card_no,
   pa.first_name,
   pa.second_name,
   pa.third_name,
   d.name_speciality,
   COUNT(tr.id) AS freq
FROM
   patient pa 
		JOIN treatment tr ON tr.card_no_patient = pa.card_no
		JOIN doctor d ON tr.id_doctor = d.id
   GROUP BY pa.card_no, d.name_speciality;
-- ddl-end --
ALTER VIEW polyclinic.query_b OWNER TO administrator;
-- ddl-end --

-- object: idx_card_no | type: INDEX --
-- DROP INDEX IF EXISTS polyclinic.idx_card_no CASCADE;
CREATE INDEX idx_card_no ON polyclinic.treatment
USING btree
(
	card_no_patient
);
-- ddl-end --

-- object: idx_doctor | type: INDEX --
-- DROP INDEX IF EXISTS polyclinic.idx_doctor CASCADE;
CREATE INDEX idx_doctor ON polyclinic.treatment
USING btree
(
	id_doctor
);
-- ddl-end --

-- object: idx_first_name | type: INDEX --
-- DROP INDEX IF EXISTS polyclinic.idx_first_name CASCADE;
CREATE INDEX idx_first_name ON polyclinic.doctor
USING btree
(
	first_name
);
-- ddl-end --

-- object: idx_second_name | type: INDEX --
-- DROP INDEX IF EXISTS polyclinic.idx_second_name CASCADE;
CREATE INDEX idx_second_name ON polyclinic.doctor
USING btree
(
	second_name
);
-- ddl-end --

-- object: idx_third_name | type: INDEX --
-- DROP INDEX IF EXISTS polyclinic.idx_third_name CASCADE;
CREATE INDEX idx_third_name ON polyclinic.doctor
USING btree
(
	third_name
);
-- ddl-end --

-- object: idx_name_speciality | type: INDEX --
-- DROP INDEX IF EXISTS polyclinic.idx_name_speciality CASCADE;
CREATE INDEX idx_name_speciality ON polyclinic.doctor
USING btree
(
	name_speciality
);
-- ddl-end --

-- object: polyclinic.check_update_date_treatment | type: FUNCTION --
-- DROP FUNCTION IF EXISTS polyclinic.check_update_date_treatment() CASCADE;
CREATE FUNCTION polyclinic.check_update_date_treatment ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	PARALLEL UNSAFE
	COST 100
	AS $$
DECLARE
	d_in treatment.date_in%TYPE;
	d_out treatment.date_out%TYPE;
BEGIN
	IF NEW.date_out IS NOT NULL THEN		
		IF NEW.date_in > NEW.date_out THEN
			RAISE EXCEPTION 'Нельзя выписать пациента раньше чем приняли!';
		END IF;
		IF NEW.date_in != OLD.date_in THEN
			SELECT MAX(date_out) INTO d_out
			FROM treatment
			WHERE card_no_patient = NEW.card_no_patient AND date_in < OLD.date_in;
				IF NEW.date_in <= d_out THEN
					RAISE EXCEPTION 'Дата поступления должна быть позднее окончания предыдущего лечения %!', d_out;
				END IF;
		END IF;
		IF NEW.date_out != OLD.date_out THEN
			SELECT MIN(date_in) INTO d_in
			FROM treatment
			WHERE card_no_patient = NEW.card_no_patient AND date_in > OLD.date_in;
				IF NEW.date_out >= d_in THEN
					RAISE EXCEPTION 'Дата выписки должна быть раньше начала следующего лечения %!', d_in;
				END IF;
		END IF;
	ELSE
		RAISE EXCEPTION 'Дата выписки не определена!';
	END IF;
	RETURN NEW;
END;
	
$$;
-- ddl-end --
ALTER FUNCTION polyclinic.check_update_date_treatment() OWNER TO administrator;
-- ddl-end --

-- object: tg_update_date_treatment | type: TRIGGER --
-- DROP TRIGGER IF EXISTS tg_update_date_treatment ON polyclinic.treatment CASCADE;
CREATE TRIGGER tg_update_date_treatment
	BEFORE UPDATE
	ON polyclinic.treatment
	FOR EACH ROW
	EXECUTE PROCEDURE polyclinic.check_update_date_treatment();
-- ddl-end --

-- object: polyclinic.patient_has_allergy | type: TABLE --
-- DROP TABLE IF EXISTS polyclinic.patient_has_allergy CASCADE;
CREATE TABLE polyclinic.patient_has_allergy (
	card_no_patient varchar(7) NOT NULL,
	id_allergy bigint NOT NULL,
	CONSTRAINT patient_has_allergy_pk PRIMARY KEY (card_no_patient,id_allergy)
);
-- ddl-end --
ALTER TABLE polyclinic.patient_has_allergy OWNER TO administrator;
-- ddl-end --

-- object: patient_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.patient_has_allergy DROP CONSTRAINT IF EXISTS patient_fk CASCADE;
ALTER TABLE polyclinic.patient_has_allergy ADD CONSTRAINT patient_fk FOREIGN KEY (card_no_patient)
REFERENCES polyclinic.patient (card_no) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: allergy_fk | type: CONSTRAINT --
-- ALTER TABLE polyclinic.patient_has_allergy DROP CONSTRAINT IF EXISTS allergy_fk CASCADE;
ALTER TABLE polyclinic.patient_has_allergy ADD CONSTRAINT allergy_fk FOREIGN KEY (id_allergy)
REFERENCES polyclinic.allergy (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE CASCADE;
-- ddl-end --

-- object: grant_rawd_1010a76e3e | type: PERMISSION --
GRANT SELECT,INSERT,UPDATE,DELETE
   ON TABLE polyclinic.treatment
   TO doctor;
-- ddl-end --

-- object: grant_rawd_6f8b2c09c0 | type: PERMISSION --
GRANT SELECT,INSERT,UPDATE,DELETE
   ON TABLE polyclinic.treatment_has_drag
   TO doctor;
-- ddl-end --

-- object: "grant_U_880c6198c8" | type: PERMISSION --
GRANT USAGE
   ON SCHEMA polyclinic
   TO doctor;
-- ddl-end --

-- object: grant_r_02d0e0e1b5 | type: PERMISSION --
GRANT SELECT
   ON TABLE polyclinic.doctor
   TO doctor;
-- ddl-end --

-- object: grant_r_5b5f3c727f | type: PERMISSION --
GRANT SELECT
   ON TABLE polyclinic.patient
   TO doctor;
-- ddl-end --

-- object: grant_r_8efce5972d | type: PERMISSION --
GRANT SELECT
   ON TABLE polyclinic.drag
   TO doctor;
-- ddl-end --

-- object: grant_r_b6cede62ba | type: PERMISSION --
GRANT SELECT
   ON TABLE polyclinic.allergy
   TO doctor;
-- ddl-end --

-- object: grant_r_c5ac1a8f45 | type: PERMISSION --
GRANT SELECT
   ON TABLE polyclinic.speciality
   TO doctor;
-- ddl-end --


