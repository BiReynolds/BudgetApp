from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, DateField, RadioField,SelectField
from wtforms.validators import DataRequired, ValidationError
import sqlalchemy as sa
from BillScreen import db 
from BillScreen.models import Bill

class BillForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired()])
    amount = DecimalField('Amount', validators = [DataRequired()])
    nextDue = DateField('Next Due', validators = [DataRequired()])
    monthInc = IntegerField('Month Increment')
    weekInc = IntegerField('Week Increment')
    dayInc = IntegerField('Day Increment')
    submit = SubmitField('Add Bill')

    def validate_name(self, name):
        check = db.session.scalar(sa.select(Bill).where(Bill.name == name.data))
        if check is not None:
            raise ValidationError('There is already a bill with that name.  Please choose a different name')
        
class MonthlyBillForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators = [DataRequired()])
    dueDay = SelectField('Day of Month',choices=range(1,29))
    submit = SubmitField('Add Bill')

    def validate_name(self, name):
        check = db.session.scalar(sa.select(Bill).where(Bill.name == name.data))
        if check is not None:
            raise ValidationError('There is already a bill with that name.  Please choose a different name')
        
class WeeklyBillForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators = [DataRequired()])
    dueDay = RadioField('Day of Week',choices=[(0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')])
    submit = SubmitField('Add Bill')

    def validate_name(self, name):
        check = db.session.scalar(sa.select(Bill).where(Bill.name == name.data))
        if check is not None:
            raise ValidationError('There is already a bill with that name.  Please choose a different name')
        
class OneTimeBillForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired()])
    amount = DecimalField('Amount (for one time income, input a negative number)', validators = [DataRequired()])
    dueDate = DateField('Date')
    submit = SubmitField('Add One Time Expense')
        
class IncomeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators = [DataRequired()])
    nextPaid = DateField('Next Pay Date', validators = [DataRequired()])
    paySched = SelectField('Pay Schedule',choices = ['Weekly','Biweekly','Monthly'])
    submit = SubmitField('Add Income')

class EditBillForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators = [DataRequired()])
    nextDue = DateField('Next Due / Paid', validators = [DataRequired()])
    submit = SubmitField('Update')