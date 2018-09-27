## a simple hacky script that takes the stderr of ffmpeg (piped to stdin of Python) and
## uses that to make a discord rich presence status for your transcode

''' 
# a function for your bashrc to automate running the script
# the only issue is that an input or output file with spaces will not be escaped properly

function ffmpeg {
/usr/local/bin/ffmpeg $@ 2>&1 | python3 ~/path/to/parser.py
}

# alternatively, you can just append this to your ffmpeg command:

2>&1 | python3 ~/path/to/parser.py
'''

APP_ID = '447917369512296458'
UPDATE_RATE = 15

import sys
import time
import re
import rpc as discordRP

# super basic arguments:
#  -q: do not pass through ffmpeg's output
#  -s: show the parsed json each update

QUIET = False
SHOW_JSON = False
if '-q' in sys.argv:
	QUIET = True
if '-s' in sys.argv:
	SHOW_JSON = True

rpc = discordRP.DiscordIpcClient.for_platform(APP_ID) # discord rpc object

norm_space = re.compile(r'\s+')  # precompiled regex

inbuffer = '' # buffer for textual input

start_time = time.time()
last_update = time.time()-100

def setactivity(data):
	firstline = 'Frame {} @ {}fps, {}'.format(data.get('frame','NA'),data.get('fps','NA'),data.get('bitrate','NA'))
	secondline = 'Position: {}, Size: {}'.format(data.get('time','NA'),data.get('size','NA'))

	activity = {
		'details':firstline,
		'state':secondline,
		'timestamps':{
			'start':start_time
		}
	}
	rpc.set_activity(activity)

def extractstatus(line):
	line_norm = norm_space.sub(' ',line)
	pairs = re.split(r'(?<!=)\s',line_norm)
	data = {}
	for pair in pairs:
		if '=' in pair:
			key,val = pair.split('=',1)
			data[key.strip()] = val.strip()
	return data

def parsestatus(line):
	global last_update
	try:
		if time.time() - last_update > UPDATE_RATE:
			last_update = time.time()
			data = extractstatus(line)
			setactivity(data)
			if SHOW_JSON:
				print(data)
	except:
		print('error setting activity i think')
		pass

def parseline(line):
	if 'speed=' in line and 'time=' in line and 'fps=' in line:
		parsestatus(line)

def mainloop():
	global inbuffer
	while True:
		inp = sys.stdin.read(16)
		if not inp:
			exit()
		if not QUIET:
			sys.stdout.write(inp)
			sys.stdout.flush()
		inbuffer += inp
		while '\n' in inbuffer or '\r' in inbuffer:
			nextline = ''
			if '\n' in inbuffer:
				nextline,inbuffer = inbuffer.split('\n',1)
			elif '\r' in inbuffer:
				nextline,inbuffer = inbuffer.split('\r',1)
			nextline = nextline.strip()
			parseline(nextline)
		#time.sleep(0.001)


if __name__ == '__main__':
	mainloop()