import argparse
import pycosat
import sys
import itertools

#positions in xy are from 1 to n_max
#vertices are from 0 to 

n_aux = 0 

def description_to_cnf(file_des,file_cnf,t):
	global n_aux

	def xy_to_v(x,y): 
		'''
		gives the vertice correpondent to (x,y)
		Input: x,y between 1 and n_max
		Output: vertice between 0 and n_max^2-1
		Error: -1 if x,y out of range
		'''
		if (x in range(1,n_max+1)) and (y in range(1,n_max+1)): 
			return (x-1) * n_max + (y-1)
		else:
			return -1	
	def color_to_k(color):
		'''
		gives a numerical code for color
		Input: character with color
		Output: 0,1,2,3
		Error: -1 when color not designated
		'''
		return{
			'R': 0,
			'G': 1,
			'Y': 2,
			'B': 3
		}.get(color, -1)
	def direction_to_d(direction):
		'''
		gives a numerical code for direction
		Input: character with direction
		Output: 0,1,2,3
		Error: -1 when direction not designated
		'''
		return {
			'U': 0,
			'D': 1,
			'R': 2,
			'L': 3
		}.get(direction.upper(), (-1,-1))
	def xyd_to_xy(x,y,direction):
		'''
		gives the next pair of coordinates in folowing
		Input: pair of coordinates and direction
		Output: pair of coordinates between 1 and n_max
		Error: (-1,-1) when direction not designated or when old or new (x1,y1) out of range
		'''
		x2, y2 = {
			'U':(x-1,y),
			'D':(x+1,y),
			'R':(x,y+1),
			'L':(x,y-1)
		}.get(direction.upper(), (-1,-1))
		if x2 in range(1,n_max+1) and y2 in range(1, n_max+1):
			return (x2,y2)
		else:
			return (-1,-1)
	def vd_to_v(v,direction):
		'''
		gives the next vertice folowing direction
		Input: vertice and direction
		Output:  vertice between n and n_max^2-1
		Error: -1 when direction not designated or when old or new v out of range
		'''	
		if not v in range(0,v_max):
			return -1 
		elif v%n_max == 0 and direction == 'L':
			return -1
		elif v%n_max == n_max-1 and direction == 'R':
			return -1
		elif v >= n_max*(n_max-1) and direction == 'D':
			return -1
		elif v < n_max  and direction == 'U':
			return -1
		else:
			return{
				'U':v-n_max,
				'D':v+n_max,
				'R':v+1,
				'L':v-1,
			}.get(direction.upper(), -1)
	def v_to_x(v):
		if v in range(0,v_max): 
			return v // n_max +1
		else:
			return -1	
	def v_to_y(v):
		if v in range(0,v_max): 
			return v % n_max + 1
		else:
			return -1	
	def between_xy(x1,y1,x2,y2):
		between = []
		if (not ((x1 == x2) or (y1 == y2))) or (not ((x1 in range(1,n_max+1)) and (y1 in range(1,n_max+1)) and (x2 in range(1,n_max+1)) and (y2 in range(1,n_max+1)))): 
			between = []
		elif (x1 == x2):
			if (y2 < y1):
				for i in range(y2,y1):
					between += [(x1,i)]
			else:
				for i in range(y1+1,y2+1):
					between += [(x1,i)]
		else:
			if (x2 < x1):
				for i in range(x2,x1):
					between += [(i,y1)]
			else:
				for i in range(x1+1,x2+1):
					between += [(i,y1)]
		return between
	def direction_xy(x1,y1,x2,y2):
		if ((x1 != x2) and (y1 != y2)) or (not ((x1 in range(1,n_max+1)) and (y1 in range(1,n_max+1)) and (x2 in range(1,n_max+1)) and (y2 in range(1,n_max+1)))): 
			d = -1
		elif (x1 == x2):
			if (y2 < y1):
				d = 'L'
			else:
				d = 'R'
		else:
			if (x2 < x1):
				d = 'U'
			else:
				d = 'D'
		return d

	#TO PROP CONVERTERS		
	def pos_xy_to_prop(color,x,y,t):
		'''
		gives the number of the proposition that corresponds to robot of *color* beeing at position (*x*,*y*) at timestep *t*
		Input: color: char ['B','Y','G',R'], x: int [1, n_max], y: int [1, n_max], t: int [0, t_max]
		Output: number of proposition 
		Error: -1 when wrong arguments
		'''
		if xy_to_v(x,y) >= 0 and color_to_k(color) >= 0 and t >= 0: 
			return  t * k_max * v_max + color_to_k(color) * v_max + xy_to_v(x,y) + 1
		else:
			return -1
	def pos_v_to_prop(color,v,t):
		'''
		gives the number of the proposition that corresponds to robot of *color* beeing at vertice *v* at timestep *t*
		Input: color: char ['B','Y','G',R'], x: int [1, n_max], y: int [1, n_max], t: int [0, t_max]
		Output: number of proposition 
		Error: -1 when wrong arguments
		'''
		if v >= 0 and color_to_k(color) >= 0 and t >= 0: 
			return   t * k_max * v_max + color_to_k(color) * v_max + v + 1
		else:
			return -1
	def link_to_prop_xy(x1,y1,x2,y2):
		'''
		gives the number of the proposition that corresponds to the link between the position (*x1*,*y1*) and position (*x2*,y2*)
		Input: x1: int [1, n_max], y1: int [1, n_max], x2: int [1, n_max], y2: int [1, n_max]
		Output: number of proposition 
		Error: -1 when wrong arguments; -2 when the vertice is the same
		'''
		v1 = xy_to_v(x1,y1)+1;
		v2 = xy_to_v(x2,y2)+1;
		if v1 <= 0 or v2 <= 0:
			return -1 #vertice out of range
		elif v1 == v2:
			return -2 #link to same vertice
		elif v2 < v1:
			v1, v2 = v2, v1
		return n_pos + (v2-v1) + (v_max-v2) * (v_max-v2+1)//2 + 1
	def link_to_prop_v(v1,v2):
		'''
		gives the number of the proposition that corresponds to the link between the position (*x1*,*y1*) and position (*x2*,y2*)
		Input: x1: int [1, n_max], y1: int [1, n_max], x2: int [1, n_max], y2: int [1, n_max]
		Output: number of proposition 
		Error: -1 when wrong arguments; -2 when the vertice is the same
		'''
		if v1 <= 0 or v2 <= 0:
			return -1 #vertice out of range
		elif v1 == v2:
			return -2 #link to same vertice
		elif v2 < v1:
			v1, v2 = v2, v1
		return n_pos + (v2-v1) + (v_max-v2) * (v_max-v2+1)//2 + 1
	def possible_to_prop(x1,y1,x2,y2,t):
		v1 = xy_to_v(x1,y1)
		v2 = xy_to_v(x2,y2)
		if (x1!= x2) and (y1 != y2):
			return -1 #vertice out of range
		elif v1 == v2:
			return -2 #link to same vertice
		
		if y1 == y2:
			return  n_pos + n_map + t * v_max * 2*n_max + v1 * 2*n_max + x2 + 1
		else:
			return  n_pos + n_map + t * v_max * 2*n_max + v1 * 2*n_max + n_max * y2 + 1
	def move_to_prop(color,direction,t):
		if direction_to_d(direction) >= 0 and color_to_k(color) >= 0 and t >= 0: 
			return  n_pos + n_map + n_poss + t * k_max * d_max + color_to_k(color) * d_max + direction_to_d(direction) + 1 
		else:
			return -1
	def aux_to_prop():
		global n_aux
		n = n_pos + n_map + n_poss + n_mov + n_aux + 1
		n_aux += 1
		return n
		
	def list_to_clause(list1):
		s = ["0\n"]
		for l in list1:
			new_s = []
			for w in l:
				for s1 in s:
					new_s += [str(w)+" "+s1]
			s = new_s
		return s

	lines = file_des.readlines()
	l = lines[0].strip()

	n_max = int(l.split()[0])	#n
	v_max = n_max * n_max  		#number of vertices 
	t_max = t					#number of steps
	k_max = 4					#number of robots
	d_max = 4					#number of directions

	n_pos = (t_max+1) * v_max * k_max   			#position of each robot for each time                      	
	n_map = (v_max-1) * (v_max) // 2				#links between two vertices on map   
	n_poss = t_max * v_max * 2*n_max				#number of possible outcomes  
	n_mov = t_max * k_max * d_max					#moves per time

	clauses = ""
	n_clauses = 0

	#initial positions__________________________
	for i in range(0,4):
		l = lines[i+1].strip()
		color = l.split()[0][0]
		x = int(l.split()[1])
		y = int(l.split()[2])
		clauses += str(pos_xy_to_prop(color,x,y,0))+" 0\n"
		n_clauses +=1

	#goal________________________________________
	l = lines[5].strip()
	color = l.split()[0][0]
	x = int(l.split()[1])
	y = int(l.split()[2])
	clauses += str(pos_xy_to_prop(color,x,y,t_max))+" 0\n"
	n_clauses += 1

	#map barriers_________________________________
	walls = []
	for l in lines[7:]:
		l = l.strip()
		x1 = int(l.split()[0])
		y1 = int(l.split()[1])
		d = l.split()[2][0]
		x2,y2 = xyd_to_xy(x1,y1,d)
		v1 = xy_to_v(x1,y1)
		v2 = xy_to_v(x2,y2)
		if(v2 != -1):
			if(v2 < v1):
				v1, v2 = v2, v1
			walls += [(v1,v2)]

	edges = []
	for v in range(0,v_max):
		for d in ['R','D']:
			v2 = v
			v3 = vd_to_v(v2,d)
			while (v3 != -1) and (not (v2,v3) in walls):
				if(v != v3):
					edges += [(v,v3)]
				v2 = v3
				v3 = vd_to_v(v2,d)

	#________________________________________
	print("1. Positions: each robot have to have one position per time step")
	#positions
	#each robot have to have one position per time step 
	for t in range(0,t_max+1):
		for k in ['R','G','Y','B']:
			for i in range(1,n_max+1):
				for j in range(1,n_max+1):
					clauses += str(pos_xy_to_prop(k,i,j,t))+" "
			clauses += "0\n"
			n_clauses +=1

	print("2. Positions: each robot can only be at most at one position at each time step")
	#each robot can only be at most at one position at each time step 
	for t in range(0,t_max+1):
		for k in ['R','G','Y','B']:
			for v1 in range(0,v_max):
				for v2 in range(v1+1,v_max):
					clauses += str(-pos_v_to_prop(k,v1,t))+" "+str(-pos_v_to_prop(k,v2,t))+" 0\n"
					n_clauses +=1

	print("3. Possible: possible moves must not have robots in the middle")
	#possible moves must not have robots in the middle
	for t in range(1,t_max):		
		for e in edges:
			v1 = e[0]
			v2 = e[1]
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			for v in between_xy(x1,y1,x2,y2):
				for k in ['R','G','Y','B']:
					clauses += str(-possible_to_prop(x1,y1,x2,y2,t))+" "+str(-pos_xy_to_prop(k,v[0],v[1],t)) +" 0\n"
					n_clauses += 1
			v1 = e[1]
			v2 = e[0]	
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			for v in between_xy(x1,y1,x2,y2):
				for k in ['R','G','Y','B']:
					clauses += str(-possible_to_prop(x1,y1,x2,y2,t))+" "+str(-pos_xy_to_prop(k,v[0],v[1],t)) +" 0\n"
					n_clauses += 1

	print("4. Possible: need to have a robot at the end")
	#possible moves need to have a robot at the end
	for t in range(1,t_max):		
		for e in edges:
			v1 = e[0]
			v2 = e[1]
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			d = direction_xy(x1,y1,x2,y2)
			if d != -1:
				x3, y3 = xyd_to_xy(x2,y2,d)
				if( (xy_to_v(x3,y3) != -1) and ((v1,xy_to_v(x3,y3)) in edges) ):
					s = str(-possible_to_prop(x1,y1,x2,y2,t))+" "
					for k in ['R','G','Y','B']:
						s += str(pos_xy_to_prop(k,x3,y3,t)) +" "
					s += "0\n"  
					clauses += s	
					n_clauses += 1		
			v1 = e[1]
			v2 = e[0]
			x1, y1 = v_to_x(v1),v_to_y(v1)
			x2, y2 = v_to_x(v2),v_to_y(v2)
			d = direction_xy(x1,y1,x2,y2)
			if d != -1:
				x3, y3 = xyd_to_xy(x2,y2,d)
				if( (xy_to_v(x3,y3) != -1) and ((xy_to_v(x3,y3),v1) in edges) ):
					s = str(-possible_to_prop(x1,y1,x2,y2,t))+" "
					for k in ['R','G','Y','B']:
						s += str(pos_xy_to_prop(k,x3,y3,t)) +" "
					s += "0\n"
					clauses += s  	
					n_clauses += 1

	print("5. Moves: each time step at most one robot can move")
	#at each time step at most one robot can move 
	for t in range(0,t_max):
		for k1 in ['R','G','Y','B']:
			for d1 in ['U','D','R','L']:
				for k2 in ['R','G','Y','B']:
					for d2 in ['U','D','R','L']:
						if k1!=k2 or d1!=d2:
							clauses += str(-move_to_prop(k1,d1,t))+" "+str(-move_to_prop(k2,d2,t))+" 0\n"
							n_clauses +=1

	print("6. Moves: for each time step each robot or stay or move")
	#for each time step each robot or stay or move
	for k in ['R','B','G','Y']:
		for t in range(1,t_max+1):
			for v in range(0,v_max):
				poss_mv = []
				aux_s = []
				x2, y2 = v_to_x(v),v_to_y(v)

				#get of possible movements
				for e in edges:
					if e[1] == v:
						x1, y1 = v_to_x(e[0]),v_to_y(e[0])
						d = direction_xy(x1,y1,x2,y2)
						poss_mv += [[pos_v_to_prop(k,e[0],t-1),possible_to_prop(x1,y1,x2,y2,t-1),move_to_prop(k,d,t-1)]]
					elif e[0] == v:
						x1, y1 = v_to_x(e[1]),v_to_y(e[1])
						d = direction_xy(x1,y1,x2,y2)
						poss_mv += [[pos_v_to_prop(k,e[1],t-1),possible_to_prop(x1,y1,x2,y2,t-1),move_to_prop(k,d,t-1)]]

				for i in poss_mv:
					aux = aux_to_prop()
					aux_s += [aux]
					for j in i:
						clauses += str(-j)+" "+str(-aux)+" 0\n" 
						n_clauses += 1

				s = str(-pos_xy_to_prop(k,x2,y2,t))+" "+str(pos_xy_to_prop(k,x2,y2,t-1))+" "
				for i in aux_s: 
					s += str(i)+" "
				
				clauses += s + " 0\n"
				n_clauses += 1
			
	'''#at each time at least one robot need to move 
	for t in range(0,t_max):
		for k1 in ['R','G','Y','B']:
			for d1 in ['U','D','R','L']:
				clauses += str(move_to_prop(k1,d1,t))+" "
		clauses += "0\n"
		n_clauses +=1

	#two different robots may be in different positions
	for t in range(0,t_max+1):
		for k in ['R','G','Y','B']:
			for v1 in range(0,v_max):
				for v2 in range(v1+1,v_max):
					clauses += str(-pos_v_to_prop(k,v1,t))+" "+str(-pos_v_to_prop(k,v2,t))+" 0\n"
					n_clauses +=1
	'''
					
	n_var = n_pos + n_map + n_mov + n_poss + n_aux	#number of total propositions
	clauses = "p cnf "+str(n_var)+" "+str(n_clauses)+"\n" + clauses

	file_cnf.write(clauses)

	'''	
	print("n_var: " + str(n_var))
	print("n_pos: " + str(n_pos))
	print("n_goal: " + str(n_goal))
	print("n_map: " + str(n_map))
	print("n_poss: " + str(n_poss))
	print("n_mov: " + str(n_mov))

	print("xy_to_v")
	print(xy_to_v(1,1))
	print(xy_to_v(1,2))
	print(xy_to_v(n_max,n_max-1))
	print(xy_to_v(n_max,n_max))

	print("pos_xy_to_prop")
	print(pos_xy_to_prop('R',1,1,0))
	print(pos_xy_to_prop('B',n_max,n_max,t_max))
	print("pos_v_to_prop")
	print(pos_v_to_prop('R',0,0))
	print(pos_v_to_prop('B',n_max*n_max-1,t_max))
	print("goal_to_prop")
	print(goal_to_prop('R',1,1))
	print(goal_to_prop('B',n_max,n_max))
	print("link_to_prop")
	print(link_to_prop(n_max,n_max,n_max,n_max-1) - (n_pos + n_goal +1))
	print(link_to_prop(1,2,1,1) - (n_pos + n_goal +1))
	print("possible_to_prop")
	print(possible_to_prop(0,0,0,0,0))
	print(possible_to_prop(1,1,1,1,t_max-1))
	print("move_to_prop")
	print(move_to_prop('R','U',0))
	print(move_to_prop('B','L',t_max-1))
	'''

def file_to_clauses(f):
	c = []
	for l in f.readlines():
		l = l.strip()
		if (not l[0] == 'p') and (l[:-1]!="") and (not l[0] == 'c'):
			nclause = map(int, l.split()[:-1])
			c += [list(nclause)]
	return c

#dois robots não podem estar no mesma posição

#


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='ricochet robots')
	parser.add_argument('-t', nargs='?', type=int, help='the number of steps', default = 1) 
	parser.add_argument('-v', nargs='?', type=int, default=0, help='the visualization mode\n\t 0 - just number of solutions \n\t 1 - cnf solutions \n\t 2 - board vizualization')
	parser.add_argument('-f', nargs='+', type=str, default="", help='file of description of the problem') 
	args = parser.parse_args()

	t_max = args.t

	if args.f != "":
		f_des = open(args.f, 'r')
	else:
		f_des = sys.stdin
	f_pro = open("problem.txt", 'w')
	description_to_cnf(f_des,f_pro,t_max)

	f_pro = open("problem.txt", 'r')
	problem = file_to_clauses(f_pro)

	#solutions = [pycosat.solve(problem)]

	#print(solutions)


	# um robot por posição
	# um movimento por time step
	# um objetivo por jogo
	# 

	