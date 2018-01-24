import sqlite3
import itertools
import random
from operator import itemgetter, attrgetter
from random import *


basket = {}


current_id = -11

def login(login_type):
    global c, conn,current_id
 
    if login_type == "c":
        sign = input("Sign in(i)/Sign up(u): ")
        if sign == "i":
            # complete later
            c_id = input("Please enter your customer id: \n")
            c_pwd = input("Please enter your password: \n")
             # check valid
            valid = check_exist(c_id, c_pwd)
             

            if valid:
                current_id = c_id
                customers(c_id)
            else:
                print("Login failed, Please try again")
                login(login_type)
                #if valid == True:
            login(login_type)
        elif sign == "u":
            # complete later
            c_id = input("Please  enter your new customer id: \n")
            c_pwd = input("Please enter your new password: \n")

            valid = check_id(c_id)
            
            
            if valid:
                name = input("Please enter your name\n")
                address = input("Please enter your address\n")
                
                c.execute("INSERT INTO customers VALUES (?,?,?,?);", (c_id, name, address, c_pwd))
                #c.execute("INSERT INTO Contacts VALUES (?, ?, ?, ?);", (firstname, lastname, phone, email))
                conn.commit()
                print("success registry")
                login(login_type)                
            else:
                print("failed, plz regi again")
                login(login_type)

        else:
            print("login error")
            login(login_type)

    elif login_type == "a":
        a_id = input("Please enter your agent id: \n")
        a_pwd = input("Please enter your password: \n")
        # check valid
        valid = check_existA(a_id,a_pwd)
    
        if valid == True:
            current_id = (a_id)
            agents(current_id)
        else:
            print("Incorrect id or password")
def log_out():
    current_id = "dfasefsdgadfsgadgasdfasdfahhjkk"
    basket={}
    
    login_type = select_type() 
    login(login_type)    
    
def select_type():

    login_type = input("Choose your login type: customer(c)/agent(a)\nenter e to exit\n")

    if login_type == "c":
        print("customers login")
    elif login_type == "a":
        print("agents login")
    elif login_type == "e":
        exit(1)
    else:
        print("error")
        login_type = select_type()

    return login_type

def check_id(user_id):
    global c, conn,current_id
    
    c.execute("SELECT cid FROM customers WHERE cid=:id;", {"id":user_id}) 
    row = c.fetchone()
    if row == None:
        valid = True
    else:
        valid = False
    return valid


def check_exist(c_id, c_pwd):
    global c, conn,current_id
 
    c.execute("SELECT cid FROM customers WHERE cid=:id AND pwd=:pd;", {"id":c_id,"pd":c_pwd}) 
    row = c.fetchone()
    
    if row == None:
        valid = False
    else:
        valid = True
    
    return valid

def check_existA(a_id, a_pwd):
    global c, conn,current_id

    c.execute("SELECT aid FROM agents WHERE aid=:id AND pwd=:pd;", {"id":a_id,"pd":a_pwd}) 
    row = c.fetchone()
    
    if row == None:
        valid = False
    else:
        valid = True
    
    return valid
#customers
def customers(user_id):
    global c, conn,current_id
    global bakset

    print("Here is current item in your \n", basket)
    function_type = input('Here are avaliable functions\n Search for products(Enter s)\n Place an order(Enter p)\n List orders(Enter l)\n Logout(Enter o)\n')

    if function_type == "s":
        search(user_id)
        customers(user_id)
    elif function_type == "p":
        place_order(user_id)
        customers(user_id)
    elif function_type == "l":
        list_order(user_id)
        customers(user_id)
    elif function_type == "o":
        main()
    # Search for products
def search(user_id):
    global c, conn
    global basket
    
    
    keywords =[]
    keyword = input("please enter your keywords,\n separate each keyword by whitespace:\n")
    keywords = str.split(keyword)
    parent_list = []
   
    # query 1 begins
    for each in keywords:
        #each = "'"+"%"+each+"%"+"'"
        
        c.execute("select p.pid, p.name,p.unit,count(p.pid),count(c.sid)from \
        products p ,carries c WHERE p.name LIKE ? and p.pid = c.pid group \
        by p.pid order by count(p.pid) DESC;", ('%'+each+'%',))
         
        child_tuple = c.fetchall()
        if len(child_tuple) == 0:
            print("No results")
            customers(user_id)
        for i in range(0,len(child_tuple)):
            parent_list.append(list(child_tuple[i]))
        
    numLines=len(parent_list)
    output1_list = []
    for i in range(len(parent_list)):  
        for j in range (i+1,len(parent_list)):           
            if (parent_list[i][0] == parent_list[j][0]):  
                parent_list[i][3] += parent_list[j][3]
                parent_list[j][3] = 0
    
    for i in range(len(parent_list)):  
        if (parent_list[i][3] != 0):
            output1_list.append (parent_list[i])
    numLines=len(parent_list)
    #print("length is "+str(numLines))      
    # query 1 ends, keywords lists
    
    #query 2 beings, last 7 days
    output2_list = []
    c.execute("SELECT olines.pid, sum(qty) FROM orders LEFT JOIN olines ON orders.oid = olines.oid WHERE date(odate, '+7 day') >= date('now') GROUP BY olines.pid;")
    child_tuple = c.fetchall()
    for i in range(0,len(child_tuple)):
        output2_list.append(list(child_tuple[i]))  
    #print(output2_list)
    #query 2 ends, last 7 days
    
    # query 3 begins, in stock #
    output3_list = []
    c.execute("SELECT c.pid, COUNT(s.sid) FROM carries c, stores s WHERE c.sid=s.sid AND qty>0 GROUP BY c.pid")
    child_tuple = c.fetchall()
    for i in range(0,len(child_tuple)):
        output3_list.append(list(child_tuple[i]))   
        
    #print(output3_list)
    # query 3 ends, in stock #
    
    # query 4 begins, min among all
    output4_list = []
    
    c.execute("SELECT DISTINCT c.pid, uprice FROM carries c, stores s WHERE c.sid=s.sid AND uprice <= (select min(uprice) FROM carries c2 WHERE c.pid=c2.pid);")
    child_tuple = c.fetchall()
    for i in range(0,len(child_tuple)):
        output4_list.append(list(child_tuple[i]))    
    # query 4 ends, min among all
    
    # query 5 begins, min among in stock
    output5_list = []
    
    c.execute("SELECT DISTINCT c.pid, c.uprice FROM carries c, stores s WHERE c.qty > 0 AND c.uprice <= (select min(uprice) FROM carries c2 WHERE c.pid=c2.pid AND c2.qty>0);")
    child_tuple = c.fetchall()
    for i in range(0,len(child_tuple)):
        output5_list.append(list(child_tuple[i]))    

    # query 5 ends, min among in stock
    merge(output1_list, output3_list)
    merge(output1_list, output4_list)
    merge(output1_list, output5_list)
    merge(output1_list, output2_list)
    
    output1_list = sorted(output1_list, key=itemgetter(3), reverse=True)
    
    
    count = 0  
    length = len(output1_list)
    current = []
    for n in range(length):
        count += 1
        current.append(output1_list[n])
        print(n, output1_list[n])
        if count == 5 or n == length - 1:
            ope = "wrong operations"
            while(ope == "wrong operations"):
                ope = operations()
                if ope ==  "select":
                    chosen_pid = input("Please enter product id :")
                    for item in current:
                        if item[0] == chosen_pid:
                            # details begins
                            c.execute("SELECT * FROM products WHERE pid=:id;", {"id":chosen_pid})
                            elet1 = c.fetchall()
                            print("Product id:",elet1[0][0], "\nName:",elet1[0][1], "\nUnit:",elet1[0][2],"\nCategory: ",elet1[0][3])
                            
                            c.execute("SELECT s.sid, s.name, c.qty, c.uprice FROM carries c, stores s WHERE c.sid=s.sid AND c.pid=:id GROUP BY s.sid;", {"id":chosen_pid})
                            elet2=[]
                            child_tuple = c.fetchall()
                            for i in range(0,len(child_tuple)):
                                elet2.append(list(child_tuple[i]))
                                
                            c.execute("SELECT olines.sid, sum(qty) FROM orders LEFT JOIN olines ON orders.oid = olines.oid WHERE date(odate, '+7 day') >= date('now') AND olines.pid=:id GROUP BY olines.sid;", {"id":chosen_pid})
                            elet3=[]
                            child_tuple = c.fetchall()
                            for i in range(0,len(child_tuple)):
                                elet3.append(list(child_tuple[i]))   
                            merge2(elet2, elet3)
                            firstTemp = []
                            secondTemp = []
                            
                            for i in range (len(elet2)):
                                if elet2[i][2]!= 0:
                                    firstTemp.append(elet2[i])
                                elif elet2[i][2]== 0:   
                                    secondTemp.append(elet2[i])
                                    
                            firstTemp=sorted(firstTemp,key=itemgetter(3), reverse=False)
                            secondTemp=sorted(secondTemp,key=itemgetter(3), reverse=False)
                            final = firstTemp + secondTemp
                            print(final)
                            
                            endsearch =input("Add this item yes/y,no/n: ")
                            if endsearch =="y":
                                store_id=input("Where are you gona buy it from?, Plz enter store id/n")
                                newqty = input("How much are you gona buy it/n")
                                if newqty == None:
                                    newqty =1
                                newItem={chosen_pid + ' '+ str(store_id):newqty}
                                basket.update(newItem)
                                return
                            if endsearch =="n":
                                customers(user_id)
                                return
                            #details ends
                        elif item == current[-1]:
                            print("no matching")
                            ope = "wrong operations" 
            count = 0
            current = []

def operations():
    global c, conn,current_id
    
    print("Commands: nextpage, select")
    a_input = input("Please enter command :")
    if a_input == "nextpage":
        return "nextpage"
    elif a_input == "select":
        return "select"
    else:
        print("wrong operations")
        return "wrong operations"
        
    #return 0
def merge(output, adder):
    for i in range(len(output)):  
        for j in range (len(adder)):           
            if (output[i][0] == adder[j][0]):  
                output[i].append(adder[j][1])
def merge2(output, adder):
    for i in range(len(output)):  
        for j in range (len(adder)):           
            if (output[i][0] == adder[j][0]):  
                output[i].append(adder[j][1])
    for i in range(len(output)): 
        if len(output[i]) != 5:
            output[i].append(0) 
def place_order(user_id):
    global c, conn,current_id, basket
    valid = True
    oid = randint(1, 1000)
    c.execute("SELECT oid FROM olines;")
    oids = c.fetchall()
    while ( oid in oids):
        oid = randint(1, 1000)
    if oid not in oids:
        print(user_id, type(user_id))
        c.execute("SELECT address FROM customers WHERE cid =:id;", {"id":user_id})
        tempaddress = c.fetchone()    
        address = tempaddress[0]
    while(valid ):
        # CHECK QTY AND WARNING 
        for item in basket:
            tempt = str.split(item, ' ')

            value = basket[item]

            c.execute("SELECT qty FROM carries WHERE pid =? AND sid =?;", (tempt[0], tempt[1]))
            qty = c.fetchone()
            qty=list(qty)
           
            # CHANGE QTY, DELETE PRODUCT
            new_qty = 0
            while (qty[0] < int(value)):
                new_qty = input("Not enough quantity in stock for "+ tempt[0] +" please enter new quantity to buy(0 means delete):\n")             
                valid = False
                basket[item] = new_qty
                value = new_qty         
    # UPDATE DB
            booked = qty[0]-int(new_qty)           
            c.execute("UPDATE carries SET qty=? WHERE sid=? and pid=?;",(booked,tempt[1], tempt[0]))
            conn.commit() 
            c.execute("SELECT uprice FROM carries WHERE pid =? AND sid =?;", (tempt[0], tempt[1]))
            uprice = c.fetchone()
            uprice=list(uprice)
            c.execute("INSERT INTO orders VALUES ((?),(?),datetime('now'), (?));", (oid,user_id,address))
            conn.commit()             
            c.execute("insert into olines values (?, ?, ?, ?, ?);",(int(oid),int(tempt[1]),str(tempt[0]),int(new_qty),float(uprice[0])))
            conn.commit() 
    # CLEAR BASKET and commit all the changes

        basket={}
        customers(user_id)
def list_order(user_id):
    global c, conn,current_id, basket
    
    #current_cid = "c50"
    c.execute("SELECT o.oid, o.odate, COUNT(distinct l.pid), SUM(l.qty * l.uprice) FROM orders o LEFT JOIN olines l \
    ON o.oid = l.oid GROUP BY o.oid HAVING o.cid =:cid ORDER BY o.odate;", {"cid":user_id})
    
    orders_output = c.fetchall()
    
    show_list = []
    for i in range(len(orders_output)):
        show_list.append(orders_output[i])
        length = len(orders_output) - 1
        if (i + 1) % 5 == 0 or i == length:
            valid = False
            while(not valid):
                for j in range(len(show_list)):
                    print(show_list[j])         
                    
                user_action = input("Please enter detail to select an order to show details\n Please enter nextpage to show more orders: \n Please enter exit to leave: ")
                #user_action = 
                if user_action == "detail":
                    # enter oid
                    chosen_oid = input("Please enter order id: ")
                    chosen_oid = int(chosen_oid)
                    print(chosen_oid)
                    #tracking details
                    c.execute("SELECT d.trackingno, d.pickUpTime, d.dropOffTime, od.address FROM deliveries d, orders od WHERE d.oid = od.oid AND od.oid =:id;", {"id":chosen_oid})
                    details1 = c.fetchall()
                    # product details
                    c.execute("SELECT l.sid, s.name, l.pid, p.name, l.qty, p.unit, l.uprice FROM olines l, products p, stores s WHERE l.sid = s.sid AND l.pid = p.pid AND l.oid =:oid GROUP BY l.pid;", {"oid":chosen_oid})
                    details2 = c.fetchall()
                    
                    print("delivery information")
                    print("trackingno pickUpTime dropOffTime address")
                    print(details1)
                    
                    print("products information")
                    print("sid sname pid pname qty unit uprice")
                    print(details2)
                    
                    valid = False        
                elif user_action == "nextpage":
                    valid = True
                    show_list = []
                elif user_action == "exit":
                    show_list = []
                    return
                else:
                    print("wrong action, please enter command again")
                    valid = False  
#agents
def agents (user_id):
    global c, conn,current_id, basket
    function_type = input("Here are avaliable functions\n Set up a delivery(Enter s)\n Update a delivery(Enter u)\n Add to stock(Enter a)\n log out(Enter o)\n")
    if function_type == "s":
        setup(user_id)
        agents(user_id)
    elif function_type == "u":
        Update(user_id)
        agents(user_id)
    elif function_type == "a":
        add(user_id)
        agents(user_id)
    elif function_type == "o":
        main() 
def setup(user_id):
    global c, conn, basket, current_id

    #create a delivery
    
    # create trackingno
    trackingno = randint(1000, 100000)
    c.execute("SELECT trackingno FROM deliveries;")
    trackingno_list = c.fetchall()    
    while (trackingno in trackingno_list):
        trackingno = randint(1000, 100000)
    # done trackingno
    # enter oids
    done = False
    add_list = []    
    while(not done):
        command = input("Please choose to add orders(add) or finish adding(fin): ")
        if command == "add":
            exist = False
            c.execute("SELECT oid FROM olines;")
            oids = c.fetchall()
            for i in range(len(oids)):
                oids[i] = list(oids[i])
            for i in range(len(oids)):
                oids[i] = oids[i][0] 
            while(not exist):
                valid = True
                not_assigned = True              
                print("Please enter end to finishing adding")
                order_id = input("Please add orders to deliveries: ")
                if order_id == "end":
                    break
                else:
                    for each in order_id:
                        if each not in ("0","1","2","3","4","5","6","7","8","9"):
                            print("wrong order number, please enter numbers only")
                            valid = False
                            break
                if valid:
                    c.execute("SELECT trackingno, oid FROM deliveries;")
                    tracking_lists = c.fetchall()
                    for each in tracking_lists:                    
                        if each[1] == int(order_id):
                            print("order has already been assigned")
                            not_assigned = False
                            break
                    if not_assigned:
                        order_id = int(order_id)
                        if order_id in oids:
                            add_list.append(order_id)
                            print("Successfully added")
                            exist = True
                        else:
                            print("Order does not exist")
        elif command == "fin":
            done = True
        else:
            print("wrong command, please enter again")
    #finish adding
    # check validility
    # add pickup time y/n
    pickup_list = []
    for i in range(len(add_list)):
        print("order_id", add_list[i])
        choice = input("Add a pickup time y/n: ")
        print(add_list)
        if choice == "y":
            year = input("Enter year: ")
            month = input("Enter month: ")
            day = input("Enter day: ")
            
            date = year + '-' + month + '-' + day
            pickup_list.append(date)
        else:
            adder = None
            pickup_list.append(adder)
    # finish adding pickup time
    for i in range(len(add_list)):
        c.execute("INSERT INTO deliveries VALUES(?,?,?,?);", (trackingno,add_list[i],pickup_list[i], None))
        conn.commit()
     
    print("Created tracking number is ", + trackingno)
    print("trackingno is created successfully")
    
    #add orders to a delivery (some with and others without a pick up time)        
    
    print("setup")
def Update(user_id):
    global c, conn,current_id, basket
    
    trackingNo = input("Plese enter trackingNo")
    c.execute("select * from deliveries d where d.trackingNo =:num;", {"num":int(trackingNo)})
    out_list = c.fetchall()
    print(out_list)
    order_list = []
    for i in range(len(out_list)):
        order_list.append(list(out_list[i]))
    
    for i in range(len(order_list)):
        print("oid, pickUpTime, dropOffTime")
        print(order_list[1:])
    command = input("Please choose to update orders(u) or finish adding(end) or delete an order(d): ")
    if command == "u":
        valid = False
        while(not valid): 
            good_id = True
            
            print("Please enter id for choosing or end to leave: ")
            order_id = input("Please enter order id to update: ")  
            for each in order_id:
                if each not in ("0","1","2","3","4","5","6","7","8","9"):
                    print("wrong order number, please enter numbers only")
                    good_id = False
                    break
            if order_id == "end":
                break            
            if good_id:
                order_id = int(order_id)
                
                for i in range(len(order_list)):
                    if order_id == order_list[i]:
                        valid = True
                        break
                    elif i == len(order_list) - 1:
                        print("Can not find matching order, please enter again")
                        valid = False
        
        if order_id != "end":
            inp = input("Wanna update pickup time? y/n: ")
            sign1 = False
            sign2 = False
            
            if inp == "y":
                sign1 = True
                print("Please enter new pickup date and time")
                year1 = input("Enter year: ")
                month1 = input("Enter month: ")
                day1 = input("Enter day: ")   
                date1 = year1 + '-' + month1 + '-'+ day1
            inp = input("Wanna update dropoff time? y/n: ")
            if inp == "y":
                sign2 = True
                print("Please enter new dropoff date and time")
                year2 = input("Enter year: ")
                month2 = input("Enter month: ")
                day2 = input("Enter day: ")               
                date2 = year2 + '-' + month2 + '-'+ day2
                
            # insert
            #c.execute("INSERT INTO deliveries VALUES(?,?,?,?);", (trackingno,add_list[i],pickup_list[i], None))
            
            c.execute("UPDATE deliveries SET pickUpTime = ?, dropOffTime = ?, where trackingno = ?, oid = ?;", (date1, date2, int(trackingNo), int(order_id)))
            conn.commit()
            agent(user_id)
    elif command == "d":
        success = False
        while(not success):
            order_id = input("Please enter order id to delete or enter (end) to cancel: ")   
            for each in order_id:
                if each not in ("0","1","2","3","4","5","6","7","8","9"):
                    print("wrong order number, please enter numbers only")
                    good_id = False
                    break
            if good_id:
                for i in range(len(order_list)):
                    if order_id == order_list[i][1]:
                        success = True
                        break
                    elif i == len(order_list) - 1:
                        print("Can not find matching order, please enter again")
                        success = False
        if order_id != "end":
            c.execute("DELETE FROM deliveries WHERE trackingNo = ?, oid = ? ;", (int(trackingNo), int(order_id)))
            conn.commit()             
                
    print("Update")     
def add(user_id):
    global c, conn,current_id, basket
    valid = False
    while(not valid):
        p_id = input("Please enter product id\n")
        s_id = input("Please enter store id\n")
        for each in s_id:
                if each not in ("0","1","2","3","4","5","6","7","8","9"):
                    print("invalide info entered")
                    add(user_id)
                else:    
                    s_id= int(s_id)
        
        qty  = input("Please enter qty\n")
        for each  in qty:
            if each not in ("0","1","2","3","4","5","6","7","8","9"):
                print("invalide info entered ")
                add(user_id)
            else:    
                qty = int(qty)
     
        uprice = input("Please enter uprice(must > 0,0 means don't change uprice) \n")
        for each in uprice:
            if each not in ("0","1","2","3","4","5","6","7","8","9","."):
                print("invalide info entered")
                add(user_id)      
            else:
                uprice = float(uprice)
        commit = input("Are you sure you want to commit all the changes? y/n \n ")
        
        if commit == "y":
            if(uprice >0):
                c.execute("UPDATE carries SET qty=?,uprice =? where sid=? and pid=?;",(qty,uprice,s_id, p_id))
                conn.commit() 
                valid = True
                print("update sucess")
            elif(uprice == 0 ):
                c.execute("UPDATE carries SET qty=? where sid=? and pid=?;",(qty,s_id, p_id,))
                conn.commit()   
                valid = True
                print("update sucess")


def main():
    global c, conn,current_id, basket
    database =input("Please enter database name\n")
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys=ON;')    
    login_type = select_type() 
    login(login_type)
    


main()