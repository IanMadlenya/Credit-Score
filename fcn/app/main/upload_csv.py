from flask import request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, ValidationError
from flask_paginate import Pagination
import pandas as pd
import numpy as np
class UploadForm(FlaskForm):
    csv_file = FileField('csv file')
    submit = SubmitField('import')
    loans=" "
    def validate_csv_file(self, field):
        if field.data.filename[-4:].lower() != '.csv':
            raise ValidationError('Invalid file extension')

    def csv_paginate(self,page):
    	global loans
    	search=False
    	PER_PAGE = 10
    	cols=loans.columns.values.tolist()
    	# pagination example
    	search = False
    	q = request.args.get('q')
    	print "print value"
    	print page
    	if q:
    		search = True
    	"""try:
    		page = int(request.args.get('page', 1))
    	except ValueError:
    		page = 1"""
    	pagination = Pagination(page=page,per_page=PER_PAGE, total=len(loans.index), search=search, record_name='loans',css_framework='foundation')
    	tables=loans[(page-1)*PER_PAGE:page*PER_PAGE][cols].to_html(classes='data')
    	return tables,pagination

    def show_tables(self,import_file_data,form):
        global loans
 
        loans=pd.read_csv(import_file_data,low_memory=False)
        features=list()
        features=['annual_inc','collection_recovery_fee','dti','emp_length_num','funded_amnt','grade','grade_num',
            'home_ownership','initial_list_status','inq_last_6mths','installment','int_rate','is_inc_v','last_delinq_none',
            'last_major_derog_none']
        loans['safe_loans'] = loans['bad_loans'].apply(lambda x : +1 if x==0 else -1)
        loans = loans.drop('bad_loans',axis=1)
        target = 'safe_loans'                    # prediction target (y) (+1 means safe, -1 is risky)
        # Extract the feature columns and target column
        loans = loans[features + [target]]
        loans=loans.dropna()
        print len(loans.columns)
               
        tables,pagination=self.csv_paginate(1)
        return tables,pagination,loans