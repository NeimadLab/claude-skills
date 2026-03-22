-- OAF Memory Schema v1
-- Applied by: oaf init / MemoryStore.__init__

CREATE TABLE IF NOT EXISTS memory (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'hypothesis',
    content         TEXT NOT NULL,
    rationale       TEXT,
    actor           TEXT,
    session_id      TEXT,
    timestamp       TEXT NOT NULL,
    linked_files    TEXT DEFAULT '[]',
    linked_commits  TEXT DEFAULT '[]',
    tags            TEXT DEFAULT '[]'
);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    content, tags, content=memory, content_rowid=rowid
);

-- FTS5 sync triggers
CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON memory BEGIN
    INSERT INTO memory_fts(rowid, content, tags)
    VALUES (new.rowid, new.content, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, content, tags)
    VALUES ('delete', old.rowid, old.content, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS memory_au AFTER UPDATE ON memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, content, tags)
    VALUES ('delete', old.rowid, old.content, old.tags);
    INSERT INTO memory_fts(rowid, content, tags)
    VALUES (new.rowid, new.content, new.tags);
END;
