-- SQL schema for bot MVP
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE,
  name VARCHAR(200),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE faqs (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200),
  trigger_keywords TEXT,
  response TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  telegram_user_id BIGINT,
  username VARCHAR(200),
  message TEXT,
  is_handled BOOLEAN DEFAULT FALSE,
  assigned_to VARCHAR(200),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE staff_replies (
  id SERIAL PRIMARY KEY,
  conversation_id INTEGER,
  staff_username VARCHAR(200),
  reply_text TEXT,
  created_at TIMESTAMP DEFAULT now()
);
