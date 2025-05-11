from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier,GradientBoostingClassifier
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.model_selection import RandomizedSearchCV,GridSearchCV
from sklearn.metrics import confusion_matrix,classification_report
from sklearn.metrics import precision_score,recall_score,f1_score,RocCurveDisplay
import numpy as np
import pandas as pd

models={'XGBclassifier':XGBClassifier(),'adb':AdaBoostClassifier(),'GB':GradientBoostingClassifier(),"Logistic_regression":LogisticRegression(),"KNN":KNeighborsClassifier(),"Random_forest":RandomForestClassifier()}

def fit_and_score(x_train,x_test,y_train,y_test):
    """
    Fits and evaluate given dictionary of models
    x,_train "training data
    x_test testing data
    y_train training labels
    y_test testing labels
    """
    models=  {'XGBclassifier':XGBClassifier(),'adb':AdaBoostClassifier(),'GB':GradientBoostingClassifier(),"Logistic_regression":LogisticRegression(),"KNN":KNeighborsClassifier(),"Random_forest":RandomForestClassifier()}
    
    np.random.seed(42)
    model_scores={}
    for name , model in models.items():
        model.fit(x_train,y_train)
        model_scores[name]=model.score(x_test,y_test)
    print(f"model scores is : {model_scores}")    
    pd.DataFrame(model_scores,index=['accuracy']).T.plot.bar()