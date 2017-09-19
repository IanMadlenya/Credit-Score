from flask_wtf import FlaskForm
import os
from wtforms import StringField, SelectField, BooleanField, SubmitField, RadioField, SelectMultipleField,DecimalField, FileField,ValidationError
from wtforms.validators import Required, Length
from wtforms_components import read_only


class NewModelForm(FlaskForm):
	modelname= StringField(u'Model Name',validators=[Required(), Length(1,20)])
	modelType = StringField(u'ML Task', default='Classification')
	method = SelectField(u'Method',default=None, choices=[('rdf', 'RDF'), ('gbt', 'GBT'),('pcb','PCB'),('svm','SVM')])
	automodel = BooleanField(u'Automodel',id='bool')
	identifier = SelectField(u'Class ID', default=None, choices=[])
	createModel = SubmitField('CreateModel')

	def __init__(self, *args, **kwargs):
		super(NewModelForm, self).__init__(*args, **kwargs)
		read_only(self.modelType)

class SelectModelForm(FlaskForm):
	csv_file = FileField('csv file')
	modelName= SelectField(u'Select Model', choices=[])
	probability_value= DecimalField(u'threshold', places=2,description='probability threshold value')
	analyze = SubmitField('Analyze')

	def validate_csv_file(self, field):
		if field.data.filename[-4:].lower() != '.csv':
			raise ValidationError('Invalid file extension')

