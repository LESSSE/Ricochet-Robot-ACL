
sign = lambda x: x and (1, -1)[x < 0]

dim_line=1
dim_col=1
dim_robot=1
dim_time=1

def colToInt(col):
     if col == "R":
          return 0
     elif col=="Y":
          return 1
     elif col=="G":
          return 2
     elif col=="B":
          return 3
     else:
          return -1

def dirToInt(direction):
     if direction=="u":
          return 1<<3
     elif direction=="d":
          return 1<<2
     elif direction=="l":
          return 1<<1
     elif direction=="r":
          return 1<<0
     else:
          return -1

def dirToVec(direction):
     if direction=="u":
          return [-1, 0]
     elif direction=="d":
          return [1, 0]
     elif direction=="l":
          return [0, -1]
     elif direction=="r":
          return [0, 1]
     else:
          return -1

def revDir(d):
     if d==8:
          return 4
     elif d==4:
          return 8
     elif d==2:
          return 1
     elif d==1:
          return 2
     return -1

#Currently, this function also writes the first few constraints (robot positions and goal)
def readEdges(in_file, outfile):
     global dim_line, dim_column, dim_robot, dim_time
     #in_file = open(filename, "r")

     robotsPositions = [0 for i in range(4)]
     goal=0

     #read board size
     cur_line = in_file.readline()
     dim_line=int(cur_line)
     dim_column=dim_line

     constraints = []

     #read robots' initial positions
     for i in range(4):
          cur_line = in_file.readline()
          #cur_line = cur_line[: len(cur_line)-1] #ignore \n
          cur_line = cur_line.rstrip()
          cur_tok = cur_line.split(" ")
          
          robotsPositions[ colToInt(cur_tok[0]) ] = [ int(cur_tok[1])-1, int(cur_tok[2])-1 ] #indices start at 1 in the file
          
          ac="(assert(position "+str(int(cur_tok[1])-1)+" "+str(int(cur_tok[2])-1)+" "+str(colToInt(cur_tok[0]))+" "+"0"+"))"
          #print(ac)
          outfile.write(ac+"\n")

     #read goal
     cur_line = in_file.readline()
     cur_line = cur_line[: len(cur_line)-1] #ignore \n
     cur_tok = cur_line.split(" ")
     goal = [ colToInt(cur_tok[0]), int(cur_tok[1])-1, int(cur_tok[2])-1 ]
     ac="(assert (or "
     count=1
     for time in range(dim_time):
          count+=1
          ac+="(position "+str(int(cur_tok[1])-1)+" "+str(int(cur_tok[2])-1)+" "+str(colToInt(cur_tok[0]))+" "+str(time)+") "
     #for i in range(count):
     #     ac+=")"
     #print(ac+"))")
     outfile.write(ac+"))\n")
     
     #read number of barriers
     cur_line = in_file.readline()
     num_barriers = int(cur_line)

     barriers = [ [0 for j in range(dim_column)] for i in range(dim_line)]
     
     #read barriers
     for i in range(num_barriers):
          cur_line = in_file.readline()

          #cur_line = cur_line[: len(cur_line)-1] #ignore \n
          cur_line=cur_line.rstrip()

          cur_tok = cur_line.split(" ")


          line = int(cur_tok[0])-1
          col =  int(cur_tok[1])-1
          d = dirToInt(cur_tok[2])


          dir_line = dirToVec(cur_tok[2])[0]
          dir_col = dirToVec(cur_tok[2])[1]
          
          barriers[line][col] = barriers[line][col] | d
          barriers[line + dir_line][col + dir_col] = barriers[line + dir_line][col + dir_col]  | revDir(d)


     returnlist = []
     returnlist += [barriers]
     returnlist += constraints
     
     return returnlist




def barrier(x, y, direction, board):
##     UP=8
##     DOWN=4
##     LEFT=2
##     RIGHT=1

     #direction should be what? powers of two, I think? Yes, whatever internal representation I have
     return board[x][y] & direction !=0


####################################################################

#gets every path that cannot be extended (oriented symmetrically in both ways)
def getMaximallyExtendedEdges( board ):

     extEdgelist=[]
     #HORIZONTAL
     for cur_line in range(0, dim_line):
          min_col=0
          max_col=0
          for cur_col in range(0, dim_column):
               if(cur_col+1 == dim_column):
                    if(min_col < max_col):
                         extEdgelist.append( [cur_line, min_col, cur_line, max_col])
                    continue

               if(barrier(cur_line, cur_col, dirToInt('r'), board) or barrier(cur_line, cur_col+1, dirToInt('l'), board)):
               #if(barrier(cur_line, cur_col, RIGHT) or barrier(cur_line, cur_col+1, LEFT)):
                    if(min_col < max_col):
                         extEdgelist.append( [cur_line, min_col, cur_line, max_col])
                    min_col=max_col+1
               else:
                    max_col=cur_col+1


     #VERTICAL
     for cur_col in range(0, dim_column):
          min_line=0
          max_line=0
          for cur_line in range(0, dim_line):
               if(cur_line+1 == dim_line):
                    if(min_line < max_line):
                         extEdgelist.append( [min_line, cur_col, max_line, cur_col])
                    continue

               if(barrier(cur_line, cur_col, dirToInt('d'), board) or barrier(cur_line+1, cur_col, dirToInt('u'), board)):
               #if(barrier(cur_line, cur_col, DOWN) or barrier(cur_line+1, cur_col, UP)):
                    if(min_line < max_line):
                         extEdgelist.append( [min_line, cur_col, max_line, cur_col])
                    min_line=max_line+1
               else:
                    max_line=cur_line+1
                         
     return extEdgelist    




####################################################################


#to find the edges that lead to a given position, knowing they're aligned is a good first step
def getConstantLineExtendedEdges(extEdgelist):
     lineSortedEdges = [ [] for i in range(0, dim_line)]
     for edge in extEdgelist:
          if edge[0] != edge[2]:
               continue
          lineSortedEdges[edge[0]].append(edge)
     return lineSortedEdges
          
          

def getConstantColumnExtendedEdges(extEdgelist):
     columnSortedEdges = [ [] for i in range(0, dim_column)]
     for edge in extEdgelist:
          if edge[1] != edge[3]:
               continue
          columnSortedEdges[edge[1]].append(edge)
     return columnSortedEdges



#There is only one extended edge that crosses a point in a given direction
def getLineCrossingExtendedEdge(pos_x, pos_y, lineSortedEdges, columnSortedEdges):
     ##print("entered getLineCrossing")
     edgelist=[]
     for edge in columnSortedEdges[pos_y]:
          if ((edge[0]>pos_x) ^ (edge[2]>pos_x)) or edge[0]==pos_x or edge[2]==pos_x:
               edgelist.append(edge)
               return edge
               
     ##print(len(edgelist))
     return -1
     return edgelist

def getColumnCrossingExtendedEdge(pos_x, pos_y, lineSortedEdges, columnSortedEdges):
     ##print("entered getColumnCrossing for point: "+str(pos_x)+","+str(pos_y))
     edgelist=[]
     
     for edge in lineSortedEdges[pos_x]:
          if ((edge[1]>pos_y) ^ (edge[3]>pos_y)) or edge[1]==pos_y or edge[3]==pos_y:
               edgelist.append(edge)
               ##print("Found: " + str(edge))
               return edge
     ##print(len(edgelist))
     return -1
     return edgelist


####################################################################

def precomputeOrigins_Point(line, col, lineSortedEdges, columnSortedEdges):
     extLine = getLineCrossingExtendedEdge(line, col, lineSortedEdges, columnSortedEdges)
     extCol = getColumnCrossingExtendedEdge(line, col, lineSortedEdges, columnSortedEdges)

     originList=[]
     if(extLine!=-1):
          #VERTICAL EDGE
          cur_line = extLine[0]
          cur_col = extLine[1]

          dir_x = sign(extLine[2]-extLine[0])
          dir_y = sign(extLine[3]-extLine[1])

          
          while(cur_line != extLine[2] or cur_col!=extLine[3]):
               if cur_line==line and cur_col == col:
                  cur_line += dir_x
                  cur_col += dir_y
                  continue
               originList.append ( [cur_line, cur_col]  )
               cur_line += dir_x
               cur_col += dir_y
               
          #process the edge's extreme
          if not(cur_line==line and cur_col == col):
              originList.append ( [cur_line, cur_col]  )

     if(extCol!=-1):
          #HORIZONTAL EDGE
          cur_line = extCol[0]
          cur_col = extCol[1]

          dir_x = sign(extCol[2]-extCol[0])
          dir_y = sign(extCol[3]-extCol[1])

          while(cur_line != extCol[2] or cur_col!=extCol[3]):
               if cur_line==line and cur_col == col:
                  cur_line += dir_x
                  cur_col += dir_y
                  continue
               originList.append ( [cur_line, cur_col]  )
               cur_line += dir_x
               cur_col += dir_y

          #process the edge's extreme
          if not(cur_line==line and cur_col == col):
              originList.append ( [cur_line, cur_col]  )

     return originList



def precomputeOrigins(extEdgelist):
     origins = [ [ 0 for j in range(dim_column)] for i in range(dim_line) ]

     lineSortedEdges = getConstantLineExtendedEdges(extEdgelist)
     columnSortedEdges = getConstantColumnExtendedEdges(extEdgelist)

##     #print("Line sorted edges: ")
##     #print (lineSortedEdges)
##     #print("Column sorted edges: ")
##     #print(columnSortedEdges)

     for line in range(dim_line):
          for col in range(dim_column):
               origins[line][col] = precomputeOrigins_Point(line, col, lineSortedEdges, columnSortedEdges)

     return origins
