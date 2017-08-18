import sqlite3
import datetime

class DBManager:

    def __init__(self, cwd = None):
        if cwd == None:
            self.CWD = '/usr/local/postapi'
        else:
            self.CWD = cwd

    def get_post_list(self):
        groupConfigDB = sqlite3.connect(self.CWD+'/api.db')
        c = groupConfigDB.cursor()
        try:
            c.execute('SELECT KeyID, PostURL, FailedCount FROM PostAccess')
        except sqlite3.OperationalError:
            c.execute('CREATE TABLE `PostAccess` (`KeyID` INTEGER NOT NULL UNIQUE, `PostURL` INTEGER NOT NULL, `FailedCount` INTEGER NOT NULL DEFAULT 0);')
        data = c.fetchall()
        c.close()
        groupConfigDB.close()
        processed_list = []
        for i in data:
            processed_list.append({'key_id': i[0], 'post_url': i[1], 'failed_count': i[2]})
        return processed_list

    def set_failed_count(self, keyid, failed_count):
        groupConfigDB = sqlite3.connect(self.CWD+'/api.db')
        c = groupConfigDB.cursor()
        c.execute('UPDATE PostAccess SET FailedCount = ? WHERE KeyID = ?', (failed_count, keyid))
        c.close()
        groupConfigDB.commit()
        groupConfigDB.close()

    def add_post_task(self, keyid, post_url):
        groupConfigDB = sqlite3.connect(self.CWD+'/api.db')
        c = groupConfigDB.cursor()
        try:
            c.execute('SELECT KeyID FROM PostAccess WHERE KeyID = ?', (keyid,))
        except sqlite3.OperationalError:
            c.execute('CREATE TABLE `PostAccess` (`KeyID` INTEGER NOT NULL UNIQUE, `PostURL` INTEGER NOT NULL, `FailedCount` INTEGER NOT NULL DEFAULT 0);')
        have_rows = len(c.fetchall()) == 0
        c.close()
        c = groupConfigDB.cursor()
        if have_rows:
            c.execute('INSERT INTO PostAccess (KeyID, PostURL) VALUES (?,?)', (keyid, post_url))
        else:
            c.execute('UPDATE PostAccess SET PostURL = ? WHERE KeyID = ?', (post_url, keyid))
        c.close()
        groupConfigDB.commit()
        groupConfigDB.close()

    def remove_post_task(self, key_id):
        groupConfigDB = sqlite3.connect(self.CWD+'/api.db')
        c = groupConfigDB.cursor()
        c.execute('DELETE FROM PostAccess WHERE KeyID = ?', (key_id,))
        c.close()
        groupConfigDB.commit()
        groupConfigDB.close()
