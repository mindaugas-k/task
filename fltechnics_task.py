import config
import psycopg2
import smtplib
import email.message


filename_europe = 'aircrafts_europe.sql'
filename_other = 'aircrafts_other.sql'

blue_color = '#D6EAF8'
red_color = '#FADBD8'
white_color = '#FFFFFF'

def get_aircrafts(cursor, filename):
    # execute an SQL statement from file named filename
    file = open(filename, 'r')
    sql = " ".join(file.readlines())
    cursor.execute(sql)
    # obtain aircraft list from cursor
    aircrafts = cursor.fetchall()
    file.close()
    return aircrafts

def get_html_skeleton():
    file = open('email_skeleton.html')
    html_skeleton = "".join(file.readlines())
    file.close()
    return html_skeleton
    
def get_aircraft_formating():
    file = open('aircraft_formating.txt', 'r')
    form = "".join(file.readlines())
    file.close()
    return form
 
def send_mail(html):    
    
    msg = email.message.Message()
    msg['Subject'] = 'fltechnics task'
    msg['From'] = 'e86bc104329205'
    msg['To'] = 'mindaugas.kepalas@gmail.com'
    password = "6fce505d45a7f7"
    
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(html)
 
    s = smtplib.SMTP('smtp.mailtrap.io: 2525')
    s.starttls()
 
    # Login Credentials for sending the mail
    s.login(msg['From'], password) 
    s.sendmail(msg['From'], [msg['To']], msg.as_string())   
    
def perform_task():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection to PosgreSQL DB parameters
        params = config.config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
 
        # create a cursor
        cur = conn.cursor()
        
        # perform sql statement to get the table of aircrafts from Europe
        aircrafts_europe = get_aircrafts(cur, filename_europe)

        # perform sql statement to get the table of aircrafts from other continents
        aircrafts_other = get_aircrafts(cur, filename_other)
        
        # email html skeleton
        html_skeleton = get_html_skeleton()
        
        # each of aircrafts has a html form where information has to be filled
        form = get_aircraft_formating()
        
        # form a html code for aircrafts from Europe
        aircrafts_europe_html = ''        
        for aircraft in aircrafts_europe:
            color = blue_color
            if (aircraft[6]=='F'):
                color = red_color
            aircrafts_europe_html = aircrafts_europe_html + form.format(color, aircraft[0], aircraft[1], aircraft[2], aircraft[3], aircraft[4], aircraft[5])
        
        # form a html code for aircrafts from other continents
        aircrafts_other_html = ''        
        for aircraft in aircrafts_other:
            color = white_color
            aircrafts_other_html = aircrafts_other_html + form.format(color, aircraft[0], aircraft[1], aircraft[2], aircraft[3], aircraft[4], aircraft[5])        
            
        # finish html email
        html = html_skeleton.format(aircrafts_europe_html, aircrafts_other_html)
        
        # send email through SMTP sever. 
        # to be able to send an email it must be in ascii encoding, 
        # symbols not from ascii are replaced
        send_mail(html.encode('ascii','replace'))        
            
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
 
 
if __name__ == '__main__':
    perform_task()