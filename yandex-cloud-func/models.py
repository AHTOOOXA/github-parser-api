from abc import ABC, abstractmethod


class Model(ABC):
    @abstractmethod
    def to_db(self):
        raise NotImplementedError


class Repository(Model):
    def __init__(self, name, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language,
                 commits_url):
        self.name = name
        self.owner = owner
        self.position_cur = position_cur
        self.position_prev = position_prev
        self.stars = stars
        self.watchers = watchers
        self.forks = forks
        self.open_issues = open_issues
        self.language = language

        self.repo_id = None
        self.commits_url = commits_url

    def to_db(self):
        return (self.name,
                self.owner,
                self.position_cur,
                self.position_prev,
                self.stars,
                self.watchers,
                self.forks,
                self.open_issues,
                self.language)


class Author(Model):
    def __init__(self, name):
        self.name = name

    def to_db(self):
        return (self.name,)


class Commit(Model):
    def __init__(self, sha, repo_id, author_name, date):
        self.sha = sha
        self.repo_id = repo_id
        self.author_id = None
        self.author_name = author_name
        self.date = date

    def to_db(self):
        return (self.sha,
                self.repo_id,
                self.author_id,
                self.date)
