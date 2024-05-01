--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: check_grade_range(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_grade_range() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.grade < 1 OR NEW.grade > 5 THEN
        RAISE EXCEPTION 'Оценка должна находиться в диапазоне от 1 до 5';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_grade_range() OWNER TO postgres;

--
-- Name: check_valid_attendance_status(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_valid_attendance_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.status not IN ('Н', 'У', '+') THEN
        RAISE EXCEPTION 'Недопустимое значение для статуса посещения';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_valid_attendance_status() OWNER TO postgres;

--
-- Name: checklesson(integer, date, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.checklesson(grid integer, d date, sq integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN (SELECT 1 FROM groupattendance WHERE groupid = grId AND date = d AND num = sq);
END;
$$;


ALTER FUNCTION public.checklesson(grid integer, d date, sq integer) OWNER TO postgres;

--
-- Name: create_attendance_and_student_attendance(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.create_attendance_and_student_attendance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    attendance_record RECORD;
    student_id INTEGER;
BEGIN
    -- Создаем запись Attendance
    

    -- Создаем записи StudentAttendance для каждого студента в группе
    FOR student_id IN
        SELECT StudentID
        FROM Students
        WHERE GroupID = NEW.GroupID
    LOOP
		INSERT INTO Attendance (StudentID, Status)
		VALUES (student_id, 'Н')
		RETURNING AttendanceID INTO attendance_record;
		
        INSERT INTO StudentAttendance (AttendanceID, GroupAttendanceID)
        VALUES (attendance_record.AttendanceID, NEW.AttendanceID);
    END LOOP;

    RETURN NULL;
END;
$$;


ALTER FUNCTION public.create_attendance_and_student_attendance() OWNER TO postgres;

--
-- Name: delete_attendance_and_student_attendance(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_attendance_and_student_attendance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    attendance_record RECORD;
    staid INTEGER;
	aid INTEGER;
BEGIN
    -- Создаем запись Attendance
    

    -- Создаем записи StudentAttendance для каждого студента в группе
    FOR staid, aid IN
        SELECT studentattendanceid, attendanceid
        FROM StudentAttendance
		WHERE groupattendanceid = OLD.attendanceid
    LOOP
		DELETE FROM studentattendance WHERE studentattendanceid = staid;
		DELETE FROM attendance
		WHERE attendanceid = aid;
    END LOOP;

    RETURN OLD;
END;
$$;


ALTER FUNCTION public.delete_attendance_and_student_attendance() OWNER TO postgres;

--
-- Name: deletelesson(integer, date, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.deletelesson(grid integer, d date, sq integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM groupattendance WHERE groupid = grId AND date = d AND num = sq;
END;
$$;


ALTER FUNCTION public.deletelesson(grid integer, d date, sq integer) OWNER TO postgres;

--
-- Name: generate_student_id(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.generate_student_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    current_year INTEGER;
    student_count INTEGER;
    new_student_id VARCHAR(6);
BEGIN
    -- Получаем текущий год
    SELECT extract(YEAR FROM current_date) INTO current_year;

    -- Подсчитываем количество студентов в текущем году
    SELECT COUNT(*)
    INTO student_count
    FROM Students
    WHERE created_year = current_year;
	RAISE NOTICE 'Current year: %', current_year;
    -- Формируем уникальный номер студенческого билета
    new_student_id := to_char(current_date, 'YY') || to_char(student_count + 1, 'FM0000');

    -- Присваиваем сгенерированный номер студенческого билета новому студенту
    NEW.cardID := new_student_id;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.generate_student_id() OWNER TO postgres;

--
-- Name: get_attendance_info(integer, date, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_attendance_info(group_id integer, date_param date, num_param integer) RETURNS TABLE(attendanceid integer, firstname character varying, surname character varying, patronymic character varying, cardid character varying, status character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT a.attendanceid, a.firstname, a.surname, a.patronymic, a.cardid, a.status
    FROM attendance_info_view a
    WHERE date = date_param AND num = num_param AND groupid = group_id;
END;
$$;


ALTER FUNCTION public.get_attendance_info(group_id integer, date_param date, num_param integer) OWNER TO postgres;

--
-- Name: planlesson(integer, date, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.planlesson(grid integer, d date, sq integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO GroupAttendance(groupid, date, seq) VALUES (grId, d, sq);
END;
$$;


ALTER FUNCTION public.planlesson(grid integer, d date, sq integer) OWNER TO postgres;

--
-- Name: planlesson(integer, character varying, date, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.planlesson(grid integer, sub character varying, d date, sq integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO GroupAttendance(groupid, subject, date, num) VALUES (grId, sub, d, sq);
END;
$$;


ALTER FUNCTION public.planlesson(grid integer, sub character varying, d date, sq integer) OWNER TO postgres;

--
-- Name: update_attendance(integer, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_attendance(attendance_id_param integer, new_status_param character varying) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE attendance_info_view
    SET status = new_status_param
    WHERE attendanceid = attendance_id_param;
END;
$$;


ALTER FUNCTION public.update_attendance(attendance_id_param integer, new_status_param character varying) OWNER TO postgres;

--
-- Name: update_students_groups_on_delete(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_students_groups_on_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE Students SET GroupID = NULL WHERE GroupID = OLD.GroupID;
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.update_students_groups_on_delete() OWNER TO postgres;

--
-- Name: updateattendance(integer, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.updateattendance(id integer, new_status character varying) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE Attendance SET status = new_status WHERE AttendanceID = id;
END;
$$;


ALTER FUNCTION public.updateattendance(id integer, new_status character varying) OWNER TO postgres;

--
-- Name: updateattendance(character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.updateattendance(status character varying, id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE Attendance SET status = status WHERE AttendanceID = id;
END;
$$;


ALTER FUNCTION public.updateattendance(status character varying, id integer) OWNER TO postgres;

--
-- Name: updatelesson(integer, character varying, date, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.updatelesson(grid integer, sub character varying, d date, sq integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE groupattendance SET subject = sub WHERE groupID = grId AND date = d and num = sq;
END;
$$;


ALTER FUNCTION public.updatelesson(grid integer, sub character varying, d date, sq integer) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance (
    attendanceid integer NOT NULL,
    studentid integer,
    status character varying(15)
);


ALTER TABLE public.attendance OWNER TO postgres;

--
-- Name: attendance_attendanceid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_attendanceid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_attendanceid_seq OWNER TO postgres;

--
-- Name: attendance_attendanceid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_attendanceid_seq OWNED BY public.attendance.attendanceid;


--
-- Name: groupattendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groupattendance (
    attendanceid integer NOT NULL,
    groupid integer,
    date date,
    subject character varying(255),
    num integer
);


ALTER TABLE public.groupattendance OWNER TO postgres;

--
-- Name: studentattendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.studentattendance (
    studentattendanceid integer NOT NULL,
    attendanceid integer,
    groupattendanceid integer
);


ALTER TABLE public.studentattendance OWNER TO postgres;

--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    studentid integer NOT NULL,
    cardid character varying(6),
    firstname character varying(255),
    surname character varying(255),
    patronymic character varying(255),
    groupid integer,
    created_year integer DEFAULT EXTRACT(year FROM CURRENT_DATE)
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: attendance_info_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.attendance_info_view AS
 SELECT a.attendanceid,
    s.firstname,
    s.surname,
    s.patronymic,
    s.cardid,
    a.status,
    ga.date,
    ga.num,
    ga.groupid
   FROM (((public.studentattendance sa
     JOIN public.groupattendance ga ON ((ga.attendanceid = sa.groupattendanceid)))
     JOIN public.attendance a ON ((sa.attendanceid = a.attendanceid)))
     JOIN public.students s ON ((a.studentid = s.studentid)));


ALTER VIEW public.attendance_info_view OWNER TO postgres;

--
-- Name: grades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grades (
    gradeid integer NOT NULL,
    studentid integer,
    subject character varying(100) NOT NULL,
    grade integer,
    comment character varying(200)
);


ALTER TABLE public.grades OWNER TO postgres;

--
-- Name: grades_gradeid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grades_gradeid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.grades_gradeid_seq OWNER TO postgres;

--
-- Name: grades_gradeid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grades_gradeid_seq OWNED BY public.grades.gradeid;


--
-- Name: groupattendance_attendanceid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.groupattendance_attendanceid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.groupattendance_attendanceid_seq OWNER TO postgres;

--
-- Name: groupattendance_attendanceid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.groupattendance_attendanceid_seq OWNED BY public.groupattendance.attendanceid;


--
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    groupid integer NOT NULL,
    groupname character varying(50) NOT NULL
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- Name: groups_groupid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.groups_groupid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.groups_groupid_seq OWNER TO postgres;

--
-- Name: groups_groupid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.groups_groupid_seq OWNED BY public.groups.groupid;


--
-- Name: studentattendance_studentattendanceid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.studentattendance_studentattendanceid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.studentattendance_studentattendanceid_seq OWNER TO postgres;

--
-- Name: studentattendance_studentattendanceid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.studentattendance_studentattendanceid_seq OWNED BY public.studentattendance.studentattendanceid;


--
-- Name: students_studentid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_studentid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_studentid_seq OWNER TO postgres;

--
-- Name: students_studentid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_studentid_seq OWNED BY public.students.studentid;


--
-- Name: subject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subject (
    subjectid integer NOT NULL,
    subject character varying(150)
);


ALTER TABLE public.subject OWNER TO postgres;

--
-- Name: subject_subjectid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subject_subjectid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subject_subjectid_seq OWNER TO postgres;

--
-- Name: subject_subjectid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subject_subjectid_seq OWNED BY public.subject.subjectid;


--
-- Name: attendance attendanceid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance ALTER COLUMN attendanceid SET DEFAULT nextval('public.attendance_attendanceid_seq'::regclass);


--
-- Name: grades gradeid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades ALTER COLUMN gradeid SET DEFAULT nextval('public.grades_gradeid_seq'::regclass);


--
-- Name: groupattendance attendanceid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groupattendance ALTER COLUMN attendanceid SET DEFAULT nextval('public.groupattendance_attendanceid_seq'::regclass);


--
-- Name: groups groupid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups ALTER COLUMN groupid SET DEFAULT nextval('public.groups_groupid_seq'::regclass);


--
-- Name: studentattendance studentattendanceid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.studentattendance ALTER COLUMN studentattendanceid SET DEFAULT nextval('public.studentattendance_studentattendanceid_seq'::regclass);


--
-- Name: students studentid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN studentid SET DEFAULT nextval('public.students_studentid_seq'::regclass);


--
-- Name: subject subjectid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subject ALTER COLUMN subjectid SET DEFAULT nextval('public.subject_subjectid_seq'::regclass);


--
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance (attendanceid, studentid, status) FROM stdin;
51	8	Н
50	7	У
53	8	Н
54	7	Н
55	8	Н
56	7	Н
57	8	Н
52	7	У
\.


--
-- Data for Name: grades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.grades (gradeid, studentid, subject, grade, comment) FROM stdin;
\.


--
-- Data for Name: groupattendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.groupattendance (attendanceid, groupid, date, subject, num) FROM stdin;
33	1	2024-04-29	Русский язык	1
34	1	2024-05-01	Биология	2
36	1	2024-04-30	Русский язык	2
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.groups (groupid, groupname) FROM stdin;
1	БСБО-01-22
\.


--
-- Data for Name: studentattendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.studentattendance (studentattendanceid, attendanceid, groupattendanceid) FROM stdin;
47	50	33
48	51	33
49	52	34
50	53	34
53	56	36
54	57	36
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (studentid, cardid, firstname, surname, patronymic, groupid, created_year) FROM stdin;
7	240001	Иван	Иванов	Иванович	1	2024
8	240002	Артем	Артемов	Артемович	1	2024
\.


--
-- Data for Name: subject; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subject (subjectid, subject) FROM stdin;
1	Русский язык
2	Математика
3	Биология
\.


--
-- Name: attendance_attendanceid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_attendanceid_seq', 65, true);


--
-- Name: grades_gradeid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.grades_gradeid_seq', 12, true);


--
-- Name: groupattendance_attendanceid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.groupattendance_attendanceid_seq', 44, true);


--
-- Name: groups_groupid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.groups_groupid_seq', 1, true);


--
-- Name: studentattendance_studentattendanceid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.studentattendance_studentattendanceid_seq', 62, true);


--
-- Name: students_studentid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_studentid_seq', 8, true);


--
-- Name: subject_subjectid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subject_subjectid_seq', 3, true);


--
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (attendanceid);


--
-- Name: grades grades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT grades_pkey PRIMARY KEY (gradeid);


--
-- Name: groupattendance groupattendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groupattendance
    ADD CONSTRAINT groupattendance_pkey PRIMARY KEY (attendanceid);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (groupid);


--
-- Name: studentattendance studentattendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.studentattendance
    ADD CONSTRAINT studentattendance_pkey PRIMARY KEY (studentattendanceid);


--
-- Name: students students_cardid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_cardid_key UNIQUE (cardid);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (studentid);


--
-- Name: subject subject_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_pkey PRIMARY KEY (subjectid);


--
-- Name: groupattendance unique_group_lesson; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groupattendance
    ADD CONSTRAINT unique_group_lesson UNIQUE (num, date, groupid);


--
-- Name: attendance_info_view update_attendance_info_view; Type: RULE; Schema: public; Owner: postgres
--

CREATE RULE update_attendance_info_view AS
    ON UPDATE TO public.attendance_info_view DO INSTEAD  UPDATE public.attendance SET status = new.status
  WHERE (attendance.attendanceid = new.attendanceid);


--
-- Name: grades check_grade_range_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER check_grade_range_trigger BEFORE INSERT OR UPDATE ON public.grades FOR EACH ROW EXECUTE FUNCTION public.check_grade_range();


--
-- Name: attendance check_valid_attendance_status_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER check_valid_attendance_status_trigger BEFORE INSERT ON public.attendance FOR EACH ROW EXECUTE FUNCTION public.check_valid_attendance_status();


--
-- Name: groupattendance create_attendance_and_student_attendance_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER create_attendance_and_student_attendance_trigger AFTER INSERT ON public.groupattendance FOR EACH ROW EXECUTE FUNCTION public.create_attendance_and_student_attendance();


--
-- Name: groupattendance delete_attendance_and_student_attendance_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER delete_attendance_and_student_attendance_trigger BEFORE DELETE ON public.groupattendance FOR EACH ROW EXECUTE FUNCTION public.delete_attendance_and_student_attendance();


--
-- Name: students generate_student_id_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER generate_student_id_trigger BEFORE INSERT ON public.students FOR EACH ROW EXECUTE FUNCTION public.generate_student_id();


--
-- Name: groups update_students_groups_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_students_groups_trigger BEFORE DELETE ON public.groups FOR EACH ROW EXECUTE FUNCTION public.update_students_groups_on_delete();


--
-- Name: attendance attendance_studentid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_studentid_fkey FOREIGN KEY (studentid) REFERENCES public.students(studentid);


--
-- Name: attendance fk_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT fk_student FOREIGN KEY (studentid) REFERENCES public.students(studentid);


--
-- Name: grades fk_student_grades; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT fk_student_grades FOREIGN KEY (studentid) REFERENCES public.students(studentid);


--
-- Name: grades grades_studentid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT grades_studentid_fkey FOREIGN KEY (studentid) REFERENCES public.students(studentid);


--
-- Name: studentattendance studentattendance_attendanceid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.studentattendance
    ADD CONSTRAINT studentattendance_attendanceid_fkey FOREIGN KEY (attendanceid) REFERENCES public.attendance(attendanceid);


--
-- Name: studentattendance studentattendance_groupattendanceid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.studentattendance
    ADD CONSTRAINT studentattendance_groupattendanceid_fkey FOREIGN KEY (groupattendanceid) REFERENCES public.groupattendance(attendanceid) ON DELETE CASCADE;


--
-- Name: students students_groupid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_groupid_fkey FOREIGN KEY (groupid) REFERENCES public.groups(groupid);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO teacher;


--
-- Name: TABLE attendance; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.attendance TO student_role;
GRANT SELECT,INSERT,UPDATE ON TABLE public.attendance TO teacher_role;
GRANT ALL ON TABLE public.attendance TO teacher;
GRANT SELECT ON TABLE public.attendance TO student;


--
-- Name: SEQUENCE attendance_attendanceid_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.attendance_attendanceid_seq TO teacher;


--
-- Name: TABLE groupattendance; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.groupattendance TO student_role;
GRANT SELECT,INSERT,UPDATE ON TABLE public.groupattendance TO teacher_role;
GRANT ALL ON TABLE public.groupattendance TO teacher;
GRANT SELECT ON TABLE public.groupattendance TO student;


--
-- Name: TABLE studentattendance; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.studentattendance TO student_role;
GRANT SELECT,INSERT,UPDATE ON TABLE public.studentattendance TO teacher_role;
GRANT ALL ON TABLE public.studentattendance TO teacher;
GRANT SELECT ON TABLE public.studentattendance TO student;


--
-- Name: TABLE students; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.students TO student_role;
GRANT SELECT,INSERT,UPDATE ON TABLE public.students TO teacher_role;
GRANT ALL ON TABLE public.students TO teacher;
GRANT SELECT ON TABLE public.students TO student;


--
-- Name: TABLE attendance_info_view; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.attendance_info_view TO teacher;
GRANT SELECT ON TABLE public.attendance_info_view TO student;


--
-- Name: TABLE grades; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.grades TO student_role;
GRANT SELECT,INSERT,UPDATE ON TABLE public.grades TO teacher_role;
GRANT ALL ON TABLE public.grades TO teacher;
GRANT SELECT ON TABLE public.grades TO student;


--
-- Name: SEQUENCE grades_gradeid_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.grades_gradeid_seq TO teacher;


--
-- Name: SEQUENCE groupattendance_attendanceid_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.groupattendance_attendanceid_seq TO teacher;


--
-- Name: TABLE groups; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.groups TO student_role;
GRANT SELECT,INSERT,UPDATE ON TABLE public.groups TO teacher_role;
GRANT ALL ON TABLE public.groups TO teacher;
GRANT SELECT ON TABLE public.groups TO student;


--
-- Name: SEQUENCE groups_groupid_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.groups_groupid_seq TO teacher;


--
-- Name: SEQUENCE studentattendance_studentattendanceid_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.studentattendance_studentattendanceid_seq TO teacher;


--
-- Name: SEQUENCE students_studentid_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.students_studentid_seq TO teacher;


--
-- Name: TABLE subject; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.subject TO teacher;
GRANT SELECT ON TABLE public.subject TO student;


--
-- Name: SEQUENCE subject_subjectid_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.subject_subjectid_seq TO teacher;


--
-- PostgreSQL database dump complete
--

