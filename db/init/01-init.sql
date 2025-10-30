-- Create application roles (dev defaults)
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT FROM pg_catalog.pg_roles WHERE rolname = 'auth_user') THEN
		CREATE ROLE auth_user LOGIN PASSWORD 'postgres';
	END IF;
	IF NOT EXISTS (
		SELECT FROM pg_catalog.pg_roles WHERE rolname = 'orders_user') THEN
		CREATE ROLE orders_user LOGIN PASSWORD 'postgres';
	END IF;
	IF NOT EXISTS (
		SELECT FROM pg_catalog.pg_roles WHERE rolname = 'billing_user') THEN
		CREATE ROLE billing_user LOGIN PASSWORD 'postgres';
	END IF;
END$$;

-- Create databases owned by respective roles
-- Note: entrypoint runs this only on first init, so IF NOT EXISTS is not required
CREATE DATABASE auth_db OWNER auth_user;
CREATE DATABASE orders_db OWNER orders_user;
CREATE DATABASE billing_db OWNER billing_user;

-- Adjust schema ownership and basic privileges
\connect auth_db
ALTER SCHEMA public OWNER TO auth_user;
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

\connect orders_db
ALTER SCHEMA public OWNER TO orders_user;
GRANT ALL PRIVILEGES ON DATABASE orders_db TO orders_user;

\connect billing_db
ALTER SCHEMA public OWNER TO billing_user;
GRANT ALL PRIVILEGES ON DATABASE billing_db TO billing_user;
