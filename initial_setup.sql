CREATE TABLE IF NOT EXISTS repositories (
    repo_id SERIAL PRIMARY KEY,
    repo VARCHAR(255) NOT NULL UNIQUE,
    position_cur INT NOT NULL,
    position_prev INT NOT NULL,
    owner VARCHAR(255) NOT NULL,
    stars INT NOT NULL,
    watchers INT NOT NULL,
    forks INT NOT NULL,
    open_issues INT NOT NULL,
    language VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS commits (
    commit_id SERIAL PRIMARY KEY,
    sha VARCHAR(255) NOT NULL UNIQUE,
    repo_id INT NOT NULL,
    author_id INT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (repo_id) REFERENCES repositories (repo_id),
    FOREIGN KEY (author_id) REFERENCES authors (author_id)
);

CREATE INDEX IF NOT EXISTS idx_repositories_stars ON repositories (stars);
