from datetime import date,timedelta
from pathlib import Path
import matplotlib.pyplot as plt
from flask import render_template, session, redirect, request, url_for
import sqlalchemy as sa 
import sqlalchemy.orm as so 
from BillScreen import app 
from BillScreen.forms import BillForm, MonthlyBillForm, WeeklyBillForm, IncomeForm, OneTimeBillForm, EditBillForm
from BillScreen.models import Bill
from BillScreen import db 


## Routes

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        form = request.form
        paidBills = db.session.query(Bill).where(Bill.id.in_([int(key) for key in form.keys() if key.isnumeric()])).all()
        for bill in paidBills:
            bill.markPaid(database=db)
        db.session.commit()
        if float(form['balance'])==0:
            try:
                curBal = session['curBal']
            except:
                curBal = 0
                session['curBal']=0
        else:
            curBal = float(form['balance'])
        bills = db.session.query(Bill).order_by(Bill.nextDue).all()
        getBalance(curBal,date(date.today().year+1,date.today().month,date.today().day),bills,session)
        makePlots(session['dateList'],session['balList'])
        return redirect('/index')
    bills = db.session.query(Bill).order_by(Bill.nextDue).all()
    try:
        return render_template('index.html', bills = bills,curBal = session['curBal'], adjBal = session['adjBal'], min30 = session['min30'],
                            min60=session['min60'],min90=session['min90'],tableDates = session['tableDates'], tableBals = session['tableBals'])
    except:
        return render_template('index.html', bills = bills, curBal = 0, adjBal = 0, min30=0, min60=0, min90=0)

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
            new_income = Bill(name=form.name.data, amount=-1*round(form.amount.data,2), nextDue=form.nextDue.data, dayInc=7)
        elif form.paySched.data == 'Biweekly':
            new_income = Bill(name=form.name.data, amount=-1*round(form.amount.data,2), nextDue=form.nextDue.data, dayInc=14)
        elif form.paySched.data == 'Monthly':
            new_income = Bill(name=form.name.data, amount=-1*round(form.amount.data,2), nextDue=form.nextDue.data, monthInc = 1)
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

@app.route('/edit/<id>',methods = ['GET','POST'])
def edit(id):
    editBill = db.session.query(Bill).where(Bill.id==id).first()
    monthInc = editBill.monthInc
    dayInc = editBill.dayInc
    if monthInc < 0:
        payType = "One Time"
    elif monthInc == 0:
        if dayInc == 7:
            payType = "Weekly"
        elif dayInc%7 == 0:
            payType = f"Every {dayInc//7} Weeks"
        else:
            payType = f"Every {dayInc} Days"
    elif monthInc == 1:
        payType = "Monthly"
    elif dayInc == 0:
        payType = f"Every {monthInc} Months"
    else:
        payType = f"Every {monthInc} Months and {dayInc} Days"
    form = EditBillForm(obj=editBill)
    if form.validate_on_submit():
        form.populate_obj(editBill)
        db.session.commit()
        return redirect(url_for('edit',id = editBill.id))
    db.session.flush()
    return render_template('editBill.html',form=form, payType=payType, billId=id)


@app.route('/delete/<id>')
def delete(id):
    bill = db.session.query(Bill).where(Bill.id==id).first()
    db.session.delete(bill)
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


## Helper Functions

def getBalance(startBal, thruDate, bills,session):
    if len(bills)==0:
        session['dateList'] = [date.today()]
        session['balList'] = [startBal]
        session['tableDates'] = [date.today().isoformat()]
        session['tableBals'] = [startBal]
        session['curBal'] = startBal
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
    session['tableDates'] = [day.isoformat() for day in dateList[0:30]]
    session['tableBals'] = balList[0:30]
    session['curBal'] = startBal
    session['adjBal'] = round(balList[0],2)
    session['min30'] = round(min(balList[0:30]),2)
    session['min60'] = round(min(balList[30:60]),2)
    session['min90'] = round(min(balList[60:90]),2)
    return session

def makePlots(dates,balances):
    datalen=len(dates)
    fig1,ax1 = plt.subplots()
    fig2,ax2 = plt.subplots()
    fig3,ax3 = plt.subplots()
    fig4,ax4 = plt.subplots()
    ax1.plot(dates,balances)
    ax2.plot(dates,[min(balances[i:]) for i in range(datalen)])
    ax3.plot(dates[0:min(datalen,30)],balances[0:min(datalen,30)])
    ax4.plot(dates[0:min(datalen,90)],balances[0:min(datalen,90)])
    fig1.savefig(Path.cwd() / "BillScreen" / "static" / "forecastImg.svg",format="svg")
    fig2.savefig(Path.cwd() / "BillScreen" / "static" / "futureForecastImg.svg",format="svg")
    fig3.savefig(Path.cwd() / "BillScreen" / "static" / "next30.svg",format="svg")
    fig4.savefig(Path.cwd() / "BillScreen" / "static" / "next90.svg",format="svg")