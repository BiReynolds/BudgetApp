from datetime import date,timedelta
from typing import Optional
import sqlalchemy as sa 
import sqlalchemy.orm as so 
from BillScreen import db 

class Bill(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key = True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index = True, unique = True)
    amount: so.Mapped[float] = so.mapped_column(sa.Float(8))
    nextDue: so.Mapped[date] = so.mapped_column(index = True)
    monthInc: so.Mapped[int] = so.mapped_column(sa.Integer(), default = 0)
    dayInc: so.Mapped[int] = so.mapped_column(sa.Integer(),default = 0)

    def __repr__(self):
        return '<Bill {}>'.format(self.name)
    
    def markPaid(self, database = None):
        if self.monthInc != 0: 
            if self.monthInc == -1:
                if database:
                    db.session.delete(self)
                else:
                    self.nextDue += timedelta(days=400)
            elif self.nextDue.month == 12:
                self.nextDue = date(self.nextDue.year + 1, 1, self.nextDue.day)
            else:
                self.nextDue = date(self.nextDue.year, self.nextDue.month + 1, self.nextDue.day)
        self.nextDue += timedelta(days = self.dayInc)