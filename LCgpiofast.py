
# Design

# Read all gpio every 0.25 seconds. This is based on the RC HW delay of over 0.5
# seconds

# If ANY cars on lap counter or has tripped lap counter, 0 indicates car has
# tripped lap counter, start readying at full speed for best resolution.

# Then when lane goes back to 1, RC counter has timed out grab the time.

# Single lane example

# Bt default nobodies stuck
lane_stuck = False

while True:
    # Has the lap counter tripped?
    lane = GetGPIO()

    # if the lane is not stuck just contnue    
    if (lane_stuck != True):
        # if car has tripped lap counter start reading fast, no delays
        if (lane == 0): # lap counter is tripped
            # Mannually determine this tick time so we are not stuck forever.
            # used to time out cars stuck on lap counter but no stall full system
            ticks = (One Second Of Ticks)
            while ticks > 0:
                ticks -= 1 # so we can break out on error
                lane = GetGPIO()
                # If the lapcounter RC circuit has times out we are done
                if (lane == 1):
                    # We now have a new time and lane
                    new_lap_time = GetNewTime()
                    print (lane, new_lap_time)
                    # Break out of the high speeed loop
                    break

            # Car stuck on lap counter so need to ignore until it gets cleared
            # We get here if ticks goes to 0 but car still on lapcounter
            if (lane == 0):
                new_lap_time = "-01 99999"
                print (-01, 99999)
                lane_stuck = True;
        else:
            # indicate no lanes tripped
            print (-01, 99999)
            # So sleep awhile
            time.sleep(0.25)
    else: # Car stuck so handle it
        if (lane == 1):
            # No longer stuck
            lane_stuck = False
            # Car was stuck but might just have a longer lap time.
            new_lap_time = GetNewTime()
            print (lane, new_lap_time)
        else:
            time.sleep(0.25)
