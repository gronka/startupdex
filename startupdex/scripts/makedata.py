#import sys
#from peewee import *
#from playhouse.sqlite_ext import *
#from ..models import Entry, FTSEntry

#def main(argv=sys.argv):
	#entry = Entry.create(
		#title="How I rewrote everything in golang",
		#content="blah blah blah golang is awesome",
	#)
	#FTSEntry.create(
		#entry=entry,
		#content='\n'.join((entry.title, entry.content))
	#)
	#entry = Entry.create(
		#title="Here is another article about golang",
		#content="after much consideration, I no longer think golang is awesome",
	#)
	#FTSEntry.create(
		#entry=entry,
		#content='\n'.join((entry.title, entry.content))
	#)
