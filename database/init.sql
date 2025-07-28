-- CulturalOS Database Schema
-- Initial database setup for PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE user_role AS ENUM ('consumer', 'enterprise', 'admin');
CREATE TYPE subscription_type AS ENUM ('free', 'premium', 'enterprise');
CREATE TYPE social_platform AS ENUM ('instagram', 'tiktok', 'spotify');
CREATE TYPE cultural_data_type AS ENUM ('post', 'story', 'music', 'interaction');
CREATE TYPE connection_status AS ENUM ('active', 'inactive', 'expired');
CREATE TYPE recommendation_type AS ENUM ('content', 'experience', 'challenge');
CREATE TYPE recommendation_status AS ENUM ('pending', 'accepted', 'dismissed');
CREATE TYPE enterprise_tier AS ENUM ('basic', 'professional', 'enterprise');
CREATE TYPE analytics_metric_type AS ENUM ('user_engagement', 'cultural_trends', 'platform_usage', 'diversity_metrics');

-- Users table with authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    passkey_credential TEXT, -- Passkey authentication data
    google_id VARCHAR(255), -- Google OAuth ID
    role user_role NOT NULL DEFAULT 'consumer',
    subscription_tier subscription_type NOT NULL DEFAULT 'free',
    privacy_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cultural profiles
CREATE TABLE cultural_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    diversity_score DECIMAL(5,2) DEFAULT 0.0,
    evolution_data JSONB DEFAULT '{}',
    influence_network JSONB DEFAULT '{}',
    blind_spots JSONB DEFAULT '[]',
    last_analysis TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Social media connections
CREATE TABLE social_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform social_platform NOT NULL,
    platform_user_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    connection_status connection_status DEFAULT 'active',
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cultural data points from social media
CREATE TABLE cultural_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform social_platform NOT NULL,
    data_type cultural_data_type NOT NULL,
    content JSONB NOT NULL,
    cultural_signals JSONB DEFAULT '{}',
    confidence_score DECIMAL(5,2) DEFAULT 0.0,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cultural evolution tracking
CREATE TABLE cultural_evolution (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    milestone_type VARCHAR(100) NOT NULL,
    cultural_shift DECIMAL(5,2) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    platforms social_platform[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cultural recommendations
CREATE TABLE cultural_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recommendation_type recommendation_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    confidence_score DECIMAL(5,2) NOT NULL,
    cultural_category VARCHAR(100),
    external_data JSONB DEFAULT '{}',
    status recommendation_status DEFAULT 'pending',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enterprise organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    subscription_tier enterprise_tier NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Team cultural analytics
CREATE TABLE team_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    team_name VARCHAR(255) NOT NULL,
    cultural_metrics JSONB NOT NULL,
    diversity_scores JSONB NOT NULL,
    trend_analysis JSONB NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Anonymized platform analytics
CREATE TABLE platform_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type analytics_metric_type NOT NULL,
    aggregated_data JSONB NOT NULL, -- No individual user data
    demographic_breakdown JSONB DEFAULT '{}', -- Anonymized demographics
    time_period DATERANGE NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System health metrics
CREATE TABLE system_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    metrics JSONB NOT NULL,
    alerts JSONB DEFAULT '[]',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_cultural_profiles_user_id ON cultural_profiles(user_id);
CREATE INDEX idx_social_connections_user_id ON social_connections(user_id);
CREATE INDEX idx_social_connections_platform ON social_connections(platform);
CREATE INDEX idx_cultural_data_points_user_id ON cultural_data_points(user_id);
CREATE INDEX idx_cultural_data_points_platform ON cultural_data_points(platform);
CREATE INDEX idx_cultural_evolution_user_id ON cultural_evolution(user_id);
CREATE INDEX idx_cultural_recommendations_user_id ON cultural_recommendations(user_id);
CREATE INDEX idx_team_analytics_org_id ON team_analytics(organization_id);
CREATE INDEX idx_platform_analytics_metric_type ON platform_analytics(metric_type);
CREATE INDEX idx_system_health_service ON system_health(service_name);

-- Insert sample data for development
INSERT INTO users (email, role, subscription_tier) VALUES 
('admin@culturalOS.com', 'admin', 'enterprise'),
('enterprise@example.com', 'enterprise', 'enterprise'),
('consumer@example.com', 'consumer', 'free');

-- Insert sample organization
INSERT INTO organizations (name, domain, subscription_tier) VALUES 
('Example Corp', 'example.com', 'professional');