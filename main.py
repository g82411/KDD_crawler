#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import email
import os
os.chdir(os.path.abspath(__file__))
from ConfigParser import RawConfigParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from time import strptime
from datetime import timedelta
from time import mktime
from datetime import datetime
import smtplib
import sys
reload(sys)
sys.setdefaultencoding("utf8")
config = RawConfigParser()
config.read("setting.ini")
def sentNews(subject,news):
    msg = MIMEMultipart()
    mailfrom = config.get("Common","sender")
    mailto = config.get("Common","recipient")
    msg["From"] = mailfrom
    msg["To"] = mailto
    msg["Subject"] = subject
    content = """
    <div>
    <table cellpadding="3px" border="1px" style="width: 90%; table-layout: fixed;">
    <tbody>
    <tr>
    <th>Title</th>
    <th>LastUpdate</th>
    <th>Comments</th>
    </tr>
    """
    for n in news:
        content += "<tr><td><a href=\"{0}\">{1}</a></td><td>{2}</td><td>{3}</td></tr>".format(n["href"],n["title"],n["lastupdate"],n["count"]).encode("utf-8")
    content += "</tbody></table></div>"
    mime_text = MIMEText(content,"html","utf-8")
    msg.attach(mime_text)
    smtp = smtplib.SMTP(config.get("SmtpServer"))
    smtp.ehlo()
    smtp.sendmail(mailfrom, mailto.split(","), msg.as_string())
    smtp.quit()
def sentError(subject,content):
    msg = MIMEMultipart()
    mailfrom = config.get("Common","sender")
    mailto = config.get("Common","recipient")
    msg["From"] = mailfrom
    msg["To"] = mailto
    msg["Subject"] = subject
    mime_text = MIMEText(content,"html","utf-8")
    msg.attach(mime_text)
    smtp = smtplib.SMTP(config.get("Common","SmtpServer"))
    smtp.ehlo()
    smtp.sendmail(mailfrom, mailto.split(","), msg.as_string())
    smtp.quit()


if __name__ == "__main__":
    last_time = datetime.now() - timedelta(days=int(config.get("Common","delta")))
    news = []
    for i in xrange(1,3):
        forms = requests.get("https://tianchi.aliyun.com/race/gitlab/posts/listOfType?raceId=231597&type=NOTES%2CISSUES&pageIndex={0}".format(i)).json()
        if(forms["errCode"] == 0):
            for article in forms["data"]["data"]:
                lastUpdate = article["gmtComment"] if article["gmtComment"] else article["gmtModified"]
                lastUpdate = strptime(lastUpdate,"%Y-%m-%d %H:%M:%S")
                lastUpdate = datetime.fromtimestamp(mktime(lastUpdate))
                if lastUpdate > last_time:
                    href = "https://tianchi.aliyun.com/competition/new_detail.html?raceId=231597&postsId={0}&from=part".format(article["id"])
                    title = article["title"]
                    count = article["commentCount"]
                    result = {"href":href,"title":title,"count":count,"lastupdate":lastUpdate}
                    news.append(result)
                else:
                    pass
        else:
            sentError("KDD news error","Error code:{0}".format(forms["errCode"]))
    sentNews("KDD News",news)









