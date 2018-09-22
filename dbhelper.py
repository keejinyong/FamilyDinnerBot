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
        
    def create_user(self, phone_no):
        stmt = "INSERT INTO mydb VALUES (?, null)"
        args = (phone_no, )
        cur = self.conn.cursor()
        cur.execute(stmt, args)
        self.conn.commit()
        cur.close()
        
        
    def find_family(self, phone_no):
        stmt = "SELECT family_name FROM mydb WHERE phone_number LIKE ?"
        args = (phone_no, )
        cur = self.conn.cursor()
        cur.execute(stmt, args)
        res = "".join("%s" % tup for tup in cur.fetchall())
        cur.close()
        if str(res) == "None":
            return False
        if not res:
            self.create_user(phone_no)
        return res

    #supposed to return eating status of every1 in family
    def check_status(self, phone_no):
        family_name = self.find_family(phone_no)
        cur = self.conn.cursor()
        stmt = "SELECT name, eating FROM " + family_name
        res = ""
        for row in cur.execute(stmt):
            res = res + str(row)
            res = res + '\n'
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
        stmt = "SELECT COUNT (*) FROM mydb WHERE family_name = ?"
        #SELECT COUNT (*) FROM mydb WHERE phone_number = "411168546"
        args = (family_name, )
        cur.execute(stmt, args)
        res = "".join("%s" % tup for tup in cur.fetchall())
        if int(res) == 0:
            stmt = "CREATE TABLE IF NOT EXISTS " + family_name + " (phone_number TEXT, name TEXT, eating TEXT)"
            cur.execute(stmt)
            self.conn.commit()
            cur.close()
            return False
        cur.close()
        return True

        #add member to family table
    def add_family_member(self, phone_no, family_name, name):
        #check if in family already
        if not self.find_family(phone_no):
            cur = self.conn.cursor()
            stmt = "INSERT INTO " + family_name + " VALUES (?, ?, 0)"
            args = (phone_no, name)
            cur.execute(stmt, args)
            #add to mydb as well
            stmt = "UPDATE mydb SET family_name = ? WHERE phone_number = ?"
            args = (family_name, phone_no)
            cur.execute(stmt, args)
            self.conn.commit()
            cur.close()
            return True
        else:
            return False

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
        
    def resetdinner(self):
        stmt = "SELECT DISTINCT family_name FROM mydb"
        cur = self.conn.cursor()
        for row in cur.execute(stmt):
            res = "".join("%s" % tup for tup in row)
            stmt2 = "UPDATE " + res + " SET eating = '0'"
            cur.execute(stmt2)
        self.conn.commit()
        cur.close()
        
    def listofnum(self):
        stmt = "SELECT phone_number FROM mydb WHERE family_name != null"
        cur = self.conn.cursor()
        num = []
        for row in cur.execute(stmt):
            res = "".join("%s" % tup for tup in row)
            num.append(res)
        return num
        
    def geteat(self, phone_no):
        family_name = self.find_family(phone_no)
        stmt = "SELECT eating FROM " + family_name + " WHERE phone_number Like ?"
        args = (phone_no, )
        cur = self.conn.cursor()
        res = "".join("%s" % tup for tup in cur.execute(stmt, args).fetchall())
        return res
        
    def removefromfamily(self, phone_no, name):
        family_name = self.find_family(phone_no)
        stmt = "SELECT phone_number FROM " + family_name + " WHERE name Like ?"
        args = (name, )
        cur = self.conn.cursor()
        res = ""
        x = 0
        for row in cur.execute(stmt, args):
            line = "".join("%s" % tup for tup in row)
            res = res + line
            x = x + 1
        if not x==1:
            return False
        else:
            stmt4 = "SELECT COUNT (*) FROM " + family_name
            cur.execute(stmt4)
            res2 = "".join("%s" % tup for tup in cur.fetchall())
            if not (int(res2) == 1):
                stmt2 = "DELETE FROM " + family_name + " WHERE phone_number = " + res
                cur.execute(stmt2)
            else:
                stmt2 = "DROP TABLE " + family_name
                cur.execute(stmt2)
            stmt3 = "UPDATE mydb SET family_name = null WHERE phone_number = " + res
            cur.execute(stmt3)
            
            self.conn.commit()
            cur.close()
            return True
        
    def close(self):
        self.conn.close()


