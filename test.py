import pymysql

pymysql.install_as_MySQLdb()

connection = pymysql.connect(
  host='localhost',
  user='anda',
  password='password',
  database='test'
)

cursor = connection.cursor()

cursor.execute('SELECT VERSION()')
version = cursor.fetchone()
print(version)