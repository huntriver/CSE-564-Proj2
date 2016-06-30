from flask import Flask,request,jsonify,render_template
from sklearn.cluster import *
from scipy.cluster.vq import *
from sklearn.decomposition import PCA as sklearnPCA
from sklearn import manifold,datasets
from matplotlib.mlab import PCA as mlabPCA
import matplotlib
matplotlib.use('Agg') 
import numpy as np
import jinja2
import csv
import json
import random
import matplotlib.pyplot as plt
import mpld3



app = Flask(__name__)
app.debug=True


@app.route("/")
def index():
    return render_template("index.html");

@app.route("/init_data")
def init_data():

    csvfile= open('static/data/ddd.csv','rU')
    # reader = csv.DictReader( csvfile, fieldnames = ("name","handedness","height","weight","avg","HR"))
    reader = csv.DictReader( csvfile, fieldnames = ("Date","Open","Close","Change","Volume"))
    # reader = csv.DictReader( csvfile, fieldnames = ( "ListingKey","ListingNumber","ListingCreationDate","CreditGrade","Term","LoanStatus","ClosedDate","BorrowerAPR","BorrowerRate","LenderYield","EstimatedEffectiveYield","EstimatedLoss","EstimatedReturn","ProsperRating (numeric)","ProsperRating (Alpha)","ProsperScore","ListingCategory (numeric)","BorrowerState","Occupation","EmploymentStatus","EmploymentStatusDuration","IsBorrowerHomeowner","CurrentlyInGroup","GroupKey","DateCreditPulled","CreditScoreRangeLower","CreditScoreRangeUpper","FirstRecordedCreditLine","CurrentCreditLines","OpenCreditLines","TotalCreditLinespast7years","OpenRevolvingAccounts","OpenRevolvingMonthlyPayment","InquiriesLast6Months","TotalInquiries","CurrentDelinquencies","AmountDelinquent","DelinquenciesLast7Years","PublicRecordsLast10Years","PublicRecordsLast12Months","RevolvingCreditBalance","BankcardUtilization","AvailableBankcardCredit","TotalTrades","TradesNeverDelinquent (percentage)","TradesOpenedLast6Months","DebtToIncomeRatio","IncomeRange","IncomeVerifiable","StatedMonthlyIncome","LoanKey","TotalProsperLoans","TotalProsperPaymentsBilled","OnTimeProsperPayments","ProsperPaymentsLessThanOneMonthLate","ProsperPaymentsOneMonthPlusLate","ProsperPrincipalBorrowed","ProsperPrincipalOutstanding","ScorexChangeAtTimeOfListing","LoanCurrentDaysDelinquent","LoanFirstDefaultedCycleNumber","LoanMonthsSinceOrigination","LoanNumber","LoanOriginalAmount","LoanOriginationDate","LoanOriginationQuarter","MemberKey","MonthlyLoanPayment","LP_CustomerPayments","LP_CustomerPrincipalPayments","LP_InterestandFees","LP_ServiceFees","LP_CollectionFees","LP_GrossPrincipalLoss","LP_NetPrincipalLoss","LP_NonPrincipalRecoverypayments","PercentFunded","Recommendations","InvestmentFromFriendsCount","InvestmentFromFriendsAmount","Investors" ) )
    data=json.dumps([ row for row in reader ])
    return data


@app.route('/random_decimation', methods = ['GET','POST'])
def random_decimation():
    json = request.get_json()
    result= random.sample(json, 100)
    return jsonify(result=result)


@app.route('/adaptive_decimation', methods = ['GET','POST'])
def adaptive_decimation():
    json = request.get_json()
    # data = json["data"]

    # n=json["clusters"]
    # print n
    n=3
    data=json
    lists=[]
    for row in data:
        aa=[row["Open"],row["Close"],row["Change"],row["Volume"]]
        #print aa
        lists.append(aa)
    a= np.array(lists).astype(np.float)
   
    res, idx = kmeans2(a,n)
    i=0
    arr=[]
    for i in range(0, n):
        arr.append([])
  
    for i in range(0,len(data)):
        arr[idx[i]].append(data[i])

    result=[]
    l=0
    for row in arr:
        x= int(round(float(len(row))/len(data)*100))
        b=random.sample(row,x)
        result.append(b)
    return jsonify(result=result)
   
@app.route('/PCA', methods = ['GET','POST'])
def pca():
    json = request.get_json()
    lists=[]
    for row in json:
        aa=[row["Open"],row["Close"],row["Change"],row["Volume"]]
        #print aa
        lists.append(aa)
    a= np.array(lists).astype(np.float)
    
    # sklearn_pca = sklearnPCA(n_components=4)
    # b= sklearn_pca.fit_transform(a).tolist()
    mlab_pca  = mlabPCA(a)
    b=mlab_pca.Y.tolist()
    #print len(b[0])
    return jsonify(result=b)

@app.route('/pcaPlot', methods = ['GET','POST'])
def pcaPlot():
    print 1
    json = request.get_json()
    # lists=[]
    # for row in json:
    #     aa=[row["Open"],row["Close"],row["Change"],row["Volume"]]
    #     #print aa
    #     lists.append(aa)
    print 2
    x=colorArray(json["clusters"])
    
    a= np.array(json["result"]).astype(np.float)
    fig=plt.figure()

    dims=random.sample(range(0, 3), 2)

    plt.scatter(a[:,dims[0]],a[:,dims[1]], c=x)

    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([-4,4])
    plt.ylim([-4,4])
    plt.title('Scree Plot of PCA')


    # X_iso = manifold.Isomap(10, n_components=2).fit_transform(mlab_pca.Y)
    
    # #mpld3.show()
    # print mpld3.fig_to_dict(fig)
    return jsonify(result=mpld3.fig_to_dict(fig))
@app.route('/pcaGraph', methods = ['GET','POST'])
def pcaGraph():
    json = request.get_json()
    # lists=[]
    # for row in json:
    #     aa=[row["Open"],row["Close"],row["Change"],row["Volume"]]
    #     #print aa
    #     lists.append(aa)

    x=colorArray(json["clusters"])
    
    a= np.array(json["result"]).astype(np.float)
    # print a
    fig=plt.figure()
    plt.scatter(a[:,0],a[:,1], c=x)

    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([-4,4])
    plt.ylim([-4,4])
    plt.title('PCA Graph')


    # X_iso = manifold.Isomap(10, n_components=2).fit_transform(mlab_pca.Y)
    
    # mpld3.show()
    # print mpld3.fig_to_dict(fig)
    return jsonify(result=mpld3.fig_to_dict(fig))

@app.route('/isoGraph', methods = ['GET','POST'])
def isoGraph():
    json = request.get_json()
    # lists=[]
    # for row in json:
    #     aa=[row["Open"],row["Close"],row["Change"],row["Volume"]]
    #     #print aa
    #     lists.append(aa)
    # x =[]
    # clusters=json["clusters"]
    # tmp=[0]*clusters[0]
    # x.extend(tmp)
    # tmp=[50]*clusters[1]
    # x.extend(tmp)
    # tmp=[100]*clusters[2]
    # x.extend(tmp)
    # x=np.array(x)
    x=colorArray(json["clusters"])
    a= np.array(json["result"]).astype(np.float)

    Y = manifold.Isomap(99, 2).fit_transform(a)
    fig=plt.figure()
    plt.scatter(Y[:,0],Y[:,1],c=x)

    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([-4,4])
    plt.ylim([-4,4])
    plt.title('Isomap Graph')


    # X_iso = manifold.Isomap(10, n_components=2).fit_transform(mlab_pca.Y)
    
    # #mpld3.show()
    # print mpld3.fig_to_dict(fig)
    return jsonify(result=mpld3.fig_to_dict(fig))


@app.route('/mdsGraph', methods = ['GET','POST'])
def mdsGraph():
    json = request.get_json()
    # lists=[]
    # for row in json:
    #     aa=[row["Open"],row["Close"],row["Change"],row["Volume"]]
    #     #print aa
    #     lists.append(aa)
    # x =[]
    # clusters=json["clusters"]
    # tmp=[0]*clusters[0]
    # x.extend(tmp)
    # tmp=[50]*clusters[1]
    # x.extend(tmp)
    # tmp=[100]*clusters[2]
    # x.extend(tmp)
    # x=np.array(x)
    x=colorArray(json["clusters"])
    a= np.array(json["result"]).astype(np.float)

    Y = manifold.MDS(2 , max_iter=100, n_init=4).fit_transform(a)
    fig=plt.figure()
    plt.scatter(Y[:,0],Y[:,1],c=x)

    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([-4,4])
    plt.ylim([-4,4])
    plt.title('MDS Graph')


    # X_iso = manifold.Isomap(10, n_components=2).fit_transform(mlab_pca.Y)
    
    # #mpld3.show()
    # print mpld3.fig_to_dict(fig)
    return jsonify(result=mpld3.fig_to_dict(fig))



def colorArray(clusters):
    if (clusters==[]):
        return np.array(['red']*100)
    x =[]
    tmp=['red']*clusters[0]
    x.extend(tmp)
    tmp=['yellow']*clusters[1]
    x.extend(tmp)
    tmp=['blue']*clusters[2]
    x.extend(tmp)
    x=np.array(x)
    return x

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=12345)