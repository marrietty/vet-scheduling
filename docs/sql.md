-- ============================================================================
-- Vet Clinic Scheduling Database Setup Script
-- Database: PostgreSQL (NeonDB)
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- DROP EXISTING TABLES (for clean setup)
-- ============================================================================
DROP TABLE IF EXISTS token_blacklist CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS pets CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS clinic_status CASCADE;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'pet_owner')),
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- PETS TABLE
-- ============================================================================
CREATE TABLE pets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(100),
    date_of_birth DATE,
    weight DECIMAL(5, 2), -- in kg, e.g., 30.50
    notes TEXT,
    medical_history JSONB DEFAULT '{}',
    last_vaccination TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for pets table
CREATE INDEX idx_pets_owner_id ON pets(owner_id);
CREATE INDEX idx_pets_species ON pets(species);

-- ============================================================================
-- APPOINTMENTS TABLE
-- ============================================================================
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('vaccination', 'routine', 'surgery', 'emergency')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed', 'scheduled')),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for appointments table
CREATE INDEX idx_appointments_pet_id ON appointments(pet_id);
CREATE INDEX idx_appointments_user_id ON appointments(user_id);
CREATE INDEX idx_appointments_start_time ON appointments(start_time);
CREATE INDEX idx_appointments_end_time ON appointments(end_time);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_time_range ON appointments(start_time, end_time);

-- ============================================================================
-- CLINIC STATUS TABLE
-- ============================================================================
CREATE TABLE clinic_status (
    id INTEGER PRIMARY KEY DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    status_message VARCHAR(500),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT single_row_constraint CHECK (id = 1)
);

-- Insert initial clinic status (single row table)
INSERT INTO clinic_status (id, status, status_message, updated_at) 
VALUES (1, 'open', 'Open from 8 AM to 6 PM', CURRENT_TIMESTAMP);

-- ============================================================================
-- TOKEN BLACKLIST TABLE (for secure logout)
-- ============================================================================
CREATE TABLE token_blacklist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    blacklisted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for token_blacklist table
CREATE INDEX idx_token_blacklist_token ON token_blacklist(token);
CREATE INDEX idx_token_blacklist_expires_at ON token_blacklist(expires_at);
CREATE INDEX idx_token_blacklist_user_id ON token_blacklist(user_id);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for pets table
CREATE TRIGGER update_pets_updated_at
    BEFORE UPDATE ON pets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for appointments table
CREATE TRIGGER update_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for clinic_status table
CREATE TRIGGER update_clinic_status_updated_at
    BEFORE UPDATE ON clinic_status
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Appointments with pet, owner, and booking user details
CREATE OR REPLACE VIEW appointments_detailed AS
SELECT 
    a.id AS appointment_id,
    a.start_time,
    a.end_time,
    a.service_type,
    a.status AS appointment_status,
    a.notes,
    a.created_at AS appointment_created_at,
    a.updated_at AS appointment_updated_at,
    p.id AS pet_id,
    p.name AS pet_name,
    p.species AS pet_species,
    p.breed AS pet_breed,
    owner.id AS owner_id,
    owner.full_name AS owner_name,
    owner.email AS owner_email,
    owner.phone AS owner_phone,
    booking_user.id AS booking_user_id,
    booking_user.full_name AS booking_user_name,
    booking_user.email AS booking_user_email
FROM appointments a
INNER JOIN pets p ON a.pet_id = p.id
INNER JOIN users owner ON p.owner_id = owner.id
INNER JOIN users booking_user ON a.user_id = booking_user.id;

-- View: Pets with owner details and vaccination status
CREATE OR REPLACE VIEW pets_detailed AS
SELECT 
    p.id AS pet_id,
    p.name AS pet_name,
    p.species,
    p.breed,
    p.date_of_birth,
    p.weight,
    p.medical_history,
    p.last_vaccination,
    CASE 
        WHEN p.last_vaccination IS NULL THEN 'unknown'
        WHEN p.last_vaccination < (CURRENT_TIMESTAMP - INTERVAL '1 year') THEN 'expired'
        ELSE 'valid'
    END AS vaccination_status,
    p.created_at AS pet_created_at,
    p.updated_at AS pet_updated_at,
    u.id AS owner_id,
    u.full_name AS owner_name,
    u.email AS owner_email,
    u.phone AS owner_phone
FROM pets p
INNER JOIN users u ON p.owner_id = u.id;


