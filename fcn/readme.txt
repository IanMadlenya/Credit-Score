1. First:

$pip install virtualenv
$cd fncc
$virtualenv fcnenv
$source fcnenv/bin/activate

2. second:
once the virtual environment is activated then 
install the python packages with requirements file

$pip install -r requirements

3. third: 
run the flask server

$python run.py

4. in the browser go to http://0.0.0.0/5000

1.register and login
2.in the preprocessing page
select the training data  "lcdata_train.csv"

3.then click on modeling page
 a. first create new model: give model name and leave the rest as it is
 b. next in the modeling page, select model
 
4. after clicking on the selectmodel
 a.import the test data "lcdata_test.csv"
 b.select the created model from "select Model" option
 c.specify the threshold value 
     ----> from 0.0 to 1
     ----> if the threshold is more than "0.5"+ then it will list out more risky peoples

 d. finally click on "Analyze" it will show list of who are risky and safe


5. models are stored in the "/static/models" directory 
