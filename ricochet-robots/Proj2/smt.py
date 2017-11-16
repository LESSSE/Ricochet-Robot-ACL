import sys
sign = lambda x: x and (1, -1)[x < 0]

dim_line=1
dim_col=1
dim_robot=1
dim_time=1

################## PREDICATES #####################

def declarePredicates(outfile):
     # position ( line, col, robot, time ) => bool
     pos="( declare-fun position ( Int Int Int Int ) ( Bool ) )"
     # clear ( orig_line, orig_col, dest_line, dest_col, time ) => bool
     clear="( declare-fun clear ( Int Int Int Int Int) ( Bool ) )"
     # reallyPossible ( orig_line, orig_col, dest_line, dest_col, time ) => bool
     possible="( declare-fun possible ( Int Int Int Int Int) ( Bool ) )"
     # moved ( robot, time ) => bool
     moved="( declare-fun moved ( Int Int ) ( Bool ) )"

     #if outfile!=-1:
     #     outfile.write(pos+"\n")
     #     outfile.write(clear+"\n")
     #     outfile.write(possible+"\n")
     #     outfile.write(moved+"\n")

     ##print(pos)
     ##print(clear)
     ##print(possible)
     ##print(moved)
     outfile.write(pos+"\n")
     outfile.write(clear+"\n")
     outfile.write(possible+"\n")
     outfile.write(moved+"\n")



################## CONSTRAINTS #####################

# only one position

dim_time=1
dim_robot=4
dim_line=3
dim_col=3



###################################################################################

def writeSinglePositionConstraintLogic(outfile):
     for time in range(dim_time):
          for robot in range(dim_robot):
               for line1 in range(dim_line):
                    for col1 in range(dim_col):
                         ac="(assert (=> ( position "+str(line1)+" "+str(col1)+" "+str(robot)+" "+str(time)+") (and "
                         for line2 in range(dim_line):
                              for col2 in range(dim_col):
                                   if(line1==line2 and col1==col2):
                                        continue
                                   ac+="(not (position "+str(line2)+" "+str(col2)+" "+str(robot)+" "+str(time)+"))"
                         ac+=")))"
                         outfile.write(ac+"\n")
               
               
#( assert  ( + position() (+ position() (+ position() (+ ... ) ) ) ) )
def writeSinglePositionConstraint(outfile):
     for time in range(dim_time):
          for robot in range(dim_robot):
               ac="( assert ( = ( + "
               count=0 #count the number of closing parenthesis
               for line in range(dim_line):
                    for col in range(dim_col):
                         ac+="(ite (position "+str(line)+" "+str(col)+" "+str(robot)+" "+str(time)+" ) 1 0) "
                         count+=1
               #ac+="0"
               #for i in range(count):
               #     ac+=")"
               ac+=") 1 ) ) "
               #if(outfile!=-1):
               #     outfile.write(ac)
               #print(ac)
               outfile.write(ac+"\n")

###################################################################################
def writeMovedConstraintLogic(outfile):
     for time in range(dim_time):
          for robot1 in range(dim_robot):
               ac="( assert ( => (moved "+str(robot1)+" " +str(time)+" ) (and  "
               for robot2 in range(dim_robot):
                    if robot1==robot2:
                         continue
                    ac+="(not (moved "+str(robot2)+" "+str(time)+" )) "
               ac+=")))\n"
               outfile.write(ac)
          
          
def writeMovedConstraint(outfile):
     for time in range(dim_time):
          ac="( assert ( = ( + "
          count=0
          for robot in range(dim_robot):
               ac+="(ite ( moved  "+ str(robot) + " " + str(time) + " ) 1 0) "
               count+=1
          #for i in range(count):
          #     ac+=")"
          ac+=") 1 ) ) "
          #if(outfile!=-1):
          #     outfile.write(ac)
          #print(ac)
          outfile.write(ac+"\n")

###################################################################################

# must receive an edge (not necessarily maximally extended)
# the outer function should do both calls, one for each orientation; also responsible for calling only for edges of length >=3

def getNoRobotInPosition(line, col, time):
     count=0
     ac=""
     for robot in range(dim_robot):
          ac+="(not ( position "+str(line)+" "+str(col)+" " +str(robot)+" " +str(time)+" )) "
          count+=1
     #for i in range(count):
     #     ac+=")"
     return ac+" "

# a->b is CLEAR => a->b-1 is CLEAR AND b has no robot
def writeClearPathConstraint_Single( start_line, start_col, end_line, end_col, outfile):
     dir_x = sign( end_line-start_line ) 
     dir_y = sign( end_col-start_col )
     edgelen = abs(( end_line-start_line )+( end_col-start_col ))

     ac=""

     if(edgelen==1):
          for time in range(dim_time):
               pos = str(start_line) + " " + str(start_col) + " " + str(end_line) + " " +str(end_col) + " " + str(time)+" "
               
               ac="( assert (=> ( clear "+pos+") (and "+getNoRobotInPosition(end_line, end_col, time)+"))) "

               #if(outfile!=-1):
               #     outfile.write(ac)
               #print(ac)
               outfile.write(ac+"\n")
          return
     
     for time in range(dim_time):
          pos = str(start_line) + " " + str(start_col) + " " + str(end_line) + " " +str(end_col) + " " + str(time)+" "
          prev_pos = str(start_line) + " " + str(start_col) + " " + str(end_line-dir_x) + " " +str(end_col-dir_y) + " " + str(time)+" "
          
          ac="( assert (=> ( clear "+pos+") (and ( clear "+ prev_pos+") "+getNoRobotInPosition(end_line, end_col, time)+"))) "

          #if(outfile!=-1):
          #     outfile.write(ac)
          #print(ac)
          outfile.write(ac+"\n")




def writeClearPathConstraints(extEdgelist, outfile=-1):
     for max_edge in extEdgelist:
          dir_x = sign(max_edge[2] - max_edge[0])
          dir_y = sign(max_edge[3] - max_edge[1])
          edgelen =( max_edge[2]-max_edge[0] )+( max_edge[3]-max_edge[1] )

          for i in range(0, edgelen):
               for j in range(i+1, edgelen+1):
                    lower_x = max_edge[0] + dir_x*i
                    lower_y = max_edge[1] + dir_y*i
                    higher_x = max_edge[0] + dir_x*j
                    higher_y = max_edge[1] + dir_y*j

                    writeClearPathConstraint_Single(lower_x, lower_y, higher_x, higher_y, outfile)
                    writeClearPathConstraint_Single(higher_x, higher_y, lower_x, lower_y, outfile)


###################################################################################

def getRobotInPosition(line, col, time):
     count=0
     ac="( or "
     for robot in range(dim_robot):
          ac+="( position "+str(line)+" "+str(col)+" " +str(robot)+" " +str(time)+" ) "
          count+=1
     #for i in range(count):
     #     ac+=")"
     return ac+") "

#Stop Vertex constraint
def writePossibleMovementConstraint_Single( start_line, start_col, end_line, end_col, outfile ):
     dir_x = sign( end_line-start_line ) 
     dir_y = sign( end_col-start_col )
     
     ac=""
     
     for time in range(dim_time):
          pos = str(start_line) + " " + str(start_col) + " " + str(end_line) + " " +str(end_col) + " " + str(time)+" "
          cur_pos = str(end_line)+" " +str(end_col)+" "+str(time)+" "
          next_pos = str(start_line) + " " + str(start_col) + " " + str(end_line+dir_x) + " " +str(end_col+dir_y) + " " + str(time)+" "

          ac="( assert (=> ( possible "+ pos + ") (and "+" " + "( clear "+pos+") "+ getRobotInPosition(end_line+dir_x, end_col+dir_y, time) +") ) )"

          #if(outfile!=-1):
          #     outfile.write(ac)
          #print(ac)
          outfile.write(ac+"\n")

def writePossibleMovementConstraint_Clear( start_line, start_col, end_line, end_col, outfile ):
     dir_x = sign( end_line-start_line ) 
     dir_y = sign( end_col-start_col )
     
     ac=""
     
     for time in range(dim_time):
          pos = str(start_line) + " " + str(start_col) + " " + str(end_line) + " " +str(end_col) + " " + str(time)+" "
          cur_pos = str(end_line)+" " +str(end_col)+" "+str(time)+" "
          next_pos = str(start_line) + " " + str(start_col) + " " + str(end_line+dir_x) + " " +str(end_col+dir_y) + " " + str(time)+" "

          ac="( assert (=> ( possible "+ pos + ") ( clear "+pos+") ))"

          #if(outfile!=-1):
          #     outfile.write(ac)
          #print(ac)
          outfile.write(ac+"\n")



def writePossibleMovementConstraint( extEdgelist, outfile=-1):
     for max_edge in extEdgelist:
          dir_x = sign(max_edge[2] - max_edge[0])
          dir_y = sign(max_edge[3] - max_edge[1])
          edgelen =( max_edge[2]-max_edge[0] )+( max_edge[3]-max_edge[1] )

          for i in range(0, edgelen):
               for j in range(i+1, edgelen+1):
                    lower_x = max_edge[0] + dir_x*i
                    lower_y = max_edge[1] + dir_y*i
                    higher_x = max_edge[0] + dir_x*j
                    higher_y = max_edge[1] + dir_y*j
                    
                    if(higher_x<max_edge[2] or higher_y<max_edge[3]):
                         writePossibleMovementConstraint_Single(lower_x, lower_y, higher_x, higher_y, outfile)
                    else:
                         writePossibleMovementConstraint_Clear(lower_x, lower_y, higher_x, higher_y, outfile)
                    if(lower_x>max_edge[0] or lower_y>max_edge[1]):
                         writePossibleMovementConstraint_Single(higher_x, higher_y, lower_x, lower_y, outfile)
                    else:
                         writePossibleMovementConstraint_Clear(higher_x, higher_y, lower_x, lower_y, outfile)

###################################################################################





def getTripleConjunction(start_line, start_col, dest_line, dest_col, robot, time):
     pos =str(start_line)+" "+str(start_col)+" "+str(robot)+" "+str(time)+" "
     path = str(start_line)+" " + str(start_col)+" "+str(dest_line) + " " + str(dest_col)+" " +str(time)+" "
     moved = str(robot) + " " + str(time)
     return "( and ( position "+ pos + ") ( possible "+ path + " ) ( moved "+ moved + ") )"



#possible origins is indexed by a destination position (line, col) and returns a list of positions that can lead to it (line, col)
# I don't remember the concrete format, need to check projencoding.py file
# both orientations are already implicit
def writeRobotMovementConstraints(possibleOrigins, outfile):
     # just need to loop through these 4
     # each 4-tuple of these variables originates a single clause/assert
     cur_line =0
     cur_col=0
     time=1
     robot=1

     for cur_line in range(dim_line):
          for cur_col in range(dim_col):
               for robot in range(dim_robot):
                    for time in range(1, dim_time):
                         ac="(assert (=> (position "+str(cur_line)+" "+str(cur_col)+" "+str(robot)+" "+str(time)+" ) "+"( or ( position "+str(cur_line)+" "+str(cur_col)+" "+str(robot)+" " +str(time-1) +" ) "
                         count =3
                         for pos in possibleOrigins[cur_line][cur_col]:
                              start_line = pos[0]
                              start_col = pos[1]
                              
                              count+=1
                              ac+="( or "+getTripleConjunction(start_line, start_col, cur_line, cur_col, robot, time-1)
                         for i in range(count):
                              ac+=")"
                         #if(outfile!=-1):
                         #     outfile.write(ac)
                         #print(ac)
                         outfile.write(ac+"\n")
          

###################################################################################


############################ ROBOTS INITIAL POSITIONS ##################################

def writeInitialPosition(line, col, robot, outfile=-1):
     ac="( assert ( position "+str(line)+" "+str(col)+" "+str(robot)+" 0 ))"
     #if(outfile!=-1):
     #     outfile.write(ac+"\n")
     return ac

def writeGoal(line, col, robot, time, outfile=-1):
     ac="( assert ( position "+str(line)+" "+str(col)+" "+str(robot)+" "+str(time)+" ))"
     #if(outfile!=-1):
     #     outfile.write(ac+"\n")
     return ac
     


###################################################################################
          

##print("\nSinglePositionConstraint")
#writeSinglePositionConstraint()
##print("\nMovedConstraint")
#writeMovedConstraint()
#writeClearPathConstraint_Single() #missing arguments
##print("\nWritePossibleMovementConstraint_Single")
#writePossibleMovementConstraint_Single(0, 0, 3,0)

##################################################
