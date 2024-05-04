from datetime import date,timedelta
from pathlib import Path
import matplotlib.pyplot as plt
from flask import render_template, session, redirect, request, url_for
import sqlalchemy as sa 
import sqlalchemy.orm as so 
from BillScreen import app 
from BillScreen.forms import BillForm, MonthlyBillForm, WeeklyBillForm, IncomeForm, OneTimeBillForm
from BillScreen.models import Bill
from BillScreen import db 

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        form = request.form
        paidBills = db.session.query(Bill).where(Bill.id.in_([int(key) for key in form.keys() if key.isnumeric()])).all()
        for bill in paidBills:
            bill.markPaid(database=db)
        db.session.commit()
        bills = db.session.query(Bill).order_by(Bill.nextDue).all()
        getBalance(float(form['balance']),date(date.today().year+1,date.today().month,date.today().day),bills,session)
        makePlots(session['dateList'],session['balList'])
        return redirect('/index')
    bills = db.session.query(Bill).order_by(Bill.nextDue).all()
    try:
        return render_template('index.html', bills = bills,adjBal = session['adjBal'], min30 = session['min30'],
                            min60=session['min60'],min90=session['min90'])
    except:
        return render_template('index.html', bills = bills, adjBal = 0, min30=0, min60=0, min90=0)

@app.route('/addMonthlyBill', methods = ['GET','POST'])
def addMonthlyBill():
    form = MonthlyBillForm()    
    if form.validate_on_submit():
        new_bill = Bill(name=form.name.data, amount=round(form.amount.data,2), nextDue = date(date.today().year,date.today().month,int(form.dueDay.data)),monthInc=1)
        db.session.add(new_bill)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addMonthlyBill.html',form = form)

@app.route('/addWeeklyBill', methods = ['GET','POST'])
def addWeeklyBill():
    form = WeeklyBillForm()    
    if form.validate_on_submit():
        new_bill = Bill(name=form.name.data, amount=round(form.amount.data,2), nextDue = date.today()+timedelta(int(form.dueDay.data)-date.today().weekday()),dayInc=7)
        db.session.add(new_bill)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addWeeklyBill.html',form = form)

@app.route('/addIncome', methods=['GET','POST'])
def addIncome():
    form = IncomeForm()
    if form.validate_on_submit():
        if form.paySched.data == 'Weekly':
            new_income = Bill(name=form.name.data, amount=-1*round(form.amount.data,2), nextDue=form.nextPaid.data, dayInc=7)
        elif form.paySched.data == 'Biweekly':
            new_income = Bill(name=form.name.data, amount=-1*round(form.amount.data,2), nextDue=form.nextPaid.data, dayInc=14)
        elif form.paySched.data == 'Monthly':
            new_income = Bill(name=form.name.data, amount=-1*round(form.amount.data,2), nextDue=form.nextPaid.data, monthInc = 1)
        db.session.add(new_income)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addIncome.html',form = form)

@app.route('/addOneTime', methods = ['GET','POST'])
def addOneTime():
    form = OneTimeBillForm()
    if form.validate_on_submit():
        new_bill = Bill(name = form.name.data, amount = round(form.amount.data,2), nextDue = form.dueDate.data, monthInc = -1)
        db.session.add(new_bill)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addOneTime.html', form = form)

@app.route('/addBill', methods = ['GET','POST'])
def addBill():
    form = BillForm()
    if form.validate_on_submit():
        new_bill = Bill(name = form.name.data, amount = form.amount.data, nextDue = form.nextDue.data, monthInc = form.monthInc.data, dayInc = 7*form.weekInc.data + form.dayInc.data)
        db.session.add(new_bill)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addBill.html', form = form)

@app.route('/delete/<id>')
def delete(id):
    user = db.session.query(Bill).where(Bill.id==id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/updateForecast')
def updateForecast():
    balance = 1000
    thruDate = date(date.today().year+1,date.today().month,date.today().day)
    bills = db.session.query(Bill)
    dates,balances = getBalance(balance,thruDate,bills)
    db.session.close()
    makePlots(dates,balances)
    return redirect(url_for('index'))

def getBalance(startBal, thruDate, bills,session):
    if len(bills)==0:
        session['dateList'] = [date.today()]
        session['balList'] = [startBal]
        session['adjBal'] = startBal
        session['min30'] = 0
        session['min60'] = 0
        session['min90'] = 0
        return session
    currDate = date.today()
    currBal = startBal
    dateList = []
    balList = []
    while currDate < thruDate:
        dateList.append(currDate)
        dueBills = [bill for bill in bills if bill.nextDue<=currDate]
        for bill in dueBills:
            currBal -= bill.amount
            bill.markPaid()
        balList.append(currBal)
        currDate += timedelta(days=1)
    session['dateList'] = dateList
    session['balList'] = balList
    session['adjBal'] = round(balList[0],2)
    session['min30'] = round(min(balList[0:30]),2)
    session['min60'] = round(min(balList[30:60]),2)
    session['min90'] = round(min(balList[60:90]),2)
    return session

def makePlots(dates,balances):
    fig1,ax1 = plt.subplots()
    fig3,ax3 = plt.subplots()
    ax1.plot(dates,balances)
    ax3.plot(dates,[min(balances[i:]) for i in range(len(balances))])
    fig1.savefig(Path.cwd() / "BillScreen" / "static" / "forecastImg.svg",format="svg")
    fig3.savefig(Path.cwd() / "BillScreen" / "static" / "futureForecastImg.svg",format="svg")