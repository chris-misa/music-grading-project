"""
Description:
A class to deal with apple loop database transactions.

Database Schema:

  Table: audioLoops

    Column Name     | type
    ----------------+--------
    filename        | text
    category        | text
    subcategory     | text
    genre           | text
    descriptors     | text
    time_signature  | text
    beat_count      | text
    key_signature   | text
    key_type        | text
  
Possible Edge cases: Drummer loops?

Authors:
Chris Misa, chris@chrismisa.com
"""

import sqlite3

class Database:
  """
    Class to handle operations in the apple loops database.
  """
  # Default name of database file
  DB_NAME = "appleloops.sqlite3"
  # List of columns and types as per current database schema
  COLUMNS = {"filename":"text", "category":"text", "subcategory":"text", \
          "genre":"text", "descriptors":"text", "time_signature":"text", \
          "beat_count":"text", "key_signature":"text", "key_type":"text"}

  def __init__(self, filepath = DB_NAME):
    """
      Instantiates a new database access object connected to the
      sqlite database at the given filepath.
    """
    self.conn = sqlite3.connect(filepath)
    # make sure there is the right table
    cur = self.conn.cursor()
    schema = ",".join(k + " " + v for k, v in self.COLUMNS.items())
    cur.execute("create table if not exists \
                 audioLoops(" + schema + ");")
    self.conn.commit()

  def __del__(self):
    """Close the connection when the object is deleted"""
    if self.conn is not None:
      self.conn.close()
  
  def getDataForLoop(self, loopFileName):
    """
      Looks up the given file name in database and returns a dict with
      metadata for this loop if found.
    """
    cols = ",".join(self.COLUMNS.keys())
    cur = self.conn.cursor()
    data = cur.execute("select {} from audioloops where filename = ?;".format(cols), \
                       (loopFileName,)).fetchall()
    result = []
    for d in data:
      result.append(dict(zip(self.COLUMNS.keys(), d)))
    return result
      
  def addFilename(self, data):
    """
      Writes the given data to the database assuming data is a dict with
      keys as described in Database Schema above.
      Returns -1 if data is not a valid entry.
    """
    # make sure there is at least a filename in the given data
    if "filename" not in data.keys():
      return -1
    # make sure there are no bad keys in given data
    for k in data.keys():
      if k not in self.COLUMNS.keys():
        print("Ignoring key: {} in {}".format(k, data['filename']))
    newdata = {k:v for k,v in data.items() if k in self.COLUMNS.keys()}
    data = newdata

    # form string for the querry
    cols = "(" + ",".join(data.keys()) + ")"
    tags = "(" + ",".join(":" + k for k in data.keys()) + ")"
    # execute querry
    cur = self.conn.cursor()
    cur.execute("insert into audioLoops {} values {};".format(cols, tags), \
                data)
    self.conn.commit()
    return 0

  def listFilenames(self):
    """
      Returns a list of all filenames (primary keys) currently stored in the database
    """
    cur = self.conn.cursor()
    return list(name for name, in cur.execute("select filename from audioloops;"))

  def removeFilename(self,filename):
    """
      Removes the data associated with the given filename, just incase
    """
    cur = self.conn.cursor()
    cur.execute("delete from audioloops where filename = ?;",(filename,))
    self.conn.commit()

