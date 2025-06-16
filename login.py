from flask import Flask, request, jsonify, render_template, send_file
import pymongo
from datetime import datetime
import os, pdfkit

app = Flask(__name__)

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['UserDatabase']
collection = db['user']
userid_coll = db['userId']

def upgrade_val():
    return userid_coll.find_one_and_update(
        filter={'id': "UserId"},
        update={'$inc': {'sequence_value': 1}},
        new=True
    )

@app.route('/')
def login():
    return render_template("login.html") 

@app.route('/user_info', methods=['POST'])
def New():
    if request.method == "POST":
        Name = request.form['Name']
        LastName = request.form['LastName']
        City = request.form['City']
        Email = request.form['Email']
        Registration = request.form['Registration']

        userInfo = {'Name': Name,'LastName': LastName,'City': City,'Email': Email,'Registration': Registration,'isDelete': 0,'date': str(datetime.today())}

        user_id_Data = upgrade_val()
        userInfo["id"] = int(user_id_Data["sequence_value"])

        data_insert = collection.insert_one(userInfo)
        if data_insert:
            return render_template('success.html')
        else:
            return render_template('failed.html')

@app.route('/pdf_gen')
def pdf():
    
    find_doc = list(collection.find({"isDelete":0}))
    if not find_doc:
        return jsonify({"message":"Not Such User"}),404
    my_list=[]
    for item in find_doc:
        item["_id"]=str(item["_id"])
        my_list.append(item)
     
    template = render_template('table.html',item = my_list)
    pdfkit.from_string(template,'output.pdf')
    print("template",template)
    return render_template('pdf.html')
  

@app.route('/download')
def download():
    file_path = os.path.join(os.getcwd(), 'output.pdf')
    return send_file(file_path, as_attachment=True)
        
@app.route('/Back',methods=["POST"])
def back():
    if request.method=="POST":
        return render_template('success.html')
    


@app.route('/get_data',methods=["GET"])
def get_data():
    get_data=list(collection.find({"isDelete":0}))
    mylist=[]
    for item in get_data:
        item["_id"]=str(item["_id"])
        mylist.append(item)
        return jsonify(mylist)



@app.route('/update',methods=["PUT"])
def update():
    check_data = collection.find_one({"Email":"rohan123@gmail.com", "isDelete":0})
    if not check_data:
        return jsonify({"message":"There is no such User"}),404
    update_result=collection.update_one({"Email":"rohan123@gmail.com", "isDelete":0},{"$set":{"City":"Mumbai"}})

    if update_result.modified_count > 0:
       return jsonify({"message":"Updated successfully"}),200
    else:
        return jsonify({"message":"Update Failed"}),500
    
    
@app.route("/delete",methods=["DELETE"])
def update1():
   find = collection.find({"Email":"aadarsh123@gmail.com","isDelete":0})
   if not find:
       return({"message":"No USER"}),404
   delete1=collection.update_one({"Email":"aadarsh123@gmail.com","isDelete":0},{"$set":{"isDelete":1}})
   if delete1.modified_count > 0:
        return jsonify({"message":"Update successfully"}),200 
   else:
        return jsonify({"messgae":"Failed"}),



                                     
if __name__=="__main__":
    app.run(debug=True)