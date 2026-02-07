-- PostgreSQL schema for Trend Intelligence Dashboard

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trend Items table
CREATE TABLE IF NOT EXISTS trend_items (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) UNIQUE NOT NULL,
    source_platform VARCHAR(50) NOT NULL,
    image_url VARCHAR(2048),
    submitted_by VARCHAR(255) NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Classification
    category VARCHAR(100),
    subcategory VARCHAR(100),
    colors JSONB,
    patterns JSONB,
    style_tags JSONB,
    price_point VARCHAR(50),

    -- Engagement metrics
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    engagement_rate NUMERIC(5, 2) DEFAULT 0.0,

    -- Scoring
    trend_score NUMERIC(8, 2) DEFAULT 0.0,
    velocity_score NUMERIC(8, 2) DEFAULT 0.0,
    cross_platform_score NUMERIC(8, 2) DEFAULT 0.0,

    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',

    -- AI Analysis
    ai_analysis_text TEXT,

    CONSTRAINT status_check CHECK (status IN ('active', 'archived', 'flagged'))
);

-- Indexes for trend_items
CREATE INDEX idx_trend_items_url ON trend_items(url);
CREATE INDEX idx_trend_items_source_platform ON trend_items(source_platform);
CREATE INDEX idx_trend_items_category ON trend_items(category);
CREATE INDEX idx_trend_items_status ON trend_items(status);
CREATE INDEX idx_trend_items_trend_score ON trend_items(trend_score DESC);
CREATE INDEX idx_trend_items_velocity_score ON trend_items(velocity_score DESC);
CREATE INDEX idx_trend_items_score_date ON trend_items(trend_score DESC, submitted_at DESC);
CREATE INDEX idx_trend_items_velocity_date ON trend_items(velocity_score DESC, submitted_at DESC);
CREATE INDEX idx_trend_items_category_status ON trend_items(category, status);

-- Trend Metrics History table
CREATE TABLE IF NOT EXISTS trend_metrics_history (
    id SERIAL PRIMARY KEY,
    trend_item_id INTEGER NOT NULL REFERENCES trend_items(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    trend_score NUMERIC(8, 2) DEFAULT 0.0
);

-- Indexes for metrics history
CREATE INDEX idx_metrics_history_trend_id ON trend_metrics_history(trend_item_id);
CREATE INDEX idx_metrics_history_date ON trend_metrics_history(trend_item_id, recorded_at);
CREATE INDEX idx_metrics_history_recorded_at ON trend_metrics_history(recorded_at DESC);

-- Mood Boards table
CREATE TABLE IF NOT EXISTS mood_boards (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(100),
    items JSONB DEFAULT '[]'::jsonb
);

-- Indexes for mood_boards
CREATE INDEX idx_mood_boards_created_by ON mood_boards(created_by);
CREATE INDEX idx_mood_boards_created_at ON mood_boards(created_at DESC);
CREATE INDEX idx_mood_boards_category ON mood_boards(category);

-- Trending Hashtags table
CREATE TABLE IF NOT EXISTS trending_hashtags (
    id SERIAL PRIMARY KEY,
    hashtag VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    mention_count INTEGER DEFAULT 0,
    growth_rate NUMERIC(8, 2) DEFAULT 0.0,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hashtag, platform)
);

-- Indexes for hashtags
CREATE INDEX idx_hashtags_hashtag ON trending_hashtags(hashtag);
CREATE INDEX idx_hashtags_platform ON trending_hashtags(platform);
CREATE INDEX idx_hashtags_growth ON trending_hashtags(growth_rate DESC, last_updated DESC);

-- Monitoring Targets table
CREATE TABLE IF NOT EXISTS monitoring_targets (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    value VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    added_by VARCHAR(255) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT type_check CHECK (type IN ('hashtag', 'account', 'keyword', 'color', 'style'))
);

-- Indexes for monitoring_targets
CREATE INDEX idx_monitoring_type ON monitoring_targets(type);
CREATE INDEX idx_monitoring_platform ON monitoring_targets(platform);
CREATE INDEX idx_monitoring_active ON monitoring_targets(active);
CREATE INDEX idx_monitoring_added_at ON monitoring_targets(added_at DESC);
CREATE INDEX idx_monitoring_active_platform ON monitoring_targets(active, platform);
CREATE INDEX idx_monitoring_type_value ON monitoring_targets(type, value);
