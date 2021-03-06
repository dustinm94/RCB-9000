
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

def find_existing_score(pid):
    '''choosing comments that only have a certain score (number of upvotes)'''
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception as e:
        return False

def acceptable(data):
    '''Used to find data we actually want.'''
    if len(data.split(' ')) > 50 or len(data) < 1:
        return False
    elif len(data) > 1000:
        return False
    elif data == '[deleted]' or data == '[removed]':
        return False
    else:
        return True

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

def transaction_bldr(sql):
    global sql_transaction
    sql_transaction.append(sql)
    if len(sql_transaction) > 1000:
        c.execute('BEGIN TRANSACTION')
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()
        sql_transaction = []

def sql_insert_replace_comment(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        sql = """UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id =?;""".format(parentid, commentid, parent, comment, subreddit, int(time), score, parentid)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion', e)

def sql_insert_has_parent(commentid,parentid,parent,comment,subreddit,time,score):
    '''inserting new row where there is a parent ID. (inserting info about parent body)'''
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(parentid, commentid, parent, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion',str(e))


def sql_insert_no_parent(commentid,parentid,comment,subreddit,time,score):
    '''When there is no parent, and we want a parent id.'''
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}",{},{});""".format(parentid, commentid, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion',str(e))



if __name__ == "__main__":
    create_table()
    row_counter = 0
    paired_rows = 0 #tells me how many parent/child pairs exist

    with open("C:/Users/Dustin/PythonProjects/reddit_ChatBot/reddit_comments/{}/RC_{}".format(timeframe.split('-')[0], timeframe), buffering = 1000) as f:
        for row in f:
            row_counter += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            comment_id = row['name']
            subreddit = row['subreddit']
            parent_data = find_parent(parent_id)

            ''' chooses what we want in our database.'''
            if score >= 5:
                if acceptable(body):
                    existing_comment_score = find_existing_score(parent_id)
                    if existing_comment_score:
                        if score > existing_comment_score:
                            sql_insert_replace_comment(comment_id, parent_id,parent_data,body, subreddit, created_utc,score)
                    else:
                        if parent_data:
                            sql_insert_has_parent(comment_id, parent_id,parent_data,body,subreddit,created_utc,score)
                            paired_rows += 1
                        else:
                            sql_insert_no_parent(comment_id, parent_id, body, subreddit, created_utc, score)

            if row_counter % 100000 == 0:
                print("Total rows read: {}, Paired rows: {}, Time: {}".format(row_counter,paired_rows, str(datetime.now())))




