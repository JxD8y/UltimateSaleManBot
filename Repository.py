import sqlite3

class USMRepo:
    _Path = ""
    _DbConnection : sqlite3.Connection = None
    _DbCursor : sqlite3.Cursor = None
    Admins = []
    
    def __init__(self,PATH):
        self._Path = PATH
        self._DbConnection = sqlite3.connect(self._Path)
        self._DbCursor = self._DbConnection.cursor()
        self._DbCursor.execute("select name from sqlite_master;")
        tbl_mstr = self._DbCursor.fetchall()
        if(len(tbl_mstr) == 0 or not all(j in tbl_mstr for j in ["admins","users","items","orders","payments"])):
            print("Creating database tables ...")
            self._CreateDatabaseTables()
        else:
            print("Database already has a valid scheme ignoring table creation ...")
        self._DbCursor.execute("SELECT number_id from admins")
        self.Admins = [i[0] for i in self._DbCursor.fetchall()]

    def _CreateDatabaseTables(self):
        if self._DbCursor == None:
            raise "Cannot create database tables."
        
        self._DbCursor.execute("CREATE TABLE IF NOT EXISTS admins "
        "(number_id int not null primary key,"
        "name text not null);")

        self._DbCursor.execute("CREATE TABLE IF NOT EXISTS users "
        "(number_id int not null primary key,"
        "name text not null," \
        "is_active integer not null default 1," \
        "start_time TEXT not null);")

        self._DbCursor.execute("CREATE TABLE IF NOT EXISTS items "
        "(id integer not null primary key AUTOINCREMENT,"
        "count int not null,"
        "item text not null," \
        "price real not null);")

        self._DbCursor.execute("CREATE TABLE IF NOT EXISTS orders "
        "(id integer not null primary key,"
        "time TEXT not null," \
        "uid integer not null,"
        "item_id integer not null," \
        "payment_id integer not null,"
        "foreign key (uid) references users(number_id)," \
        "foreign key (item_id) references items(id));")

        self._DbCursor.execute("CREATE TABLE IF NOT EXISTS payments "
        "(id integer not null primary key,"
        "method text not null," \
        "amount real not null,"
        "pay_time TEXT not null," \
        "state boolean not null," \
        "uid integer not null," \
        "foreign key (uid) references users(number_id));")

        print("DATABASE TABLES INITIATED")
    
    def AppendAdmin(self,number_id,name):
        self._DbCursor.execute("SELECT number_id from admins")
        self.Admins = [i[0] for i in self._DbCursor.fetchall()]
        if(number_id not in self.Admins):
            self._DbCursor.execute("INSERT INTO admins values (?,?)",(number_id,name))
            self._DbConnection.commit()
            self.Admins.append(number_id)
        else:
            print(f"admin {name} already exist in database")

    def RemoveAdmin(self,number_id,name):
        self._DbCursor.execute("SELECT number_id from admins")
        self.Admins = [i[0] for i in self._DbCursor.fetchall()]
        if(number_id in self.Admins):
            self._DbCursor.execute(f"DELETE FROM admins WHERE number_id = {number_id}")
            self._DbConnection.commit()
            self.Admins.remove(number_id)
        else:
            print(f"admin {name} {number_id} doesn't exist in database")
    
    def GetUser(self,number_id):
        self._DbCursor.execute(f"SELECT * from users where number_id = {number_id}")
        return self._DbCursor.fetchone()
    
    def GetAdmin(self,number_id):
        self._DbCursor.execute("SELECT * FROM admins WHERE number_id = ?",(number_id,))
        return self._DbCursor.fetchone()

    def AddUser(self,number_id,name,start_time):
        self._DbCursor.execute(f"INSERT INTO users values (?,?,?,?)",(number_id,name,1,start_time))
        self._DbConnection.commit()

    def GetUserAmount(self,number_id):
        self._DbCursor.execute("SELECT charge from users where number_id = (?)",(number_id))
        charge = self._DbCursor.fetchone()
        return float(charge)
    
    def GetUsers(self):
        self._DbCursor.execute("SELECT * FROM users")
        return self._DbCursor.fetchall()
    
    def SetUserActiveState(self,number_id,active:bool):
        if active:
            self._DbCursor.execute("UPDATE users set is_active = 1 where number_id = ?",(number_id,))
        else:
            self._DbCursor.execute("UPDATE users set is_active = 0 where number_id = ?",(number_id,))

    def DeleteUser(self,number_id):
        self._DbCursor.execute("DELETE FROM users where number_id = ?",(number_id,))
        self._DbConnection.commit()

    def GetItems(self):
        self._DbCursor.execute("SELECT * from items")
        return self._DbCursor.fetchall()
    
    def AddItem(self,name,price,quantity):
        self._DbCursor.execute("INSERT INTO items (count,item,price) VALUES (?,?,?)",(quantity,name,price))
        self._DbConnection.commit()
    
    def GetItem(self,id):
        self._DbCursor.execute("SELECT * FROM items WHERE id = ?",(id,))
        return self._DbCursor.fetchone()
    
    def DeleteItem(self, id):
        self._DbCursor.execute("DELETE FROM items WHERE id = ?",(id,))
        self._DbConnection.commit()
    
    def UpdateItem(self,id,name,price,count):
        self._DbCursor.execute(f"UPDATE items SET item = \"{name}\", count = \"{count}\" , price = \"{price}\" WHERE id = {id}")
        self._DbConnection.commit()

USMRepository : USMRepo = None

def SetRepo(URepo:USMRepo):
    global USMRepository
    USMRepository = URepo

def GetRepo() -> USMRepo:
    return USMRepository