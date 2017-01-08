Features
1. Handles 4 lanes
2. Timing using just python code good to 0.02 seconds or better, estimated.
3. Hardware debounce and over voltage protection.
4. Switches for cars testing, still needs to hook to real track.
5. Python raw gpio handler process running at 1000 Hz, estimated
6. GUI updates 10 times a second.
7. Uses built in Python logger
8. Designed such that a real-time non-Python gpio handler could be swapped in.

Todo:
1. Add reset button for new race
2. Test more
3. Hook to track
4. Add a clock or activity meter

Biggest challenges.
1. Medication sure slows me down.
2. General understanding of threads, processes, and real-time is poor in Python community.
3. Very touchy to communicate between 2 separate Python processes without blocking. 
4. Python throws in its own tricks just to make life trickier. Example, writing many
   separate strings to stdout works fine but for some reason the last write always
   tosses in an extra non-character at the end, weird and never explained.
5. Pythons indentation for code blocks is often nice until those code blocks get long.
6. The idea that ':' is needed at the end of many statements, such as if (a == b): is totally silly

Python pluses.
1. I love tuples:
   def func_rev(a, b)
       return(b, a)

   (x, y) = func_rev(10, 20)

   x is now 20, y is now 10

   Cleans up so much simple code.

Biggest Python negative design
1. Acts mostly like a higher level language but then also like script language and maybe both at the same time.
   Example script:
     in this case some_cool_var_of_undetermined_type could be a list of structures and work perfect
     print "Howard", some_cool_var_of_undetermined_type

  Example language:
    if val is not an int this is an error
    log.info("Value=%d", val)

  Object oriented inconsistency
  astring = "ABC"
  thelen = len(astring)

  Yet other cases you can do things like astring.find("A").


New scheme: LCgpioraw only writes errors or laps, no status of "-01
00000" since it wasted so much time.

Issue

1.gpio raw writes so many -01 00000 that gpio takes a large amount
  of time cleaning this up.

Options:

1. Just don't print debug when '' character is removed since it prints
   all of the -01 00000
2. Somehow get gpio raw to not add ''.
3. Maybe just blindly remove it in gpio
4. Fastest may be to never send -01 00000 since gpio already handles
   this. A little harder to debug but maybe worth it.

5. If we could determine the stdout for gpio raw was empty and we had
   no data, only then send -01 00000. Even so gpio raw runs so fast,
   in the long 1000 Hz we would still have 1000 -01 00000 to remove.

LClapcounter.py
  LCcontroller.py
    LCgpio.py		# Spawn GPIO process, returns strings (lll tttttt)
    			# lll = 000-003, -01 == no data, -02 == error
			# ttttt == milliseconds, 99999 is more than 10 seconds
      . read_lanetime() # Returns tuples (lane/status/error time in seconds or error code
      LCgpioraw.py	# prints via stdout, which id setup for non-blocking, strings of the form "lll tttttt"
    LCview
      LClane

TODO:
1. Hook up real GPIO
   a. Add power to bread board
2. Jeremy add reset button
3. Jeremy align decimal points
4. Jeremy needs to put up -- or xx for out of range values

DONE:
1. Need method to kill LCgpioraw.py when
   LClapcounter.py->LCcontroller.py->LCgpio.py ends. Using closed pipe
   scheme.

   LCview::killit() causes pipe tp close
2. Prioritize LCgpioraw.py as high priority thread
   Must start LClapcounter.py as sudo or start idle as sudo

3. root problem for GPIO works fine just as nice issue

4: Logging works as well 

5. Fixed and simplified logger duplicates.
