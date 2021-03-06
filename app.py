from flask import Flask , render_template ,request ,flash , redirect , url_for
from passlib.hash import sha256_crypt
from wtforms import Form , StringField , TextAreaField, PasswordField , validators
from functools import wraps
from PIL import Image
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt
import numpy as np
from datetime import datetime
import os
import json
from ast import literal_eval
import time
import subprocess
from pygame import mixer
import numpy as np
from datetime import date
import secretKey
import order
import sessions

ImageName="/static/CoverImageDefault.jpg"
app = Flask(__name__)
secret=secretKey.s_key()
app.config["SECRET_KEY"] = secret

def has_run():
    has_run.has_run={"running":False}

administration_key=""
CHEFKEY=""

app.config['MONGO_URI']="mongodb+srv://Sohaib:sohaib12439@cluster0-5ij3o.gcp.mongodb.net/AutonomousServingSystem?retryWrites=true&w=majority"
mongo=PyMongo(app)

@app.route("/",methods=["GET","POST"])
def home():
    sessions.session.clear()
    sessions.session["admin_logged_in"]=False
    cur=mongo.db.AutonomousServingSystem
    result=cur.find_one({"title":"KEYS"})
    if result:
        global administration_key
        global CHEFKEY
        administration_key=result["AK"]
        CHEFKEY=result["CK"]
    layout=cur.find_one({"title":"LAYOUT"})
    return render_template("home.html",ImageName=ImageName,layout=layout)

@app.route("/AdminLogin")
def AL():
    return render_template("AdminLogin.html")

def admin_logged_in(g):
    @wraps(g)
    def wrap(*args , **kwargs):
        if 'admin_logged_in' in sessions.session:
            return g(*args , **kwargs)
        else:
            flash("Unauthorized Please login " , "danger")
            return redirect("/AdminLogin")
    return wrap

@app.route("/AdminSignup")
@admin_logged_in
def AS():
    return render_template("AdminSignUp.html",session=sessions.session)

@app.route("/CustomerLogin")
def CL():
    return render_template("CustomerLogin.html")

@app.route("/CustomerSignup")
def CS():
    return render_template("CustomerSignUp.html",session=sessions.session)

@app.route("/CustomerSignUpProcess",methods=["GET","POST","UPDATE"])
def CSUP():   
    if request.method == 'POST':
        data=request.form
        cur=mongo.db.AutonomousServingSystem
        cp=sha256_crypt.encrypt(str(data["pass"]))
        rn=np.random.randint(low=4, size=8)
        temp=""
        for i in rn:
            temp+=str(i)
        username=str(data["username"])+temp
        cur=mongo.db.AutonomousServingSystem
        global administration_key
        rn=cur.find_one({"title":"Rooms"})
        if rn:
            t="Room"+str(data["room_number"])   
            if rn[t]=="not reserved":
                price=cur.find_one({"packagePrices":"ASS"})
                bill=""
                for k,v in enumerate(price):
                    if data["package"]==v:
                        bill=price[v]
                        break
                if administration_key==str(data["r_key"]):
                    if str(data["pass"])==str(data["con_pass"]):
                        cur.insert_one({"title":"Customer","username":username,"customer_name":data["username"],"age":data["age"],"gender":data["gender"],"room_number":data["room_number"],"package":data["package"],"country":data["country"],"date_of_birth":data["dob"],"phone_number":data["phone"],"cnic":data["cnic"],"password":cp,"r-key":administration_key,"date_of_register":datetime.now(),"bill":bill,"checkout":False})
                        flash("You are now registered and can login username="+username,"success")
                        cur.find_one_and_update({"title":"Rooms"},{"$set":{t:"reserved"}})
                        if sessions.session["admin_logged_in"]==True:
                            return redirect("/AdminPortal")
                        else:
                            return redirect("/CustomerLogin")
                    else:
                        flash("Confirm Password Not Matched","danger")
                        return redirect("/CustomerSignup")                
                else:
                    flash("Registeration Key Not Correct","danger")
                    return redirect("/CustomerSignup")  
            else:
                flash("Room already assigned to another customer","danger")
                return redirect("/CustomerSignup")  
        else:
            price=cur.find_one({"packagePrices":"ASS"})
            bill=""
            for k,v in enumerate(price):
                if data["package"]==v:
                    bill=price[v]
                    break
            if administration_key==str(data["r_key"]):
                if str(data["pass"])==str(data["con_pass"]):
                    cur.insert_one({"title":"Customer","username":username,"age":data["age"],"gender":data["gender"],"room_number":data["room_number"],"package":data["package"],"country":data["country"],"date_of_birth":data["dob"],"phone_number":data["phone"],"cnic":data["cnic"],"password":cp,"r-key":administration_key,"date_of_register":datetime.now(),"bill":bill,"checkout":False})
                    flash("You are now registered and can login username="+username,"success")
                    return redirect("/CustomerLogin")
                else:
                    flash("Confirm Password Not Matched","danger")
                    return redirect("/CustomerSignup")                
            else:
                flash("Registeration Key Not Correct","danger")
                return redirect("/CustomerSignup")

@app.route("/CustomomerLoginTest",methods=["GET","POST"])
def clt():
    if request.method == 'POST':
        data=request.form
        cursor=mongo.db.AutonomousServingSystem
        result=cursor.find_one({"username":data["username"]})
        if(result):
            if(str(result["room_number"])==str(data["room_no"]) and result["title"]=="Customer"):
                if sha256_crypt.verify(data["password"] , result["password"]):
                    if result["package"]=="Normal":
                        sessions.session["username"]=result["username"]
                        sessions.session["title"]=result["title"]
                        sessions.session["package"]="Normal"
                        sessions.session["customer_logged_in"]=True
                        sessions.session["normal"]=True
                        sessions.session["room_no"]=data["room_no"]
                        flash("You are now logged in","success")
                        return redirect("/CustomerNormalPortal")
                    if result["package"]=="Luxury":
                        sessions.session["username"]=result["username"]
                        sessions.session["title"]=result["title"]
                        sessions.session["package"]="Luxury"
                        sessions.session["customer_logged_in"]=True 
                        sessions.session["luxury"]=True  
                        sessions.session["room_no"]=data["room_no"]                     
                        flash("You are now logged in","success")
                        return redirect("/CustomerLuxuryPortal")
                    if result["package"]=="SeaView":
                        sessions.session["username"]=result["username"]
                        sessions.session["title"]=result["title"]
                        sessions.session["package"]="SeaView"
                        sessions.session["customer_logged_in"]=True
                        sessions.session["seaview"]=True
                        sessions.session["room_no"]=data["room_no"]
                        flash("You are now logged in","success")
                        return redirect("/CustomerSeaViewPortal")
                    else:
                        flash("Package Error","danger")
                        return redirect("/CustomerLogin")
                else:
                    flash("Invalid username or password","warning")
                    return redirect("/CustomerLogin")
            else:
                flash("Entered room number is not assign to you","warning")
                return redirect("/CustomerLogin")
        else:
            flash("Invalid username or password","danger")
            return redirect("/CustomerLogin")

def customer_logged_in(g):
    @wraps(g)
    def wrap(*args , **kwargs):
        if 'customer_logged_in' in sessions.session:
            return g(*args , **kwargs)
        else:
            flash("Unauthorized Please login " , "danger")
            return redirect("/CustomerLogin")
    return wrap

@app.route("/CustomerNormalPortal")
@customer_logged_in
def cnp():
    cursor=mongo.db.AutonomousServingSystem
    data=cursor.find_one({"username":sessions.session["username"],"title":sessions.session["title"]})
    cur=mongo.db.AutonomousServingRobot
    result=cur.find_one({"username":sessions.session["username"],"room":sessions.session["room_no"],"status":"waiting"})
    if result:
        return redirect("/OrderArived")
    return render_template("CustomerNormalPortal.html",data=data)

@app.route("/CustomerSeaViewPortal")
@customer_logged_in
def csvp():
    cursor=mongo.db.AutonomousServingSystem
    data=cursor.find_one({"username":sessions.session["username"],"title":sessions.session["title"]})
    cur=mongo.db.AutonomousServingRobot
    result=cur.find_one({"username":sessions.session["username"],"room":sessions.session["room_no"],"status":"waiting"})
    if result:
        return redirect("/OrderArived")
    return render_template("CustomerSeaViewPortal.html",data=data)

@app.route("/CustomerLuxuryPortal")
@customer_logged_in
def clp():
    cursor=mongo.db.AutonomousServingSystem
    data=cursor.find_one({"username":sessions.session["username"],"title":sessions.session["title"]})
    cur=mongo.db.AutonomousServingRobot
    result=cur.find_one({"username":sessions.session["username"],"room":sessions.session["room_no"],"status":"waiting"})
    if result:
        return redirect("/OrderArived")
    return render_template("CustomerLuxuryPortal.html",data=data)

@app.route("/CustomerSignout")
@customer_logged_in
def clo():
    sessions.session.clear()
    flash("You are now logged out","success")
    return redirect("/CustomerLogin")

@app.route("/OrderNow")
@customer_logged_in
def on():
    cur=mongo.db.AutonomousServingSystem
    result=cur.find({"title":"deal"})
    if result:
        deals=[]
        temp={}
        n=0
        for i in result:
            temp.clear()
            for k,v in i.items():
                if k=="deal_name":
                    temp[k]=v
                elif k=="description":
                    temp[k]=v
                elif k=="price":
                    temp[k]=v
                elif k=="deal_image":
                    temp[k]=v
            deals.append(temp.copy())
        return render_template("OrderNow.html",totalItems=order.NumberOfItems,deals=deals)
    else:
        flash("No Deal Found")
        return render_template("OrderNow.html",totalItems=order.NumberOfItems)

@app.route("/addItem",methods=["GET","POST"])
@customer_logged_in
def ai():
    if request.method == 'POST':
        data=request.form
        temp=""
        for i in order.Items:
            for k,v in i.items():
                if data["itemName"]==v:
                    temp="present"
                    break
        if temp=="present":
            flash("Item already present in cart","warning")
        else:
            temp={}
            temp["itemName"]=data["itemName"]
            temp["itemPrice"]=int(data["itemPrice"])
            temp["itemQuantity"]=1
            order.Items.append(temp)
            order.NumberOfItems+=1
            order.TotalPrice+=int(data["itemPrice"])
            flash("Item Added","success")
    return redirect("/OrderNow")

@app.route("/Cart")
@customer_logged_in
def cart():
    return render_template("Cart.html",items=order.Items,total=order.TotalPrice,session=sessions.session)

@app.route("/QuantityIncrement",methods=["GET","POST"])
def qi():
    data=request.form
    temp=0
    itemPrice=0
    itemQuantity=0
    for i in order.Items:
        for k,v in i.items():
            if v==data["itemName"]:
                order.Items[temp]["itemQuantity"]+=1
                break
        temp+=1
    order.TotalPrice=0
    for i in order.Items:
        price=i["itemPrice"]*i["itemQuantity"]
        order.TotalPrice+=price            
    return redirect("/Cart")

@app.route("/QuantityDecrement",methods=["GET","POST"])
def qd():
    data=request.form
    temp=0
    itemPrice=0
    itemQuantity=0
    for i in order.Items:
        for k,v in i.items():
            if v==data["itemName"]:
                if order.Items[temp]["itemQuantity"]>=2:
                    order.Items[temp]["itemQuantity"]=order.Items[temp]["itemQuantity"]-1
        temp+=1
    order.TotalPrice=0
    for i in order.Items:
        price=i["itemPrice"]*i["itemQuantity"]
        order.TotalPrice+=price            
    return redirect("/Cart")

@app.route("/removeItem",methods=["GET","POST"])
def ri():
    if request.method=="POST":
        data=request.form
        temp=0
        print(data)
        for i in order.Items:
            print(i)
            temp2=i["itemName"].split()
            if temp2[0]==data["itemName"] and i["itemPrice"]==int(data["itemPrice"]):
                print(i)
                del order.Items[temp]
                order.NumberOfItems=order.NumberOfItems-1
                order.TotalPrice=order.TotalPrice-(int(data["itemPrice"])*int(data["itemQuantity"]))
                break
            temp+=1
    return redirect("/Cart")

@app.route("/clearCart")
@customer_logged_in
def cc():
    order.Items.clear()
    order.NumberOfItems=0
    order.TotalPrice=0
    flash("Items Cleared","success")
    return redirect("/Cart")

@app.route("/orderConfirm")
@customer_logged_in
def oc():
    cur=mongo.db.AutonomousServingSystem
    temp=0
    for i in order.Items:
        if i["itemQuantity"]==0:
            del order.Items[temp]
        temp+=1
    if len(order.Items)>0:
        result=cur.find_one({"username":sessions.session["username"]})
        if result:
            now=datetime.now()
            time = now.strftime("%H:%M:%S")
            today = datetime.today().strftime('%Y-%m-%d')
            cur.insert_one({"title":"order","customerName":sessions.session["username"],"order":order.Items,"amount":order.TotalPrice,"room_number":result["room_number"],"status":"placed","date":str(today),"time":str(time)})
            updatedBill=int(result["bill"])+int(order.TotalPrice)
            cur.update({"_id":result["_id"]},{"$set":{"bill":str(updatedBill)}})
            order.Items.clear()
            order.TotalPrice=0
            order.NumberOfItems=0
            flash("Order Placed","success")
            if sessions.session["package"]=="Normal":
                return redirect("/CustomerNormalPortal")
            elif sessions.session["package"]=="Luxury":
                return redirect("/CustomerLuxuryPortal")
            elif sessions.session["package"]=="SeaView":
                return redirect("/CustomerSeaViewPortal")
    else:
        flash("No Item Found","danger")
        return redirect("/Cart")

@app.route("/ordersDetails")
@customer_logged_in
def od():
    cur=mongo.db.AutonomousServingSystem
    result=cur.find({"title":"order","customerName":sessions.session["username"]})
    if result:
        d=[]
        for i in result:
            d.append(i)
        if len(d)==0:
            flash("No Data Found","warning")
            return render_template("OrderedDetails.html")
        else:
            orders=[]
            temp=0
            for i in d:
                for k,v in i.items():
                    if k=="order":
                        for l in i[k]:
                            orders.append(l)
                            orders[temp]["date"]=i["date"]
                            orders[temp]["time"]=i["time"]
                            temp+=1  
            return render_template("OrderedDetails.html",orders=orders)
    else:
        flash("No Data Found","warning")
        if sessions.session["package"]=="Normal":
            return redirect("/CustomerNormalPortal")
        elif sessions.session["package"]=="Luxury":
            return redirect("/CustomerLuxuryPortal")
        elif sessions.session["package"]=="SeaView":
            return redirect("/CustomerSeaViewPortal")
    
@app.route("/billing")
@customer_logged_in
def b():
    cur=mongo.db.AutonomousServingSystem
    bill=[]
    result=cur.find_one({"packagePrices":"ASS"})
    if result:
        pA=result[sessions.session["package"]]
        Total=int(pA)
        cur=mongo.db.AutonomousServingSystem
        order=cur.find({"title":"order","customerName":sessions.session["username"]})
        if order:
            for i in order:
                temp={}
                temp["dateTime"]=i["date"]+" "+i["time"]
                temp["amount"]=i["amount"]
                Total+=int(i["amount"])
                bill.append(temp)
    return render_template("Billing.html",bill=bill,pA=pA,total=Total)

def cr(data):
    cp=sha256_crypt.encrypt(str(data["pass"]))
    rn=np.random.randint(low=3, size=6)
    temp=""
    x = datetime.now()
    for i in rn:
        temp+=str(i)
    id=str(data["username"][0])+temp+"-"+str(x.year)
    cur=mongo.db.AutonomousServingSystem
    global administration_key
    if administration_key==str(data["r_key"]):
        if str(data["pass"])==str(data["con_pass"]):
            fn=""
            if "Image" in request.files:
                data=request.form
                chefImage=request.files["Image"]
                fn=id+"_"+chefImage.filename
                mongo.save_file(fn,chefImage)
                cur.insert_one({"title":"Chef","id":id,"username":data["username"],"age":data["age"],"gender":data["gender"],"post":data["post"],"qualification":data["qualification"],"country":data["country"],"date_of_birth":data["dob"],"phone_number":data["phone"],"cnic":data["cnic"],"password":cp,"r-key":administration_key,"date_of_register":datetime.now(),"JobStatus":"Available","chefImage":fn})
                flash("You are now registered and can loginid="+id,"success")
                return redirect("/AdminPortal")
            else:
                flash("Uploaded Image Not Found","warning")
                return redirect("/AdminSignup")
        else:
            flash("Confirm Password Not Matched","danger")
            return redirect("/AdminSignup")                
    else:
        flash("Registeration Key Not Correct","danger")
        return redirect("/AdminSignup")     
    return redirect("/AdminLogin")

def arf(data):
    cp=sha256_crypt.encrypt(str(data["pass"]))
    rn=np.random.randint(low=3, size=6)
    temp=""
    x = datetime.now()
    for i in rn:
        temp+=str(i)
    id=str(data["username"][0])+temp+"-"+str(x.year)
    cur=mongo.db.AutonomousServingSystem
    global administration_key
    if administration_key==str(data["r_key"]):
        if str(data["pass"])==str(data["con_pass"]):
            fn=""
            if "Image" in request.files:
                data=request.form
                adminImage=request.files["Image"]
                fn=id+"_"+adminImage.filename
                mongo.save_file(fn,adminImage)
                cur.insert_one({"title":"Admin","id":id,"username":data["username"],"age":data["age"],"gender":data["gender"],"post":data["adminPost"],"qualification":data["qualification"],"country":data["country"],"date_of_birth":data["dob"],"phone_number":data["phone"],"cnic":data["cnic"],"password":cp,"r-key":administration_key,"date_of_register":datetime.now(),"JobStatus":"Available","adminImage":fn})
                flash("New Admin is now registered and can loginid="+id,"success")
                if sessions.session["md_logged_in"]:
                    return redirect("/MDPortal")
                else:
                    return redirect("/AdminPortal")
            else:
                flash("Uploaded Image Not Found","warning")
                return redirect("/AdminSignup")
        else:
            flash("Confirm Password Not Matched","danger")
            return redirect("/AdminSignup")                
    else:
        flash("Registeration Key Not Correct","danger")
        return redirect("/AdminSignup")     

@app.route("/AdminRegistration",methods=["GET","POST"])
def ar():
    data=request.form
    if data["post"]=="chef":
        cr(data)
    elif data["post"]=="admin":
        arf(data)
    elif data["post"]=="":
        flash("Post not found","danger")
        return redirect("/AdminSignUp")
    if sessions.session["md_logged_in"]:
        return redirect("/MDPortal")
    else:
        return redirect("/AdminPortal")

@app.route("/ChefLoginTest",methods=["GET","POST"])
def chefLoginTest():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    global CHEFKEY
    result=cur.find_one({"title":"Chef","id":data["id"]})
    if result:
        if sha256_crypt.verify(data["password"] , result["password"]):
            if CHEFKEY==data["key"]:
                sessions.session["id"]=result["id"]
                sessions.session["title"]=result["title"]
                sessions.session["chef_logged_in"]=True 
                flash("You are now loggedin","success")
                return redirect("/ChefPortal")
            else:
                flash("Incorrect Key","danger")
                return redirect("/AdminLogin")
        else:
            flash("Incorrect Id or Password","danger")
            return redirect("/AdminLogin")
    else:
        flash("Incorrect Id or Password","danger")
        return redirect("/AdminLogin")

def chef_logged_in(g):
    @wraps(g)
    def wrap(*args , **kwargs):
        if 'chef_logged_in' in sessions.session:
            return g(*args , **kwargs)
        else:
            flash("Unauthorized Please login " , "danger")
            return redirect("/AdminLogin")
    return wrap

@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)

@app.route("/ChefPortal",methods=["GET","POST"])
@chef_logged_in
def cp():
    cur=mongo.db.AutonomousServingSystem
    result=cur.find_one({"title":"Chef","id":sessions.session["id"]})
    if result:
        data=result
        order=cur.find({"title":"order"})
        placed=[]
        recieved=[]
        if order:
            for i in order:
                if i["status"]=="delivered":
                    pass
                elif i["status"]=="recieved":
                    recieved.append(i)
                else:
                    placed.append(i)
        np=len(placed)
        rp=len(recieved)
        cur=mongo.db.AutonomousServingRobot
        result2=cur.find_one({"title":"status"})
        robot_status=result2["status"]
        return render_template("ChefPortal.html",data=data,np=np,rp=rp,placed=placed,recieved=recieved,robot_status=robot_status)
    else:
        flash("Login Error","danger")
        return redirect("/AdminLogin")

@app.route("/ChefSignout")
@chef_logged_in
def cS():
    sessions.session.clear()
    flash("Successfully Logged Out","success")
    return redirect("/AdminLogin")

@app.route("/CurrentOrders")
@chef_logged_in
def co():
    cur=mongo.db.AutonomousServingSystem
    result=cur.find({"title":"order","status":"placed"})
    if result:
        data=result
        return render_template("CurrentOrders.html",data=data)
    else:
        flash("No Order Found","warning")
        return render_template("CurrentOrders.html")

@app.route("/RecieveOrder",methods=["GET","POST","UPDATE"])
@chef_logged_in
def ro():
    cur=mongo.db.AutonomousServingSystem
    data=request.form.to_dict()
    result=cur.find_one({"title":"order","customerName":data["customerName"],"room_number":data["rn"],"date":data["date"],"time":data["time"]})
    if result:
        now=datetime.now()
        time = now.strftime("%H:%M:%S")
        today = datetime.today().strftime('%Y-%m-%d')
        cur.find_one_and_update({"_id":result["_id"]},{"$set":{"status":"recieved"}})
        cur.insert_one({"title":"recievedOrder","chefId":sessions.session["id"],"customerName":data["customerName"],"order":data["items"],"room_number":data["rn"],"status":"preparing","date":str(today),"time":str(time)})
        flash("Order Recieved","success")
        return redirect("/ChefPortal")
    else:
        flash("Order Not Recieved","danger")
        return redirect("/ChefPortal")

@app.route("/RecievedOrders",methods=["GET","POST"])
@chef_logged_in
def rdo():
    cur=mongo.db.AutonomousServingSystem
    result=cur.find({"title":"recievedOrder","status":"preparing"})
    if result:
        data=result
        orders=[]
        inc=0
        for i in data:
            orders.append(i)
            for k,v in i.items():
                if k=="order":
                    temp=literal_eval(i["order"])
                    orders[inc]["order"]=temp
            inc+=1
        return render_template("RecievedOrders.html",orders=orders)
    else:
        flash("No Order Found","success")
        return render_template("RecievedOrders.html")

@app.route("/UploadDeal",methods=["GET","POST"])
@chef_logged_in
def ud():
    return render_template("UploadDeal.html")

@app.route("/PostDeal",methods=["GET","POST"])
@chef_logged_in
def pd():
    data=request.form
    if "deal_image" in request.files:
        deal_image=request.files["deal_image"]
        temp=""
        rn=np.random.randint(low=1, size=3)
        for i in rn:
            temp+=str(i)        
        fn=data["title"]+temp+deal_image.filename
        mongo.save_file(fn,deal_image)
        cursor=mongo.db.AutonomousServingSystem
        cursor.insert_one({"title":"deal","deal_name":data["title"],"description":data["description"],"price":int(data["price"]),"deal_image":fn,"chef_name":sessions.session["id"],"dateTime":datetime.now()})
        flash("Deal Uploaded","success")
        return redirect("/ChefPortal")
    else:
        flash("Deal Not Uploaded","danger")
        return redirect("/ChefPortal")

@app.route("/DeleteDeal",methods=["GET","POST","DELETE"])
@chef_logged_in
def dd():
    cur=mongo.db.AutonomousServingSystem
    result=cur.find({"title":"deal","chef_name":sessions.session["id"]})
    if result:
        deals=[]
        temp={}
        n=0
        for i in result:
            temp.clear()
            for k,v in i.items():
                if k=="deal_name":
                    temp[k]=v
                elif k=="description":
                    temp[k]=v
                elif k=="price":
                    temp[k]=v
                elif k=="deal_image":
                    temp[k]=v
            deals.append(temp.copy())
        return render_template("DeleteDeal.html",deals=deals)
    else:
        flash("No Deal Found")
        return render_template("DeleteDeal.html")

@app.route("/DeleteProcess",methods=["GET","POST","DELETE"])
@chef_logged_in
def ddp():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    result=cur.remove({"title":"deal","deal_name":data["deal_name"],"description":data["description"],"price":int(data["price"]),"chef_name":sessions.session["id"]})
    if result:
        flash("Deal Deleted","success")
        return redirect("/DeleteDeal")
    else:
        flash("Deal Not Deleted...","danger")
        return redirect("/DeleteDeal")

@app.route("/DeliveredOrders",methods=["GET","POST"])
def deliveredOrders():
    cursor=mongo.db.AutonomousServingSystem
    result=cursor.find_one({"title":"AST_Order","chef_id":sessions.session["id"],"status":"delivered"})
    if result:
        data=[result]
        return render_template("DeliveredOrders.html",data=data)
    else:
        flash("No Data Found","warning")
        return redirect("/ChefPortal")
    
@app.route("/AdminLoginTest",methods=["GET","POST"])
def alt():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    global administration_key
    result=cur.find_one({"title":"Admin","id":data["id"],"post":data["adminPost"]})
    if result:
        if sha256_crypt.verify(data["password"] , result["password"]):
            if administration_key==data["key"]:
                if data["adminPost"]=="MD":
                    sessions.session["md_verification"]=True
                    sessions.session["id"]=result["id"]
                    return redirect("/MD")
                else:
                    sessions.session["id"]=result["id"]
                    sessions.session["title"]=result["title"]
                    sessions.session["post"]=result["post"]
                    sessions.session["username"]=result["username"]
                    sessions.session["admin_logged_in"]=True 
                    if result["post"]=="Manager" or result["post"]=="manager" or result=="MANAGER":
                        flash("Access is only available from authorized system","warning")
                        sessions.session.clear()
                        return redirect("/AdminLogin")
                    else:
                        return redirect("/AdminPortal")
            else:
                flash("Incorrect Key","danger")
                return redirect("/AdminLogin")
        else:
            flash("Incorrect Id or Password","danger")
            return redirect("/AdminLogin")
    else:
        flash("Incorrect Id or Password","danger")
        return redirect("/AdminLogin")
    return render_template("/AdminLogin")

@app.route("/AdminPortal")
@admin_logged_in
def ap():
    cur=mongo.db.AutonomousServingSystem
    data=cur.find_one({"title":"Admin","id":sessions.session["id"]})
    return render_template("AdminPortal.html",data=data)

@app.route("/AdminSignout")
def aso():
    sessions.session.clear()
    flash("Loggeod Out","success")
    return redirect("/AdminLogin")

def md_verification(g):
    @wraps(g)
    def wrap(*args , **kwargs):
        if 'md_verification' in sessions.session:
            return g(*args , **kwargs)
        else:
            flash("Unauthorized Please login" , "danger")
            return redirect("/AdminLogin")
    return wrap

@app.route("/MD")
@md_verification
def md():
    return render_template("md_verification.html")

@app.route("/MDTest",methods=["GET","POST"])
def mdt():
    entered_data=request.form
    cur=mongo.db.AutonomousServingSystem
    database=cur.find_one({"title":"Admin","id":sessions.session["id"]})
    if entered_data["cnic"]==database["cnic"]:
        sessions.session["md_logged_in"]=True
        sessions.session["admin_logged_in"]=True
        flash("Welcome "+database["username"],"success")
        return redirect("/MDPortal")
    else:
        sessions.session.clear()
        flash("Unauthorized Login","danger")
        return redirect("/AdminLogin")

def md_logged_in(g):
    @wraps(g)
    def wrap(*args , **kwargs):
        if 'md_logged_in' in sessions.session:
            return g(*args , **kwargs)
        else:
            flash("Unauthorized Please login " , "danger")
            return redirect("/AdminLogin")
    return wrap

@app.route("/MDPortal")
@md_logged_in
def mdp():
    cur=mongo.db.AutonomousServingSystem
    data=cur.find_one({"title":"Admin","id":sessions.session["id"]})
    return render_template("MDPortal.html",data=data)


@app.route("/CustomerInquiry",methods=["GET","POST"])
@admin_logged_in
def CustomerInquiry():
    cur=mongo.db.AutonomousServingSystem
    data=cur.find({"title":"Customer"})
    if data:
        return render_template("CustomerInquiry.html",data=data)
    else:
        flash("No Data Found","warninig")
        return render_template("CustomerInquiry.html",session=sessions.session)

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

@app.route("/search",methods=["GET","POST"])
@admin_logged_in
def search():
    s=request.form
    cur=mongo.db.AutonomousServingSystem
    result=hasNumbers(s["search"])
    if result:
        data=cur.find({"title":"Customer","username":s["search"]})
        return render_template("CustomerInquiry.html",data=data)
    else:
        data=cur.find({"title":"Customer","customer_name":s["search"]})
        return render_template("CustomerInquiry.html",data=data)

@app.route("/ChefInquiry",methods=["GET","POST"])
@md_logged_in
def ChefInquiry():
    cur=mongo.db.AutonomousServingSystem
    data=cur.find({"title":"Chef"})
    if data:
        return render_template("ChefInquiry.html",data=data)
    else:
        flash("No Data Found","warninig")
        return render_template("ChefInquiry.html")

@app.route("/ChefSearch",methods=["GET","POST"])
@md_logged_in
def ChefSearch():
    s=request.form
    cur=mongo.db.AutonomousServingSystem
    result=hasNumbers(s["search"])
    if result:
        data=cur.find({"title":"Chef","id":s["search"]})
        return render_template("ChefInquiry.html",data=data)
    else:
        data=cur.find({"title":"Chef","username":s["search"]})
        return render_template("ChefInquiry.html",data=data)

@app.route("/AdminInquiry",methods=["GET","POST"])
@md_logged_in
def AdminInquiry():
    cur=mongo.db.AutonomousServingSystem
    data=cur.find({"title":"Admin"})
    if data:
        return render_template("AdminInquiry.html",data=data)
    else:
        flash("No Data Found","warninig")
        return render_template("AdminInquiry.html")

@app.route("/AdminSearch",methods=["GET","POST"])
@md_logged_in
def AdminSearch():
    s=request.form
    cur=mongo.db.AutonomousServingSystem
    result=hasNumbers(s["search"])
    if result:
        data=cur.find({"title":"Admin","id":s["search"]})
        return render_template("AdminInquiry.html",data=data)
    else:
        data=cur.find({"title":"Admin","username":s["search"]})
        return render_template("AdminInquiry.html",data=data)

@app.route("/AllDeals")
def ad():
    cur=mongo.db.AutonomousServingSystem
    result=cur.find({"title":"deal"})
    if result:
        deals=[]
        temp={}
        n=0
        for i in result:
            temp.clear()
            for k,v in i.items():
                if k=="deal_name":
                    temp[k]=v
                elif k=="description":
                    temp[k]=v
                elif k=="price":
                    temp[k]=v
                elif k=="deal_image":
                    temp[k]=v
            deals.append(temp.copy())
        return render_template("AllDeals.html",deals=deals)
    else:
        flash("No Deal Found","warning")
        return render_template("AllDeals.html")

@app.route("/CustomerCheckout")
@admin_logged_in
def cco():
    return render_template("CustomerCheckout.html")

@app.route("/Checkout",methods=["GET","POST","UPDATE"])
@admin_logged_in
def checkout():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    room_number="Room"+str(data["room_number"])
    cur.find_one_and_update({"title":"Rooms"},{"$set":{room_number:"not reserved"}})
    cur.find_one_and_update({"title":"Customer","username":data["username"]},{"$set":{"checkout":"True","CheckoutDate":str(datetime.now())}})
    flash("Status Updated","success")
    return redirect("/AdminPortal")

@app.route("/TerminateChef",methods=["GET","POST","DELETE"])
@md_logged_in
def tc():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    result=cur.remove({"title":"Chef","id":data["id"],"cnic":data["cnic"]})
    if result:
        cur.remove({"title":"deal","chef_name":data["id"]})
        flash("Chef Removed Successfully","success")
        return redirect("/ChefInquiry")
    else:
        flash("Error","danger")
        return redirect("/ChefInquiry")

@app.route("/TerminateAdmin",methods=["GET","POST","DELETE"])
@md_logged_in
def ta():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    result=cur.remove({"title":"Admin","id":data["id"],"username":data["username"],"cnic":data["cnic"],"post":data["post"]})
    if result:
        flash("Admin Removed Successfully","success")
        return redirect("/AdminInquiry")
    else:
        flash("Error","danger")
        return redirect("/AdminInquiry")

@app.route("/RoomsStatus")
def RoomStatus():
    cur=mongo.db.AutonomousServingSystem
    data=cur.find_one({"title":"Rooms"})
    return render_template("RoomsStatus.html",data=data,session=sessions.session)

@app.route("/RoomsAddresses")
@md_logged_in
def RoomsAddresses():
    cur=mongo.db.AutonomousServingSystem
    data=cur.find_one({"title":"Rooms"})
    address=cur.find({"class":"room_address"})
    temp=[]
    for i in address:
        temp.append(i)
    addresses={}
    for i in temp:
        addresses[i["title"]]=i["distance"]
    return render_template("RoomsAddresses.html",data=data,address=addresses)

temp_room=""

@app.route("/RoomAddress",methods=["GET","POST"])
@md_logged_in
def RoomAddresses():
    data=request.form
    global temp_room
    room=data["room"]
    temp_room=room
    return render_template("RoomAddress.html",room=room)

@app.route("/Turns",methods=["GET","POST"])
@md_logged_in
def Turns():
    data=request.form
    global temp_room
    room=temp_room
    t=int(data["number_of_turns"])
    turn=[i for i in range(1,t+1)]
    return render_template("RoomAddress.html",turns=turn,room=room)

@app.route("/UpdateAddress",methods=["GET","POST","UPDATE"])
@md_logged_in
def UpdateAddress():
    data=request.form
    global temp_room
    cur=mongo.db.AutonomousServingSystem
    temp=[]
    for k,v in enumerate(data):
        temp.append(data[v])
    for i in range(1,len(temp)+1,2):
        if temp[i]=="wait":
            pass
        else:
            temp[i]=float(temp[i])
    result=cur.find_one({"title":temp_room})
    if result:
        cur.find_one_and_update({"title":temp_room},{"$set":{"distance":temp}})
    else:
        cur.insert_one({"title":temp_room,"class":"room_address","distance":temp})
    flash("Room Address Updated","success")
    return redirect("/MDPortal")

@app.route("/AddRoom")
@md_logged_in
def AddRoom():
    return render_template("AddRoom.html")

@app.route("/AddRoomProcess",methods=["GET","POST","UPDATE"])
@md_logged_in
def AddRoomProcess():
    data=request.form
    global administration_key
    cur=mongo.db.AutonomousServingSystem
    if data["key"]==administration_key:
        room="Room"+str(data["room_number"])
        cur.find_one_and_update({"title":"Rooms"},{"$set":{room:"not reserved"}})
        flash("Room Added Successfully","success")
        return redirect("/RoomsAddresses")
    else:
        flash("Incorrect Administration Key","danger")
        return redirect("/RoomsAddresses")

@app.route("/Setting")
@md_logged_in
def setting():
    return render_template("Setting.html")

@app.route("/UpdateAdministrationKey")
@md_logged_in
def upk():
    return render_template("UpdateAdministrationKey.html")

@app.route("/UAKP",methods=["GET","POST","UPDATE"])
@md_logged_in
def uakp():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    global administration_key
    if data["old_key"]==administration_key:
        cur.find_one_and_update({"title":"KEYS"},{"$set":{"AK":data["new_key"]}})
        administration_key=data["new_key"]
        flash("Updated Successfully","success")
        return redirect("/Setting")
    else:
        flash("Incorrect Administration Key","danger")
        return redirect("/Setting")       

@app.route("/UpdateChefKey")
@md_logged_in
def uck():
    return render_template("UpdateChefKey.html")

@app.route("/UCKP",methods=["GET","POST","UPDATE"])
@md_logged_in
def uckp():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    global CHEFKEY
    if data["old_key"]==CHEFKEY:
        cur.find_one_and_update({"title":"KEYS"},{"$set":{"CK":data["new_key"]}})
        CHEFKEY=data["new_key"]
        flash("Updated Successfully","success")
        return redirect("/Setting")
    else:
        flash("Incorrect Chef Key","danger")
        return redirect("/Setting")    

@app.route("/UpdateBackgroundLayout")
@md_logged_in
def ubl():
    return render_template("UpdateBackgroundLayout.html")

@app.route("/UpdateLayoutTitleColour")
@md_logged_in
def ultc():
    title="COLOUR"
    return render_template("UpdateLayoutTitle.html",title=title)

@app.route("/UpdateLayoutTitleColourProcess",methods=["GET","POST"])
@md_logged_in
def ultcp():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    global administration_key
    if data["key"]==administration_key:
        cur.find_one_and_update({"title":"LAYOUT"},{"$set":{"title_color":data["update"]}})
        flash("Colour Updated Successfully","success")
        return redirect("/UpdateBackgroundLayout")
    else:
        flash("Incorrect Key","danger")
        return redirect("/UpdateLayoutTitleColour")

@app.route("/UpdateLayoutTitleImage")
@md_logged_in
def ulti():
    title="IMAGE"
    return render_template("UpdateLayoutTitle.html",title=title)

@app.route("/UpdateLayoutTitleImageProcess",methods=["GET","POST"])
@md_logged_in
def ultip():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    global administration_key
    if data["key"]==administration_key:
        if "update" in request.files:
            CoverImage=request.files["update"]
            IN=CoverImage.filename
            im1 = Image.open(CoverImage)
            im1.save("D:/FYP CODE/FLASK WORK/static/"+IN)
            cur.find_one_and_update({"title":"LAYOUT"},{"$set":{"title_image":IN}})
            flash("Image Updated Successfully","success")
            return redirect("/UpdateBackgroundLayout")
        else:
            flash("Upload File Correctly","danger")
            return redirect("/UpdateLayoutTitleImage")
    else:
        flash("Incorrect Key","danger")
        return redirect("/UpdateLayoutTitleImage")

@app.route("/UpdateTitleSlider")
@md_logged_in
def uts():
    title="title"
    return render_template("UpdateSlider.html",title=title)

@app.route("/UpdateTitleSliderProcess",methods=["GET","POST"])
@md_logged_in
def utsp():
    data=request.form
    global administration_key
    if data["key"]==administration_key:
        if "update" in request.files:
            img_no="S1"+str(data["slide_no"])
            cur=mongo.db.AutonomousServingSystem
            SlideImage=request.files["update"]
            ImageName=SlideImage.filename
            im1 = Image.open(SlideImage)
            im1.save("D:/FYP CODE/FLASK WORK/static/"+ImageName)
            cur.find_one_and_update({"title":"LAYOUT"},{"$set":{img_no:ImageName}})
            flash("Slider Suceessfully Updated","success")
            return redirect("/UpdateBackgroundLayout")
        else:
            flash("Incorrect File","danger")
            return redirect("/UpdateTitleSlider")
    else:
        flash("Incorrect Key","danger")
        return redirect("/UpdateTitleSlider")

@app.route("/UpdateNormalSlider")
@md_logged_in
def uns():
    title="normal"
    return render_template("UpdateSlider.html",title=title)

@app.route("/UpdateNormalSliderProcess",methods=["GET","POST"])
@md_logged_in
def unsp():
    data=request.form
    global administration_key
    if data["key"]==administration_key:
        if "update" in request.files:
            img_no="S4"+str(data["slide_no"])
            cur=mongo.db.AutonomousServingSystem
            SlideImage=request.files["update"]
            ImageName=SlideImage.filename
            im1 = Image.open(SlideImage)
            im1.save("D:/FYP CODE/FLASK WORK/static/"+ImageName)
            cur.find_one_and_update({"title":"LAYOUT"},{"$set":{img_no:ImageName}})
            flash("Slider Suceessfully Updated","success")
            return redirect("/UpdateBackgroundLayout")
        else:
            flash("Incorrect File","danger")
            return redirect("/UpdateNormalSlider")
    else:
        flash("Incorrect Key","danger")
        return redirect("/UpdateNormalSlider")

@app.route("/UpdateSeaViewSlider")
@md_logged_in
def uss():
    title="sea_view"
    return render_template("UpdateSlider.html",title=title)

@app.route("/UpdateSeaViewSliderProcess",methods=["GET","POST"])
@md_logged_in
def ussp():
    data=request.form
    global administration_key
    if data["key"]==administration_key:
        if "update" in request.files:
            img_no="S2"+str(data["slide_no"])
            cur=mongo.db.AutonomousServingSystem
            SlideImage=request.files["update"]
            ImageName=SlideImage.filename
            im1 = Image.open(SlideImage)
            im1.save("D:/FYP CODE/FLASK WORK/static/"+ImageName)
            cur.find_one_and_update({"title":"LAYOUT"},{"$set":{img_no:ImageName}})
            flash("Slider Suceessfully Updated","success")
            return redirect("/UpdateBackgroundLayout")
        else:
            flash("Incorrect File","danger")
            return redirect("/UpdateSeaViewSlider")
    else:
        flash("Incorrect Key","danger")
        return redirect("/UpdateSeaViewSlider")

@app.route("/UpdateLuxurySlider")
@md_logged_in
def uls():
    title="luxury"
    return render_template("UpdateSlider.html",title=title)

@app.route("/UpdateLuxurySliderProcess",methods=["GET","POST"])
@md_logged_in
def ulsp():
    data=request.form
    global administration_key
    if data["key"]==administration_key:
        if "update" in request.files:
            img_no="S3"+str(data["slide_no"])
            cur=mongo.db.AutonomousServingSystem
            SlideImage=request.files["update"]
            ImageName=SlideImage.filename
            im1 = Image.open(SlideImage)
            im1.save("D:/FYP CODE/FLASK WORK/static/"+ImageName)
            cur.find_one_and_update({"title":"LAYOUT"},{"$set":{img_no:ImageName}})
            flash("Slider Suceessfully Updated","success")
            return redirect("/UpdateBackgroundLayout")
        else:
            flash("Incorrect File","danger")
            return redirect("/UpdateLuxurySlider")
    else:
        flash("Incorrect Key","danger")
        return redirect("/UpdateLuxurySlider")

@app.route("/Services")
def s():
    sessions.session["services"]=True
    cur=mongo.db.AutonomousServingSystem
    result=cur.find_one({"title":"services"})
    return render_template("Services.html",session=sessions.session,data=result)

@app.route("/Contact")
def C():
    sessions.session["contact"]=True
    return render_template("Contact.html")

@app.route("/Feedback",methods=["GET","POST"])
def fb():
    if request.method == 'POST':
        data=request.form
        cursor=mongo.db.CustomerFeedback
        cursor.insert_one({"title":"feedback","email":data["email"],"msg":data["msg"]})
        return redirect("/")

@app.route("/AST_Portal",methods=["GET","POST"])
@chef_logged_in
def astp():
    return render_template("AST_UI.html")

@app.route("/AST_Command",methods=["GET","POST"])
@chef_logged_in
def astc():
    data=request.form
    cur=mongo.db.AutonomousServingSystem
    global CHEFKEY
    if data["ck"]==CHEFKEY:
        today = date.today()
        d = today.strftime("%B %d, %Y")
        cur.insert_one({"title":"AST_Order","room":data["rn"],"customer_name":data["cn"],"chef_id":sessions.session["id"],"status":"not_delivered","date":d})
        flash("Command Assigned","success")
        return redirect("/ChefPortal")
    else:
        flash("Incorrect Key","danger")
        return redirect("/ChefPortal")

@app.route("/Login",methods=["GET","POST"])
def l():
    return render_template("Login.html")

@app.route("/Help",methods=["GET","POST"])
def help():
    if "email" in sessions.session:
        cur=mongo.db.CustomerCommunication
        result=cur.find_one({"email":sessions.session["email"]})
        print(result)
        if result==None:
            cur.insert_one({"email":sessions.session["email"],"message":0,"reply":0})
            return render_template("Help.html")
        else:
            history=[]
            for k,v in enumerate(result):
                if k<=3:
                    pass
                else:
                    history.append(result[v])
            return render_template("Help.html",data=history)
    else:
        data=request.form
        if data:
            cur=mongo.db.CustomerCommunication
            sessions.session["email"]=data["email"]
            result=cur.find_one({"email":sessions.session["email"]})
            if result==None:
                cur.insert_one({"email":data["email"],"message":0,"reply":0})
                return render_template("Help.html")
            else:
                history=[]
                for k,v in enumerate(result):
                    if k<=3:
                        pass
                    else:
                        history.append(result[v])
                return render_template("Help.html",data=history)
        else:
            return redirect("/Login")

def chatbot(msg):
    dictionary={"how are you":"Fine and you","i have some problems can you solve it":"Yeah! Tell me",
    "can i book a room":"For Booking Call:+923332140546","i have problem":"Tell me","what your name":"ASSBot",
    "there is an lagging issue in website":"Thank for comment! resolve is earlier","i forgot my password":
    "Call +923332140546 for new password","i forgot my username":"Call +923332140546","hi":"hello","hello":"Hi",
    "i dont have your hotel location can you send it to me":"Indus Unversity","location":"Indus University","fine":"Good",
    "thanks":":)","thank you":":)"}
    message=msg.lower()
    try:
        return dictionary[message]
    except:
        return "The admin is not available right now for contact AutonomousServingSystem.com/Contact"

@app.route("/SentMessage",methods=["GET","POST"])
def sm():
    data=request.form
    msg=data["message"]
    cur=mongo.db.CustomerCommunication
    result=cur.find_one({"email":sessions.session["email"]})
    if result:
        nom=int(result["message"])
        message_key="msg"+str(nom)
        cur.find_one_and_update({"email":sessions.session["email"]},{"$set":{"message":nom+1,message_key:msg}})
        reply=chatbot(msg)
        nor=int(result["reply"])
        reply_key="reply"+str(nor)
        cur.find_one_and_update({"email":sessions.session["email"]},{"$set":{"reply":nor+1,reply_key:reply}})
        return redirect("/Help")
    else:
        return redirect("/Login")

@app.route("/UpdateServices",methods=["GET","POST"])
@md_logged_in
def us():
    return render_template("UpdateServices.html")

@app.route("/UpdateServicesProcess",methods=["GET","POST","UPDATE"])
@md_logged_in
def usp():
    data=request.form
    service=data["services"]
    cur=mongo.db.AutonomousServingSystem
    global administration_key
    if data["key"]==administration_key:
        cur.find_one_and_update({"title":"services"},{"$set":{data["package"]:service}})
        flash("Services Updated","success")
        return redirect("/Setting")
    else:
        flash("Incorrect Key","danger")
        return redirect("/Setting")

@app.route("/ChangeMDPassword",methods=["GET","POST"])
@md_logged_in
def cmdp():
    return render_template("ChangeMDPassword.html")

@app.route("/ChangeMDPasswordProcess",methods=["GET","POST","UPDATE"])
@md_logged_in
def cmdpp():
    data=request.form
    if data["pass"]==data["confirm_pass"]:
        password=sha256_crypt.encrypt(str(data["pass"]))
        cur=mongo.db.AutonomousServingSystem
        cur.find_one_and_update({"id":sessions.session["id"],"post":"MD"},{"$set":{"password":password}})
        flash("Password Updated","success")
        return redirect("/MDPortal")
    else:
        flash("Incorrect Confirm Password","danger")
        return redirect("/ChangeMDPassword")

@app.route("/ChangeAdminPassword",methods=["GET","POST"])
@admin_logged_in
def cadp():
    return render_template("ChangeAdminPassword.html")

@app.route("/ChangeAdminPasswordProcess",methods=["GET","POST","UPDATE"])
@admin_logged_in
def cadpp():
    data=request.form
    if data["pass"]==data["confirm_pass"]:
        password=sha256_crypt.encrypt(str(data["pass"]))
        cur=mongo.db.AutonomousServingSystem
        cur.find_one_and_update({"id":sessions.session["id"],"title":"Admin"},{"$set":{"password":password}})
        flash("Password Updated","success")
        return redirect("/AdminPortal")
    else:
        flash("Incorrect Confirm Password","danger")
        return redirect("/ChangeAdminPassword")

@app.route("/ChangeChefPassword",methods=["GET","POST"])
@chef_logged_in
def ccdp():
    return render_template("ChangeChefPassword.html")

@app.route("/ChangeChefPasswordProcess",methods=["GET","POST","UPDATE"])
@chef_logged_in
def ccdpp():
    data=request.form
    if data["pass"]==data["confirm_pass"]:
        password=sha256_crypt.encrypt(str(data["pass"]))
        cur=mongo.db.AutonomousServingSystem
        cur.find_one_and_update({"id":sessions.session["id"],"title":"Chef"},{"$set":{"password":password}})
        flash("Password Updated","success")
        return redirect("/ChefPortal")
    else:
        flash("Incorrect Confirm Password","danger")
        return redirect("/ChangeChefPassword")

@app.route("/ASTMC")
def ASTMC():
    os.chdir(r"C:\Windows\system32") 
    subprocess.Popen("mstsc.exe")
    return render_template("ASTMC.html")

@app.route("/OrderArived",methods=["GET","POST"])
@customer_logged_in
def oa():
    for i in range(2):  
        mixer.init() 
        mixer.music.load("OrderArrivedMessage.mp3")
        mixer.music.set_volume(1) 
        mixer.music.play()
        if i<2:
            time.sleep(5)
    return render_template("OrderArrived.html",session=sessions.session)

@app.route("/orderRecieved")
@customer_logged_in
def orderRecieved():
    cursor=mongo.db.AutonomousServingRobot
    cursor.find_one_and_update({"customer_name":sessions.session["username"],"room":sessions.session["room_no"]},{"$set":{"status":"Recieved"}})
    if sessions.session["package"]=="Normal":
        return redirect("/CustomerNormalPortal")
    elif sessions.session["package"]=="Luxury":
        return redirect("/CustomerLuxuryPortal")
    elif sessions.session["package"]=="Luxury":
        return redirect("/CustomerSeaViewPortal")
    else:
        return redirect("/")        

@app.route("/T&S")
def ts():
    return render_template("T&S.html")

@app.route("/lift")
def lift():
    cur=mongo.db.Lift
    data=cur.find_one({"Title":"Lift"})
    return render_template("Lift.html",data=data)

if __name__=='__main__':
    app.run(debug = True,port=1267)
