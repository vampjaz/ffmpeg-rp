FFMPEG rich presence for Discord
===

![example screenshot](https://github.com/red-green/ffmpeg-rp/raw/master/example.png)

A simple script that parses the output of ffmpeg (specifically the status messages written to stderr) and shows the progress of your encode with discord rich presence. Now your friends can see when you're torturing your cpu too!

There are a few limitations of this:

- Colors in the printout get stripped out cause the act of piping them through python strips the bash color sequences.
- Its not completely seamless without the bash function below (i.e. you would have to paste a script call after every ffmpeg command)
- The rich presence API has been known to break after some particularly long encoding sessions. I think this is some sort of rate limit imposed by Discord. There is no way to easily reconnect without restarting the program and probably the transcode.
- If you kill it with ctrl-c, the rich presence script will exit but ffmpeg will keep running with no output, making it hard to tell what's going on.
- It was thrown together in an hour so don't expect it to be bug free!

Basically, its run by appending this to the end of your ffmpeg command to pipe the status messages into the script:

```shell
2>&1 | python3 ~/path/to/parser.py
```

Having to paste that every time got annoying, so in order to run it, I added this to my bashrc:

```shell
# ffmpeg rich presence

function ffmpeg {
/usr/local/bin/ffmpeg $@ 2>&1 | python3 ~/path/to/parser.py
}
```
*(you may need to change the path to the ffmpeg file and the parser script)*

Which creates a bash function so that you can run most ffmpeg commands normally, thought there are some extra limitations of this method:
- Your input and output file names cannot have any spaces in them, even if they are escaped properly. This is an issue with bash function argument passing.
- If you want to use the normal ffmpeg (without the rich presence running), you'd have to call the full executable path

This is why I named the function `ffmpegrp` so that the normal ffmpeg is still usable if need be.

There are also some arguments that can be passed to the parser if you really want to:

- `-q`: do not pass through ffmpeg's output
- `-s`: show the parsed json each update
