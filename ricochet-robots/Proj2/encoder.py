import smt as Encoding
import puzzle_input as Reader
import time
import os
import sys
import math

#def writeConstraints_opt(outfile, extEdgelist, origins):
#    Encoding.writeRobotInPositionConstraint(outfile)
#    Encoding.writeRobotNotIn2VerticesConstraint(outfile)
#    Encoding.writeMovementConstraint_opt(extEdgelist, outfile, origins)
#    Encoding.writeNoRobotInPathConstraints_opt(extEdgelist, outfile)
#    Encoding.writeReallyPossibleConstraint2(extEdgelist, outfile)
#    Encoding.writeSingleMoveConstraint(outfile)

##print(sys.argv)

#if len(sys.argv)<2:
#    #print("Import file missing! usage is: \"python <program.py> <import_filename>")
#    sys.exit()


################################### READ INPUT AND ENCODE BOARD ######################################

   
def writeEverything(infile, outfile, t_max):
    
    start_time = time.time()
    start_clock = time.clock()
    
    #outfile=open(outfile_name, "w")
    
    
    #print(";Predicates")
    Encoding.declarePredicates(outfile)
    
    
    dim_line=1
    dim_col=1
    dim_robot=4
    dim_time=t_max
    
    
    Encoding.dim_line=dim_line
    Encoding.dim_col=dim_col
    Encoding.dim_robot=dim_robot
    Encoding.dim_time=dim_time
    
    Reader.dim_line=dim_line
    Reader.dim_col=dim_col
    Reader.dim_robot=dim_robot
    Reader.dim_time=dim_time

    #print("; 4 initial positions and goal")
    temp = Reader.readEdges(infile, outfile)
    
    dim_line = Reader.dim_line
    dim_col=Reader.dim_line
    
    Encoding.dim_line=dim_line
    Encoding.dim_column=dim_col
    Encoding.dim_col=dim_col #FIXME I used different variables for the same thing and don't know where or which or what so yeah oops

    ##print("DIMTIME: ")
    ##print(dim_time)
    ##print(Encoding.dim_time)
    ##print(Reader.dim_time)
    ##print("\n\n")
    
    board = temp[0]

    extEdgelist = Reader.getMaximallyExtendedEdges(board)
    origins = Reader.precomputeOrigins(extEdgelist)

    #writeConstraints_opt(outfile, extEdgelist, origins)

    
    ##print(extEdgelist)
    
    
    #print(";Moved constraint")
    outfile.write(";Moved constraint\n")
    Encoding.writeMovedConstraintLogic(outfile)
    #Encoding.writeMovedConstraint(outfile)
    #print(";Single position constraint")
    outfile.write(";Single position constraint\n")
    #Encoding.writeSinglePositionConstraint(outfile)
    Encoding.writeSinglePositionConstraintLogic(outfile)
    #print(";Clear path constraints")
    outfile.write(";Clear path constraints\n")
    Encoding.writeClearPathConstraints(extEdgelist, outfile)
    #print(";Stop Vertex")
    outfile.write(";Stop Vertex\n")
    Encoding.writePossibleMovementConstraint(extEdgelist, outfile)
    #print(";Movement constraints")
    outfile.write(";Movement constraints\n")
    Encoding.writeRobotMovementConstraints(origins, outfile)
    
    #print("\n\n")
    #print("(check-sat)")
    outfile.write("(check-sat)\n")
    #print("(get-model)")
    outfile.write("(get-model)\n")
    outfile.close()



######################################################################################################

def getRobot(i):
    if i==0:
        return "R"
    if i==1:
        return "Y"
    if i==2:
        return "G"
    if i==3:
        return "B"
    else: 
        return "X"
        
def getDirection(robotPos1, robotPos2):
    if(robotPos1[0]>robotPos2[0]):
        return "u"
    if(robotPos1[0]<robotPos2[0]):
        return "d"
    if(robotPos1[1]>robotPos2[1]):
        return "l"
    if(robotPos1[1]<robotPos2[1]):
        return "r"
    else:
        return "X"



'''

filename = sys.argv[1]
#filename="barriermaze3x3.txt"
#filename="puzzle-1.rr"
splitfilename = filename.split("/")
cur_name = splitfilename[ len(splitfilename)-1 ]
splitfilename=cur_name.split(".")
cur_name = splitfilename[0]
#print(cur_name)

outfile_name="out"
#outfile_name = "../system_output/"+cur_name+"_opt.cnf"
outfile_name = cur_name+".z3"
##print("Outfile name is: "+outfile_name)

in_file = open(sys.argv[1], "r")
outfile = open(outfile_name, "w")

writeEverything(in_file, outfile, 3)

'''

'''


##foundSolution=False
##start = time.clock()
##start_time = time.time()
##while True:
##
##    Encoding.dim_time = int(cur_dim)
##    writeEverything_opt(outfile_name)
##    os.system(".//lingeling/lingeling "+outfile_name+" > testsystemcall_opt.out")
##    sat_output = open("testsystemcall_opt.out", "r")
##    solution = readSolution(sat_output, cur_dim)
##    satisfied=solution[0]
##    
##
##    if not satisfied:
##        lb=cur_dim
##    	if not foundSolution:
##    		ub_exp+=1
##    		ub*=2
##            	cur_dim=ub
##    	else:
##    		cur_dim = max(lb+1, math.floor((lb+ub)/2.0))
##
##	##print("Current number of steps: "+ str(cur_dim))
##
##    else:
##	    ##print(str(cur_dim-1)+" was sat.")
##	    ub=solution[1] #just in case there were null movements
##	    cur_dim = max(lb+1, math.floor((lb+ub)/2.0))
##	    foundSolution=True
##	    current_best_solution = solution[2]
##
##
##    if( lb+1 >= ub):
##        #if not foundSolution:
##            ##print("Unsat!")
##        #else:
##            ##print("Sat!")
##            ##print("Upper bound (should be the same as the number of steps) is: "+str(ub))
##                
##        ##print("LB>UB - should be unsat?")
##            
##        if foundSolution:
##            #printSolution(current_best_solution)
##            ##print("Time taken: "+str(time.clock()-start) + " seconds.") #python processing only
##            ##print("Time taken: "+str(time.time()-start_time) + " seconds.") #system call - sat, I assume?
##            sat_output.close()
##            os.remove(cur_name+"_opt.cnf")
##            os.remove(cur_name+"_opt.sol")
##            os.remove("testsystemcall_opt.out")
##			
##            exit();
##            
'''