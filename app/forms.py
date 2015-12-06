from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired

class LoginForm(Form):
	openid = StringField('openid', validators = [DataRequired()])

class TypeForm(Form):
    stock_type = SelectField('Label', 
        choices = [('Open', 'Opening Price'), ('Close','Closing Price'), 
            ('Adj. Close','Adjusted Closing Price'), ('Low', 'Low Price')]) 

class RangeForm(Form):
    date_type = SelectField('Label', 
        choices = [('1M', '1 month'), ('6M','6 Months'), 
            ('1Y','1 year'), (None, 'All')]) 
