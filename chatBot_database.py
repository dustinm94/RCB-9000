import sqlite3
import json
from datetime import datetime

'''sql transaction is used because of the large size of the data set.
avoids creating rows one by one.'''

timeframe = '2015-05'
sql_transaction = []

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()

def create_table():
    c.execute("""CREATE TABLE IF NOT EXISTS parent_reply
(parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT, 
comment TEXT, subreddit TEXT, unix INT, score INT)""")

def format_data(data):
    '''replacing newlines in our reddit data, this makes tokenizing things much easier
    \n will be two separate entities when tokenized. Newline characters stay together'''
    data = data.replace("\n", " newlinechar ").replace("\r"," newlinechar ").replace('"', "'")
    return data

def find_parent(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(parent_id)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0] #Zero due to only selecting one comment.
        else:
            return False
    except Exception as e:
        print("find_parent", e)
        return False



if __name__ == "__main__":
    create_table()
    row_counter = 0
    paired_rows = 0 #tells me how many parent/child pairs exist

    with open("C:/Users/Dustin/PythonProjects/chatBot/reddit_comments/RC_{}".format(timeframe.split('-')[0], timeframe), buffer = 1000) as f:
        for row in f:
            row_counter += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']

            parent_data = find_parent(parent_id)


