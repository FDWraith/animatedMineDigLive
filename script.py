import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    returnVal = { }
    for command in commands:
        if command[0] == "basename":
            returnVal['basename'] = command[1]
        elif command[0] == "frames":
            returnVal['num_frames'] = command[1]
        elif command[0] == "vary":
            if 'num_frames' not in returnVal.keys():
                exit
    if 'basename' not in returnVal.keys():
        print "Basename not found, using default ( \"animation\" )"
        returnVal['basename'] = 'animation'
    return returnVal


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    varyCommands = [ command for command in commands if command[0] == "vary" ]
    knobNames = set( command[1] for command in varyCommands )

    knobValues = { }
    for varyCommand in varyCommands:
        if varyCommand[1] not in knobValues.keys():
            knobValues[ varyCommand[1] ] = [ 0 for num in range(num_frames) ]
        if varyCommand[2] < 0 or varyCommand[2] > ( num_frames - 1 ) or varyCommand[3] > ( num_frames - 1 ):
            print "Vary Command out of range for %s"%( varyCommand[2] )
            exit
        frame = varyCommand[2]
        finalFrame = varyCommand[3] 
        diff = ( finalFrame - frame ) / abs( frame - finalFrame )
        knobChange = ( varyCommand[5] - varyCommand[4] ) * 1.0 / ( abs(frame - finalFrame) + 1 )
        currentVal = varyCommand[4] 
        while( frame != finalFrame + 1):
            knobValues[ varyCommand[1] ][ frame ] = currentVal
            frame += diff
            currentVal += knobChange
    return ( knobNames, knobValues )

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1

    
    #Animation Stuff
    info = first_pass( commands)
    ANIMATION = True if 'num_frames' in info else False
    basename = info['basename']
    
    if ANIMATION:
        num_frames = info['num_frames']
        knobInfo = second_pass( commands, num_frames )
        knobNames = knobInfo[0]
        knobValues = knobInfo[1]
        
        for frame in range( num_frames ):
            savefile = "./anim/%s%s.png"%(basename, tres(frame) )
            knobTable = { knobName: knobValue  for knobName in knobNames for knobValue in [ knobValues[knobName][frame] ] }
            print knobNames
            exit
            tmp = new_matrix()
            ident(tmp)
            stack = [ [x[:] for x in tmp] ]
            screen = new_screen()
            tmp = []
            
            for command in commands:
                print command
                c = command[0]
                args = command[1:]
                
                if c == 'box':
                    add_box(tmp,
                            args[0], args[1], args[2],
                            args[3], args[4], args[5])
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, color)
                    tmp = []
                elif c == 'sphere':
                    add_sphere(tmp,
                               args[0], args[1], args[2], args[3], step)
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, color)
                    tmp = []
                elif c == 'torus':
                    add_torus(tmp,
                              args[0], args[1], args[2], args[3], args[4], step)
                    matrix_mult( stack[-1], tmp )
                    draw_polygons(tmp, screen, color)
                    tmp = []
                elif c == 'move':
                    tmp = make_translate(args[0], args[1], args[2])
                    if args[3]:
                        if args[3] not in knobTable:
                            print "%s is used, but not varied"%( args[3] )
                        else:
                            scalar_mult( tmp, knobTable[ args[3] ])
                    matrix_mult(stack[-1], tmp)
                    stack[-1] = [x[:] for x in tmp]
                    tmp = []
                elif c == 'scale':
                    tmp = make_scale(args[0], args[1], args[2])
                    if args[3]:
                        if args[3] not in knobTable:
                            print "%s is used, but not varied"%( args[3] )
                        else:
                            scalar_mult( tmp, knobTable[ args[3] ])
                    matrix_mult(stack[-1], tmp)
                    stack[-1] = [x[:] for x in tmp]
                    tmp = []
                elif c == 'rotate':
                    theta = args[1] * (math.pi/180)
                    if args[0] == 'x':
                        tmp = make_rotX(theta)
                    elif args[0] == 'y':
                        tmp = make_rotY(theta)
                    else:
                        tmp = make_rotZ(theta)
                    if args[2]:
                        if args[2] not in knobTable:
                            print "%s is used, but not varied"%( args[2] )
                        else:
                            scalar_mult( tmp, knobTable[ args[2] ])
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
                elif c == 'push':
                    stack.append([x[:] for x in stack[-1]] )
                elif c == 'pop':
                    stack.pop()
                elif c == 'display':
                    display(screen)
                elif c == 'save':
                    save_extension(screen, args[0])

            save_extension( screen, savefile )
        make_animation( basename )
    else:
        for command in commands:
            print command
            c = command[0]
            args = command[1:]
            
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

def tres( num ):
    if num < 10:
        return "00%s"%(num)
    if num < 100:
        return "0%s"%(num)
    if num < 1000:
        return "%s"%(num)
    print( "Frame Size too large" )
    return ""
