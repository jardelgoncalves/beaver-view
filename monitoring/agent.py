import mysql.connector
import requests
import json
import sys
import datetime, time

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="beaver_user",
        passwd="JNFBEEzXp397",
        database="beaver_db"
    )
except mysql.connector.errors.ProgrammingError:
    print "Falha ao conectar com o banco"
    sys.exit()


def monitoring_switches():
    mycursor = mydb.cursor()
    query = "SELECT * FROM devices"
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    DPID =None

    for device in myresult:
        DPID=device[2]
        r = requests.get("http://localhost:8080/stats/port/%i" % int(DPID,16))
        if r.status_code == 200:
            a = json.loads(r.text)
            for elem in a[str(int(DPID,16))]:
                if elem["port_no"] == "LOCAL":
                    c = mydb.cursor()
                    ultimo = "SELECT last_rx, last_tx FROM stats WHERE ip_dpid='%s' ORDER BY date DESC limit 1" %DPID
                    c.execute(ultimo)
                    consulta = c.fetchall()
                    rx = 0
                    tx = 0
                    if len(consulta) > 0:
                        rx = int(elem["rx_bytes"]) - consulta[0][0]
                        tx = int(elem["tx_bytes"]) - consulta[0][1]
                    else:
                        rx = int(elem["rx_bytes"])
                        tx = int(elem["tx_bytes"])

                    insert = "INSERT INTO stats (ip_dpid, rx, tx, last_rx,last_tx, date) VALUES ('%s', %i, %i, %i, %i, '%s')" %(
                                                            DPID, rx, tx, int(elem["rx_bytes"]),int(elem["tx_bytes"]), 
                                                            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    mycursor.execute(insert)
                    mydb.commit()
        else:
            pass

    
if __name__ == "__main__":
        monitoring_switches()