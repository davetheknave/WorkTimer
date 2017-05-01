#!/usr/bin/python3

import datetime
import argparse

#getting arguments
parser = argparse.ArgumentParser(description="Create a timer")
parser.add_argument('-w',metavar='minutes',type=int,nargs='?',default=50,help="Work period, default 50")
parser.add_argument('-b',metavar='minutes',type=int,nargs='?',default=15,help="Break period, default 15")
parser.add_argument('-c',type=int,nargs='?',metavar='count',default=3,help="Number of work periods, default 3")
parser.add_argument('--start-time',nargs='?',default='',help="Format HH:MM in 24 time")
parser.add_argument('--notifier',action="store_true",help="Activates notification service")
args = parser.parse_args()
w = args.w
b = args.b
c = args.c*2
start = args.start_time
timer = args.notifier

def createList(work, rest, count, start):
    '''
    work, rest, count are integers for how long the periods are and how many work/break units to make in list
    start is the first time, as a datetime object
    '''
    if work < 0 or rest < 0:
        raise(ValueError("Work and rest cannot be negative"))

    #Setting up times
    workperiod = datetime.timedelta(minutes=w)
    breakperiod = datetime.timedelta(minutes=b)

    alltimes = [start]
    for i in range(c-1):
        if i % 2 == 0:
            addedtime = workperiod
        else:
            addedtime = breakperiod
        alltimes.append(alltimes[i]+addedtime)
    return alltimes

def printTimes(times):
    """
    Input list of datetime objects, and print a list of them, odd ones are work times, even are breaks
    """
    index = 0
    for i in times:
        i = i.strftime("%H:%M")
        if index % 2 == 0:
            print("Start Work:  " + i)
        else:
            print("Break:       " + i)
        index+=1

def startTimer(alltimes,startingNow):
    import gi
    gi.require_version('Notify','0.7')
    from gi.repository import Notify
    import time
    Notify.init("Timer")
    notifier = Notify.Notification().new("")

    def notifyAtTime(target,notifier,text):
        if target < datetime.datetime.now():
            raise(ValueError("Tried to create a notification in the past?"))
        delta = (target-datetime.datetime.now()).seconds
        time.sleep(delta)
        notifier.update("Timer",text)
        notifier.show()

    if not startingNow:
        timenow = datetime.datetime.now()
        if alltimes[0] < timenow.replace(second=0):
            alltimes = [i for i in alltimes if timenow < i]
            if len(alltimes) % 2 == 1:
                alltimes.pop()
            if len(alltimes) == 0:
                raise(ArithmeticError("Notifier cannot be started if work times have already occured"))
        else:
            time.sleep((alltimes[0] - datetime.datetime.now()).seconds)

    index = 0
    for i in alltimes:
        next = alltimes[index+1].strftime("%H:%M")
        if i == alltimes[0]:
            notifier.update("Timer", "Work until "+next)
            notifier.show()
        elif index % 2 == 0:
            notifyAtTime(i,notifier,"Work until "+next)
        else:
            notifyAtTime(i,notifier,"Rest until "+next)
        index+=1

if start == "":
    start = datetime.datetime.now().replace(second=0)
else:
    start = datetime.datetime.strptime(start,"%H:%M")
    d = datetime.date.today()
    start = start.replace(year=d.year, month=d.month, day=d.day)
alltimes = createList(w,b,c,start)
printTimes(alltimes)
if timer: startTimer(alltimes,not bool(args.start_time))
