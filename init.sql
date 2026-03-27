-- ============================================================
-- init.sql — Database initialisation script
-- MySQL runs this file automatically on first startup.
-- This creates our table so the app has somewhere to store tasks.
-- ============================================================

-- Use our database (created automatically by docker-compose env vars)
USE flaskdb;

-- Create the tasks table
-- IF NOT EXISTS = safe to run multiple times, won't error if table exists
CREATE TABLE IF NOT EXISTS tasks (
  id   INT AUTO_INCREMENT PRIMARY KEY,  -- unique ID, auto-increments (1, 2, 3...)
  name VARCHAR(255) NOT NULL,           -- the task description
  done BOOLEAN DEFAULT FALSE            -- is it completed? Default: no
);

-- Seed some example tasks so the app isn't empty on first run
INSERT INTO tasks (name, done) VALUES
  ('Set up AWS EC2 instance', FALSE),
  ('Install Docker on the server', FALSE),
  ('Configure Jenkins CI/CD pipeline', FALSE),
  ('Push first image to Docker Hub', FALSE);
