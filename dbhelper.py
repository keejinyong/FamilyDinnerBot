import sqlite3


class DBHelper:
    

    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    #setup mydb table to check which family some id belong to  --- only 1 family per id
    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS mydb (phone_number TEXT, family_name TEXT)"
        self.conn.execute(stmt)
        self.conn.commit()
        
    def find_family(self, phone_no):
        stmt = "SELECT family_name FROM mydb WHERE phone_number LIKE ?"
        args = (phone_no, )
        cur = self.conn.cursor()
        cur.execute(stmt, args)
        res = "".join("%s" % tup for tup in cur.fetchall())
        cur.close()
        return res

    #supposed to return eating status of every1 in family
    def check_status(self, phone_no):
        family_name = self.find_family(phone_no)
        cur = self.conn.cursor()
        stmt = "SELECT * FROM " + family_name
        res = ""
        for row in cur.execute(stmt):
            res = res + str(row)
            res = res + '\n'
            print(res)
        cur.close()
        return res
        
    def find_myname(self, phone_no):
        family_name = self.find_family(phone_no)
        cur = self.conn.cursor()
        stmt = "SELECT name FROM " + family_name + " WHERE phone_number Like ?"
        args = (phone_no, )
        cur = self.conn.cursor()
        cur.execute(stmt, args)
        res = "".join("%s" % tup for tup in cur.fetchall())
        cur.close()
        return res

    #create 1 table for each family
    def add_family(self, family_name):
        cur = self.conn.cursor()
        stmt = "CREATE TABLE IF NOT EXISTS " + family_name + " (phone_number TEXT, name TEXT, eating INTEGER)"
        args = (family_name, )
        cur.execute(stmt)
        self.conn.commit()
        cur.close()

        #add member to family table
    def add_family_member(self, phone_no, family_name, name):
            cur = self.conn.cursor()
            stmt = "INSERT INTO " + family_name + " VALUES (?, ?, 0)"
            args = (phone_no, name)
            cur.execute(stmt, args)
            #add to mydb as well
            stmt = "INSERT INTO mydb VALUES (?, ?)"
            args = (phone_no, family_name)
            cur.execute(stmt, args)
            self.conn.commit()
            cur.close()

    #set whether eating anot
    #eating: 1 = eating, 0 = unconfirmed, 2 = not eating
    def set_eating(self, phone_no, eating):
        family_name = self.find_family(phone_no)
        stmt = "UPDATE " + family_name + " SET eating = ? WHERE phone_number = ?"
        args = (eating, phone_no, )
        cur = self.conn.cursor()
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        
    def set_name(self, phone_no, name):
        family_name = self.find_family(phone_no)
        stmt = "UPDATE " + family_name + " SET name = ? WHERE phone_number = ?"
        args = (name, phone_no, )
        cur = self.conn.cursor()
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        
    def close(self):
        self.conn.close()
        print("rdyrdy")


