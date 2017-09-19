from flask import Flask, render_template, request
from flask_wtf import Form
from wtforms import FileField, SubmitField, ValidationError
import pandas as pd
import os
from flask_paginate import Pagination

#from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
import pickle
import random
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import precision_score,recall_score
import numpy as np
import app

class Createnewmodel():
	#app.config['MAX_CONTENT_LENGTH'] = 100* 1024 * 1024
	pd.set_option('display.float_format', lambda x:'%f'%x)

	def data_prepare(self,loans,modelname,target):
	    search=False
	    #loans.index +=1
	    target='safe_loans'

	    loans=pd.get_dummies(loans)
	    train_data,validation_data=train_test_split(loans,train_size=0.8)
	    train_target=train_data['safe_loans']
	    validation_target=validation_data['safe_loans']
	    train_features=train_data.drop('safe_loans',axis=1)
	    validation_features=validation_data.drop('safe_loans',axis=1)
	   
	    clf = RandomForestClassifier(n_jobs=2,max_depth=7,n_estimators=500)

	    clf.fit(train_features, train_target)
	    self.save_pickle_model(clf,modelname)


	    #validation_safe_loans = validation_data[validation_data[target] == 1]
	    #validation_risky_loans = validation_data[validation_data[target] == -1]
	    acc=100*round(self.accuracy(validation_target,clf.predict(validation_features)),2)
	    probability=clf.predict_proba(validation_features)
	    predictions_with_default_threshold = self.apply_threshold(probability[:,-1], 0.5)
	    predictions_with_high_threshold = self.apply_threshold(probability[:,-1], 0.9)
	    print "Number of positive predicted reviews (threshold = 0.9): %s" % (sum([x for x in predictions_with_high_threshold if x == 1]))
	    print "Number of positive predicted reviews (threshold = 0.5): %s" %(sum([x for x in predictions_with_default_threshold if x == 1]))
	    # Threshold = 0.5
	    # precision_with_default_threshold = graphlab.evaluation.precision(test_data['sentiment'],
	    #                                         predictions_with_default_threshold)
	    precision_with_default_threshold = precision_score(y_true=validation_target,
	    	y_pred=predictions_with_default_threshold)
	    # recall_with_default_threshold = graphlab.evaluation.recall(test_data['sentiment'],
	    #                                         predictions_with_default_threshold)
	    recall_with_default_threshold = recall_score(y_true=validation_target,
	    	y_pred=predictions_with_default_threshold)
	    	# Threshold = 0.9
	    	# precision_with_high_threshold = graphlab.evaluation.precision(test_data['sentiment'],
	    	#                                         predictions_with_high_threshold)
	    precision_with_high_threshold = precision_score(y_true=validation_target, 
	    	y_pred=predictions_with_high_threshold)
	    # recall_with_high_threshold = graphlab.evaluation.recall(test_data['sentiment'],
	    #                                         predictions_with_high_threshold)
	    recall_with_high_threshold = recall_score(y_true=validation_target,
	    	y_pred=predictions_with_high_threshold)
	    print "Precision (threshold = 0.5): %s" % precision_with_default_threshold
	    print "Recall (threshold = 0.5)   : %s" % recall_with_default_threshold

	    print "Precision (threshold = 0.9): %s" % precision_with_high_threshold
	    print "Recall (threshold = 0.9)   : %s" % recall_with_high_threshold
	    threshold_values = np.linspace(0.5, 1, num=100)
	    precision_all = []
	    recall_all = []
	    # probabilities = model.predict(test_data, output_type='probability')
	    for threshold in threshold_values:
	    	predictions = self.apply_threshold(probability[:,-1], threshold)
	    	#     precision = graphlab.evaluation.precision(test_data['sentiment'], predictions)
	    	precision = precision_score(y_true=validation_target,
	    		y_pred=predictions)
	    	# recall = graphlab.evaluation.recall(test_data['sentiment'], predictions)
	    	recall = recall_score(y_true=validation_target, y_pred=predictions)
	    	#print 'Metrics Threshold %s Precision %s Recall %s' % (threshold, precision, recall)
	    	precision_all.append(precision)
	    	recall_all.append(recall)
	    print 'Metrics Threshold %s Precision %s Recall %s' % (threshold, precision, recall)
	    precision_all.append(precision)
	    recall_all.append(recall)
	    cmat = confusion_matrix(y_true=validation_target,
	    	y_pred=self.apply_threshold(probability[:,-1], 0.98),
	    	labels=clf.classes_)    # use the same order of class as the LR model.
	    print ' target_label | predicted_label | count '
	    print '--------------+-----------------+-------'
	    # Print out the confusion matrix.
	    # NOTE: Your tool may arrange entries in a different order. Consult appropriate manuals.
	    for i, target_label in enumerate(clf.classes_):
	    	for j, predicted_label in enumerate(clf.classes_):
	    		print '{0:^13} | {1:^15} | {2:5d}'.format(target_label, predicted_label, cmat[i,j])
	    return precision_all,recall_all,acc

	def apply_threshold(self,probabilities, threshold):
	    ### YOUR CODE GOES HERE # +1 if >= threshold and -1 otherwise.
	    return [1 if x > threshold else -1 for x in probabilities]

	def accuracy(self,validation_target,predictions):
	    """caculate the accuracy of the sentiment's predicitons"""
	    correctly_classified = 0
	    total_examples = predictions.shape[0]
	    
	    for safe_loan,prediction in zip(validation_target,predictions):
	        if prediction == safe_loan:
	            correctly_classified += 1
	        else:
	            continue
	    print correctly_classified   
	    return float(correctly_classified)/float(total_examples)

	def save_pickle_model(self,model,name):
	    # save the model to disk
	    filename = os.path.join('static','models'+'/'+name)
	    pickle.dump(model, open(filename, 'wb'))



class Selectmodel():

        def open_pickle_model(self,name):
            filename= os.path.join('static','models'+'/'+name)
            loaded_model = pickle.load(open(filename,'rb'))
            return loaded_model

        def very_deep_copy(self,cool):
        	return pd.DataFrame(cool.values.copy(), cool.index.copy(), cool.columns.copy())

        def predicted_data(self,import_file_data,modelname,threshold):
            loans=pd.read_csv(import_file_data,low_memory=False)
            features1=list()
            features1=['member_id','annual_inc','collection_recovery_fee','dti','emp_length_num','funded_amnt','grade','grade_num',
            'home_ownership','initial_list_status','inq_last_6mths','installment','int_rate','is_inc_v','last_delinq_none',
            'last_major_derog_none']            
            features=list()
            features=['annual_inc','collection_recovery_fee','dti','emp_length_num','funded_amnt','grade','grade_num',
            'home_ownership','initial_list_status','inq_last_6mths','installment','int_rate','is_inc_v','last_delinq_none',
            'last_major_derog_none']
            loans = loans[features1]
            loans=loans.dropna()
            selected_data=self.very_deep_copy(loans)
            loans1=pd.get_dummies(loans[features])
            clf=self.open_pickle_model(modelname)
            probability=clf.predict_proba(loans1)

            predicted=[('safe' if x>=float(threshold) else 'risky') for x in probability[:,-1]]
            loans.insert(0,'score',probability[:,-1]) 
            loans.insert(0,'predicted',predicted)
            table,pagination=self.csv_paginate(loans,1)
            return table,pagination,loans,probability,selected_data

        def predicted_prob_change_data(self,loans_data,probability,modelname,threshold):
        	selected_data=self.very_deep_copy(loans_data)
        	
        	predicted=[('safe' if x>=float(threshold) else 'risky') for x in probability[:,-1]]
        	loans_data.insert(0,'score',probability[:,-1])
        	loans_data.insert(0,'predicted',predicted)
        	table,pagination=self.csv_paginate(loans_data,1)
        	return table,pagination,loans_data,selected_data

        def csv_paginate(self,loans,page):
            search=False
            PER_PAGE = 10
            cols=loans.columns.values.tolist()
            q = request.args.get('q')
            print page
            if q:
                search = True
            pagination = Pagination(page=page,per_page=PER_PAGE, total=len(loans.index), search=search, record_name='loans',css_framework='foundation')
            tables=loans[(page-1)*PER_PAGE:page*PER_PAGE][cols].to_html(classes='data')
            return tables,pagination