import urllib.request
import sqlite3
import dbmanager
import time

def notify_all(post_data, tasklist):
    if len(tasklist) == 0:
        return
    failed_list = []
    post_data = urllib.parse.urlencode(post_data)
    post_data = post_data.encode('utf-8')
    for i in tasklist:
        try:
            if i['failed_count'] > 0:
                failed_list.append(i)  # 链接坏的，降低优先级，直接扔到失败列表等15秒再发
                continue
            http_post(i['post_url'], post_data)
        except Exception:
            failed_list.append(i)
    retry = 0
    last_sleep_time = 15
    time.sleep(last_sleep_time)
    while True:
        if len(failed_list) == 0:
            return
        success_list = []
        for i in range(0, len(failed_list)):
            now_task = failed_list[i]
            try:
                http_post(now_task['post_url'], post_data)
                success_list.append(i)
                if now_task['failed_count'] > 0:
                    dbmanager.db.set_failed_count(now_task['key_id'], 0)
            except Exception as e:
                pass
        if retry >= 10: # 最多重试10次，超过10次则不再尝试发送
            groupConfigDB = sqlite3.connect('api.db')
            c = groupConfigDB.cursor()
            for i in failed_list:
                if i['failed_count'] >= 20: # 当连续失败20次时，从数据库删除，不再发送到这个服务器
                    c.execute('DELETE FROM PostAccess WHERE KeyID = ?', (i['key_id'],))
                else:
                    c.execute('UPDATE PostAccess SET FailedCount = ? WHERE KeyID = ?', (i['failed_count']+1, i['key_id']))
            c.close()
            groupConfigDB.commit()
            groupConfigDB.close()
            return
        for i in success_list:
            del failed_list[i] # 从未成功发送列表里删去已经成功发送的
            success_list = []
        # 休眠一段时间再继续，起步15秒，每失败一次时间乘2
        retry += 1
        last_sleep_time = last_sleep_time*2
        time.sleep(last_sleep_time)

def http_post(url, post_data):
    request = urllib.request.Request(url)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=utf-8')
    request.add_header('User-Agent', 'CN-BlackList-Post-API/0.1')
    recv_content = urllib.request.urlopen(request, post_data, timeout = 5)
    return recv_content
