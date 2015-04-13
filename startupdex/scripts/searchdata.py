import sys
from peewee import *
from playhouse.sqlite_ext import *
from ..models import Entry, FTSEntry

def main(argv=sys.argv):
	query = (FTSEntry
			 .select(Entry.title)
			 .join(Entry)
			 .where(FTSEntry.match('golang'))
			 .dicts()
			 )
	for row_dict in query:
		print(row_dict)
