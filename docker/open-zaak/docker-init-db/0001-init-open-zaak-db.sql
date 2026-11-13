CREATE USER openzaak;
-- Owner, so the user can create tables in the public schema (Postgres 15+)
CREATE DATABASE openzaak WITH OWNER openzaak;
