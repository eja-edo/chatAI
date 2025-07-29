-- Xóa bảng phụ thuộc trước
DROP TABLE IF EXISTS message_intents;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS intents;
DROP TABLE IF EXISTS chat_sessions;
DROP TABLE IF EXISTS llm_calls;
DROP TABLE IF EXISTS users;


-- Table: users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL unique,
    email TEXT NOT NULL UNIQUE,
    hash_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: chat_sessions
CREATE TABLE chat_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
	summary JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- Table: messages
CREATE TABLE messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender TEXT CHECK (sender IN ('user', 'bot')) NOT NULL,
    content JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: intents
CREATE TABLE intents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Table: message_intents
CREATE TABLE message_intents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    intent_id UUID REFERENCES intents(id) ON DELETE CASCADE,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1)
);

-- Table: llm_calls (tuỳ chọn)
CREATE TABLE llm_calls (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model TEXT NOT NULL,
    prompt JSONB NOT NULL,
    response JSONB NOT NULL,
    called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


