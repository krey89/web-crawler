import threading
from queue import Queue
from spider import Spider
from domain import *
from general import *
#from PyQt4 import QtGui
# from tkinter import *
#
# root = Tk()
# topFrame = Frame(root)
# topFrame.pack()
# botFrame = Frame(root)
# botFrame.pack(side=BOTTOM)
#
# button1 = Button(topFrame,text="BT1",fg="red")
# button2 = Button(botFrame,text="BT2",fg="blue")
# button3 = Button(topFrame,text="BT3",fg="green")
# button4 = Button(botFrame,text="BT4",fg="purple")
#
# button1.pack(side=LEFT)
# button2.pack()
# button3.pack(side=RIGHT)
# button4.pack()
#
#
# root.mainloop()

PROJECT_NAME = 'directory'
HOMEPAGE = 'https://www.yoursite.com/'
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
EMAILS_FILE = PROJECT_NAME + '/emails.txt'
ERRORS_FILE = PROJECT_NAME + '/errors.txt'
NUMBER_OF_THREADS = 8
queue = Queue()
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)


# Create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue
def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()


# Each queued link is a new job
def create_jobs():
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)
    queue.join()
    crawl()


# Check if there are items in the queue, if so crawl them
def crawl():
    queued_links = file_to_set(QUEUE_FILE)
    if len(queued_links) > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()


create_workers()
crawl()

