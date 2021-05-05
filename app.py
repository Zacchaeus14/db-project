from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import json
import datetime
import calendar
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
import os
import glob
import numpy as np
import random
import hashlib
mpl.use('Agg')
mpl.is_interactive()
app = Flask(__name__)
dbconfig = json.load(open("dbconfig.json"))
conn = mysql.connector.connect(host=dbconfig['host'], user=dbconfig['user'],
                               password=dbconfig['password'], database=dbconfig['database'])

def get_md5(s):
    md = hashlib.md5()
    md.update(s.encode('utf-8'))
    return md.hexdigest()


@app.route("/")
def public():
    stype = request.args.get('stype')
    dtype = request.args.get('dtype')
    src = request.args.get('src')
    dst = request.args.get('dst')
    date_search = request.args.get('date_search')
    flight_num = request.args.get('flight_num')
    datetype = request.args.get('datetype')
    date_check = request.args.get('date_check')
    flights = None
    statuses = None
    cursor = conn.cursor()
    if src:
        if stype == "city" and dtype == "city":
            query = """select * from flight, airport a1, airport a2
                    where departure_airport = a1.airport_name and a1.airport_city = '{}'
                    and arrival_airport = a2.airport_name and a2.airport_city = '{}'
                    and departure_time LIKE '{}%' and status = 'upcoming'"""
        elif stype == "airport" and dtype == "city":
            query = """select * from flight, airport
                    where departure_airport = '{}'
                    and arrival_airport = airport.airport_name and airport.airport_city = '{}'
                    and departure_time LIKE '{}%' and status = 'upcoming'"""
        elif stype == "city" and dtype == "airport":
            query = """select * from flight, airport
                    where departure_airport = airport.airport_name and airport.airport_city = '{}'
                    and arrival_airport = '{}'
                    and departure_time LIKE '{}%' and status = 'upcoming'"""
        else:
            query = """select * from flight
                    where departure_airport = '{}'
                    and arrival_airport = '{}'
                    and departure_time LIKE '{}%' and status = 'upcoming'"""
        cursor.execute(query.format(src, dst, date_search))
        flights = cursor.fetchall()
    if flight_num:
        query = """select status from flight
                where flight_num = '{}' and {}_time LIKE '{}%'"""
        cursor.execute(query.format(flight_num, datetype, date_check))
        statuses = cursor.fetchall()
    cursor.close()
    kwargs = dict(
        stype=stype,
        dtype=dtype,
        src=src,
        dst=dst,
        date_search=date_search,
        flight_num=flight_num,
        datetype=datetype,
        date_check=date_check
    )
    for k, v in kwargs.items():
        if v == None:
            kwargs[k] = ""
    if "usertype" not in session:
        usertype = ""
    else:
        usertype = session["usertype"]
    return render_template('public.html', **kwargs, flights=flights, statuses=statuses, usertype=usertype)


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/register")
def signup():
    return render_template('register.html')


@app.route('/login_c')
def login_c():
    return render_template('login_c.html')


@app.route('/login_s')
def login_s():
    return render_template('login_s.html')


@app.route('/login_b')
def login_b():
    return render_template('login_b.html')


@app.route("/register_c")
def register_c():
    return render_template('register_c.html')


@app.route("/register_s")
def register_s():
    return render_template('register_s.html')


@app.route("/register_b")
def register_b():
    return render_template('register_b.html')

# Authenticates the login Customer


@app.route('/loginAuthC', methods=['GET', 'POST'])
def loginAuthC():
    # grabs information from the forms
    username = request.form['email']
    password = request.form['password']

    password = get_md5(password+"SSC")

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM customer WHERE email = \'{}\' and password = \'{}\'"
    cursor.execute(query.format(username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        name = data[1]
        session['username'] = name
        session['usertype'] = "customer"
        return redirect(url_for('customer_page'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login_c.html', error=error)

# Authenticates the login Booking Agent


@app.route('/loginAuthB', methods=['GET', 'POST'])
def loginAuthB():
    # grabs information from the forms
    username = request.form['email']
    password = request.form['password']
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM booking_agent WHERE email = \'{}\' and password = \'{}\'"
    cursor.execute(query.format(username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        session['usertype'] = "booking_agent"
        return redirect(url_for('booking_agent_page'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login_b.html', error=error)

# Authenticates the login Airline Staff


@app.route('/loginAuthS', methods=['GET', 'POST'])
def loginAuthS():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM airline_staff WHERE username = \'{}\' and password = \'{}\'"
    cursor.execute(query.format(username, password))
    # stores the results in a variable
    profile = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(profile):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        session['usertype'] = "staff"

        # get this user's airline name
        cursor = conn.cursor()
        query = """select distinct airline_name from airline_staff
                    where username='{}'"""
        cursor.execute(query.format(username))
        session['airline_name'] = cursor.fetchone()[0]
        cursor.close()
        return redirect(url_for('homeS'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login_s.html', error=error)


# Authenticates the register Customer
@app.route('/registerAuthC', methods=['GET', 'POST'])
def registerAuthC():
    # grabs information from the forms
    email = request.form["email"]
    username = request.form['username']
    password = request.form['password']
    building_number = request.form["building_number"]
    street = request.form["street"]
    city = request.form["city"]
    state = request.form["state"]
    phone_number = request.form["phone_number"]
    passport_number = request.form["passport_number"]
    passport_expiration = request.form["passport_expiration"]
    passport_country = request.form["passport_country"]
    date_of_birth = request.form["date_of_birth"]

#   if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)

    password = get_md5(password+"SSC")

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM customer WHERE email = \'{}\'"
    cursor.execute(query.format(username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO customer VALUES(\'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\')"
        cursor.execute(ins.format(email, username, password, building_number, street, city, state,
                                  phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return redirect(url_for('public'))

# Authenticates the register Booking Agent


@app.route('/registerAuthB', methods=['GET', 'POST'])
def registerAuthB():
    # grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    booking_agent_id = request.form['booking_agent_id']

#   if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM booking_agent WHERE email= \'{}\'"
    cursor.execute(query.format(email))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO booking_agent VALUES(\'{}\', \'{}\',\'{}\')"
        cursor.execute(ins.format(email, password, booking_agent_id))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return redirect(url_for('public'))

# Authenticates the register Airline Staff


@app.route('/registerAuthS', methods=['GET', 'POST'])
def registerAuthS():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form["last_name"]
    date_of_birth = request.form["date_of_birth"]
    airline_name = request.form["airline_name"]

#   if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM airline_staff WHERE username = \'{}\'"
    cursor.execute(query.format(username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO airline_staff VALUES(\'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')"
        cursor.execute(ins.format(username, password, first_name,
                                  last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return redirect(url_for('public'))


@app.route("/homeS")
def homeS():
    return render_template('home_s.html')


@app.route('/logout')
def logout():
    try:
        session.pop('username')
        session.pop('usertype')
        session.pop('airline_name')
    except KeyError:
        pass
    return redirect('/')


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


@app.route("/staff_view_my_flights")
def staff_view_my_flights():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    stype = request.args.get('stype')
    dtype = request.args.get('dtype')
    src = request.args.get('src')
    dst = request.args.get('dst')
    flights = None
    if not start_date:
        start_date = datetime.datetime.today().strftime('%Y-%m-%d')
        end_date = add_months(datetime.date.today(), 1).strftime('%Y-%m-%d')

    airline_name = session["airline_name"]
    cursor = conn.cursor()
    if not (src or dst):
        query = """select * from flight
                where departure_time between '{} 00:00:00' and '{} 00:00:00'
                and airline_name='{}'"""
        cursor.execute(query.format(start_date, end_date, airline_name))
    elif src and (not dst):
        if stype == "airport":
            query = """select * from flight
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and departure_airport = '{}'
                    and airline_name='{}'"""
        else:
            query = """select flight.* from flight, airport
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and airport_city = '{}'
                    and departure_airport = airport_name
                    and airline_name='{}'"""
        cursor.execute(query.format(start_date, end_date, src, airline_name))
    elif (not src) and dst:
        if dtype == "airport":
            query = """select * from flight
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and arrival_airport = '{}'
                    and airline_name='{}'"""
        else:
            query = """select flight.* from flight, airport
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and airport_city = '{}'
                    and arrival_airport = airport_name
                    and airline_name='{}'"""
        cursor.execute(query.format(start_date, end_date, dst, airline_name))
    else:
        if stype == "airport" and dtype == "airport":
            query = """select * from flight
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and departure_airport = '{}'
                    and arrival_airport = '{}'
                    and airline_name='{}'"""
        elif stype == "city" and dtype == "airport":
            query = """select flight.* from flight, airport
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and airport_city = '{}'
                    and arrival_airport = '{}'
                    and departure_airport = airport_name
                    and airline_name='{}'"""
        elif stype == "airport" and dtype == "city":
            query = """select flight.* from flight, airport
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and departure_name = '{}'
                    and airport_city = '{}'
                    and arrival_airport = airport_name
                    and airline_name='{}'"""
        else:
            query = """select flight.* from flight, airport a1, airport a2
                    where departure_time between '{} 00:00:00' and '{} 00:00:00'
                    and a1.airport_city = '{}'
                    and a2.airport_city = '{}'
                    and departure_airport = a1.airport_name
                    and arrival_airport = a2.airport_name
                    and airline_name='{}'"""
        cursor.execute(query.format(
            start_date, end_date, src, dst, airline_name))

    flights = cursor.fetchall()
    cursor.close()
    flights = [list(x) for x in flights]
    for i, flight in enumerate(flights):
        for j, attribute in enumerate(flight):
            flights[i][j] = str(flights[i][j])
    kwargs = dict(
        start_date=start_date,
        end_date=end_date,
        stype=stype,
        dtype=dtype,
        src=src,
        dst=dst,
        flights=flights
    )
    for k, v in kwargs.items():
        if v == None:
            kwargs[k] = ""
    return render_template("staff_view_my_flights.html", **kwargs)


@app.route("/view_customers")
def view_customers():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    flight_num = request.args.get("flight_num")
    cursor = conn.cursor()
    query = """select distinct customer.* from purchases, ticket, customer
            where flight_num = '{}'
            and email = customer_email
            and purchases.ticket_id = ticket.ticket_id
            """
    cursor.execute(query.format(flight_num))
    customers = cursor.fetchall()
    cursor.close()
    customers = [[str(x) for x in row] for row in customers]
    # customers = json.dumps(customers)
    # remove password
    for i in range(len(customers)):
        del customers[i][2]
    kwargs = dict(
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date"),
        stype=request.args.get('stype'),
        dtype=request.args.get('dtype'),
        src=request.args.get('src'),
        dst=request.args.get('dst'),
        customers=customers
    )
    return render_template("staff_view_customers.html", **kwargs)


@app.route("/staff_create_new_flights")
def staff_create_new_flights():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    flight_num = request.args.get("flight_num")
    if not flight_num:
        return render_template("staff_create_new_flights.html", res=None)
    departure_airport = request.args.get("departure_airport")
    departure_time = request.args.get("departure_time").replace("T", " ")
    arrival_airport = request.args.get("arrival_airport")
    arrival_time = request.args.get("arrival_time").replace("T", " ")
    price = request.args.get("price")
    status = request.args.get("status")
    airplane_id = request.args.get("airplane_id")

    cursor = conn.cursor()
    query = """insert into flight values('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""
    try:
        cursor.execute(query.format(session["airline_name"],
                                    flight_num,
                                    departure_airport,
                                    departure_time,
                                    arrival_airport,
                                    arrival_time,
                                    price,
                                    status,
                                    airplane_id))
        conn.commit()
        res = flight_num
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()

    return render_template("staff_create_new_flights.html", res=res)


@ app.route("/staff_change_flights_status")
def staff_change_flights_status():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    flight_num = request.args.get("flight_num")
    if not flight_num:
        return render_template("staff_change_flights_status.html", res=None)
    status = request.args.get("status")

    cursor = conn.cursor()
    query = """select * from flight
    where flight_num = '{}'"""
    cursor.execute(query.format(flight_num))
    flights = cursor.fetchall()
    if not flights:
        res = "notfound"
        cursor.close()
        return render_template("staff_change_flights_status.html", res=res)
    query = """update flight
                set status = '{}'
                where flight_num = '{}'
                and airline_name = '{}'"""
    try:
        cursor.execute(query.format(status,
                                    flight_num,
                                    session["airline_name"]))
        conn.commit()
        res = flight_num
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()

    return render_template("staff_change_flights_status.html", res=res)


@ app.route("/staff_add_airplane")
def staff_add_airplane():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    airplane_id = request.args.get("airplane_id")
    if not airplane_id:
        return render_template("staff_add_airplane.html", res=None)
    seats = request.args.get("seats")
    cursor = conn.cursor()
    query = """select * from airplane
    where airplane_id = '{}'
    and airline_name = '{}'"""
    cursor.execute(query.format(airplane_id, session["airline_name"]))
    airplanes = cursor.fetchall()
    if airplanes:
        cursor.close()
        return render_template("staff_add_airplane.html", res="exist")
    query = """insert into airplane values ('{}', '{}', '{}')"""
    try:
        cursor.execute(query.format(
            session["airline_name"], airplane_id, seats))
        conn.commit()
        res = airplane_id
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()
    return render_template("staff_add_airplane.html", res=res)


@ app.route("/staff_add_airport")
def staff_add_airport():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    airport_name = request.args.get("airport_name")
    if not airport_name:
        return render_template("staff_add_airport.html", res=None)
    airport_city = request.args.get("airport_city")
    cursor = conn.cursor()
    query = """select * from airport
    where airport_name = '{}'"""
    cursor.execute(query.format(airport_name))
    airports = cursor.fetchall()
    if airports:
        cursor.close()
        return render_template("staff_add_airport.html", res="exist")
    query = """insert into airport values ('{}', '{}')"""
    try:
        cursor.execute(query.format(airport_name, airport_city))
        conn.commit()
        res = airport_name
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()
    return render_template("staff_add_airport.html", res=res)


@ app.route("/staff_view_booking_agents")
def staff_view_booking_agents():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    cursor = conn.cursor()
    query = """select booking_agent.*, count(*)
            from booking_agent natural join purchases natural join ticket
            where purchase_date > '{}'
            and airline_name = '{}'
            group by email
            order by count(*) DESC
            limit 5
            """
    last_month = add_months(datetime.date.today(), -1).strftime('%Y-%m-%d')
    cursor.execute(query.format(last_month, session["airline_name"]))
    data1 = cursor.fetchall()
    data1 = [[attr for attr in agent] for agent in data1]
    # remove password
    for i in range(len(data1)):
        del data1[i][1]

    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    cursor.execute(query.format(last_year, session["airline_name"]))
    data2 = cursor.fetchall()
    data2 = [[attr for attr in agent] for agent in data2]
    # remove password
    for i in range(len(data2)):
        del data2[i][1]

    query = """select booking_agent.*, sum(price)*0.1
            from booking_agent natural join purchases natural join ticket natural join flight
            where purchase_date > '{}'
            and airline_name = '{}'
            group by email
            order by sum(price) DESC
            limit 5
            """
    cursor.execute(query.format(last_year, session["airline_name"]))
    data3 = cursor.fetchall()
    data3 = [[attr for attr in agent] for agent in data3]
    # remove password
    for i in range(len(data3)):
        del data3[i][1]

    cursor.close()
    kwargs = dict(
        data1=data1,
        date1=last_month,
        data2=data2,
        date2=last_year,
        data3=data3,
        date3=last_year
    )
    return render_template("staff_view_booking_agents.html", **kwargs)


@ app.route("/staff_view_frequent_customers")
def staff_view_frequent_customers():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    cursor = conn.cursor()
    query = """
            select customer.*, count(*)
            from customer, purchases, ticket
            where customer.email = purchases.customer_email
            and ticket.ticket_id = purchases.ticket_id
            and airline_name = '{}'
            and purchase_date > '{}'
            group by email
            order by count(*) DESC
            limit 1
            """
    cursor.execute(query.format(session["airline_name"], last_year))
    top_customer = cursor.fetchall()[0]
    top_customer = [str(attr) for attr in top_customer]
    del top_customer[2]

    email = request.args.get("email")
    query = """
            select distinct flight.*
            from flight natural join purchases natural join ticket
            where customer_email = '{}'
            and airline_name = '{}'
            """
    cursor.execute(query.format(email, session["airline_name"]))
    flights = cursor.fetchall()
    flights = [[str(attr) for attr in flight] for flight in flights]

    cursor.close()
    kwargs = dict(
        top_customer=top_customer,
        last_year=last_year,
        my_airline=session["airline_name"],
        flights=flights,
        email=email
    )
    return render_template("staff_view_frequent_customers.html", **kwargs)


@ app.route("/staff_view_reports")
def staff_view_reports():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    cursor = conn.cursor()
    query = """
            select count(*)
            from purchases natural join ticket
            where airline_name = '{}'
            and purchase_date > '{}'
            """
    cursor.execute(query.format(session["airline_name"], last_year))
    amt_tck_ly = str(cursor.fetchall()[0][0])

    last_month = add_months(datetime.date.today(), -1).strftime('%Y-%m-%d')
    cursor.execute(query.format(session["airline_name"], last_month))
    amt_tck_lm = str(cursor.fetchall()[0][0])

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    amt_tck_range = None
    if start_date:
        query = """
                select count(*)
                from purchases natural join ticket
                where airline_name = '{}'
                and (purchase_date between '{} 00:00' and '{} 23:59')
                """
        cursor.execute(query.format(
            session["airline_name"], start_date, end_date))
        amt_tck_range = str(cursor.fetchall()[0][0])

    year = request.args.get("year")
    img_url = ""
    if year:
        # clear history images
        dir = './static/staff_view_reports/'
        filelist = glob.glob(os.path.join(dir, "*"))
        for f in filelist:
            os.remove(f)
        image_name = str(time.time()).split(
            '.')[-1] + '.png'  # avoid image caching
        img_url = os.path.join(dir, image_name)
        sales = []
        for month in range(1, 13):
            query = """
                    select count(*)
                    from purchases natural join ticket
                    where year(purchase_date) = '{}'
                    and month(purchase_date) = '{}'
                    and airline_name = '{}'
                    """
            cursor.execute(query.format(year, month, session["airline_name"]))
            sales.append(int(cursor.fetchall()[0][0]))
        x = [m for m in range(1, 13)]
        fig, axes = plt.subplots(1, 1)
        axes.bar(x, sales)
        axes.xaxis.set_ticks(x)
        axes.set_title(f"Monthly sales in {year}")
        axes.set_xlabel("month")
        axes.set_ylabel("sales")
        plt.savefig(img_url)

    cursor.close()

    current_year = datetime.date.today().strftime('%Y-%m-%d')[:4]
    kwargs = dict(
        amt_tck_ly=amt_tck_ly,
        amt_tck_lm=amt_tck_lm,
        start_date=start_date,
        end_date=end_date,
        amt_tck_range=amt_tck_range,
        current_year=current_year,
        img_url=img_url,
        year=year
    )
    # return json.dumps(kwargs)
    return render_template("staff_view_reports.html", **kwargs)


@ app.route("/staff_compare_revenue")
def staff_compare_revenue():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    cursor = conn.cursor()
    query = """
            select sum(price)
            from purchases natural join ticket natural join flight
            where airline_name = '{}'
            and booking_agent_id {} NULL
            and purchase_date > '{}'
            """

    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    last_month = add_months(datetime.date.today(), -1).strftime('%Y-%m-%d')

    cursor.execute(query.format(session["airline_name"], "is", last_year))
    res = cursor.fetchall()[0][0]
    direct_ly = 0 if not res else int(res)

    cursor.execute(query.format(session["airline_name"], "is not", last_year))
    res = cursor.fetchall()[0][0]
    indirect_ly = 0 if not res else int(res)

    cursor.execute(query.format(session["airline_name"], "is", last_month))
    res = cursor.fetchall()[0][0]
    direct_lm = 0 if not res else int(res)

    cursor.execute(query.format(session["airline_name"], "is not", last_month))
    res = cursor.fetchall()[0][0]
    indirect_lm = 0 if not res else int(res)

    cursor.close()

    dir = './static/staff_compare_revenue/'
    filelist = glob.glob(os.path.join(dir, "*"))
    for f in filelist:
        os.remove(f)
    image_name = str(time.time()).split(
        '.')[-1] + '.png'  # avoid image caching
    img_url = os.path.join(dir, image_name)

    x1 = [direct_ly, indirect_ly]
    x2 = [direct_lm, indirect_lm]
    labels = ["direct_sales", "indirect_sales"]

    fig, axes = plt.subplots(2)

    def func(pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}%\n({:d} $)".format(pct, absolute)


    wedges, texts, autotexts = axes[0].pie(x1, autopct=lambda pct: func(pct, x1),
                                  textprops=dict(color="w"))
    axes[0].legend(wedges, labels, loc=(1.0, 0.6))
    axes[0].set_title(f"Revenue comparison in last year")

    wedges, texts, autotexts = axes[1].pie(x2, autopct=lambda pct: func(pct, x2),
                                  textprops=dict(color="w"))
    axes[1].legend(wedges, labels, loc=(1.0, 0.6))
    axes[1].set_title(f"Revenue comparison in last month")
    plt.savefig(img_url)

    kwargs = dict(
        direct_ly=direct_ly,
        indirect_ly=indirect_ly,
        direct_lm=direct_lm,
        indirect_lm=indirect_lm,
        img_url=img_url
    )
    return render_template("staff_compare_revenue.html", **kwargs)


@ app.route("/staff_view_top_destinations")
def staff_view_top_destinations():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    cursor = conn.cursor()
    query = """
            select airport_city
            from (purchases natural join ticket natural join flight), airport
            where arrival_airport = airport_name
            and purchase_date > '{}'
            and airline_name = '{}'
            group by airport_city
            order by count(*)
            desc
            limit 3
            """
    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    last_3months = add_months(datetime.date.today(), -3).strftime('%Y-%m-%d')

    cursor.execute(query.format(last_year, session["airline_name"]))
    dsts_ly = [row[0] for row in cursor.fetchall()]

    cursor.execute(query.format(last_3months, session["airline_name"]))
    dsts_l3m = [row[0] for row in cursor.fetchall()]
    cursor.close()

    kwargs = dict(
        dsts_ly=dsts_ly,
        dsts_l3m=dsts_l3m
        )
    return render_template("staff_view_top_destinations.html", **kwargs)

@ app.route("/show_sessions")
def show_sessions():
    d = {}
    for k, v in session.items():
        d[k] = v
    return json.dumps(d)


@app.route('/customer_page')
def customer_page():
    if "username" in session:
        username = session["username"]
        return render_template("/customer_page.html", username = "Welcome! "+username, flights_rec = None, flights_found = None)

@app.route('/booking_agent_page')
def booking_agent_page():
    if "username" in session:
        username = session["username"]
        return render_template("/booking_agent_page.html", username = "Welcome! "+username, flights_rec = None, flights_found = None)

@app.route('/view_my_flights', methods = ["GET", "POST"])
def view_my_flights():
    usertype = session["usertype"]
    cursor = conn.cursor()
    choice = request.form["choice"]
    if choice == "default":
        out = None
        # cursor used to send queries

        # executes query
        if usertype == "customer":
            query = "SELECT * FROM flight where status = 'upcoming' and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name = \'{}\')"
        elif usertype == "booking agent":
            query = "SELECT * FROM flight where status = 'upcoming' and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email = \'{}\')"
        elif usertype == "staff":
            query = "SELECT * FROM flight where status = 'upcoming' and airline_name = (SELECT airline_name FROM airline_staff WHERE username =  \'{}\') and DateDiff(departure_time, CURDATE()) <= 30"
        cursor.execute(query.format(session["username"]))
        # stores the results in a variable
        out = cursor.fetchall()
        # use fetchall() if you are expecting more than 1 data row
    elif choice == "specify":
        info = request.form.getlist("info")
        cities = "SELECT airport_city FROM airport"
        cursor.execute(cities)
        res = cursor.fetchall()
        city = []
        for i in res:
            city.append(i[0])
        airports = "SELECT airport_name FROM airport"
        cursor.execute(airports)
        out = cursor.fetchall()
        airport = []
        for i in out:
            airport.append(i[0])

        place = None
        time = None

        out = []
        data1 = []
        data2 = []

        for i in info:
            if i == "date":
                time = i
            elif i == "name":
                place = i

        if time is not None:
            start = request.form["start"]
            end = request.form["end"]
            if usertype == "customer":
                query1 = "SELECT * FROM flight WHERE (departure_time between \'{}\' and \'{}\') and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name = \'{}\')"
            elif usertype == "booking agent":
                query1 = "SELECT * FROM flight WHERE (departure_time between \'{}\' and \'{}\') and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email = \'{}\')"
            elif usertype == "staff":
                query1 = "SELECT * FROM flight WHERE (departure_time between \'{}\' and \'{}\') and airline_name = (SELECT airline_name FROM airline_staff WHERE username = \'{}\')"
            cursor.execute(query1.format(start,end,session["username"]))
            data1 = cursor.fetchall()

        if place is not None:
            dept = request.form["d_name"]
            arr = request.form["a_name"]
            if dept in city and arr in city:
                if usertype == "customer":
                    query2 = "SELECT * FROM flight WHERE departure_airport in (SELECT airport_name FROM airport \
                        WHERE airport_city = \'{}\') and arrival_airport in (select airport_name from airport where airport_city = \'{}\') and flight_num in \
                        (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name = \'{}\')"
                elif usertype == "booking agent":
                    query2 = "SELECT * FROM flight WHERE departure_airport in (SELECT airport_name FROM airport \
                        WHERE airport_city = \'{}\') and arrival_airport in (select airport_name from airport where airport_city = \'{}\') and flight_num in \
                        (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email = \'{}\')"
                elif usertype == "staff":
                    query2 = "SELECT * FROM flight WHERE departure_airport in (SELECT airport_name FROM airport \
                        WHERE airport_city = \'{}\') and arrival_airport in (select airport_name from airport where airport_city = \'{}\') and airline_name = \
                        (SELECT airline_name FROM airline_staff WHERE username = \'{}\')"
                cursor.execute(query2.format(dept,arr,session["username"]))
                data2 = cursor.fetchall()
            elif dept in airport and arr in airport:
                if usertype == "customer":
                    query2 = "SELECT * FROM flight WHERE departure_airport = \'{}\' and arrival_airport = \'{}\' and flight_num in\
                            (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name = \'{}\')"
                elif usertype == "booking agent":
                    query2 = "SELECT * FROM flight WHERE departure_airport = \'{}\' and arrival_airport = \'{}\' and flight_num in\
                        (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email = \'{}\')"
                elif usertype == "staff":
                    query2 = "SELECT * FROM flight WHERE departure_airport = \'{}\' and arrival_airport = \'{}\' and airline_name =\
                        (SELECT airline_name FROM airline_staff WHERE username = \'{}\')"
                cursor.execute(query2.format(dept,arr,session["username"]))
                data2 = cursor.fetchall()
        if data1 == [] and data2 == []:
            out = []
        elif data1 != [] and data2 == []:
            out = data1
        elif data2 != [] and data1 == []:
            out = data2
        else:
            for i in data1:
                for i in data2:
                    out.append(i)
    cursor.close()
    if usertype == "customer":
        return render_template("customer_page.html", username = session["username"],flights_rec = out)
    elif usertype == "booking agent":
        return render_template("booking_agent_page.html", username = session["username"],flights_rec = out)

@app.route('/track_my_spending_c')
def track_my_spending_c():
    return render_template('track_my_spending_c.html')


@app.route('/spending_c', methods = ["GET", "POST"])
def spending_c():
    choice = request.form["choice"]
    cursor = conn.cursor()

    if choice == "default":
        year = "SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN customer WHERE name = \'{}\'\
            and DateDiff(CURDATE(), purchase_date) <= 365"
        cursor.execute(year.format(session["username"]))
        spend = cursor.fetchone()[0]
        month = "SELECT SUM(price),convert(varchar(7),purchase_date) FROM purchases NATURAL JOIN ticket NATURAL JOIN\
            flight NATURAL JOIN customer WHERE name = \'{}\' and DateDiff(CURDATE(), purchase_date) <= 365/2 GROUP BY convert(varchar(7),purchase_date)"
        cursor.execute(month.format(session["username"]))
        spent = cursor.fetchall()

        return render_template('track_my_spending_c.html', spending = spend, spent = spent)
    elif choice == "specify":
        start = request.form["start"]
        end = request.form["end"]
        year = "SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN customer WHERE name = \'{}\'\
            and purchase_date between \'{}\' and \'{}\'"
        cursor.execute(year.format(session["username"], start, end))
        spend = cursor.fetchone()[0]

        month = "SELECT SUM(price),convert(varchar(7),purchase_date) FROM purchases NATURAL JOIN ticket NATURAL JOIN\
            flight NATURAL JOIN customer WHERE name = \'{}\' and purchase_date between \'{}\' and \'{}\' GROUP BY convert(varchar(7),purchase_date)"
        cursor.execute(month.format(session["username"], start, end))
        spent = cursor.fetchall()

        return render_template('track_my_spending_c.html', spending = spend, spent = spent)

@app.route("/purchase")
def purchase():
    usertype = session["usertype"]
    username = session["username"]
    return render_template('purchase.html', username = username, usertype = usertype)

@app.route('/search_flights', methods = ["GET", "POST"])
def search_flights():
    usertype = session["usertype"]
    scity = request.args.get('scity')
    dcity = request.args.get('dcity')
    sair = request.args.get("sair")
    dair = request.args.get("dair")
    date_search = request.args.get('date_search')
    flight_num = request.args.get('flight_num')
    dateof = request.args.get('dateof')
    date_check = request.args.get('date_check')
    flights = None
    statuses = None
    cursor = conn.cursor()

    # grab all cities in the database
    querycity = "SELECT airport_city from airport"
    cursor.execute(querycity)
    citiesdata = cursor.fetchall()
    cities = []
    for i in citiesdata:
        cities.append(i[0])
    # grab all airports in the database
    queryairport = "SELECT airport_name from airport"
    cursor.execute(queryairport)
    airportsdata = cursor.fetchall()
    airports = []
    for i in airportsdata:
        airports.append(i[0])

    error1 = None
    if scity:
        if (scity not in cities) or (dcity not in cities):
            error1 = "Errors in City names, please check again and enter a correct one"
            if usertype =="booking agent" or usertype == "customer":
                return render_template('purchase.html', error = error1)
        else:
            query = """select * from flight, airport a1, airport a2
                    where departure_airport = a1.airport_name and a1.airport_city = '{}'
                    and arrival_airport = a2.airport_name and a2.airport_city = '{}'
                    and departure_time LIKE '{}%' and status = 'upcoming'"""
            cursor.execute(query.format(scity, dcity, date_search))
            flights = cursor.fetchall()
    elif sair:
        if (sair not in airports) or (dair not in airports):
            error1 = "Errors in Airport names, please check again and enter a correct one"
            if usertype =="booking agent" or usertype == "customer":
                return render_template('purchase.html', error = error1)
        else:
            query = """select * from flight, airport a1, airport a2
                    where departure_airport = a1.airport_name and a1.airport_name = '{}'
                    and arrival_airport = a2.airport_name and a2.airport_name = '{}'
                    and departure_time LIKE '{}%' and status = 'upcoming'"""
            cursor.execute(query.format(sair, dair, date_search))
            flights = cursor.fetchall()
    elif flight_num:
        query = """select status from flight
                where flight_num = '{}' and {}_time LIKE '{}%'"""
        cursor.execute(query.format(flight_num, dateof, date_check))
        statuses = cursor.fetchall()
    conn.commit()
    cursor.close()
    if usertype == "booking agent" or usertype == "customer":
        return render_template("purchase.html", flights = flights, statuses = statuses)




@app.route("/purchase_confirm")
def purchase_confirm():
    usertype = session["usertype"]
    username = session["username"]
    return render_template('purchase_confirm.html', username = username, usertype = usertype)

@app.route('/purchasing', methods = ["GET", "POST"])
def purchasing():
    airline_name = request.form["airline_name"]
    flight_num = request.form["flight_num"]
    usertype = session["usertype"]
    message1 = None
    session["airline_name"] = airline_name
    session["flight_num"] = flight_num
    cursor = conn.cursor()

    # check whether the seats of the plane is enough.
    seatcount = "SELECT seats FROM airplane NATURAL JOIN flight WHERE flight.airline_name = \'{}\' and flight.flight_num = \'{}\'"
    cursor.execute(seatcount.format(airline_name, flight_num))
    seat = cursor.fetchone()
    print(seat[0])

    ticketcount = "SELECT count(*) FROM ticket WHERE airline_name = \'{}\' and flight_num = \'{}\'"
    cursor.execute(ticketcount.format(airline_name, flight_num))
    count = cursor.fetchone()
    cursor.close()
    if count[0] >= seat[0]:
        message1 = "The ticket of this flight is sold out. Please choose from other flights."
        session.pop('airline_name')
        session.pop('flight_num')
        return render_template("purchase.html", usertype = usertype, message1 = message1)

    else:
        message1 = "Confirm your purchase information."
        return render_template("purchase_confirm.html", usertype = usertype)

@app.route('/confirm', methods = ["GET", "POST"])
def confirm():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["airline_name"]
    flight_num = session["flight_num"]
    ticket_id = random.randint(10000, 99999)
    message = "Successfully Purchased!"


    cursor = conn.cursor()
    iticket = "Insert into ticket values(\'{}\', \'{}\', \'{}\')"
    cursor.execute(iticket.format(ticket_id, airline_name, flight_num))
    conn.commit()

    if usertype == "customer":
        # executes query
        query = "SELECT * FROM customer WHERE name = \'{}\'"
        cursor.execute(query.format(username))
        # stores the results in a variable
        data = cursor.fetchone()
        username = data[0]
        ipurchase = "Insert into purchases (ticket_id, customer_email,purchase_date) values(\'{}\', \'{}\',\'{}\')"
        cursor.execute(ipurchase.format(ticket_id, username,datetime.datetime.today().strftime('%Y-%m-%d')))
        conn.commit()

    else:
        # Find booking agent id
        query = "select booking_agent_id from booking_agent where email = \'{}\'"
        cursor.execute(query.format(username))
        booking_agent_id = cursor.fetchone()
        # insert to purchases
        customer_email = request.form["customer_email"]
        ipurchase = "Insert into purchases (ticket_id, customer_email, booking_agent_id,purchase_date) values(\'{}\', \'{}\', \'{}\',\'{}\')"
        cursor.execute(ipurchase.format(ticket_id, customer_email, booking_agent_id[0],datetime.datetime.today().strftime('%Y-%m-%d')))
        conn.commit()

    cursor.close()


    session.pop('airline_name')
    session.pop('flight_num')

    return render_template("purchase_confirm.html", message = message, usertype = usertype)

@app.route('/view_commission', methods = ["GET", "POST"])
def view_commission():
    username = session["username"]
    select = request.form["select"]
    cursor = conn.cursor()

    book_id = "SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\'"
    cursor.execute(book_id.format(username))
    booking_agent_id = cursor.fetchone()[0]

    if select == "no":
        tot = "SELECT SUM(price * 0.1) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id = \'{}\'\
            and DateDiff(CURDATE(), purchases.purchase_date) <= 30"
        cursor.execute(tot.format(booking_agent_id))
        tot_com = cursor.fetchone()[0]

        ave = "SELECT SUM(price * 0.1) / COUNT(ticket_id) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id = \'{}\' \
            and DateDiff(CURDATE(), purchases.purchase_date) <= 30"
        cursor.execute(ave.format(booking_agent_id))
        ave_com = cursor.fetchone()[0]
        sold = "SELECT COUNT(ticket_id) FROM ticket NATURAL JOIN purchases WHERE booking_agent_id = \'{}\' \
            and DateDiff(CURDATE(), purchases.purchase_date) <= 30"
        cursor.execute(sold.format(booking_agent_id))
        tot_sold = cursor.fetchone()[0]

    elif select == "yes":
        start = request.form["start"]
        end = request.form["end"]
        tot = "SELECT SUM(price * 0.1) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id = \'{}\'\
            and purchases.purchase_date between \'{}\' and \'{}\'"
        cursor.execute(tot.format(booking_agent_id, start, end))
        tot_com = cursor.fetchone()[0]
        ave = "SELECT SUM(price * 0.1) / COUNT(ticket_id) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id = \'{}\' \
            and purchases.purchase_date between \'{}\' and \'{}\'"
        cursor.execute(ave.format(booking_agent_id, start, end))
        ave_com = cursor.fetchone()[0]
        sold = "SELECT COUNT(ticket_id) FROM ticket NATURAL JOIN purchases WHERE booking_agent_id = \'{}\' \
            and purchases.purchase_date between \'{}\' and \'{}\'"
        cursor.execute(sold.format(booking_agent_id, start, end))
        tot_sold = cursor.fetchone()[0]
    if tot_com == None:
        tot_com = 0
    if ave_com == None:
        ave_com = 0
    if tot_sold == None:
        tot_sold = 0

    return render_template("booking_agent_page.html", total_commission = round(tot_com,2),average_commission = round(ave_com,2), total_ticket = round(tot_sold,2), username=username)

@app.route('/customers_b')
def customers_b():
    usertype = session["usertype"]
    cursor = conn.cursor()

    username = session["username"]
    t1 = "SELECT customer_email, name, COUNT(*) FROM (purchases NATURAL JOIN booking_agent) JOIN customer ON customer_email\
            = customer.email WHERE booking_agent.email = \'{}\' and DateDiff(CURDATE(), purchase_date)<365/2 \
                GROUP BY customer.email ORDER BY count(*) DESC LIMIT 5"
    t2 = "SELECT customer_email, name, SUM(price * 0.1)/COUNT(ticket_id) FROM （purchases NATURAL JOIN booking_agent NATURAL JOIN ticket NATURAL JOIN flight) JOIN customer ON customer_email \
         = customer.email WHERE booking_agent.email = \'{}\' and DateDiff(CURDATE(), purchase_date) < 365\
              GROUP BY customer.email ORDER BY SUM(price * 0.1)/COUNT(ticket_id) DESC LIMIT 5"
    cursor.execute(t1.format(username))
    customer = cursor.fetchall()
    conn.commit()
    cursor.execute(t2.format(username))
    customer_year = cursor.fetchall()
    conn.commit()

    cursor.close()
    return render_template('customers.html', customer = customer, customer_y = customer_year, usertype = usertype)

@app.route("/public_info")
def public_info():
    scity = request.args.get('scity')
    dcity = request.args.get('dcity')
    date_search = request.args.get('date_search')
    flight_num = request.args.get('flight_num')
    dateof = request.args.get('dateof')
    date_check = request.args.get('date_check')
    flights = None
    statuses = None
    cursor = conn.cursor()
    if scity:
        query = """select * from flight, airport a1, airport a2
                where departure_airport = a1.airport_name and a1.airport_city = '{}'
                and arrival_airport = a2.airport_name and a2.airport_city = '{}'
                and departure_time LIKE '{}%' and status = 'upcoming'"""
        cursor.execute(query.format(scity, dcity, date_search))
        flights = cursor.fetchall()
    if flight_num:
        query = """select status from flight
                where flight_num = '{}' and {}_time LIKE '{}%'"""
        cursor.execute(query.format(flight_num, dateof, date_check))
        statuses = cursor.fetchall()
    cursor.close()
    return render_template('public_info.html', flights=flights, statuses=statuses)


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
